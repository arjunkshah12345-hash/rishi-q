"""Tests for ISEF2027 technical package (no confirmatory unlock)."""

from __future__ import annotations

from pathlib import Path

from rishiq.isef2027.adversarial import mask_vocabulary
from rishiq.isef2027.baselines import binary_vector_jaccard, ranking_accuracy
from rishiq.isef2027.concept_graph import ConceptGraph, NodeKind, EdgeKind, graph_overlap_score
from rishiq.isef2027.freeze import freeze_dev
from rishiq.isef2027.human_val import cohens_kappa
from rishiq.isef2027.inventory import build_inventory
from rishiq.isef2027.registry import ExperimentRecord, register_experiment
from rishiq.isef2027.splits import SplitManifest, assert_no_split_overlap, build_skeleton_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_inventory_flags_flagship():
    inv = build_inventory(ROOT)
    assert inv["implemented_modules"]["isef_flagship_exploratory"] is True
    assert inv["confirmatory_status"] == "LOCKED"


def test_freeze_writes_manifest(tmp_path, monkeypatch):
    # freeze against real root
    path = freeze_dev(ROOT)
    assert path.exists()
    data = path.read_text()
    assert "ISEF2027-DEV-FREEZE" in data
    assert "sha256" in data


def test_split_no_overlap():
    man = build_skeleton_manifest(ROOT)
    assert assert_no_split_overlap(man) == []
    assert man.confirmatory_sealed_ids == []


def test_concept_graph_overlap():
    a = ConceptGraph(
        graph_id="a",
        domain="historical_text",
        nodes=[
            {"id": "m", "kind": NodeKind.field_medium, "label": "medium"},
            {"id": "s", "kind": NodeKind.observable, "label": "sound"},
        ],
        edges=[{"source": "s", "target": "m", "kind": EdgeKind.PROPAGATES_THROUGH}],
    )
    b = ConceptGraph(
        graph_id="b",
        domain="theory_fingerprint",
        nodes=[
            {"id": "m", "kind": NodeKind.field_medium, "label": "medium"},
            {"id": "l", "kind": NodeKind.observable, "label": "light"},
        ],
        edges=[{"source": "l", "target": "m", "kind": EdgeKind.PROPAGATES_THROUGH}],
    )
    score = graph_overlap_score(a, b)
    assert 0.0 <= score <= 1.0


def test_mask_and_jaccard():
    assert "[MASK]" in mask_vocabulary("quantum field energy")
    assert binary_vector_jaccard({"a": 1, "b": 0}, {"a": 1, "b": 1}) == 0.5


def test_ranking_accuracy():
    r = ranking_accuracy({"classical_em": 0.9, "quantum_field_theory": 0.1}, "classical_em")
    assert r["top1_correct"] is True


def test_kappa_demo():
    k = cohens_kappa(["1", "0", "1"], ["1", "0", "0"])
    assert k == k  # not NaN


def test_registry_append_only(tmp_path):
    root = tmp_path
    (root / "results/isef2027/registry").mkdir(parents=True)
    rec = ExperimentRecord(
        experiment_id="TEST-EXP-1",
        hypothesis="h",
        config_hash="abc",
        dataset_hash="def",
        code_commit="x",
        random_seed=1,
        timestamp="2026-01-01T00:00:00Z",
        phase="exploratory",
    )
    register_experiment(root, rec)
    try:
        register_experiment(root, rec)
        assert False, "should refuse duplicate"
    except ValueError:
        pass
