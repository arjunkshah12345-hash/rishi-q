"""Upgraded adversarial battery using real method outputs where available."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from rishiq.isef2027.adversarial import mask_vocabulary, run_adversarial_battery
from rishiq.isef2027.baselines import mean_tfidf_similarity
from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance
from rishiq.isef2027.inference import leave_one_work_out, work_level_permutation
from rishiq.isef2027.power_hier import PowerAssumptions, power_grid
from rishiq.isef2027.scrub import scrub_text


def run_calibration_batteries(root: Path, seed: int = 42) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    pq = root / "corpus/development/pd_passages.parquet"
    texts: list[str] = []
    traditions: list[str] = []
    works: list[str] = []
    if pq.exists():
        df = pd.read_parquet(pq).head(120)
        text_col = "translation" if "translation" in df.columns else "text"
        for _, row in df.iterrows():
            texts.append(str(row.get(text_col, "")))
            traditions.append(str(row.get("tradition", "unk")))
            works.append(str(row.get("work", row.get("passage_id", "unk"))))

    scrub_stats = []
    for t in texts:
        r = scrub_text(t)
        scrub_stats.append({"n_replacements": r.n_replacements, "patterns": r.patterns_hit})

    # Prefer ontology-like scores if validation outputs exist; else length-free TF-IDF self-sim proxy
    def score_proxy(t: str) -> float:
        # modernization density — not confirmatory QS
        modern = sum(w in t.lower() for w in ("energy", "field", "quantum", "vibration", "wave"))
        return float(modern) / max(len(t.split()), 1)

    vectors = [{"modern_density": score_proxy(t), "scrub_hits": float(scrub_text(t).n_replacements)} for t in texts] or [
        {"modern_density": 0.0, "scrub_hits": 0.0}
    ]
    adv = run_adversarial_battery(
        texts=texts or ["placeholder continuum medium sound mark"],
        feature_vectors=vectors,
        tradition_labels=traditions or ["x"],
        seed=seed,
    )

    if len(texts) >= 4:
        raw_sim = mean_tfidf_similarity(texts[:20], texts[20:40] if len(texts) > 40 else texts[:20])
        masked = [mask_vocabulary(t) for t in texts]
        masked_sim = mean_tfidf_similarity(masked[:20], masked[20:40] if len(masked) > 40 else masked[:20])
    else:
        raw_sim = masked_sim = float("nan")

    # Work-level battery on modern_density aggregates (DEVELOPMENT_ANALYSIS on real PD text)
    work_scores: dict[str, list[float]] = {}
    for w, t in zip(works, texts):
        work_scores.setdefault(w, []).append(score_proxy(t))
    work_means = {w: float(np.mean(v)) for w, v in work_scores.items() if v}
    # Split works alphabetically into pseudo arms for LOO/permutation stress test only
    keys = sorted(work_means)
    mid = max(len(keys) // 2, 1)
    t_means = {k: work_means[k] for k in keys[:mid]}
    c_means = {k: work_means[k] for k in keys[mid:]} or {"C0": 0.0}
    perm = work_level_permutation(t_means, c_means, seed=seed) if len(t_means) >= 2 and len(c_means) >= 1 else {}

    scores = []
    wlist = []
    roles = []
    for w, m in t_means.items():
        scores.append(m)
        wlist.append(w)
        roles.append("target")
    for w, m in c_means.items():
        scores.append(m)
        wlist.append(w)
        roles.append("control")
    loo = leave_one_work_out(scores, wlist, roles) if scores else {}

    # OLD toy power retained but labeled
    toy_power = {
        "label": "SOFTWARE_DEMO_NOT_SAMPLE_SIZE_EVIDENCE",
        "method": "logistic_toy_power_curve",
        "warning": "Do not use for confirmatory N. See power_hier_v2.",
        "grid": [],
    }
    for e in (0.05, 0.1, 0.2):
        for n in (20, 40):
            p = float(1 / (1 + np.exp(-(n * e * 8 - 2))))
            toy_power["grid"].append(
                {
                    "effect": e,
                    "n_per_group": n,
                    "approx_power": p,
                    "evidence_class": "SOFTWARE_DEMO",
                }
            )

    # Real hierarchical power grid with UNKNOWN variance
    hier = power_grid(
        effects=[0.05, 0.10, 0.15],
        works_grid=[6, 8, 12, 20],
        passages_grid=[5, 10],
        between_work_sd="UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE",
        within_work_sd="UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE",
        n_sim=80,
        seed=seed,
    )

    payload = attach_provenance(
        {
            "battery_id": "ISEF2027-CAL-ADV-v2",
            "seed": seed,
            "n_texts": len(texts),
            "scrub_mean_replacements": float(np.mean([s["n_replacements"] for s in scrub_stats]))
            if scrub_stats
            else 0.0,
            "adversarial": adv,
            "tests": {
                "length_corr_on_modern_density": adv.get("length_score_corr"),
                "vocabulary_masking_tfidf_raw": raw_sim,
                "vocabulary_masking_tfidf_masked": masked_sim,
                "work_level_permutation_on_modern_density": perm,
                "leave_one_work_out": loo,
                "random_label_permute_sample": adv.get("permuted_labels_sample"),
            },
            "toy_power_SOFTWARE_DEMO_NOT_SAMPLE_SIZE_EVIDENCE": toy_power,
            "hierarchical_power_v2": hier,
            "warnings": [
                "Adversarial outputs on modern_density are DEVELOPMENT diagnostics, not confirmatory p-values.",
                "Toy logistic power is SOFTWARE_DEMO_NOT_SAMPLE_SIZE_EVIDENCE.",
                "Hierarchical power uses UNKNOWN variance → not ready for sample-size freeze.",
            ],
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.DEVELOPMENT_ANALYSIS,
            synthetic=False,
            real_text=bool(texts),
            phase="calibration",
            source_split="calibration_or_dev_pd",
            method_version="cal_adv_v2",
        ),
    )
    out = root / "results/isef2027/dev/calibration_adversarial.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")
    return payload
