#!/usr/bin/env python3
"""Comparative Capra autopsy across PD traditions — novelty hunt beyond Vedānta-only.

Asks: is CONTRADICTED_AS_QUANTUM Vedānta-specific, or universal for any metaphysics?
Also measures Level-I richness without Level-III (the 'Capra trap' vulnerability).
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Reuse Capra claim defs from autopsy if importable; else inline minimal
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "exploratory" / "capra_comparative"
OUT.mkdir(parents=True, exist_ok=True)

# Prefer existing labeled feature matrix from discovery/pd pilot
CANDIDATES = [
    ROOT / "results" / "exploratory" / "pd_pilot" / "passage_feature_matrix.parquet",
    ROOT / "results" / "exploratory" / "annotations_joined.parquet",
    ROOT / "results" / "discovery" / "discovery_payload.json",
]


def load_feature_table() -> pd.DataFrame | None:
    # Try parquet matrices
    for p in ROOT.rglob("*feature*.parquet"):
        if "blind" in str(p):
            continue
        try:
            df = pd.read_parquet(p)
            if {"tradition", "feature_id", "label"} <= set(df.columns) or {
                "role",
                "feature_id",
                "label",
            } <= set(df.columns):
                return df
        except Exception:
            continue
    # Long annotations
    for p in [
        ROOT / "results" / "exploratory" / "pd_pilot" / "annotations.parquet",
        ROOT / "results" / "exploratory" / "kaggle_gpu" / "annotations_joined.parquet",
    ]:
        if p.exists():
            return pd.read_parquet(p)
    return None


def main() -> None:
    # Fall back: re-run lightweight heuristic on PD corpus via existing script outputs
    # Read Capra autopsy JSON which has vedanta-only; rebuild from primary passages if needed
    flag = ROOT / "paper" / "assets" / "flagship_finding.json"
    if not flag.exists():
        raise SystemExit("flagship_finding.json missing — run Capra autopsy first")

    # Use heuristic scores by tradition from headline / exploratory assets
    # Build from corpus development scores if present
    score_paths = list((ROOT / "results").rglob("*passage*score*.parquet")) + list(
        (ROOT / "results").rglob("*annotations*.parquet")
    )
    df = None
    for p in score_paths:
        try:
            t = pd.read_parquet(p)
        except Exception:
            continue
        cols = set(t.columns)
        if "feature_id" in cols and "label" in cols and (
            "tradition" in cols or "role" in cols or "work_id" in cols
        ):
            df = t
            print("using", p)
            break

    if df is None:
        # synthesize comparative summary from known PD pilot primary_effect + flagship
        # by re-invoking annotator on small samples via subprocess would be heavy;
        # instead load discovery enrichments / claims
        print("No annotation matrix found; running inline heuristic on PD parquet")
        import sys

        sys.path.insert(0, str(ROOT / "src"))
        from rishiq.annotation import HeuristicAnnotator
        from rishiq.models.ontology import Ontology

        ont = Ontology.from_yaml(ROOT / "ontology" / "ontology_v0.1.yaml")
        ann = HeuristicAnnotator(ont)
        passages = pd.read_parquet(ROOT / "kaggle" / "bundle" / "pd_passages.parquet")
        # map via blinding if needed — pd_passages may have tradition
        rows = []
        for _, r in passages.iterrows():
            text = r["text"]
            trad = r.get("tradition") or r.get("role") or "unknown"
            pid = r.get("passage_id") or r.get("id")
            labels = ann.annotate_passage_features(text) if hasattr(ann, "annotate_passage_features") else None
            if labels is None:
                # use annotate API
                from rishiq.models import Passage

                pas = Passage(
                    passage_id=str(pid),
                    text=text,
                    tradition=str(trad),
                    work_id=str(r.get("work_id", "w")),
                    language="en",
                )
                # HeuristicAnnotationBackend style
                try:
                    from rishiq.annotation import get_backend

                    backend = get_backend("heuristic")
                except Exception:
                    backend = ann
                feats = []
                for f in ont.features:
                    # classical cue annotate one feature
                    pass
            break
        raise SystemExit("Need annotation matrix — will call run_capra with multi tradition")

    print(df.columns.tolist()[:20], len(df))


if __name__ == "__main__":
    main()
