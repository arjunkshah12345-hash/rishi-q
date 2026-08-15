#!/usr/bin/env python3
"""Development corpus acquisition scaffold.

Does NOT download copyrighted translations into the public tree.
Records provenance plans and can append public-domain / synthetic passages.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    manifest = ROOT / "corpus/manifests/sources.csv"
    rows = list(csv.DictReader(manifest.open(encoding="utf-8")))
    print(f"sources in manifest: {len(rows)}")
    available = [r for r in rows if r["availability_status"] in {"available", "candidate_pd"}]
    pointers = [r for r in rows if r["availability_status"] == "pointer"]
    pending = [r for r in rows if r["availability_status"] == "pending_acquisition"]
    print("available/candidate_pd:", len(available))
    print("bibliographic pointers only:", len(pointers))
    print("pending acquisition:", len(pending))
    print(
        "Next: acquire PD texts with provenance scripts; keep copyrighted works as pointers.\n"
        "Sampling rules must be reproducible before confirmatory collection."
    )
    # Ensure synthetic corpus exists
    from rishiq.ingest.synthetic import build_synthetic_corpus

    out = build_synthetic_corpus(ROOT / "corpus/development/synthetic_passages.parquet")
    print("synthetic corpus:", out)


if __name__ == "__main__":
    main()
