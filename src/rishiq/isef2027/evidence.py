"""Evidence-class tags — keep synthetic/demo out of scientific result tables."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class EvidenceClass(str, Enum):
    SOFTWARE_DEMO = "SOFTWARE_DEMO"
    DEVELOPMENT_ANALYSIS = "DEVELOPMENT_ANALYSIS"
    HELD_OUT_METHOD_VALIDATION = "HELD_OUT_METHOD_VALIDATION"
    CONFIRMATORY = "CONFIRMATORY"
    METADATA_ONLY = "METADATA_ONLY"


FORBIDDEN_SYNTHETIC_TARGETS = {
    EvidenceClass.CONFIRMATORY,
    EvidenceClass.HELD_OUT_METHOD_VALIDATION,
}


class ProvenanceEnvelope(BaseModel):
    evidence_class: EvidenceClass
    synthetic: bool = False
    real_text: bool = True
    blinded: bool = False
    phase: str = "development"  # exploratory | calibration | validation | confirmatory
    source_split: str = "development"
    method_version: str = "unknown"
    student_reviewed_inputs: bool = False
    notes: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _no_synthetic_scientific(self) -> ProvenanceEnvelope:
        if self.synthetic and self.evidence_class in FORBIDDEN_SYNTHETIC_TARGETS:
            raise ValueError(
                f"synthetic=True cannot be tagged {self.evidence_class.value}"
            )
        if self.evidence_class == EvidenceClass.CONFIRMATORY and self.phase != "confirmatory":
            raise ValueError("CONFIRMATORY evidence_class requires phase=confirmatory")
        return self


def attach_provenance(payload: dict[str, Any], prov: ProvenanceEnvelope) -> dict[str, Any]:
    out = dict(payload)
    out["evidence_class"] = prov.evidence_class.value
    out["provenance"] = prov.model_dump(mode="json")
    return out
