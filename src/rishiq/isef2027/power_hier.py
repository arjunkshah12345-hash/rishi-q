"""Hierarchical work-level permutation power for Δ_Q (confirmatory design).

SOFTWARE / DESIGN tool — parameters marked UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE
must not be invented to force a convenient N.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance
from rishiq.isef2027.inference import work_level_permutation


@dataclass
class PowerAssumptions:
    effect_delta_q: float
    n_works_per_arm: int
    passages_per_work: int
    between_work_sd: float | str  # float or "UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE"
    within_work_sd: float | str
    missingness_rate: float = 0.0
    n_sim: int = 400
    n_perm: int = 199
    alpha: float = 0.05
    seed: int = 20270816
    notes: str = ""

    def resolved(self) -> tuple[dict[str, Any], bool]:
        """Return assumption dict and whether all critical params are numeric."""
        unknown = []
        out: dict[str, Any] = asdict(self)
        for k in ("between_work_sd", "within_work_sd"):
            if isinstance(getattr(self, k), str):
                unknown.append(k)
        out["unknown_parameters"] = unknown
        out["ready_for_sample_size_freeze"] = len(unknown) == 0
        return out, len(unknown) == 0


def _as_float(x: float | str, default: float) -> float:
    if isinstance(x, str):
        return default
    return float(x)


def simulate_delta_q_power(assumptions: PowerAssumptions) -> dict[str, Any]:
    """Monte Carlo power under work-level mean Δ_Q permutation test."""
    meta, ready = assumptions.resolved()
    # For software exercise when UNKNOWN, use labeled provisional defaults WITHOUT claiming freeze-ready
    bw = _as_float(assumptions.between_work_sd, 0.08)
    ww = _as_float(assumptions.within_work_sd, 0.12)
    provisional = isinstance(assumptions.between_work_sd, str) or isinstance(assumptions.within_work_sd, str)

    rng = np.random.default_rng(assumptions.seed)
    rejects = 0
    deltas = []
    for s in range(assumptions.n_sim):
        t_means: dict[str, float] = {}
        c_means: dict[str, float] = {}
        for i in range(assumptions.n_works_per_arm):
            tw = rng.normal(assumptions.effect_delta_q, bw)
            cw = rng.normal(0.0, bw)
            t_pass = []
            c_pass = []
            for _ in range(assumptions.passages_per_work):
                if rng.random() < assumptions.missingness_rate:
                    continue
                t_pass.append(tw + rng.normal(0, ww))
                c_pass.append(cw + rng.normal(0, ww))
            if t_pass:
                t_means[f"T{i}"] = float(np.mean(t_pass))
            if c_pass:
                c_means[f"C{i}"] = float(np.mean(c_pass))
        if len(t_means) < 2 or len(c_means) < 2:
            continue
        res = work_level_permutation(
            t_means,
            c_means,
            n_perm=assumptions.n_perm,
            seed=int(rng.integers(0, 1_000_000)),
        )
        deltas.append(res["observed_delta"])
        # one-sided via p_ge_obs on positive observed delta
        p_one = float(res["p_ge_obs"]) if res["observed_delta"] > 0 else 1.0
        if p_one < assumptions.alpha:
            rejects += 1

    n_ok = max(len(deltas), 1)
    power = rejects / assumptions.n_sim
    # Monte Carlo SE of binomial proportion
    mc_se = float(np.sqrt(power * (1 - power) / assumptions.n_sim))
    # Normal approx 95% simulation interval for power estimate
    z = 1.96
    lo = float(max(0.0, power - z * mc_se))
    hi = float(min(1.0, power + z * mc_se))
    payload = {
        "analysis_id": "ISEF2027-POWER-HIER-v2",
        "primary_test": "work_level_permutation_one_sided_delta_q",
        "assumptions": meta,
        "provisional_defaults_used": provisional,
        "ready_for_sample_size_freeze": ready and not provisional,
        "n_sim": assumptions.n_sim,
        "empirical_power": power,
        "monte_carlo_se": mc_se,
        "power_sim_interval_95": [lo, hi],
        "mean_observed_delta": float(np.mean(deltas)) if deltas else float("nan"),
        "label": "DESIGN_SIMULATION"
        if ready
        else "PROVISIONAL_SIMULATION_UNKNOWN_VARIANCE",
    }
    return attach_provenance(
        payload,
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.SOFTWARE_DEMO if provisional else EvidenceClass.DEVELOPMENT_ANALYSIS,
            synthetic=True,
            real_text=False,
            phase="calibration",
            source_split="simulation",
            method_version="power_hier_v2",
            notes="Hierarchical Δ_Q power; not confirmatory evidence.",
        ),
    )


def power_grid(
    *,
    effects: list[float],
    works_grid: list[int],
    passages_grid: list[int],
    between_work_sd: float | str,
    within_work_sd: float | str,
    missingness_rate: float = 0.05,
    n_sim: int = 200,
    seed: int = 20270816,
) -> dict[str, Any]:
    rows = []
    for e in effects:
        for nw in works_grid:
            for ppw in passages_grid:
                a = PowerAssumptions(
                    effect_delta_q=e,
                    n_works_per_arm=nw,
                    passages_per_work=ppw,
                    between_work_sd=between_work_sd,
                    within_work_sd=within_work_sd,
                    missingness_rate=missingness_rate,
                    n_sim=n_sim,
                    seed=seed,
                )
                rows.append(simulate_delta_q_power(a))
    return attach_provenance(
        {
            "grid_id": "ISEF2027-POWER-GRID-v2",
            "n_cells": len(rows),
            "rows": rows,
            "interpretation": (
                "Do not freeze confirmatory N from provisional cells where variance is UNKNOWN. "
                "Use empirical ICC/variance from calibration real scores first."
            ),
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.SOFTWARE_DEMO,
            synthetic=True,
            real_text=False,
            phase="calibration",
            source_split="simulation",
            method_version="power_hier_v2",
        ),
    )
