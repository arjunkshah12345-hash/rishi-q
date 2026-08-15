#!/usr/bin/env python3
"""Import human labels and report agreement (fails soft if empty)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from rishiq.human_validation import STATUS, disagreement_report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", type=Path, required=True)
    args = ap.parse_args()
    if not args.path.exists():
        raise SystemExit(f"missing import file: {args.path}")
    df = pd.read_csv(args.path)
    report = disagreement_report(df)
    out = Path("results/exploratory/human_agreement.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(pd.Series(report).to_json(), encoding="utf-8")
    print(report)
    if report.get("status") == STATUS or report.get("n_labeled", 0) == 0:
        print("Still", STATUS)


if __name__ == "__main__":
    main()
