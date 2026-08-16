"""Ontology loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class OntologyFeature(BaseModel):
    id: str
    name: str
    family: str
    level: str
    definition: str
    positive_requirements: list[str] = Field(default_factory=list)
    negative_conditions: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    ambiguity_rules: str = ""
    positive_examples: list[str] = Field(default_factory=list)
    negative_examples: list[str] = Field(default_factory=list)
    physics_relevance: str = ""
    quantum_specific: bool = False
    field_like: bool = False
    version: str = "0.1.0"

    @field_validator("level")
    @classmethod
    def _level_ok(cls, v: str) -> str:
        if v not in {"I", "II", "III"}:
            raise ValueError(f"level must be I/II/III, got {v}")
        return v


class Ontology(BaseModel):
    ontology_id: str
    version: str
    status: str = "PROPOSED"
    description: str = ""
    annotation_values: dict[str, str] = Field(default_factory=dict)
    hard_rules: list[str] = Field(default_factory=list)
    families: list[str] = Field(default_factory=list)
    features: list[OntologyFeature]

    def feature_ids(self) -> list[str]:
        return [f.id for f in self.features]

    def quantum_feature_ids(self) -> list[str]:
        return [f.id for f in self.features if f.quantum_specific]

    def field_feature_ids(self) -> list[str]:
        return [f.id for f in self.features if f.field_like]

    def by_id(self) -> dict[str, OntologyFeature]:
        return {f.id: f for f in self.features}


def load_ontology(path: str | Path) -> Ontology:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    ont = Ontology.model_validate(data)
    ids = ont.feature_ids()
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate feature ids in ontology")
    if len(ids) < 30:
        raise ValueError(f"ontology too small: {len(ids)} features")
    return ont


def validate_ontology_file(path: str | Path) -> dict[str, Any]:
    ont = load_ontology(path)
    return {
        "ok": True,
        "version": ont.version,
        "n_features": len(ont.features),
        "n_quantum_specific": len(ont.quantum_feature_ids()),
        "n_field_like": len(ont.field_feature_ids()),
        "families": ont.families,
    }
