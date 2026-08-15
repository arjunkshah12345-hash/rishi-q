#!/usr/bin/env python3
"""Export blinded annotation tasks for external human reviewers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from rishiq.human_validation import STATUS, export_blinded_tasks, write_reviewer_instructions


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ann = root / "results/exploratory/synthetic_e2e/annotations.parquet"
    if not ann.exists():
        raise SystemExit(f"missing {ann}; run: rishiq annotate --config configs/development.yaml")
    df = pd.read_parquet(ann)
    out = root / "human_validation/exports/tasks_seed42.csv"
    export_blinded_tasks(df, out, sample_n=30, seed=42)
    write_reviewer_instructions(root / "human_validation/instructions/reviewer_instructions.md")
    tmpl = root / "human_validation/templates/annotation_template.csv"
    tmpl.write_text(
        "passage_id,feature_id,label,human_label,human_evidence,reviewer_id,notes\n",
        encoding="utf-8",
    )
    print(STATUS)
    print("wrote", out)


if __name__ == "__main__":
    main()
