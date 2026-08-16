"""Method validation benchmark: lexical vs ontology vs graph (embeddings optional).

Uses METHOD_VALIDATION panels with known target theories — not historical Sanskrit claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from rishiq.fingerprints import load_all_fingerprints
from rishiq.isef2027.baselines import binary_vector_jaccard, mean_tfidf_similarity, ranking_accuracy, tfidf_pairwise
from rishiq.isef2027.concept_graph import ConceptGraph, graph_overlap_score
from rishiq.isef2027.adversarial import mask_vocabulary


# Curated short panels for METHOD VALIDATION ONLY (modern physics pedagogy language).
POSITIVE_PANELS: dict[str, list[str]] = {
    "newtonian": [
        "Point masses move under forces in absolute space and time; acceleration equals force over mass.",
        "Planetary orbits follow inverse-square gravitational force without quantized action.",
        "Collisions conserve momentum; trajectories are continuous classical paths.",
    ],
    "classical_em": [
        "Light is an electromagnetic wave; electric and magnetic fields obey Maxwell equations.",
        "Charge produces fields; induction couples changing magnetic flux to electric fields.",
        "Radiation unifies luminous and non-luminous electromagnetic disturbances in one field.",
    ],
    "thermodynamics": [
        "Heat flows from hot to cold; entropy of an isolated system tends to increase.",
        "Temperature and pressure describe equilibrium states of macroscopic matter.",
        "Work and heat are energy transfers; no microscopic quantum amplitudes are required.",
    ],
    "quantum_mechanics": [
        "Observables are operators; incompatible observables do not share eigenbases.",
        "Measurement yields eigenvalues with Born-rule probabilities; superposition is linear.",
        "Planck's constant sets action scale; discrete spectra appear for bound systems.",
    ],
    "quantum_field_theory": [
        "Fields are operator-valued; particles are quantized field excitations.",
        "Creation and annihilation operators act on Fock space; interactions via local Lagrangians.",
        "Vacuum fluctuations and renormalization appear; classical EM is the ħ→0 limit of the photon field.",
    ],
}

NEGATIVE_PANELS: dict[str, list[str]] = {
    "generic_metaphysics": [
        "All is one; everything is interconnected in a hidden deeper reality.",
        "Vibration underlies existence; unity and impermanence define the cosmos.",
        "An ineffable absolute grounds changing appearances without specifying dynamics.",
    ],
    "ethics_verse": [
        "Do not kill; speak truth; cultivate compassion toward all beings.",
        "Anger destroys wisdom; mindfulness brings peace to the mind.",
    ],
}


def _hashing_embed(texts: list[str], dim: int = 256, seed: int = 42) -> np.ndarray:
    """Lightweight bag-of-hashed-ngrams embedding (no GPU / no network)."""
    rng = np.random.default_rng(seed)
    # Fixed random projections per token hash
    mat = np.zeros((len(texts), dim), dtype=float)
    for i, text in enumerate(texts):
        toks = text.lower().split()
        for t in toks:
            h = hash(t) % (2**31)
            rng_t = np.random.default_rng(h ^ seed)
            mat[i] += rng_t.normal(size=dim)
        n = np.linalg.norm(mat[i])
        if n > 0:
            mat[i] /= n
    return mat


def embedding_mean_similarity(a: list[str], b: list[str], seed: int = 42) -> float:
    if not a or not b:
        return 0.0
    A = _hashing_embed(a, seed=seed)
    B = _hashing_embed(b, seed=seed)
    # mean pairwise cosine
    sims = A @ B.T
    return float(np.mean(sims))


def keyword_feature_proxy(text: str) -> dict[str, int]:
    """Crude lexical→ontology proxy for method benchmarking (not confirmatory annotation)."""
    t = text.lower()
    feats = {
        "O02": int(any(w in t for w in ("mass", "particle", "atom", "constituent"))),
        "O04": int(any(w in t for w in ("field", "medium", "wave"))),
        "D01": int(any(w in t for w in ("force", "acceleration", "motion", "orbit"))),
        "D04": int(any(w in t for w in ("equation", "law", "maxwell", "lagrangian"))),
        "F01": int("field" in t),
        "F02": int(any(w in t for w in ("electromagnetic", "electric", "magnetic", "maxwell"))),
        "F03": int("light" in t or "radiation" in t),
        "F07": int(any(w in t for w in ("quantized", "quantum field", "fock", "excitation"))),
        "Q01": int(any(w in t for w in ("operator", "eigen", "superposition", "born"))),
        "Q03": int(any(w in t for w in ("planck", "discrete spectra", "ħ", "hbar"))),
        "Q06": int("entangle" in t),
        "Q08": int(any(w in t for w in ("creation", "annihilation", "fock", "quantized field"))),
        "R01": int(any(w in t for w in ("field", "mediate", "interaction"))),
    }
    return feats


def aggregate_panel_vector(texts: list[str]) -> dict[str, int]:
    acc: dict[str, int] = {}
    for text in texts:
        v = keyword_feature_proxy(text)
        for k, val in v.items():
            acc[k] = max(acc.get(k, 0), val)
    return acc


def run_theory_identification_benchmark(root: Path, seed: int = 42) -> dict[str, Any]:
    fps = load_all_fingerprints(root / "ontology/physics_fingerprints")
    rows = []
    for theory_id, texts in POSITIVE_PANELS.items():
        if theory_id not in fps:
            continue
        vec = aggregate_panel_vector(texts)
        scores = {
            tid: binary_vector_jaccard(vec, {k: int(fp.features.get(k, 0)) for k in set(vec) | set(fp.features)})
            for tid, fp in fps.items()
        }
        rank = ranking_accuracy(scores, correct_key=theory_id)
        # baselines vs reference panel of same theory vs QFT/generic
        ref_qft = POSITIVE_PANELS.get("quantum_field_theory", [])
        rows.append(
            {
                "panel": theory_id,
                "ontology_rank": rank,
                "tfidf_vs_self": mean_tfidf_similarity(texts, texts),
                "tfidf_vs_qft": mean_tfidf_similarity(texts, ref_qft) if theory_id != "quantum_field_theory" else 1.0,
                "hash_embed_vs_qft": embedding_mean_similarity(texts, ref_qft, seed=seed)
                if theory_id != "quantum_field_theory"
                else 1.0,
                "tfidf_vs_generic_metaphysics": mean_tfidf_similarity(texts, NEGATIVE_PANELS["generic_metaphysics"]),
                "masked_tfidf_vs_qft": mean_tfidf_similarity(
                    [mask_vocabulary(t) for t in texts],
                    [mask_vocabulary(t) for t in ref_qft],
                )
                if theory_id != "quantum_field_theory"
                else 1.0,
            }
        )

    # Graph overlap if templates exist
    graph_scores = {}
    ak = root / "ontology/concept_graph/template_vaisesika_akasa_sabda.json"
    mx = root / "ontology/concept_graph/template_maxwell_em.json"
    if ak.exists() and mx.exists():
        ga = ConceptGraph.model_validate_json(ak.read_text())
        gm = ConceptGraph.model_validate_json(mx.read_text())
        graph_scores["template_akasa_vs_maxwell"] = graph_overlap_score(ga, gm)

    top1 = [r["ontology_rank"]["top1_correct"] for r in rows]
    summary = {
        "benchmark_id": "ISEF2027-METHOD-BENCH-v1",
        "seed": seed,
        "n_panels": len(rows),
        "ontology_top1_accuracy": float(np.mean(top1)) if top1 else float("nan"),
        "rows": rows,
        "graph_scores": graph_scores,
        "negative_controls": {
            "generic_vs_em_tfidf": mean_tfidf_similarity(
                NEGATIVE_PANELS["generic_metaphysics"], POSITIVE_PANELS["classical_em"]
            ),
            "ethics_vs_qm_tfidf": mean_tfidf_similarity(
                NEGATIVE_PANELS["ethics_verse"], POSITIVE_PANELS["quantum_mechanics"]
            ),
        },
        "warnings": [
            "METHOD VALIDATION ONLY — not evidence about classical Sanskrit corpora.",
            "keyword_feature_proxy is a crude stand-in until human/model annotation is frozen.",
            "hash embeddings are a local proxy; sentence-transformers remain optional ML secondary.",
        ],
    }
    out = root / "results/isef2027/dev/method_benchmark.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
