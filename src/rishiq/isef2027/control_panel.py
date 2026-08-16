"""Expand control panel with concrete PD source file mappings (still student-approved)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


def build_control_panel_inventory(root: Path) -> dict:
    pd_dir = root / "corpus/raw/pd"
    files = sorted(p.name for p in pd_dir.glob("*.txt")) if pd_dir.exists() else []
    # Map known PD files to candidate families
    mapping = {
        "lucretius_785.txt": {
            "family": "greek_atomist_epicurean",
            "work": "Lucretius De Rerum Natura (PD)",
            "strength": "strong_natural_philosophy",
        },
        "plato_timaeus_1572.txt": {
            "family": "greek_platonic_aristotelian",
            "work": "Plato Timaeus (PD)",
            "strength": "strong_cosmology",
        },
        "taoteching_216.txt": {
            "family": "chinese_natural_philosophy",
            "work": "Dao De Jing (PD)",
            "strength": "weak_as_physics_control",
        },
        "dhammapada_2017.txt": {
            "family": "buddhist_philosophical",
            "work": "Dhammapada (PD)",
            "strength": "weak_ethics_verse",
        },
        "upanishads_paramananda_3283.txt": {
            "family": "other_indian_schools",
            "work": "Upanishads PD translation",
            "strength": "mixed_metaphysics_not_automatic_target",
        },
        "sacred_books_east_12894.txt": {
            "family": "other_indian_schools",
            "work": "Sacred Books of the East excerpt (PD)",
            "strength": "mixed_needs_filtering",
        },
    }
    inventory = []
    for fn in files:
        meta = mapping.get(fn, {"family": "unclassified", "work": fn, "strength": "unknown"})
        p = pd_dir / fn
        inventory.append(
            {
                "file": fn,
                "bytes": p.stat().st_size if p.exists() else 0,
                **meta,
                "student_decision": "PENDING",
                "path": f"corpus/raw/pd/{fn}",
            }
        )

    # Also list gretil primary
    gretil = []
    for fn in ("vaisesika_sutra_gretil.txt", "prasastapada_gretil.txt"):
        p = root / "corpus/development" / fn
        if p.exists():
            gretil.append(
                {
                    "file": fn,
                    "bytes": p.stat().st_size,
                    "role": "development_primary_or_commentary",
                    "path": f"corpus/development/{fn}",
                    "student_decision": "IN_DEV_FREEZE",
                }
            )

    payload = {
        "status": "INVENTORY_FOR_STUDENT_APPROVAL",
        "pd_controls": inventory,
        "gretil_dev": gretil,
        "hard_rules": [
            "Do not auto-include weak ethics-only panels as primary confirmatory controls.",
            "Prefer matched natural-philosophy works.",
            "Document inclusion/exclusion reasons in split_manifest.",
        ],
    }
    out = root / "artifacts/isef2027/control_panel_inventory.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Refresh YAML decisions file with concrete files listed
    yml = root / "artifacts/isef2027/control_panel_candidates.yaml"
    if yml.exists():
        data = yaml.safe_load(yml.read_text()) or {}
        data["concrete_pd_files"] = inventory
        data["status"] = "CANDIDATE_LIST_WITH_FILE_INVENTORY"
        yml.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return payload
