"""Translation-shift discovery: lexical modernization as research signal."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

# Terms whose appearance in translations may inflate modern-physics readings
MODERN_PHYSICS_LEXICON = [
    "energy",
    "field",
    "vibration",
    "particle",
    "atom",
    "frequency",
    "information",
    "dimension",
    "quantum",
    "wave",
    "spectrum",
    "force",
    "matter",
    "space-time",
    "spacetime",
]


def lexicon_hits(text: str) -> dict[str, int]:
    low = text.lower()
    return {w: low.count(w) for w in MODERN_PHYSICS_LEXICON if w in low}


def translation_shift_graph(
    aligned_versions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a shift graph across chronologically ordered translations of one passage.

    Each item: {year, translation_id, text, feature_yes: set[str], qs: float}
    """
    ordered = sorted(aligned_versions, key=lambda x: x.get("year") or 0)
    nodes = []
    edges = []
    for i, v in enumerate(ordered):
        hits = lexicon_hits(v.get("text", ""))
        nodes.append(
            {
                "id": v.get("translation_id", f"t{i}"),
                "year": v.get("year"),
                "lexicon_hits": hits,
                "n_modern_terms": sum(hits.values()),
                "qs": v.get("qs"),
                "features": sorted(v.get("feature_yes", [])),
            }
        )
        if i > 0:
            prev = ordered[i - 1]
            prev_hits = lexicon_hits(prev.get("text", ""))
            gained = {k: hits.get(k, 0) - prev_hits.get(k, 0) for k in MODERN_PHYSICS_LEXICON}
            gained = {k: d for k, d in gained.items() if d > 0}
            feat_prev = set(prev.get("feature_yes", []))
            feat_cur = set(v.get("feature_yes", []))
            edges.append(
                {
                    "from": prev.get("translation_id", f"t{i-1}"),
                    "to": v.get("translation_id", f"t{i}"),
                    "year_from": prev.get("year"),
                    "year_to": v.get("year"),
                    "lexicon_gained": gained,
                    "features_gained": sorted(feat_cur - feat_prev),
                    "features_lost": sorted(feat_prev - feat_cur),
                    "delta_qs": (v.get("qs") or 0) - (prev.get("qs") or 0),
                }
            )
    return {"nodes": nodes, "edges": edges, "status": "exploratory"}


def aggregate_modernization_by_decade(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """rows: translation_year, text, qs optional."""
    buckets: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        y = r.get("translation_year")
        if y is None:
            continue
        try:
            import math

            if isinstance(y, float) and math.isnan(y):
                continue
            yi = int(y)
        except (TypeError, ValueError):
            continue
        decade = (yi // 10) * 10
        buckets[decade].append(r)
    out = []
    for decade in sorted(buckets):
        items = buckets[decade]
        hit_sums = defaultdict(int)
        qs_vals = []
        for it in items:
            for k, v in lexicon_hits(it.get("text", "")).items():
                hit_sums[k] += v
            if it.get("qs") is not None:
                qs_vals.append(float(it["qs"]))
        out.append(
            {
                "decade": decade,
                "n_translations": len(items),
                "lexicon_totals": dict(hit_sums),
                "mean_modern_term_mentions": sum(hit_sums.values()) / max(len(items), 1),
                "mean_qs": sum(qs_vals) / len(qs_vals) if qs_vals else None,
            }
        )
    return out
