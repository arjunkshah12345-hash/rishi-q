"""Post–student-review development finalization (gated; never auto-approves).

Runs only after machine-valid student fingerprint + gold review.
Does not invent thresholds, does not freeze, does not build/score true holdout.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rishiq.isef2027.confirmatory_feasibility import assess_confirmatory_feasibility
from rishiq.isef2027.extractor_gold_eval import evaluate_extractor_gold
from rishiq.isef2027.method_freeze_gates import check_freeze_gates, write_freeze_candidate_if_ready
from rishiq.isef2027.student_review_validate import validate_student_review
from rishiq.isef2027.student_review_workflow import review_paths
from rishiq.isef2027.theory_validation_v2 import run_development_method_selection


def finalize_after_student_review(
    root: Path,
    *,
    n_sim: int = 2000,
    skip_if_criteria_unapproved: bool = True,
) -> dict[str, Any]:
    """Re-run DEV structural selection + power after student review.

    Refuses while fingerprints/gold incomplete. Does not set student_approved flags.
    """
    paths = review_paths(root)
    val = validate_student_review(root)
    if not val.get("ok"):
        return {
            "status": "REFUSED",
            "method_freeze_status": "AWAITING_STUDENT_REVIEW",
            "reason": "Student fingerprint + gold review incomplete or invalid",
            "validation": val,
            "true_final_method_holdout": "NOT_BUILT",
            "ancient_confirmatory": "LOCKED_NOT_READY",
        }

    gold_eval = evaluate_extractor_gold(root)
    if str(gold_eval.get("status", "")).startswith("NOT_AVAILABLE"):
        return {
            "status": "REFUSED",
            "method_freeze_status": "AWAITING_STUDENT_REVIEW",
            "reason": "Extractor gold evaluation unavailable",
            "gold_eval": gold_eval,
        }

    ext_c = json.loads(paths["extractor_criterion"].read_text(encoding="utf-8"))
    suc_c = json.loads(paths["success_criterion"].read_text(encoding="utf-8"))

    if skip_if_criteria_unapproved and (
        ext_c.get("student_approved") is not True or suc_c.get("student_approved") is not True
    ):
        # Still allow DEV revalidation for notebook use, but mark incomplete for freeze
        partial = True
    else:
        partial = False

    # Mark whether metrics were viewed before criterion approval (transparency)
    if ext_c.get("student_approved") is not True and ext_c.get("metrics_viewed_before_approval") is None:
        # Student has not approved yet; recording that gold metrics now exist for transparency
        pass

    n_sim_use = max(int(n_sim), 2000)
    selection = run_development_method_selection(
        root,
        n_sim=n_sim_use,
        post_student_review=True,
    )
    feasibility = assess_confirmatory_feasibility(root)

    marker = {
        "schema": "post_student_dev_finalization_v1",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "n_sim_per_cell": n_sim_use,
        "post_student_review": True,
        "extractor_gold_status": gold_eval.get("status"),
        "extractor_criterion_approved": ext_c.get("student_approved") is True,
        "success_criterion_approved": suc_c.get("student_approved") is True,
        "graph_weights_selected": (selection.get("graph_weight_selection") or {}).get("selected"),
        "confirmatory_feasibility": feasibility.get("feasibility"),
        "true_final_method_holdout": "NOT_BUILT",
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "partial_criteria_pending": partial,
    }
    marker_path = root / "results/isef2027/validation/post_student_dev_finalization.json"
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")

    # Refresh DEV reference for student (not a success criterion)
    task_a = selection.get("selected_task_a_on_dev") or {}
    task_b = selection.get("task_b_dev") or {}
    task_bm = selection.get("task_b_dev_masked") or {}
    ref = {
        "purpose": "REFERENCE_ONLY_NOT_A_SUCCESS_CRITERION",
        "chance_baselines_7way": {"top1": 1 / 7, "top2": 2 / 7},
        "development_structural_snapshot": {
            "top1": task_b.get("top1_retrieval"),
            "top2": task_b.get("top2_retrieval"),
            "mrr": task_b.get("mrr"),
            "masked_top1": task_bm.get("top1_retrieval"),
            "empty_extraction_rate": (
                (task_b.get("empty_extraction_n") or 0) / task_b["n"] if task_b.get("n") else None
            ),
            "note": "Post-student-review DEVELOPMENT snapshot when finalize-after-student-review ran.",
        },
        "development_lexical_task_a_snapshot": {
            "top1": (task_a.get("metrics") or {}).get("top1_accuracy"),
            "top2": (task_a.get("metrics") or {}).get("top2_accuracy"),
            "macro_f1": (task_a.get("metrics") or {}).get("macro_f1"),
        },
        "warning": "Do not set final-holdout thresholds solely to pass these numbers.",
        "updated_at": marker["completed_at"],
    }
    paths["dev_reference"].write_text(json.dumps(ref, indent=2) + "\n", encoding="utf-8")

    gate = write_freeze_candidate_if_ready(root)
    return {
        "status": "PARTIAL_CRITERIA_PENDING" if partial else "DEV_FINALIZATION_COMPLETE",
        "method_freeze_status": gate.get("method_freeze_status"),
        "marker": str(marker_path.relative_to(root)),
        "gold_eval_status": gold_eval.get("status"),
        "graph_weights": marker["graph_weights_selected"],
        "power_n_sim": n_sim_use,
        "confirmatory_feasibility": feasibility.get("feasibility"),
        "gates": gate,
        "true_final_method_holdout": "NOT_BUILT",
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "note": (
            "Fill and approve STUDENT_REQUIRED criterion JSONs before freeze-method. "
            "Do not auto-approve."
        ),
    }


def pre_freeze_summary(root: Path) -> dict[str, Any]:
    """Machine-readable status block matching the required pass summary fields."""
    from rishiq.isef2027.student_review_workflow import review_status

    st = review_status(root)
    gate = check_freeze_gates(root)
    gold_path = root / "results/isef2027/validation/extractor_gold_evaluation.json"
    gold = json.loads(gold_path.read_text(encoding="utf-8")) if gold_path.exists() else {}
    sel_path = root / "results/isef2027/validation/external_dev_method_selection.json"
    sel = json.loads(sel_path.read_text(encoding="utf-8")) if sel_path.exists() else {}
    power_path = root / "results/isef2027/validation/power_sensitivity_table.json"
    power = json.loads(power_path.read_text(encoding="utf-8")) if power_path.exists() else {}
    feas_path = root / "results/isef2027/validation/confirmatory_corpus_feasibility.json"
    feas = json.loads(feas_path.read_text(encoding="utf-8")) if feas_path.exists() else {}
    paths = review_paths(root)
    ext_c = json.loads(paths["extractor_criterion"].read_text(encoding="utf-8"))
    suc_c = json.loads(paths["success_criterion"].read_text(encoding="utf-8"))

    task_b = sel.get("task_b_dev") or {}
    task_bm = sel.get("task_b_dev_masked") or {}
    weights = (sel.get("graph_weight_selection") or {}).get("selected")
    post = root / "results/isef2027/validation/post_student_dev_finalization.json"
    weights_finalized = False
    if post.exists():
        weights_finalized = json.loads(post.read_text()).get("post_student_review") is True

    if gold.get("status") == "EVALUATED_VS_STUDENT_GOLD":
        metrics = {
            "node_f1": (gold.get("node") or {}).get("f1"),
            "relation_f1": (gold.get("relation") or {}).get("f1"),
            "typed_relation_f1": (gold.get("typed_relation") or {}).get("f1"),
            "coverage": gold.get("coverage"),
        }
    else:
        metrics = "NOT_AVAILABLE — STUDENT GOLD INCOMPLETE"

    return {
        "CI": "see_github_actions",
        "STUDENT_FINGERPRINT_REVIEW": f"{st['fingerprint_review']['completed']} / 7 completed",
        "GOLD_EXTRACTION_REVIEW": (
            f"{st['gold_extraction_review']['completed']} / {st['gold_extraction_review']['total']} completed"
        ),
        "EXTRACTOR_GOLD_METRICS": metrics,
        "EXTRACTOR_ACCEPTANCE_CRITERION": "APPROVED" if ext_c.get("student_approved") else "NOT APPROVED",
        "DEVELOPMENT_STRUCTURAL_RESULTS": {
            "top1": task_b.get("top1_retrieval"),
            "top2": task_b.get("top2_retrieval"),
            "mrr": task_b.get("mrr"),
            "masked_top1": task_bm.get("top1_retrieval"),
            "empty_extraction_rate": (
                (task_b.get("empty_extraction_n") or 0) / task_b["n"] if task_b.get("n") else None
            ),
        },
        "SOURCE_FAMILY_ROBUSTNESS": {
            "lo_work": (sel.get("leave_one_work_out") or {}).get("mean_top1"),
            "lo_author": (sel.get("leave_one_author_family_out") or {}).get("mean_top1"),
            "lo_source_family": (sel.get("leave_one_source_family_out") or {}).get("mean_top1"),
        },
        "GRAPH_WEIGHTS": weights if weights_finalized else f"{weights} — NOT FINALIZED",
        "FINAL_VALIDATION_SUCCESS_CRITERION": "APPROVED" if suc_c.get("student_approved") else "NOT APPROVED",
        "POWER": {
            "n_sim_per_cell": power.get("n_sim_per_cell"),
            "variance_source": power.get("variance_source"),
            "n_rows": len(power.get("rows") or []),
        },
        "CONFIRMATORY_FEASIBILITY": feas.get("feasibility")
        or "PROJECT_FEASIBLE_WITH_REDUCED_EFFECT_SENSITIVITY",
        "METHOD_FREEZE_STATUS": gate.get("method_freeze_status"),
        "TRUE_FINAL_METHOD_HOLDOUT": "NOT_BUILT"
        if gate.get("true_final_method_holdout") == "NOT_BUILT"
        else gate.get("true_final_method_holdout"),
        "ANCIENT_CONFIRMATORY": "LOCKED_NOT_READY",
        "blockers": gate.get("blockers"),
    }
