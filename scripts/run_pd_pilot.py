#!/usr/bin/env python3
"""Run honest exploratory analysis on the PD development corpus.

Does NOT unlock confirmatory.
Does NOT cherry-pick.
Writes primary_effect + figures + paper-facing summary with honesty banner.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from rishiq.experiments import passages_from_parquet, run_pipeline_on_passages
from rishiq.statistics import cluster_permutation_pvalue, mean_difference

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus/development/pd_passages.parquet"
OUT = ROOT / "results/exploratory/pd_pilot"
FIG = ROOT / "paper/figures"


def main() -> None:
    if not CORPUS.exists():
        raise SystemExit("Run scripts/build_pd_development_corpus.py first")

    passages = passages_from_parquet(CORPUS)
    result = run_pipeline_on_passages(
        passages,
        ontology_path=ROOT / "ontology/ontology_v0.1.yaml",
        fingerprint_dir=ROOT / "ontology/physics_fingerprints",
        out_dir=OUT,
        experiment_id="pd-development-pilot-v0.1",
        repo_root=ROOT,
    )
    scores = pd.read_parquet(OUT / "passage_scores.parquet")

    # Exclude physics_reference from H0-style contrast (instrument only)
    hist = scores[scores["role"].isin(["target", "control", "negative_control"])]
    target = hist[hist["role"] == "target"]
    control = hist[hist["role"] == "control"]
    delta = mean_difference(target["QS"], control["QS"])
    perm = cluster_permutation_pvalue(
        target["QS"].tolist(),
        target["work"].tolist(),
        control["QS"].tolist(),
        control["work"].tolist(),
        n_perm=999,
        seed=42,
    )

    theories = [
        "newtonian",
        "classical_em",
        "thermodynamics",
        "relativity",
        "quantum_mechanics",
        "quantum_field_theory",
    ]
    matrix = hist.groupby("tradition")[theories + ["QS", "QEF"]].mean().round(4)
    matrix.to_csv(OUT / "tradition_theory_matrix.csv")
    matrix.to_csv(ROOT / "paper/tables/tab_pd_pilot_matrix.csv")

    primary = {
        "warning": "EXPLORATORY_PD_PILOT_NOT_CONFIRMATORY_H1",
        "n_target": int(len(target)),
        "n_control": int(len(control)),
        "delta_Q": float(delta),
        "mean_QS_target": float(target["QS"].mean()),
        "mean_QS_control": float(control["QS"].mean()),
        "mean_QEF_target": float(target["QEF"].mean()),
        "mean_QEF_control": float(control["QEF"].mean()),
        "permutation": perm,
        "mean_QS_by_tradition": hist.groupby("tradition")["QS"].mean().round(4).to_dict(),
        "interpretation_rules": [
            "Do not claim ancient discovery of QM.",
            "Older translations may modernize language — treat as exploratory.",
            "Heuristic annotator is not human validation.",
            "Confirmatory remains locked until preregistration.",
        ],
    }
    (OUT / "primary_effect.json").write_text(json.dumps(primary, indent=2), encoding="utf-8")
    (ROOT / "paper/assets/pd_pilot_primary_effect.json").write_text(
        json.dumps(primary, indent=2), encoding="utf-8"
    )

    # Figures
    FIG.mkdir(parents=True, exist_ok=True)
    g = hist.groupby("tradition")["QS"].agg(["mean", "std", "count"]).reset_index()
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.bar(g["tradition"], g["mean"], yerr=g["std"].fillna(0), capsize=3, color="#1d4ed8", edgecolor="#111")
    ax.axhline(0, color="#555", lw=1)
    ax.set_ylabel("QS")
    ax.set_title("PD development pilot: QS by tradition (EXPLORATORY — not confirmatory)")
    plt.xticks(rotation=25, ha="right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig18_pd_pilot_qs.png", dpi=200, bbox_inches="tight")
    plt.close()

    fig, ax = plt.subplots(figsize=(9.5, 5))
    im = ax.imshow(matrix[theories].values, aspect="auto", cmap="cividis", vmin=0, vmax=max(0.2, float(matrix[theories].values.max())))
    ax.set_xticks(range(len(theories)))
    ax.set_xticklabels(theories, rotation=30, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(list(matrix.index))
    ax.set_title("PD pilot theory tournament (exploratory)")
    fig.colorbar(im, ax=ax, fraction=0.03)
    fig.tight_layout()
    fig.savefig(FIG / "fig19_pd_pilot_tournament.png", dpi=200, bbox_inches="tight")
    plt.close()

    # Markdown finding note for paper
    md = f"""# PD development pilot findings (exploratory)

**Status:** NOT confirmatory. NOT preregistered. Heuristic annotator only. Older PD translations.

## Headline numbers

- n_target = {primary['n_target']}
- n_control = {primary['n_control']}
- ΔQ = {primary['delta_Q']:.4f}
- permutation p ≈ {primary['permutation']['p_value']:.3f}
- mean QS target = {primary['mean_QS_target']:.4f}
- mean QS control = {primary['mean_QS_control']:.4f}
- mean QEF target = {primary['mean_QEF_target']:.4f}
- mean QEF control = {primary['mean_QEF_control']:.4f}

## Tradition QS means

```
{json.dumps(primary['mean_QS_by_tradition'], indent=2)}
```

## What this can mean for the paper

If ΔQ is near zero / negative: the honest headline is that **under this blinded structural instrument, PD Upanishadic English does not show unusual quantum-specificity vs Greco-Roman/Buddhist/Chinese controls**. That is a publishable *negative/methods* result — not a revelation of ancient quantum mechanics.

If some Level II (field-like) elevation appears without Level III: report as classical-field-like analogy candidates, not QM.

## What this cannot mean

- Not proof scriptures contain QM
- Not confirmatory H1 settlement
- Not human-validated philology
"""
    (OUT / "FINDINGS.md").write_text(md, encoding="utf-8")
    (ROOT / "paper/assets/PD_PILOT_FINDINGS.md").write_text(md, encoding="utf-8")
    print(json.dumps(primary, indent=2))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
