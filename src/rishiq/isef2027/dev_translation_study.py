"""Development-only translation variance study (not confirmatory).

Uses public-domain multi-edition material already in the external corpus
where the same work appears in development-eligible contexts. Does NOT
touch sealed confirmatory outcomes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance
from rishiq.isef2027.theory_validation_v2 import mask_giveaway_vocab


def run_dev_translation_variance_study(root: Path) -> dict[str, Any]:
    """Pair passages within the same work across different acquisition windows.

    Without multiple independent translators for the same chapter on disk,
    this reports within-work lexical / ranking variance as a lower bound on
    translator/edition sensitivity — labeled provisional.
    """
    path = root / "data/theory_validation_v2/passages/development.jsonl"
    if not path.exists():
        return {"status": "MISSING_DEV_CORPUS"}
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_work: dict[str, list[dict]] = {}
    for r in rows:
        by_work.setdefault(r["work_id"], []).append(r)

    pairs = []
    for work, items in by_work.items():
        if len(items) < 2:
            continue
        # Compare first two passages as edition/window proxy pairs
        a, b = items[0], items[1]
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        X = vec.fit_transform([a["text"], b["text"]]).toarray()
        na = X[0] / (np.linalg.norm(X[0]) + 1e-12)
        nb = X[1] / (np.linalg.norm(X[1]) + 1e-12)
        lex = float(na @ nb)
        ma, mb = mask_giveaway_vocab(a["text"]), mask_giveaway_vocab(b["text"])
        Xm = vec.fit_transform([ma, mb]).toarray()
        nam = Xm[0] / (np.linalg.norm(Xm[0]) + 1e-12)
        nbm = Xm[1] / (np.linalg.norm(Xm[1]) + 1e-12)
        lex_masked = float(nam @ nbm)
        pairs.append(
            {
                "work_id": work,
                "passage_a": a["passage_id"],
                "passage_b": b["passage_id"],
                "lexical_cosine": lex,
                "lexical_cosine_masked": lex_masked,
                "same_theory_label": a["theory_label"] == b["theory_label"],
                "note": "within_work_window_proxy_not_multi_translator_pair",
            }
        )

    payload = attach_provenance(
        {
            "study_id": "ISEF2027-DEV-TRANSLATION-VARIANCE-v1",
            "n_pairs": len(pairs),
            "mean_lexical_cosine": float(np.mean([p["lexical_cosine"] for p in pairs])) if pairs else None,
            "mean_lexical_cosine_masked": float(np.mean([p["lexical_cosine_masked"] for p in pairs])) if pairs else None,
            "pairs": pairs[:50],
            "limitation": (
                "True multi-translator PD pairs should replace this within-work proxy "
                "before confirmatory design freeze."
            ),
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.DEVELOPMENT_ANALYSIS,
            synthetic=False,
            real_text=True,
            phase="validation",
            source_split="development",
            method_version="dev_translation_variance_v1",
            notes="Confirmatory sealed texts unused.",
        ),
    )
    out = root / "results/isef2027/validation/dev_translation_variance.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
