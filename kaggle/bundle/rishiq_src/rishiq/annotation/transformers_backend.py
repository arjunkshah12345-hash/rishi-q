"""Open-model / Transformers annotation backend (Kaggle-oriented).

Conservative structured prompting. Prefer NA over YES.
Requires optional ml extras: torch, transformers.
"""

from __future__ import annotations

import json
import re
from typing import Any

from rishiq.models import (
    AnnotationLabel,
    BlindedPassage,
    FeatureAnnotation,
    Passage,
    Proposition,
)
from rishiq.models.ontology import Ontology
from rishiq.propositions import HeuristicPropositionExtractor
from rishiq.annotation import AnnotationBackend  # noqa: PLC0415 — shared ABC


def _parse_label_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return {"label": "NA", "evidence": "", "reason": "unparseable", "confidence": 0.2}
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"label": "NA", "evidence": "", "reason": "invalid_json", "confidence": 0.2}
    label = str(obj.get("label", "NA")).upper().replace("YES", "1").replace("NO", "0")
    if label not in {"1", "0", "NA", "U"}:
        label = "NA"
    return {
        "label": label,
        "evidence": str(obj.get("evidence", "") or ""),
        "reason": str(obj.get("reason", "") or ""),
        "confidence": float(obj.get("confidence", 0.5) or 0.5),
    }


class TransformersAnnotationBackend(AnnotationBackend):
    """Generate feature labels with a local/HF causal LM.

    Designed for Kaggle GPUs. On CPU/Mac this may be too slow/heavy — use heuristic.
    """

    name = "transformers-annotator"
    prompt_version = "ann-v0.1"

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
        revision: str = "main",
        max_new_tokens: int = 128,
        device: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.revision = revision
        self.max_new_tokens = max_new_tokens
        self._prop = HeuristicPropositionExtractor()
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            raise ImportError(
                "Install ml extras: uv pip install -e '.[ml]' (or Kaggle requirements)"
            ) from e

        self._torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            revision=revision,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
        )
        if device:
            self.model.to(device)
        elif not torch.cuda.is_available():
            self.model.to("cpu")
        self.model.eval()

    def extract_propositions(self, passage: Passage | BlindedPassage) -> list[Proposition]:
        return self._prop.extract(passage)

    def _generate(self, prompt: str) -> str:
        tor = self._torch
        messages = [
            {
                "role": "system",
                "content": (
                    "You label structural ontology features. Prefer NA over 1. "
                    "Unity is not entanglement. Vibration is not QFT. "
                    "Respond with JSON only."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        if hasattr(self.tokenizer, "apply_chat_template"):
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            text = prompt
        inputs = self.tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with tor.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        gen = out[0][inputs["input_ids"].shape[-1] :]
        return self.tokenizer.decode(gen, skip_special_tokens=True)

    def annotate_features(
        self,
        passage: Passage | BlindedPassage,
        propositions: list[Proposition],
        ontology: Ontology,
    ) -> list[FeatureAnnotation]:
        if isinstance(passage, BlindedPassage):
            pid = passage.anonymous_id
            text = passage.text
        else:
            pid = passage.passage_id
            text = passage.translation or passage.source_text

        # Limit cost: annotate only features with any weak lexical hint OR all if short
        out: list[FeatureAnnotation] = []
        for feat in ontology.features:
            prompt = (
                f"Passage:\n{text[:1800]}\n\n"
                f"Feature {feat.id} ({feat.name}).\n"
                f"Definition: {feat.definition}\n"
                f"Positive requirements: {feat.positive_requirements}\n"
                f"Exclusions: {feat.exclusions}\n"
                f"Ambiguity rule: {feat.ambiguity_rules}\n\n"
                'Return JSON: {"label":"1|0|NA|U","evidence":"...","reason":"...","confidence":0.0}'
            )
            try:
                raw = self._generate(prompt)
                parsed = _parse_label_json(raw)
            except Exception as e:
                parsed = {
                    "label": "NA",
                    "evidence": "",
                    "reason": f"generation_error:{type(e).__name__}",
                    "confidence": 0.1,
                }
            label = AnnotationLabel(parsed["label"])
            evidence = parsed["evidence"]
            if label == AnnotationLabel.YES and evidence and evidence.lower() not in text.lower():
                # require span presence; else downgrade
                label = AnnotationLabel.NA
                parsed["reason"] += ";evidence_not_in_passage"
            out.append(
                FeatureAnnotation(
                    passage_id=pid,
                    feature_id=feat.id,
                    label=label,
                    evidence=evidence if label == AnnotationLabel.YES else "",
                    reason=parsed["reason"],
                    confidence=min(1.0, max(0.0, parsed["confidence"])),
                    annotator=self.name,
                    model_version=f"{self.model_name}@{self.revision}",
                    prompt_version=self.prompt_version,
                )
            )
        return out


def get_backend(name: str = "heuristic", **kwargs) -> AnnotationBackend:
    from rishiq.annotation import HeuristicAnnotationBackend

    if name in {"heuristic", "dummy", "local"}:
        return HeuristicAnnotationBackend()
    if name in {"transformers", "hf", "llm"}:
        return TransformersAnnotationBackend(**kwargs)
    raise ValueError(f"unknown backend: {name}")
