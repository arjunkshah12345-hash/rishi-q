"""Role-aware structural graph similarity (not literal node-ID matching).

Methods kept (scientifically justified subset):
  A) Typed relation multiset Jaccard on (src_kind, edge_kind, tgt_kind)
  E) Optimal assignment of nodes by kind + neighborhood signatures (Hungarian)

Hungarian size-mismatch policy (Pass 3 Option B):
  similarity = matched_quality * coverage
  coverage = n_real_matches / max(|A|, |B|)
  Dummy-pad assignment cells are NOT discarded from the size penalty:
  unmatched node mass lowers coverage even when matched pairs are perfect.

Primary structural blend weights are configurable; default is provisional
until development-only weight selection freezes a candidate.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

from rishiq.isef2027.concept_graph import ConceptGraph, EdgeKind, graph_overlap_score

# Provisional defaults — may be overwritten by frozen method config after DEV selection.
DEFAULT_TYPED_WEIGHT = 0.55
DEFAULT_HUNGARIAN_WEIGHT = 0.45
PAD_COST = 3.0


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
    keys = set(sa[1]) | set(sb[1]) | set(sa[2]) | set(sb[2])
    if not keys:
        hist = 0.0
    else:
        hist = sum(abs(sa[1][k] - sb[1][k]) + abs(sa[2][k] - sb[2][k]) for k in keys)
        hist = hist / (
            2.0
            * max(
                1,
                sum(sa[1].values())
                + sum(sa[2].values())
                + sum(sb[1].values())
                + sum(sb[2].values()),
            )
        )
    return kind_pen + hist


def hungarian_role_alignment_similarity(a: ConceptGraph, b: ConceptGraph) -> float:
    """Method E with explicit size-mismatch penalty (Option B).

    1. Build padded square cost matrix (pad cost = PAD_COST).
    2. Hungarian assignment.
    3. Quality = 1 - mean(cost) over *real–real* matches only (cost mapped /2).
    4. Coverage = n_real_matches / max(|A|, |B|).
    5. Return quality * coverage.

    Unmatched nodes therefore lower similarity even when matched pairs are perfect.
    """
    na = [n.id for n in a.nodes]
    nb = [n.id for n in b.nodes]
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    sa = [_node_signature(a, i) for i in na]
    sb = [_node_signature(b, i) for i in nb]
    n = max(len(na), len(nb))
    cost = np.full((n, n), PAD_COST)
    for i in range(len(na)):
        for j in range(len(nb)):
            cost[i, j] = _sig_distance(sa[i], sb[j])
    r, c = linear_sum_assignment(cost)
    matched = [(i, j) for i, j in zip(r, c) if i < len(na) and j < len(nb)]
    if not matched:
        return 0.0
    mean_cost = float(np.mean([cost[i, j] for i, j in matched]))
    quality = float(max(0.0, 1.0 - mean_cost / 2.0))
    coverage = float(len(matched) / n)
    return float(quality * coverage)


def structural_similarity_bundle(
    a: ConceptGraph,
    b: ConceptGraph,
    *,
    typed_weight: float | None = None,
    hungarian_weight: float | None = None,
) -> dict[str, float]:
    tw = DEFAULT_TYPED_WEIGHT if typed_weight is None else float(typed_weight)
    hw = DEFAULT_HUNGARIAN_WEIGHT if hungarian_weight is None else float(hungarian_weight)
    tr = typed_relation_similarity(a, b)
    hu = hungarian_role_alignment_similarity(a, b)
    return {
        "literal_id_overlap_baseline": graph_overlap_score(a, b),
        "typed_relation_multiset": tr,
        "hungarian_role_alignment": hu,
        "primary_structural": float(tw * tr + hw * hu),
        "typed_weight": tw,
        "hungarian_weight": hw,
    }


def pairwise_fingerprint_matrix(
    graphs: dict[str, ConceptGraph],
    *,
    typed_weight: float | None = None,
    hungarian_weight: float | None = None,
) -> dict[str, Any]:
    tw = DEFAULT_TYPED_WEIGHT if typed_weight is None else float(typed_weight)
    hw = DEFAULT_HUNGARIAN_WEIGHT if hungarian_weight is None else float(hungarian_weight)
    ids = sorted(graphs)
    mat = {i: {j: 0.0 for j in ids} for i in ids}
    detail = {}
    for i in ids:
        for j in ids:
            bund = structural_similarity_bundle(
                graphs[i], graphs[j], typed_weight=tw, hungarian_weight=hw
            )
            mat[i][j] = bund["primary_structural"]
            detail[f"{i}__{j}"] = bund
    return {
        "method": f"primary={tw}*typed_relation+{hw}*hungarian_coverage_penalized",
        "size_mismatch_policy": "Option_B_quality_times_coverage",
        "matrix": mat,
        "pairwise_detail": detail,
    }
