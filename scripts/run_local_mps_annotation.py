#!/usr/bin/env python3
"""Local MPS/CPU oneshot annotation (same protocol as Kaggle GPU notebook).

Exploratory only — not confirmatory. Blinded IDs need private map to join.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "kaggle" / "bundle"
DEFAULT_OUTPUT = ROOT / "results" / "exploratory" / "local_mps"


def pick_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def parse_list(raw: str):
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--max-passages", type=int, default=0)
    ap.add_argument("--model", default=os.environ.get("RISHIQ_MODEL", "Qwen/Qwen2.5-1.5B-Instruct"))
    ap.add_argument("--max-new-tokens", type=int, default=3500)
    args = ap.parse_args()

    INPUT = args.input
    OUTPUT = args.output
    OUTPUT.mkdir(parents=True, exist_ok=True)
    device = pick_device()
    print("device", device, "torch", torch.__version__)

    blinded = pd.read_parquet(INPUT / "blinded_passages.parquet")
    ont = yaml.safe_load((INPUT / "ontology_v0.1.yaml").read_text())
    features = ont["features"]
    n = args.max_passages or int(os.environ.get("RISHIQ_MAX_PASSAGES", "0")) or len(blinded)
    blinded = blinded.head(n).reset_index(drop=True)
    print("passages", len(blinded), "features", len(features))

    MODEL = args.model
    dtype = torch.float16 if device in {"cuda", "mps"} else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=dtype)
    model.to(device)
    model.eval()
    print("loaded", MODEL)

    feat_brief = [
        {
            "id": f["id"],
            "name": f["name"],
            "definition": f["definition"][:220],
            "exclusions": (f.get("exclusions") or "")[:160],
        }
        for f in features
    ]
    SYSTEM = (
        "You label RISHI-Q structural ontology features on a passage. "
        "Prefer NA over 1 when unsure. Unity/oneness is NOT entanglement (Q06). "
        "Vibration is NOT QFT. Evidence spans must be exact substrings of the passage. "
        "Return ONLY a JSON list of objects: "
        '[{"feature_id":"O01","label":"1|0|NA|U","evidence":"...","reason":"...","confidence":0.0}, ...] '
        "Include EVERY feature id exactly once."
    )

    def generate(prompt: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        gen = out[0][inputs["input_ids"].shape[-1] :]
        return tokenizer.decode(gen, skip_special_tokens=True)

    def annotate_passage(anonymous_id: str, text: str):
        prompt = (
            f"Passage:\n{text[:2200]}\n\n"
            f"Features to label (JSON schemas):\n{json.dumps(feat_brief)}\n\n"
            "Return JSON list covering every feature_id."
        )
        raw = generate(prompt)
        parsed = parse_list(raw)
        rows = []
        by_id = {}
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict) and item.get("feature_id"):
                    by_id[str(item["feature_id"])] = item
        for f in features:
            fid = f["id"]
            item = by_id.get(fid) or {}
            label = str(item.get("label", "NA")).upper().replace("YES", "1").replace("NO", "0")
            if label not in {"1", "0", "NA", "U"}:
                label = "NA"
            evidence = str(item.get("evidence") or "")
            reason = str(item.get("reason") or "missing_or_unparsed")
            conf = float(item.get("confidence") or 0.4)
            if label == "1":
                if not evidence or evidence.lower() not in text.lower():
                    label = "NA"
                    reason += ";evidence_not_in_passage"
                    evidence = ""
            rows.append(
                {
                    "passage_id": anonymous_id,
                    "feature_id": fid,
                    "label": label,
                    "evidence": evidence if label == "1" else "",
                    "reason": reason,
                    "confidence": min(1.0, max(0.0, conf)),
                    "annotator": "transformers-annotator-oneshot",
                    "model_version": f"{MODEL}@main",
                    "prompt_version": "ann-v0.2-oneshot",
                    "verified": False,
                    "verification_flags": [],
                }
            )
        return rows, raw[:500]

    all_rows = []
    t0 = time.time()
    checkpoint = OUTPUT / "annotations_partial.parquet"
    for i, r in blinded.iterrows():
        aid = r["anonymous_id"]
        text = r["text"]
        try:
            rows, _preview = annotate_passage(aid, text)
        except Exception as e:
            rows = [
                {
                    "passage_id": aid,
                    "feature_id": f["id"],
                    "label": "NA",
                    "evidence": "",
                    "reason": f"generation_error:{type(e).__name__}",
                    "confidence": 0.1,
                    "annotator": "transformers-annotator-oneshot",
                    "model_version": f"{MODEL}@main",
                    "prompt_version": "ann-v0.2-oneshot",
                    "verified": False,
                    "verification_flags": ["error"],
                }
                for f in features
            ]
        all_rows.extend(rows)
        if (i + 1) % 5 == 0 or (i + 1) == len(blinded):
            pos = sum(1 for x in all_rows if x["label"] == "1")
            print(f"{i+1}/{len(blinded)} elapsed={time.time()-t0:.1f}s positives={pos}", flush=True)
            pd.DataFrame(all_rows).to_parquet(checkpoint, index=False)

    ann_df = pd.DataFrame(all_rows)
    ann_path = OUTPUT / "annotations.parquet"
    ann_df.to_parquet(ann_path, index=False)
    manifest = {
        "experiment_id": "local-mps-annotation-pd-pilot-oneshot",
        "backend": "transformers-annotator-oneshot",
        "model_name": MODEL,
        "prompt_version": "ann-v0.2-oneshot",
        "n_passages": len(blinded),
        "n_annotations": len(ann_df),
        "n_positive": int((ann_df["label"] == "1").sum()),
        "elapsed_sec": time.time() - t0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gpu": device != "cpu",
        "device": device,
        "note": "EXPLORATORY — not confirmatory; blinded IDs require private map to join",
        "kaggle_blocked": "aks1321 batch workers had no GPU despite enable_gpu/machine_shape",
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2), flush=True)
    print("wrote", ann_path, flush=True)


if __name__ == "__main__":
    main()
