"""Structural similarity metrics and quantum specificity scoring."""

from __future__ import annotations

from typing import Iterable

from rishiq.fingerprints import TheoryFingerprint
from rishiq.models import AnnotationLabel, FeatureAnnotation, FeatureVector, TheoryScore, label_to_numeric


def annotations_to_vector(
    passage_id: str,
    annotations: Iterable[FeatureAnnotation],
    feature_ids: list[str],
    ontology_version: str,
) -> FeatureVector:
    by_f = {a.feature_id: a for a in annotations}
    values: dict[str, float | None] = {}
    labels: dict[str, AnnotationLabel] = {}
    for fid in feature_ids:
        if fid not in by_f:
            labels[fid] = AnnotationLabel.NA
            values[fid] = None
            continue
        ann = by_f[fid]
        labels[fid] = ann.label
        values[fid] = label_to_numeric(ann.label)
    return FeatureVector(
        passage_id=passage_id,
        values=values,
        labels=labels,
        ontology_version=ontology_version,
    )


def weighted_jaccard(
    x: dict[str, float | None],
    t: dict[str, float],
    weights: dict[str, float] | None = None,
) -> float:
    """Missing/NA on passage excluded from num and den (decision log)."""
    keys = [k for k in t if x.get(k) is not None]
    if not keys:
        return 0.0
    w = weights or {k: 1.0 for k in keys}
    num = 0.0
    den = 0.0
    for k in keys:
        wk = float(w.get(k, 1.0))
        xv = float(x[k])  # type: ignore[arg-type]
        tv = float(t.get(k, 0.0))
        num += wk * min(xv, tv)
        den += wk * max(xv, tv)
    return 0.0 if den == 0 else num / den


def unweighted_jaccard(x: dict[str, float | None], t: dict[str, float]) -> float:
    return weighted_jaccard(x, t, weights={k: 1.0 for k in t})


def dice_binary(x: dict[str, float | None], t: dict[str, float]) -> float:
    keys = [k for k in t if x.get(k) is not None]
    if not keys:
        return 0.0
    xs = {k for k in keys if x[k] == 1.0}
    ts = {k for k in keys if t.get(k, 0) == 1}
    if not xs and not ts:
        return 0.0
    return 2 * len(xs & ts) / (len(xs) + len(ts))


METRICS = {
    "weighted_jaccard": weighted_jaccard,
    "unweighted_jaccard": unweighted_jaccard,
    "dice": dice_binary,
}


def score_against_theory(
    vector: FeatureVector,
    fingerprint: TheoryFingerprint,
    metric: str = "weighted_jaccard",
) -> TheoryScore:
    fn = METRICS[metric]
    t = {k: float(v) for k, v in fingerprint.features.items()}
    if metric == "weighted_jaccard":
        score = fn(vector.values, t, fingerprint.weights)  # type: ignore[misc]
    else:
        score = fn(vector.values, t)  # type: ignore[misc]
    return TheoryScore(
        passage_id=vector.passage_id,
        theory_id=fingerprint.theory_id,
        score=float(score),
        metric=metric,
        ontology_version=vector.ontology_version,
        fingerprint_version=fingerprint.version,
    )


def score_all_theories(
    vector: FeatureVector,
    fingerprints: dict[str, TheoryFingerprint],
    metric: str = "weighted_jaccard",
) -> list[TheoryScore]:
    return [score_against_theory(vector, fp, metric=metric) for fp in fingerprints.values()]


def quantum_specificity_score(
    scores: list[TheoryScore],
    *,
    quantum_ids: Iterable[str] = ("quantum_mechanics", "quantum_field_theory"),
    classical_ids: Iterable[str] = (
        "newtonian",
        "classical_em",
        "thermodynamics",
        "relativity",
    ),
) -> float:
    """QS = max quantum similarity - max classical similarity."""
    by = {s.theory_id: s.score for s in scores}
    q = max((by.get(i, 0.0) for i in quantum_ids), default=0.0)
    c = max((by.get(i, 0.0) for i in classical_ids), default=0.0)
    return q - c


def quantum_exclusive_feature_score(
    vector: FeatureVector,
    qef_features: list[str],
) -> float:
    """QEF = (# explicit quantum-specific features) / (# eligible)."""
    eligible = [f for f in qef_features if vector.values.get(f) is not None]
    if not eligible:
        return 0.0
    positive = sum(1 for f in eligible if vector.values.get(f) == 1.0)
    return positive / len(eligible)
