"""Freeze exploratory artifacts with content hashes (pre-upgrade snapshot)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# Paths relative to repo root — development/exploratory freeze set
FREEZE_PATHS = [
    "FLAGSHIP_FINDING.md",
    "HEADLINE_FINDING.md",
    "PROOF_HUNT.md",
    "ontology/ontology_v0.1.yaml",
    "ontology/physics_fingerprints/index.yaml",
    "ontology/physics_fingerprints/newtonian.yaml",
    "ontology/physics_fingerprints/classical_em.yaml",
    "ontology/physics_fingerprints/thermodynamics.yaml",
    "ontology/physics_fingerprints/relativity.yaml",
    "ontology/physics_fingerprints/quantum_mechanics.yaml",
    "ontology/physics_fingerprints/quantum_field_theory.yaml",
    "configs/physics_vocab_v0.1.json",
    "configs/development.yaml",
    "prompts/ann-v0.1.yaml",
    "prompts/prop-v0.1.yaml",
    "scripts/run_isef_akasa_sound_field.py",
    "scripts/run_isef_expansion_v2.py",
    "scripts/make_isef_extra_figures.py",
    "scripts/run_discovery_engine.py",
    "src/rishiq/similarity/__init__.py",
    "src/rishiq/statistics/__init__.py",
    "src/rishiq/leakage/__init__.py",
    "src/rishiq/blinding/__init__.py",
    "src/rishiq/masking/__init__.py",
    "src/rishiq/experiments/firewall.py",
    "results/exploratory/isef_akasa_sound_field/summary.json",
    "results/exploratory/isef_akasa_sound_field/expansion_v2.json",
    "results/exploratory/isef_akasa_sound_field/VERDICT.md",
    "results/exploratory/isef_akasa_sound_field/NOVELTY.md",
    "chatgpt-handoff/data/FACTS.json",
    "chatgpt-handoff/tables/scorecard.csv",
    "chatgpt-handoff/tables/R_six_tradition_vectors.csv",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze_dev(root: Path) -> Path:
    root = root.resolve()
    files = []
    missing = []
    for rel in FREEZE_PATHS:
        p = root / rel
        if not p.exists():
            missing.append(rel)
            continue
        files.append(
            {
                "path": rel,
                "sha256": sha256_file(p),
                "bytes": p.stat().st_size,
            }
        )

    # Feature definitions snapshot from FACTS / expansion if present
    feature_defs = {
        "R1": "Pervasive non-atomic medium/substance",
        "R2": "Sound specially tied to that medium",
        "R3": "Light/heat treated as different carrier than sound-medium",
        "R4": "Atomic/corpuscular ordinary matter",
        "R5": "Medium itself not a dynamical EM field",
        "R6": "Maxwell-style unified electromagnetism",
    }

    payload = {
        "freeze_id": "ISEF2027-DEV-FREEZE-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "EXPLORATORY_FROZEN",
        "warning": (
            "These hashes record what was known BEFORE ISEF2027 upgrades. "
            "Do not revise these files to strengthen claims. "
            "Fair-coin P=1/64 is NOT confirmatory inference."
        ),
        "n_files_hashed": len(files),
        "n_missing": len(missing),
        "missing": missing,
        "files": files,
        "feature_definitions_r1_r6": feature_defs,
        "headline_exploratory_numbers_reference": {
            "kanada_attestation": "9/9",
            "prasastapada_replication": "6/6",
            "maxwell_hits": "0/5",
            "fair_coin_null_P": 0.015625,
            "note": "exploratory only; see FACTS.json hash above",
        },
    }

    out = root / "artifacts/isef2027/dev_freeze_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Immutable copy note
    note = root / "artifacts/isef2027/DEV_FREEZE_README.md"
    note.write_text(
        "# Development freeze\n\n"
        "See `dev_freeze_manifest.json`.\n\n"
        "Exploratory flagship results are frozen. New work lives under "
        "`configs/isef2027.yaml`, `src/rishiq/isef2027/`, and "
        "`results/isef2027/`.\n",
        encoding="utf-8",
    )
    return out
