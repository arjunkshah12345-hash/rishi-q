"""Development-only method selection for theory validation v2.

Prespecified modest candidate set. Select using TRAIN fit + DEVELOPMENT metrics only.
Never loads final holdout.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from rishiq.isef2027.contamination import ContaminationState, EvidenceRole
from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance
from rishiq.isef2027.concept_graph import ConceptGraph
from rishiq.isef2027.graph_similarity import structural_similarity_bundle
from rishiq.isef2027.graph_templates import build_all_theory_graph_templates
from rishiq.isef2027.validation_ledger import append_validation_ledger

GIVEAWAY_TERMS = [
    r"\bquantum\b",
    r"\brelativity\b",
    r"\brelativistic\b",
    r"\bnewton\b",
    r"\bnewtonian\b",
    r"\bmaxwell\b",
    r"\bentropy\b",
    r"\bthermodynamic\b",
    r"\bthermodynamics\b",
    r"\bphoton\b",
    r"\belectron\b",
    r"\bhilbert\b",
    r"\bschrödinger\b",
    r"\bschrodinger\b",
    r"\bspacetime\b",
    r"\belectromagnetic\b",
    r"\belectromagnetism\b",
    r"\beinstein\b",
    r"\bplanck\b",
    r"\bbohr\b",
]

MASK_RE = re.compile("|".join(GIVEAWAY_TERMS), re.I)

# Prespecified graph weight grid — evaluate on DEVELOPMENT only AFTER real extractor.
# Prior lexical-proxy selection (typed=1.0, hungarian=0.0) is RETIRED_PROXY_SELECTION.
GRAPH_WEIGHT_GRID = [
    (1.0, 0.0),
    (0.75, 0.25),
    (0.5, 0.5),
    (0.25, 0.75),
    (0.0, 1.0),
]
RETIRED_PROXY_SELECTION = {"typed_weight": 1.0, "hungarian_weight": 0.0, "status": "RETIRED_PROXY_SELECTION"}


def mask_giveaway_vocab(text: str) -> str:
    return MASK_RE.sub("[MASKED]", text)


def _load_split(root: Path, split: str) -> list[dict[str, Any]]:
    """Load train or development only — never final_holdout."""
    if split not in {"train", "development"}:
        raise ValueError(f"refusing to load split={split} in development runner")
    path = root / "data/theory_validation_v2/passages" / f"{split if split != 'development' else 'development'}.jsonl"
    if split == "train":
        path = root / "data/theory_validation_v2/passages/train.jsonl"
    if not path.exists():
        raise FileNotFoundError(path)
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def _metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    labels = sorted(set(y_true) | set(y_pred))
    prec, rec, f1s, supp = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    top1 = float(np.mean([a == b for a, b in zip(y_true, y_pred)]))
    # top-2 via ranks if available separately
    per = {
        lab: {
            "precision": float(prec[i]),
            "recall": float(rec[i]),
            "f1": float(f1s[i]),
            "support": int(supp[i]),
        }
        for i, lab in enumerate(labels)
    }
    return {
        "top1_accuracy": top1,
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "labels": labels,
        "per_theory": per,
    }


def _bootstrap_ci(y_true: list[str], y_pred: list[str], n: int = 400, seed: int = 0) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y_true))
    scores = []
    for _ in range(n):
        samp = rng.choice(idx, size=len(idx), replace=True)
        yt = [y_true[i] for i in samp]
        yp = [y_pred[i] for i in samp]
        scores.append(float(np.mean([a == b for a, b in zip(yt, yp)])))
    return {
        "top1_mean": float(np.mean(scores)),
        "top1_ci95_low": float(np.percentile(scores, 2.5)),
        "top1_ci95_high": float(np.percentile(scores, 97.5)),
    }


def _fit_predict_candidates(
    train: list[dict],
    dev: list[dict],
    *,
    masked: bool,
) -> list[dict[str, Any]]:
    def tx(rows):
        return [mask_giveaway_vocab(r["text"]) if masked else r["text"] for r in rows]

    Xtr, ytr = tx(train), [r["theory_label"] for r in train]
    Xdv, ydv = tx(dev), [r["theory_label"] for r in dev]
    results = []

    # majority baseline
    maj = Counter(ytr).most_common(1)[0][0]
    y_maj = [maj] * len(ydv)
    results.append({"model": "majority_baseline", "metrics": _metrics(ydv, y_maj), "hyperparameters": {"label": maj}})

    # random baseline (seeded)
    rng = np.random.default_rng(0)
    labs = sorted(set(ytr))
    y_rand = [labs[i] for i in rng.integers(0, len(labs), size=len(ydv))]
    results.append({"model": "random_baseline", "metrics": _metrics(ydv, y_rand), "hyperparameters": {"seed": 0}})

    candidates = [
        ("tfidf_unigram_linearsvc", TfidfVectorizer(ngram_range=(1, 1), min_df=1), LinearSVC(random_state=0)),
        ("tfidf_unigram_bigram_linearsvc", TfidfVectorizer(ngram_range=(1, 2), min_df=1), LinearSVC(random_state=0)),
        (
            "tfidf_unigram_bigram_logreg",
            TfidfVectorizer(ngram_range=(1, 2), min_df=1),
            LogisticRegression(max_iter=2000, random_state=0),
        ),
    ]
    for name, vec, clf in candidates:
        pipe = Pipeline([("tfidf", vec), ("clf", clf)])
        pipe.fit(Xtr, ytr)
        yhat = list(pipe.predict(Xdv))
        m = _metrics(ydv, yhat)
        m["bootstrap"] = _bootstrap_ci(ydv, yhat)
        # ranks / top2 for linear models
        if hasattr(pipe.named_steps["clf"], "decision_function"):
            scores = np.atleast_2d(pipe.decision_function(Xdv))
            classes = list(pipe.named_steps["clf"].classes_)
            if scores.shape[1] == 1 and len(classes) == 2:
                scores = np.column_stack([-scores[:, 0], scores[:, 0]])
            top2 = []
            ranks = []
            for i, yt in enumerate(ydv):
                order = np.argsort(-scores[i])
                ranked = [classes[int(j)] for j in order]
                top2.append(yt in ranked[:2])
                ranks.append(ranked.index(yt) + 1 if yt in ranked else len(ranked))
            m["top2_accuracy"] = float(np.mean(top2))
            m["mean_correct_rank"] = float(np.mean(ranks))
        results.append(
            {
                "model": name,
                "metrics": m,
                "hyperparameters": {"vectorizer": str(vec), "clf": str(clf)},
            }
        )

    # centroid similarity
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = vec.fit_transform(Xtr)
    centroids = {}
    for lab in sorted(set(ytr)):
        idx = [i for i, y in enumerate(ytr) if y == lab]
        centroids[lab] = np.asarray(X[idx].mean(axis=0)).ravel()
    Xd = vec.transform(Xdv)
    labels = list(centroids)
    C = np.stack([centroids[l] for l in labels])
    xa = np.asarray(Xd.toarray(), dtype=float)
    Xn = xa / (np.linalg.norm(xa, axis=1, keepdims=True) + 1e-12)
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    sims = Xn @ Cn.T
    y_cent = [labels[int(i)] for i in sims.argmax(axis=1)]
    m = _metrics(ydv, y_cent)
    m["bootstrap"] = _bootstrap_ci(ydv, y_cent)
    order = np.argsort(-sims, axis=1)
    m["top2_accuracy"] = float(np.mean([ydv[i] in [labels[j] for j in order[i, :2]] for i in range(len(ydv))]))
    results.append({"model": "tfidf_centroid", "metrics": m, "hyperparameters": {"ngram": (1, 2)}})

    return results


def _load_fingerprints(root: Path):
    build_all_theory_graph_templates(root)
    gdir = root / "ontology/concept_graph"
    graphs = {}
    for p in gdir.glob("template_fp_*.json"):
        g = ConceptGraph.model_validate(json.loads(p.read_text(encoding="utf-8")))
        tid = p.stem.replace("template_fp_", "")
        graphs[tid] = g
    return graphs


def task_b_fingerprint_retrieval(
    root: Path,
    rows: list[dict],
    *,
    typed_w: float,
    hung_w: float,
    masked: bool = False,
    extractor: str = "structural",
) -> dict[str, Any]:
    """Task B Stage 2: theory retrieval from extracted structure only.

    extractor:
      - structural: claim-bearing deterministic theory-agnostic extractor
      - lexical_proxy: LEXICAL_GRAPH_PROXY_BASELINE (comparison only)
    """
    from rishiq.isef2027.structural_extractor import EXTRACTOR_VERSION, extract_structure, lexical_graph_proxy_baseline

    fps = _load_fingerprints(root)
    ranks = []
    top1 = []
    top2 = []
    margins = []
    mrr = []
    empty_n = 0
    for r in rows:
        text = mask_giveaway_vocab(r["text"]) if masked else r["text"]
        if extractor == "lexical_proxy":
            pg = lexical_graph_proxy_baseline(text, fps)
            method_tag = "LEXICAL_GRAPH_PROXY_BASELINE"
        else:
            ext = extract_structure(text)
            pg = ext.to_concept_graph(graph_id=f"passage_{r['passage_id']}")
            method_tag = EXTRACTOR_VERSION
        if not pg.nodes:
            empty_n += 1

        scores = {}
        for tid, g in fps.items():
            bund = structural_similarity_bundle(pg, g, typed_weight=typed_w, hungarian_weight=hung_w)
            scores[tid] = bund["primary_structural"]
        ordered = sorted(scores, key=scores.get, reverse=True)
        yt = r["theory_label"]
        rank = ordered.index(yt) + 1 if yt in ordered else len(ordered)
        ranks.append(rank)
        top1.append(ordered[0] == yt)
        top2.append(yt in ordered[:2])
        mrr.append(1.0 / rank)
        best = scores[ordered[0]]
        second = scores[ordered[1]] if len(ordered) > 1 else 0.0
        correct = scores.get(yt, 0.0)
        margins.append(correct - second if ordered[0] == yt else correct - best)

    claim_bearing = extractor != "lexical_proxy"
    return {
        "task": "B_structural_fingerprint_retrieval",
        "extractor": method_tag if extractor != "lexical_proxy" else "LEXICAL_GRAPH_PROXY_BASELINE",
        "claim_bearing": claim_bearing,
        "typed_weight": typed_w,
        "hungarian_weight": hung_w,
        "masked": masked,
        "n": len(rows),
        "empty_extraction_n": empty_n,
        "mean_correct_rank": float(np.mean(ranks)) if ranks else None,
        "mrr": float(np.mean(mrr)) if mrr else None,
        "top1_retrieval": float(np.mean(top1)) if top1 else None,
        "top2_retrieval": float(np.mean(top2)) if top2 else None,
        "mean_correct_vs_next_margin": float(np.mean(margins)) if margins else None,
        "note": (
            "Fingerprints remain AI_DRAFT_PENDING_STUDENT_REVIEW; "
            + ("primary structural extractor." if claim_bearing else "baseline only — not claim-bearing.")
        ),
    }


def select_graph_weights_on_dev(root: Path, dev: list[dict]) -> dict[str, Any]:
    grid = []
    for tw, hw in GRAPH_WEIGHT_GRID:
        res = task_b_fingerprint_retrieval(
            root, dev, typed_w=tw, hung_w=hw, masked=False, extractor="structural"
        )
        grid.append(res)
    best = max(grid, key=lambda x: (x["mrr"] or 0.0))
    return {
        "grid": grid,
        "selected": {"typed_weight": best["typed_weight"], "hungarian_weight": best["hungarian_weight"]},
        "selection_criterion": "max_dev_mrr_structural_extractor",
        "selected_on": "development_only",
        "retired_proxy_selection": RETIRED_PROXY_SELECTION,
        "extractor": "structural_extractor_deterministic_v1",
    }


def leave_one_source_out(train: list[dict], key: str = "work_id") -> dict[str, Any]:
    groups = sorted({r[key] for r in train})
    folds = []
    for g in groups:
        tr = [r for r in train if r[key] != g]
        te = [r for r in train if r[key] == g]
        if len(tr) < 5 or len(te) < 2:
            continue
        pipe = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                ("clf", LinearSVC(random_state=0)),
            ]
        )
        pipe.fit([r["text"] for r in tr], [r["theory_label"] for r in tr])
        yhat = list(pipe.predict([r["text"] for r in te]))
        ytrue = [r["theory_label"] for r in te]
        folds.append(
            {
                "held_out_group": g,
                "n_test": len(te),
                "top1": float(np.mean([a == b for a, b in zip(ytrue, yhat)])),
                "macro_f1": float(f1_score(ytrue, yhat, average="macro", zero_division=0)),
            }
        )
    return {
        "grouping": key,
        "n_folds": len(folds),
        "folds": folds,
        "mean_top1": float(np.mean([f["top1"] for f in folds])) if folds else None,
        "mean_macro_f1": float(np.mean([f["macro_f1"] for f in folds])) if folds else None,
    }


def estimate_calibration_variance(dev: list[dict], scores_by_passage: dict[str, float] | None = None) -> dict[str, Any]:
    """Estimate within/between work variance using development structural scores."""
    by_work: dict[str, list[float]] = defaultdict(list)
    missing = 0
    for r in dev:
        if scores_by_passage and r["passage_id"] in scores_by_passage:
            s = scores_by_passage[r["passage_id"]]
        else:
            missing += 1
            continue
        by_work[r["work_id"]].append(s)

    work_means = {w: float(np.mean(v)) for w, v in by_work.items() if v}
    if len(work_means) < 2:
        return {
            "status": "INSUFFICIENT_WORKS",
            "between_work_sd": "UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE",
            "within_work_sd": "UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE",
            "icc": None,
        }

    between = float(np.std(list(work_means.values()), ddof=1))
    within_vars = [float(np.var(v, ddof=1)) for v in by_work.values() if len(v) > 1]
    within = float(np.sqrt(np.mean(within_vars))) if within_vars else float("nan")
    n_bar = float(np.mean([len(v) for v in by_work.values()]))
    icc = None
    if within == within and between == between and (between**2 + within**2) > 0:
        icc = float(between**2 / (between**2 + within**2))

    rng = np.random.default_rng(0)
    works = list(by_work)
    boot_b, boot_w, boot_icc = [], [], []
    for _ in range(400):
        samp = [works[i] for i in rng.integers(0, len(works), size=len(works))]
        wm = {w: float(np.mean(by_work[w])) for w in samp}
        b = float(np.std(list(wm.values()), ddof=1)) if len(wm) > 1 else float("nan")
        wvars = [float(np.var(by_work[w], ddof=1)) for w in samp if len(by_work[w]) > 1]
        w = float(np.sqrt(np.mean(wvars))) if wvars else float("nan")
        boot_b.append(b)
        boot_w.append(w)
        if w == w and b == b and (b**2 + w**2) > 0:
            boot_icc.append(b**2 / (b**2 + w**2))

    return {
        "status": "FROM_DEV_STRUCTURAL_CORRECT_SCORE",
        "n_works": len(by_work),
        "mean_passages_per_work": n_bar,
        "between_work_sd": between,
        "within_work_sd": within,
        "icc": icc,
        "between_work_sd_ci95": [float(np.nanpercentile(boot_b, 2.5)), float(np.nanpercentile(boot_b, 97.5))],
        "within_work_sd_ci95": [float(np.nanpercentile(boot_w, 2.5)), float(np.nanpercentile(boot_w, 97.5))],
        "icc_ci95": [float(np.nanpercentile(boot_icc, 2.5)), float(np.nanpercentile(boot_icc, 97.5))] if boot_icc else None,
        "missingness_rate_estimate": float(missing / max(1, len(dev))),
        "score_definition": "correct_theory_structural_similarity_on_development",
        "ready_to_freeze_N": False,
        "note": "Work-level bootstrap; fingerprints still pending student review.",
    }


def _structural_scores_by_passage(root: Path, rows: list[dict], typed_w: float, hung_w: float) -> dict[str, float]:
    from rishiq.isef2027.structural_extractor import extract_structure

    fps = _load_fingerprints(root)
    out: dict[str, float] = {}
    for r in rows:
        pg = extract_structure(r["text"]).to_concept_graph(graph_id=r["passage_id"])
        yt = r["theory_label"]
        if yt not in fps:
            continue
        bund = structural_similarity_bundle(pg, fps[yt], typed_weight=typed_w, hungarian_weight=hung_w)
        out[r["passage_id"]] = bund["primary_structural"]
    return out


def run_development_method_selection(root: Path) -> dict[str, Any]:
    train = _load_split(root, "train")
    dev = _load_split(root, "development")

    raw_models = _fit_predict_candidates(train, dev, masked=False)
    masked_models = _fit_predict_candidates(train, dev, masked=True)

    ranked = sorted(
        [m for m in raw_models if not m["model"].endswith("baseline")],
        key=lambda m: m["metrics"]["macro_f1"],
        reverse=True,
    )
    best_a = ranked[0] if ranked else raw_models[0]

    weight_sel = select_graph_weights_on_dev(root, dev)
    tw = weight_sel["selected"]["typed_weight"]
    hw = weight_sel["selected"]["hungarian_weight"]
    task_b = task_b_fingerprint_retrieval(root, dev, typed_w=tw, hung_w=hw, masked=False, extractor="structural")
    task_b_masked = task_b_fingerprint_retrieval(root, dev, typed_w=tw, hung_w=hw, masked=True, extractor="structural")
    task_b_lexical = task_b_fingerprint_retrieval(
        root, dev, typed_w=tw, hung_w=hw, masked=False, extractor="lexical_proxy"
    )

    loso = leave_one_source_out(train + dev, key="work_id")
    loao = leave_one_source_out(train + dev, key="author_family")
    losf = leave_one_source_out(train + dev, key="source_family")

    hard = [r for r in dev if r.get("hard_negative_or_cross_theory_context")]
    hard_metrics = None
    if hard and best_a["model"].startswith("tfidf"):
        pipe = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
                ("clf", LinearSVC(random_state=0)),
            ]
        )
        pipe.fit([r["text"] for r in train], [r["theory_label"] for r in train])
        yhat = list(pipe.predict([r["text"] for r in hard]))
        hard_metrics = _metrics([r["theory_label"] for r in hard], yhat)

    scores = _structural_scores_by_passage(root, dev, tw, hw)
    var_est = estimate_calibration_variance(dev, scores)

    from rishiq.isef2027.power_hier import PowerAssumptions, simulate_delta_q_power

    power_table = []
    bw = var_est["between_work_sd"] if isinstance(var_est.get("between_work_sd"), float) else 0.08
    ww = var_est["within_work_sd"] if isinstance(var_est.get("within_work_sd"), float) else 0.12
    n_sim = 400
    for effect, scenario in [(0.02, "pessimistic"), (0.05, "base"), (0.08, "base"), (0.12, "optimistic")]:
        for n_works in [6, 10, 15]:
            for ppw in [3, 5]:
                ass = PowerAssumptions(
                    effect_delta_q=effect,
                    n_works_per_arm=n_works,
                    passages_per_work=ppw,
                    between_work_sd=bw,
                    within_work_sd=ww,
                    n_sim=n_sim,
                    n_perm=79,
                    notes="structural_dev_variance_calibrated",
                )
                sim = simulate_delta_q_power(ass)
                power_table.append(
                    {
                        "effect": effect,
                        "works_per_arm": n_works,
                        "passages_per_work": ppw,
                        "power": sim.get("empirical_power"),
                        "estimated_power": sim.get("empirical_power"),
                        "mc_se": sim.get("monte_carlo_se"),
                        "sim_interval_95": sim.get("power_sim_interval_95"),
                        "scenario": scenario,
                        "n_sim": n_sim,
                    }
                )

    train_sf = {r.get("source_family", r["work_id"]) for r in train}
    dev_sf = {r.get("source_family", r["work_id"]) for r in dev}
    train_af = {r.get("author_family") for r in train}
    dev_af = {r.get("author_family") for r in dev}

    method_freeze = {
        "status": "NOT_READY_TO_FREEZE",
        "reasons": [
            "physics_fingerprints_verified=false (student review required)",
            "Stage-1 extraction gold annotations awaiting student approval",
            "true final method holdout NOT_BUILT (correct until after freeze)",
            "confirmatory corpus feasibility may constrain independent N",
        ],
        "provisional_task_a_model": best_a["model"],
        "provisional_graph_weights": weight_sel["selected"],
        "retired_proxy_graph_weights": RETIRED_PROXY_SELECTION,
        "final_holdout": "NOT_BUILT",
        "constructed_unevaluated": "CONSTRUCTED_UNEVALUATED_VALIDATION_SET",
    }

    payload = attach_provenance(
        {
            "benchmark_id": "ISEF2027-THEORY-VAL-EXTERNAL-DEV-v2-structural",
            "contamination_state": ContaminationState.DEVELOPMENT_CONTAMINATED.value,
            "evidence_role": EvidenceRole.EXTERNAL_METHOD_DEVELOPMENT.value,
            "n_train": len(train),
            "n_dev": len(dev),
            "n_passages": len(train) + len(dev),
            "n_works": len({r["work_id"] for r in train + dev}),
            "n_authors": len({r["author_family"] for r in train + dev}),
            "n_source_families": len({r.get("source_family", r["work_id"]) for r in train + dev}),
            "train_works": sorted({r["work_id"] for r in train}),
            "dev_works": sorted({r["work_id"] for r in dev}),
            "source_family_overlap_train_dev": sorted(train_sf & dev_sf),
            "author_family_overlap_train_dev": sorted(train_af & dev_af),
            "task_a_raw": raw_models,
            "task_a_masked": masked_models,
            "selected_task_a_on_dev": best_a,
            "graph_weight_selection": weight_sel,
            "task_b_dev": task_b,
            "task_b_dev_masked": task_b_masked,
            "task_b_lexical_proxy_baseline": task_b_lexical,
            "leave_one_work_out": loso,
            "leave_one_author_family_out": loao,
            "leave_one_source_family_out": losf,
            "hard_negative_dev": {"n": len(hard), "metrics": hard_metrics},
            "calibration_variance": var_est,
            "power_sensitivity_table": power_table,
            "method_freeze": method_freeze,
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.DEVELOPMENT_ANALYSIS,
            synthetic=False,
            real_text=True,
            phase="validation",
            source_split="train+development",
            method_version="theory_val_external_dev_v2_structural",
            notes="True final holdout not built. Ancient confirmatory locked.",
        ),
    )

    out = root / "results/isef2027/validation/external_dev_method_selection.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=float) + "\n", encoding="utf-8")

    append_validation_ledger(
        root,
        {
            "dataset_version": "theory_validation_external_v2_family_clean",
            "dataset_hash_file": "data/theory_validation_v2/passages/corpus_meta.json",
            "train_sources": sorted({r["work_id"] for r in train}),
            "dev_sources": sorted({r["work_id"] for r in dev}),
            "test_sources": [],
            "model": best_a["model"],
            "hyperparameters": best_a.get("hyperparameters"),
            "graph_weights": weight_sel["selected"],
            "preprocessing": "none",
            "masking_config": "giveaway_vocab_v1",
            "metrics": {
                "task_a_macro_f1": best_a["metrics"]["macro_f1"],
                "task_a_top1": best_a["metrics"]["top1_accuracy"],
                "task_b_mrr": task_b.get("mrr"),
                "task_b_top1": task_b.get("top1_retrieval"),
            },
            "test_previously_viewed": False,
            "evidence_class": EvidenceClass.DEVELOPMENT_ANALYSIS.value,
            "influenced_subsequent_design": False,
            "final_holdout_touched": False,
        },
    )

    (root / "results/isef2027/validation/power_sensitivity_table.json").write_text(
        json.dumps(
            {
                "variance_source": var_est,
                "rows": power_table,
                "sample_size_justified": False,
                "n_sim_per_cell": n_sim,
            },
            indent=2,
            default=float,
        )
        + "\n",
        encoding="utf-8",
    )
    return payload
