"""Claims-vs-data: curated popular/scholarly claims tested against ontology scores."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from rishiq.models import AnnotationLabel, FeatureAnnotation


DEFAULT_CLAIMS = [
    {
        "claim_id": "C01",
        "claim": "prāṇa = energy",
        "kind": "popular",
        "required_features": ["D03", "F03"],
        "quantum_features": [],
        "notes": "Energy as dynamical activity, not necessarily quantum.",
    },
    {
        "claim_id": "C02",
        "claim": "ākāśa = quantum field",
        "kind": "popular",
        "required_features": ["F01", "F02", "O04"],
        "quantum_features": ["Q01", "Q03", "Q06", "Q08"],
        "notes": "Field-like support ≠ quantum-specific support.",
    },
    {
        "claim_id": "C03",
        "claim": "spanda = quantum vibration",
        "kind": "popular",
        "required_features": ["D03", "F06"],
        "quantum_features": ["Q01", "Q02"],
    },
    {
        "claim_id": "C04",
        "claim": "Brahman = unified field",
        "kind": "popular",
        "required_features": ["O01", "F01", "O05"],
        "quantum_features": ["Q08"],
    },
    {
        "claim_id": "C05",
        "claim": "observer consciousness = measurement effect",
        "kind": "popular",
        "required_features": ["M01", "M02"],
        "quantum_features": ["Q04", "Q07"],
    },
    {
        "claim_id": "C06",
        "claim": "oneness = entanglement",
        "kind": "popular",
        "required_features": ["O01", "O02"],
        "quantum_features": ["Q06"],
        "notes": "Unity ≠ entanglement; Q06 required for quantum reading.",
    },
    {
        "claim_id": "C07",
        "claim": "aṇu = quantum particle",
        "kind": "popular",
        "required_features": ["O03"],
        "quantum_features": ["Q01", "Q05"],
    },
]


def load_claims(path: Path | None = None) -> list[dict[str, Any]]:
    if path and path.exists():
        data = yaml.safe_load(path.read_text())
        return list(data.get("claims", data))
    return list(DEFAULT_CLAIMS)


def evaluate_claim(
    claim: dict[str, Any],
    annotations_by_passage: dict[str, list[FeatureAnnotation]],
    tradition_filter: set[str] | None = None,
    meta: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    meta = meta or {}
    req = set(claim.get("required_features", []))
    qf = set(claim.get("quantum_features", []))

    feature_hits = {f: 0 for f in req | qf}
    n_passages = 0
    n_with_any_req = 0
    n_with_all_req = 0
    n_with_any_q = 0
    n_with_all_q = 0

    for pid, anns in annotations_by_passage.items():
        if tradition_filter:
            trad = meta.get(pid, {}).get("tradition")
            if trad not in tradition_filter:
                continue
        n_passages += 1
        yes = {
            a.feature_id
            for a in anns
            if a.label == AnnotationLabel.YES and a.evidence.strip()
        }
        for f in feature_hits:
            if f in yes:
                feature_hits[f] += 1
        if yes & req:
            n_with_any_req += 1
        if req and req <= yes:
            n_with_all_req += 1
        if yes & qf:
            n_with_any_q += 1
        if qf and qf <= yes:
            n_with_all_q += 1

    supported_components = [f for f in req if feature_hits.get(f, 0) > 0]
    unsupported = [f for f in req if feature_hits.get(f, 0) == 0]
    contradicted: list[str] = []
    q_supported = [f for f in qf if feature_hits.get(f, 0) > 0]
    q_unsupported = [f for f in qf if feature_hits.get(f, 0) == 0]

    if q_supported and n_with_any_q > 0:
        best = "partial_quantum_overlap"
    elif supported_components and not q_supported:
        best = "classical_or_field_like_ontology"
    elif not supported_components:
        best = "unsupported_in_sample"
    else:
        best = "mixed"

    if claim["claim_id"] == "C02" and supported_components and not q_supported:
        best = "classical_field_like_ontology"

    return {
        "claim_id": claim["claim_id"],
        "claim": claim["claim"],
        "kind": claim.get("kind", "popular"),
        "n_passages_examined": n_passages,
        "SUPPORTED_STRUCTURAL_COMPONENTS": supported_components,
        "UNSUPPORTED_COMPONENTS": unsupported,
        "CONTRADICTED_COMPONENTS": contradicted,
        "QUANTUM_SUPPORTED": q_supported,
        "QUANTUM_UNSUPPORTED": q_unsupported,
        "rates": {
            "any_required": n_with_any_req / max(n_passages, 1),
            "all_required": n_with_all_req / max(n_passages, 1),
            "any_quantum": n_with_any_q / max(n_passages, 1),
            "all_quantum": n_with_all_q / max(n_passages, 1),
        },
        "BEST_PHYSICS_MATCH": best,
        "TRANSLATION_DEPENDENCE": "untested",
        "EVIDENCE_QUALITY": "exploratory_heuristic"
        if n_passages
        else "no_data",
        "notes": claim.get("notes", ""),
    }
