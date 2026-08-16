"""Append-only experiment registry with evidence-class enforcement."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from rishiq.isef2027.evidence import EvidenceClass, FORBIDDEN_SYNTHETIC_TARGETS


class ExperimentRecord(BaseModel):
    experiment_id: str
    hypothesis: str
    config_hash: str
    dataset_hash: str
    code_commit: str
    random_seed: int
    timestamp: str
    output_paths: list[str] = Field(default_factory=list)
    phase: str  # exploratory | calibration | validation | confirmatory
    blinded: bool = False
    config_frozen_beforehand: bool = False
    notes: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)
    # v2 provenance fields
    evidence_class: EvidenceClass = EvidenceClass.DEVELOPMENT_ANALYSIS
    synthetic: bool = False
    method_version: str = "unspecified"
    source_split: str = "development"
    student_reviewed_inputs: bool = False

    @model_validator(mode="after")
    def _validate_evidence(self) -> ExperimentRecord:
        if self.synthetic and self.evidence_class in FORBIDDEN_SYNTHETIC_TARGETS:
            raise ValueError(
                f"Refuse registry row: synthetic=True with {self.evidence_class.value}"
            )
        if self.phase == "confirmatory" and self.evidence_class != EvidenceClass.CONFIRMATORY:
            raise ValueError("phase=confirmatory requires evidence_class=CONFIRMATORY")
        if self.evidence_class == EvidenceClass.CONFIRMATORY and self.synthetic:
            raise ValueError("CONFIRMATORY cannot be synthetic")
        return self


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
    if path.exists():
        existing = {
            json.loads(line)["experiment_id"]
            for line in path.read_text().splitlines()
            if line.strip()
        }
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
    evidence_class: EvidenceClass | str = EvidenceClass.DEVELOPMENT_ANALYSIS,
    synthetic: bool = False,
    method_version: str = "unspecified",
    source_split: str = "development",
    student_reviewed_inputs: bool = False,
    extra: dict[str, Any] | None = None,
) -> ExperimentRecord:
    cfg_hash = hash_file(config_path) if config_path else "NA"
    ec = EvidenceClass(evidence_class) if isinstance(evidence_class, str) else evidence_class
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
        evidence_class=ec,
        synthetic=synthetic,
        method_version=method_version,
        source_split=source_split,
        student_reviewed_inputs=student_reviewed_inputs,
        extra=extra or {},
    )
