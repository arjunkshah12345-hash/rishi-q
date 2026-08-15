"""End-to-end experiment runners."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from rishiq.annotation import HeuristicAnnotationBackend
from rishiq.blinding import blind_passage
from rishiq.experiments.firewall import assert_not_confirmatory_path, split_guard
from rishiq.field_analysis import classify_field_ontology
from rishiq.fingerprints import load_all_fingerprints, load_fingerprint_index
from rishiq.models import Passage
from rishiq.models.ontology import load_ontology
from rishiq.provenance import build_manifest, sha256_file, sha256_json, write_manifest
from rishiq.similarity import (
    annotations_to_vector,
    quantum_exclusive_feature_score,
    quantum_specificity_score,
    score_all_theories,
)


def passages_from_parquet(path: str | Path) -> list[Passage]:
    assert_not_confirmatory_path(path)
    df = pd.read_parquet(path)
    records = df.to_dict(orient="records")
    cleaned = []
    for row in records:
        for k, v in list(row.items()):
            if v is None:
                continue
            try:
                if isinstance(v, float) and pd.isna(v):
                    row[k] = None
            except Exception:
                pass
        cleaned.append(Passage.model_validate(row))
    return cleaned


def passages_to_parquet(passages: list[Passage], path: str | Path) -> Path:
    assert_not_confirmatory_path(path)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([p.model_dump(mode="json") for p in passages])
    df.to_parquet(path, index=False)
    return path


def run_pipeline_on_passages(
    passages: list[Passage],
    *,
    ontology_path: str | Path,
    fingerprint_dir: str | Path,
    out_dir: str | Path,
    experiment_id: str = "dev-synthetic-e2e",
    backend_name: str = "heuristic",
    metric: str = "weighted_jaccard",
    seed: int = 42,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    assert_not_confirmatory_path(out_dir)

    for p in passages:
        split_guard(p.dataset_split.value if hasattr(p.dataset_split, "value") else p.dataset_split)

    ontology = load_ontology(ontology_path)
    fingerprints = load_all_fingerprints(fingerprint_dir)
    index = load_fingerprint_index(fingerprint_dir)
    backend = HeuristicAnnotationBackend()

    annotation_rows: list[dict] = []
    score_rows: list[dict] = []
    summary_rows: list[dict] = []
    field_rows: list[dict] = []

    for passage in passages:
        blinded = blind_passage(passage)
        props = backend.extract_propositions(blinded)
        anns = backend.annotate_features(blinded, props, ontology)
        anns = backend.verify(anns, blinded, ontology)
        # Map anonymous annotations back to real passage_id for storage
        anns = [
            a.model_copy(update={"passage_id": passage.passage_id}) for a in anns
        ]
        vec = annotations_to_vector(
            passage.passage_id, anns, ontology.feature_ids(), ontology.version
        )
        scores = score_all_theories(vec, fingerprints, metric=metric)
        qs = quantum_specificity_score(scores)
        qef = quantum_exclusive_feature_score(vec, index["qef_features"])
        field = classify_field_ontology(vec)

        for a in anns:
            annotation_rows.append(a.model_dump(mode="json"))
        for s in scores:
            score_rows.append(s.model_dump(mode="json"))
        summary_rows.append(
            {
                "passage_id": passage.passage_id,
                "tradition": passage.tradition,
                "role": passage.role,
                "work": passage.work,
                "QS": qs,
                "QEF": qef,
                "dataset_split": passage.dataset_split.value
                if hasattr(passage.dataset_split, "value")
                else passage.dataset_split,
                **{s.theory_id: s.score for s in scores},
                "field_class": field["class"],
            }
        )
        field_rows.append(field)

    ann_path = out_dir / "annotations.parquet"
    score_path = out_dir / "theory_scores.parquet"
    summary_path = out_dir / "passage_scores.parquet"
    field_path = out_dir / "field_ontology.parquet"
    pd.DataFrame(annotation_rows).to_parquet(ann_path, index=False)
    pd.DataFrame(score_rows).to_parquet(score_path, index=False)
    pd.DataFrame(summary_rows).to_parquet(summary_path, index=False)
    pd.DataFrame(field_rows).to_parquet(field_path, index=False)

    dataset_hash = sha256_json([p.model_dump(mode="json") for p in passages])
    fp_hash = sha256_json(
        {k: v.model_dump(mode="json") for k, v in fingerprints.items()}
    )
    manifest = build_manifest(
        experiment_id=experiment_id,
        dataset_hash=dataset_hash,
        ontology_version=ontology.version,
        prompt_version=backend.prompt_version,
        model_name=backend.name,
        model_revision=backend.revision,
        random_seed=seed,
        fingerprint_hash=fp_hash,
        notes="Exploratory/development run — not confirmatory",
        repo=repo_root,
        extra={
            "metric": metric,
            "n_passages": len(passages),
            "outputs": {
                "annotations": str(ann_path),
                "theory_scores": str(score_path),
                "passage_scores": str(summary_path),
            },
        },
    )
    write_manifest(manifest, out_dir / "manifest.json")

    return {
        "manifest": manifest.model_dump(mode="json"),
        "n_passages": len(passages),
        "summary_path": str(summary_path),
        "mean_QS_by_role": pd.DataFrame(summary_rows)
        .groupby("role")["QS"]
        .mean()
        .to_dict()
        if summary_rows
        else {},
    }
