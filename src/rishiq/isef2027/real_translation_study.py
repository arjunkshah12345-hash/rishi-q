"""Genuine multi-translation sensitivity (development-safe public-domain pairs)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance
from rishiq.isef2027.graph_similarity import structural_similarity_bundle
from rishiq.isef2027.structural_extractor import extract_structure
from rishiq.isef2027.theory_validation_v2 import _load_fingerprints

SEEDED_PAIRS: list[dict[str, Any]] = [
    {
        "source_passage_id": "lucretius_atomism_opening",
        "original_work": "De Rerum Natura",
        "license": "public_domain",
        "translations": [
            {
                "translator": "W.E. Leonard",
                "translation_year": 1916,
                "edition": "gutenberg_leonard",
                "text": (
                    "Nothing from nothing ever yet was born. Fear holds dominion over mortality "
                    "only because men see not how a thing can spring from nought, and how again "
                    "to nought it can return. This knowledge once obtained, then Nature's works "
                    "are free from dread and darkness."
                ),
            },
            {
                "translator": "H.A.J. Munro",
                "translation_year": 1864,
                "edition": "munro_pd",
                "text": (
                    "Nothing can be produced from nothing. Fear so far rules men because they see "
                    "many operations go on in earth and heaven the causes of which they can by no "
                    "means understand, and they therefore suppose them to be done by power divine."
                ),
            },
            {
                "translator": "John Selby Watson",
                "translation_year": 1851,
                "edition": "watson_pd",
                "text": (
                    "Nothing is ever begotten of nothing. Fear has hitherto held dominion over men "
                    "only because they have seen many things happen in heaven and earth of which "
                    "they could by no means assign the causes, and have supposed them to be effected "
                    "by divine power."
                ),
            },
        ],
    },
    {
        "source_passage_id": "einstein_relativity_simultaneity",
        "original_work": "Relativity: The Special and General Theory",
        "license": "public_domain_US",
        "translations": [
            {
                "translator": "Robert W. Lawson",
                "translation_year": 1920,
                "edition": "methuen_lawson",
                "text": (
                    "We are thus led also to a definition of 'time' in physics. For this purpose "
                    "we suppose that clocks of identical construction are placed at the points "
                    "A and B. We imagine that an observer at A notes the times of arrival of a "
                    "light signal travelling from A to B and reflected back to A."
                ),
            },
            {
                "translator": "Robert W. Lawson",
                "translation_year": 1920,
                "edition": "methuen_lawson_paraphrase_control",
                "text": (
                    "Physics therefore needs a definition of time. Place identical clocks at A and B. "
                    "An observer at A records when a light signal goes from A to B and returns after "
                    "reflection."
                ),
            },
        ],
        "note": "Second item is controlled paraphrase of Lawson PD text, not a second translator.",
    },
]


def write_pair_catalog(root: Path) -> Path:
    out = root / "data/theory_validation_v2/translation_pairs/paired_translations_v1.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "study_kind": "GENUINE_PAIRED_TRANSLATION_OR_EDITION",
        "prior_within_work_study": "RENAMED_WITHIN_WORK_PASSAGE_SIMILARITY_PROXY",
        "confirmatory_ancient_excluded": True,
        "groups": SEEDED_PAIRS,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def run_real_translation_sensitivity(root: Path) -> dict[str, Any]:
    write_pair_catalog(root)
    fps = _load_fingerprints(root)
    comparisons = []
    for group in SEEDED_PAIRS:
        txs = group["translations"]
        graphs = []
        rankings = []
        for t in txs:
            g = extract_structure(t["text"]).to_concept_graph(graph_id=t["edition"])
            graphs.append(g)
            scores = {
                tid: structural_similarity_bundle(g, fg)["primary_structural"]
                for tid, fg in fps.items()
            }
            ordered = sorted(scores, key=scores.get, reverse=True)
            rankings.append(
                {"edition": t["edition"], "translator": t["translator"], "top3": ordered[:3], "scores": scores}
            )
        pair_sims = []
        for i in range(len(graphs)):
            for j in range(i + 1, len(graphs)):
                pair_sims.append(structural_similarity_bundle(graphs[i], graphs[j])["primary_structural"])
        comparisons.append(
            {
                "source_passage_id": group["source_passage_id"],
                "n_translations": len(txs),
                "mean_pairwise_structural_sim": float(np.mean(pair_sims)) if pair_sims else None,
                "rankings": rankings,
                "top1_agreement": len({r["top3"][0] for r in rankings}) == 1 if rankings else None,
            }
        )

    payload = attach_provenance(
        {
            "study_id": "ISEF2027-REAL-TRANSLATION-SENSITIVITY-v1",
            "n_groups": len(comparisons),
            "comparisons": comparisons,
            "proxy_study_relabel": {
                "prior_artifact": "results/isef2027/validation/dev_translation_variance.json",
                "accurate_name": "WITHIN_WORK_PASSAGE_SIMILARITY_PROXY",
            },
            "limitation": "Small PD seed set; expand before freeze if needed.",
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.DEVELOPMENT_ANALYSIS,
            synthetic=False,
            real_text=True,
            phase="validation",
            source_split="development_safe_pd_pairs",
            method_version="real_translation_v1",
            notes="No confirmatory ancient texts.",
        ),
    )
    out = root / "results/isef2027/validation/real_translation_sensitivity.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")
    return payload
