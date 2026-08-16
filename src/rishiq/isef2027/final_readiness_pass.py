"""Orchestrate final pre-confirmatory readiness pass (no true holdout eval)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rishiq.isef2027.confirmatory_feasibility import assess_confirmatory_feasibility
from rishiq.isef2027.dev_translation_study import run_dev_translation_variance_study
from rishiq.isef2027.extraction_gold import create_blank_gold_templates, evaluate_extractor_vs_gold
from rishiq.isef2027.final_holdout_eligibility import write_final_holdout_eligibility
from rishiq.isef2027.fingerprint_distinguishability import fingerprint_distinguishability_report
from rishiq.isef2027.graph_robustness import run_graph_transformation_benchmark
from rishiq.isef2027.method_freeze_candidate import write_method_freeze_candidate
from rishiq.isef2027.real_translation_study import run_real_translation_sensitivity
from rishiq.isef2027.theory_validation_v2 import run_development_method_selection
from rishiq.isef2027.theory_validation_v2_corpus import build_external_theory_corpus


STUDENT_CHECKLIST = """# Student fingerprint + method decisions (required)

For each theory fingerprint, record exactly one:

KEEP | MODIFY | DELETE | UNSURE | SOURCE_NEEDED

Theories:
- newtonian
- thermodynamics
- classical_em
- relativity
- quantum_mechanics
- quantum_field_theory
- atomistic_corpuscular

Until complete: physics_fingerprints_verified = false

Also approve:
1. Extraction gold annotations (blank templates in data/theory_validation_v2/extraction_gold/)
2. Exact final-validation success criterion (before any true holdout eval)
3. Method freeze candidate JSON (artifacts READY_FOR_STUDENT_METHOD_FREEZE only when engineering gates pass)

Coding agents must NOT mark fingerprints student-approved.
"""


def run_final_readiness_pass(root: Path) -> dict[str, Any]:
    corpus_meta = build_external_theory_corpus(root)
    gold_meta = create_blank_gold_templates(root, n=40)
    extract_eval = evaluate_extractor_vs_gold(root)
    graph_rob = run_graph_transformation_benchmark(root)
    # Relabel old translation proxy
    proxy = run_dev_translation_variance_study(root)
    if isinstance(proxy, dict):
        proxy["accurate_name"] = "WITHIN_WORK_PASSAGE_SIMILARITY_PROXY"
        proxy["study_kind"] = "PROXY_NOT_MULTI_TRANSLATOR"
        ppath = root / "results/isef2027/validation/dev_translation_variance.json"
        if ppath.exists():
            ppath.write_text(json.dumps(proxy, indent=2, default=float) + "\n", encoding="utf-8")
    real_tr = run_real_translation_sensitivity(root)
    fp_dist = fingerprint_distinguishability_report(root)
    elig = write_final_holdout_eligibility(root)
    # Method selection (structural extractor; DEV only)
    sel = run_development_method_selection(root)
    feas = assess_confirmatory_feasibility(root)

    blockers = []
    if corpus_meta.get("source_family_overlap_train_dev"):
        blockers.append(f"source_family_overlap_train_dev={corpus_meta['source_family_overlap_train_dev']}")
    if extract_eval.get("status") != "EVALUATED_VS_STUDENT_GOLD":
        blockers.append("Stage-1 extraction gold not student-approved")
    blockers.append("physics_fingerprints_verified=false")
    blockers.append("validation success criterion not student-approved")
    if fp_dist.get("flags"):
        blockers.append("fingerprint distinguishability flags: " + "; ".join(fp_dist["flags"][:3]))

    # Engineering can be READY_FOR_STUDENT_METHOD_FREEZE only if family-clean + extractor exists
    # Student gates still pending → honest status is NOT_READY_TO_FREEZE until student acts,
    # OR READY_FOR_STUDENT_METHOD_FREEZE meaning engineering done and awaiting student.
    # Spec: STATE A = READY_FOR_STUDENT_METHOD_FREEZE means fingerprints awaiting only explicit
    # student approval OR approved. So engineering-complete with student review pending = STATE A.
    eng_ok = (
        not corpus_meta.get("source_family_overlap_train_dev")
        and extract_eval.get("status") in {"AWAITING_STUDENT_GOLD_APPROVAL", "EVALUATED_VS_STUDENT_GOLD"}
        and sel.get("task_b_dev", {}).get("claim_bearing") is True
        and corpus_meta.get("true_final_method_holdout") == "NOT_BUILT"
    )
    # Spec end-state A includes "fingerprints awaiting only explicit student approval"
    # and "extractor validated" — without gold, extractor not fully validated → NOT_READY
    ready = eng_ok and extract_eval.get("status") == "EVALUATED_VS_STUDENT_GOLD"
    # Honest: without student gold, NOT_READY_TO_FREEZE
    freeze = write_method_freeze_candidate(root, ready=ready, blockers=blockers)

    checklist_path = root / "docs/STUDENT_FINGERPRINT_REVIEW_CHECKLIST.md"
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_path.write_text(STUDENT_CHECKLIST, encoding="utf-8")

    status = {
        "pass": "final_pre_confirmatory_readiness",
        "method_freeze_status": freeze["status"],
        "true_final_theory_holdout": "NOT_BUILT",
        "constructed_unevaluated": corpus_meta.get("constructed_unevaluated_status"),
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "ci_note": "run tests separately",
        "corpus": {
            "n_passages": corpus_meta.get("n_passages"),
            "n_works": corpus_meta.get("n_works"),
            "n_authors": corpus_meta.get("n_authors"),
            "n_source_families": corpus_meta.get("n_source_families"),
            "source_family_overlap_train_dev": corpus_meta.get("source_family_overlap_train_dev"),
            "author_family_overlap_train_dev": corpus_meta.get("author_family_overlap_train_dev"),
        },
        "extraction_stage1": extract_eval,
        "gold_templates": gold_meta,
        "task_b_dev": sel.get("task_b_dev"),
        "task_b_masked": sel.get("task_b_dev_masked"),
        "task_b_lexical_baseline": sel.get("task_b_lexical_proxy_baseline"),
        "task_a_selected": sel.get("selected_task_a_on_dev"),
        "loso": {
            "work": sel.get("leave_one_work_out"),
            "author_family": sel.get("leave_one_author_family_out"),
            "source_family": sel.get("leave_one_source_family_out"),
        },
        "graph_robustness_keys": list((graph_rob.get("results") or {}).keys()),
        "translation_real": {
            "n_groups": real_tr.get("n_groups"),
            "comparisons": real_tr.get("comparisons"),
        },
        "variance": sel.get("calibration_variance"),
        "power_rows_n": len(sel.get("power_sensitivity_table") or []),
        "feasibility": feas.get("feasibility"),
        "fingerprint_flags": fp_dist.get("flags"),
        "eligibility": elig,
        "blockers": blockers,
        "student_checklist": str(checklist_path.relative_to(root)),
    }

    # PROJECT_STATUS update
    proj = root / "artifacts/isef2027/PROJECT_STATUS.json"
    cur = json.loads(proj.read_text(encoding="utf-8")) if proj.exists() else {}
    cur.update(
        {
            "method_freeze_status": freeze["status"],
            "true_final_method_holdout": "NOT_BUILT",
            "constructed_unevaluated_validation_set": "PRESERVED_UNEVALUATED",
            "ancient_confirmatory_status": "LOCKED_NOT_READY",
            "physics_fingerprints_verified": False,
            "n_passages": corpus_meta.get("n_passages"),
            "n_works": corpus_meta.get("n_works"),
            "n_authors": corpus_meta.get("n_authors"),
            "n_source_families": corpus_meta.get("n_source_families"),
            "structural_extractor": "structural_extractor_deterministic_v1",
            "confirmatory_feasibility": feas.get("feasibility"),
        }
    )
    proj.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")

    out = root / "results/isef2027/validation/final_readiness_pass_summary.json"
    out.write_text(json.dumps(status, indent=2, default=float) + "\n", encoding="utf-8")
    return status
