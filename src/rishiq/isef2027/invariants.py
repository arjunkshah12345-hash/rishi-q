"""Sealed-split and confirmatory-lock invariants (never score sealed data)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_split_manifest(root: Path) -> dict[str, Any]:
    return json.loads((root / "artifacts/isef2027/split_manifest.json").read_text(encoding="utf-8"))


def load_sealed_lock(root: Path) -> dict[str, Any]:
    return json.loads((root / "corpus/confirmatory_sealed/lock.json").read_text(encoding="utf-8"))


def assert_sealed_lock_invariants(root: Path) -> list[str]:
    """Return list of issues (empty = pass). Does not read sealed text payloads for scoring."""
    issues: list[str] = []
    man = load_split_manifest(root)
    lock = load_sealed_lock(root)
    sealed = set(man.get("confirmatory_sealed_ids", []))
    dev = set(man.get("development_ids", []))
    cal = set(man.get("calibration_ids", []))

    if sealed & dev:
        issues.append(f"sealed∩development={sorted(sealed & dev)}")
    if sealed & cal:
        issues.append(f"sealed∩calibration={sorted(sealed & cal)}")
    if lock.get("status") != "LOCKED":
        issues.append(f"lock.status={lock.get('status')}")
    if lock.get("allow_open_sealed") is not False:
        issues.append("allow_open_sealed must be false")

    # No confirmatory score artifacts
    results = root / "results"
    if results.exists():
        for p in results.rglob("*"):
            if not p.is_file():
                continue
            if "confirmatory" not in str(p).lower():
                continue
            if p.suffix.lower() not in {".json", ".csv", ".parquet", ".jsonl"}:
                continue
            name = p.name.lower()
            if name in {"readme.md", "lock.json"} or name.endswith(".md"):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for needle in ("delta_q", "qs_score", "ontology_top1", "confirmatory_p_value"):
                if needle in text.lower() and "locked" not in text.lower():
                    issues.append(f"possible confirmatory score artifact: {p.relative_to(root)}")
                    break

    # Sealed dir must not contain analyzed score sidecars
    sealed_dir = root / "corpus/confirmatory_sealed"
    if sealed_dir.exists():
        for p in sealed_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".parquet", ".csv"} and "score" in p.name.lower():
                issues.append(f"sealed score file forbidden: {p.relative_to(root)}")

    return issues
