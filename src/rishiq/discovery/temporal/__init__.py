"""Temporal discovery: first appearance of features, combinations, motifs.

Dates are ranges; never pretend uncertain chronology is exact.
"""

from __future__ import annotations

from typing import Any


def _midpoint(year_start: int | None, year_end: int | None) -> float | None:
    if year_start is None and year_end is None:
        return None
    if year_start is None:
        return float(year_end)  # type: ignore[arg-type]
    if year_end is None:
        return float(year_start)
    return (year_start + year_end) / 2.0


def first_appearances(
    passage_features: dict[str, set[str]],
    dating: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """For each feature and 2-feature combo, earliest defensible date range."""
    feature_first: dict[str, dict[str, Any]] = {}
    combo_first: dict[str, dict[str, Any]] = {}

    for pid, feats in passage_features.items():
        d = dating.get(pid, {})
        ys, ye = d.get("year_start"), d.get("year_end")
        mid = _midpoint(ys, ye)
        if mid is None:
            continue
        uncertainty = abs((ye or ys or 0) - (ys or ye or 0))
        for f in feats:
            prev = feature_first.get(f)
            if prev is None or mid < prev["midpoint"]:
                feature_first[f] = {
                    "feature": f,
                    "passage_id": pid,
                    "year_start": ys,
                    "year_end": ye,
                    "midpoint": mid,
                    "range_width": uncertainty,
                    "tradition": d.get("tradition"),
                    "work_id": d.get("work_id"),
                }
        feats_l = sorted(feats)
        for i, a in enumerate(feats_l):
            for b in feats_l[i + 1 :]:
                key = f"{a}+{b}"
                prev = combo_first.get(key)
                if prev is None or mid < prev["midpoint"]:
                    combo_first[key] = {
                        "combination": key,
                        "passage_id": pid,
                        "year_start": ys,
                        "year_end": ye,
                        "midpoint": mid,
                        "range_width": uncertainty,
                        "tradition": d.get("tradition"),
                        "work_id": d.get("work_id"),
                    }

    return {
        "features": feature_first,
        "combinations": combo_first,
        "note": "Date ranges only; wide ranges indicate low chronological precision.",
    }


def motif_temporal(
    motif_passages: dict[str, list[str]],
    dating: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for mid, pids in motif_passages.items():
        mids = []
        ranges = []
        for pid in pids:
            d = dating.get(pid, {})
            midpt = _midpoint(d.get("year_start"), d.get("year_end"))
            if midpt is not None:
                mids.append(midpt)
                ranges.append((d.get("year_start"), d.get("year_end")))
        if not mids:
            out[mid] = {"status": "undated"}
            continue
        out[mid] = {
            "earliest_midpoint": min(mids),
            "latest_midpoint": max(mids),
            "median_midpoint": float(sorted(mids)[len(mids) // 2]),
            "n_dated": len(mids),
            "sample_ranges": ranges[:10],
        }
    return out
