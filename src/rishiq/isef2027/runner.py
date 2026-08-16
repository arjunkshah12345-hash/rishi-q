"""Reproducible ISEF2027 runner — development/calibration only; never opens sealed set."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml

from rishiq.isef2027.adversarial import run_adversarial_battery
from rishiq.isef2027.baselines import binary_vector_jaccard, mean_tfidf_similarity, ranking_accuracy
from rishiq.isef2027.benchmark import run_theory_identification_benchmark
from rishiq.isef2027.blind_audit import run_blind_audit
from rishiq.isef2027.calibration import build_calibration_from_pd
from rishiq.isef2027.concept_graph import ConceptGraph, graph_overlap_score, write_schema_and_templates
from rishiq.isef2027.discovery_replication import write_discovery_replication
from rishiq.isef2027.freeze import freeze_dev
from rishiq.isef2027.human_val import write_human_validation_pack
from rishiq.isef2027.inference import cluster_effect_bundle, work_level_permutation
from rishiq.isef2027.inventory import write_inventory
from rishiq.isef2027.registry import hash_file, new_record, register_experiment
from rishiq.isef2027.splits import write_split_manifest
from rishiq.isef2027.translation_battery import run_translation_battery
from rishiq.fingerprints import load_all_fingerprints


def _load_config(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _positive_control_demo(seed: int = 42) -> dict:
    """Software positive-control vector resembling classical EM fingerprint features.

    Uses ontology feature IDs from physics_fingerprints — not Sanskrit scoring.
    """
    rng = np.random.default_rng(seed)
    # Emphasize field-like classical features; zero quantum-specific
    classical_like = {
        "O04": 1,
        "O05": 1,
        "D01": 1,
        "D02": 1,
        "D03": 1,
        "D04": 1,
        "D05": 1,
        "F01": 1,
        "F02": 1,
        "F03": 1,
        "F04": 1,
        "R01": 1,
        "Q01": 0,
        "Q03": 0,
        "Q06": 0,
        "Q08": 0,
        "F07": 0,
    }
    texts = [
        "Bodies move under forces through absolute space; light is a wave in the ether field.",
        "Charge and induction obey inverse-square laws; fields mediate electromagnetic forces.",
        "Heat flows; entropy increases; no quantized energy levels are posited.",
    ]
    return {
        "seed": seed,
        "n_positive_control_texts": len(texts),
        "classical_like_vector_template": classical_like,
        "noise_draws": int(rng.integers(0, 1000)),
        "note": "Positive-control harness for method validation — not a historical claim.",
    }


def run_dev_calibration(root: Path, config_path: Path) -> dict:
    root = root.resolve()
    cfg = _load_config(config_path)
    seed = int(cfg.get("seed", 42))
    out_dir = root / cfg.get("out_dir", "results/isef2027/dev")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) inventory + freeze + splits + concept-graph templates
    inv_path = write_inventory(root)
    freeze_path = freeze_dev(root)
    split_path = write_split_manifest(root)
    cg_paths = write_schema_and_templates(root)
    hv_path = write_human_validation_pack(root)

    split_payload = json.loads(split_path.read_text(encoding="utf-8"))
    leak_issues = split_payload.get("leakage_check", {}).get("issues", [])

    # 2) theory fingerprints present?
    fp_dir = root / cfg.get("fingerprint_dir", "ontology/physics_fingerprints")
    fps = load_all_fingerprints(fp_dir)

    # 3) concept-graph overlap on templates
    ak = ConceptGraph.model_validate_json(
        (root / "ontology/concept_graph/template_vaisesika_akasa_sabda.json").read_text()
    )
    mx = ConceptGraph.model_validate_json(
        (root / "ontology/concept_graph/template_maxwell_em.json").read_text()
    )
    graph_score = graph_overlap_score(ak, mx)

    # 4) fingerprint pairwise jaccard among theories (method sanity)
    fp_jaccard = {}
    ids = list(fps.keys())
    for i, a in enumerate(ids):
        for b in ids[i + 1 :]:
            fp_jaccard[f"{a}__{b}"] = binary_vector_jaccard(fps[a].features, fps[b].features)

    # 5) lexical baseline on tiny PD-ish strings (dev only)
    vais_like = [
        "A pervasive medium is marked by sound; heat belongs to a distinct fiery substance.",
        "Sound is the mark by which the pervasive substance is inferred.",
    ]
    maxwell_like = [
        "Light is an electromagnetic wave in a dynamical field unified with radiation.",
        "Charge and induction produce evolving electromagnetic fields; sound is mechanical.",
    ]
    tfidf_vm = mean_tfidf_similarity(vais_like, maxwell_like)

    # 6) ranking demo: score classical_like against fingerprints
    classical_vec = {k: float(v) for k, v in _positive_control_demo(seed)["classical_like_vector_template"].items()}
    theory_scores = {}
    for tid, fp in fps.items():
        # overlap on shared keys only
        shared = {k: classical_vec.get(k, 0) for k in fp.features}
        theory_scores[tid] = binary_vector_jaccard(
            {k: int(shared[k]) for k in shared},
            {k: int(fp.features.get(k, 0)) for k in shared},
        )
    ranking = ranking_accuracy(theory_scores, correct_key=cfg.get("positive_control_expected", "classical_em"))

    # 7) adversarial battery on toy texts
    adv = run_adversarial_battery(
        texts=vais_like + maxwell_like,
        feature_vectors=[classical_vec for _ in range(len(vais_like) + len(maxwell_like))],
        tradition_labels=["vais"] * len(vais_like) + ["maxwell"] * len(maxwell_like),
        seed=seed,
    )

    # 8) inference scaffolding demo (synthetic clustered scores)
    rng = np.random.default_rng(seed)
    t_scores = rng.normal(0.4, 0.05, size=12)
    c_scores = rng.normal(0.35, 0.05, size=12)
    t_clust = [f"W{i//3}" for i in range(12)]
    c_clust = [f"C{i//3}" for i in range(12)]
    infer = cluster_effect_bundle(t_scores, t_clust, c_scores, c_clust, seed=seed)
    work_perm = work_level_permutation(
        {f"W{i}": float(t_scores[i * 3 : (i + 1) * 3].mean()) for i in range(4)},
        {f"C{i}": float(c_scores[i * 3 : (i + 1) * 3].mean()) for i in range(4)},
        seed=seed,
    )

    # 9) method benchmark + translation + blind + discovery/replication + calibration
    bench = run_theory_identification_benchmark(root, seed=seed)
    trans = run_translation_battery(root, seed=seed)
    blind = run_blind_audit(root)
    disc = write_discovery_replication(root, seed=seed)
    calib = build_calibration_from_pd(root)

    summary = {
        "run_id": f"ISEF2027-DEV-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "phase": "development_calibration_harness",
        "seed": seed,
        "sealed_confirmatory_opened": False,
        "split_leakage_issues": leak_issues,
        "paths": {
            "inventory": str(inv_path.relative_to(root)),
            "freeze": str(freeze_path.relative_to(root)),
            "splits": str(split_path.relative_to(root)),
            "human_validation": str(hv_path.relative_to(root)),
            "concept_graphs": [str(p.relative_to(root)) for p in cg_paths],
            "method_benchmark": "results/isef2027/dev/method_benchmark.json",
            "translation_battery": "results/isef2027/dev/translation_battery.json",
            "blind_audit": "results/isef2027/dev/blind_audit.json",
            "discovery_replication": "results/isef2027/dev/discovery_replication.json",
            "calibration_manifest": "corpus/calibration/calibration_manifest.json",
        },
        "n_theory_fingerprints": len(fps),
        "theory_ids": ids,
        "concept_graph_overlap_akasa_vs_maxwell_TEMPLATE": graph_score,
        "fingerprint_pairwise_jaccard": fp_jaccard,
        "tfidf_vais_vs_maxwell_toy": tfidf_vm,
        "positive_control_ranking": ranking,
        "adversarial": adv,
        "inference_demo": {"cluster_bundle": infer, "work_level_permutation": work_perm},
        "method_benchmark_summary": {
            "ontology_top1_accuracy": bench.get("ontology_top1_accuracy"),
            "n_panels": bench.get("n_panels"),
            "negative_controls": bench.get("negative_controls"),
        },
        "translation_battery_summary": {
            "corr_year_vs_modernization_lexicon": trans.get("translator_year_demo", {}).get(
                "corr_year_vs_modernization_lexicon"
            ),
        },
        "blind_audit_status": blind.get("status"),
        "discovery_replication_survives_demo": disc.get("survives_replication_demo_threshold"),
        "calibration_n_records": calib.get("n_records"),
        "warnings": [
            "Toy/dev metrics only — not confirmatory scientific results.",
            "TEMPLATE concept graphs are not student-verified.",
            "Do not interpret these numbers as ancient-quantum evidence.",
            "Method benchmark panels are modern pedagogy text for software validation.",
        ],
    }

    summary_path = out_dir / "run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=float) + "\n", encoding="utf-8")

    # tables
    (out_dir / "fingerprint_jaccard.json").write_text(
        json.dumps(fp_jaccard, indent=2) + "\n", encoding="utf-8"
    )

    # registry (unique id per run)
    rec = new_record(
        root,
        experiment_id=summary["run_id"],
        hypothesis="METHOD_HARNESS: validate baselines/fingerprints/graph overlap on DEV only",
        config_path=config_path,
        dataset_hash=hash_file(split_path),
        seed=seed,
        phase="exploratory",
        output_paths=[str(summary_path.relative_to(root))],
        blinded=False,
        config_frozen_beforehand=False,
        notes="Harness run; sealed set not opened.",
    )
    reg_path = register_experiment(root, rec)
    summary["registry_path"] = str(reg_path.relative_to(root))
    summary_path.write_text(json.dumps(summary, indent=2, default=float) + "\n", encoding="utf-8")
    return summary
