"""Stronger randomization inference scaffolding (calibration/dev only)."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from rishiq.statistics import cluster_bootstrap_ci, cluster_permutation_pvalue, mean_difference


def work_level_permutation(
    work_means_target: dict[str, float],
    work_means_control: dict[str, float],
    *,
    n_perm: int = 2000,
    seed: int = 42,
) -> dict:
    """Permute work labels between target/control pools."""
    rng = np.random.default_rng(seed)
    t_keys = list(work_means_target)
    c_keys = list(work_means_control)
    all_keys = t_keys + c_keys
    all_vals = {**work_means_target, **work_means_control}
    n_t = len(t_keys)
    obs = mean_difference([work_means_target[k] for k in t_keys], [work_means_control[k] for k in c_keys])
    null = []
    for _ in range(n_perm):
        perm = rng.permutation(all_keys)
        t = [all_vals[k] for k in perm[:n_t]]
        c = [all_vals[k] for k in perm[n_t:]]
        null.append(mean_difference(t, c))
    null_a = np.asarray(null, dtype=float)
    p = float(np.mean(null_a >= obs))
    return {"observed_delta": obs, "p_ge_obs": p, "n_perm": n_perm, "seed": seed, "method": "work_level_permutation"}


def leave_one_work_out(
    passage_scores: Sequence[float],
    works: Sequence[str],
    roles: Sequence[str],
) -> dict[str, float]:
    """Recompute target-control delta omitting each work."""
    scores = np.asarray(passage_scores, dtype=float)
    works_a = np.asarray(list(works))
    roles_a = np.asarray(list(roles))
    uniq = sorted(set(works_a.tolist()))
    out = {}
    for w in uniq:
        mask = works_a != w
        t = scores[(roles_a == "target") & mask]
        c = scores[(roles_a == "control") & mask]
        out[w] = float(t.mean() - c.mean()) if len(t) and len(c) else float("nan")
    return out


def max_statistic_permutation(
    feature_deltas: dict[str, float],
    null_feature_deltas: list[dict[str, float]],
) -> dict:
    """Family-wise max-statistic using permuted feature deltas."""
    obs_max = max(abs(v) for v in feature_deltas.values()) if feature_deltas else 0.0
    null_max = [max(abs(v) for v in d.values()) if d else 0.0 for d in null_feature_deltas]
    p = float(np.mean(np.asarray(null_max) >= obs_max)) if null_max else float("nan")
    return {"obs_max_abs_delta": obs_max, "p_max_statistic": p, "n_null": len(null_max)}


def cluster_effect_bundle(
    target: Sequence[float],
    target_clusters: Sequence[str],
    control: Sequence[float],
    control_clusters: Sequence[str],
    *,
    seed: int = 42,
) -> dict:
    delta = mean_difference(target, control)
    mean, lo, hi = cluster_bootstrap_ci(
        list(target) + list(control),
        list(target_clusters) + list(control_clusters),
        seed=seed,
    )
    perm = cluster_permutation_pvalue(
        target, target_clusters, control, control_clusters, seed=seed
    )
    return {
        "delta": delta,
        "pooled_mean": mean,
        "cluster_bootstrap_ci": [lo, hi],
        "cluster_permutation": perm,
    }
