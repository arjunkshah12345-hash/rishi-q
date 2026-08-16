"""Role-aware structural graph similarity (not literal node-ID matching).

Methods kept (scientifically justified subset):
  A) Typed relation multiset Jaccard on (src_kind, edge_kind, tgt_kind)
  E) Optimal assignment of nodes by kind + neighborhood signatures (Hungarian)

Literal ID overlap remains available as a diagnostic baseline only.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

from rishiq.isef2027.concept_graph import ConceptGraph, EdgeKind, graph_overlap_score


def typed_relation_multiset(g: ConceptGraph) -> Counter[tuple[str, str, str]]:
    """Method A: ignore node IDs; count (source_kind, edge_kind, target_kind)."""
    kind = {n.id: n.kind.value for n in g.nodes}
    c: Counter[tuple[str, str, str]] = Counter()
    for e in g.edges:
        sk = kind.get(e.source, "UNKNOWN")
        tk = kind.get(e.target, "UNKNOWN")
        c[(sk, e.kind.value, tk)] += 1
    return c


def multiset_jaccard(a: Counter, b: Counter) -> float:
    if not a and not b:
        return 1.0
    keys = set(a) | set(b)
    inter = sum(min(a[k], b[k]) for k in keys)
    union = sum(max(a[k], b[k]) for k in keys)
    return float(inter / union) if union else 0.0


def typed_relation_similarity(a: ConceptGraph, b: ConceptGraph) -> float:
    return multiset_jaccard(typed_relation_multiset(a), typed_relation_multiset(b))


def _node_signature(g: ConceptGraph, node_id: str) -> tuple[str, Counter[str], Counter[str]]:
    kind_map = {n.id: n.kind.value for n in g.nodes}
    out_e: Counter[str] = Counter()
    in_e: Counter[str] = Counter()
    for e in g.edges:
        if e.source == node_id:
            out_e[e.kind.value] += 1
        if e.target == node_id:
            in_e[e.kind.value] += 1
    return kind_map.get(node_id, "UNKNOWN"), out_e, in_e


def _sig_distance(sa: tuple[str, Counter, Counter], sb: tuple[str, Counter, Counter]) -> float:
    kind_pen = 0.0 if sa[0] == sb[0] else 1.0
    # edge-kind histogram L1
    keys = set(sa[1]) | set(sb[1]) | set(sa[2]) | set(sb[2])
    if not keys:
        hist = 0.0
    else:
        hist = sum(abs(sa[1][k] - sb[1][k]) + abs(sa[2][k] - sb[2][k]) for k in keys)
        hist = hist / (2.0 * max(1, sum(sa[1].values()) + sum(sa[2].values()) + sum(sb[1].values()) + sum(sb[2].values())))
    return kind_pen + hist


def hungarian_role_alignment_similarity(a: ConceptGraph, b: ConceptGraph) -> float:
    """Method E: map nodes maximizing kind+neighborhood agreement; return 1 - mean cost."""
    na = [n.id for n in a.nodes]
    nb = [n.id for n in b.nodes]
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    sa = [_node_signature(a, i) for i in na]
    sb = [_node_signature(b, i) for i in nb]
    # Pad to square with high cost
    n = max(len(na), len(nb))
    cost = np.full((n, n), 3.0)
    for i in range(len(na)):
        for j in range(len(nb)):
            cost[i, j] = _sig_distance(sa[i], sb[j])
    r, c = linear_sum_assignment(cost)
    matched = [(i, j) for i, j in zip(r, c) if i < len(na) and j < len(nb)]
    if not matched:
        return 0.0
    mean_cost = float(np.mean([cost[i, j] for i, j in matched]))
    # Map cost in [0, ~3] → similarity
    return float(max(0.0, 1.0 - mean_cost / 2.0))


def structural_similarity_bundle(a: ConceptGraph, b: ConceptGraph) -> dict[str, float]:
    return {
        "literal_id_overlap_baseline": graph_overlap_score(a, b),
        "typed_relation_multiset": typed_relation_similarity(a, b),
        "hungarian_role_alignment": hungarian_role_alignment_similarity(a, b),
        "primary_structural": float(
            0.55 * typed_relation_similarity(a, b) + 0.45 * hungarian_role_alignment_similarity(a, b)
        ),
    }


def pairwise_fingerprint_matrix(graphs: dict[str, ConceptGraph]) -> dict[str, Any]:
    ids = sorted(graphs)
    mat = {i: {j: 0.0 for j in ids} for i in ids}
    detail = {}
    for i in ids:
        for j in ids:
            bund = structural_similarity_bundle(graphs[i], graphs[j])
            mat[i][j] = bund["primary_structural"]
            detail[f"{i}__{j}"] = bund
    return {"method": "primary=0.55*typed_relation+0.45*hungarian", "matrix": mat, "pairwise_detail": detail}
