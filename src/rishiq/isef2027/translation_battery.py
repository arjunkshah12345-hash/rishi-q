"""Translation contamination and masking battery (development/calibration)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from rishiq.isef2027.adversarial import DEFAULT_MASK_TERMS, mask_vocabulary
from rishiq.isef2027.baselines import mean_tfidf_similarity
from rishiq.isef2027.benchmark import POSITIVE_PANELS, keyword_feature_proxy
from rishiq.isef2027.baselines import binary_vector_jaccard
from rishiq.fingerprints import load_all_fingerprints


def _modernization_score(text: str) -> float:
    """Heuristic density of modern physics lexicon (leakage proxy)."""
    t = text.lower()
    hits = sum(1 for w in DEFAULT_MASK_TERMS if re.search(rf"\b{re.escape(w)}\b", t))
    toks = max(len(t.split()), 1)
    return hits / toks


def translator_year_stratified_demo(seed: int = 42) -> dict[str, Any]:
    """Synthetic strata: 'old' vs 'modern' wording of the same classical-EM ideas."""
    old = [
        "Light is a disturbance in the luminiferous ether obeying known electrical laws.",
        "Magnetic influence induces electrical tension in neighboring circuits.",
    ]
    modern = [
        "Light is a quantized electromagnetic field excitation in vacuum.",
        "Quantum vacuum fluctuations underlie electromagnetic induction phenomena.",
    ]
    years = [1880, 1890, 2015, 2020]
    texts = old + modern
    modern_flags = [0, 0, 1, 1]
    scores = [_modernization_score(t) for t in texts]
    # correlation year vs modernization score
    if np.std(years) > 0 and np.std(scores) > 0:
        corr = float(np.corrcoef(np.asarray(years, float), np.asarray(scores, float))[0, 1])
    else:
        corr = float("nan")
    return {
        "n": len(texts),
        "years": years,
        "modern_flags": modern_flags,
        "modernization_scores": scores,
        "corr_year_vs_modernization_lexicon": corr,
        "tfidf_old_vs_modern": mean_tfidf_similarity(old, modern),
        "note": "Synthetic illustration of translator-era leakage risk — not historical data.",
        "seed": seed,
    }


def masked_unmasked_theory_shift(root: Path) -> dict[str, Any]:
    fps = load_all_fingerprints(root / "ontology/physics_fingerprints")
    out = {}
    for tid, texts in POSITIVE_PANELS.items():
        if tid not in fps:
            continue
        raw = {}
        masked = {}
        for label, panel in (("raw", texts), ("masked", [mask_vocabulary(t) for t in texts])):
            vec = {}
            for t in panel:
                for k, v in keyword_feature_proxy(t).items():
                    vec[k] = max(vec.get(k, 0), v)
            scores = {
                k: binary_vector_jaccard(vec, {f: int(fp.features.get(f, 0)) for f in set(vec) | set(fp.features)})
                for k, fp in fps.items()
            }
            if label == "raw":
                raw = scores
            else:
                masked = scores
        out[tid] = {
            "raw_top1": max(raw, key=raw.get) if raw else None,
            "masked_top1": max(masked, key=masked.get) if masked else None,
            "raw_scores": raw,
            "masked_scores": masked,
            "top1_changed": (max(raw, key=raw.get) != max(masked, key=masked.get)) if raw and masked else None,
        }
    return out


def run_translation_battery(root: Path, seed: int = 42) -> dict[str, Any]:
    payload = {
        "battery_id": "ISEF2027-TRANSLATION-v1",
        "mask_terms": DEFAULT_MASK_TERMS,
        "translator_year_demo": translator_year_stratified_demo(seed=seed),
        "masked_unmasked_shift": masked_unmasked_theory_shift(root),
        "warnings": [
            "Requires real multi-translation corpora before confirmatory claims.",
            "Student must freeze mask list independently of Sanskrit–QM outcomes.",
        ],
    }
    # If PD passages exist, report modernization score by tradition (exploratory descriptive)
    pq = root / "corpus/development/pd_passages.parquet"
    if pq.exists():
        df = pd.read_parquet(pq)
        text_col = "translation" if "translation" in df.columns else "text"
        if text_col in df.columns and "tradition" in df.columns:
            rows = []
            for trad, g in df.groupby("tradition"):
                scores = [_modernization_score(str(t)) for t in g[text_col].head(80).tolist()]
                rows.append({"tradition": trad, "n": len(scores), "mean_modernization": float(np.mean(scores))})
            payload["pd_tradition_modernization_descriptive"] = rows

    out = root / "results/isef2027/dev/translation_battery.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
