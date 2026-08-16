"""Method freeze gates and post-freeze holdout ops (refuse until student freeze)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rishiq.isef2027.method_freeze_candidate import write_method_freeze_candidate
from rishiq.isef2027.student_review_validate import validate_student_review
from rishiq.isef2027.student_review_workflow import review_paths, review_status


def _git_sha(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "UNKNOWN"


def _sha_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_freeze_gates(root: Path) -> dict[str, Any]:
    """All gates for READY_FOR_STUDENT_METHOD_FREEZE / freeze-method."""
    paths = review_paths(root)
    st = review_status(root)
    val = validate_student_review(root)
    ext_c = json.loads(paths["extractor_criterion"].read_text(encoding="utf-8"))
    suc_c = json.loads(paths["success_criterion"].read_text(encoding="utf-8"))

    corpus_meta = {}
    meta_path = root / "data/theory_validation_v2/passages/corpus_meta.json"
    if meta_path.exists():
        corpus_meta = json.loads(meta_path.read_text(encoding="utf-8"))

    gold_eval_path = root / "results/isef2027/validation/extractor_gold_evaluation.json"
    gold_eval = json.loads(gold_eval_path.read_text(encoding="utf-8")) if gold_eval_path.exists() else {}

    frozen_path = root / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    holdout_true = root / "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json"
    true_holdout = "NOT_BUILT"
    if holdout_true.exists():
        true_holdout = json.loads(holdout_true.read_text(encoding="utf-8")).get("status", "NOT_BUILT")

    # Extractor passes criterion only if criterion approved AND metrics available AND meet thresholds
    extractor_passes = False
    extractor_pass_detail = "criterion_not_approved_or_metrics_missing"
    if ext_c.get("student_approved") is True and gold_eval.get("status") == "EVALUATED_VS_STUDENT_GOLD":
        fails = []
        for key, metric_path in [
            ("minimum_node_f1", ("node", "f1")),
            ("minimum_relation_f1", ("relation", "f1")),
            ("minimum_typed_relation_f1", ("typed_relation", "f1")),
        ]:
            thr = ext_c.get(key)
            if thr is None:
                fails.append(f"{key}=null")
                continue
            cur = gold_eval
            for p in metric_path:
                cur = cur.get(p, {}) if isinstance(cur, dict) else None
            if not isinstance(cur, (int, float)) or float(cur) < float(thr):
                fails.append(f"{key}: got {cur} < {thr}")
        max_empty = ext_c.get("maximum_empty_extraction_rate")
        empty = (gold_eval.get("coverage") or {}).get("empty_extraction_rate")
        if max_empty is None:
            fails.append("maximum_empty_extraction_rate=null")
        elif empty is None or float(empty) > float(max_empty):
            fails.append(f"empty_rate {empty} > {max_empty}")
        extractor_passes = len(fails) == 0
        extractor_pass_detail = "pass" if extractor_passes else "; ".join(fails)

    gates = {
        "student_review_validation_ok": val.get("ok") is True,
        "physics_fingerprints_verified": val.get("physics_fingerprints_verified") is True,
        "gold_review_complete": val.get("extraction_gold_complete") is True,
        "extractor_acceptance_criterion_approved": ext_c.get("student_approved") is True,
        "extractor_passes_criterion": extractor_passes,
        "validation_success_criterion_approved": suc_c.get("student_approved") is True,
        "source_family_leakage_zero": corpus_meta.get("source_family_overlap_train_dev") == [],
        "true_final_holdout_not_built": true_holdout == "NOT_BUILT",
        "ancient_confirmatory_locked": True,  # enforced by firewall; never auto-unlock
        "method_not_already_frozen": not frozen_path.exists(),
    }
    all_pass = all(gates.values())
    blockers = [k for k, v in gates.items() if not v]

    if all_pass:
        freeze_status = "READY_FOR_STUDENT_METHOD_FREEZE"
    elif st["fingerprint_review"]["completed"] < 7 or st["gold_extraction_review"]["completed"] < st["gold_extraction_review"]["total"]:
        freeze_status = "AWAITING_STUDENT_REVIEW"
    else:
        freeze_status = "NOT_READY_TO_FREEZE"

    return {
        "gates": gates,
        "all_pass": all_pass,
        "blockers": blockers,
        "method_freeze_status": freeze_status,
        "extractor_pass_detail": extractor_pass_detail,
        "true_final_method_holdout": true_holdout,
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "validation": val,
    }


def write_freeze_candidate_if_ready(root: Path) -> dict[str, Any]:
    gate = check_freeze_gates(root)
    ready = gate["method_freeze_status"] == "READY_FOR_STUDENT_METHOD_FREEZE"
    blockers = gate["blockers"] if not ready else []
    if gate["method_freeze_status"] == "AWAITING_STUDENT_REVIEW":
        blockers = blockers or ["student_review_incomplete"]
    cand = write_method_freeze_candidate(root, ready=ready, blockers=blockers)
    # Force status string from gates (never auto-approve)
    cand["status"] = gate["method_freeze_status"]
    if gate["method_freeze_status"] != "READY_FOR_STUDENT_METHOD_FREEZE":
        cand["ready_for_student_method_freeze"] = False
    out = root / "artifacts/isef2027/theory_validation_v2_method_freeze_CANDIDATE.json"
    out.write_text(json.dumps(cand, indent=2) + "\n", encoding="utf-8")
    gate["candidate"] = cand
    return gate


def freeze_method(root: Path, *, confirm: str | None = None) -> dict[str, Any]:
    gate = check_freeze_gates(root)
    if not gate["all_pass"]:
        return {
            "status": "REFUSED",
            "method_freeze_status": gate["method_freeze_status"],
            "blockers": gate["blockers"],
            "detail": gate,
        }
    summary = {
        "action": "freeze-method",
        "git_sha": _git_sha(root),
        "gates": gate["gates"],
        "warning": "After freeze, true final holdout may be built once; do not retune from that holdout.",
    }
    print(json.dumps(summary, indent=2))
    if confirm != "FREEZE":
        return {
            "status": "CONFIRMATION_REQUIRED",
            "instruction": "Re-run with --confirm FREEZE after reviewing the summary.",
            "summary": summary,
        }

    paths = review_paths(root)
    frozen = {
        "artifact": "theory_validation_v2_method_FROZEN",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(root),
        "extractor_version": "structural_extractor_deterministic_v1",
        "fingerprint_decisions_sha256": _sha_file(paths["fingerprint_decisions"]),
        "student_gold_sha256": _sha_file(paths["student_gold"]),
        "extractor_criterion_sha256": _sha_file(paths["extractor_criterion"]),
        "success_criterion_sha256": _sha_file(paths["success_criterion"]),
        "corpus_meta_sha256": _sha_file(root / "data/theory_validation_v2/passages/corpus_meta.json"),
        "point_of_no_return_for_final_validation": True,
        "true_final_method_holdout": "NOT_BUILT",
        "ancient_confirmatory": "LOCKED_NOT_READY",
    }
    out = root / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    out.write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
    return {"status": "FROZEN", "path": str(out.relative_to(root)), "frozen": frozen}


def build_final_validation_holdout(root: Path) -> dict[str, Any]:
    frozen = root / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    if not frozen.exists():
        return {
            "status": "REFUSED",
            "true_final_method_holdout": "NOT_BUILT",
            "reason": "Method must be FROZEN first via rishiq-isef freeze-method",
        }
    return {
        "status": "NOT_IMPLEMENTED_IN_THIS_PASS",
        "true_final_method_holdout": "NOT_BUILT",
        "note": (
            "Separate operation after freeze. Candidate eligibility lives under "
            "data/theory_validation_v2/final_holdout_candidates/. Do not score."
        ),
    }


def evaluate_final_validation_once(root: Path) -> dict[str, Any]:
    frozen = root / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    if not frozen.exists():
        return {
            "status": "REFUSED",
            "reason": "Method not frozen",
            "true_final_method_holdout": "NOT_BUILT",
        }
    status_path = root / "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json"
    hold = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else {}
    if hold.get("status") != "BUILT_UNEVALUATED":
        return {
            "status": "REFUSED",
            "reason": "Holdout must be BUILT_UNEVALUATED first",
            "holdout_status": hold.get("status", "NOT_BUILT"),
        }
    if hold.get("evaluated_once"):
        return {"status": "REFUSED", "reason": "Already EVALUATED_ONCE_AFTER_METHOD_FREEZE"}
    print("THIS RESULT MAY NOT BE USED TO RETUNE THE CURRENT FROZEN METHOD.")
    return {
        "status": "NOT_IMPLEMENTED_IN_THIS_PASS",
        "note": "One-shot evaluator wires after holdout is built post-freeze.",
    }
