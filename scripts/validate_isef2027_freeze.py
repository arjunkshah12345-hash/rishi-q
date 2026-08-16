#!/usr/bin/env python3
"""Validate ISEF2027 freeze integrity (hashes + lock + decisions)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    errors: list[str] = []
    manifest = ROOT / "protocol/osf/FREEZE_MANIFEST.sha256"
    if not manifest.exists():
        errors.append("missing protocol/osf/FREEZE_MANIFEST.sha256")
    else:
        for line in manifest.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            digest, rel = line.split(maxsplit=1)
            path = ROOT / rel
            if not path.exists():
                errors.append(f"missing {rel}")
                continue
            got = sha256(path)
            if got != digest:
                errors.append(f"HASH MISMATCH {rel}\n  expected {digest}\n  got      {got}")

    decisions = (ROOT / "artifacts/isef2027/STUDENT_DECISIONS.yaml").read_text()
    if "status: FROZEN" not in decisions and "status:FROZEN" not in decisions:
        # allow first-line version status
        if "\nstatus: FROZEN\n" not in decisions and not decisions.startswith("status: FROZEN"):
            # check YAML status field near top
            if "status: FROZEN" not in decisions:
                errors.append("STUDENT_DECISIONS.yaml not marked FROZEN")

    lock = json.loads((ROOT / "corpus/confirmatory_sealed/lock.json").read_text())
    if lock.get("status") != "LOCKED" or lock.get("allow_open_sealed") is not False:
        errors.append("confirmatory_sealed lock not LOCKED")

    idx = json.loads((ROOT / "ontology/concept_graph/index.json").read_text())
    if idx.get("status") != "FROZEN":
        errors.append("concept_graph index not FROZEN")

    prereg = (ROOT / "protocol/isef2027_prereg_TEMPLATE.yaml").read_text()
    if "prereg-isef2027-v1" not in prereg:
        errors.append("prereg missing GitHub release tag reference")

    if errors:
        print("FREEZE VALIDATION FAILED")
        for e in errors:
            print("-", e)
        return 1

    print("FREEZE VALIDATION PASS")
    print(f"  manifest entries: {sum(1 for _ in manifest.read_text().splitlines() if _.strip())}")
    print(f"  sealed ids: {len(lock.get('confirmatory_sealed_ids', []))}")
    print(f"  graphs: {len(idx.get('graphs', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
