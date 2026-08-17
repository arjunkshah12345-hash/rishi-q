"""Canonical frozen-method manifest + integrity verification."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rishiq.isef2027.confirmatory_lock import verify_ancient_confirmatory_lock
from rishiq.isef2027.student_review_workflow import THEORIES, review_paths

SCHEMA_VERSION = "frozen_method_manifest_v1"
FROZEN_REL = "artifacts/isef2027/theory_validation_v2_method_FROZEN.json"

# Claim-bearing extractor + helpers that affect extraction behavior
EXTRACTOR_SOURCES = [
    "src/rishiq/isef2027/structural_extractor.py",
    "src/rishiq/isef2027/concept_graph.py",
]

# Ontology / schema files affecting node/edge kinds & interpretation
ONTOLOGY_PATHS = [
    "src/rishiq/isef2027/concept_graph.py",
    "ontology/concept_graph/schema.json",
    "ontology/concept_graph/index.json",
    "ontology/ontology_v0.1.yaml",
]

# Graph scoring claim-bearing sources
GRAPH_SCORING_SOURCES = [
    "src/rishiq/isef2027/graph_similarity.py",
    "src/rishiq/isef2027/graph_templates.py",
]

# Preprocessing / masking / hard-negative related sources
PREPROCESSING_SOURCES = [
    "src/rishiq/isef2027/theory_validation_v2.py",
    "src/rishiq/isef2027/theory_validation_v2_corpus.py",
]

# Statistical method sources used for final validation claims
STATISTICAL_SOURCES = [
    "src/rishiq/isef2027/theory_validation_v2.py",
    "src/rishiq/isef2027/method_freeze_gates.py",
]

# Source-family / eligibility
CORPUS_RULE_PATHS = [
    "data/theory_validation_v2/passages/corpus_meta.json",
    "data/theory_validation_v2/eligibility/source_eligibility_v1.json",
    "artifacts/isef2027/split_manifest.json",
    "data/theory_validation_v2/passages/train.jsonl",
    "data/theory_validation_v2/passages/development.jsonl",
]

FINGERPRINT_TEMPLATE = "ontology/concept_graph/template_fp_{theory}.json"


def _git_sha(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return "UNKNOWN"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return sha256_bytes(path.read_bytes())


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def _hash_paths(root: Path, rels: list[str]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for rel in rels:
        out[rel] = sha256_file(root / rel)
    return out


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint_entries(root: Path) -> list[dict[str, Any]]:
    entries = []
    for tid in THEORIES:
        rel = FINGERPRINT_TEMPLATE.format(theory=tid)
        path = root / rel
        entries.append(
            {
                "theory_name": tid,
                "path": rel,
                "sha256": sha256_file(path),
            }
        )
    return entries


def build_frozen_method_manifest(root: Path) -> dict[str, Any]:
    """Assemble the immutable claim-bearing freeze manifest (call only at freeze)."""
    root = Path(root)
    paths = review_paths(root)
    sel = _load_json(root / "results/isef2027/validation/external_dev_method_selection.json") or {}
    weights = (sel.get("graph_weight_selection") or {}).get("selected")
    if not isinstance(weights, dict):
        weights = {}
    tw = float(weights.get("typed_weight", 0.25))
    hw = float(weights.get("hungarian_weight", 0.75))

    post = _load_json(root / "results/isef2027/validation/post_student_dev_finalization.json") or {}
    power = _load_json(root / "results/isef2027/validation/power_sensitivity_table.json") or {}
    suc = _load_json(paths["success_criterion"]) or {}
    ext_c = _load_json(paths["extractor_criterion"]) or {}

    from rishiq.isef2027.structural_extractor import EXTRACTOR_VERSION

    manifest: dict[str, Any] = {
        "artifact": "theory_validation_v2_method_FROZEN",
        "schema_version": SCHEMA_VERSION,
        "git_sha": _git_sha(root),
        "freeze_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "point_of_no_return_for_final_validation": True,
        "repository_state": {
            "git_sha": _git_sha(root),
            "schema_version": SCHEMA_VERSION,
        },
        "extractor": {
            "extractor_version": EXTRACTOR_VERSION,
            "extractor_source_path": EXTRACTOR_SOURCES[0],
            "extractor_source_sha256": sha256_file(root / EXTRACTOR_SOURCES[0]),
            "helper_module_sha256": _hash_paths(root, EXTRACTOR_SOURCES),
        },
        "ontology": {
            "files_sha256": _hash_paths(root, ONTOLOGY_PATHS),
        },
        "fingerprints": fingerprint_entries(root),
        "graph_scoring": {
            "sources_sha256": _hash_paths(root, GRAPH_SCORING_SOURCES),
            "algorithm": "typed_relation_coverage_adjusted + hungarian Option_B",
            "graph_weights": {"typed_weight": tw, "hungarian_weight": hw},
            "retired_proxy_weights": {
                "typed_weight": 1.0,
                "hungarian_weight": 0.0,
                "status": "RETIRED_PROXY_SELECTION",
            },
        },
        "preprocessing": {
            "vocabulary_mask_list": "giveaway_vocab_v1",
            "sources_sha256": _hash_paths(root, PREPROCESSING_SOURCES),
            "notes": "mask_giveaway_vocab + hard_negative_or_cross_theory_context labeling in corpus builder",
        },
        "student_scientific_artifacts": {
            "fingerprint_decisions_path": _rel(root, paths["fingerprint_decisions"]),
            "fingerprint_decisions_sha256": sha256_file(paths["fingerprint_decisions"]),
            "student_gold_path": _rel(root, paths["student_gold"]),
            "student_gold_sha256": sha256_file(paths["student_gold"]),
            "extractor_acceptance_criterion_path": _rel(root, paths["extractor_criterion"]),
            "extractor_acceptance_criterion_sha256": sha256_file(paths["extractor_criterion"]),
            "final_validation_success_criterion_path": _rel(root, paths["success_criterion"]),
            "final_validation_success_criterion_sha256": sha256_file(paths["success_criterion"]),
            "extractor_criterion_object": ext_c,
            "success_criterion_object": suc,
        },
        "corpus_development_state": {
            "files_sha256": _hash_paths(root, CORPUS_RULE_PATHS),
            "source_eligibility_rules": "data/theory_validation_v2/eligibility/source_eligibility_v1.json",
        },
        "statistical_method": {
            "sources_sha256": _hash_paths(root, STATISTICAL_SOURCES),
            "metrics": ["top1", "top2", "mrr", "macro_f1", "work_level_permutation_power"],
            "power_artifact_sha256": sha256_file(
                root / "results/isef2027/validation/power_sensitivity_table.json"
            ),
            "n_sim_per_cell": power.get("n_sim_per_cell"),
        },
        "development_selection_result": {
            "artifact": "results/isef2027/validation/external_dev_method_selection.json",
            "artifact_sha256": sha256_file(
                root / "results/isef2027/validation/external_dev_method_selection.json"
            ),
            "post_student_finalization_sha256": sha256_file(
                root / "results/isef2027/validation/post_student_dev_finalization.json"
            ),
            "graph_weights": {"typed_weight": tw, "hungarian_weight": hw},
            "structural_configuration": "structural_extractor_deterministic_v1",
            "lexical_baseline": (sel.get("selected_task_a_on_dev") or {}).get("model"),
            "development_metrics_snapshot": {
                "task_b_dev": sel.get("task_b_dev"),
                "selected_task_a_on_dev": sel.get("selected_task_a_on_dev"),
            },
            "post_student_marker": {
                "post_student_review": post.get("post_student_review"),
            },
        },
        "final_validation_criterion": suc,
        "true_final_method_holdout": "NOT_BUILT",
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "constructed_unevaluated_validation_set": "PRESERVED_UNEVALUATED",
    }
    return manifest


def write_frozen_method_manifest(root: Path, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    root = Path(root)
    payload = manifest or build_frozen_method_manifest(root)
    out = root / FROZEN_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=False) + "\n"
    out.write_text(text, encoding="utf-8")
    digest = sha256_bytes(text.encode("utf-8"))
    out.with_suffix(".sha256").write_text(digest + "\n", encoding="utf-8")
    payload["_written_sha256"] = digest
    payload["_path"] = str(out.relative_to(root))
    return payload


def _expect_file_hash(root: Path, rel: str | None, expected: str | None, failures: list[str], label: str) -> None:
    if not rel:
        return
    got = sha256_file(root / rel)
    if expected is None and got is None:
        return
    if got != expected:
        failures.append(f"{label}: {rel} sha256 changed (expected {expected}, got {got})")


def verify_frozen_method(root: Path) -> dict[str, Any]:
    """Recompute every stored SHA256 and config. Does not update the manifest."""
    root = Path(root)
    frozen_path = root / FROZEN_REL
    if not frozen_path.exists():
        return {
            "status": "FROZEN_METHOD_INTEGRITY_FAILURE",
            "ok": False,
            "failures": ["frozen method manifest missing"],
            "path": FROZEN_REL,
        }

    manifest = _load_json(frozen_path)
    if not isinstance(manifest, dict):
        return {
            "status": "FROZEN_METHOD_INTEGRITY_FAILURE",
            "ok": False,
            "failures": ["frozen manifest unreadable"],
        }

    failures: list[str] = []

    # Manifest file self-hash if sidecar present
    sidecar = frozen_path.with_suffix(".sha256")
    if sidecar.exists():
        expected_self = sidecar.read_text(encoding="utf-8").strip().split()[0]
        got_self = sha256_file(frozen_path)
        if got_self != expected_self:
            failures.append(
                f"frozen manifest file sha256 mismatch (sidecar {expected_self}, got {got_self})"
            )

    # Git / schema metadata (git may advance after freeze — record mismatch as failure only if
    # manifest claims a sha and we are verifying claim-bearing content; git_sha drift alone is
    # warned but claim-bearing hashes are authoritative. Spec: verify git/frozen metadata —
    # we require schema_version match and freeze timestamp present.)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        failures.append(
            f"schema_version mismatch: {manifest.get('schema_version')!r} != {SCHEMA_VERSION!r}"
        )
    if not manifest.get("freeze_timestamp_utc") and not manifest.get("frozen_at"):
        failures.append("freeze_timestamp_utc missing")

    # Extractor
    ext = manifest.get("extractor") or {}
    _expect_file_hash(
        root,
        ext.get("extractor_source_path") or EXTRACTOR_SOURCES[0],
        ext.get("extractor_source_sha256"),
        failures,
        "extractor",
    )
    for rel, expected in (ext.get("helper_module_sha256") or {}).items():
        _expect_file_hash(root, rel, expected, failures, "extractor_helper")

    # Ontology
    for rel, expected in ((manifest.get("ontology") or {}).get("files_sha256") or {}).items():
        _expect_file_hash(root, rel, expected, failures, "ontology")

    # Fingerprints
    for entry in manifest.get("fingerprints") or []:
        _expect_file_hash(root, entry.get("path"), entry.get("sha256"), failures, "fingerprint")

    # Graph scoring sources + weights
    gs = manifest.get("graph_scoring") or {}
    for rel, expected in (gs.get("sources_sha256") or {}).items():
        _expect_file_hash(root, rel, expected, failures, "graph_scoring")
    frozen_w = gs.get("graph_weights") or {}
    # Also compare against current selection artifact if present
    sel = _load_json(root / "results/isef2027/validation/external_dev_method_selection.json") or {}
    cur_w = (sel.get("graph_weight_selection") or {}).get("selected") or {}
    if frozen_w:
        for k in ("typed_weight", "hungarian_weight"):
            if k in frozen_w and k in cur_w and float(frozen_w[k]) != float(cur_w[k]):
                failures.append(
                    f"graph_weight {k} changed: frozen={frozen_w[k]} current_selection={cur_w[k]}"
                )
        # Embedded weights must match development_selection_result
        dsr_w = ((manifest.get("development_selection_result") or {}).get("graph_weights") or {})
        for k in ("typed_weight", "hungarian_weight"):
            if k in frozen_w and k in dsr_w and float(frozen_w[k]) != float(dsr_w[k]):
                failures.append(f"internal graph_weight inconsistency on {k}")

    # Preprocessing
    for rel, expected in ((manifest.get("preprocessing") or {}).get("sources_sha256") or {}).items():
        _expect_file_hash(root, rel, expected, failures, "preprocessing")

    # Student artifacts
    stud = manifest.get("student_scientific_artifacts") or {}
    _expect_file_hash(
        root,
        stud.get("fingerprint_decisions_path"),
        stud.get("fingerprint_decisions_sha256"),
        failures,
        "student_fingerprint_decisions",
    )
    _expect_file_hash(
        root,
        stud.get("student_gold_path"),
        stud.get("student_gold_sha256"),
        failures,
        "student_gold",
    )
    _expect_file_hash(
        root,
        stud.get("extractor_acceptance_criterion_path"),
        stud.get("extractor_acceptance_criterion_sha256"),
        failures,
        "extractor_criterion",
    )
    _expect_file_hash(
        root,
        stud.get("final_validation_success_criterion_path"),
        stud.get("final_validation_success_criterion_sha256"),
        failures,
        "success_criterion",
    )
    # Exact success criterion object match
    paths = review_paths(root)
    cur_suc = _load_json(paths["success_criterion"])
    frozen_suc = manifest.get("final_validation_criterion") or stud.get("success_criterion_object")
    if frozen_suc is not None and cur_suc != frozen_suc:
        failures.append("final_validation_success_criterion object changed after freeze")

    # Corpus / source-family rules
    for rel, expected in ((manifest.get("corpus_development_state") or {}).get("files_sha256") or {}).items():
        _expect_file_hash(root, rel, expected, failures, "corpus_development")

    # Statistical sources
    for rel, expected in ((manifest.get("statistical_method") or {}).get("sources_sha256") or {}).items():
        _expect_file_hash(root, rel, expected, failures, "statistical_method")

    # Development selection artifact
    dsr = manifest.get("development_selection_result") or {}
    _expect_file_hash(
        root,
        dsr.get("artifact"),
        dsr.get("artifact_sha256"),
        failures,
        "development_selection",
    )

    # Ancient confirmatory lock (independent)
    conf = verify_ancient_confirmatory_lock(root)
    if not conf.get("ok"):
        failures.append(
            "ancient_confirmatory_lock: " + "; ".join(conf.get("failing_invariants") or ["failed"])
        )

    ok = len(failures) == 0
    return {
        "status": "FROZEN_METHOD_INTEGRITY_OK" if ok else "FROZEN_METHOD_INTEGRITY_FAILURE",
        "ok": ok,
        "failures": failures,
        "git_sha_frozen": manifest.get("git_sha"),
        "git_sha_current": _git_sha(root),
        "ancient_confirmatory": conf.get("status_label"),
        "manifest_path": FROZEN_REL,
    }


def frozen_manifest_categories() -> list[str]:
    return [
        "repository_state",
        "extractor",
        "ontology",
        "fingerprints",
        "graph_scoring",
        "preprocessing",
        "student_scientific_artifacts",
        "corpus_development_state",
        "statistical_method",
        "development_selection_result",
        "final_validation_criterion",
        "ancient_confirmatory_lock_verified_at_check",
    ]
