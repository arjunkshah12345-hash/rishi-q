"""Real multi-translation pair infrastructure (metadata + scoring hooks).

Synthetic translator-year demo remains separate under SOFTWARE_DEMO.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance


def write_translation_pair_schema(root: Path) -> Path:
    schema = {
        "unit": "same_underlying_passage_across_translations",
        "fields": [
            "source_passage_id",
            "work_id",
            "language_source",
            "translation_id",
            "translator",
            "translator_year",
            "literal_vs_free",
            "edition",
            "source_url",
            "text",
            "lexical_modernization_score",
            "structural_scores_by_theory",
            "masked_structural_scores_by_theory",
        ],
        "analysis": "paired_or_hierarchical_by_source_passage_id",
        "unknown_policy": "leave null; do not infer style from vibes",
    }
    out = root / "protocol/isef2027_v2/translation_pairs_SCHEMA.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    return out


def write_translation_pair_manifest_stub(root: Path) -> dict[str, Any]:
    """Seed manifest with known multi-translation opportunities — texts not scored here."""
    pairs = [
        {
            "work_id": "bhagavad_gita",
            "note": "Many English translations across eras; acquire PD-only editions",
            "status": "TO_ACQUIRE_PD_EDITIONS",
            "source_passage_ids_aligned": False,
        },
        {
            "work_id": "upanishads_select",
            "note": "Multiple PD translations exist; align by verse ID before scoring",
            "status": "PARTIAL_LOCAL_ONE_TRANSLATION_ONLY",
            "local_path": "corpus/raw/pd/upanishads_paramananda_3283.txt",
            "source_passage_ids_aligned": False,
        },
        {
            "work_id": "lucretius",
            "note": "DEV contaminated for confirmatory; usable for translation-shift DEVELOPMENT study only",
            "status": "DEV_ONLY_TRANSLATION_STUDY_CANDIDATE",
            "source_passage_ids_aligned": False,
        },
    ]
    payload = attach_provenance(
        {
            "manifest_id": "ISEF2027-TRANSLATION-PAIRS-v2",
            "n_works": len(pairs),
            "pairs": pairs,
            "scored": False,
            "synthetic_demo_separate_file": "results/isef2027/dev/translation_battery.json",
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.METADATA_ONLY,
            synthetic=False,
            real_text=False,
            phase="development",
            source_split="metadata",
            method_version="translation_pairs_v2",
            notes="Infrastructure only; no structural scores computed on confirmatory sealed data.",
        ),
    )
    out = root / "artifacts/isef2027/translation_pair_manifest.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_translation_pair_schema(root)
    return payload
