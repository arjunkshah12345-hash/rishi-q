"""Negative controls and adversarial robustness battery."""

from __future__ import annotations

from copy import deepcopy
from typing import Callable

import numpy as np

from rishiq.models import FeatureVector
from rishiq.similarity import quantum_specificity_score, score_all_theories
from rishiq.fingerprints import TheoryFingerprint


def shuffle_features(vector: FeatureVector, seed: int = 42) -> FeatureVector:
    rng = np.random.default_rng(seed)
    keys = list(vector.values.keys())
    vals = [vector.values[k] for k in keys]
    rng.shuffle(vals)
    new_vals = dict(zip(keys, vals))
    return vector.model_copy(update={"values": new_vals, "passage_id": vector.passage_id + "::shuf"})


def randomize_fingerprint(
    fp: TheoryFingerprint, seed: int = 42
) -> TheoryFingerprint:
    rng = np.random.default_rng(seed)
    keys = list(fp.features.keys())
    vals = [fp.features[k] for k in keys]
    rng.shuffle(vals)
    return fp.model_copy(update={"features": dict(zip(keys, vals)), "theory_id": fp.theory_id + "_rand"})


ROBUSTNESS_TESTS = [
    "A_remove_unity_concepts",
    "B_remove_vibration_concepts",
    "C_remove_atomism",
    "D_remove_prana",
    "E_remove_akasa",
    "F_remove_brahman",
    "G_remove_sakti_spanda",
    "H_older_translations_only",
    "I_literal_translations_only",
    "J_mask_physics_vocab",
    "K_human_annotations_only",
    "L_high_confidence_only",
    "N_no_embeddings",
    "S_alternative_metrics",
]


def run_robustness_battery(
    *,
    primary_delta: float,
    variants: dict[str, float],
) -> list[dict]:
    """variants maps test_id -> delta_Q under that ablation."""
    rows = []
    for test_id in ROBUSTNESS_TESTS:
        delta = variants.get(test_id, primary_delta)
        rows.append(
            {
                "test_id": test_id,
                "delta_Q": delta,
                "status": "computed" if test_id in variants else "not_run",
                "note": "Human-only (K) requires external annotations"
                if test_id.startswith("K_")
                else "",
            }
        )
    return rows


def negative_control_feature_shuffle(
    vectors: list[FeatureVector],
    fingerprints: dict[str, TheoryFingerprint],
    seed: int = 42,
) -> dict:
    qs = []
    for i, v in enumerate(vectors):
        sv = shuffle_features(v, seed=seed + i)
        scores = score_all_theories(sv, fingerprints)
        qs.append(quantum_specificity_score(scores))
    return {
        "control": "N1_shuffle_features",
        "mean_qs": float(np.mean(qs)) if qs else float("nan"),
        "abs_mean_qs": float(np.mean(np.abs(qs))) if qs else float("nan"),
        "n": len(qs),
        "expected": "near_zero_nonspecific",
    }
