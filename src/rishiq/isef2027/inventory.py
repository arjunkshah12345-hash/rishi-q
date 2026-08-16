"""Machine-readable inventory of what exists vs proposed."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def build_inventory(root: Path) -> dict:
    root = root.resolve()

    def exists(rel: str) -> bool:
        return (root / rel).exists()

    implemented = {
        "ontology_v0_1": exists("ontology/ontology_v0.1.yaml"),
        "physics_fingerprints_6": exists("ontology/physics_fingerprints/index.yaml"),
        "weighted_jaccard_similarity": exists("src/rishiq/similarity/__init__.py"),
        "cluster_bootstrap_permutation": exists("src/rishiq/statistics/__init__.py"),
        "leakage_audit_basic": exists("src/rishiq/leakage/__init__.py"),
        "blinding": exists("src/rishiq/blinding/__init__.py"),
        "masking": exists("src/rishiq/masking/__init__.py"),
        "confirmatory_firewall": exists("src/rishiq/experiments/firewall.py"),
        "discovery_engine": exists("scripts/run_discovery_engine.py"),
        "human_validation_scaffold": exists("human_validation/README.md"),
        "isef_flagship_exploratory": exists(
            "results/exploratory/isef_akasa_sound_field/summary.json"
        ),
        "chatgpt_handoff_pack": exists("chatgpt-handoff/data/FACTS.json"),
        "cli_rishiq": exists("src/rishiq/cli.py"),
    }

    proposed_or_new = {
        "dev_calibration_sealed_splits": "isef2027",
        "typed_concept_graph": "isef2027",
        "graph_similarity_methods": "isef2027",
        "lexical_embedding_baselines": "isef2027",
        "theory_fingerprint_atomistic": "isef2027",
        "experiment_registry": "isef2027",
        "adversarial_battery_v2": "isef2027",
        "matched_control_manifest": "isef2027",
        "reproduce_cli": "isef2027",
        "ai_usage_log": "isef2027",
        "gap_audit": "isef2027",
        "animated_3d_visuals": "isef2027",
        "human_reliability_stats_ready": "isef2027_no_data_collection",
        "confirmatory_unlock": "BLOCKED_student_prereg",
    }

    status = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": str(root),
        "implemented_modules": implemented,
        "n_implemented_true": sum(1 for v in implemented.values() if v),
        "upgrade_targets": proposed_or_new,
        "exploratory_status": "MUST_REMAIN_EXPLORATORY",
        "confirmatory_status": "LOCKED",
        "notes": [
            "Existing ISEF-AKASA-SOUND-FIELD numbers are development-only.",
            "Fair-coin P=1/64 is exploratory descriptive null, not confirmatory inference.",
            "Do not open sealed confirmatory texts during development.",
        ],
    }
    return status


def write_inventory(root: Path, out: Path | None = None) -> Path:
    out = out or (root / "artifacts/isef2027/REPO_INVENTORY.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = build_inventory(root)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out
