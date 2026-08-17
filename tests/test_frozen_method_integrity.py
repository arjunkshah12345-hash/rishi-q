"""Adversarial integrity tests for frozen-method protection.

Uses temporary copies so the real repository is not corrupted.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from rishiq.isef2027.confirmatory_lock import verify_ancient_confirmatory_lock
from rishiq.isef2027.frozen_method_integrity import (
    FROZEN_REL,
    build_frozen_method_manifest,
    verify_frozen_method,
    write_frozen_method_manifest,
)
from rishiq.isef2027.method_freeze_gates import (
    build_final_validation_holdout,
    evaluate_final_validation_once,
)
from rishiq.isef2027.student_review_workflow import ensure_student_artifacts, review_paths

ROOT = Path(__file__).resolve().parents[1]

# Minimal tree to copy for integrity fixtures
_COPY_RELS = [
    "corpus/confirmatory_sealed/lock.json",
    "artifacts/isef2027/PROJECT_STATUS.json",
    "artifacts/isef2027/split_manifest.json",
    "artifacts/isef2027/extractor_acceptance_criterion_STUDENT_REQUIRED.json",
    "artifacts/isef2027/final_validation_success_criterion_STUDENT_REQUIRED.json",
    "artifacts/isef2027/student_review/fingerprint_decisions_v1.json",
    "data/theory_validation_v2/passages/corpus_meta.json",
    "data/theory_validation_v2/passages/train.jsonl",
    "data/theory_validation_v2/passages/development.jsonl",
    "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json",
    "data/theory_validation_v2/eligibility/source_eligibility_v1.json",
    "data/theory_validation_v2/extraction_gold/meta.json",
    "data/theory_validation_v2/extraction_gold/gold_templates_BLANK.jsonl",
    "ontology/concept_graph",
    "ontology/ontology_v0.1.yaml",
    "src/rishiq/isef2027/structural_extractor.py",
    "src/rishiq/isef2027/concept_graph.py",
    "src/rishiq/isef2027/graph_similarity.py",
    "src/rishiq/isef2027/graph_templates.py",
    "src/rishiq/isef2027/theory_validation_v2.py",
    "src/rishiq/isef2027/theory_validation_v2_corpus.py",
    "src/rishiq/isef2027/method_freeze_gates.py",
    "results/isef2027/validation/external_dev_method_selection.json",
    "results/isef2027/validation/power_sensitivity_table.json",
    "results/isef2027/validation/post_student_dev_finalization.json",
]


def _copy_tree(dst: Path) -> Path:
    for rel in _COPY_RELS:
        src = ROOT / rel
        if not src.exists():
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
    # Ensure student artifacts exist in fixture
    ensure_student_artifacts(dst)
    # Seed a student gold file for mutation tests
    gold = dst / "data/theory_validation_v2/extraction_gold/student_gold_v1.jsonl"
    if not gold.exists():
        gold.write_text(
            json.dumps(
                {
                    "passage_id": "fixture-gold-1",
                    "entities": [],
                    "relations": [],
                    "annotation_locked": True,
                    "ai_generated": False,
                    "student_decisions_ai_generated": False,
                    "student_decisions_present": True,
                }
            )
            + "\n",
            encoding="utf-8",
        )
    # Ensure selection has weights
    sel_path = dst / "results/isef2027/validation/external_dev_method_selection.json"
    sel_path.parent.mkdir(parents=True, exist_ok=True)
    if sel_path.exists():
        sel = json.loads(sel_path.read_text(encoding="utf-8"))
    else:
        sel = {}
    sel.setdefault(
        "graph_weight_selection",
        {"selected": {"typed_weight": 0.25, "hungarian_weight": 0.75}},
    )
    if not (sel.get("graph_weight_selection") or {}).get("selected"):
        sel["graph_weight_selection"] = {"selected": {"typed_weight": 0.25, "hungarian_weight": 0.75}}
    sel_path.write_text(json.dumps(sel, indent=2) + "\n", encoding="utf-8")
    return dst


def _freeze_fixture(dst: Path) -> dict:
    # Approve criteria so success criterion object is frozen
    paths = review_paths(dst)
    suc = json.loads(paths["success_criterion"].read_text(encoding="utf-8"))
    suc["primary_metric"] = "top1"
    suc["minimum_primary_value"] = 0.5
    suc["student_approved"] = True
    suc["student_decisions_present"] = True
    paths["success_criterion"].write_text(json.dumps(suc, indent=2) + "\n", encoding="utf-8")
    manifest = build_frozen_method_manifest(dst)
    return write_frozen_method_manifest(dst, manifest)


@pytest.fixture()
def frozen_repo(tmp_path: Path) -> Path:
    dst = tmp_path / "repo"
    dst.mkdir()
    _copy_tree(dst)
    _freeze_fixture(dst)
    return dst


def test_live_confirmatory_lock_ok():
    out = verify_ancient_confirmatory_lock(ROOT)
    assert out["ok"] is True
    assert out["ancient_confirmatory_locked"] is True
    assert out["status_label"] == "LOCKED_NOT_READY"


def test_fingerprint_mutation_fails(frozen_repo: Path):
    fp = frozen_repo / "ontology/concept_graph/template_fp_newtonian.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    data["_integrity_probe"] = "mutated"
    fp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("fingerprint" in f for f in out["failures"])


def test_extractor_mutation_fails(frozen_repo: Path):
    path = frozen_repo / "src/rishiq/isef2027/structural_extractor.py"
    path.write_text(path.read_text(encoding="utf-8") + "\n# integrity probe\n", encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("extractor" in f for f in out["failures"])


def test_graph_weight_mutation_fails(frozen_repo: Path):
    sel_path = frozen_repo / "results/isef2027/validation/external_dev_method_selection.json"
    sel = json.loads(sel_path.read_text(encoding="utf-8"))
    sel["graph_weight_selection"]["selected"]["typed_weight"] = 0.99
    sel_path.write_text(json.dumps(sel, indent=2) + "\n", encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("graph_weight" in f for f in out["failures"])


def test_success_criterion_mutation_fails(frozen_repo: Path):
    paths = review_paths(frozen_repo)
    suc = json.loads(paths["success_criterion"].read_text(encoding="utf-8"))
    suc["minimum_primary_value"] = 0.99
    paths["success_criterion"].write_text(json.dumps(suc, indent=2) + "\n", encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("success_criterion" in f or "final_validation" in f for f in out["failures"])


def test_student_fingerprint_decision_mutation_fails(frozen_repo: Path):
    paths = review_paths(frozen_repo)
    dec = json.loads(paths["fingerprint_decisions"].read_text(encoding="utf-8"))
    dec["integrity_probe"] = True
    paths["fingerprint_decisions"].write_text(json.dumps(dec, indent=2) + "\n", encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("fingerprint_decisions" in f or "student_fingerprint" in f for f in out["failures"])


def test_student_gold_mutation_fails(frozen_repo: Path):
    paths = review_paths(frozen_repo)
    gold = paths["student_gold"]
    gold.write_text(gold.read_text(encoding="utf-8") + '{"passage_id":"x"}\n', encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("student_gold" in f for f in out["failures"])


def test_source_family_rule_mutation_fails(frozen_repo: Path):
    path = frozen_repo / "data/theory_validation_v2/eligibility/source_eligibility_v1.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data["integrity_probe"] = True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("corpus_development" in f or "eligibility" in f for f in out["failures"])


def test_confirmatory_lock_mutation_refuses_integrity(frozen_repo: Path):
    lock = frozen_repo / "corpus/confirmatory_sealed/lock.json"
    data = json.loads(lock.read_text(encoding="utf-8"))
    data["allow_open_sealed"] = True
    lock.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    out = verify_frozen_method(frozen_repo)
    assert out["status"] == "FROZEN_METHOD_INTEGRITY_FAILURE"
    assert any("ancient_confirmatory" in f or "allow_open" in f for f in out["failures"])


def test_holdout_mutation_refuses_evaluation(frozen_repo: Path):
    # Build a fake acquired holdout + status as BUILT
    acquired = frozen_repo / "data/theory_validation_v2/final_holdout_candidates/acquired"
    acquired.mkdir(parents=True, exist_ok=True)
    row = {
        "passage_id": "hold-1",
        "work_id": "hold_work",
        "source_family": "hold_family_unique_xyz",
        "text": "a particle interacts with a field",
        "theory_label": "newtonian",
    }
    passages = acquired / "passages.jsonl"
    passages.write_text(json.dumps(row) + "\n", encoding="utf-8")

    # Mark corpus families so no overlap
    meta_path = frozen_repo / "data/theory_validation_v2/passages/corpus_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta["train_source_families"] = []
    meta["dev_source_families"] = []
    meta["source_family_overlap_train_dev"] = []
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    # Empty train/dev to avoid overlap checks on work ids
    (frozen_repo / "data/theory_validation_v2/passages/train.jsonl").write_text("", encoding="utf-8")
    (frozen_repo / "data/theory_validation_v2/passages/development.jsonl").write_text("", encoding="utf-8")

    # Re-freeze after corpus_meta change so integrity matches build-time hashes
    _freeze_fixture(frozen_repo)

    built = build_final_validation_holdout(frozen_repo)
    assert built["status"] == "BUILT_UNEVALUATED"

    holdout = frozen_repo / "data/theory_validation_v2/passages/true_final_holdout.jsonl"
    holdout.write_text(holdout.read_text(encoding="utf-8") + json.dumps({**row, "passage_id": "tampered"}) + "\n")

    ev = evaluate_final_validation_once(frozen_repo)
    assert ev["status"] == "REFUSED"
    assert ev.get("reason") == "FINAL_HOLDOUT_INTEGRITY_FAILURE"


def test_one_shot_second_eval_refuses(frozen_repo: Path):
    status_path = frozen_repo / "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json"
    holdout = frozen_repo / "data/theory_validation_v2/passages/true_final_holdout.jsonl"
    holdout.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(
        {
            "passage_id": "hold-1",
            "work_id": "hold_work",
            "source_family": "hold_family_unique_xyz",
            "text": "a particle interacts with a field",
            "theory_label": "newtonian",
        }
    ) + "\n"
    holdout.write_text(content, encoding="utf-8")
    import hashlib

    h = hashlib.sha256(holdout.read_bytes()).hexdigest()
    frozen_sha = hashlib.sha256((frozen_repo / FROZEN_REL).read_bytes()).hexdigest()
    status_path.write_text(
        json.dumps(
            {
                "status": "EVALUATED_ONCE_AFTER_METHOD_FREEZE",
                "evaluated_once": True,
                "holdout_sha256": h,
                "frozen_method_sha256": frozen_sha,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    ev = evaluate_final_validation_once(frozen_repo)
    assert ev["status"] == "REFUSED"
    assert "EVALUATED_ONCE" in ev.get("reason", "")


def test_build_holdout_refuses_on_integrity_failure(frozen_repo: Path):
    fp = frozen_repo / "ontology/concept_graph/template_fp_newtonian.json"
    fp.write_text(fp.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    # ensure hash changes
    data = json.loads(fp.read_text(encoding="utf-8"))
    data["probe"] = 1
    fp.write_text(json.dumps(data) + "\n", encoding="utf-8")
    out = build_final_validation_holdout(frozen_repo)
    assert out["status"] == "REFUSED"
    assert out.get("reason") == "FROZEN_METHOD_INTEGRITY_FAILURE"


def test_provenance_fields_on_templates():
    ensure_student_artifacts(ROOT)
    paths = review_paths(ROOT)
    dec = json.loads(paths["fingerprint_decisions"].read_text(encoding="utf-8"))
    assert dec["template_created_by"] == "coding_agent"
    assert dec["template_generated_with_ai"] is True
    assert dec["student_decisions_ai_generated"] is False
    assert dec["student_decisions_present"] is False
    ext = json.loads(paths["extractor_criterion"].read_text(encoding="utf-8"))
    assert ext["template_generated_with_ai"] is True
    assert ext["student_approved"] is False
    meta = json.loads((ROOT / "data/theory_validation_v2/extraction_gold/meta.json").read_text())
    assert meta["template_created_by"] == "coding_agent"
