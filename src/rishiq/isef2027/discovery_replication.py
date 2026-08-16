"""Discovery → held-out replication scaffold (same dataset must not 'confirm' itself)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


def mine_bigram_motifs(texts: list[str], top_k: int = 15) -> list[str]:
    bg: Counter[str] = Counter()
    for text in texts:
        toks = [t.lower() for t in text.split() if t.isalpha() and len(t) > 3]
        for a, b in zip(toks, toks[1:]):
            bg[f"{a}_{b}"] += 1
    return [m for m, _ in bg.most_common(top_k)]


def enrichment(motifs: list[str], texts: list[str], background: list[str]) -> dict[str, float]:
    def rate(ms: list[str], corpus: list[str]) -> float:
        if not corpus:
            return 0.0
        hits = 0
        for text in corpus:
            tl = text.lower()
            if any(m.replace("_", " ") in tl or m.split("_")[0] in tl for m in ms[:5]):
                hits += 1
        return hits / len(corpus)

    d = rate(motifs, texts)
    b = rate(motifs, background)
    return {
        "discovery_hit_rate": d,
        "background_hit_rate": b,
        "lift": (d + 1e-9) / (b + 1e-9),
    }


def run_discovery_replication_demo(seed: int = 42) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    discover = [
        "A pervasive medium is inferred from sound as its distinctive mark.",
        "Heat and light belong to a fiery substance distinct from the sound medium.",
        "The all-pervasive substance is actionless relative to dynamical field equations.",
        "Sound is produced and impermanent yet marks the ethereal substance.",
        "Inference from auditory objects establishes the pervasive continuum.",
    ]
    replicate = [
        "Auditory marks indicate a single pervasive continuum substance.",
        "Fiery substance carries heat separately from the sound-bearing medium.",
        "No dynamical electromagnetic equations define the pervasive substance.",
        "Impermanent sounds still serve as inferential marks of the medium.",
    ]
    background = [
        "Compassion and non-harm define ethical conduct among beings.",
        "Ritual purity hierarchies do not specify physical substrates.",
        "Narrative metaphors of unity lack dynamical field structure.",
    ]
    discover = [discover[i] for i in rng.permutation(len(discover))]
    motifs = mine_bigram_motifs(discover)
    enrich_disc = enrichment(motifs, discover, background)
    enrich_rep = enrichment(motifs, replicate, background)
    survives = enrich_rep["lift"] >= 1.2 and enrich_rep["discovery_hit_rate"] >= 0.4
    return {
        "pipeline_id": "ISEF2027-DISC-REPL-v1",
        "seed": seed,
        "n_discover": len(discover),
        "n_replicate": len(replicate),
        "motifs_top": motifs[:10],
        "enrichment_discovery": enrich_disc,
        "enrichment_replication": enrich_rep,
        "survives_replication_demo_threshold": bool(survives),
        "rule": "Findings mined on discover split are tested only on replicate split.",
        "warnings": [
            "Toy demo only. Real discovery must use frozen motif definitions and sealed replication data.",
            "Never present discovery-set enrichment as independent confirmation.",
        ],
    }


def write_discovery_replication(root: Path, seed: int = 42) -> dict[str, Any]:
    payload = run_discovery_replication_demo(seed=seed)
    out = root / "results/isef2027/dev/discovery_replication.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
