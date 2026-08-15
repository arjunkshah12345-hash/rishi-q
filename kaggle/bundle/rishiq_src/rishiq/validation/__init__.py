"""Evidence verification for annotations."""

from __future__ import annotations

import re

from rishiq.models import AnnotationLabel, FeatureAnnotation
from rishiq.models.ontology import Ontology

METAPHOR_BLOCKLIST = re.compile(
    r"\b(like|as if|metaphorically|symbolically)\b",
    re.I,
)


def verify_evidence(
    annotation: FeatureAnnotation,
    passage_text: str,
    ontology: Ontology | None = None,
) -> FeatureAnnotation:
    flags: list[str] = []
    label = annotation.label
    evidence = annotation.evidence.strip()

    if label == AnnotationLabel.YES:
        if not evidence:
            flags.append("missing_evidence")
            label = AnnotationLabel.NA
        elif evidence.lower() not in passage_text.lower() and not _fuzzy_in(
            evidence, passage_text
        ):
            flags.append("evidence_span_not_found")
            label = AnnotationLabel.NA
        elif ontology is not None:
            feat = ontology.by_id().get(annotation.feature_id)
            if feat and feat.quantum_specific:
                if METAPHOR_BLOCKLIST.search(evidence) and not re.search(
                    r"\b(state|measurement|observables|excitation|probability)\b",
                    evidence,
                    re.I,
                ):
                    flags.append("quantum_feature_metaphor_only")
                    label = AnnotationLabel.U
                # Hard rule checks
                if annotation.feature_id == "Q06" and re.search(
                    r"everything is (one|interconnected)|all is one|interconnected",
                    evidence,
                    re.I,
                ) and not re.search(
                    r"independent component|non-?factor|joint state",
                    evidence,
                    re.I,
                ):
                    flags.append("unity_not_nonseparability")
                    label = AnnotationLabel.NO

    verified = len(flags) == 0 and label == annotation.label
    return annotation.model_copy(
        update={
            "label": label,
            "verified": verified or (label != AnnotationLabel.YES and "missing_evidence" not in flags),
            "verification_flags": flags,
            "evidence": evidence if label == AnnotationLabel.YES else (
                evidence if flags else annotation.evidence
            ),
        }
    )


def _fuzzy_in(evidence: str, text: str) -> bool:
    tokens = [t for t in re.findall(r"\w+", evidence.lower()) if len(t) > 3]
    if not tokens:
        return False
    hay = text.lower()
    hits = sum(1 for t in tokens if t in hay)
    return hits / len(tokens) >= 0.8
