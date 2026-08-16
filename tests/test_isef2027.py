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


def test_split_skeleton_empty_sealed():
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


from rishiq.isef2027.benchmark import POSITIVE_PANELS, run_theory_identification_benchmark
from rishiq.isef2027.blind_audit import detect_extended_leaks
from rishiq.isef2027.discovery_replication import run_discovery_replication_demo
from rishiq.isef2027.translation_battery import translator_year_stratified_demo


def test_method_benchmark_runs():
    summary = run_theory_identification_benchmark(ROOT, seed=0)
    assert summary["n_panels"] >= 4
    assert 0.0 <= summary["ontology_top1_accuracy"] <= 1.0


def test_translation_demo_corr_finite():
    d = translator_year_stratified_demo(seed=0)
    assert d["corr_year_vs_modernization_lexicon"] == d["corr_year_vs_modernization_lexicon"]


def test_discovery_replication_structure():
    d = run_discovery_replication_demo(seed=0)
    assert "enrichment_replication" in d
    assert "survives_replication_demo_threshold" in d


def test_scrub_removes_tradition_names():
    from rishiq.isef2027.scrub import scrub_text

    r = scrub_text("Vaiśeṣika in India cites Maxwell and the Veda.")
    assert "Maxwell" not in r.text or "[SCRUBBED]" in r.text
    assert r.n_replacements >= 1


def test_graph_templates_build():
    from rishiq.isef2027.graph_templates import build_all_theory_graph_templates

    paths = build_all_theory_graph_templates(ROOT)
    assert any("template_fp_classical_em" in str(p) for p in paths)


def test_freeze_validator_passes():
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_isef2027_freeze.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PASS" in r.stdout
