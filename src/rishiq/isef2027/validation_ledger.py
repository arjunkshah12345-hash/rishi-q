"""Append-only validation ledger — prevents invisible iterative test tuning."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _git_sha(root: Path) -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=str(root), stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except Exception:
        return "UNKNOWN"


def append_validation_ledger(
    root: Path,
    entry: dict[str, Any],
) -> Path:
    path = root / "results/isef2027/validation/VALIDATION_LEDGER.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(root),
        **entry,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, default=float) + "\n")
    return path
