"""Method freeze CANDIDATE artifact (not frozen until student approval)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _git_sha(root: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        )
    except Exception:
        return "UNKNOWN"


def _file_sha(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_method_freeze_candidate(root: Path, *, ready: bool, blockers: list[str]) -> dict[str, Any]:
    dev = root / "results/isef2027/validation/external_dev_method_selection.json"
    sel = json.loads(dev.read_text(encoding="utf-8")) if dev.exists() else {}
    weights = (sel.get("graph_weight_selection") or {}).get("selected") or {}
    task_a = sel.get("selected_task_a_on_dev") or {}

    fp_dir = root / "ontology/concept_graph"
    fp_hashes = {}
    if fp_dir.exists():
        for p in sorted(fp_dir.glob("template_fp_*.json")):
            fp_hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()

    status = "READY_FOR_STUDENT_METHOD_FREEZE" if ready else "NOT_READY_TO_FREEZE"
    payload = {
        "artifact": "theory_validation_v2_method_freeze_CANDIDATE",
        "status": status,
        "ready_for_student_method_freeze": ready,
        "blockers": blockers,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": _git_sha(root),
        "extractor_version": "structural_extractor_deterministic_v1",
        "ontology_version": "rishiq_concept_graph_v1",
        "fingerprint_hashes": fp_hashes,
        "student_review_status": {
            "physics_fingerprints_verified": False,
            "extraction_gold_approved": False,
            "validation_success_criterion_approved": False,
        },
        "graph_algorithm": "typed_relation_coverage_adjusted + hungarian Option_B",
        "graph_weights": weights,
        "retired_proxy_weights": {"typed_weight": 1.0, "hungarian_weight": 0.0, "status": "RETIRED_PROXY_SELECTION"},
        "mask_list": "giveaway_vocab_v1",
        "classifier_baseline": task_a.get("model"),
        "structural_scoring_method": "primary_structural = tw*typed_cov_adj + hw*hungarian",
        "theory_competitors": [
            "newtonian",
            "thermodynamics",
            "classical_em",
            "relativity",
            "quantum_mechanics",
            "quantum_field_theory",
            "atomistic_corpuscular",
        ],
        "preprocessing": "none",
        "source_eligibility_rules": "data/theory_validation_v2/eligibility/source_eligibility_v1.json",
        "family_split_rules": "no source_family overlap train↔development; true final holdout NOT_BUILT until freeze",
        "statistical_metrics": ["top1", "top2", "mrr", "macro_f1", "work_level_permutation_power"],
        "random_seeds": {"sklearn": 0, "power": 20270816, "variance_bootstrap": 0},
        "corpus_meta_sha256": _file_sha(root / "data/theory_validation_v2/passages/corpus_meta.json"),
        "dev_selection_artifact": "results/isef2027/validation/external_dev_method_selection.json",
        "true_final_method_holdout": "NOT_BUILT",
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "note": "Do NOT mark frozen until student approval. Do NOT evaluate true final holdout yet.",
    }
    out = root / "artifacts/isef2027/theory_validation_v2_method_freeze_CANDIDATE.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
