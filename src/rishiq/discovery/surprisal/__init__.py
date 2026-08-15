"""Structural surprisal / outlier detection with artifact guards."""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from rishiq.discovery import PassageGraph


def _signature_prob(sig: frozenset[str], background: Counter[str], total: int) -> float:
    """Naive independent-token probability under background (smoothed)."""
    if not sig or total <= 0:
        return 1.0
    p = 1.0
    for tok in sig:
        p *= (background[tok] + 1) / (total + len(background))
    return max(p, 1e-12)


def compute_surprisal(
    graphs: list[PassageGraph],
    control_ids: set[str] | None = None,
    meta: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Surprisal_i = -log P(X_i | C) under control/historical background.

    Flags artifact risks: empty evidence graphs, very short/long passage notes
    in meta, duplicate signatures.
    """
    meta = meta or {}
    control_ids = control_ids or set()

    background: Counter[str] = Counter()
    n_bg = 0
    for g in graphs:
        if control_ids and g.passage_id not in control_ids:
            continue
        sig = g.motif_signature()
        if not sig:
            continue
        background.update(sig)
        n_bg += 1
    if n_bg == 0:
        # fallback: all graphs
        for g in graphs:
            sig = g.motif_signature()
            background.update(sig)
            n_bg += 1

    # duplicate signature detection
    sig_counts: Counter[str] = Counter()
    for g in graphs:
        key = "|".join(sorted(g.motif_signature()))
        if key:
            sig_counts[key] += 1

    rows: list[dict[str, Any]] = []
    for g in graphs:
        sig = g.motif_signature()
        if not sig:
            continue
        p = _signature_prob(sig, background, max(sum(background.values()), 1))
        surprisal = float(-np.log(p))
        m = meta.get(g.passage_id, {})
        text_len = int(m.get("char_len", m.get("n_chars", 0)) or 0)
        artifacts: list[str] = []
        if text_len and text_len < 40:
            artifacts.append("very_short_passage")
        if text_len and text_len > 4000:
            artifacts.append("very_long_passage")
        if not g.edges and len(g.nodes) <= 1:
            artifacts.append("sparse_graph")
        key = "|".join(sorted(sig))
        if sig_counts[key] >= 5:
            artifacts.append("duplicate_signature_cluster")
        if m.get("ocr_risk"):
            artifacts.append("ocr_risk")
        if m.get("modern_editorial"):
            artifacts.append("modern_editorial_contamination")

        rows.append(
            {
                "passage_id": g.passage_id,
                "surprisal": surprisal,
                "n_nodes": len(g.nodes),
                "n_edges": len(g.edges),
                "signature": sorted(sig),
                "artifact_flags": artifacts,
                "anomaly_candidate": surprisal >= np.percentile(
                    [r["surprisal"] for r in rows] + [surprisal], 95
                )
                if rows
                else False,
            }
        )

    if not rows:
        return []
    thr = float(np.percentile([r["surprisal"] for r in rows], 95))
    for r in rows:
        r["anomaly_candidate"] = bool(
            r["surprisal"] >= thr and not r["artifact_flags"]
        )
        r["status"] = (
            "ARTIFACT_SUSPECTED"
            if r["artifact_flags"]
            else ("ANOMALY_CANDIDATE" if r["anomaly_candidate"] else "TYPICAL")
        )
    rows.sort(key=lambda x: -x["surprisal"])
    return rows
