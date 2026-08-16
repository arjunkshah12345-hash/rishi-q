"""Tests for sealed-lock / split / evidence-class invariants."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope
from rishiq.isef2027.invariants import assert_sealed_lock_invariants, load_split_manifest
from rishiq.isef2027.splits import assert_no_split_overlap, build_skeleton_manifest

ROOT = Path(__file__).resolve().parents[1]


def test_skeleton_dev_empty_sealed_by_design():
    """Skeleton builder still starts sealed empty; live manifest may reserve IDs."""
    man = build_skeleton_manifest(ROOT)
    assert assert_no_split_overlap(man) == []
    assert man.confirmatory_sealed_ids == []


def test_live_manifest_sealed_may_exist_without_overlap():
    man = load_split_manifest(ROOT)
    sealed = set(man["confirmatory_sealed_ids"])
    assert sealed  # reserved candidates exist
    assert not (sealed & set(man["development_ids"]))
    assert not (sealed & set(man["calibration_ids"]))
    assert man["leakage_check"]["status"] == "PASS"


def test_sealed_lock_invariants_pass():
    issues = assert_sealed_lock_invariants(ROOT)
    assert issues == [], issues


def test_no_confirmatory_run_summary():
    assert not (ROOT / "results/confirmatory/run_summary.json").exists()


def test_synthetic_cannot_be_held_out_or_confirmatory():
    with pytest.raises(ValueError):
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.HELD_OUT_METHOD_VALIDATION,
            synthetic=True,
        )
    with pytest.raises(ValueError):
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.CONFIRMATORY,
            synthetic=True,
            phase="confirmatory",
        )


def test_project_status_json_consistent():
    path = ROOT / "artifacts/isef2027/PROJECT_STATUS.json"
    assert path.exists()
    st = json.loads(path.read_text(encoding="utf-8"))
    assert st["confirmatory_opened"] is False
    assert st["confirmatory_scored"] is False
    assert st["osf_registered"] is False
    assert st["v1_superseded_for_future_confirmatory_analysis"] is True
    assert "V2" in st["v2_status"]
