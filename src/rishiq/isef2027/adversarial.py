"""Adversarial / falsification battery — designed to make hypotheses easy to fail."""

from __future__ import annotations

import re
from typing import Callable

import numpy as np


DEFAULT_MASK_TERMS = [
    "atom",
    "particle",
    "wave",
    "field",
    "energy",
    "quantum",
    "vibration",
    "ether",
    "aether",
    "space",
    "force",
]


def mask_vocabulary(text: str, terms: list[str] | None = None) -> str:
    terms = terms or DEFAULT_MASK_TERMS
    out = text
    for t in terms:
        out = re.sub(rf"\b{re.escape(t)}\b", "[MASK]", out, flags=re.I)
    return out


def feature_shuffle(vector: dict[str, float], rng: np.random.Generator) -> dict[str, float]:
    keys = list(vector.keys())
    vals = [vector[k] for k in keys]
    rng.shuffle(vals)
    return dict(zip(keys, vals))


def label_permute(labels: list[str], rng: np.random.Generator) -> list[str]:
    out = list(labels)
    rng.shuffle(out)
    return out


def leave_one_out_deltas(
    item_scores: dict[str, float],
    aggregate: Callable[[list[float]], float] | None = None,
) -> dict[str, float]:
    """Effect of removing each item on mean score."""
    agg = aggregate or (lambda xs: float(np.mean(xs)) if xs else 0.0)
    keys = list(item_scores.keys())
    full = agg(list(item_scores.values()))
    out = {}
    for k in keys:
        rest = [item_scores[x] for x in keys if x != k]
        out[k] = full - agg(rest)
    return out


def run_adversarial_battery(
    *,
    texts: list[str],
    feature_vectors: list[dict[str, float]],
    tradition_labels: list[str],
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    masked = [mask_vocabulary(t) for t in texts]
    shuffled = [feature_shuffle(v, rng) for v in feature_vectors]
    perm_labels = label_permute(tradition_labels, rng)

    # Length control: correlation of score proxy (vector sum) with length
    lengths = np.array([len(t.split()) for t in texts], dtype=float)
    proxies = np.array([sum(v.values()) for v in feature_vectors], dtype=float)
    if len(lengths) > 2 and np.std(lengths) > 0 and np.std(proxies) > 0:
        length_corr = float(np.corrcoef(lengths, proxies)[0, 1])
    else:
        length_corr = float("nan")

    return {
        "seed": seed,
        "n_texts": len(texts),
        "mask_terms": DEFAULT_MASK_TERMS,
        "masked_texts_sample": masked[:3],
        "n_feature_shuffles": len(shuffled),
        "permuted_labels_sample": perm_labels[:10],
        "length_score_corr": length_corr,
        "leave_one_out_tradition": leave_one_out_deltas(
            {lab: float(proxies[i]) for i, lab in enumerate(tradition_labels)}
            if len(tradition_labels) == len(proxies)
            else {f"i{i}": float(proxies[i]) for i in range(len(proxies))}
        ),
        "interpretation_note": (
            "Battery outputs are diagnostics for development/calibration. "
            "Do not select the friendliest p-value."
        ),
    }
