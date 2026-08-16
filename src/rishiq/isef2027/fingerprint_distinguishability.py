"""Fingerprint distinguishability diagnostics (no auto-edits to fingerprints)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rishiq.isef2027.concept_graph import ConceptGraph
from rishiq.isef2027.graph_similarity import (
    pairwise_fingerprint_matrix,
    typed_relation_multiset,
    typed_relation_similarity,
)
from rishiq.isef2027.graph_templates import build_all_theory_graph_templates


def fingerprint_distinguishability_report(root: Path) -> dict[str, Any]:
    build_all_theory_graph_templates(root)
    gdir = root / "ontology/concept_graph"
    graphs = {}
    for p in gdir.glob("template_fp_*.json"):
        g = ConceptGraph.model_validate(json.loads(p.read_text(encoding="utf-8")))
        tid = p.stem.replace("template_fp_", "")
        graphs[tid] = g

    mat = pairwise_fingerprint_matrix(graphs)
    ids = sorted(graphs)
    nearest = {}
    flags = []
    for i in ids:
        others = [(j, mat["matrix"][i][j]) for j in ids if j != i]
        others.sort(key=lambda x: -x[1])
        nearest[i] = {"neighbor": others[0][0], "similarity": others[0][1]}
        if others[0][1] >= 0.85:
            flags.append(f"NEAR_INDISTINGUISHABLE:{i}≈{others[0][0]}@{others[0][1]:.3f}")

    multisets = {i: typed_relation_multiset(graphs[i]) for i in ids}
    pairwise = []
    for a in ids:
        for b in ids:
            if a >= b:
                continue
            sa, sb = set(multisets[a]), set(multisets[b])
            pairwise.append(
                {
                    "a": a,
                    "b": b,
                    "shared_features": len(sa & sb),
                    "unique_a": len(sa - sb),
                    "unique_b": len(sb - sa),
                    "typed_jaccard": typed_relation_similarity(graphs[a], graphs[b]),
                    "primary_structural": mat["matrix"][a][b],
                }
            )

    payload = {
        "physics_fingerprints_verified": False,
        "student_review_required": True,
        "n_fingerprints": len(ids),
        "nearest_neighbor": nearest,
        "flags": flags,
        "pairwise": pairwise,
        "matrix_method": mat["method"],
        "note": "Do not modify fingerprints solely to improve classifier scores.",
    }
    out = root / "results/isef2027/validation/fingerprint_distinguishability.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
