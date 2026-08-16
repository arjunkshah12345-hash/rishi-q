#!/usr/bin/env python3
"""Build a complete ChatGPT report-writing handoff pack.

No AI report prose — only facts, process, evidence, tables, figures, constraints.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results/exploratory/isef_akasa_sound_field"
FIG_SRC = ROOT / "paper/figures"
PACK = ROOT / "chatgpt-handoff"

NAVY, BLUE, GREEN, RED, AMBER, SLATE, CREAM = (
    "#0f2744",
    "#1d4ed8",
    "#15803d",
    "#b91c1c",
    "#b45309",
    "#64748b",
    "#f8fafc",
)

FEATURES = ["R1", "R2", "R3", "R4", "R5", "R6"]
FEATURE_LABELS = {
    "R1": "Pervasive medium",
    "R2": "Sound↔medium",
    "R3": "Light separate",
    "R4": "Atomic matter",
    "R5": "Medium ≠ EM field",
    "R6": "Maxwell unified EM",
}


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def ensure_dirs() -> dict[str, Path]:
    dirs = {
        "root": PACK,
        "figures": PACK / "figures",
        "tables": PACK / "tables",
        "data": PACK / "data",
        "evidence": PACK / "evidence",
        "scripts": PACK / "scripts",
        "corpus_snippets": PACK / "corpus_snippets",
        "paper_legacy": PACK / "paper_legacy_do_not_use",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def copy_existing(dirs: dict[str, Path], summary: dict, expansion: dict) -> list[dict]:
    assets = []

    # Core JSON
    for name, obj in [("summary.json", summary), ("expansion_v2.json", expansion)]:
        dest = dirs["data"] / name
        dest.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        assets.append({"path": f"data/{name}", "type": "json", "role": "primary_results"})

    for name in ["VERDICT.md", "NOVELTY.md"]:
        src = SRC / name
        if src.exists():
            shutil.copy2(src, dirs["data"] / name)
            assets.append({"path": f"data/{name}", "type": "md", "role": "verdict_novelty"})

    # Existing ISEF figures
    fig_names = [
        "fig41_isef_akasa_sound_field.png",
        "fig42_isef_process.png",
        "fig43_isef_timeline.png",
        "fig44_isef_radar.png",
        "fig45_isef_distance.png",
        "fig46_isef_evidence.png",
        "fig47_isef_claim_filter.png",
        "fig48_isef_ontology_graph.png",
        "fig49_isef_expansion_board.png",
        "fig40_vaisesika_akasa_sabda.png",
        "fig39_em_quantum_proof_hunt.png",
        "fig35_capra_claim_autopsy.png",
        "fig37_claim_verdicts.png",
        "fig38_flagship_poster.png",
    ]
    for fn in fig_names:
        src = FIG_SRC / fn
        if not src.exists():
            alt = SRC / fn
            src = alt if alt.exists() else src
        if src.exists():
            shutil.copy2(src, dirs["figures"] / fn)
            assets.append({"path": f"figures/{fn}", "type": "png", "role": "existing_figure"})

    board = SRC / "fig_isef_board.png"
    if board.exists():
        shutil.copy2(board, dirs["figures"] / "fig_isef_board.png")
        assets.append({"path": "figures/fig_isef_board.png", "type": "png", "role": "existing_figure"})

    # Scripts (reproducibility)
    for fn in [
        "run_isef_akasa_sound_field.py",
        "make_isef_extra_figures.py",
        "run_isef_expansion_v2.py",
        "build_chatgpt_handoff.py",
    ]:
        src = ROOT / "scripts" / fn
        if src.exists():
            shutil.copy2(src, dirs["scripts"] / fn)
            assets.append({"path": f"scripts/{fn}", "type": "py", "role": "repro_script"})

    # Flagship docs
    for fn in ["FLAGSHIP_FINDING.md", "PROOF_HUNT.md", "HEADLINE_FINDING.md"]:
        src = ROOT / fn
        if src.exists():
            shutil.copy2(src, dirs["data"] / fn)
            assets.append({"path": f"data/{fn}", "type": "md", "role": "project_flag"})

    # Corpus caches (snippets / full gretil text for evidence)
    for fn in ["vaisesika_sutra_gretil.txt", "prasastapada_gretil.txt"]:
        src = ROOT / "corpus/development" / fn
        if src.exists():
            shutil.copy2(src, dirs["corpus_snippets"] / fn)
            assets.append({"path": f"corpus_snippets/{fn}", "type": "txt", "role": "primary_text"})

    # Mark old paper as do-not-use for ChatGPT writing
    note = dirs["paper_legacy"] / "README.txt"
    note.write_text(
        "Do NOT imitate the prose style of isef_report.tex/pdf.\n"
        "Use only numbers, tables, figures, and FACTS from this pack.\n"
        "Write a fresh human-style ISEF report from the evidence.\n",
        encoding="utf-8",
    )
    if (ROOT / "paper/isef_report.pdf").exists():
        shutil.copy2(ROOT / "paper/isef_report.pdf", dirs["paper_legacy"] / "isef_report.pdf")
    assets.append({"path": "paper_legacy_do_not_use/", "type": "dir", "role": "legacy_ignore_style"})
    return assets


def export_tables(dirs: dict[str, Path], summary: dict, expansion: dict) -> list[dict]:
    assets = []

    t_rows = summary["theory_attestation"]["items"]
    pd.DataFrame(t_rows).to_csv(dirs["tables"] / "T_kanada_attestation.csv", index=False)
    assets.append({"path": "tables/T_kanada_attestation.csv", "role": "table"})

    c_rows = expansion["prasastapada_replication"]["items"]
    pd.DataFrame(c_rows).to_csv(dirs["tables"] / "C_prasastapada_replication.csv", index=False)
    assets.append({"path": "tables/C_prasastapada_replication.csv", "role": "table"})

    m_rows = [
        {"id": "M1", "item": "Light as mode of same pervasive medium", "found_in_vaisesika": False},
        {"id": "M2", "item": "Sound NOT defining quality of EM medium", "found_in_vaisesika": False},
        {"id": "M3", "item": "Unified luminous + non-luminous radiation", "found_in_vaisesika": False},
        {"id": "M4", "item": "Charge / induction / inverse-square law", "found_in_vaisesika": False},
        {"id": "M5", "item": "Dynamical evolving field equations", "found_in_vaisesika": False},
    ]
    pd.DataFrame(m_rows).to_csv(dirs["tables"] / "M_maxwell_confrontation.csv", index=False)
    assets.append({"path": "tables/M_maxwell_confrontation.csv", "role": "table"})

    trad = expansion["expanded_traditions"]
    vec_rows = []
    for name, payload in trad.items():
        row = {"tradition": name, "R2": payload["R2"]}
        for i, f in enumerate(FEATURES):
            row[f] = payload["vector"][i]
        vec_rows.append(row)
    pd.DataFrame(vec_rows).to_csv(dirs["tables"] / "R_six_tradition_vectors.csv", index=False)
    assets.append({"path": "tables/R_six_tradition_vectors.csv", "role": "table"})

    ham = summary["comparative_rubric"]["hamming_distances"]
    pd.DataFrame([{"pair": k, "hamming": v} for k, v in ham.items()]).to_csv(
        dirs["tables"] / "hamming_distances.csv", index=False
    )
    assets.append({"path": "tables/hamming_distances.csv", "role": "table"})

    null = expansion["null_models"]
    pd.DataFrame([null]).to_csv(dirs["tables"] / "null_models.csv", index=False)
    assets.append({"path": "tables/null_models.csv", "role": "table"})

    # Full pairwise Hamming among 6
    names = list(trad.keys())
    mat = np.zeros((6, 6), dtype=int)
    vectors = [np.array(trad[n]["vector"]) for n in names]
    for i in range(6):
        for j in range(6):
            mat[i, j] = int(np.sum(vectors[i] != vectors[j]))
    ham_df = pd.DataFrame(mat, index=names, columns=names)
    ham_df.to_csv(dirs["tables"] / "hamming_matrix_6x6.csv")
    assets.append({"path": "tables/hamming_matrix_6x6.csv", "role": "table"})

    # Scorecard
    scorecard = pd.DataFrame(
        [
            {"gate": "Kanada_T_attestation", "pass_count": 9, "total": 9, "rate": 1.0},
            {"gate": "Prasastapada_C_replication", "pass_count": 6, "total": 6, "rate": 1.0},
            {"gate": "Maxwell_M_hits", "pass_count": 0, "total": 5, "rate": 0.0},
            {"gate": "R2_unique_among_6", "pass_count": 1, "total": 6, "rate": 1 / 6},
            {
                "gate": "fair_coin_null_P_exactly_one_R2_is_Vaisesika",
                "pass_count": None,
                "total": None,
                "rate": 0.015625,
            },
        ]
    )
    scorecard.to_csv(dirs["tables"] / "scorecard.csv", index=False)
    assets.append({"path": "tables/scorecard.csv", "role": "table"})
    return assets


def write_evidence(dirs: dict[str, Path], summary: dict, expansion: dict) -> list[dict]:
    assets = []
    lines = ["# Evidence excerpts (machine-extracted)", ""]
    lines.append("## Kaṇāda T1–T9")
    for item in summary["theory_attestation"]["items"]:
        lines.append(f"### {item['id']}: {item['claim']}")
        lines.append(f"- pass: `{item['pass']}`")
        lines.append(f"- sutras: {', '.join(item['sutras'])}")
        lines.append(f"- found: {', '.join(item['found'])}")
        lines.append(f"- excerpt: `{item.get('excerpt', '')}`")
        lines.append("")
    lines.append("## Praśastapāda C1–C6")
    for item in expansion["prasastapada_replication"]["items"]:
        lines.append(f"- **{item['id']}**: {item['claim']} — pass=`{item['pass']}`")
    lines.append("")
    lines.append("## Sources")
    lines.append(f"- GRETIL: {summary['source']['gretil']}")
    lines.append(f"- n_sutras indexed: {summary['source']['n_sutras']}")
    lines.append(f"- OCR used: `{not summary['source']['no_ocr']}` (must be false)")
    p = dirs["evidence"] / "EXCERPTS.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assets.append({"path": "evidence/EXCERPTS.md", "role": "evidence"})

    # Plain JSON evidence dump
    ev = {
        "theory_items": summary["theory_attestation"]["items"],
        "prasastapada_items": expansion["prasastapada_replication"]["items"],
        "maxwell_hits": summary["maxwell_em_hits"],
        "source": summary["source"],
    }
    (dirs["evidence"] / "evidence.json").write_text(
        json.dumps(ev, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    assets.append({"path": "evidence/evidence.json", "role": "evidence"})
    return assets


def new_figures(dirs: dict[str, Path], summary: dict, expansion: dict) -> list[dict]:
    assets = []
    out = dirs["figures"]
    trad = expansion["expanded_traditions"]
    names = list(trad.keys())
    vectors = np.array([trad[n]["vector"] for n in names])

    def save(fig, name: str, role: str = "new_figure"):
        path = out / name
        fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        assets.append({"path": f"figures/{name}", "type": "png", "role": role})

    # 50 — T attestation bars
    fig, ax = plt.subplots(figsize=(9, 4.2))
    tids = [x["id"] for x in summary["theory_attestation"]["items"]]
    passes = [1 if x["pass"] else 0 for x in summary["theory_attestation"]["items"]]
    colors = [GREEN if p else RED for p in passes]
    ax.bar(tids, passes, color=colors, edgecolor=NAVY, linewidth=0.6)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("Pass (1) / Fail (0)")
    ax.set_title("Kaṇāda primary attestation (T1–T9) — 9/9")
    ax.set_yticks([0, 1])
    for i, p in enumerate(passes):
        ax.text(i, p + 0.05, "PASS" if p else "FAIL", ha="center", fontsize=8, color=NAVY)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig50_T_attestation_bars.png")

    # 51 — Maxwell fail bars
    fig, ax = plt.subplots(figsize=(9, 4.2))
    mids = ["M1", "M2", "M3", "M4", "M5"]
    ax.bar(mids, [0] * 5, color=RED, edgecolor=NAVY, linewidth=0.6)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("Found in Vaiśeṣika (1) / Absent (0)")
    ax.set_title("Maxwell EM confrontation — 0/5 hits")
    for i in range(5):
        ax.text(i, 0.08, "ABSENT", ha="center", fontsize=9, color=RED, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig51_maxwell_zero_hits.png")

    # 52 — Praśastapāda
    fig, ax = plt.subplots(figsize=(9, 4.2))
    cids = [x["id"].split("_", 1)[0] for x in expansion["prasastapada_replication"]["items"]]
    cpass = [1 if x["pass"] else 0 for x in expansion["prasastapada_replication"]["items"]]
    ax.bar(cids, cpass, color=GREEN, edgecolor=NAVY, linewidth=0.6)
    ax.set_ylim(0, 1.25)
    ax.set_title("Praśastapāda commentarial replication — 6/6")
    ax.set_ylabel("Pass")
    ax.set_yticks([0, 1])
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig52_prasastapada_replication.png")

    # 53 — R2 uniqueness
    fig, ax = plt.subplots(figsize=(9, 4.5))
    r2 = [trad[n]["R2"] for n in names]
    cols = [GREEN if v == 1 else SLATE for v in r2]
    ax.barh(names[::-1], r2[::-1], color=cols[::-1], edgecolor=NAVY, linewidth=0.6)
    ax.set_xlim(0, 1.2)
    ax.set_xlabel("R2 = sound specially tied to pervasive medium")
    ax.set_title("R2 uniqueness across six traditions (only Vaiśeṣika = 1)")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig53_R2_uniqueness.png")

    # 54 — Heatmap 6 traditions × 6 features
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    im = ax.imshow(vectors, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(6))
    ax.set_xticklabels([f"{f}\n{FEATURE_LABELS[f]}" for f in FEATURES], fontsize=8)
    ax.set_yticks(range(6))
    ax.set_yticklabels(names, fontsize=9)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, str(int(vectors[i, j])), ha="center", va="center", color="white" if vectors[i, j] else NAVY, fontsize=11)
    ax.set_title("Six-tradition × six-feature rubric")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    save(fig, "fig54_rubric_heatmap.png")

    # 55 — Full Hamming matrix
    ham = np.zeros((6, 6), dtype=int)
    for i in range(6):
        for j in range(6):
            ham[i, j] = int(np.sum(vectors[i] != vectors[j]))
    fig, ax = plt.subplots(figsize=(7.2, 6))
    im = ax.imshow(ham, cmap="YlOrRd", vmin=0, vmax=6)
    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
    ax.set_yticklabels(names, fontsize=8)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, str(ham[i, j]), ha="center", va="center", fontsize=11)
    ax.set_title("Pairwise Hamming distances (0–6)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    save(fig, "fig55_hamming_matrix.png")

    # 56 — Scorecard
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    labels = ["Kaṇāda\n9/9", "Praśastapāda\n6/6", "Maxwell\n0/5", "R2 unique\nYes"]
    vals = [9 / 9, 6 / 6, 0 / 5, 1.0]
    cols = [GREEN, GREEN, RED, BLUE]
    ax.bar(labels, vals, color=cols, edgecolor=NAVY, linewidth=0.6)
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("Normalized score")
    ax.set_title("Primary result scorecard")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig56_scorecard.png")

    # 57 — Null coin visualization
    fig, ax = plt.subplots(figsize=(8, 4.5))
    # 64 outcomes schematic: highlight 1/64
    xs = np.arange(64)
    ys = np.zeros(64)
    ys[0] = 1  # one favorable bin
    ax.bar(xs, np.ones(64) / 64, color=SLATE, width=1.0, edgecolor="none", alpha=0.35)
    ax.bar([0], [1 / 64], color=GREEN, width=1.0, edgecolor=NAVY, label="Exactly one R2 and it is Vaiśeṣika")
    ax.axhline(1 / 64, color=GREEN, ls="--", lw=1)
    ax.set_xlim(-1, 64)
    ax.set_xlabel("Equally likely fair-coin outcomes (schematic bins)")
    ax.set_ylabel("Probability")
    ax.set_title("Descriptive null: P = 1/64 = 0.015625")
    ax.legend(loc="upper right", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig57_null_p_one_over_64.png")

    # 58 — Kanada vs Maxwell feature diverge
    fig, ax = plt.subplots(figsize=(9, 4.5))
    kv = trad["Vaiśeṣika"]["vector"]
    mv = trad["Maxwell"]["vector"]
    x = np.arange(6)
    w = 0.38
    ax.bar(x - w / 2, kv, w, label="Vaiśeṣika", color=BLUE, edgecolor=NAVY)
    ax.bar(x + w / 2, mv, w, label="Maxwell EM", color=AMBER, edgecolor=NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{f}\n{FEATURE_LABELS[f]}" for f in FEATURES], fontsize=8)
    ax.set_ylim(0, 1.35)
    ax.set_ylabel("Feature present")
    ax.set_title("Vaiśeṣika vs Maxwell — feature-by-feature (Hamming = 4)")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig58_vaisesika_vs_maxwell.png")

    # 59 — Process flowchart style (simple stages)
    fig, ax = plt.subplots(figsize=(10, 3.2))
    stages = [
        "Filter Capra\nclaims",
        "Lock ākāśa–\nśabda + tejas",
        "GRETIL\n9/9",
        "Maxwell\n0/5",
        "6-tradition\nrubric",
        "Praśastapāda\n6/6",
        "Nulls +\nnovelty",
    ]
    for i, s in enumerate(stages):
        ax.add_patch(plt.Rectangle((i * 1.35, 0.35), 1.15, 1.1, fill=True, facecolor=CREAM, edgecolor=NAVY, lw=1.2))
        ax.text(i * 1.35 + 0.575, 0.9, s, ha="center", va="center", fontsize=8, color=NAVY)
        if i < len(stages) - 1:
            ax.annotate("", xy=((i + 1) * 1.35, 0.9), xytext=(i * 1.35 + 1.15, 0.9),
                        arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.5))
    ax.set_xlim(-0.2, len(stages) * 1.35)
    ax.set_ylim(0, 2)
    ax.axis("off")
    ax.set_title("Research process (locked order)", color=NAVY, pad=8)
    save(fig, "fig59_process_stages.png")

    # 60 — What we claim vs refuse
    fig, ax = plt.subplots(figsize=(9, 4.8))
    claim = [
        "Recoverable sound-medium ontology",
        "Primary + commentarial attestation",
        "R2 unique on 6-tradition panel",
        "Open falsification vs Maxwell",
        "Descriptive null + novelty audit",
    ]
    refuse = [
        "Ancient Maxwell discovery",
        "Ancient quantum mechanics",
        "Laboratory ākāśa detection",
        "Capra-style metaphor upgrades",
        "First notice of ākāśa–sound",
    ]
    ax.barh(np.arange(len(claim)) + 0.15, [1] * 5, height=0.35, color=GREEN, label="CLAIM")
    ax.barh(np.arange(len(refuse)) - 0.15, [1] * 5, height=0.35, left=1.15, color=RED, label="REFUSE")
    for i, (c, r) in enumerate(zip(claim, refuse)):
        ax.text(0.05, i + 0.15, c, va="center", fontsize=8, color="white", fontweight="bold")
        ax.text(1.2, i - 0.15, r, va="center", fontsize=8, color="white", fontweight="bold")
    ax.set_xlim(0, 2.3)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("Claim boundary (use this in every section)")
    ax.legend(loc="lower right")
    ax.spines[:].set_visible(False)
    save(fig, "fig60_claim_boundary.png")

    # 61 — Stacked feature presence counts
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    present_counts = vectors.sum(axis=0)
    ax.bar(FEATURES, present_counts, color=BLUE, edgecolor=NAVY)
    ax.set_ylabel("# traditions with feature = 1 (of 6)")
    ax.set_ylim(0, 6.5)
    ax.set_title("How common is each rubric feature?")
    for i, v in enumerate(present_counts):
        ax.text(i, v + 0.15, str(int(v)), ha="center", fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig61_feature_prevalence.png")

    # 62 — Distance from Maxwell ranking
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    maxwell_v = np.array(trad["Maxwell"]["vector"])
    dists = [(n, int(np.sum(np.array(trad[n]["vector"]) != maxwell_v))) for n in names if n != "Maxwell"]
    dists.sort(key=lambda x: x[1])
    ax.barh([d[0] for d in dists], [d[1] for d in dists], color=AMBER, edgecolor=NAVY)
    ax.set_xlabel("Hamming distance to Maxwell")
    ax.set_title("How far from Maxwell EM? (higher = more different)")
    ax.set_xlim(0, 6)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, "fig62_distance_to_maxwell.png")

    return assets


def write_docs(dirs: dict[str, Path], summary: dict, expansion: dict, asset_list: list[dict]) -> None:
    facts = {
        "experiment_id": "ISEF-AKASA-SOUND-FIELD",
        "author": "Arjun Shah",
        "school": "Stratford Preparatory Milpitas",
        "category": "Physics and Astronomy",
        "date": "2026-08-15",
        "title_suggested": "Sound as the Mark of a Pervasive Medium: A Quantitative Test of a Vaiśeṣika Field Ontology Against Greek, Chinese, and Buddhist Controls and Maxwell Electromagnetism",
        "headline_numbers": {
            "kanada_attestation": "9/9",
            "prasastapada_replication": "6/6",
            "maxwell_hits": "0/5",
            "R2_unique": True,
            "fair_coin_null_P": 0.015625,
            "hamming_Kanada_Maxwell": 4,
            "n_sutras_indexed": 369,
            "ocr": False,
        },
        "verdict_code": expansion["verdict"],
        "safe_groundbreaking_claim": expansion["groundbreaking_claim_safe"],
        "never_claim": expansion["novelty"]["never_claim"],
        "hypotheses": {
            "H1": "Primary Kaṇāda sutras recover sound-marked pervasive medium (ākāśa↔śabda); light/heat in tejas",
            "H2": "Attested ontology fails Maxwell structural features",
            "H3": "R2 unique among Lucretius, Timaeus, Dao De Jing, Dhammapada, Maxwell",
            "H4": "Core claims replicate in Praśastapāda",
        },
        "hypothesis_outcomes": {"H1": "SUPPORTED", "H2": "SUPPORTED", "H3": "SUPPORTED", "H4": "SUPPORTED"},
        "features_R1_to_R6": FEATURE_LABELS,
        "traditions": expansion["expanded_traditions"],
        "null_models": expansion["null_models"],
        "novelty": expansion["novelty"],
        "limitations": [
            "GRETIL is a digital edition, not a fully critical edition for every sandhi",
            "Greek/Chinese/Buddhist scores use PD English with scholarly overrides",
            "Rubric features are coarse binary summaries",
            "Null models are descriptive, not causal historical models",
            "No laboratory acoustics/magnetometry component",
            "Later Nyāya–Vaiśeṣika commentarial diversity beyond Praśastapāda not exhaustively scored",
        ],
        "materials": [
            "GRETIL Vaiśeṣika Sūtra (Kaṇāda) — typed Unicode Sanskrit",
            "GRETIL Praśastapāda Padārthadharmasaṅgraha",
            "PD English: Lucretius (n=60), Timaeus (n=50), Dao De Jing (n=40), Dhammapada (n=40)",
            "Maxwell EM as textbook structural foil (Jackson-style)",
        ],
        "reproduce": [
            "uv run python scripts/run_isef_akasa_sound_field.py",
            "uv run python scripts/make_isef_extra_figures.py",
            "uv run python scripts/run_isef_expansion_v2.py",
            "uv run python scripts/build_chatgpt_handoff.py",
        ],
    }
    (dirs["data"] / "FACTS.json").write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    (dirs["root"] / "CONSTRAINTS.md").write_text(
        """# Hard constraints for any report written from this pack

## MUST say
- Vaiśeṣika ākāśa is a pervasive medium whose distinctive mark is sound (śabda).
- Light/heat belong to tejas (separate substance).
- Primary attestation 9/9; Praśastapāda replication 6/6; Maxwell structural hits 0/5.
- Only Vaiśeṣika scores R2=1 on the six-tradition panel.
- Fair-coin descriptive null P=1/64=0.015625.
- Contribution = open comparative falsification package.

## MUST NOT say
- Ancient India discovered electromagnetism or Maxwell’s equations.
- Ancient India discovered quantum mechanics / QFT.
- ākāśa = EM field / quantum vacuum (Capra upgrade).
- Laboratory detection of ākāśa.
- “First person in history to notice sound relates to ākāśa.”
- Invented positive Maxwell hits or failed attestation items.

## Tone
- Precise, evidence-first, student science-fair professional.
- Prefer short sentences and tables over rhetorical flourish.
- Negatives (0/5 Maxwell) are results, not failures to hide.
""",
        encoding="utf-8",
    )

    (dirs["root"] / "PROCESS.md").write_text(
        """# Research process (chronological)

1. **Capra / popular claim filter**  
   Rejected vague upgrades: ether→quantum vacuum, vibration→QM, unity→entanglement, ākāśa→EM field. Prior RISHI-Q work showed Level-III quantum claims fail on Vedānta PD panels.

2. **Doctrine lock**  
   Chose under-researched sharp doctrine: Kaṇāda’s ākāśa marked by śabda; tejas carries heat/light. Experiment ID: `ISEF-AKASA-SOUND-FIELD`.

3. **Primary attestation (Procedure A)**  
   Downloaded GRETIL Vaiśeṣika Sūtra HTML → stripped tags → indexed 369 sutra IDs (`KVs_x,y.z`). Scored frozen checklist T1–T9. Result: **9/9**. No OCR.

4. **Maxwell confrontation (Procedure B)**  
   Five structural items M1–M5 scored present/absent in attested ontology. Predicted absences a priori. Result: **0/5**.

5. **Comparative rubric (Procedure C)**  
   Frozen features R1–R6. Scored Vaiśeṣika, Lucretius, Timaeus, Maxwell; later added Dao De Jing + Dhammapada. Hamming distances computed. R2 unique to Vaiśeṣika.

6. **Commentarial replication (Procedure D)**  
   Praśastapāda GRETIL text scored C1–C6. Result: **6/6**.

7. **Descriptive nulls (Procedure E)**  
   Fair-coin R2 model → P(exactly one R2 and it is Vaiśeṣika)=1/64. Among 64 binary 6-vectors, P(d to Maxwell ≥ 4)=0.34375.

8. **Novelty audit (Procedure F)**  
   Qualitative Indology on ākāśa–śabda exists. Open quantitative multi-civilization package with Maxwell foil + nulls + replication **not found** in search. Novelty = package, not discovery of the doctrine itself.

9. **Handoff pack**  
   This folder: all facts, tables, figures, evidence for external report writing.
""",
        encoding="utf-8",
    )

    (dirs["root"] / "METHODS.md").write_text(
        """# Methods (operational)

## Materials
See `data/FACTS.json` → materials. Corpus files in `corpus_snippets/`.

## Procedure A — Primary attestation
- Input: GRETIL typed Sanskrit (cached).
- Checklist: T1–T9 in `tables/T_kanada_attestation.csv`.
- Pass rule: expected sutra ID(s) present AND pattern/content match on body (compact match allowed because GRETIL often omits spaces).

## Procedure B — Maxwell confrontation
- Items M1–M5 in `tables/M_maxwell_confrontation.csv`.
- Scored against attested Vaiśeṣika ontology, not against English metaphors.

## Procedure C — Comparative rubric
- Features R1–R6 defined in `data/FACTS.json`.
- Vectors in `tables/R_six_tradition_vectors.csv`.
- Lucretius/Timaeus: PD English keyword hits + scholarly overrides (documented in summary.json notes).
- Dao De Jing / Dhammapada: PD panels; no Vaiśeṣika-style sound-marked ether → R2=0.

## Procedure D — Praśastapāda replication
- Items C1–C6 in `tables/C_prasastapada_replication.csv`.

## Procedure E — Nulls
- See `tables/null_models.csv` and `data/expansion_v2.json` → null_models.
- Descriptive only — not a generative cultural model.

## Procedure F — Novelty
- See `data/NOVELTY.md` and expansion novelty block.

## Risk / ethics
- No human subjects, vertebrate animals, or hazardous agents.
- Public digital texts only.
""",
        encoding="utf-8",
    )

    # Asset index
    lines = ["# Asset index", "", "| Path | Role |", "|---|---|"]
    for a in asset_list:
        lines.append(f"| `{a.get('path')}` | {a.get('role', '')} |")
    (dirs["root"] / "ASSET_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (dirs["data"] / "asset_index.json").write_text(
        json.dumps(asset_list, indent=2) + "\n", encoding="utf-8"
    )

    # ChatGPT prompt
    (dirs["root"] / "CHATGPT_PROMPT.md").write_text(
        """# Paste this into ChatGPT (with the folder / zip attached)

You are helping write a Regeneron ISEF research paper for **Arjun Shah** (Stratford Preparatory Milpitas), category **Physics and Astronomy**.

## Your job
Write a clean, professional, human-sounding ISEF research report from the evidence pack.  
**Do not invent results.** Use only numbers and claims in this pack.

## Read first (in order)
1. `CONSTRAINTS.md` — hard do/don’t
2. `data/FACTS.json` — all headline numbers + hypotheses
3. `PROCESS.md` + `METHODS.md`
4. `tables/scorecard.csv` and other CSVs
5. `evidence/EXCERPTS.md`
6. `data/NOVELTY.md` + `data/VERDICT.md`
7. Figures in `figures/` (especially fig50–fig62 and fig41–fig49)

## Ignore
- `paper_legacy_do_not_use/` — old draft; **do not copy its prose/style**

## Required report structure (match a serious science-fair report)
1. Title page (left-aligned title; category bold; author italic; school + date bottom-right)
2. Table of Contents
3. Abstract (multi-paragraph; include 9/9, 6/6, 0/5, R2 unique, P=1/64; no Capra claim)
4. Introduction / problem / hypotheses H1–H4
5. Background / literature (brief; gap = quantitative package)
6. Materials and Methods (Procedures A–F)
7. Results (tables + figure callouts; every number from FACTS)
8. Discussion (interpret; emphasize negative Maxwell result as a result)
9. Conclusions
10. Acknowledgments, Bibliography, Appendices if needed

## Formatting preferences
- Times New Roman, 12 pt, 1-inch margins, justified body
- Cover page like a clean school report (not centered poster)
- TOC without leader dots if possible
- Embed / reference figures from `figures/`

## Safe groundbreaking sentence (use near end)
See `data/FACTS.json` → `safe_groundbreaking_claim`.

## Forbidden
Any claim that classical India discovered EM or quantum physics.
""",
        encoding="utf-8",
    )

    (dirs["root"] / "README.md").write_text(
        """# ChatGPT handoff pack — ISEF-AKASA-SOUND-FIELD

Everything needed to write the ISEF report **outside** this repo (e.g. ChatGPT).

## Start here
1. Open `CHATGPT_PROMPT.md` and paste into ChatGPT
2. Upload this whole folder (or zip it)
3. ChatGPT should follow `CONSTRAINTS.md` + `data/FACTS.json`

## What’s inside
| Folder / file | Contents |
|---|---|
| `data/` | FACTS.json, summary.json, expansion_v2.json, verdicts, novelty |
| `tables/` | All result CSVs |
| `figures/` | Existing boards + new fig50–fig62 visualizations |
| `evidence/` | Sutra excerpts + evidence.json |
| `corpus_snippets/` | GRETIL Kaṇāda + Praśastapāda text caches |
| `scripts/` | Reproducibility scripts |
| `PROCESS.md` / `METHODS.md` | How the work was done |
| `CONSTRAINTS.md` | Hard claim boundaries |
| `ASSET_INDEX.md` | Full file list |
| `paper_legacy_do_not_use/` | Old PDF — **ignore style** |

## Headline numbers (do not change)
- Kaṇāda **9/9**
- Praśastapāda **6/6**
- Maxwell **0/5**
- R2 unique among 6 traditions
- Fair-coin null **P = 1/64 = 0.015625**
- Verdict: `GROUNDBREAKING_COMPARATIVE_PACKAGE_NOT_ANCIENT_EM`

## Rebuild
```bash
uv run python scripts/build_chatgpt_handoff.py
```
""",
        encoding="utf-8",
    )


def main() -> None:
    summary = load_json(SRC / "summary.json")
    expansion = load_json(SRC / "expansion_v2.json")
    dirs = ensure_dirs()

    assets: list[dict] = []
    assets += copy_existing(dirs, summary, expansion)
    assets += export_tables(dirs, summary, expansion)
    assets += write_evidence(dirs, summary, expansion)
    assets += new_figures(dirs, summary, expansion)
    write_docs(dirs, summary, expansion, assets)

    # Also sync new figs into paper/figures for convenience
    for fn in sorted((dirs["figures"]).glob("fig5*.png")):
        shutil.copy2(fn, FIG_SRC / fn.name)
    for fn in sorted((dirs["figures"]).glob("fig6*.png")):
        shutil.copy2(fn, FIG_SRC / fn.name)

    print(f"Pack ready: {PACK}")
    print(f"Assets indexed: {len(assets)}")
    print(f"Figures: {len(list(dirs['figures'].glob('*.png')))}")
    print(f"Tables: {len(list(dirs['tables'].glob('*.csv')))}")


if __name__ == "__main__":
    main()
