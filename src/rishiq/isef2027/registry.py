"""Append-only experiment registry (never silently overwrite)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class ExperimentRecord(BaseModel):
    experiment_id: str
    hypothesis: str
    config_hash: str
    dataset_hash: str
    code_commit: str
    random_seed: int
    timestamp: str
    output_paths: list[str] = Field(default_factory=list)
    phase: str  # exploratory | calibration | confirmatory
    blinded: bool = False
    config_frozen_beforehand: bool = False
    notes: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)


def git_commit(root: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "UNKNOWN"


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    return hash_bytes(path.read_bytes()) if path.exists() else "MISSING"


def registry_path(root: Path) -> Path:
    return root / "results/isef2027/registry/experiments.jsonl"


def register_experiment(root: Path, record: ExperimentRecord) -> Path:
    path = registry_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite: append only; refuse duplicate experiment_id
    if path.exists():
        existing = {json.loads(line)["experiment_id"] for line in path.read_text().splitlines() if line.strip()}
        if record.experiment_id in existing:
            raise ValueError(f"experiment_id already registered (append-only): {record.experiment_id}")
    with path.open("a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")
    return path


def new_record(
    root: Path,
    *,
    experiment_id: str,
    hypothesis: str,
    config_path: Path | None,
    dataset_hash: str,
    seed: int,
    phase: str,
    output_paths: list[str],
    blinded: bool = False,
    config_frozen_beforehand: bool = False,
    notes: str = "",
) -> ExperimentRecord:
    cfg_hash = hash_file(config_path) if config_path else "NA"
    return ExperimentRecord(
        experiment_id=experiment_id,
        hypothesis=hypothesis,
        config_hash=cfg_hash,
        dataset_hash=dataset_hash,
        code_commit=git_commit(root),
        random_seed=seed,
        timestamp=datetime.now(timezone.utc).isoformat(),
        output_paths=output_paths,
        phase=phase,
        blinded=blinded,
        config_frozen_beforehand=config_frozen_beforehand,
        notes=notes,
    )
