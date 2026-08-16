"""Tests for student-review gates — never auto-approve."""

from __future__ import annotations

import json
from pathlib import Path

from rishiq.isef2027.extractor_gold_eval import evaluate_extractor_gold
from rishiq.isef2027.method_freeze_gates import (
    build_final_validation_holdout,
    check_freeze_gates,
    freeze_method,
)
from rishiq.isef2027.student_review_validate import validate_student_review
from rishiq.isef2027.student_review_workflow import ensure_student_artifacts, review_status

ROOT = Path(__file__).resolve().parents[1]


def test_ensure_student_artifacts_not_approved():
    ensure_student_artifacts(ROOT)
    paths = ROOT / "artifacts/isef2027"
    ext = json.loads((paths / "extractor_acceptance_criterion_STUDENT_REQUIRED.json").read_text())
    suc = json.loads((paths / "final_validation_success_criterion_STUDENT_REQUIRED.json").read_text())
    assert ext["student_approved"] is False
    assert suc["student_approved"] is False
    assert ext["minimum_node_f1"] is None
    assert suc["primary_metric"] is None


def test_validate_student_review_fails_while_blank():
    ensure_student_artifacts(ROOT)
    out = validate_student_review(ROOT)
    assert out["ok"] is False
    assert out["physics_fingerprints_verified"] is False
    assert any("incomplete" in e for e in out["errors"])


def test_evaluate_extractor_gold_blocked_without_student_gold():
    out = evaluate_extractor_gold(ROOT)
    assert "NOT_AVAILABLE" in out["status"]


def test_freeze_method_refuses_without_gates():
    out = freeze_method(ROOT, confirm="FREEZE")
    assert out["status"] == "REFUSED"
    assert out["method_freeze_status"] in {"AWAITING_STUDENT_REVIEW", "NOT_READY_TO_FREEZE"}


def test_build_final_holdout_refuses_without_freeze():
    out = build_final_validation_holdout(ROOT)
    assert out["status"] == "REFUSED"
    assert out["true_final_method_holdout"] == "NOT_BUILT"


def test_review_status_awaiting_student():
    st = review_status(ROOT)
    assert st["workflow_status"] == "AWAITING_STUDENT_REVIEW"
    assert st["true_final_method_holdout"] == "NOT_BUILT"
    assert st["ancient_confirmatory"] == "LOCKED_NOT_READY"
    assert st["fingerprint_review"]["completed"] == 0
    assert st["gold_extraction_review"]["completed"] == 0


def test_check_freeze_gates_not_ready():
    g = check_freeze_gates(ROOT)
    assert g["all_pass"] is False
    assert g["method_freeze_status"] == "AWAITING_STUDENT_REVIEW"
    assert g["ancient_confirmatory"] == "LOCKED_NOT_READY"
    assert g["gates"]["development_selection_finished"] is False
    assert g["gates"]["power_updated"] is False


def test_finalize_after_student_review_refuses_while_blank():
    from rishiq.isef2027.post_student_finalize import finalize_after_student_review

    out = finalize_after_student_review(ROOT)
    assert out["status"] == "REFUSED"
    assert out["method_freeze_status"] == "AWAITING_STUDENT_REVIEW"
    assert out["true_final_method_holdout"] == "NOT_BUILT"


def test_pre_freeze_summary_awaiting():
    from rishiq.isef2027.post_student_finalize import pre_freeze_summary

    s = pre_freeze_summary(ROOT)
    assert s["METHOD_FREEZE_STATUS"] == "AWAITING_STUDENT_REVIEW"
    assert s["TRUE_FINAL_METHOD_HOLDOUT"] == "NOT_BUILT"
    assert s["ANCIENT_CONFIRMATORY"] == "LOCKED_NOT_READY"
    assert "NOT_AVAILABLE" in str(s["EXTRACTOR_GOLD_METRICS"])


def test_evaluate_final_refuses_without_freeze():
    from rishiq.isef2027.method_freeze_gates import evaluate_final_validation_once

    out = evaluate_final_validation_once(ROOT)
    assert out["status"] == "REFUSED"
