#!/usr/bin/env python3
"""Regenerate the full RISHI-Q visualization suite (System A + B)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

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
from rishiq.visualization.discovery import (
    plot_claims_vs_data,
    plot_cluster_bootstrap,
    plot_concept_graph_example,
    plot_discovery_flow,
    plot_dual_system,
    plot_motif_atlas,
    plot_motif_enrichment,
    plot_pd_pilot_panel,
    plot_success_tiers,
    plot_surprisal,
    plot_temporal_firsts,
    plot_translation_modernization,
    plot_translation_shift_graph,
)
from rishiq.robustness import run_robustness_battery
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "paper/figures"
ASSETS = ROOT / "paper/assets"
DISC = ROOT / "results/discovery"
ONT = ROOT / "ontology/ontology_v0.1.yaml"
SCORES = ROOT / "results/exploratory/synthetic_e2e/passage_scores.parquet"
ANN = ROOT / "results/exploratory/synthetic_e2e/annotations.parquet"
POWER = ROOT / "results/exploratory/power_recommendations.json"
PD_SCORES = ROOT / "results/exploratory/pd_pilot/passage_scores.parquet"
PROTO = ROOT / "results/exploratory/prototype100/passage_scores.parquet"

THEORIES = [
    "newtonian",
    "classical_em",
    "thermodynamics",
    "relativity",
    "quantum_mechanics",
    "quantum_field_theory",
]


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    catalog = []

    def rec(path: Path, desc: str) -> None:
        catalog.append(
            {
                "path": str(path.relative_to(ROOT)),
                "description": desc,
                "generated_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        print("wrote", path.name)

    # Schematics
    rec(plot_pipeline_diagram(FIG / "fig01_pipeline.png"), "Pipeline")
    rec(plot_three_level_cartoon(FIG / "fig02_three_levels.png"), "Three levels")
    rec(plot_ontology_overview(ONT, FIG / "fig03_ontology_overview.png"), "Ontology")
    rec(plot_dev_confirmatory_firewall(FIG / "fig04_firewall.png"), "Firewall")
    rec(plot_dual_system(FIG / "fig23_dual_system.png"), "Dual system A/B")
    rec(plot_discovery_flow(FIG / "fig24_discovery_flow.png"), "Discovery flow")
    rec(plot_concept_graph_example(FIG / "fig25_concept_graph.png"), "Concept graph")
    rec(plot_success_tiers(FIG / "fig26_success_tiers.png"), "Success tiers")

    # Synthetic / instrument
    if SCORES.exists():
        df = pd.read_parquet(SCORES)
        ann = pd.read_parquet(ANN)
        rec(plot_positive_control_validation(df, FIG / "fig05_positive_controls.png"), "Positive controls")
        rec(plot_qs_by_tradition(df, FIG / "fig06_qs_by_tradition.png"), "QS by tradition")
        rec(plot_theory_heatmap(df, THEORIES, FIG / "fig07_theory_heatmap.png"), "Theory heatmap")
        rec(plot_qs_qef_scatter(df, FIG / "fig08_qs_qef_scatter.png"), "QS/QEF scatter")
        rec(
            plot_feature_heatmap_from_annotations(ann, df, FIG / "fig09_feature_heatmap.png"),
            "Feature heatmap",
        )
        t = df[df["role"] == "target"]["QS"]
        c = df[df["role"] == "control"]["QS"]
        primary = float(t.mean() - c.mean()) if len(t) and len(c) else 0.0
        rows = run_robustness_battery(primary_delta=primary, variants={"N_no_embeddings": primary})
        rec(plot_robustness_forest(rows, FIG / "fig10_robustness_forest.png"), "Robustness")

    if POWER.exists():
        rec(plot_power_curves(POWER, FIG / "fig11_power_curves.png"), "Power")

    # Prototype100 extras if present
    if PROTO.exists():
        pdf = pd.read_parquet(PROTO)
        # reuse builders from run_protocol if figures missing — keep simple QS by role
        import matplotlib.pyplot as plt
        from rishiq.visualization import PALETTE, _style

        g = pdf.groupby("role")["QS"].agg(["mean", "std", "count"]).reset_index()
        fig, ax = plt.subplots(figsize=(7.5, 4.2))
        ax.bar(g["role"], g["mean"], yerr=g["std"].fillna(0), capsize=3, color=PALETTE["accent"], edgecolor=PALETTE["ink"])
        ax.axhline(0, color=PALETTE["muted"], lw=1)
        ax.set_ylabel("QS")
        ax.set_title("Prototype100 QS by role (EXPLORATORY)")
        _style(ax)
        fig.tight_layout()
        p = FIG / "fig14_prototype100_qs_by_role.png"
        fig.savefig(p, dpi=200, bbox_inches="tight")
        plt.close(fig)
        rec(p, "Prototype QS by role")

        mat = pdf.groupby("tradition")[THEORIES].mean()
        fig, ax = plt.subplots(figsize=(9.2, 5.0))
        im = ax.imshow(mat.values, aspect="auto", cmap="cividis", vmin=0, vmax=1)
        ax.set_xticks(range(len(THEORIES)))
        ax.set_xticklabels(THEORIES, rotation=35, ha="right")
        ax.set_yticks(range(len(mat.index)))
        ax.set_yticklabels(list(mat.index))
        ax.set_title("Cross-civilization theory matrix (prototype100, EXPLORATORY)")
        fig.colorbar(im, ax=ax, fraction=0.046)
        _style(ax)
        fig.tight_layout()
        p = FIG / "fig13_cross_civilization.png"
        fig.savefig(p, dpi=200, bbox_inches="tight")
        plt.close(fig)
        rec(p, "Cross-civ tournament")

        # balance
        bal = pdf.groupby(["role", "tradition"]).size().reset_index(name="n")
        fig, ax = plt.subplots(figsize=(9, 4.5))
        piv = bal.pivot(index="tradition", columns="role", values="n").fillna(0)
        piv.plot(kind="bar", stacked=True, ax=ax, edgecolor=PALETTE["ink"])
        ax.set_ylabel("Passages")
        ax.set_title("Prototype composition (EXPLORATORY)")
        ax.legend(frameon=False, fontsize=8)
        _style(ax)
        plt.xticks(rotation=25, ha="right")
        fig.tight_layout()
        p = FIG / "fig17_prototype_balance.png"
        fig.savefig(p, dpi=200, bbox_inches="tight")
        plt.close(fig)
        rec(p, "Prototype balance")

        # primary effect bar
        t = pdf[pdf["role"] == "target"]["QS"]
        c = pdf[pdf["role"] == "control"]["QS"]
        delta = float(t.mean() - c.mean()) if len(t) and len(c) else 0.0
        fig, ax = plt.subplots(figsize=(5.5, 4))
        ax.bar(["ΔQ"], [delta], color=PALETTE["accent"], edgecolor=PALETTE["ink"])
        ax.axhline(0, color=PALETTE["muted"], lw=1)
        ax.set_title("Exploratory ΔQ (prototype100)")
        ax.set_ylabel("ΔQ")
        _style(ax)
        fig.tight_layout()
        p = FIG / "fig16_primary_effect_exploratory.png"
        fig.savefig(p, dpi=200, bbox_inches="tight")
        plt.close(fig)
        rec(p, "Primary effect exploratory")

        if "field_class" in pdf.columns:
            fc = pdf.groupby(["role", "field_class"]).size().unstack(fill_value=0)
            fc = fc.div(fc.sum(axis=1), axis=0)
            fig, ax = plt.subplots(figsize=(8.5, 4.5))
            fc.plot(kind="bar", stacked=True, ax=ax, edgecolor=PALETTE["ink"])
            ax.set_ylabel("Fraction")
            ax.set_title("Field-ontology classes by role (EXPLORATORY)")
            ax.legend(frameon=False, fontsize=7, ncol=2)
            _style(ax)
            plt.xticks(rotation=20, ha="right")
            fig.tight_layout()
            p = FIG / "fig15_field_ontology.png"
            fig.savefig(p, dpi=200, bbox_inches="tight")
            plt.close(fig)
            rec(p, "Field ontology")

    # PD pilot
    if PD_SCORES.exists():
        paths = plot_pd_pilot_panel(
            PD_SCORES,
            FIG / "fig18_pd_pilot_qs.png",
            FIG / "fig19_pd_pilot_tournament.png",
        )
        for p in paths:
            rec(p, "PD pilot panel")

    # Translation demo figure if scores exist
    tdemo = ROOT / "results/exploratory/translation_demo/passage_scores.parquet"
    if tdemo.exists():
        import matplotlib.pyplot as plt
        from rishiq.visualization import PALETTE, _style

        tdf = pd.read_parquet(tdemo)
        tdf["style"] = tdf["passage_id"].str.split("__").str[-1]
        fig, ax = plt.subplots(figsize=(6.5, 4))
        ax.bar(tdf["style"], tdf["QS"], color=PALETTE["accent2"], edgecolor=PALETTE["ink"])
        ax.axhline(0, color=PALETTE["muted"], lw=1)
        ax.set_ylabel("QS")
        ax.set_title("Translation contamination demo (TCI≈0)")
        _style(ax)
        fig.tight_layout()
        p = FIG / "fig12_translation_tci_demo.png"
        fig.savefig(p, dpi=200, bbox_inches="tight")
        plt.close(fig)
        rec(p, "TCI demo")

    # Discovery outputs
    if (DISC / "motif_rankings.json").exists():
        ranked = json.loads((DISC / "motif_rankings.json").read_text())
        enrich = json.loads((DISC / "motif_enrichments.json").read_text())
        atlas = json.loads((DISC / "motif_atlas.json").read_text())
        sur = json.loads((DISC / "surprisal.json").read_text())
        temporal = json.loads((DISC / "temporal.json").read_text())
        translation = json.loads((DISC / "translation_modernization.json").read_text())
        cluster = json.loads((DISC / "motif_cluster_bootstrap.json").read_text())
        claims = json.loads((DISC / "claims_vs_data.json").read_text())

        rec(plot_motif_enrichment(ranked, enrich, FIG / "fig20_discovery_motif_enrichment.png"), "Motif enrichment")
        rec(plot_motif_atlas(atlas, FIG / "fig21_discovery_motif_atlas.png"), "Motif atlas")
        rec(plot_surprisal(sur, FIG / "fig22_discovery_surprisal.png"), "Surprisal")
        rec(plot_claims_vs_data(claims if isinstance(claims, list) else [], FIG / "fig27_claims_vs_data.png"), "Claims vs data")
        rec(plot_temporal_firsts(temporal, FIG / "fig28_temporal_combinations.png"), "Temporal")
        rec(plot_translation_modernization(translation, FIG / "fig29_translation_modernization.png"), "Translation modernization")
        rec(plot_cluster_bootstrap(cluster, FIG / "fig30_cluster_bootstrap.png"), "Cluster bootstrap")
        shifts = translation.get("aligned_shift_graphs") or []
        if shifts:
            rec(plot_translation_shift_graph(shifts[0], FIG / "fig31_translation_shift_graph.png"), "Shift graph")

    # Headline figures if present
    for name, desc in [
        ("fig32_contamination_by_tradition.png", "Contamination"),
        ("fig33_vedanta_vs_lucretius_features.png", "Vedanta vs Lucretius"),
        ("fig34_qs_after_v03.png", "QS v0.3"),
    ]:
        p = FIG / name
        if p.exists():
            rec(p, desc)

    (ASSETS / "visualization_catalog.json").write_text(
        json.dumps({"n": len(catalog), "figures": catalog}, indent=2), encoding="utf-8"
    )
    # captions update stub
    print(json.dumps({"ok": True, "n_figures": len(catalog)}, indent=2))


if __name__ == "__main__":
    main()
