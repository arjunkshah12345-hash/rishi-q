"""Calibration adversarial + power scaffolding."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from rishiq.isef2027.adversarial import mask_vocabulary, run_adversarial_battery
from rishiq.isef2027.baselines import mean_tfidf_similarity
from rishiq.isef2027.inference import leave_one_work_out, work_level_permutation
from rishiq.isef2027.scrub import scrub_text


def _safe_power(**kwargs) -> dict[str, Any]:
    try:
        from rishiq.statistics import approximate_power_two_groups

        return {"method": "approximate_power_two_groups", **approximate_power_two_groups(**kwargs)}
    except Exception:
        # Minimal local approximation
        effect = float(kwargs.get("effect", 0.2))
        n_per = int(kwargs.get("n_per_group", 30))
        # toy: larger n / effect → higher pseudo-power
        p = float(1 / (1 + np.exp(-(n_per * effect * 8 - 2))))
        return {
            "method": "logistic_toy_power_curve",
            "effect": effect,
            "n_per_group": n_per,
            "approx_power": p,
            "note": "Placeholder power curve until student freezes ICC/variance from calibration.",
        }


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
    scrubbed = []
    for t in texts:
        r = scrub_text(t)
        scrubbed.append(r.text)
        scrub_stats.append({"n_replacements": r.n_replacements, "patterns": r.patterns_hit})

    # Feature proxy vectors: modernization density
    def prox(t: str) -> dict[str, float]:
        return {"len": float(len(t.split())), "scrub_hits": float(scrub_text(t).n_replacements)}

    vectors = [prox(t) for t in texts] if texts else [{"len": 1.0, "scrub_hits": 0.0}]
    adv = run_adversarial_battery(
        texts=texts or ["placeholder continuum medium sound mark"],
        feature_vectors=vectors,
        tradition_labels=traditions or ["x"],
        seed=seed,
    )

    # Masked vs raw self-similarity drop
    if len(texts) >= 4:
        raw_sim = mean_tfidf_similarity(texts[:20], texts[20:40] if len(texts) > 40 else texts[:20])
        masked = [mask_vocabulary(t) for t in texts]
        masked_sim = mean_tfidf_similarity(masked[:20], masked[20:40] if len(masked) > 40 else masked[:20])
    else:
        raw_sim = masked_sim = float("nan")

    # Synthetic clustered scores for LOO / permutation demos on "calibration-shaped" sizes
    n = max(len(set(works)), 8)
    t_means = {f"W{i}": float(rng.normal(0.42, 0.05)) for i in range(n // 2)}
    c_means = {f"C{i}": float(rng.normal(0.38, 0.05)) for i in range(n - n // 2)}
    perm = work_level_permutation(t_means, c_means, seed=seed)

    # Fake passage-level for LOO API
    scores = []
    wlist = []
    roles = []
    for w, m in t_means.items():
        for _ in range(3):
            scores.append(m + float(rng.normal(0, 0.01)))
            wlist.append(w)
            roles.append("target")
    for w, m in c_means.items():
        for _ in range(3):
            scores.append(m + float(rng.normal(0, 0.01)))
            wlist.append(w)
            roles.append("control")
    loo = leave_one_work_out(scores, wlist, roles)

    power = {
        "grid": [
            _safe_power(effect=e, n_per_group=n)
            for e in (0.05, 0.1, 0.2, 0.3)
            for n in (20, 40, 80)
        ]
    }

    payload = {
        "battery_id": "ISEF2027-CAL-ADV-v1",
        "seed": seed,
        "n_texts": len(texts),
        "scrub_mean_replacements": float(np.mean([s["n_replacements"] for s in scrub_stats])) if scrub_stats else 0.0,
        "scrub_pattern_freq": {
            k: int(sum(1 for s in scrub_stats if k in s["patterns"]))
            for k in sorted({p for s in scrub_stats for p in s["patterns"]})
        },
        "adversarial": adv,
        "tfidf_raw_sim": raw_sim,
        "tfidf_masked_sim": masked_sim,
        "work_level_permutation": perm,
        "leave_one_work_out_deltas": loo,
        "power_scaffold": power,
        "warnings": [
            "Calibration adversarial outputs are diagnostics, not confirmatory p-values.",
            "Power scaffold requires student-frozen ICC/variance before prereg sample size.",
        ],
    }
    out = root / "results/isef2027/dev/calibration_adversarial.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")
    return payload
