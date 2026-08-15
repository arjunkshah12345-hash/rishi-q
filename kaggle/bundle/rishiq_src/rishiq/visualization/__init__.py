"""Publication-quality figure generators for RISHI-Q.

All figures must be regenerable from data/code. No hand-drawn fake numbers.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import yaml


# Paper style: restrained, print-friendly (avoid purple glow / cream tropes)
PALETTE = {
    "ink": "#1a1a1a",
    "muted": "#5c5c5c",
    "accent": "#1d4ed8",
    "accent2": "#0f766e",
    "warn": "#b45309",
    "neg": "#b91c1c",
    "grid": "#e5e5e5",
    "level_i": "#94a3b8",
    "level_ii": "#0f766e",
    "level_iii": "#1d4ed8",
}


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=PALETTE["ink"])
    ax.yaxis.label.set_color(PALETTE["ink"])
    ax.xaxis.label.set_color(PALETTE["ink"])
    ax.title.set_color(PALETTE["ink"])


def plot_qs_by_tradition(df: pd.DataFrame, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g = df.groupby("tradition")["QS"].agg(["mean", "std", "count"]).reset_index()
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.bar(
        g["tradition"],
        g["mean"],
        yerr=g["std"].fillna(0),
        capsize=4,
        color=PALETTE["accent"],
        edgecolor=PALETTE["ink"],
        linewidth=0.6,
    )
    ax.axhline(0, color=PALETTE["muted"], lw=1)
    ax.set_ylabel("Quantum Specificity (QS)")
    ax.set_xlabel("Tradition / corpus slice")
    ax.set_title("QS by tradition (exploratory / synthetic instrument run)")
    plt.xticks(rotation=28, ha="right")
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_theory_heatmap(
    df: pd.DataFrame, theory_cols: list[str], out_path: str | Path
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mat = df.groupby("tradition")[theory_cols].mean()
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    im = ax.imshow(mat.values, aspect="auto", cmap="cividis", vmin=0, vmax=1)
    ax.set_xticks(range(len(theory_cols)))
    ax.set_xticklabels(theory_cols, rotation=35, ha="right")
    ax.set_yticks(range(len(mat.index)))
    ax.set_yticklabels(list(mat.index))
    ax.set_title("Mean theory similarity by tradition (weighted Jaccard)")
    fig.colorbar(im, ax=ax, fraction=0.046, label="Similarity")
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_robustness_forest(rows: list[dict], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    labels = [r["test_id"] for r in rows]
    vals = [r["delta_Q"] for r in rows]
    colors = [
        PALETTE["accent"] if r.get("status") == "computed" else PALETTE["level_i"]
        for r in rows
    ]
    fig, ax = plt.subplots(figsize=(8.2, 6.5))
    ax.axvline(0, color=PALETTE["muted"], lw=1)
    ax.scatter(vals, range(len(vals)), c=colors, zorder=3)
    for i, v in enumerate(vals):
        ax.plot([v - 0.02, v + 0.02], [i, i], color=colors[i], lw=2)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel(r"$\Delta_Q$ (exploratory)")
    ax.set_title("Robustness battery (scaffold; many arms not yet run)")
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_pipeline_diagram(out_path: str | Path) -> Path:
    """Schematic of the RISHI-Q analysis pipeline."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stages = [
        "Passage\n(+ provenance)",
        "Source\nblinding",
        "Proposition\nextraction",
        "Ontology\nannotation",
        "Evidence\nverification",
        "Feature\nvector",
        "Theory\nfingerprints",
        "QS / QEF\n+ statistics",
    ]
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.set_xlim(0, len(stages) + 0.2)
    ax.set_ylim(0, 2)
    ax.axis("off")
    for i, label in enumerate(stages):
        x = i + 0.5
        box = mpatches.FancyBboxPatch(
            (x - 0.42, 0.7),
            0.84,
            0.9,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            linewidth=1.2,
            edgecolor=PALETTE["ink"],
            facecolor="#f8fafc",
        )
        ax.add_patch(box)
        ax.text(x, 1.15, label, ha="center", va="center", fontsize=8, color=PALETTE["ink"])
        if i < len(stages) - 1:
            ax.annotate(
                "",
                xy=(x + 0.55, 1.15),
                xytext=(x + 0.42, 1.15),
                arrowprops=dict(arrowstyle="->", color=PALETTE["accent"], lw=1.4),
            )
    ax.text(
        len(stages) / 2,
        0.25,
        "Primary signal = explicit ontology labels · Embeddings secondary only · Confirmatory locked until preregistration",
        ha="center",
        fontsize=8,
        color=PALETTE["muted"],
    )
    ax.set_title("RISHI-Q analysis pipeline", fontsize=12, pad=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_ontology_overview(ontology_path: str | Path, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ont = yaml.safe_load(Path(ontology_path).read_text(encoding="utf-8"))
    features = ont["features"]
    families = {}
    levels = {"I": 0, "II": 0, "III": 0}
    for f in features:
        families[f["family"]] = families.get(f["family"], 0) + 1
        levels[f["level"]] = levels.get(f["level"], 0) + 1

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    fam_names = list(families.keys())
    fam_vals = [families[k] for k in fam_names]
    axes[0].barh(fam_names, fam_vals, color=PALETTE["accent2"], edgecolor=PALETTE["ink"], lw=0.5)
    axes[0].set_xlabel("Feature count")
    axes[0].set_title("Features by family")
    _style(axes[0])

    lvl_order = ["I", "II", "III"]
    colors = [PALETTE["level_i"], PALETTE["level_ii"], PALETTE["level_iii"]]
    axes[1].bar(
        [f"Level {x}" for x in lvl_order],
        [levels[x] for x in lvl_order],
        color=colors,
        edgecolor=PALETTE["ink"],
        lw=0.5,
    )
    axes[1].set_ylabel("Feature count")
    axes[1].set_title("Features by evidentiary level")
    _style(axes[1])
    fig.suptitle("RISHI-Q ontology v0.1 overview", fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_positive_control_validation(df: pd.DataFrame, out_path: str | Path) -> Path:
    """Show that modern physics passages map to expected theories."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    phys = df[df["role"] == "physics_reference"].copy()
    theories = [
        "newtonian",
        "classical_em",
        "thermodynamics",
        "relativity",
        "quantum_mechanics",
        "quantum_field_theory",
    ]
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    x = np.arange(len(phys))
    width = 0.13
    for i, t in enumerate(theories):
        ax.bar(
            x + (i - 2.5) * width,
            phys[t].values,
            width=width,
            label=t,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(phys["passage_id"], rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Similarity")
    ax.set_ylim(0, 1.05)
    ax.set_title("Positive-control validation: theory scores for modern physics passages")
    ax.legend(fontsize=7, ncol=3, frameon=False)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_qs_qef_scatter(df: pd.DataFrame, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    role_colors = {
        "physics_reference": PALETTE["accent"],
        "target": PALETTE["accent2"],
        "control": PALETTE["muted"],
        "negative_control": PALETTE["warn"],
    }
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    for role, g in df.groupby("role"):
        ax.scatter(
            g["QEF"],
            g["QS"],
            s=55,
            alpha=0.85,
            label=role,
            c=role_colors.get(role, PALETTE["ink"]),
            edgecolors=PALETTE["ink"],
            linewidths=0.4,
        )
        for _, row in g.iterrows():
            ax.annotate(
                row["passage_id"].replace("PHYS_", "").replace("SYN_", ""),
                (row["QEF"], row["QS"]),
                fontsize=6,
                textcoords="offset points",
                xytext=(4, 3),
                color=PALETTE["muted"],
            )
    ax.axhline(0, color=PALETTE["grid"], lw=1)
    ax.axvline(0, color=PALETTE["grid"], lw=1)
    ax.set_xlabel("Quantum-Exclusive Feature score (QEF)")
    ax.set_ylabel("Quantum Specificity (QS)")
    ax.set_title("QS vs QEF (exploratory synthetic + physics controls)")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_feature_heatmap_from_annotations(
    annotations: pd.DataFrame,
    meta: pd.DataFrame,
    out_path: str | Path,
    feature_ids: list[str] | None = None,
) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = annotations.merge(
        meta[["passage_id", "tradition", "role"]], on="passage_id", how="left"
    )
    df["pos"] = (df["label"] == "1").astype(float)
    if feature_ids is None:
        # prioritize quantum + field features for readability
        feature_ids = sorted(
            {
                f
                for f in df["feature_id"].unique()
                if f.startswith(("Q", "F", "M", "O", "D", "R"))
            }
        )
        # keep a manageable subset: those with any positives + all Q/F
        pos_feats = set(df.loc[df["pos"] > 0, "feature_id"])
        feature_ids = [f for f in feature_ids if f.startswith(("Q", "F")) or f in pos_feats]
    pivot = (
        df[df["feature_id"].isin(feature_ids)]
        .groupby(["tradition", "feature_id"])["pos"]
        .mean()
        .unstack(fill_value=0)
    )
    # order columns
    cols = [c for c in feature_ids if c in pivot.columns]
    pivot = pivot[cols]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    im = ax.imshow(pivot.values, aspect="auto", cmap="cividis", vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=90, fontsize=7)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(list(pivot.index), fontsize=8)
    ax.set_title("Feature positivity rate by tradition (label=1)")
    fig.colorbar(im, ax=ax, fraction=0.02, label="Mean positivity")
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_three_level_cartoon(out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    ax.axis("off")
    levels = [
        (
            "Level I\nGeneric metaphysical",
            "unity · change · hidden reality\ninterconnectedness · consciousness",
            PALETTE["level_i"],
            "Weak evidence for\nquantum claims",
        ),
        (
            "Level II\nClassical / field-like",
            "distributed substrate · local state\npropagation · mediation · oscillation",
            PALETTE["level_ii"],
            "May resemble classical\nfields — not QM/QFT",
        ),
        (
            "Level III\nQuantum-specific",
            "nonseparability · contextuality\nincompatible observables · quanta",
            PALETTE["level_iii"],
            "Stronger structural\ncorrespondence only",
        ),
    ]
    for i, (title, body, color, note) in enumerate(levels):
        x = 0.3 + i * 3.1
        rect = mpatches.FancyBboxPatch(
            (x, 0.6),
            2.8,
            2.4,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            facecolor=color,
            alpha=0.18,
            edgecolor=color,
            linewidth=2,
        )
        ax.add_patch(rect)
        ax.text(x + 1.4, 2.6, title, ha="center", va="top", fontsize=10, fontweight="bold")
        ax.text(x + 1.4, 1.85, body, ha="center", va="center", fontsize=8)
        ax.text(x + 1.4, 0.95, note, ha="center", va="center", fontsize=8, style="italic")
    ax.set_xlim(0, 9.6)
    ax.set_ylim(0.3, 3.3)
    ax.set_title("Central scientific distinction (RISHI-Q)", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_dev_confirmatory_firewall(out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.axis("off")
    boxes = [
        (0.4, "Development\ncorpus + ontology\npiloting", PALETTE["accent2"], "OPEN"),
        (3.5, "Preregistration\n(OSF / equivalent)", PALETTE["warn"], "DRAFT ONLY"),
        (6.6, "Confirmatory\ncorpus + H1 test", PALETTE["neg"], "LOCKED"),
    ]
    for x, text, color, badge in boxes:
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (x, 0.8),
                2.4,
                1.6,
                boxstyle="round,pad=0.03,rounding_size=0.08",
                facecolor="#fff",
                edgecolor=color,
                linewidth=2,
            )
        )
        ax.text(x + 1.2, 1.7, text, ha="center", va="center", fontsize=9)
        ax.text(
            x + 1.2,
            1.05,
            badge,
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color=color,
        )
    ax.annotate("", xy=(3.4, 1.6), xytext=(2.9, 1.6), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("", xy=(6.5, 1.6), xytext=(6.0, 1.6), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.set_xlim(0, 9.2)
    ax.set_ylim(0.4, 2.8)
    ax.set_title("Development vs confirmatory firewall", fontsize=12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_power_curves(power_json: str | Path, out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = pd.read_json(power_json)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for effect, g in rows.groupby("effect"):
        g = g.sort_values("n_clusters_per_arm")
        ax.plot(
            g["n_clusters_per_arm"],
            g["power"],
            marker="o",
            label=f"effect={effect}",
        )
    ax.axhline(0.8, color=PALETTE["muted"], ls="--", lw=1, label="target power 0.8")
    ax.set_xlabel("Clusters per arm (works)")
    ax.set_ylabel("Estimated power")
    ax.set_ylim(0, 1.05)
    ax.set_title("Exploratory power simulation (not confirmatory n)")
    ax.legend(frameon=False, fontsize=8)
    _style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path
