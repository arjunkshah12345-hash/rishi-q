"""Metadata-only confirmatory corpus candidate inventory (NO scoring)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_confirmatory_candidate_manifest(root: Path) -> dict[str, Any]:
    """Inventory candidate works. Does not read sealed payloads for physics features."""
    candidates = [
        {
            "candidate_id": "cand-upanishads-paramananda-pd",
            "work": "Upanishads (Paramananda PD translation)",
            "civilization": "Indian",
            "school": "Upanishadic",
            "author": "various",
            "approximate_date": "classical_upanishadic_core_uncertain_range",
            "subject_domain": "metaphysics_natural_philosophy_mixed",
            "genre": "scriptural_philosophical",
            "language": "English_translation",
            "translation": "Paramananda",
            "translator_year": "1919_approx",
            "license_status": "public_domain",
            "full_work_available": True,
            "path_if_local": "corpus/raw/pd/upanishads_paramananda_3283.txt",
            "estimated_usable_passages": "UNKNOWN_REQUIRES_SEGMENTATION",
            "role_candidate": "target_or_within_india_comparator",
            "matching_variables": ["era", "genre", "length_band"],
            "contamination_status": "FILE_ON_DISK_HASH_RESERVED_UNSCORED",
            "seen_in_development_scoring": False,
            "independent_work_unit": True,
            "notes": "Do not score for confirmatory QS during v2 method work.",
        },
        {
            "candidate_id": "cand-sbe-hold",
            "work": "Sacred Books of the East (PD dump)",
            "civilization": "Indian_mixed",
            "school": "mixed",
            "author": "various",
            "approximate_date": "mixed",
            "subject_domain": "mixed",
            "genre": "anthology",
            "language": "English_translation",
            "translation": "various",
            "translator_year": "mixed",
            "license_status": "public_domain",
            "full_work_available": True,
            "path_if_local": "corpus/raw/pd/sacred_books_east_12894.txt",
            "estimated_usable_passages": "UNKNOWN_REQUIRES_SECTION_FILTER",
            "role_candidate": "hold_until_filter",
            "matching_variables": [],
            "contamination_status": "UNFILTERED_NOT_PRIMARY",
            "seen_in_development_scoring": False,
            "independent_work_unit": False,
            "notes": "Anthology ≠ one independent work.",
        },
        {
            "candidate_id": "cand-aristotle-physics-toacquire",
            "work": "Aristotle Physics (English PD edition)",
            "civilization": "Greek",
            "school": "Aristotelian",
            "author": "Aristotle",
            "approximate_date": "4th_c_BCE",
            "subject_domain": "natural_philosophy",
            "genre": "treatise",
            "language": "English_translation",
            "translation": "TO_ACQUIRE",
            "translator_year": "UNKNOWN",
            "license_status": "expect_public_domain_edition",
            "full_work_available": False,
            "path_if_local": "",
            "estimated_usable_passages": "UNKNOWN",
            "role_candidate": "primary_control",
            "matching_variables": ["natural_philosophy", "era_band", "length"],
            "contamination_status": "NOT_IN_DEV",
            "seen_in_development_scoring": False,
            "independent_work_unit": True,
            "notes": "Required matched control family member.",
        },
        {
            "candidate_id": "cand-epicurus-letters-toacquire",
            "work": "Epicurus letters / Principal Doctrines (PD)",
            "civilization": "Greek",
            "school": "Epicurean",
            "author": "Epicurus",
            "approximate_date": "3rd_c_BCE",
            "subject_domain": "natural_philosophy_atomism",
            "genre": "letters_doctrines",
            "language": "English_translation",
            "translation": "TO_ACQUIRE",
            "translator_year": "UNKNOWN",
            "license_status": "expect_public_domain_edition",
            "full_work_available": False,
            "path_if_local": "",
            "estimated_usable_passages": "UNKNOWN",
            "role_candidate": "primary_control",
            "matching_variables": ["atomism", "natural_philosophy"],
            "contamination_status": "NOT_IN_DEV",
            "seen_in_development_scoring": False,
            "independent_work_unit": True,
            "notes": "Lucretius PD already DEV-contaminated — cannot count as confirmatory work.",
        },
        {
            "candidate_id": "cand-nyaya-toacquire",
            "work": "Nyāya natural-philosophy sections",
            "civilization": "Indian",
            "school": "Nyaya",
            "author": "various",
            "approximate_date": "classical",
            "subject_domain": "epistemology_ontology",
            "genre": "sutra_bhasya",
            "language": "Sanskrit_or_PD_English",
            "translation": "TO_ACQUIRE",
            "translator_year": "UNKNOWN",
            "license_status": "UNKNOWN",
            "full_work_available": False,
            "path_if_local": "",
            "estimated_usable_passages": "UNKNOWN",
            "role_candidate": "target_or_within_india_control",
            "matching_variables": ["Indian_school", "philosophical_treatise"],
            "contamination_status": "NOT_IN_DEV",
            "seen_in_development_scoring": False,
            "independent_work_unit": True,
            "notes": "",
        },
        {
            "candidate_id": "cand-samkhya-toacquire",
            "work": "Sāṃkhya Kārikā / natural philosophy sections",
            "civilization": "Indian",
            "school": "Samkhya",
            "author": "Ishvarakrishna_traditionally",
            "approximate_date": "classical",
            "subject_domain": "dualist_cosmology",
            "genre": "karika",
            "language": "Sanskrit_or_PD_English",
            "translation": "TO_ACQUIRE",
            "translator_year": "UNKNOWN",
            "license_status": "UNKNOWN",
            "full_work_available": False,
            "path_if_local": "",
            "estimated_usable_passages": "UNKNOWN",
            "role_candidate": "target_or_within_india_control",
            "matching_variables": ["Indian_school"],
            "contamination_status": "NOT_IN_DEV",
            "seen_in_development_scoring": False,
            "independent_work_unit": True,
            "notes": "",
        },
        # Contaminated DEV exemplars — listed for exclusion clarity
        {
            "candidate_id": "exclude-dev-lucretius",
            "work": "Lucretius De Rerum Natura (PD used in DEV)",
            "civilization": "Greek_Roman",
            "school": "Epicurean",
            "role_candidate": "EXCLUDE_CONFIRMATORY",
            "seen_in_development_scoring": True,
            "independent_work_unit": True,
            "contamination_status": "DEV_CONTAMINATED",
            "notes": "Strong control family exemplar for matching only.",
        },
        {
            "candidate_id": "exclude-dev-timaeus",
            "work": "Plato Timaeus (PD used in DEV)",
            "civilization": "Greek",
            "school": "Platonic",
            "role_candidate": "EXCLUDE_CONFIRMATORY",
            "seen_in_development_scoring": True,
            "independent_work_unit": True,
            "contamination_status": "DEV_CONTAMINATED",
        },
        {
            "candidate_id": "exclude-dev-vaisesika",
            "work": "Vaiśeṣika Sūtra GRETIL (DEV)",
            "civilization": "Indian",
            "school": "Vaisesika",
            "role_candidate": "EXCLUDE_CONFIRMATORY",
            "seen_in_development_scoring": True,
            "independent_work_unit": True,
            "contamination_status": "DEV_CONTAMINATED",
        },
        {
            "candidate_id": "exclude-dev-prasastapada",
            "work": "Praśastapāda PDS GRETIL (DEV)",
            "civilization": "Indian",
            "school": "Vaisesika",
            "role_candidate": "EXCLUDE_CONFIRMATORY",
            "seen_in_development_scoring": True,
            "independent_work_unit": True,
            "contamination_status": "DEV_CONTAMINATED",
        },
    ]

    usable_target = [
        c
        for c in candidates
        if c.get("role_candidate") in {"target_or_within_india_comparator", "target_or_within_india_control"}
        and c.get("contamination_status") not in {"DEV_CONTAMINATED", "UNFILTERED_NOT_PRIMARY"}
        and c.get("independent_work_unit") is True
    ]
    usable_control = [
        c
        for c in candidates
        if c.get("role_candidate") == "primary_control" and c.get("independent_work_unit") is True
    ]

    payload = {
        "manifest_id": "ISEF2027-CONFIRMATORY-CANDIDATES-v2",
        "evidence_class": "METADATA_ONLY",
        "scored": False,
        "candidates": candidates,
        "feasibility": {
            "independent_target_side_candidates": len(usable_target),
            "independent_primary_control_candidates": len(usable_control),
            "available_now_on_disk_unscored": sum(1 for c in candidates if c.get("path_if_local")),
            "to_acquire": sum(1 for c in candidates if c.get("translation") == "TO_ACQUIRE"),
            "assessment": (
                "Far below any 20-works-per-arm target. Do not fabricate independence by "
                "splitting one work into fake works. Acquire more matched PD treatises first."
            ),
            "v1_n20_realistic_with_current_inventory": False,
        },
        "hierarchy_note": "Inference unit is work-level clustering of passages — never treat passages as independent works.",
    }
    out = root / "artifacts/isef2027/confirmatory_candidate_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
