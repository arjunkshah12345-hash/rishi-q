"""Tests for structural graph similarity + held-out theory validation."""

from __future__ import annotations

from pathlib import Path

from rishiq.isef2027.concept_graph import ConceptGraph, EdgeKind, GraphEdge, GraphNode, NodeKind
from rishiq.isef2027.graph_similarity import structural_similarity_bundle, typed_relation_similarity
from rishiq.isef2027.theory_validation import build_theory_validation_corpus, run_held_out_theory_validation

ROOT = Path(__file__).resolve().parents[1]


def _iso_cause_graphs():
    """Same relational pattern, different literal IDs/labels."""
    a = ConceptGraph(
        graph_id="a",
        domain="theory_fingerprint",
        nodes=[
            GraphNode(id="charge", kind=NodeKind.entity, label="charge"),
            GraphNode(id="em", kind=NodeKind.field_medium, label="em field"),
        ],
        edges=[GraphEdge(source="charge", target="em", kind=EdgeKind.CAUSES)],
    )
    b = ConceptGraph(
        graph_id="b",
        domain="theory_fingerprint",
        nodes=[
            GraphNode(id="mass", kind=NodeKind.entity, label="mass"),
            GraphNode(id="grav", kind=NodeKind.field_medium, label="gravity effect"),
        ],
        edges=[GraphEdge(source="mass", target="grav", kind=EdgeKind.CAUSES)],
    )
    return a, b


def test_typed_relation_matches_isomorphic_different_labels():
    a, b = _iso_cause_graphs()
    # Literal ID overlap baseline should be ~0; typed relation should be high
    bund = structural_similarity_bundle(a, b)
    assert bund["literal_id_overlap_baseline"] < 0.2
    assert typed_relation_similarity(a, b) == 1.0
    assert bund["primary_structural"] > 0.5


def test_held_out_theory_validation_runs():
    build_theory_validation_corpus(ROOT)
    out = run_held_out_theory_validation(ROOT)
    held = out["held_out"]
    assert held["evidence_class"] == "HELD_OUT_METHOD_VALIDATION"
    assert held["n_test"] >= 5
    assert 0.0 <= held["top1_accuracy"] <= 1.0
    assert held["provenance"]["synthetic"] is False
    demo = out["keyword_proxy_demo"]
    assert demo["evidence_class"] == "SOFTWARE_DEMO"
