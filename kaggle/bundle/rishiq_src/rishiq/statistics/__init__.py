"""Statistical analysis: effects, bootstrap, permutation, power."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass
class EffectEstimate:
    estimate: float
    ci_low: float
    ci_high: float
    n_target: int
    n_control: int
    method: str


def mean_difference(target: Sequence[float], control: Sequence[float]) -> float:
    return float(np.mean(target) - np.mean(control))


def cluster_bootstrap_ci(
    values: Sequence[float],
    clusters: Sequence[str],
    *,
    n_boot: int = 1000,
    seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Bootstrap CI resampling entire clusters."""
    rng = np.random.default_rng(seed)
    values = np.asarray(values, dtype=float)
    clusters = np.asarray(list(clusters))
    uniq = np.unique(clusters)
    means = []
    for _ in range(n_boot):
        chosen = rng.choice(uniq, size=len(uniq), replace=True)
        mask = np.isin(clusters, chosen)
        # reweight by multiplicity of chosen clusters
        sample = []
        for c in chosen:
            sample.extend(values[clusters == c].tolist())
        means.append(np.mean(sample) if sample else np.nan)
    means = np.asarray(means, dtype=float)
    means = means[~np.isnan(means)]
    lo = float(np.quantile(means, alpha / 2))
    hi = float(np.quantile(means, 1 - alpha / 2))
    return float(np.mean(values)), lo, hi


def cluster_permutation_pvalue(
    target_values: Sequence[float],
    target_clusters: Sequence[str],
    control_values: Sequence[float],
    control_clusters: Sequence[str],
    *,
    n_perm: int = 1000,
    seed: int = 42,
    alternative: str = "greater",
) -> dict:
    """Shuffle tradition labels at cluster level."""
    rng = np.random.default_rng(seed)
    obs = mean_difference(target_values, control_values)
    # Build cluster-level means
    t_map: dict[str, list[float]] = {}
    for v, c in zip(target_values, target_clusters):
        t_map.setdefault(c, []).append(float(v))
    c_map: dict[str, list[float]] = {}
    for v, c in zip(control_values, control_clusters):
        c_map.setdefault(c, []).append(float(v))
    labels = [(k, "T") for k in t_map] + [(k, "C") for k in c_map]
    all_means = {**{k: float(np.mean(v)) for k, v in t_map.items()}, **{k: float(np.mean(v)) for k, v in c_map.items()}}
    null = []
    keys = [k for k, _ in labels]
    for _ in range(n_perm):
        assign = rng.permutation([lab for _, lab in labels])
        t = [all_means[k] for k, a in zip(keys, assign) if a == "T"]
        c = [all_means[k] for k, a in zip(keys, assign) if a == "C"]
        if not t or not c:
            continue
        null.append(float(np.mean(t) - np.mean(c)))
    null_arr = np.asarray(null, dtype=float)
    if alternative == "greater":
        p = float((np.sum(null_arr >= obs) + 1) / (len(null_arr) + 1))
    else:
        p = float((np.sum(np.abs(null_arr) >= abs(obs)) + 1) / (len(null_arr) + 1))
    return {
        "observed_delta": obs,
        "p_value": p,
        "n_perm": len(null_arr),
        "null_mean": float(np.mean(null_arr)) if len(null_arr) else float("nan"),
    }


def bh_fdr(p_values: Sequence[float], q: float = 0.05) -> list[bool]:
    """Benjamini–Hochberg FDR control."""
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    thresh = q * (np.arange(1, n + 1) / n)
    below = ranked <= thresh
    if not np.any(below):
        return [False] * n
    max_i = np.max(np.where(below)[0])
    cut = ranked[max_i]
    return [bool(x <= cut) for x in p]


def power_simulation(
    *,
    effect: float,
    n_clusters_per_arm: int,
    passages_per_cluster: int,
    noise_sd: float = 0.15,
    icc: float = 0.2,
    n_sim: int = 200,
    seed: int = 42,
    alpha: float = 0.05,
) -> dict:
    """Simple cluster-randomized power simulation for mean QS difference."""
    rng = np.random.default_rng(seed)
    detections = 0
    for _ in range(n_sim):
        def arm(shift: float) -> tuple[list[float], list[str]]:
            vals = []
            clus = []
            for j in range(n_clusters_per_arm):
                cluster_effect = rng.normal(0, np.sqrt(icc) * noise_sd)
                for k in range(passages_per_cluster):
                    vals.append(shift + cluster_effect + rng.normal(0, noise_sd))
                    clus.append(f"c{j}")
            return vals, clus

        t_v, t_c = arm(effect)
        c_v, c_c = arm(0.0)
        # rename control clusters
        c_c = [f"k{x}" for x in c_c]
        res = cluster_permutation_pvalue(
            t_v, t_c, c_v, c_c, n_perm=99, seed=int(rng.integers(0, 1_000_000))
        )
        if res["p_value"] < alpha:
            detections += 1
    return {
        "effect": effect,
        "n_clusters_per_arm": n_clusters_per_arm,
        "passages_per_cluster": passages_per_cluster,
        "n_sim": n_sim,
        "power": detections / n_sim,
        "alpha": alpha,
    }


def recommend_sample_sizes(
    effects: Sequence[float] = (0.05, 0.1, 0.15),
    cluster_grid: Sequence[int] = (10, 20, 40, 80),
    passages_per_cluster: int = 10,
    target_power: float = 0.8,
    seed: int = 42,
    n_sim: int = 40,
) -> list[dict]:
    """Exploratory power grid. Increase n_sim on Kaggle before freezing confirmatory n."""
    rows = []
    for e in effects:
        for nc in cluster_grid:
            sim = power_simulation(
                effect=e,
                n_clusters_per_arm=nc,
                passages_per_cluster=passages_per_cluster,
                n_sim=n_sim,
                seed=seed,
            )
            rows.append({**sim, "meets_target": sim["power"] >= target_power})
    return rows
