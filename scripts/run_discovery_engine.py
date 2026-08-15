#!/usr/bin/env python3
"""Run System B discovery engine on an existing exploratory annotation run.

Does NOT unlock confirmatory.
Does NOT declare STRONG discoveries without novelty review.
Physics mapping happens AFTER motif mining.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
import yaml

from rishiq.discovery import DiscoveryCandidate
from rishiq.discovery.atlas import build_motif_atlas
from rishiq.discovery.claims import evaluate_claim, load_claims
from rishiq.discovery.claims.report import write_claims_report
from rishiq.discovery.graphs import extract_passage_graph
from rishiq.discovery.motifs import map_motifs_to_physics, mine_motifs, motif_enrichment
from rishiq.discovery.novelty import write_novelty_dossier
from rishiq.discovery.ranker import motif_to_candidate, novelty_gate, rank_motifs
from rishiq.discovery.report import write_discovery_report
from rishiq.discovery.significance import (
    cluster_enrichment_bootstrap,
    mine_feature_combinations,
)
from rishiq.discovery.surprisal import compute_surprisal
from rishiq.discovery.temporal import first_appearances, motif_temporal
from rishiq.discovery.translation import (
    aggregate_modernization_by_decade,
    lexicon_hits,
    translation_shift_graph,
)
from rishiq.fingerprints import load_all_fingerprints
from rishiq.models import AnnotationLabel, FeatureAnnotation

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANN = ROOT / "results/exploratory/pd_pilot/annotations.parquet"
DEFAULT_SCORES = ROOT / "results/exploratory/pd_pilot/passage_scores.parquet"
DEFAULT_CORPUS = ROOT / "corpus/development/pd_passages.parquet"
OUT = ROOT / "results/discovery"
CAND_DIR = ROOT / "results/discovery_candidates"
NOVELTY_DIR = ROOT / "novelty"
CLAIMS_PATH = ROOT / "ontology/claims_vs_data.yaml"
FP_DIR = ROOT / "ontology/physics_fingerprints"

SANSKRITISH = {
    "vedanta",
    "upanishad",
    "sanskrit_vedanta",
    "advaita",
    "samkhya",
    "nyaya",
    "vaisheshika",
    "yoga",
    "buddhist_sanskrit",
}


def _load_annotations(path: Path) -> dict[str, list[FeatureAnnotation]]:
    df = pd.read_parquet(path)
    by: dict[str, list[FeatureAnnotation]] = defaultdict(list)
    for row in df.to_dict(orient="records"):
        # normalize label
        lab = row.get("label")
        if lab in ("1", 1, "YES", "yes", True):
            row["label"] = AnnotationLabel.YES
        elif lab in ("0", 0, "NO", "no", False):
            row["label"] = AnnotationLabel.NO
        elif lab in ("U", "AMBIGUOUS", "ambiguous"):
            row["label"] = AnnotationLabel.AMBIGUOUS
        else:
            row["label"] = AnnotationLabel.NA
        by[row["passage_id"]].append(FeatureAnnotation.model_validate(row))
    return dict(by)


def _split_by_work(scores: pd.DataFrame, seed: int = 42) -> dict[str, list[str]]:
    """Work-level discovery / replication split stratified by role (no within-work leakage)."""
    discovery_works: list[str] = []
    replication_works: list[str] = []
    for role in sorted(scores["role"].dropna().unique()):
        works = sorted(
            scores.loc[scores["role"] == role, "work"].dropna().unique().tolist()
        )
        if not works:
            continue
        mid = max(1, len(works) // 2) if len(works) > 1 else 1
        # if only one work in role, keep it in discovery for motif mining; replication notes absence
        if len(works) == 1:
            discovery_works.extend(works)
        else:
            discovery_works.extend(works[:mid])
            replication_works.extend(works[mid:])
    discovery_works = sorted(set(discovery_works))
    replication_works = sorted(set(replication_works) - set(discovery_works))
    disc_pids = scores[scores["work"].isin(discovery_works)]["passage_id"].tolist()
    repl_pids = scores[scores["work"].isin(replication_works)]["passage_id"].tolist()
    return {
        "discovery_works": discovery_works,
        "replication_works": replication_works,
        "discovery_passages": disc_pids,
        "replication_passages": repl_pids,
        "seed": seed,
        "note": "Stratified by role, split by work to avoid within-work leakage. Confirmatory remains locked.",
    }


# Approximate historical ranges when passage-level dating is unavailable (wide, honest).
TRADITION_DATE_PRIORS: dict[str, tuple[int, int]] = {
    "vedanta_pd": (-800, 800),
    "greek_lucretius_pd": (-99, -55),
    "greek_timaeus_pd": (-400, -350),
    "buddhist_dhammapada_pd": (-300, 400),
    "chinese_ddj_pd": (-400, 200),
    "modern_physics": (1900, 2020),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    NOVELTY_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT / "corpus/discovery_split").mkdir(parents=True, exist_ok=True)
    (ROOT / "corpus/replication_split").mkdir(parents=True, exist_ok=True)

    if not DEFAULT_ANN.exists():
        raise SystemExit(f"Missing annotations: {DEFAULT_ANN} — run PD pilot first")

    anns_by = _load_annotations(DEFAULT_ANN)
    scores = pd.read_parquet(DEFAULT_SCORES)

    meta: dict[str, dict] = {}
    dating: dict[str, dict] = {}
    passage_features: dict[str, set[str]] = {}

    corpus_df = None
    if DEFAULT_CORPUS.exists():
        corpus_df = pd.read_parquet(DEFAULT_CORPUS)
        for row in corpus_df.to_dict(orient="records"):
            pid = row["passage_id"]
            meta[pid] = {
                "tradition": row.get("tradition", "unknown"),
                "work_id": row.get("work", "unknown"),
                "role": row.get("role", ""),
                "char_len": len(row.get("translation") or row.get("source_text") or ""),
                "translation_year": row.get("translation_year"),
            }
            dating[pid] = {
                "year_start": row.get("estimated_date_min"),
                "year_end": row.get("estimated_date_max"),
                "tradition": row.get("tradition"),
                "work_id": row.get("work"),
            }
            if dating[pid]["year_start"] is None and dating[pid]["year_end"] is None:
                prior = TRADITION_DATE_PRIORS.get(str(row.get("tradition", "")).lower())
                if prior:
                    dating[pid]["year_start"], dating[pid]["year_end"] = prior
                    dating[pid]["date_source"] = "tradition_prior_wide_range"

    for _, row in scores.iterrows():
        pid = row["passage_id"]
        if pid not in meta:
            meta[pid] = {
                "tradition": row.get("tradition", "unknown"),
                "work_id": row.get("work", "unknown"),
                "role": row.get("role", ""),
                "char_len": 0,
            }

    # Graphs (physics-agnostic)
    graphs = []
    for pid, anns in anns_by.items():
        g = extract_passage_graph(pid, anns)
        graphs.append(g)
        yes = {
            a.feature_id
            for a in anns
            if a.label == AnnotationLabel.YES and a.evidence.strip()
        }
        passage_features[pid] = yes

    graphs_path = OUT / "passage_graphs.jsonl"
    with graphs_path.open("w", encoding="utf-8") as f:
        for g in graphs:
            f.write(g.model_dump_json() + "\n")

    # Split
    split = _split_by_work(scores)
    (ROOT / "corpus/discovery_split/split_manifest.json").write_text(
        json.dumps(split, indent=2), encoding="utf-8"
    )
    (ROOT / "corpus/replication_split/split_manifest.json").write_text(
        json.dumps(
            {
                "replication_works": split["replication_works"],
                "replication_passages": split["replication_passages"],
                "note": split["note"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    discovery_set = set(split["discovery_passages"])
    disc_graphs = [g for g in graphs if g.passage_id in discovery_set] or graphs

    # Motif mining WITHOUT physics
    motifs = mine_motifs(disc_graphs, meta=meta, min_support=3)

    # Post-hoc physics mapping
    fps = load_all_fingerprints(FP_DIR)
    fp_sets = {name: set(fp.active_features()) for name, fp in fps.items()}
    motifs = map_motifs_to_physics(motifs, fp_sets)
    (OUT / "motifs_discovery_split.json").write_text(
        json.dumps([m.model_dump() for m in motifs], indent=2), encoding="utf-8"
    )

    # Enrichment on FULL exploratory graphs (labeled exploratory); motifs mined on discovery split.
    # Recompute tradition counts from all graphs for enrichment denominators.
    full_motifs = mine_motifs(graphs, meta=meta, min_support=3)
    # carry physics map from discovery motif signatures where possible
    sig_to_phys = {
        "|".join(m.signature): (m.nearest_physics, m.physics_family) for m in motifs
    }
    full_motifs = map_motifs_to_physics(full_motifs, fp_sets)
    for m in full_motifs:
        key = "|".join(m.signature)
        if key in sig_to_phys and m.nearest_physics in (None, "unrelated_or_generic"):
            np_, fam = sig_to_phys[key]
            if np_:
                m.nearest_physics = np_
                m.physics_family = fam  # type: ignore[assignment]

    n_target = int((scores["role"] == "target").sum())
    n_control = int(scores["role"].isin(["control", "negative_control"]).sum())
    target_trad = {
        str(t).lower()
        for t in scores.loc[scores["role"] == "target", "tradition"].unique()
    }
    control_trad = {
        str(t).lower()
        for t in scores.loc[
            scores["role"].isin(["control", "negative_control"]), "tradition"
        ].unique()
    }
    enrichments = {}
    for m in full_motifs:
        m.traditions = {str(k).lower(): v for k, v in m.traditions.items()}
        enrichments[m.motif_id] = motif_enrichment(
            m,
            target_trad,
            control_trad,
            n_target=max(n_target, 1),
            n_control=max(n_control, 1),
        )

    ranked = rank_motifs(full_motifs, enrichments)
    motifs = full_motifs  # report uses enriched full-corpus motif table
    (OUT / "motifs.json").write_text(
        json.dumps([m.model_dump() for m in motifs], indent=2), encoding="utf-8"
    )
    (OUT / "motif_rankings.json").write_text(json.dumps(ranked, indent=2), encoding="utf-8")
    (OUT / "motif_enrichments.json").write_text(
        json.dumps(enrichments, indent=2), encoding="utf-8"
    )

    # Cluster-aware work-level bootstrap for top motifs
    passage_to_work = {
        row["passage_id"]: row["work"] for _, row in scores.iterrows()
    }
    passage_to_role = {
        row["passage_id"]: row["role"] for _, row in scores.iterrows()
    }
    all_works = {
        row["work"]: row["role"]
        for _, row in scores.drop_duplicates("work").iterrows()
    }
    cluster_stats = {}
    for row in ranked[:15]:
        m = next(x for x in motifs if x.motif_id == row["motif_id"])
        cluster_stats[m.motif_id] = cluster_enrichment_bootstrap(
            m,
            passage_to_work=passage_to_work,
            passage_to_role=passage_to_role,
            all_works=all_works,
            n_boot=499,
            seed=42,
        )
    (OUT / "motif_cluster_bootstrap.json").write_text(
        json.dumps(cluster_stats, indent=2), encoding="utf-8"
    )

    # Combinatorial feature co-occurrence (physics-label-free)
    combos = mine_feature_combinations(passage_features, meta, min_support=3, max_size=4)
    (OUT / "feature_combinations.json").write_text(
        json.dumps(combos, indent=2), encoding="utf-8"
    )

    # Surprisal
    control_ids = set(
        scores.loc[scores["role"].isin(["control", "negative_control"]), "passage_id"]
    )
    anomalies = compute_surprisal(graphs, control_ids=control_ids, meta=meta)
    (OUT / "surprisal.json").write_text(json.dumps(anomalies[:100], indent=2), encoding="utf-8")

    # Temporal
    temporal = first_appearances(passage_features, dating)
    motif_passages = {m.motif_id: m.passages for m in motifs}
    temporal["motifs"] = motif_temporal(motif_passages, dating)
    (OUT / "temporal.json").write_text(json.dumps(temporal, indent=2, default=str), encoding="utf-8")

    # Translation modernization (corpus-level exploratory) + aligned shift graphs
    trans_rows = []
    if corpus_df is not None:
        qs_map = scores.set_index("passage_id")["QS"].to_dict()
        for row in corpus_df.to_dict(orient="records"):
            text = row.get("translation") or ""
            trans_rows.append(
                {
                    "translation_year": row.get("translation_year"),
                    "text": text,
                    "qs": qs_map.get(row["passage_id"]),
                    "lexicon": lexicon_hits(text),
                }
            )
    shift_graphs = []
    demo_corpus = ROOT / "corpus/development/translation_demo_passages.parquet"
    demo_ann = ROOT / "results/exploratory/translation_demo/annotations.parquet"
    demo_scores = ROOT / "results/exploratory/translation_demo/passage_scores.parquet"
    if demo_corpus.exists() and demo_ann.exists() and demo_scores.exists():
        dcorp = pd.read_parquet(demo_corpus)
        dann = _load_annotations(demo_ann)
        dqs = pd.read_parquet(demo_scores).set_index("passage_id")["QS"].to_dict()
        families: dict[str, list] = {}
        for row in dcorp.to_dict(orient="records"):
            fam = str(row.get("section") or row["passage_id"].split("__")[0])
            yes = {
                a.feature_id
                for a in dann.get(row["passage_id"], [])
                if a.label == AnnotationLabel.YES and a.evidence.strip()
            }
            families.setdefault(fam, []).append(
                {
                    "year": row.get("translation_year"),
                    "translation_id": row.get("translation_id") or row["passage_id"],
                    "text": row.get("translation") or "",
                    "feature_yes": yes,
                    "qs": dqs.get(row["passage_id"]),
                }
            )
        for fam, vers in families.items():
            g = translation_shift_graph(vers)
            g["passage_family"] = fam
            shift_graphs.append(g)
    translation = {
        "decade_modernization": aggregate_modernization_by_decade(trans_rows),
        "aligned_shift_graphs": shift_graphs,
        "status": "exploratory",
        "note": (
            "Decade lexicon vs QS is exploratory. Aligned shift graphs use "
            "synthetic multi-translation demo until licensed Sanskrit pairs exist."
        ),
    }
    (OUT / "translation_modernization.json").write_text(
        json.dumps(translation, indent=2, default=str), encoding="utf-8"
    )

    # Claims vs data
    if not CLAIMS_PATH.exists():
        CLAIMS_PATH.write_text(
            yaml.dump({"claims": load_claims()}, default_flow_style=False),
            encoding="utf-8",
        )
    claims = load_claims(CLAIMS_PATH)
    claim_results = [
        evaluate_claim(
            c,
            anns_by,
            tradition_filter={
                str(t).lower()
                for t in scores.loc[scores["role"] == "target", "tradition"].unique()
            },
            meta=meta,
        )
        for c in claims
    ]
    (OUT / "claims_vs_data.json").write_text(
        json.dumps(claim_results, indent=2), encoding="utf-8"
    )
    write_claims_report(OUT / "claims_vs_data.md", claim_results)
    # ensure full JSON not overwritten
    (OUT / "claims_vs_data.json").write_text(
        json.dumps(claim_results, indent=2), encoding="utf-8"
    )

    # Atlas
    atlas = build_motif_atlas(motifs)
    (OUT / "motif_atlas.json").write_text(json.dumps(atlas, indent=2), encoding="utf-8")

    # Candidates + novelty dossiers for top 5
    candidates: list[dict] = []
    for row in ranked[:5]:
        m = next(x for x in motifs if x.motif_id == row["motif_id"])
        enr = enrichments[m.motif_id]
        cand = motif_to_candidate(m, enr, row)
        # attach cluster bootstrap into control_comparison
        cs = cluster_stats.get(m.motif_id, {})
        cand.control_comparison = json.dumps({"passage_enrichment": enr, "cluster_bootstrap": cs})
        if cs.get("enrichment_work_level") is not None:
            cand.effect_size = cs.get("enrichment_work_level")
        cand = novelty_gate(cand)
        candidates.append(cand.model_dump())
        cpath = CAND_DIR / f"{cand.candidate_id}.json"
        cpath.write_text(json.dumps(cand.model_dump(), indent=2), encoding="utf-8")
        write_novelty_dossier(
            NOVELTY_DIR / f"{m.motif_id}.md",
            candidate_id=cand.candidate_id,
            title=cand.title,
            empirical=json.dumps(enr),
            passages=", ".join(m.passages[:8]),
            apparent_new="Unsupervised structural motif with post-hoc physics mapping; quantitative enrichment vs controls pending literature check.",
            search_terms=[
                " ".join(m.signature[:4]),
                m.nearest_physics or "",
                "Sanskrit structural ontology",
                "field metaphysics Indology",
            ],
        )

    # Replication check: recompute support of top motifs on replication split
    repl_set = set(split["replication_passages"])
    failed_repl = []
    if repl_set:
        repl_graphs = [g for g in graphs if g.passage_id in repl_set]
        repl_motifs = mine_motifs(repl_graphs, meta=meta, min_support=2)
        repl_sigs = {"|".join(m.signature) for m in repl_motifs}
        for row in ranked[:10]:
            sig = "|".join(row["signature"])
            if sig not in repl_sigs:
                # also check subset presence in any repl graph
                atoms = set(row["signature"])
                hit = any(atoms <= g.motif_signature() for g in repl_graphs)
                if not hit:
                    failed_repl.append(
                        f"{row['motif_id']} signature not recovered on replication works"
                    )

    top_findings = [
        "System B discovery pipeline executed: graphs → unsupervised motifs → post-hoc physics map.",
        "No candidate auto-promoted to STRONG_DISCOVERY_CANDIDATE (novelty gate + literature review required).",
        f"Combinatorial mining found {len(combos)} feature co-occurrence patterns (min_support=3).",
        f"Cluster-aware bootstrap computed for {len(cluster_stats)} top motifs (work-level).",
    ]
    # Field-like motifs enriched in controls more than Vedānta under heuristic = important negative-ish discovery path
    field_control_heavy = [
        mid
        for mid, e in enrichments.items()
        if (e.get("enrichment") or 0) == 0 and e.get("n_control", 0) > 0 and e.get("n_target", 0) == 0
    ]
    if field_control_heavy:
        top_findings.append(
            f"{len(field_control_heavy)} motifs appear in historical controls but not target "
            "under current annotator — weakens Sanskrit-specific quantum readings for those structures."
        )
    # Highlight field-like non-quantum claim results
    for c in claim_results:
        if "field" in str(c.get("BEST_PHYSICS_MATCH", "")).lower() and not c.get(
            "QUANTUM_SUPPORTED"
        ):
            top_findings.append(
                f"Claims-vs-data: '{c['claim']}' best matches {c['BEST_PHYSICS_MATCH']} "
                f"(quantum components unsupported in this sample)."
            )
        if "quantum" in c.get("claim", "").lower() and not c.get("QUANTUM_SUPPORTED"):
            if c.get("SUPPORTED_STRUCTURAL_COMPONENTS") or c.get("BEST_PHYSICS_MATCH") == "unsupported_in_sample":
                top_findings.append(
                    f"Popular claim divergence: '{c['claim']}' lacks quantum-specific features in sample."
                )
    if anomalies:
        clean = [a for a in anomalies if a.get("anomaly_candidate")]
        if clean:
            top_findings.append(
                f"Surprisal engine flagged {len(clean)} anomaly candidates after artifact guards."
            )
        else:
            top_findings.append(
                "High-surprisal passages were largely artifact-flagged or not above clean threshold."
            )
    if shift_graphs:
        top_findings.append(
            f"Translation-shift graphs built for {len(shift_graphs)} aligned passage families (demo)."
        )

    payload = {
        "top_findings": top_findings,
        "ranked_motifs": ranked,
        "enrichments": enrichments,
        "cluster_bootstrap": cluster_stats,
        "feature_combinations": combos[:30],
        "temporal": temporal,
        "translation": translation,
        "anomalies": anomalies[:15],
        "claims": claim_results,
        "atlas": atlas,
        "candidates": candidates,
        "failed_replication": failed_repl,
    }
    (OUT / "discovery_payload.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    report_path = write_discovery_report(OUT, payload)
    # project-facing copy
    (ROOT / "discovery_report.md").write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "n_graphs": len(graphs),
                "n_motifs": len(motifs),
                "n_candidates": len(candidates),
                "report": str(ROOT / "discovery_report.md"),
                "failed_replication": failed_repl[:5],
                "warning": "EXPLORATORY_SYSTEM_B_NOT_CONFIRMATORY",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
