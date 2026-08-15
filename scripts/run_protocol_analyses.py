#!/usr/bin/env python3
"""Run exploratory analyses required by protocol milestones: primary_effect, classifier,
negative controls, vocabulary masking — all marked exploratory / not H1.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from rishiq.annotation import HeuristicAnnotationBackend
from rishiq.blinding import blind_passage
from rishiq.classifier import PhysicsOntologyClassifier
from rishiq.experiments import passages_from_parquet
from rishiq.fingerprints import load_all_fingerprints, load_fingerprint_index
from rishiq.masking import make_variants
from rishiq.models.ontology import load_ontology
from rishiq.robustness import negative_control_feature_shuffle, run_robustness_battery
from rishiq.similarity import (
    annotations_to_vector,
    quantum_specificity_score,
    score_all_theories,
)
from rishiq.statistics import cluster_permutation_pvalue, mean_difference

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/exploratory/protocol_analyses"
SCORES = ROOT / "results/exploratory/prototype100/passage_scores.parquet"
CORPUS = ROOT / "corpus/development/prototype100_passages.parquet"


def run_primary_effect(scores: pd.DataFrame) -> dict:
    target = scores[scores["role"] == "target"]
    control = scores[scores["role"].isin(["control", "negative_control"])]
    # cluster by work
    delta = mean_difference(target["QS"], control["QS"])
    perm = cluster_permutation_pvalue(
        target["QS"].tolist(),
        target["work"].tolist(),
        control["QS"].tolist(),
        control["work"].tolist(),
        n_perm=499,
        seed=42,
    )
    return {
        "warning": "EXPLORATORY_ONLY_NOT_CONFIRMATORY_H1",
        "n_target": int(len(target)),
        "n_control": int(len(control)),
        "delta_Q": float(delta),
        "mean_QS_target": float(target["QS"].mean()) if len(target) else None,
        "mean_QS_control": float(control["QS"].mean()) if len(control) else None,
        "permutation": perm,
        "note": "Synthetic prototype100; do not interpret as Sanskrit result.",
    }


def run_classifier(scores_path: Path) -> dict:
    ont = load_ontology(ROOT / "ontology/ontology_v0.1.yaml")
    fps = load_all_fingerprints(ROOT / "ontology/physics_fingerprints")
    backend = HeuristicAnnotationBackend()
    # Train only on physics_reference passages
    passages = passages_from_parquet(CORPUS)
    phys = [p for p in passages if p.role == "physics_reference"]
    label_map = {
        "PHYS_NEWTON_001": "CLASSICAL_MECHANICS",
        "PHYS_EM_001": "ELECTROMAGNETISM",
        "PHYS_THERMO_001": "THERMODYNAMICS",
        "PHYS_REL_001": "RELATIVITY",
        "PHYS_QM_001": "QUANTUM_MECHANICS",
        "PHYS_QFT_001": "QUANTUM_FIELD_THEORY",
        "PHYS_ENTANGLE_001": "QUANTUM_MECHANICS",
    }
    vectors = []
    labels = []
    for p in phys:
        if p.passage_id not in label_map:
            continue
        b = blind_passage(p)
        anns = backend.verify(
            backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
        )
        vec = annotations_to_vector(p.passage_id, anns, ont.feature_ids(), ont.version)
        vectors.append(vec)
        labels.append(label_map[p.passage_id])
    clf = PhysicsOntologyClassifier()
    clf.fit(vectors, labels, ont.feature_ids())
    clf.freeze()
    # Evaluate a few ancient-like synthetic passages
    synth = [p for p in passages if p.role in {"target", "control", "negative_control"}][:12]
    preds = []
    for p in synth:
        b = blind_passage(p)
        anns = backend.verify(
            backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
        )
        vec = annotations_to_vector(p.passage_id, anns, ont.feature_ids(), ont.version)
        probs = clf.predict_proba(vec)
        preds.append({"passage_id": p.passage_id, "tradition": p.tradition, "role": p.role, **probs})
    return {
        "warning": "SECONDARY_EXPLORATORY_CLASSIFIER",
        "train_n": len(vectors),
        "train_labels": labels,
        "predictions_sample": preds,
        "note": "Trained only on modern physics ontology vectors; not proof a text 'is quantum'.",
    }


def run_masking_demo() -> dict:
    text = "Cosmic energy permeates the quantum field as sacred vibration and particle-wave resonance."
    variants = make_variants(text)
    ont = load_ontology(ROOT / "ontology/ontology_v0.1.yaml")
    fps = load_all_fingerprints(ROOT / "ontology/physics_fingerprints")
    backend = HeuristicAnnotationBackend()
    from rishiq.models import DatasetSplit, Passage
    from rishiq.provenance import sha256_text

    rows = []
    for name, payload in variants.items():
        p = Passage(
            passage_id=f"MASKDEMO_{name}",
            tradition="masking_demo",
            work="Vocabulary masking demo",
            source_language="en",
            translation=payload["text"],
            translation_style="synthetic",
            license_status="synthetic",
            dataset_split=DatasetSplit.SYNTHETIC,
            role="negative_control",
            source_hash=sha256_text(payload["text"]),
        )
        b = blind_passage(p)
        anns = backend.verify(
            backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
        )
        vec = annotations_to_vector(p.passage_id, anns, ont.feature_ids(), ont.version)
        scores = score_all_theories(vec, fps)
        rows.append(
            {
                "variant": name,
                "text": payload["text"],
                "QS": quantum_specificity_score(scores),
                "n_edits": len(payload["edits"]),
            }
        )
    return {"warning": "EXPLORATORY_MASKING_DEMO", "rows": rows}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not SCORES.exists():
        raise SystemExit("Run scripts/build_prototype100.py first")

    scores = pd.read_parquet(SCORES)
    primary = run_primary_effect(scores)
    (OUT / "primary_effect.json").write_text(json.dumps(primary, indent=2), encoding="utf-8")

    # Cross-civilization matrix (mean theory scores)
    theories = [
        "newtonian",
        "classical_em",
        "thermodynamics",
        "relativity",
        "quantum_mechanics",
        "quantum_field_theory",
    ]
    matrix = scores.groupby("tradition")[theories].mean().round(3)
    matrix.to_csv(OUT / "cross_civilization_matrix.csv")
    matrix.to_csv(ROOT / "paper/tables/tab_cross_civilization_matrix.csv")

    # Negative control: feature shuffle
    ont = load_ontology(ROOT / "ontology/ontology_v0.1.yaml")
    fps = load_all_fingerprints(ROOT / "ontology/physics_fingerprints")
    backend = HeuristicAnnotationBackend()
    passages = passages_from_parquet(CORPUS)[:30]
    vectors = []
    for p in passages:
        b = blind_passage(p)
        anns = backend.verify(
            backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
        )
        vectors.append(annotations_to_vector(p.passage_id, anns, ont.feature_ids(), ont.version))
    neg = negative_control_feature_shuffle(vectors, fps, seed=42)
    (OUT / "negative_control_shuffle.json").write_text(json.dumps(neg, indent=2), encoding="utf-8")

    # Robustness table from prototype delta
    t = scores[scores["role"] == "target"]["QS"]
    c = scores[scores["role"].isin(["control", "negative_control"])]["QS"]
    primary_delta = float(t.mean() - c.mean()) if len(t) and len(c) else 0.0
    # masking variant as exploratory stand-in
    mask = run_masking_demo()
    (OUT / "masking_demo.json").write_text(json.dumps(mask, indent=2), encoding="utf-8")
    variants = {
        "N_no_embeddings": primary_delta,
        "J_mask_physics_vocab": float(np.mean([r["QS"] for r in mask["rows"] if r["variant"] != "original"]))
        - float(next(r["QS"] for r in mask["rows"] if r["variant"] == "original")),
    }
    rob = run_robustness_battery(primary_delta=primary_delta, variants=variants)
    pd.DataFrame(rob).to_csv(OUT / "robustness_table.csv", index=False)
    pd.DataFrame(rob).to_csv(ROOT / "paper/tables/tab_robustness_battery.csv", index=False)

    clf = run_classifier(SCORES)
    (OUT / "physics_classifier_exploratory.json").write_text(
        json.dumps(clf, indent=2), encoding="utf-8"
    )

    # Field ontology summary
    field = pd.read_parquet(ROOT / "results/exploratory/prototype100/field_ontology.parquet")
    field_join = field.merge(scores[["passage_id", "tradition", "role"]], on="passage_id")
    field_sum = (
        field_join.groupby(["role", "class"]).size().reset_index(name="n")
    )
    field_sum.to_csv(OUT / "field_ontology_summary.csv", index=False)

    summary = {
        "primary_effect_path": str(OUT / "primary_effect.json"),
        "delta_Q_exploratory": primary["delta_Q"],
        "permutation_p": primary["permutation"]["p_value"],
        "negative_control_abs_mean_qs": neg["abs_mean_qs"],
        "classifier_train_n": clf["train_n"],
        "warning": "ALL_EXPLORATORY",
    }
    (OUT / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
