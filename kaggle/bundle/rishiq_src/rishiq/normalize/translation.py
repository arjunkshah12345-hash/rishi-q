"""Translation handling and Translation Contamination Index."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd


def translation_contamination_index(
    scores: pd.DataFrame,
    *,
    passage_key: str = "passage_family_id",
    style_col: str = "translation_style",
    qs_col: str = "QS",
    modern_styles: tuple[str, ...] = ("recent_scholarly", "machine"),
    older_styles: tuple[str, ...] = ("literal", "older_scholarly"),
) -> pd.DataFrame:
    """TCI = QS_modern - QS_literal/older for paired passages.

    Expects multiple rows per underlying passage family with different styles.
    """
    if passage_key not in scores.columns:
        raise ValueError(f"need {passage_key} for paired translations")
    rows = []
    for fam, g in scores.groupby(passage_key):
        modern = g[g[style_col].isin(modern_styles)][qs_col]
        older = g[g[style_col].isin(older_styles)][qs_col]
        if modern.empty or older.empty:
            continue
        tci = float(modern.mean() - older.mean())
        rows.append(
            {
                passage_key: fam,
                "QS_modern_mean": float(modern.mean()),
                "QS_older_mean": float(older.mean()),
                "TCI": tci,
                "interpretation": (
                    "possible_modernization"
                    if tci > 0.1
                    else "near_zero"
                    if abs(tci) <= 0.1
                    else "older_higher"
                ),
            }
        )
    return pd.DataFrame(rows)


def summarize_tci(tci_df: pd.DataFrame) -> dict:
    if tci_df.empty:
        return {"n_pairs": 0, "mean_TCI": float("nan"), "status": "insufficient_pairs"}
    return {
        "n_pairs": int(len(tci_df)),
        "mean_TCI": float(tci_df["TCI"].mean()),
        "std_TCI": float(tci_df["TCI"].std(ddof=1)) if len(tci_df) > 1 else 0.0,
        "status": "ok",
    }
