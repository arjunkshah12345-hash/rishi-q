#!/usr/bin/env python3
"""Extra ISEF figures: process, timeline, radar, evidence map, distance matrix."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/exploratory/isef_akasa_sound_field"
FIG = ROOT / "paper/figures"
SUM = json.loads((OUT / "summary.json").read_text())

NAVY, BLUE, GREEN, RED, SLATE, CREAM, GOLD = (
    "#0f2744",
    "#1d4ed8",
    "#15803d",
    "#b91c1c",
    "#64748b",
    "#f8fafc",
    "#b45309",
)


def style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.facecolor": CREAM,
            "figure.facecolor": "white",
            "axes.labelcolor": NAVY,
            "xtick.color": NAVY,
            "ytick.color": NAVY,
            "text.color": NAVY,
        }
    )


def fig_process():
    """Research iteration flowchart."""
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3)
    ax.axis("off")
    steps = [
        (0.3, "Reject\nCapra QM\nmemes"),
        (2.4, "Hunt obscure\nfield/sound\ntheories"),
        (4.5, "Lock\nākāśa↔śabda\n+ tejas split"),
        (6.6, "GRETIL\n9/9\nattestation"),
        (8.7, "Greek +\nMaxwell\nrubric"),
    ]
    for i, (x, lab) in enumerate(steps):
        ax.add_patch(
            mpatches.FancyBboxPatch(
                (x, 0.85),
                1.7,
                1.5,
                boxstyle="round,pad=0.04,rounding_size=0.08",
                facecolor="white",
                edgecolor=NAVY,
                linewidth=1.4,
            )
        )
        ax.text(x + 0.85, 1.6, lab, ha="center", va="center", fontsize=8.5, color=NAVY, fontweight="bold")
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.05, 1.6), xytext=(x + 1.75, 1.6), arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.8))
    ax.text(5.5, 0.35, "Iterative path → ISEF-AKASA-SOUND-FIELD  ·  Arjun Shah", ha="center", fontsize=9, color=SLATE)
    ax.set_title("Research process (iteration, not post-hoc fitting)", loc="left", fontsize=11, fontweight="bold", color=NAVY, pad=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig42_isef_process.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "fig42_isef_process.png", dpi=220, bbox_inches="tight")
    plt.close()


def fig_timeline():
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.set_xlim(-800, 2100)
    ax.set_ylim(0, 2)
    ax.axhline(1, color=SLATE, lw=1.2)
    events = [
        (-400, "Kaṇāda\nVaiśeṣika\n(approx.)", GREEN),
        (-50, "Lucretius\nDRN", SLATE),
        (360, "Timaeus\n(text; earlier)", SLATE),
        (1865, "Maxwell\nEM", RED),
        (2026, "This\nstudy", BLUE),
    ]
    # Timaeus is 4th c BCE - fix
    events = [
        (-450, "Kaṇāda\n(~est.)", GREEN),
        (-360, "Plato\nTimaeus", SLATE),
        (-55, "Lucretius", SLATE),
        (1865, "Maxwell\nEM", RED),
        (2026, "This\nstudy", BLUE),
    ]
    for x, lab, c in events:
        ax.plot(x, 1, "o", color=c, markersize=12, markeredgecolor=NAVY, markeredgewidth=0.8)
        ax.text(x, 1.45 if x < 1000 else 0.35, lab, ha="center", va="bottom" if x < 1000 else "top", fontsize=8, color=NAVY, fontweight="bold")
    ax.set_yticks([])
    ax.set_xlabel("Year (approximate CE; negative = BCE)")
    ax.set_title("Historical placement of compared ontologies", loc="left", fontsize=11, fontweight="bold", color=NAVY)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig43_isef_timeline.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "fig43_isef_timeline.png", dpi=220, bbox_inches="tight")
    plt.close()


def fig_radar():
    labels = ["R1\nmedium", "R2\nsound↔med", "R3\nlight split", "R4\natoms", "R5\ninert med", "R6\nMaxwell"]
    traditions = {
        "Vaiśeṣika": SUM["comparative_rubric"]["traditions"]["kanada"]["vector"],
        "Lucretius": SUM["comparative_rubric"]["traditions"]["lucretius"]["vector"],
        "Timaeus": SUM["comparative_rubric"]["traditions"]["timaeus"]["vector"],
        "Maxwell": SUM["comparative_rubric"]["traditions"]["maxwell"]["vector"],
    }
    colors = {"Vaiśeṣika": GREEN, "Lucretius": SLATE, "Timaeus": GOLD, "Maxwell": RED}
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6.2, 6.2), subplot_kw=dict(polar=True))
    for name, vec in traditions.items():
        vals = vec + vec[:1]
        ax.plot(angles, vals, color=colors[name], lw=2, label=name)
        ax.fill(angles, vals, color=colors[name], alpha=0.12)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["0", "1"])
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), frameon=False, fontsize=8)
    ax.set_title("Ontology radar (binary rubric)", fontsize=11, fontweight="bold", color=NAVY, pad=16)
    fig.tight_layout()
    fig.savefig(FIG / "fig44_isef_radar.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "fig44_isef_radar.png", dpi=220, bbox_inches="tight")
    plt.close()


def fig_distance_matrix():
    names = ["Kaṇāda", "Lucretius", "Timaeus", "Maxwell"]
    # Build from vectors
    vecs = [
        SUM["comparative_rubric"]["traditions"]["kanada"]["vector"],
        SUM["comparative_rubric"]["traditions"]["lucretius"]["vector"],
        SUM["comparative_rubric"]["traditions"]["timaeus"]["vector"],
        SUM["comparative_rubric"]["traditions"]["maxwell"]["vector"],
    ]
    D = np.zeros((4, 4))
    for i in range(4):
        for j in range(4):
            D[i, j] = sum(a != b for a, b in zip(vecs[i], vecs[j]))
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    im = ax.imshow(D, cmap="YlOrRd", vmin=0, vmax=6)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(names, rotation=20)
    ax.set_yticklabels(names)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{int(D[i,j])}", ha="center", va="center", color=NAVY if D[i, j] < 3 else "white", fontweight="bold")
    ax.set_title("Hamming distance matrix (0–6)", loc="left", fontsize=11, fontweight="bold", color=NAVY)
    fig.colorbar(im, ax=ax, fraction=0.046, label="feature mismatches")
    fig.tight_layout()
    fig.savefig(FIG / "fig45_isef_distance.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "fig45_isef_distance.png", dpi=220, bbox_inches="tight")
    plt.close()


def fig_evidence_map():
    items = SUM["theory_attestation"]["items"]
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    y = np.arange(len(items))
    ax.barh(y, [1] * len(items), color=GREEN, height=0.65, edgecolor=NAVY, linewidth=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{it['id']}: {it['claim'][:42]}" for it in items], fontsize=8)
    ax.set_xlim(0, 1.15)
    ax.set_xticks([])
    for i, it in enumerate(items):
        sut = ", ".join(it["found"])
        ax.text(0.02, i, sut, va="center", fontsize=7.5, color="white", fontweight="bold")
    ax.set_title("Evidence map — checklist item → GRETIL sutra IDs (all pass)", loc="left", fontsize=11, fontweight="bold", color=NAVY)
    ax.invert_yaxis()
    for spine in ["top", "right", "bottom"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig46_isef_evidence.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "fig46_isef_evidence.png", dpi=220, bbox_inches="tight")
    plt.close()


def fig_claim_contrast():
    """Popular claim vs attested theory."""
    fig, ax = plt.subplots(figsize=(10.5, 3.4))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    # left box - popular
    ax.add_patch(mpatches.FancyBboxPatch((0.2, 0.4), 4.4, 2.2, boxstyle="round,pad=0.05", facecolor="#fef2f2", edgecolor=RED, lw=1.5))
    ax.text(2.4, 2.3, "Popular claim (reject)", ha="center", fontsize=10, fontweight="bold", color=RED)
    ax.text(2.4, 1.5, "ākāśa ≈ quantum field / EM energy\nspanda ≈ quantum vibration\noneness ≈ entanglement", ha="center", va="center", fontsize=8.5, color=NAVY)
    # right box - attested
    ax.add_patch(mpatches.FancyBboxPatch((5.4, 0.4), 4.4, 2.2, boxstyle="round,pad=0.05", facecolor="#f0fdf4", edgecolor=GREEN, lw=1.5))
    ax.text(7.6, 2.3, "Attested theory (this paper)", ha="center", fontsize=10, fontweight="bold", color=GREEN)
    ax.text(7.6, 1.5, "ākāśa marked by sound (śabda)\ntejas carries light/heat\nmedium is actionless — not Maxwell", ha="center", va="center", fontsize=8.5, color=NAVY)
    ax.annotate("", xy=(5.3, 1.5), xytext=(4.7, 1.5), arrowprops=dict(arrowstyle="->", color=NAVY, lw=2))
    ax.set_title("Claim filter: discard Capra upgrades; keep recoverable ontology", loc="left", fontsize=11, fontweight="bold", color=NAVY)
    fig.tight_layout()
    fig.savefig(FIG / "fig47_isef_claim_filter.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUT / "fig47_isef_claim_filter.png", dpi=220, bbox_inches="tight")
    plt.close()


def main():
    style()
    FIG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fig_process()
    fig_timeline()
    fig_radar()
    fig_distance_matrix()
    fig_evidence_map()
    fig_claim_contrast()
    print("wrote fig42–fig47")


if __name__ == "__main__":
    main()
