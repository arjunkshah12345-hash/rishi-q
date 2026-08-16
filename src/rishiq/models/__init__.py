"""Pydantic data models for passages, annotations, and experiments."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class DatasetSplit(str, Enum):
    DEVELOPMENT = "development"
    VALIDATION = "validation"
    CONFIRMATORY = "confirmatory"
    SYNTHETIC = "synthetic"
    PHYSICS_CONTROL = "physics_control"


class AnnotationLabel(str, Enum):
    YES = "1"
    NO = "0"
    NA = "NA"
    AMBIGUOUS = "U"


class Passage(BaseModel):
    """Strict passage schema (protocol §22 / Phase 8)."""

    passage_id: str
    tradition: str
    school: str = ""
    work: str
    section: str = ""
    verse_reference: str = ""
    estimated_date_min: int | None = None
    estimated_date_max: int | None = None
    source_language: str
    source_text: str = ""
    translation: str
    translation_id: str = ""
    translator: str = ""
    translation_year: int | None = None
    translation_style: str = Field(
        default="unspecified",
        description="literal|older_scholarly|recent_scholarly|machine|synthetic|physics_reference",
    )
    edition: str = ""
    source_identifier: str = ""
    source_url: str = ""
    license_status: str = Field(
        default="unknown",
        description="public_domain|open_license|bibliographic_pointer_only|synthetic|unknown",
    )
    genre: str = ""
    topic: str = ""
    word_count: int = 0
    token_count: int = 0
    dataset_split: DatasetSplit = DatasetSplit.DEVELOPMENT
    source_hash: str = ""
    role: str = Field(
        default="unspecified",
        description="target|control|negative_control|physics_reference|synthetic",
    )
    notes: str = ""

    @model_validator(mode="after")
    def _fill_counts_and_require_text(self) -> Passage:
        text = (self.translation or self.source_text or "").strip()
        if not text:
            raise ValueError("passage must have translation or source_text")
        if self.word_count <= 0:
            self.word_count = len(text.split())
        if self.token_count <= 0:
            self.token_count = self.word_count
        return self


class BlindedPassage(BaseModel):
    anonymous_id: str
    text: str
    source_language: str = "en"
    word_count: int = 0
    prompt_safe: bool = True


class Proposition(BaseModel):
    proposition_id: str
    passage_id: str
    text: str
    evidence_span: str
    model_name: str
    prompt_version: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    notes: str = ""


class FeatureAnnotation(BaseModel):
    passage_id: str
    feature_id: str
    label: AnnotationLabel
    evidence: str = ""
    reason: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    annotator: str
    model_version: str
    prompt_version: str = ""
    verified: bool = False
    verification_flags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _require_evidence_for_positive(self) -> FeatureAnnotation:
        if self.label == AnnotationLabel.YES and not self.evidence.strip():
            raise ValueError(
                f"positive annotation for {self.feature_id} requires evidence span"
            )
        return self


class FeatureVector(BaseModel):
    """Numeric encoding: 1, 0, or None (NA/U)."""

    passage_id: str
    values: dict[str, float | None]
    labels: dict[str, AnnotationLabel]
    ontology_version: str


class TheoryScore(BaseModel):
    passage_id: str
    theory_id: str
    score: float
    metric: str
    ontology_version: str
    fingerprint_version: str


class ExperimentManifest(BaseModel):
    experiment_id: str
    git_commit: str = "unknown"
    dataset_hash: str
    ontology_version: str
    prompt_version: str
    model_name: str
    model_revision: str = "unspecified"
    random_seed: int = 42
    package_versions: dict[str, str] = Field(default_factory=dict)
    timestamp: str
    config_hash: str = ""
    fingerprint_hash: str = ""
    notes: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)


LabelLiteral = Literal["1", "0", "NA", "U"]


def label_to_numeric(label: AnnotationLabel | str) -> float | None:
    value = label.value if isinstance(label, AnnotationLabel) else str(label)
    if value == "1":
        return 1.0
    if value == "0":
        return 0.0
    return None
