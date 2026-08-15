#!/usr/bin/env python3
"""Export strongest correspondence / contradiction examples for the paper.

Uses exploratory physics/synthetic runs only. Never fabricates Sanskrit 'discoveries'.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    scores = pd.read_parquet(
        root / "results/exploratory/synthetic_e2e/passage_scores.parquet"
    )
    ann = pd.read_parquet(
        root / "results/exploratory/synthetic_e2e/annotations.parquet"
    )
    # Strongest QS among physics references
    phys = scores[scores["role"] == "physics_reference"].sort_values("QS", ascending=False)
    strongest = phys.head(3)
    weakest_qs = scores.sort_values("QS").head(3)

    # Contradictions: unity metaphor with Q06 explicitly non-yes
    q06 = ann[ann["feature_id"] == "Q06"][["passage_id", "label", "evidence", "reason"]]
    unity = scores[scores["passage_id"] == "SYN_UNITY_001"]

    examples = {
        "warning": "EXPLORATORY_INSTRUMENT_EXAMPLES_ONLY",
        "strongest_qs_physics": strongest[
            ["passage_id", "work", "QS", "QEF", "quantum_mechanics", "classical_em"]
        ].to_dict(orient="records"),
        "lowest_qs_overall": weakest_qs[
            ["passage_id", "tradition", "role", "QS", "QEF"]
        ].to_dict(orient="records"),
        "unity_metaphor_control": {
            "passage_scores": unity[["passage_id", "QS", "QEF"]].to_dict(orient="records"),
            "Q06_annotation": q06[q06["passage_id"] == "SYN_UNITY_001"].to_dict(
                orient="records"
            ),
            "lesson": "Generic unity must not count as nonseparability.",
        },
        "entanglement_control": {
            "passage_scores": scores[scores["passage_id"] == "PHYS_ENTANGLE_001"][
                ["passage_id", "QS", "QEF", "quantum_mechanics"]
            ].to_dict(orient="records"),
            "Q06_annotation": q06[q06["passage_id"] == "PHYS_ENTANGLE_001"].to_dict(
                orient="records"
            ),
            "lesson": "Explicit non-factorizable joint state supports Q06.",
        },
    }
    out = root / "paper/assets/worked_examples.json"
    out.write_text(json.dumps(examples, indent=2), encoding="utf-8")

    # Markdown for paper drafting
    md = ["# Worked examples (exploratory instrument checks)\n\n"]
    md.append("> Not Sanskrit confirmatory results.\n\n")
    md.append("## Strongest QS (physics references)\n\n")
    for r in examples["strongest_qs_physics"]:
        md.append(
            f"- `{r['passage_id']}` — QS={r['QS']:.3f}, QEF={r['QEF']:.3f}, "
            f"QM={r['quantum_mechanics']:.3f}\n"
        )
    md.append("\n## Unity metaphor (must fail Q06)\n\n")
    md.append(json.dumps(examples["unity_metaphor_control"], indent=2))
    md.append("\n\n## Entanglement control (should support Q06)\n\n")
    md.append(json.dumps(examples["entanglement_control"], indent=2))
    md.append("\n")
    (root / "paper/assets/worked_examples.md").write_text("".join(md), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
