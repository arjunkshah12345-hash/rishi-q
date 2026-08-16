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


def _post_student_finalization(root: Path) -> dict[str, Any]:
    path = root / "results/isef2027/validation/post_student_dev_finalization.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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

    post = _post_student_finalization(root)
    power_path = root / "results/isef2027/validation/power_sensitivity_table.json"
    power = json.loads(power_path.read_text(encoding="utf-8")) if power_path.exists() else {}
    sel_path = root / "results/isef2027/validation/external_dev_method_selection.json"
    sel = json.loads(sel_path.read_text(encoding="utf-8")) if sel_path.exists() else {}

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

    development_selection_finished = (
        post.get("post_student_review") is True
        and sel.get("post_student_review") is True
        and (sel.get("graph_weight_selection") or {}).get("selected") is not None
    )
    power_updated = (
        post.get("post_student_review") is True
        and int(power.get("n_sim_per_cell") or 0) >= 2000
        and power.get("post_student_review") is True
    )

    gates = {
        "student_review_validation_ok": val.get("ok") is True,
        "physics_fingerprints_verified": val.get("physics_fingerprints_verified") is True,
        "gold_review_complete": val.get("extraction_gold_complete") is True,
        "extractor_acceptance_criterion_approved": ext_c.get("student_approved") is True,
        "extractor_passes_criterion": extractor_passes,
        "validation_success_criterion_approved": suc_c.get("student_approved") is True,
        "source_family_leakage_zero": corpus_meta.get("source_family_overlap_train_dev") == [],
        "development_selection_finished": development_selection_finished,
        "power_updated": power_updated,
        "true_final_holdout_not_built": true_holdout == "NOT_BUILT",
        "ancient_confirmatory_locked": True,
        "method_not_already_frozen": not frozen_path.exists(),
    }
    all_pass = all(gates.values())
    blockers = [k for k, v in gates.items() if not v]

    if all_pass:
        freeze_status = "READY_FOR_STUDENT_METHOD_FREEZE"
    elif (
        st["fingerprint_review"]["completed"] < 7
        or st["gold_extraction_review"]["completed"] < st["gold_extraction_review"]["total"]
    ):
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
    post = _post_student_finalization(root)
    sel_path = root / "results/isef2027/validation/external_dev_method_selection.json"
    sel = json.loads(sel_path.read_text(encoding="utf-8")) if sel_path.exists() else {}
    weights = (sel.get("graph_weight_selection") or {}).get("selected")
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
        "post_student_finalization_sha256": _sha_file(
            root / "results/isef2027/validation/post_student_dev_finalization.json"
        ),
        "graph_weights": weights,
        "point_of_no_return_for_final_validation": True,
        "true_final_method_holdout": "NOT_BUILT",
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "post_student_marker": post,
    }
    out = root / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    out.write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
    sha = _sha_file(out)
    if sha:
        (out.with_suffix(".sha256")).write_text(sha + "\n", encoding="utf-8")
    return {"status": "FROZEN", "path": str(out.relative_to(root)), "frozen": frozen}


def build_final_validation_holdout(root: Path) -> dict[str, Any]:
    """Post-freeze only. Materialize holdout from acquired candidates. Does not score."""
    frozen = root / "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"
    if not frozen.exists():
        return {
            "status": "REFUSED",
            "true_final_method_holdout": "NOT_BUILT",
            "reason": "Method must be FROZEN first via rishiq-isef freeze-method",
        }

    status_path = root / "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json"
    if status_path.exists():
        cur = json.loads(status_path.read_text(encoding="utf-8"))
        if cur.get("status") in {"BUILT_UNEVALUATED", "EVALUATED_ONCE_AFTER_METHOD_FREEZE"}:
            return {
                "status": "REFUSED",
                "reason": "Holdout already built; do not rebuild",
                "true_final_method_holdout": cur.get("status"),
            }

    acquired_dir = root / "data/theory_validation_v2/final_holdout_candidates/acquired"
    passages_path = acquired_dir / "passages.jsonl"
    if not passages_path.exists():
        return {
            "status": "REFUSED",
            "true_final_method_holdout": "NOT_BUILT",
            "reason": (
                "No acquired holdout passages at "
                "data/theory_validation_v2/final_holdout_candidates/acquired/passages.jsonl. "
                "Acquire legally eligible sources after freeze, then re-run."
            ),
            "eligibility": "data/theory_validation_v2/final_holdout_candidates/candidate_availability.json",
        }

    rows = [json.loads(l) for l in passages_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not rows:
        return {
            "status": "REFUSED",
            "true_final_method_holdout": "NOT_BUILT",
            "reason": "Acquired passages.jsonl is empty",
        }

    meta_path = root / "data/theory_validation_v2/passages/corpus_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    train_dev_sf = set(meta.get("train_source_families") or []) | set(meta.get("dev_source_families") or [])
    split_sf: set[str] = set()
    for split in ("train", "development"):
        p = root / f"data/theory_validation_v2/passages/{split}.jsonl"
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                split_sf.add(r.get("source_family") or r.get("work_id"))
    blocked = train_dev_sf | split_sf
    hold_sf = {r.get("source_family") or r.get("work_id") for r in rows}
    overlap = sorted(x for x in hold_sf if x in blocked)
    if overlap:
        return {
            "status": "REFUSED",
            "true_final_method_holdout": "NOT_BUILT",
            "reason": "source_family overlap with train/dev",
            "overlap": overlap,
        }

    out_passages = root / "data/theory_validation_v2/passages/true_final_holdout.jsonl"
    out_passages.parent.mkdir(parents=True, exist_ok=True)
    out_passages.write_text(passages_path.read_text(encoding="utf-8"), encoding="utf-8")
    corpus_hash = hashlib.sha256(out_passages.read_bytes()).hexdigest()
    status = {
        "status": "BUILT_UNEVALUATED",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "frozen_method_sha256": _sha_file(frozen),
        "holdout_passages_sha256": corpus_hash,
        "n_passages": len(rows),
        "source_families": sorted(hold_sf),
        "evaluated_once": False,
        "scoring_forbidden_until": "evaluate-final-validation-once",
        "ancient_confirmatory": "LOCKED_NOT_READY",
    }
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "BUILT_UNEVALUATED",
        "true_final_method_holdout": "BUILT_UNEVALUATED",
        "path": str(out_passages.relative_to(root)),
        "holdout_passages_sha256": corpus_hash,
        "n_passages": len(rows),
        "note": "Do not score until evaluate-final-validation-once.",
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

    holdout_path = root / "data/theory_validation_v2/passages/true_final_holdout.jsonl"
    if not holdout_path.exists():
        return {"status": "REFUSED", "reason": "true_final_holdout.jsonl missing"}

    rows = [json.loads(l) for l in holdout_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    frozen_obj = json.loads(frozen.read_text(encoding="utf-8"))
    weights = frozen_obj.get("graph_weights") or {"typed_weight": 0.25, "hungarian_weight": 0.75}
    tw = float(weights.get("typed_weight", 0.25))
    hw = float(weights.get("hungarian_weight", 0.75))

    from rishiq.isef2027.theory_validation_v2 import (
        _fit_predict_candidates,
        _load_split,
        task_b_fingerprint_retrieval,
    )

    train = _load_split(root, "train")
    task_a_models = _fit_predict_candidates(train, rows, masked=False)
    task_a_masked = _fit_predict_candidates(train, rows, masked=True)
    ranked = sorted(
        [m for m in task_a_models if not m["model"].endswith("baseline")],
        key=lambda m: m["metrics"]["macro_f1"],
        reverse=True,
    )
    best_a = ranked[0] if ranked else task_a_models[0]

    task_b = task_b_fingerprint_retrieval(root, rows, typed_w=tw, hung_w=hw, masked=False, extractor="structural")
    task_b_masked = task_b_fingerprint_retrieval(
        root, rows, typed_w=tw, hung_w=hw, masked=True, extractor="structural"
    )

    by_sf: dict[str, list[dict]] = {}
    for r in rows:
        sf = r.get("source_family") or r.get("work_id") or "unknown"
        by_sf.setdefault(sf, []).append(r)
    per_sf = {
        sf: task_b_fingerprint_retrieval(root, rs, typed_w=tw, hung_w=hw, masked=False, extractor="structural")
        for sf, rs in by_sf.items()
    }

    hard = [r for r in rows if r.get("hard_negative_or_cross_theory_context")]
    hard_b = None
    if hard:
        hard_b = task_b_fingerprint_retrieval(
            root, hard, typed_w=tw, hung_w=hw, masked=False, extractor="structural"
        )

    suc_path = review_paths(root)["success_criterion"]
    criterion = json.loads(suc_path.read_text(encoding="utf-8")) if suc_path.exists() else {}

    primary = criterion.get("primary_metric")
    primary_val = None
    if primary == "top1":
        primary_val = task_b.get("top1_retrieval")
    elif primary == "top2":
        primary_val = task_b.get("top2_retrieval")
    elif primary == "mrr":
        primary_val = task_b.get("mrr")

    met = None
    if (
        criterion.get("student_approved")
        and primary_val is not None
        and criterion.get("minimum_primary_value") is not None
    ):
        met = float(primary_val) >= float(criterion["minimum_primary_value"])

    result = {
        "status": "EVALUATED_ONCE_AFTER_METHOD_FREEZE",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "warning": "THIS RESULT MAY NOT BE USED TO RETUNE THE CURRENT FROZEN METHOD.",
        "frozen_method_sha256": _sha_file(frozen),
        "holdout_passages_sha256": hold.get("holdout_passages_sha256"),
        "n_holdout": len(rows),
        "task_a_lexical": best_a,
        "task_a_masked": task_a_masked,
        "task_b_structural": task_b,
        "task_b_masked": task_b_masked,
        "hard_cases": hard_b,
        "per_source_family": per_sf,
        "success_criterion": criterion,
        "primary_metric_value": primary_val,
        "meets_student_success_criterion": met,
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "note": "Passing final validation does NOT unlock ancient confirmatory scoring.",
    }
    out = root / "results/isef2027/validation/final_validation_ONCE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, default=float) + "\n", encoding="utf-8")
    sha = _sha_file(out)
    if sha:
        (out.with_suffix(".sha256")).write_text(sha + "\n", encoding="utf-8")

    hold["status"] = "EVALUATED_ONCE_AFTER_METHOD_FREEZE"
    hold["evaluated_once"] = True
    hold["result_path"] = str(out.relative_to(root))
    hold["result_sha256"] = sha
    status_path.write_text(json.dumps(hold, indent=2) + "\n", encoding="utf-8")

    return result
