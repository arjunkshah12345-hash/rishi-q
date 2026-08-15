"""Cluster-aware motif significance (work-level resampling).

Passages from the same work are not treated as independent.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from rishiq.discovery import RishiMotif


def _work_motif_presence(
    motif: RishiMotif,
    passage_to_work: dict[str, str],
    passage_to_role: dict[str, str],
) -> dict[str, dict[str, int]]:
    """Aggregate motif presence to work level: work -> {role, present}."""
    works: dict[str, dict[str, Any]] = {}
    for pid in motif.passages:
        work = passage_to_work.get(pid, "unknown")
        role = passage_to_role.get(pid, "unknown")
        if work not in works:
            works[work] = {"role": role, "present": 1}
        else:
            works[work]["present"] = 1
    return works  # type: ignore[return-value]


def cluster_enrichment_bootstrap(
    motif: RishiMotif,
    *,
    passage_to_work: dict[str, str],
    passage_to_role: dict[str, str],
    all_works: dict[str, str],
    n_boot: int = 999,
    seed: int = 42,
) -> dict[str, Any]:
    """Bootstrap enrichment at the work cluster level.

    all_works: work_id -> role (target|control|...)
    Enrichment = P(motif|target works) / P(motif|control works)
    """
    rng = np.random.default_rng(seed)
    present_works = set()
    for pid in motif.passages:
        w = passage_to_work.get(pid)
        if w:
            present_works.add(w)

    target_works = [w for w, r in all_works.items() if r == "target"]
    control_works = [
        w for w, r in all_works.items() if r in {"control", "negative_control"}
    ]
    if not target_works or not control_works:
        return {
            "motif_id": motif.motif_id,
            "status": "insufficient_clusters",
            "enrichment": None,
            "ci95": None,
            "p_boot": None,
        }

    def _enrich(t_set: list[str], c_set: list[str]) -> float:
        pt = sum(1 for w in t_set if w in present_works) / max(len(t_set), 1)
        pc = sum(1 for w in c_set if w in present_works) / max(len(c_set), 1)
        if pc == 0:
            return float("inf") if pt > 0 else 1.0
        return pt / pc

    observed = _enrich(target_works, control_works)
    boots: list[float] = []
    # Resample works with replacement within role
    for _ in range(n_boot):
        t_s = list(rng.choice(target_works, size=len(target_works), replace=True))
        c_s = list(rng.choice(control_works, size=len(control_works), replace=True))
        e = _enrich(t_s, c_s)
        if e == float("inf"):
            e = 50.0  # cap for CI stability
        boots.append(e)

    boots_a = np.asarray(boots, dtype=float)
    obs_cap = 50.0 if observed == float("inf") else observed
    # two-sided: how often |log e| as extreme as observed under null of shuffle labels
    # Null: shuffle role labels across all eligible works
    nulls: list[float] = []
    pool = target_works + control_works
    n_t = len(target_works)
    for _ in range(n_boot):
        perm = rng.permutation(pool)
        t_s = list(perm[:n_t])
        c_s = list(perm[n_t:])
        e = _enrich(t_s, c_s)
        nulls.append(50.0 if e == float("inf") else e)
    nulls_a = np.asarray(nulls, dtype=float)
    p_boot = float(np.mean(np.abs(np.log(nulls_a + 1e-9)) >= abs(np.log(obs_cap + 1e-9))))

    return {
        "motif_id": motif.motif_id,
        "status": "ok",
        "n_target_works": len(target_works),
        "n_control_works": len(control_works),
        "n_present_works": len(present_works),
        "enrichment_work_level": None if observed == float("inf") else float(observed),
        "enrichment_infinite": observed == float("inf"),
        "ci95": [float(np.percentile(boots_a, 2.5)), float(np.percentile(boots_a, 97.5))],
        "p_boot_two_sided": p_boot,
        "note": "Work-cluster bootstrap; p is secondary to effect size / replication.",
    }


def mine_feature_combinations(
    passage_features: dict[str, set[str]],
    meta: dict[str, dict[str, str]],
    *,
    min_support: int = 3,
    max_size: int = 4,
) -> list[dict[str, Any]]:
    """Association-style combinatorial discovery on feature co-occurrence (no physics labels)."""
    from itertools import combinations
    from collections import Counter

    support: Counter[frozenset[str]] = Counter()
    owners: dict[frozenset[str], list[str]] = defaultdict(list)
    for pid, feats in passage_features.items():
        items = sorted(feats)
        if len(items) < 2:
            continue
        for k in range(2, min(max_size, len(items)) + 1):
            for combo in combinations(items, k):
                s = frozenset(combo)
                support[s] += 1
                owners[s].append(pid)

    rows = []
    for i, (sig, n) in enumerate(support.most_common(100), 1):
        if n < min_support:
            continue
        trad: Counter[str] = Counter()
        for pid in owners[sig]:
            trad[meta.get(pid, {}).get("tradition", "unknown")] += 1
        rows.append(
            {
                "combo_id": f"C{i:03d}",
                "features": sorted(sig),
                "support": n,
                "traditions": dict(trad),
                "n_traditions": len(trad),
                "passages": owners[sig][:20],
            }
        )
    return rows
