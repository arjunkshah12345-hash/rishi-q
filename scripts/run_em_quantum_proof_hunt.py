#!/usr/bin/env python3
"""Ancient EM / quantum proof-hunt (exploratory).

Goal: look as hard as the protocol allows for evidence that Hindu/Vedānta
passages carry classical-EM or quantum structural fingerprints *beyond*
Greek/Chinese/Buddhist controls — the kind of surplus that would support
an 'advanced ancient physics' reading.

If no surplus: accept defeat at the specified level (do not force a win).

Uses existing heuristic annotation scores from pd_pilot_v03 (and optional
fresh Capra-style rescored subset). Confirmatory remains locked.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "results/exploratory/pd_pilot_v03/passage_scores.parquet"
OUT = ROOT / "results/exploratory/em_quantum_proof_hunt"
FIG = ROOT / "paper/figures"

HINDU = {"vedanta_pd"}  # expand when more Indic corpora land
CONTROLS = {"greek_lucretius_pd", "greek_timaeus_pd", "buddhist_dhammapada_pd", "chinese_ddj_pd"}
PHYSICS_REF = {"modern_physics"}

THEORIES = [
    "classical_em",
    "quantum_mechanics",
    "quantum_field_theory",
    "newtonian",
    "relativity",
    "thermodynamics",
]


def mw_greater(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3 or len(b) < 3:
        return float("nan")
    return float(stats.mannwhitneyu(a, b, alternative="greater").pvalue)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(SCORES)
    # development target/control only (exclude physics_reference for main contrast)
    dev = df[df["dataset_split"] == "development"].copy()
    hindu = dev[dev["tradition"].isin(HINDU)]
    ctrl = dev[dev["tradition"].isin(CONTROLS)]
    pref = df[df["tradition"].isin(PHYSICS_REF)]

    rows = []
    for th in THEORIES + ["QS", "QEF"]:
        h = hindu[th].to_numpy(float)
        c = ctrl[th].to_numpy(float)
        p = pref[th].to_numpy(float) if len(pref) else np.array([])
        rows.append(
            {
                "metric": th,
                "hindu_mean": float(np.mean(h)),
                "hindu_median": float(np.median(h)),
                "hindu_max": float(np.max(h)),
                "hindu_frac_pos": float(np.mean(h > 0)),
                "control_mean": float(np.mean(c)),
                "control_median": float(np.median(c)),
                "control_max": float(np.max(c)),
                "control_frac_pos": float(np.mean(c > 0)),
                "physics_ref_mean": float(np.mean(p)) if len(p) else None,
                "delta_hindu_minus_control": float(np.mean(h) - np.mean(c)),
                "mannwhitney_hindu_gt_control_p": mw_greater(h, c),
                "mannwhitney_control_gt_hindu_p": mw_greater(c, h),
            }
        )
    metrics = pd.DataFrame(rows)

    # Best-of Hindu passages on EM and QM
    top_em = hindu.nlargest(10, "classical_em")[
        ["passage_id", "tradition", "work", "classical_em", "QS", "QEF", "field_class"]
    ]
    top_qm = hindu.nlargest(10, "quantum_mechanics")[
        ["passage_id", "tradition", "work", "quantum_mechanics", "QS", "QEF", "field_class"]
    ]
    top_qft = hindu.nlargest(10, "quantum_field_theory")[
        ["passage_id", "tradition", "work", "quantum_field_theory", "QS", "QEF", "field_class"]
    ]

    # Proof criteria (pre-specified for this exploratory hunt):
    # SUPPORT candidate if Hindu mean classical_em OR quantum_mechanics OR QFT
    # significantly exceeds controls (MW p<0.05) AND mean delta > 0.05
    # AND physics_ref still clearly higher (sanity: we can detect real physics text).
    em = metrics[metrics["metric"] == "classical_em"].iloc[0]
    qm = metrics[metrics["metric"] == "quantum_mechanics"].iloc[0]
    qft = metrics[metrics["metric"] == "quantum_field_theory"].iloc[0]
    qs = metrics[metrics["metric"] == "QS"].iloc[0]

    sanity_physics_detectable = bool(
        pref["classical_em"].mean() > ctrl["classical_em"].mean() + 0.2
        or pref["quantum_mechanics"].mean() > ctrl["quantum_mechanics"].mean() + 0.2
        or pref["QS"].mean() > ctrl["QS"].mean() + 0.2
    )

    # Proof criteria — require INDEPENDENT signals (EM≠QFT column) and Level-III for quantum claim
    em_qft_identical = bool(
        np.allclose(hindu["classical_em"].to_numpy(), hindu["quantum_field_theory"].to_numpy())
    )
    quantum_hits = int(np.sum(hindu["QS"] > 0) + np.sum(hindu["QEF"] > 0))

    wins = []
    for label, row in [("classical_em", em), ("quantum_mechanics", qm), ("quantum_field_theory", qft), ("QS", qs)]:
        if (
            row["delta_hindu_minus_control"] > 0.05
            and row["mannwhitney_hindu_gt_control_p"] < 0.05
        ):
            wins.append(label)
    # Collapse EM/QFT double-count
    if em_qft_identical and "classical_em" in wins and "quantum_field_theory" in wins:
        wins = [w for w in wins if w != "quantum_field_theory"]
        wins = ["level_ii_fieldlike_shared_em_qft_features" if w == "classical_em" else w for w in wins]

    if quantum_hits == 0 and "QS" not in wins and "quantum_mechanics" not in wins:
        # No Level-III / QM surplus → cannot claim quantum civilization support
        if wins and sanity_physics_detectable:
            verdict = "DEFEAT_QUANTUM_AND_MAXWELL__WEAK_LEVEL_II_SUBSTRATE_SURPLUS"
            interp = (
                f"No quantum-exclusive hits (QS/QEF all zero on Vedānta). "
                f"Scorer shows Level-II field-like surplus ({wins}) but classical_em≡QFT "
                f"columns (shared features) — not Maxwell labs or QFT. Accept defeat on "
                f"advanced EM/quantum-civilization claim for this panel."
            )
            novelty = False
        elif not sanity_physics_detectable:
            verdict = "ASSAY_FAILURE"
            interp = "Physics-reference assay too weak; do not interpret Hindu null as definitive."
            novelty = False
        else:
            verdict = "DEFEAT_AT_SPECIFIED_LEVEL"
            interp = (
                "No EM/quantum fingerprint surplus for Vedānta vs controls. Accept defeat "
                "at the specified level for this panel."
            )
            novelty = False
    elif wins and sanity_physics_detectable:
        verdict = "CANDIDATE_SUPPORT_AT_SPECIFIED_LEVEL"
        interp = (
            f"Hindu/Vedānta scores exceeded controls on: {', '.join(wins)}. "
            f"Escalate: larger corpus, blinded human audit, prereg. Not lab proof."
        )
        novelty = True
    else:
        verdict = "DEFEAT_AT_SPECIFIED_LEVEL"
        interp = "No robust surplus. Accept defeat at the specified level."
        novelty = False

    # Field-class distribution
    field_tab = (
        dev[dev["tradition"].isin(HINDU | CONTROLS)]
        .groupby(["tradition", "field_class"])
        .size()
        .unstack(fill_value=0)
    )

    summary = {
        "experiment_id": "EM-QM-proof-hunt-pd-v03",
        "status": "EXPLORATORY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hypothesis": (
            "If an advanced ancient Hindu civilization encoded EM/quantum structure, "
            "Vedānta PD passages should show higher classical_em / QM / QFT / QS scores "
            "than Greek/Buddhist/Chinese philosophical controls."
        ),
        "n_hindu": int(len(hindu)),
        "n_control": int(len(ctrl)),
        "n_physics_ref": int(len(pref)),
        "sanity_physics_detectable": sanity_physics_detectable,
        "winning_metrics": wins,
        "verdict_draft": verdict,
        "result_interpretation": interp,
        "novelty_candidate": novelty,
        "metrics": rows,
        "what_this_does_establish": (
            "Whether this PD panel + heuristic scorer shows Hindu surplus on EM/QM fingerprints."
        ),
        "what_this_does_not_establish": (
            "Existence/nonexistence of all ancient advanced civilizations; "
            "truth of Hindu metaphysics; lab detection of ākāśa."
        ),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    metrics.to_csv(OUT / "metrics_by_theory.csv", index=False)
    top_em.to_csv(OUT / "top_hindu_classical_em.csv", index=False)
    top_qm.to_csv(OUT / "top_hindu_quantum_mechanics.csv", index=False)
    top_qft.to_csv(OUT / "top_hindu_qft.csv", index=False)
    field_tab.to_csv(OUT / "field_class_by_tradition.csv")

    # Figure
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    ax = axes[0]
    plot_m = ["classical_em", "quantum_mechanics", "quantum_field_theory", "QS", "QEF"]
    x = np.arange(len(plot_m))
    h_means = [float(hindu[m].mean()) for m in plot_m]
    c_means = [float(ctrl[m].mean()) for m in plot_m]
    p_means = [float(pref[m].mean()) if len(pref) else 0 for m in plot_m]
    w = 0.25
    ax.bar(x - w, h_means, w, label="Vedānta (Hindu)", color="#b45309", edgecolor="k")
    ax.bar(x, c_means, w, label="Controls", color="#64748b", edgecolor="k")
    ax.bar(x + w, p_means, w, label="Modern physics ref", color="#2563eb", edgecolor="k")
    ax.set_xticks(x)
    ax.set_xticklabels(["EM", "QM", "QFT", "QS", "QEF"], fontsize=9)
    ax.set_ylabel("mean fingerprint score")
    ax.set_title("Proof-hunt: Hindu vs controls vs physics ref")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1]
    # per-tradition EM and QM
    trads = sorted(set(dev["tradition"]) | set(pref["tradition"]))
    em_m = [float(df[df["tradition"] == t]["classical_em"].mean()) for t in trads]
    qm_m = [float(df[df["tradition"] == t]["quantum_mechanics"].mean()) for t in trads]
    xpos = np.arange(len(trads))
    ax.bar(xpos - 0.2, em_m, 0.4, label="classical EM", color="#0f766e", edgecolor="k")
    ax.bar(xpos + 0.2, qm_m, 0.4, label="QM", color="#7c3aed", edgecolor="k")
    ax.set_xticks(xpos)
    ax.set_xticklabels([t.replace("_pd", "").replace("greek_", "gr_")[:12] for t in trads], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("mean score")
    ax.set_title(f"Verdict: {verdict}")
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle("RISHI-Q — EM/quantum advanced-civilization proof hunt (exploratory)", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "fig_proof_hunt.png", dpi=180, bbox_inches="tight")
    fig.savefig(FIG / "fig39_em_quantum_proof_hunt.png", dpi=180, bbox_inches="tight")
    plt.close()

    (OUT / "experiment_card.md").write_text(
        f"# EM/Quantum proof hunt\n\n**{verdict}**\n\n{interp}\n\n"
        f"Wins: {wins or 'none'}\nPhysics assay OK: {sanity_physics_detectable}\n",
        encoding="utf-8",
    )

    # Human-readable defeat/support note
    (OUT / "VERDICT.md").write_text(
        f"""# Proof-hunt verdict

**{verdict}**

{interp}

## Your question (restated)
Is there fingerprint evidence on this panel that Hindu/Vedānta texts encode
classical electromagnetism or quantum structure beyond other philosophical traditions?

## Answer at specified level
{"Candidate yes on: " + ", ".join(wins) if wins else "No surplus found. Accept defeat for this panel + scorer."}

## Next escalation (if still hunting)
1. Larger pre-modern Sanskrit corpus (critical editions, not only PD)
2. Human-blinded annotation audit
3. Separate EM-law claims (inverse-square, induction) as binary checklist
4. Physical EM experiments only after a unique quantitative prediction exists
""",
        encoding="utf-8",
    )
    print(json.dumps({k: summary[k] for k in summary if k != "metrics"}, indent=2))
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
