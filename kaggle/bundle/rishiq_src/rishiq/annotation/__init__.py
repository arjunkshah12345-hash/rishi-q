"""Annotation backends: interchangeable model interface."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Iterable

from rishiq.annotation.classical_cues import CLASSICAL_NP_CUES
from rishiq.annotation.metaphysical_cues import METAPHYSICAL_CUES
from rishiq.models import (
    AnnotationLabel,
    BlindedPassage,
    FeatureAnnotation,
    Passage,
    Proposition,
)
from rishiq.models.ontology import Ontology, load_ontology
from rishiq.propositions import HeuristicPropositionExtractor, extract_propositions
from rishiq.validation import verify_evidence


# Conservative keyword → feature heuristics for synthetic/physics controls.
# These are NOT used to chase Sanskrit–quantum analogies; they encode explicit
# structural English cues for instrument validation and synthetic E2E tests.
POSITIVE_CUES: dict[str, list[re.Pattern[str]]] = {
    "O01": [re.compile(r"underlying (reality|entity|substrate|level)", re.I)],
    "O02": [re.compile(r"composed of|aggregates of|made of (more )?elementary", re.I)],
    "O03": [re.compile(r"indivisible|cannot be further divided|discrete (atoms|units)", re.I)],
    "O04": [re.compile(r"continuous (medium|entity|substrate|field)", re.I)],
    "O05": [re.compile(r"localized manifestations|local forms appear", re.I)],
    "O06": [re.compile(r"arise from lower-level|emerge from", re.I)],
    "D01": [re.compile(r"configuration|distinguishable (states|configurations)", re.I)],
    "D02": [re.compile(r"evolves according|change according to|transformation law", re.I)],
    "D03": [re.compile(r"oscillat|periodically|cyclic", re.I)],
    "D04": [re.compile(r"propagat|travels through", re.I)],
    "D05": [re.compile(r"conserved|remains unchanged|invariant quantity", re.I)],
    "D06": [re.compile(r"invariant under", re.I)],
    "D07": [re.compile(r"reversed|inverse process|reversible", re.I)],
    "Q01": [re.compile(r"only (certain|discrete) (energy )?levels|allowed (states|values)", re.I)],
    "Q02": [re.compile(r"superposition|simultaneously represented|jointly represents mutually exclusive", re.I)],
    "Q03": [re.compile(r"probabilities are basic|inherent probability|irreducible probability", re.I)],
    "Q04": [re.compile(r"measurement interaction|outcome is produced in association with a measurement", re.I)],
    "Q05": [re.compile(r"cannot both have definite|incompatible observables|non-commuting", re.I)],
    "Q06": [re.compile(r"cannot be (written|represented) as independent component|non-?factoriz|nonseparab", re.I)],
    "Q07": [re.compile(r"depend(s)? on (which|the) (compatible )?measurement context|contextuality", re.I)],
    "Q08": [re.compile(r"discrete excitations of (the )?(underlying )?field|quanta of the field", re.I)],
    "R01": [re.compile(r"local interactions|neighboring interactions", re.I)],
    "R02": [re.compile(r"distant (entities|systems).*(correlat|relation)", re.I)],
    "R03": [re.compile(r"not recoverable from independent part|irreducible whole", re.I)],
    "R04": [re.compile(r"defined relative to|relative to a reference", re.I)],
    "M01": [re.compile(r"distinguish (the )?measur|observer and (the )?observed|apparatus from the measured", re.I)],
    "M02": [re.compile(r"measurement interaction alters|observation (physically )?changes|alters the system's", re.I)],
    "M03": [re.compile(r"cannot know|ignorance of|unknown to us", re.I)],
    "M04": [re.compile(r"no definite value is predetermined|not predetermined prior", re.I)],
    "F01": [re.compile(r"throughout a spatial region|across (an )?extended|present throughout", re.I)],
    "F02": [re.compile(r"different values at different locations|spatially varying", re.I)],
    "F03": [re.compile(r"travels through space|propagat\w+ through", re.I)],
    "F04": [re.compile(r"manifestations of the (extended )?field|arise from that distributed", re.I)],
    "F05": [re.compile(r"mediated by the|mediates interactions", re.I)],
    "F06": [re.compile(r"dynamical disturbance of the medium|dynamically changed states of the underlying", re.I)],
    "F07": [re.compile(r"discrete excitation quanta|only discrete excitations", re.I)],
}

NEGATIVE_CUES: dict[str, list[re.Pattern[str]]] = {
    "Q06": [re.compile(r"everything is (one|interconnected)|all is one", re.I)],
    "Q03": [re.compile(r"probability only reflects our ignorance", re.I)],
    "M04": [re.compile(r"definite value exists but is unknown", re.I)],
}


class AnnotationBackend(ABC):
    name: str
    revision: str
    prompt_version: str

    @abstractmethod
    def extract_propositions(self, passage: Passage | BlindedPassage) -> list[Proposition]:
        raise NotImplementedError

    @abstractmethod
    def annotate_features(
        self,
        passage: Passage | BlindedPassage,
        propositions: list[Proposition],
        ontology: Ontology,
    ) -> list[FeatureAnnotation]:
        raise NotImplementedError

    def verify(
        self,
        annotations: list[FeatureAnnotation],
        passage: Passage | BlindedPassage,
        ontology: Ontology,
    ) -> list[FeatureAnnotation]:
        text = passage.text if isinstance(passage, BlindedPassage) else (
            passage.translation or passage.source_text
        )
        return [verify_evidence(a, text, ontology) for a in annotations]


class HeuristicAnnotationBackend(AnnotationBackend):
    """Rule-based backend for tests and MacBook development (no LLM required)."""

    name = "heuristic-annotator"
    revision = "0.3.0"
    prompt_version = "ann-v0.1"

    def __init__(
        self,
        use_classical_np_cues: bool = True,
        use_metaphysical_cues: bool = True,
    ) -> None:
        self._prop = HeuristicPropositionExtractor()
        self.use_classical_np_cues = use_classical_np_cues
        self.use_metaphysical_cues = use_metaphysical_cues

    def extract_propositions(self, passage: Passage | BlindedPassage) -> list[Proposition]:
        return extract_propositions(passage, self._prop)

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
        combined = " ".join([text] + [p.text for p in propositions])
        out: list[FeatureAnnotation] = []
        for feat in ontology.features:
            label = AnnotationLabel.NA
            evidence = ""
            reason = "insufficient explicit evidence"
            # Negatives first for hard-rule demos
            for pat in NEGATIVE_CUES.get(feat.id, []):
                m = pat.search(combined)
                if m and feat.id == "Q06" and re.search(
                    r"everything is (one|interconnected)|all is one", combined, re.I
                ):
                    label = AnnotationLabel.NO
                    evidence = m.group(0)
                    reason = "generic unity/interconnection does not support nonseparability"
                    break
            cues = list(POSITIVE_CUES.get(feat.id, []))
            if self.use_classical_np_cues:
                cues = cues + list(CLASSICAL_NP_CUES.get(feat.id, []))
            if self.use_metaphysical_cues:
                cues = cues + list(METAPHYSICAL_CUES.get(feat.id, []))
            if label == AnnotationLabel.NA:
                for pat in cues:
                    m = pat.search(combined)
                    if m:
                        evidence = _span_containing(text, m.group(0))
                        if evidence:
                            label = AnnotationLabel.YES
                            reason = f"matched structural cue for {feat.id}"
                        break
            out.append(
                FeatureAnnotation(
                    passage_id=pid,
                    feature_id=feat.id,
                    label=label,
                    evidence=evidence if label == AnnotationLabel.YES else evidence,
                    reason=reason,
                    confidence=0.7 if label == AnnotationLabel.YES else 0.55,
                    annotator=self.name,
                    model_version=self.revision,
                    prompt_version=self.prompt_version,
                )
            )
        return out


def _span_containing(text: str, needle: str) -> str:
    idx = text.lower().find(needle.lower())
    if idx < 0:
        # fall back to needle itself if present in combined props only
        return needle
    # expand to sentence
    start = text.rfind(".", 0, idx)
    start = 0 if start < 0 else start + 1
    end = text.find(".", idx)
    end = len(text) if end < 0 else end + 1
    return text[start:end].strip()


def get_backend(name: str = "heuristic", **kwargs) -> AnnotationBackend:
    if name in {"heuristic", "dummy", "local"}:
        return HeuristicAnnotationBackend()
    if name in {"transformers", "hf", "llm"}:
        from rishiq.annotation.transformers_backend import TransformersAnnotationBackend

        return TransformersAnnotationBackend(**kwargs)
    raise ValueError(f"unknown backend: {name}")


def annotate_features(
    propositions: list[Proposition],
    passage: Passage | BlindedPassage,
    ontology: Ontology,
    backend: AnnotationBackend | None = None,
) -> list[FeatureAnnotation]:
    backend = backend or HeuristicAnnotationBackend()
    return backend.annotate_features(passage, propositions, ontology)
