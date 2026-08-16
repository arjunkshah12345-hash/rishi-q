#!/usr/bin/env python3
"""Acquire public-domain confirmatory candidates into corpus/raw/pd/ (no scoring).

Usage:
  uv run python scripts/acquire_sealed_pd.py --dry-run
  uv run python scripts/acquire_sealed_pd.py --url URL --out NAME.txt --seal-id ID

Does NOT run ontology scoring. Updates lock hashes only when --commit-hash is set.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
PD = ROOT / "corpus" / "raw" / "pd"
LOCK = ROOT / "corpus" / "confirmatory_sealed" / "lock.json"

# Known candidate endpoints (may 403/401 depending on mirror policy).
CANDIDATES = [
    {
        "seal_id": "seal-control-toacquire-aristotle-physics",
        "note": "English Aristotle Physics PD — try Archive.org / Gutenberg manually if mirrors block bots",
        "urls": [],
    },
    {
        "seal_id": "seal-control-toacquire-epicurus-letters",
        "note": "Epicurus Letter to Herodotus / Principal Doctrines PD",
        "urls": [],
    },
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--url")
    ap.add_argument("--out", help="filename under corpus/raw/pd/")
    ap.add_argument("--seal-id")
    ap.add_argument("--commit-hash", action="store_true")
    args = ap.parse_args()

    if args.dry_run or not args.url:
        print("Sealed acquisition helper — no automatic scoring.")
        for c in CANDIDATES:
            print(f"- {c['seal_id']}: {c['note']}")
        print("\nExample:")
        print("  uv run python scripts/acquire_sealed_pd.py \\")
        print("    --url https://example.org/physics.txt --out aristotle_physics_pd.txt \\")
        print("    --seal-id seal-control-toacquire-aristotle-physics --commit-hash")
        return

    PD.mkdir(parents=True, exist_ok=True)
    out = PD / (args.out or "acquired.txt")
    r = httpx.get(args.url, follow_redirects=True, timeout=60.0)
    r.raise_for_status()
    out.write_bytes(r.content)
    digest = hashlib.sha256(r.content).hexdigest()
    print(f"wrote {out} sha256={digest} bytes={len(r.content)}")

    if args.commit_hash and args.seal_id:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        lock.setdefault("hashes_on_disk", {})[args.seal_id] = digest
        LOCK.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
        print(f"updated lock hash for {args.seal_id}")
        print("Remember: still LOCKED — do not score until unlock.")


if __name__ == "__main__":
    main()
