#!/usr/bin/env python3
"""Discovery-layer figures for paper assets (exploratory System B)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "results/discovery"
FIG = ROOT / "paper/figures"
ASSETS = ROOT / "paper/assets"


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    ranked = json.loads((DISC / "motif_rankings.json").read_text())
    enrich = json.loads((DISC / "motif_enrichments.json").read_text())
    atlas = json.loads((DISC / "motif_atlas.json").read_text())

    # Motif enrichment bar
    rows = []
    for r in ranked[:12]:
        e = enrich.get(r["motif_id"], {})
        rows.append(
            {
                "motif": r["motif_id"],
                "enrichment": e.get("enrichment") or 0,
                "family": r.get("physics_family"),
            }
        )
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = [
        "#1d4ed8"
        if f == "field_like"
        else "#b45309"
        if f == "classical"
        else "#7c3aed"
        if f == "quantum_specific"
        else "#64748b"
        for f in df["family"]
    ]
    ax.bar(df["motif"], df["enrichment"], color=colors, edgecolor="#111")
    ax.axhline(1.0, color="#333", ls="--", lw=1, label="enrichment=1")
    ax.set_ylabel("Enrichment (target/control)")
    ax.set_title("System B: motif enrichment (EXPLORATORY — physics mapped post-hoc)")
    ax.legend(loc="upper right", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(FIG / "fig20_discovery_motif_enrichment.png", dpi=160)
    plt.close()

    # Atlas counts
    labels = [
        "field_like",
        "atomistic",
        "relational",
        "observer",
        "quantum_specific",
        "shared",
    ]
    vals = [
        len(atlas.get("field_like_motifs", [])),
        len(atlas.get("atomistic_motifs", [])),
        len(atlas.get("relational_motifs", [])),
        len(atlas.get("observer_related_motifs", [])),
        len(atlas.get("quantum_specific_motifs", [])),
        len(atlas.get("shared_across_traditions", [])),
    ]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(labels, vals, color="#0f766e", edgecolor="#111")
    ax.set_xlabel("Count")
    ax.set_title("Cross-civilization motif atlas categories (EXPLORATORY)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(FIG / "fig21_discovery_motif_atlas.png", dpi=160)
    plt.close()

    # Surprisal histogram
    if (DISC / "surprisal.json").exists():
        sur = json.loads((DISC / "surprisal.json").read_text())
        xs = [s["surprisal"] for s in sur]
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(xs, bins=20, color="#334155", edgecolor="#111")
        ax.set_xlabel("Surprisal")
        ax.set_ylabel("Passages")
        ax.set_title("Structural surprisal distribution (EXPLORATORY)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        fig.savefig(FIG / "fig22_discovery_surprisal.png", dpi=160)
        plt.close()

    summary = {
        "figures": [
            "fig20_discovery_motif_enrichment.png",
            "fig21_discovery_motif_atlas.png",
            "fig22_discovery_surprisal.png",
        ],
        "warning": "EXPLORATORY_SYSTEM_B",
        "n_motifs_ranked": len(ranked),
        "n_quantum_specific": len(atlas.get("quantum_specific_motifs", [])),
    }
    (ASSETS / "discovery_figures.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
