"""Theory fingerprints and loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class TheoryFingerprint(BaseModel):
    theory_id: str
    name: str
    version: str = "0.1.0"
    classical: bool = False
    quantum: bool = False
    notes: str = ""
    features: dict[str, int] = Field(default_factory=dict)
    weights: dict[str, float] = Field(default_factory=dict)

    def active_features(self) -> list[str]:
        return [k for k, v in self.features.items() if v]


def load_fingerprint(path: str | Path) -> TheoryFingerprint:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return TheoryFingerprint.model_validate(data)


def load_fingerprint_index(dir_path: str | Path) -> dict[str, Any]:
    path = Path(dir_path) / "index.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_all_fingerprints(dir_path: str | Path) -> dict[str, TheoryFingerprint]:
    dir_path = Path(dir_path)
    index = load_fingerprint_index(dir_path)
    out: dict[str, TheoryFingerprint] = {}
    for tid in index["theories"]:
        out[tid] = load_fingerprint(dir_path / f"{tid}.yaml")
    return out
