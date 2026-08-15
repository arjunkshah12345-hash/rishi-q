#!/usr/bin/env python3
"""Join Kaggle annotations (anonymous_id) back to passage_ids and score."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from rishiq.experiments import passages_from_parquet, run_pipeline_on_passages
from rishiq.fingerprints import load_all_fingerprints, load_fingerprint_index
from rishiq.models import AnnotationLabel, FeatureAnnotation
from rishiq.models.ontology import load_ontology
from rishiq.similarity import (
    annotations_to_vector,
    quantum_exclusive_feature_score,
    quantum_specificity_score,
    score_all_theories,
)
from rishiq.statistics import cluster_permutation_pvalue, mean_difference
from rishiq.field_analysis import classify_field_ontology
from rishiq.provenance import build_manifest, write_manifest, sha256_file

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--annotations", type=Path, required=True)
    ap.add_argument(
        "--blinding-map",
        type=Path,
        default=ROOT / "kaggle/bundle/blinding_map.PRIVATE.json",
    )
    ap.add_argument(
        "--corpus",
        type=Path,
        default=ROOT / "corpus/development/pd_passages.parquet",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results/exploratory/kaggle_joined",
    )
    args = ap.parse_args()

    mapping = json.loads(args.blinding_map.read_text())  # anonymous -> passage_id
    ann = pd.read_parquet(args.annotations)
    if "passage_id" not in ann.columns and "anonymous_id" in ann.columns:
        ann["passage_id"] = ann["anonymous_id"].map(mapping)
    elif ann["passage_id"].astype(str).str.startswith("PASSAGE_").any():
        ann["passage_id"] = ann["passage_id"].map(lambda x: mapping.get(x, x))

    passages = {p.passage_id: p for p in passages_from_parquet(args.corpus)}
    ontology = load_ontology(ROOT / "ontology/ontology_v0.1.yaml")
    fps = load_all_fingerprints(ROOT / "ontology/physics_fingerprints")
    index = load_fingerprint_index(ROOT / "ontology/physics_fingerprints")

    args.out.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    score_rows = []
    for pid, g in ann.groupby("passage_id"):
        if pid not in passages:
            continue
        annotations = []
        for _, row in g.iterrows():
            try:
                annotations.append(
                    FeatureAnnotation(
                        passage_id=pid,
                        feature_id=row["feature_id"],
                        label=AnnotationLabel(str(row["label"])),
                        evidence=str(row.get("evidence") or ""),
                        reason=str(row.get("reason") or ""),
                        confidence=float(row.get("confidence") or 0.5),
                        annotator=str(row.get("annotator") or "kaggle"),
                        model_version=str(row.get("model_version") or "unknown"),
                        prompt_version=str(row.get("prompt_version") or "ann-v0.1"),
                        verified=True,
                    )
                )
            except Exception:
                continue
        vec = annotations_to_vector(pid, annotations, ontology.feature_ids(), ontology.version)
        scores = score_all_theories(vec, fps)
        p = passages[pid]
        summary_rows.append(
            {
                "passage_id": pid,
                "tradition": p.tradition,
                "role": p.role,
                "work": p.work,
                "QS": quantum_specificity_score(scores),
                "QEF": quantum_exclusive_feature_score(vec, index["qef_features"]),
                **{s.theory_id: s.score for s in scores},
                "field_class": classify_field_ontology(vec)["class"],
            }
        )
        score_rows.extend([s.model_dump(mode="json") for s in scores])

    summary = pd.DataFrame(summary_rows)
    summary.to_parquet(args.out / "passage_scores.parquet", index=False)
    pd.DataFrame(score_rows).to_parquet(args.out / "theory_scores.parquet", index=False)
    ann.to_parquet(args.out / "annotations_joined.parquet", index=False)

    hist = summary[summary["role"].isin(["target", "control"])]
    target = hist[hist["role"] == "target"]
    control = hist[hist["role"] == "control"]
    primary = {
        "warning": "EXPLORATORY_KAGGLE_JOIN_NOT_CONFIRMATORY",
        "n_target": int(len(target)),
        "n_control": int(len(control)),
        "delta_Q": float(mean_difference(target["QS"], control["QS"])) if len(target) and len(control) else None,
        "mean_QS_by_tradition": hist.groupby("tradition")["QS"].mean().to_dict() if len(hist) else {},
    }
    if len(target) and len(control):
        primary["permutation"] = cluster_permutation_pvalue(
            target["QS"].tolist(),
            target["work"].tolist(),
            control["QS"].tolist(),
            control["work"].tolist(),
            n_perm=999,
            seed=42,
        )
    (args.out / "primary_effect.json").write_text(json.dumps(primary, indent=2), encoding="utf-8")
    write_manifest(
        build_manifest(
            experiment_id="kaggle-joined-pd",
            dataset_hash=sha256_file(args.corpus),
            ontology_version=ontology.version,
            prompt_version="ann-v0.1",
            model_name="kaggle-import",
            notes="Joined Kaggle annotations; exploratory",
            repo=ROOT,
        ),
        args.out / "manifest.json",
    )
    print(json.dumps(primary, indent=2))


if __name__ == "__main__":
    main()
