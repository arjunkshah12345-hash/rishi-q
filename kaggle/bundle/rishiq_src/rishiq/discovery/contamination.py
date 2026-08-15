"""Modern scientific lexicon contamination / anachronism detection.

Detects twentieth-century (and later) physics vocabulary inside texts presented
as translations/commentaries of ancient philosophy. This is a System B research
signal: apparent 'scientific' resonance may be editorial modernization.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

# Strong anachronisms for pre-modern source traditions (English PD translations)
STRONG_ANACHRONISMS = [
    "electron",
    "proton",
    "neutron",
    "quantum",
    "photon",
    "relativity",
    "spacetime",
    "space-time",
    "dna",
    "neuron",
    "galaxy",
    "black hole",
    "radio wave",
    "x-ray",
    "spectrum analysis",
]

# Softer modern-physics lexicon (can also appear in classical atomism translations)
MODERN_PHYSICS_LEXICON = [
    "energy",
    "field",
    "vibration",
    "particle",
    "atom",
    "frequency",
    "wave",
    "dimension",
    "force",
    "matter",
    "molecule",
    "electric",
    "magnetic",
    "gravity",
]


def find_anachronisms(text: str) -> dict[str, list[str]]:
    low = text.lower()
    strong = [t for t in STRONG_ANACHRONISMS if t in low]
    soft = [t for t in MODERN_PHYSICS_LEXICON if t in low]
    return {"strong": strong, "soft": soft}


def passage_contamination_rows(
    passages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for p in passages:
        text = p.get("translation") or p.get("text") or ""
        hits = find_anachronisms(text)
        rows.append(
            {
                "passage_id": p.get("passage_id"),
                "tradition": p.get("tradition"),
                "role": p.get("role"),
                "translation_year": p.get("translation_year"),
                "translator": p.get("translator"),
                "strong_anachronisms": hits["strong"],
                "soft_lexicon": hits["soft"],
                "n_strong": len(hits["strong"]),
                "n_soft": len(hits["soft"]),
                "contaminated": len(hits["strong"]) > 0,
                "excerpt": text[:280].replace("\n", " "),
            }
        )
    return rows


def summarize_by_tradition(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by: dict[str, list] = defaultdict(list)
    for r in rows:
        by[str(r.get("tradition"))].append(r)
    out = {}
    for trad, items in by.items():
        n = len(items)
        n_cont = sum(1 for i in items if i["contaminated"])
        soft_counts = defaultdict(int)
        strong_counts = defaultdict(int)
        for i in items:
            for t in i["soft_lexicon"]:
                soft_counts[t] += 1
            for t in i["strong_anachronisms"]:
                strong_counts[t] += 1
        out[trad] = {
            "n_passages": n,
            "n_contaminated": n_cont,
            "contamination_rate": n_cont / max(n, 1),
            "strong_term_passage_counts": dict(strong_counts),
            "soft_term_passage_counts": dict(soft_counts),
        }
    return out
