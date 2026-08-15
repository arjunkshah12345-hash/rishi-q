#!/usr/bin/env python3
"""Run power simulations; write exploratory recommendations (not confirmatory n)."""

from __future__ import annotations

import json
from pathlib import Path

from rishiq.statistics import recommend_sample_sizes


def main() -> None:
    rows = recommend_sample_sizes()
    out = Path("results/exploratory/power_recommendations.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", out)
    print("NOTE: confirmatory n must be frozen at preregistration from development estimates.")


if __name__ == "__main__":
    main()
