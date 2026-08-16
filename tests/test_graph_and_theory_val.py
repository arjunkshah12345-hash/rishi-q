"""Tests for Pass 3: graph size penalty, pedagogy downgrade, source-group splits."""

from __future__ import annotations

from pathlib import Path

import pytest

from rishiq.isef2027.concept_graph import ConceptGraph, EdgeKind, GraphEdge, GraphNode, NodeKind
from rishiq.isef2027.contamination import ContaminationState, EvidenceRole
from rishiq.isef2027.final_holdout_guard import assert_final_holdout_access_allowed
from rishiq.isef2027.graph_robustness import run_graph_transformation_benchmark
from rishiq.isef2027.graph_similarity import hungarian_role_alignment_similarity, structural_similarity_bundle, typed_relation_similarity
from rishiq.isef2027.theory_validation import build_theory_validation_corpus, run_held_out_theory_validation
from rishiq.isef2027.theory_validation_v2_corpus import assert_no_work_overlap, build_external_theory_corpus

ROOT = Path(__file__).resolve().parents[1]


def _iso_cause_graphs():
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
    bund = structural_similarity_bundle(a, b)
    assert bund["literal_id_overlap_baseline"] < 0.2
    assert typed_relation_similarity(a, b) == 1.0
    assert bund["primary_structural"] > 0.5


def test_hungarian_identical_approx_one():
    a, _ = _iso_cause_graphs()
    b = a.model_copy(deep=True)
    assert hungarian_role_alignment_similarity(a, b) > 0.95


def test_hungarian_size_mismatch_penalized():
    small = ConceptGraph(
        graph_id="small",
        domain="theory_fingerprint",
        nodes=[
            GraphNode(id="a", kind=NodeKind.entity, label="a"),
            GraphNode(id="b", kind=NodeKind.field_medium, label="b"),
        ],
        edges=[GraphEdge(source="a", target="b", kind=EdgeKind.CAUSES)],
    )
    bloated = small.model_copy(deep=True)
    for i in range(18):
        bloated.nodes.append(GraphNode(id=f"j{i}", kind=NodeKind.entity, label=f"j{i}"))
    sim = hungarian_role_alignment_similarity(small, bloated)
    assert sim < 0.25, f"size mismatch must lower similarity, got {sim}"


def test_hungarian_empty_vs_nonempty():
    empty = ConceptGraph(graph_id="e", domain="theory_fingerprint")
    a, _ = _iso_cause_graphs()
    assert hungarian_role_alignment_similarity(empty, a) == 0.0


def test_hungarian_unrelated_same_size_low():
    a, _ = _iso_cause_graphs()
    u = ConceptGraph(
        graph_id="u",
        domain="theory_fingerprint",
        nodes=[
            GraphNode(id="t1", kind=NodeKind.time, label="t1"),
            GraphNode(id="t2", kind=NodeKind.measurement, label="t2"),
        ],
        edges=[GraphEdge(source="t1", target="t2", kind=EdgeKind.DISTINCT_FROM)],
    )
    assert hungarian_role_alignment_similarity(a, u) < 0.5


def test_duplicate_nodes_do_not_inflate_above_identical():
    a, _ = _iso_cause_graphs()
    identical = hungarian_role_alignment_similarity(a, a.model_copy(deep=True))
    dup = a.model_copy(deep=True)
    for n in list(a.nodes):
        dup.nodes.append(GraphNode(id=f"{n.id}_d", kind=n.kind, label=n.label))
    sim = hungarian_role_alignment_similarity(a, dup)
    assert sim <= identical + 1e-9
    assert sim < 0.9


def test_pedagogy_benchmark_downgraded():
    build_theory_validation_corpus(ROOT)
    out = run_held_out_theory_validation(ROOT)
    held = out["held_out"]
    assert held["evidence_class"] == "DEVELOPMENT_ANALYSIS"
    assert held["evidence_role"] == EvidenceRole.CURATED_PEDAGOGY_DEVELOPMENT_BENCHMARK.value
    assert held["contamination_state"] == ContaminationState.DEVELOPMENT_CONTAMINATED.value
    assert held["provenance"]["real_text"] is False
    assert held["n_test"] >= 5
    assert 0.0 <= held["top1_accuracy"] <= 1.0
    demo = out["keyword_proxy_demo"]
    assert demo["evidence_class"] == "SOFTWARE_DEMO"


def test_graph_transform_benchmark_runs():
    out = run_graph_transformation_benchmark(ROOT)
    assert out["results"]["identical"]["hungarian_role_alignment"] > 0.95
    assert out["results"]["size_mismatch_2_vs_20"]["hungarian_role_alignment"] < 0.3
    assert out["results"]["size_mismatch_2_vs_20"]["typed_relation_coverage_adjusted"] < 0.25
    assert out["results"]["empty_vs_nonempty"]["hungarian_role_alignment"] == 0.0


def test_typed_coverage_adjusted_penalizes_isolated_bloat():
    from rishiq.isef2027.graph_similarity import typed_relation_similarity_coverage_adjusted

    small = ConceptGraph(
        graph_id="small",
        domain="theory_fingerprint",
        nodes=[
            GraphNode(id="a", kind=NodeKind.entity, label="a"),
            GraphNode(id="b", kind=NodeKind.field_medium, label="b"),
        ],
        edges=[GraphEdge(source="a", target="b", kind=EdgeKind.CAUSES)],
    )
    bloated = small.model_copy(deep=True)
    for i in range(18):
        bloated.nodes.append(GraphNode(id=f"j{i}", kind=NodeKind.entity, label=f"j{i}"))
    raw = typed_relation_similarity(small, bloated)
    adj = typed_relation_similarity_coverage_adjusted(small, bloated)
    assert raw == 1.0
    assert adj < 0.2


def test_external_corpus_source_family_no_overlap():
    from rishiq.isef2027.source_families import assert_no_family_overlap
    import json

    meta = build_external_theory_corpus(ROOT)
    assert meta["n_passages"] > 50
    assert meta["work_overlap_issues"] == []
    assert meta["source_family_overlap_train_dev"] == []
    assert meta["true_final_method_holdout"] == "NOT_BUILT"
    works = {s: set(meta["splits"][s]["works"]) for s in ("train", "development")}
    assert not (works["train"] & works["development"])
    lock = json.loads((ROOT / "data/theory_validation_v2/final_holdout/lock_manifest.json").read_text())
    assert lock["status"] == "CONSTRUCTED_UNEVALUATED_VALIDATION_SET"
    # family fields present on rows
    train = [
        json.loads(l)
        for l in (ROOT / "data/theory_validation_v2/passages/train.jsonl").read_text().splitlines()
        if l.strip()
    ]
    assert train and "source_family" in train[0]
    issues = assert_no_family_overlap(train + [
        json.loads(l)
        for l in (ROOT / "data/theory_validation_v2/passages/development.jsonl").read_text().splitlines()
        if l.strip()
    ], "source_family")
    assert not any(x.startswith("HARD_") for x in issues)


def test_structural_extractor_theory_agnostic_api():
    from rishiq.isef2027.structural_extractor import extract_structure

    text = "A particle interacts with a field and energy propagates through the medium."
    # Must not require theory label
    out = extract_structure(text)
    assert out.extractor_version
    assert len(out.nodes) >= 2
    g = out.to_concept_graph()
    assert len(g.nodes) >= 2


def test_final_holdout_guard_blocks_without_token():
    with pytest.raises(PermissionError):
        assert_final_holdout_access_allowed(ROOT, None)
    with pytest.raises(PermissionError):
        assert_final_holdout_access_allowed(ROOT, "wrong")


def test_assert_no_work_overlap_detects_leak():
    rows = [
        {"split": "train", "work_id": "A"},
        {"split": "development", "work_id": "A"},
    ]
    issues = assert_no_work_overlap(rows)
    assert issues
