"""Contamination / holdout states for theory-validation datasets."""

from __future__ import annotations

from enum import Enum


class ContaminationState(str, Enum):
    UNSEEN = "UNSEEN"
    EVALUATED_ONCE_FROZEN_METHOD = "EVALUATED_ONCE_FROZEN_METHOD"
    DEVELOPMENT_CONTAMINATED = "DEVELOPMENT_CONTAMINATED"
    RETIRED = "RETIRED"


class EvidenceRole(str, Enum):
    """How a corpus may be cited scientifically."""

    CURATED_PEDAGOGY_DEVELOPMENT_BENCHMARK = "CURATED_PEDAGOGY_DEVELOPMENT_BENCHMARK"
    EXTERNAL_METHOD_DEVELOPMENT = "EXTERNAL_METHOD_DEVELOPMENT"
    FINAL_METHOD_HOLDOUT = "FINAL_METHOD_HOLDOUT"
    GRAPH_ALGORITHM_SYNTHETIC = "GRAPH_ALGORITHM_SYNTHETIC"
