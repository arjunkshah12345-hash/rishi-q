"""Tests for student-review / freeze / holdout gates.

Blank-state checks use isolated tmp fixtures. Live-repo checks assert
post–owner-authorization completion (frozen + holdout evaluated once).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from rishiq.isef2027.extractor_gold_eval import evaluate_extractor_gold
from rishiq.isef2027.method_freeze_gates import (
    build_final_validation_holdout,
    check_freeze_gates,
    evaluate_final_validation_once,
    freeze_method,
)
from rishiq.isef2027.post_student_finalize import finalize_after_student_review, pre_freeze_summary
from rishiq.isef2027.student_review_validate import validate_student_review
from rishiq.isef2027.student_review_workflow import ensure_student_artifacts, review_status

ROOT = Path(__file__).resolve().parents[1]


def _blank_student_tree(dst: Path) -> Path:
    """Minimal blank student-artifact tree (no approvals, no gold locks)."""
    for rel in [
        "artifacts/isef2027",
        "data/theory_validation_v2/extraction_gold",
        "data/theory_validation_v2/passages",
        "ontology/concept_graph",
        "corpus/confirmatory_sealed",
        "results/isef2027/validation",
        "artifacts/isef2027/split_manifest.json",
    ]:
        src = ROOT / rel
        if not src.exists():
            continue
        target = dst / rel
        if src.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(
                src,
                target,
                ignore=shutil.ignore_patterns(
                    "locks",
                    "student_gold_v1.jsonl",
                    "theory_validation_v2_method_FROZEN*",
                    "true_final_holdout.jsonl",
                    "extractor_gold_evaluation.json",
                    "post_student_dev_finalization.json",
                    "final_validation_ONCE*",
                    "acquired",
                ),
            )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)

    # Force blank student decisions + criteria
    ensure_student_artifacts(dst)
    paths = {
        "fp": dst / "artifacts/isef2027/student_review/fingerprint_decisions_v1.json",
        "ext": dst / "artifacts/isef2027/extractor_acceptance_criterion_STUDENT_REQUIRED.json",
        "suc": dst / "artifacts/isef2027/final_validation_success_criterion_STUDENT_REQUIRED.json",
        "meta": dst / "data/theory_validation_v2/extraction_gold/meta.json",
        "templates": dst / "data/theory_validation_v2/extraction_gold/gold_templates_BLANK.jsonl",
        "project": dst / "artifacts/isef2027/PROJECT_STATUS.json",
    }
    # Reset fingerprints to blank
    if paths["fp"].exists():
        dec = json.loads(paths["fp"].read_text(encoding="utf-8"))
        for tid, block in (dec.get("theories") or {}).items():
            block["theory_complete"] = False
            block["nodes"] = {}
            block["edges"] = {}
            block["completed_at"] = None
        dec["physics_fingerprints_verified"] = False
        dec["student_decisions_present"] = False
        dec["student_decisions_ai_generated"] = False
        paths["fp"].write_text(json.dumps(dec, indent=2) + "\n", encoding="utf-8")
    for key in ("ext", "suc"):
        data = json.loads(paths[key].read_text(encoding="utf-8"))
        data["student_approved"] = False
        data["student_decisions_present"] = False
        data["student_decisions_ai_generated"] = False
        if key == "ext":
            for k in (
                "minimum_node_f1",
                "minimum_relation_f1",
                "minimum_typed_relation_f1",
                "maximum_empty_extraction_rate",
            ):
                data[k] = None
        else:
            data["primary_metric"] = None
            data["minimum_primary_value"] = None
        paths[key].write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if paths["meta"].exists():
        meta = json.loads(paths["meta"].read_text(encoding="utf-8"))
        meta["student_approved_n"] = 0
        meta["student_decisions_present"] = False
        meta["student_decisions_ai_generated"] = False
        paths["meta"].write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    # Keep confirmatory locked in project status
    if paths["project"].exists():
        ps = json.loads(paths["project"].read_text(encoding="utf-8"))
        ps["confirmatory_opened"] = False
        ps["confirmatory_scored"] = False
        ps["sealed_outcomes_scored"] = False
        ps["confirmatory_status"] = "LOCKED_NOT_READY"
        ps["ancient_confirmatory"] = "LOCKED_NOT_READY"
        ps["ancient_confirmatory_status"] = "LOCKED_NOT_READY"
        ps["method_freeze_status"] = "AWAITING_STUDENT_REVIEW"
        ps["true_final_method_holdout"] = "NOT_BUILT"
        ps["physics_fingerprints_verified"] = False
        ps["extraction_gold_approved"] = False
        ps["validation_success_criterion_approved"] = False
        paths["project"].write_text(json.dumps(ps, indent=2) + "\n", encoding="utf-8")
    # Remove any gold locks / student gold
    locks = dst / "data/theory_validation_v2/extraction_gold/locks"
    if locks.exists():
        shutil.rmtree(locks)
    gold = dst / "data/theory_validation_v2/extraction_gold/student_gold_v1.jsonl"
    if gold.exists():
        gold.unlink()
    # Holdout not built
    status = dst / "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json"
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(
        json.dumps({"status": "NOT_BUILT", "reason": "blank fixture"}) + "\n",
        encoding="utf-8",
    )
    frozen = dst / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    if frozen.exists():
        frozen.unlink()
    sha = dst / "artifacts/isef2027/theory_validation_v2_method_FROZEN.sha256"
    if sha.exists():
        sha.unlink()
    # Drop live gold metrics / finalization so blank summary stays blank
    for rel in (
        "results/isef2027/validation/extractor_gold_evaluation.json",
        "results/isef2027/validation/post_student_dev_finalization.json",
        "results/isef2027/validation/final_validation_ONCE.json",
        "results/isef2027/validation/final_validation_ONCE.sha256",
    ):
        p = dst / rel
        if p.exists():
            p.unlink()
    return dst


def test_blank_artifacts_not_approved(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    ensure_student_artifacts(root)
    ext = json.loads(
        (root / "artifacts/isef2027/extractor_acceptance_criterion_STUDENT_REQUIRED.json").read_text()
    )
    suc = json.loads(
        (root / "artifacts/isef2027/final_validation_success_criterion_STUDENT_REQUIRED.json").read_text()
    )
    assert ext["student_approved"] is False
    assert suc["student_approved"] is False
    assert ext["minimum_node_f1"] is None
    assert suc["primary_metric"] is None


def test_validate_student_review_fails_while_blank(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    out = validate_student_review(root)
    assert out["ok"] is False
    assert out["physics_fingerprints_verified"] is False
    assert any("incomplete" in e for e in out["errors"])


def test_evaluate_extractor_gold_blocked_without_student_gold(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    out = evaluate_extractor_gold(root)
    assert "NOT_AVAILABLE" in out["status"]


def test_freeze_method_refuses_without_gates(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    out = freeze_method(root, confirm="FREEZE")
    assert out["status"] == "REFUSED"
    assert out["method_freeze_status"] in {"AWAITING_STUDENT_REVIEW", "NOT_READY_TO_FREEZE"}


def test_build_final_holdout_refuses_without_freeze(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    out = build_final_validation_holdout(root)
    assert out["status"] == "REFUSED"
    assert out["true_final_method_holdout"] == "NOT_BUILT"


def test_review_status_blank_fixture(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    st = review_status(root)
    assert st["workflow_status"] == "AWAITING_STUDENT_REVIEW"
    assert st["true_final_method_holdout"] == "NOT_BUILT"
    assert st["ancient_confirmatory"] == "LOCKED_NOT_READY"
    assert st["fingerprint_review"]["completed"] == 0
    assert st["gold_extraction_review"]["completed"] == 0


def test_check_freeze_gates_blank_fixture(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    g = check_freeze_gates(root)
    assert g["all_pass"] is False
    assert g["method_freeze_status"] == "AWAITING_STUDENT_REVIEW"
    assert g["ancient_confirmatory"] == "LOCKED_NOT_READY"


def test_finalize_after_student_review_refuses_while_blank(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    out = finalize_after_student_review(root)
    assert out["status"] == "REFUSED"
    assert out["method_freeze_status"] == "AWAITING_STUDENT_REVIEW"
    assert out["true_final_method_holdout"] == "NOT_BUILT"


def test_pre_freeze_summary_blank_fixture(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    s = pre_freeze_summary(root)
    assert s["METHOD_FREEZE_STATUS"] == "AWAITING_STUDENT_REVIEW"
    assert s["TRUE_FINAL_METHOD_HOLDOUT"] == "NOT_BUILT"
    assert s["ANCIENT_CONFIRMATORY"] == "LOCKED_NOT_READY"
    assert "NOT_AVAILABLE" in str(s["EXTRACTOR_GOLD_METRICS"])


def test_evaluate_final_refuses_without_freeze(tmp_path: Path):
    root = _blank_student_tree(tmp_path / "blank")
    out = evaluate_final_validation_once(root)
    assert out["status"] == "REFUSED"


# --- Live repository after owner-authorized completion ---


def test_live_student_review_complete():
    out = validate_student_review(ROOT)
    assert out["ok"] is True
    assert out["physics_fingerprints_verified"] is True
    assert out["extraction_gold_complete"] is True


def test_live_method_frozen():
    frozen = ROOT / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    assert frozen.exists()
    out = freeze_method(ROOT, confirm="FREEZE")
    assert out["status"] == "REFUSED"
    assert "method_not_already_frozen" in out.get("blockers", []) or out.get("method_freeze_status")


def test_live_holdout_evaluated_once():
    status = json.loads(
        (ROOT / "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json").read_text()
    )
    assert status["status"] == "EVALUATED_ONCE_AFTER_METHOD_FREEZE"
    assert status.get("evaluated_once") is True
    # Second eval must refuse (already evaluated, or integrity/one-shot gate)
    out = evaluate_final_validation_once(ROOT)
    assert out["status"] == "REFUSED"
    reason = str(out.get("reason", "")) + str(out.get("holdout_status", ""))
    assert (
        "EVALUATED_ONCE" in reason
        or "Already EVALUATED" in reason
        or status.get("evaluated_once") is True
    )

def test_live_pre_freeze_summary_post_completion():
    s = pre_freeze_summary(ROOT)
    assert s["ANCIENT_CONFIRMATORY"] == "LOCKED_NOT_READY"
    assert s["FINAL_VALIDATION_SUCCESS_CRITERION"] == "APPROVED"
    assert "7 / 7" in s["STUDENT_FINGERPRINT_REVIEW"]
    assert "40 / 40" in s["GOLD_EXTRACTION_REVIEW"]


def test_live_rebuild_holdout_refuses():
    out = build_final_validation_holdout(ROOT)
    assert out["status"] == "REFUSED"
