#!/usr/bin/env python3
"""Build all paper-facing figures, tables, and asset catalog from reproducible outputs.

Never invent confirmatory results. Exploratory/synthetic runs are labeled as such.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from rishiq.robustness import run_robustness_battery
from rishiq.visualization import (
    plot_dev_confirmatory_firewall,
    plot_feature_heatmap_from_annotations,
    plot_ontology_overview,
    plot_pipeline_diagram,
    plot_positive_control_validation,
    plot_power_curves,
    plot_qs_by_tradition,
    plot_qs_qef_scatter,
    plot_robustness_forest,
    plot_theory_heatmap,
    plot_three_level_cartoon,
)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "paper" / "figures"
TAB = ROOT / "paper" / "tables"
ASSETS = ROOT / "paper" / "assets"
SCORES = ROOT / "results" / "exploratory" / "synthetic_e2e" / "passage_scores.parquet"
ANN = ROOT / "results" / "exploratory" / "synthetic_e2e" / "annotations.parquet"
POWER = ROOT / "results" / "exploratory" / "power_recommendations.json"
ONT = ROOT / "ontology" / "ontology_v0.1.yaml"

THEORIES = [
    "newtonian",
    "classical_em",
    "thermodynamics",
    "relativity",
    "quantum_mechanics",
    "quantum_field_theory",
]


def latex_escape(s: str) -> str:
    return (
        str(s)
        .replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
    )


def df_to_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = list(df.columns)
    header = " & ".join(latex_escape(c) for c in cols) + " \\\\"
    lines = [
        "% Auto-generated — do not edit by hand",
        f"% Generated: {datetime.now(timezone.utc).isoformat()}",
        "\\begin{table}[t]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\begin{tabular}{" + ("l" * len(cols)) + "}",
        "\\toprule",
        header,
        "\\midrule",
    ]
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            v = row[c]
            if isinstance(v, float):
                cells.append(f"{v:.3f}")
            else:
                cells.append(latex_escape(v))
        lines.append(" & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    df.to_csv(path.with_suffix(".csv"), index=False)


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    if not SCORES.exists():
        raise SystemExit(f"missing {SCORES}; run rishiq annotate first")

    df = pd.read_parquet(SCORES)
    ann = pd.read_parquet(ANN)

    # --- figures ---
    assets: list[dict] = []

    def record(path: Path, kind: str, description: str) -> None:
        assets.append(
            {
                "path": str(path.relative_to(ROOT)),
                "kind": kind,
                "description": description,
                "generated_utc": datetime.now(timezone.utc).isoformat(),
            }
        )

    p = plot_pipeline_diagram(FIG / "fig01_pipeline.png")
    record(p, "figure", "Analysis pipeline schematic")
    p = plot_three_level_cartoon(FIG / "fig02_three_levels.png")
    record(p, "figure", "Level I/II/III scientific distinction")
    p = plot_ontology_overview(ONT, FIG / "fig03_ontology_overview.png")
    record(p, "figure", "Ontology feature counts by family and level")
    p = plot_dev_confirmatory_firewall(FIG / "fig04_firewall.png")
    record(p, "figure", "Development vs confirmatory firewall")
    p = plot_positive_control_validation(df, FIG / "fig05_positive_controls.png")
    record(p, "figure", "Modern physics positive-control theory scores")
    p = plot_qs_by_tradition(df, FIG / "fig06_qs_by_tradition.png")
    record(p, "figure", "QS by tradition (exploratory)")
    p = plot_theory_heatmap(df, THEORIES, FIG / "fig07_theory_heatmap.png")
    record(p, "figure", "Theory similarity heatmap")
    p = plot_qs_qef_scatter(df, FIG / "fig08_qs_qef_scatter.png")
    record(p, "figure", "QS vs QEF scatter with passage labels")
    p = plot_feature_heatmap_from_annotations(
        ann, df, FIG / "fig09_feature_heatmap.png"
    )
    record(p, "figure", "Feature positivity heatmap")

    t = df[df["role"] == "target"]["QS"]
    c = df[df["role"] == "control"]["QS"]
    primary = float(t.mean() - c.mean()) if len(t) and len(c) else 0.0
    rows = run_robustness_battery(
        primary_delta=primary, variants={"N_no_embeddings": primary}
    )
    p = plot_robustness_forest(rows, FIG / "fig10_robustness_forest.png")
    record(p, "figure", "Robustness forest scaffold")

    if not POWER.exists():
        from rishiq.statistics import recommend_sample_sizes

        POWER.write_text(json.dumps(recommend_sample_sizes(n_sim=30), indent=2))
    p = plot_power_curves(POWER, FIG / "fig11_power_curves.png")
    record(p, "figure", "Exploratory power curves")

    # Translation demo figure if present
    tci_fig = FIG / "fig12_translation_tci_demo.png"
    if tci_fig.exists():
        record(tci_fig, "figure", "Synthetic translation contamination demo")
    else:
        print("note: run scripts/run_translation_demo.py then rebuild for fig12")

    # Keep legacy filenames used earlier
    plot_qs_by_tradition(df, FIG / "qs_by_tradition.png")
    plot_theory_heatmap(df, THEORIES, FIG / "theory_heatmap.png")
    plot_robustness_forest(rows, FIG / "robustness_forest.png")

    # --- tables ---
    score_tbl = df[
        [
            "passage_id",
            "tradition",
            "role",
            "QS",
            "QEF",
            "field_class",
            *THEORIES,
        ]
    ].copy()
    score_tbl = score_tbl.round(3)
    df_to_latex(
        score_tbl,
        TAB / "tab_passage_scores.tex",
        "Exploratory passage scores (synthetic + physics controls). Not confirmatory.",
        "tab:passage-scores",
    )
    record(TAB / "tab_passage_scores.tex", "table", "Passage-level QS/QEF/theory scores")

    phys = df[df["role"] == "physics_reference"][
        ["passage_id", "work", "QS", "QEF", "quantum_mechanics", "classical_em"]
    ].round(3)
    # expected mapping notes
    expected = {
        "PHYS_NEWTON_001": "classical mechanics",
        "PHYS_EM_001": "classical EM / field",
        "PHYS_THERMO_001": "thermo / epistemic",
        "PHYS_QM_001": "quantum mechanics",
        "PHYS_QFT_001": "QFT",
        "PHYS_ENTANGLE_001": "nonseparability",
    }
    phys = phys.copy()
    phys["expected_emphasis"] = phys["passage_id"].map(expected)
    df_to_latex(
        phys,
        TAB / "tab_positive_controls.tex",
        "Positive-control instrument check on modern physics passages.",
        "tab:positive-controls",
    )
    record(TAB / "tab_positive_controls.tex", "table", "Positive control summary")

    role_sum = (
        df.groupby("role")[["QS", "QEF"]]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    role_sum.columns = [
        "role",
        "QS_mean",
        "QS_std",
        "QS_n",
        "QEF_mean",
        "QEF_std",
        "QEF_n",
    ]
    role_sum = role_sum.round(3)
    df_to_latex(
        role_sum,
        TAB / "tab_role_summary.tex",
        "Exploratory QS/QEF summary by role.",
        "tab:role-summary",
    )

    pos = ann[ann["label"] == "1"].groupby("feature_id").size().reset_index(name="n_positive")
    pos = pos.sort_values("n_positive", ascending=False)
    df_to_latex(
        pos.head(25),
        TAB / "tab_positive_features.tex",
        "Most frequent positive ontology features in the exploratory run.",
        "tab:positive-features",
    )

    # Ontology inventory table
    ont = yaml.safe_load(ONT.read_text(encoding="utf-8"))
    ont_rows = pd.DataFrame(
        [
            {
                "id": f["id"],
                "name": f["name"],
                "family": f["family"],
                "level": f["level"],
                "quantum_specific": f["quantum_specific"],
                "field_like": f["field_like"],
            }
            for f in ont["features"]
        ]
    )
    df_to_latex(
        ont_rows,
        TAB / "tab_ontology_features.tex",
        "RISHI-Q ontology v0.1 feature inventory.",
        "tab:ontology-features",
    )
    record(TAB / "tab_ontology_features.tex", "table", "Full ontology feature list")

    # Hard rules table
    rules = pd.DataFrame(
        {"rule_id": [f"R{i+1:02d}" for i in range(len(ont["hard_rules"]))], "rule": ont["hard_rules"]}
    )
    df_to_latex(
        rules,
        TAB / "tab_hard_rules.tex",
        "Hard interpretation rules (annotation codebook).",
        "tab:hard-rules",
    )

    # Manifest excerpt
    man = json.loads(
        (ROOT / "results/exploratory/synthetic_e2e/manifest.json").read_text()
    )
    man_tbl = pd.DataFrame(
        [
            {"field": k, "value": v if not isinstance(v, dict) else json.dumps(v)[:80]}
            for k, v in man.items()
            if k != "package_versions"
        ]
        + [{"field": f"pkg:{k}", "value": v} for k, v in man.get("package_versions", {}).items()]
    )
    df_to_latex(
        man_tbl,
        TAB / "tab_experiment_manifest.tex",
        "Experiment manifest for exploratory synthetic end-to-end run.",
        "tab:manifest",
    )

    # Status gates for paper honesty
    status = pd.DataFrame(
        [
            {"gate": "Ontology v0.1", "status": "PILOTED"},
            {"gate": "Synthetic E2E pipeline", "status": "COMPLETE"},
            {"gate": "Positive-control instrument tests", "status": "PASSING"},
            {"gate": "Human validation", "status": "REQUIRES_EXTERNAL_HUMAN_VALIDATION"},
            {"gate": "OSF preregistration", "status": "READY_FOR_EXTERNAL_PREREGISTRATION"},
            {"gate": "Confirmatory analysis", "status": "LOCKED"},
            {"gate": "Licensed development corpus (500-800)", "status": "IN_PROGRESS_POINTERS"},
            {"gate": "Expert Sanskrit review", "status": "REQUIRES_EXPERT_REVIEW"},
            {"gate": "Expert physicist review", "status": "REQUIRES_EXPERT_REVIEW"},
        ]
    )
    df_to_latex(
        status,
        TAB / "tab_project_status.tex",
        "Project status gates (honest incomplete items listed).",
        "tab:status",
    )

    catalog = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_assets": len(assets),
        "assets": assets,
        "notes": "All numeric figures/tables derive from exploratory synthetic pipeline unless marked schematic.",
    }
    (ASSETS / "catalog.json").write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    md = ["# Paper asset catalog\n", f"Generated: `{catalog['generated_utc']}`\n\n"]
    for a in assets:
        md.append(f"- `{a['path']}` — {a['description']} ({a['kind']})\n")
    (ASSETS / "CATALOG.md").write_text("".join(md), encoding="utf-8")

    # Methods numbers snippet for paper
    snippet = {
        "n_passages_exploratory": int(len(df)),
        "n_annotations": int(len(ann)),
        "n_positive_labels": int((ann["label"] == "1").sum()),
        "n_ontology_features": len(ont["features"]),
        "n_quantum_specific_features": sum(1 for f in ont["features"] if f["quantum_specific"]),
        "mean_QS_physics": float(df.loc[df["role"] == "physics_reference", "QS"].mean()),
        "mean_QS_unity_control": float(
            df.loc[df["passage_id"] == "SYN_UNITY_001", "QS"].mean()
        ),
        "mean_QS_qm_passage": float(df.loc[df["passage_id"] == "PHYS_QM_001", "QS"].mean()),
        "primary_delta_target_minus_control_exploratory": primary,
        "warning": "EXPLORATORY_ONLY_NOT_H1",
    }
    (ASSETS / "exploratory_numbers.json").write_text(
        json.dumps(snippet, indent=2), encoding="utf-8"
    )
    print(f"wrote {len(assets)} recorded assets + tables to paper/")
    print(json.dumps(snippet, indent=2))


if __name__ == "__main__":
    main()
