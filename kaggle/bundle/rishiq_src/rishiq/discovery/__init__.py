"""Concept-graph schemas for RISHI-Q discovery (System B)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


NODE_TYPES = [
    "substrate",
    "matter",
    "constituent",
    "whole",
    "observer",
    "state",
    "property",
    "space",
    "time",
    "cause",
    "effect",
    "manifestation",
    "motion",
    "disturbance",
    "potential_state",
    "measurement",
]

EDGE_TYPES = [
    "composed_of",
    "manifests_as",
    "causes",
    "transforms_into",
    "depends_on",
    "pervades",
    "contains",
    "emerges_from",
    "interacts_with",
    "observes",
    "changes",
    "correlates_with",
    "is_state_of",
    "propagates_through",
    "cannot_be_reduced_to",
]


class GraphNode(BaseModel):
    node_id: str
    node_type: str
    label: str = ""
    evidence_span: str = ""
    feature_ids: list[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    edge_id: str
    edge_type: str
    source: str
    target: str
    evidence_span: str = ""
    feature_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.5


class PassageGraph(BaseModel):
    passage_id: str
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    ontology_version: str = ""
    extractor: str = "feature_map_v0.1"
    notes: str = ""

    def motif_signature(self) -> frozenset[str]:
        """Physics-label-free structural signature for mining."""
        parts = {f"N:{n.node_type}" for n in self.nodes}
        parts |= {f"E:{e.edge_type}" for e in self.edges}
        return frozenset(parts)


class RishiMotif(BaseModel):
    motif_id: str
    signature: list[str]
    support: int
    passages: list[str] = Field(default_factory=list)
    traditions: dict[str, int] = Field(default_factory=dict)
    works: dict[str, int] = Field(default_factory=dict)
    # filled only AFTER discovery, in a separate mapping step
    nearest_physics: str | None = None
    physics_family: Literal[
        "unrelated", "classical", "field_like", "quantum_specific", "unknown"
    ] = "unknown"


class DiscoveryCandidate(BaseModel):
    candidate_id: str
    title: str
    discovery_type: str
    motif_id: str | None = None
    supporting_sources: list[str] = Field(default_factory=list)
    n_independent_works: int = 0
    estimated_historical_period: str = "unknown"
    effect_size: float | None = None
    confidence_interval: list[float] | None = None
    control_comparison: str = ""
    translation_robustness: str = "untested"
    model_robustness: str = "untested"
    human_validation_status: str = "REQUIRES_EXTERNAL_HUMAN_VALIDATION"
    nearest_physics_analogue: str = ""
    classical_vs_quantum_specificity: str = ""
    prior_literature_status: str = "NOVELTY_REVIEW_REQUIRED"
    alternative_explanations: list[str] = Field(default_factory=list)
    novelty_confidence: float = 0.0
    scientific_importance: float = 0.0
    status: Literal[
        "RAW_CANDIDATE",
        "ARTIFACT_SUSPECTED",
        "KNOWN_IN_LITERATURE",
        "PARTIALLY_KNOWN",
        "APPARENTLY_NOVEL",
        "NOVELTY_REVIEW_REQUIRED",
        "STRONG_DISCOVERY_CANDIDATE",
        "REJECTED",
    ] = "RAW_CANDIDATE"
    so_what: dict[str, float] = Field(default_factory=dict)
    notes: str = ""


__all__ = [
    "NODE_TYPES",
    "EDGE_TYPES",
    "GraphNode",
    "GraphEdge",
    "PassageGraph",
    "RishiMotif",
    "DiscoveryCandidate",
]
