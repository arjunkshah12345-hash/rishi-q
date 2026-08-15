"""Additional publication figures for System B discovery + dual architecture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from rishiq.visualization import PALETTE, _style


def plot_dual_system(out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    ax.axis("off")
    # System A
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (0.3, 0.5), 4.6, 3.2,
            boxstyle="round,pad=0.04,rounding_size=0.1",
            facecolor="#eff6ff", edgecolor=PALETTE["accent"], lw=2,
        )
    )
    ax.text(2.6, 3.4, "SYSTEM A — Confirmatory", ha="center", fontsize=11, fontweight="bold", color=PALETTE["accent"])
    ax.text(
        2.6, 2.2,
        "Preregistered H0/H1\nQuantum-specificity ΔQ\nBlinding · TCI · masking\nCluster-aware inference\n\nSTATUS: LOCKED until OSF",
        ha="center", va="center", fontsize=9,
    )
    # System B
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (5.4, 0.5), 4.6, 3.2,
            boxstyle="round,pad=0.04,rounding_size=0.1",
            facecolor="#f0fdfa", edgecolor=PALETTE["accent2"], lw=2,
        )
    )
    ax.text(7.7, 3.4, "SYSTEM B — Discovery", ha="center", fontsize=11, fontweight="bold", color=PALETTE["accent2"])
    ax.text(
        7.7, 2.2,
        "Concept graphs → Rishi Motifs\n(no physics labels first)\nSurprisal · temporal · translation\nClaims-vs-data · novelty gate\n\nSTATUS: EXPLORATORY",
        ha="center", va="center", fontsize=9,
    )
    ax.annotate(
        "",
        xy=(5.3, 2.1),
        xytext=(5.0, 2.1),
        arrowprops=dict(arrowstyle="<->", color=PALETTE["ink"], lw=1.5),
    )
    ax.text(5.15, 2.55, "complementary", ha="center", fontsize=7, color=PALETTE["muted"], rotation=90)
    ax.set_xlim(0, 10.3)
    ax.set_ylim(0.2, 4.0)
    ax.set_title("RISHI-Q dual research architecture", fontsize=13, pad=6)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_discovery_flow(out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stages = [
        "Ancient\npassages",
        "Structural\ngraphs",
        "Motif\nmining",
        "Enrichment\n+ surprisal",
        "THEN map to\nphysics",
        "Novelty\ngate",
    ]
    fig, ax = plt.subplots(figsize=(11.2, 2.6))
    ax.set_xlim(0, len(stages) + 0.3)
    ax.set_ylim(0, 2)
    ax.axis("off")
    for i, label in enumerate(stages):
        x = i + 0.55
        color = PALETTE["warn"] if i == 4 else PALETTE["accent2"]
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (x - 0.42, 0.55), 0.84, 1.0,
                boxstyle="round,pad=0.02,rounding_size=0.05",
                linewidth=1.3, edgecolor=color, facecolor="#fff",
            )
        )
        ax.text(x, 1.05, label, ha="center", va="center", fontsize=8)
        if i < len(stages) - 1:
            ax.annotate(
                "",
                xy=(x + 0.52, 1.05),
                xytext=(x + 0.42, 1.05),
                arrowprops=dict(arrowstyle="->", color=PALETTE["ink"], lw=1.2),
            )
    ax.text(
        len(stages) / 2,
        0.25,
        "Physics labels enter only after unsupervised motif discovery",
        ha="center",
        fontsize=8,
        color=PALETTE["muted"],
    )
    ax.set_title("System B discovery flow (label-free → post-hoc physics)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_motif_enrichment(
    rankings: list[dict],
    enrichments: dict[str, dict],
    out_path: str | Path,
    top_n: int = 12,
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in rankings[:top_n]:
        e = enrichments.get(r["motif_id"], {})
        rows.append(
            {
                "motif": r["motif_id"],
                "enrichment": e.get("enrichment") if e.get("enrichment") is not None else 0,
                "family": r.get("physics_family", "unknown"),
            }
        )
    df = pd.DataFrame(rows)
    color_map = {
        "field_like": PALETTE["accent"],
        "classical": PALETTE["warn"],
        "quantum_specific": "#7c3aed",
        "unrelated": PALETTE["muted"],
        "unknown": "#94a3b8",
    }
    colors = [color_map.get(f, PALETTE["muted"]) for f in df["family"]]
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    ax.bar(df["motif"], df["enrichment"], color=colors, edgecolor=PALETTE["ink"], lw=0.5)
    ax.axhline(1.0, color=PALETTE["ink"], ls="--", lw=1, label="enrichment = 1")
    ax.set_ylabel("Enrichment P(M|target) / P(M|control)")
    ax.set_title("Discovered motifs: enrichment vs controls (EXPLORATORY)")
    handles = [
        mpatches.Patch(color=c, label=lab)
        for lab, c in color_map.items()
        if lab in set(df["family"])
    ]
    ax.legend(handles=handles + [plt.Line2D([0], [0], color=PALETTE["ink"], ls="--", label="=1")], frameon=False, fontsize=8)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_motif_atlas(atlas: dict[str, Any], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    labels = [
        "field-like",
        "atomistic",
        "relational",
        "observer",
        "quantum-specific",
        "shared (≥2 trad.)",
    ]
    vals = [
        len(atlas.get("field_like_motifs", [])),
        len(atlas.get("atomistic_motifs", [])),
        len(atlas.get("relational_motifs", [])),
        len(atlas.get("observer_related_motifs", [])),
        len(atlas.get("quantum_specific_motifs", [])),
        len(atlas.get("shared_across_traditions", [])),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    ax.barh(labels[::-1], vals[::-1], color=PALETTE["accent2"], edgecolor=PALETTE["ink"], lw=0.5)
    ax.set_xlabel("Motif count")
    ax.set_title("Cross-civilization motif atlas (EXPLORATORY)")
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_surprisal(surprisal_rows: list[dict], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    xs = [r["surprisal"] for r in surprisal_rows]
    flags = [bool(r.get("artifact_flags")) for r in surprisal_rows]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.hist(
        [x for x, f in zip(xs, flags) if not f],
        bins=18,
        color=PALETTE["accent"],
        edgecolor=PALETTE["ink"],
        alpha=0.85,
        label="clean",
    )
    ax.hist(
        [x for x, f in zip(xs, flags) if f],
        bins=18,
        color=PALETTE["warn"],
        edgecolor=PALETTE["ink"],
        alpha=0.65,
        label="artifact-flagged",
    )
    ax.set_xlabel("Structural surprisal −log P(X|C)")
    ax.set_ylabel("Passages")
    ax.set_title("Outlier engine (EXPLORATORY)")
    ax.legend(frameon=False)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_claims_vs_data(claims: list[dict], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not claims or not isinstance(claims, list) or "claim" not in claims[0]:
        # empty / summary-only fallback
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.axis("off")
        ax.text(0.5, 0.5, "Re-run discovery engine to refresh claims panel", ha="center", va="center")
        fig.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        return out_path
    names = [c["claim"][:42] for c in claims]
    struct = [c.get("rates", {}).get("any_required", 0) for c in claims]
    quant = [c.get("rates", {}).get("any_quantum", 0) for c in claims]
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    ax.barh(y + 0.18, struct, height=0.35, color=PALETTE["accent2"], label="structural components", edgecolor=PALETTE["ink"], lw=0.4)
    ax.barh(y - 0.18, quant, height=0.35, color=PALETTE["accent"], label="quantum components", edgecolor=PALETTE["ink"], lw=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("Fraction of examined passages with any matching features")
    ax.set_xlim(0, 1.05)
    ax.set_title("Claims vs data (popular analogies; EXPLORATORY)")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_temporal_firsts(temporal: dict, out_path: str | Path, top_n: int = 12) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combos = list((temporal.get("combinations") or {}).values())
    combos = sorted(combos, key=lambda x: x.get("midpoint") or 99999)[:top_n]
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
    if not combos:
        ax.axis("off")
        ax.text(0.5, 0.5, "No dated feature combinations available", ha="center")
    else:
        ys = range(len(combos))
        for i, c in enumerate(combos):
            ys_, ye = c.get("year_start"), c.get("year_end")
            mid = c.get("midpoint")
            if ys_ is not None and ye is not None:
                ax.plot([ys_, ye], [i, i], color=PALETTE["accent"], lw=3, solid_capstyle="round")
            if mid is not None:
                ax.scatter([mid], [i], color=PALETTE["ink"], zorder=3, s=28)
        ax.set_yticks(list(ys))
        ax.set_yticklabels([c.get("combination", "") for c in combos], fontsize=7)
        ax.set_xlabel("Approximate year (tradition prior ranges; wide = uncertain)")
        ax.set_title("Earliest feature combinations in sample (EXPLORATORY)")
        _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_translation_modernization(translation: dict, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    decades = translation.get("decade_modernization") or []
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    if decades:
        d = [r["decade"] for r in decades]
        m = [r["mean_modern_term_mentions"] for r in decades]
        q = [r["mean_qs"] if r["mean_qs"] is not None else np.nan for r in decades]
        axes[0].plot(d, m, marker="o", color=PALETTE["warn"])
        axes[0].set_xlabel("Translation decade")
        axes[0].set_ylabel("Mean modern-lexicon hits / passage")
        axes[0].set_title("Lexical modernization")
        _style(axes[0])
        axes[1].plot(d, q, marker="s", color=PALETTE["accent"])
        axes[1].axhline(0, color=PALETTE["muted"], lw=1)
        axes[1].set_xlabel("Translation decade")
        axes[1].set_ylabel("Mean QS")
        axes[1].set_title("QS by translation decade")
        _style(axes[1])
    else:
        for ax in axes:
            ax.axis("off")
            ax.text(0.5, 0.5, "No decade data", ha="center")
    fig.suptitle("Translation modernization analysis (EXPLORATORY)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_translation_shift_graph(shift: dict, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nodes = shift.get("nodes") or []
    edges = shift.get("edges") or []
    fig, ax = plt.subplots(figsize=(9.0, 3.8))
    ax.axis("off")
    if not nodes:
        ax.text(0.5, 0.5, "No aligned translation graph", ha="center", transform=ax.transAxes)
    else:
        n = len(nodes)
        for i, node in enumerate(nodes):
            x = 0.8 + i * 2.8
            ax.add_patch(
                mpatches.FancyBboxPatch(
                    (x, 1.0), 2.2, 1.6,
                    boxstyle="round,pad=0.03,rounding_size=0.08",
                    facecolor="#fff", edgecolor=PALETTE["accent"], lw=1.5,
                )
            )
            ax.text(
                x + 1.1,
                2.2,
                f"{node.get('year')}\n{node.get('id')}",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
            )
            ax.text(
                x + 1.1,
                1.45,
                f"modern terms: {node.get('n_modern_terms')}\nQS: {node.get('qs')}",
                ha="center",
                va="center",
                fontsize=7,
            )
            if i < len(edges):
                e = edges[i]
                ax.annotate(
                    "",
                    xy=(x + 2.7, 1.8),
                    xytext=(x + 2.3, 1.8),
                    arrowprops=dict(arrowstyle="->", color=PALETTE["warn"], lw=1.5),
                )
                gained = ",".join(list((e.get("lexicon_gained") or {}).keys())[:3]) or "—"
                ax.text(x + 2.5, 2.55, f"ΔQS={e.get('delta_qs'):+.2f}\n+{gained}", ha="center", fontsize=6.5, color=PALETTE["warn"])
        ax.set_xlim(0.4, 0.8 + n * 2.8)
        ax.set_ylim(0.6, 3.2)
    ax.set_title(
        f"Translation-shift graph — {shift.get('passage_family', 'aligned family')} (demo)",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_concept_graph_example(out_path: str | Path) -> Path:
    """Schematic of an evidence-bound concept graph (illustrative motif shape)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.axis("off")
    nodes = {
        "substrate": (2.0, 3.5),
        "space": (5.5, 3.5),
        "manifestation": (2.0, 1.2),
        "disturbance": (5.5, 1.2),
    }
    for name, (x, y) in nodes.items():
        ax.add_patch(plt.Circle((x, y), 0.55, facecolor="#eff6ff", edgecolor=PALETTE["accent"], lw=1.8))
        ax.text(x, y, name, ha="center", va="center", fontsize=9, fontweight="bold")
    edges = [
        ("substrate", "space", "pervades"),
        ("substrate", "manifestation", "manifests_as"),
        ("disturbance", "space", "propagates_through"),
        ("disturbance", "substrate", "is_state_of"),
    ]
    for s, t, lab in edges:
        x1, y1 = nodes[s]
        x2, y2 = nodes[t]
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color=PALETTE["ink"], lw=1.2, connectionstyle="arc3,rad=0.05"),
        )
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.15, lab, fontsize=7, color=PALETTE["muted"], ha="center")
    ax.set_xlim(0.8, 6.8)
    ax.set_ylim(0.3, 4.4)
    ax.set_title("Evidence-bound concept graph (illustrative field-like motif)", fontsize=12)
    ax.text(
        3.8,
        0.45,
        "Edges require YES labels + evidence spans — never hallucinated",
        ha="center",
        fontsize=8,
        color=PALETTE["muted"],
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_success_tiers(out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tiers = [
        ("Tier 1", "Methodological\nframework", PALETTE["level_i"], True),
        ("Tier 2", "New quantitative\nfinding", PALETTE["accent2"], True),
        ("Tier 3", "Conceptual /\nhistorical discovery", PALETTE["accent"], False),
        ("Tier 4", "Physics-relevant\nsurprise", PALETTE["warn"], False),
        ("Tier 5", "Transformative\n(extraordinary evidence)", PALETTE["neg"], False),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 3.4))
    ax.axis("off")
    for i, (name, desc, color, reached) in enumerate(tiers):
        x = 0.35 + i * 2.05
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (x, 0.7), 1.85, 2.2,
                boxstyle="round,pad=0.03,rounding_size=0.08",
                facecolor=color if reached else "#fff",
                alpha=0.25 if reached else 1.0,
                edgecolor=color,
                lw=2,
            )
        )
        ax.text(x + 0.92, 2.45, name, ha="center", fontsize=10, fontweight="bold", color=color)
        ax.text(x + 0.92, 1.6, desc, ha="center", fontsize=8)
        ax.text(
            x + 0.92,
            0.95,
            "in reach" if reached else "not claimed",
            ha="center",
            fontsize=7,
            style="italic",
            color=PALETTE["muted"],
        )
        if i < len(tiers) - 1:
            ax.annotate("", xy=(x + 2.0, 1.8), xytext=(x + 1.9, 1.8), arrowprops=dict(arrowstyle="->", lw=1.2))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0.4, 3.2)
    ax.set_title("Discovery success tiers — do not claim higher without evidence", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_cluster_bootstrap(cluster: dict[str, dict], out_path: str | Path, top_n: int = 10) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    items = list(cluster.items())[:top_n]
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    ys = []
    labels = []
    for i, (mid, cs) in enumerate(items):
        enr = cs.get("enrichment_work_level")
        ci = cs.get("ci95") or [None, None]
        if enr is None:
            continue
        ys.append(i)
        labels.append(mid)
        ax.plot([ci[0], ci[1]], [i, i], color=PALETTE["accent"], lw=2)
        ax.scatter([enr], [i], color=PALETTE["ink"], zorder=3, s=36)
    ax.axvline(1.0, color=PALETTE["muted"], ls="--", lw=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Work-level enrichment (bootstrap CI)")
    ax.set_title("Cluster-aware motif enrichment (EXPLORATORY)")
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_pd_pilot_panel(
    scores_path: str | Path,
    out_qs: str | Path,
    out_heat: str | Path,
) -> list[Path]:
    """PD historical pilot visuals."""
    df = pd.read_parquet(scores_path)
    hist = df[df["role"].isin(["target", "control", "negative_control"])]
    paths = []
    g = hist.groupby("tradition")["QS"].agg(["mean", "std", "count"]).reset_index()
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.bar(g["tradition"], g["mean"], yerr=g["std"].fillna(0), capsize=3, color=PALETTE["accent"], edgecolor=PALETTE["ink"])
    ax.axhline(0, color=PALETTE["muted"], lw=1)
    ax.set_ylabel("QS")
    ax.set_title("PD development pilot: QS by tradition (EXPLORATORY — not confirmatory)")
    plt.xticks(rotation=25, ha="right")
    _style(ax)
    fig.tight_layout()
    out_qs = Path(out_qs)
    fig.savefig(out_qs, dpi=200, bbox_inches="tight")
    plt.close(fig)
    paths.append(out_qs)

    theories = [
        "newtonian",
        "classical_em",
        "thermodynamics",
        "relativity",
        "quantum_mechanics",
        "quantum_field_theory",
    ]
    mat = hist.groupby("tradition")[theories].mean()
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    im = ax.imshow(mat.values, aspect="auto", cmap="cividis", vmin=0, vmax=max(0.01, float(mat.values.max())))
    ax.set_xticks(range(len(theories)))
    ax.set_xticklabels(theories, rotation=35, ha="right")
    ax.set_yticks(range(len(mat.index)))
    ax.set_yticklabels(list(mat.index))
    ax.set_title("PD pilot theory tournament (EXPLORATORY)")
    fig.colorbar(im, ax=ax, fraction=0.046, label="Similarity")
    _style(ax)
    fig.tight_layout()
    out_heat = Path(out_heat)
    fig.savefig(out_heat, dpi=200, bbox_inches="tight")
    plt.close(fig)
    paths.append(out_heat)
    return paths
