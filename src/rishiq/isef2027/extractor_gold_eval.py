"""Stage-1 extractor evaluation vs student gold (development only)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from rishiq.isef2027.structural_extractor import EXTRACTOR_VERSION, extract_structure
from rishiq.isef2027.student_review_workflow import review_paths


def _f1(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = (2 * p * r / (p + r)) if (p + r) else 0.0
    return p, r, f


def evaluate_extractor_gold(root: Path) -> dict[str, Any]:
    paths = review_paths(root)
    if not paths["student_gold"].exists():
        return {
            "status": "NOT_AVAILABLE — STUDENT GOLD INCOMPLETE",
            "extractor_version": EXTRACTOR_VERSION,
        }
    rows = [
        json.loads(l)
        for l in paths["student_gold"].read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    locked = [
        r
        for r in rows
        if r.get("annotation_locked")
        and r.get("ai_generated") is False
        and r.get("annotator_role") == "student_researcher"
    ]
    templates_n = 0
    if paths["templates"].exists():
        templates_n = sum(1 for l in paths["templates"].read_text().splitlines() if l.strip())
    if not locked or (templates_n and len(locked) < templates_n):
        return {
            "status": "NOT_AVAILABLE — STUDENT GOLD INCOMPLETE",
            "n_locked": len(locked),
            "n_required": templates_n,
            "extractor_version": EXTRACTOR_VERSION,
        }

    node_tp = node_fp = node_fn = 0
    rel_tp = rel_fp = rel_fn = 0
    typed_tp = typed_fp = typed_fn = 0
    error_classes: Counter[str] = Counter()
    passage_node_f1 = []
    passage_rel_f1 = []
    with_node = 0
    with_rel = 0

    for r in locked:
        pred = extract_structure(r["text"])
        if pred.nodes:
            with_node += 1
        if pred.edges:
            with_rel += 1

        gold_ent_surf = {e["surface"].lower(): e for e in r.get("entities") or []}
        pred_ent_surf = {n.surface.lower(): n for n in pred.nodes}
        g_set, p_set = set(gold_ent_surf), set(pred_ent_surf)
        tp_s = g_set & p_set
        for s in tp_s:
            if gold_ent_surf[s]["canonical_entity_type"] != pred_ent_surf[s].kind:
                error_classes["wrong_entity_kind"] += 1
            else:
                node_tp += 1
        for s in p_set - g_set:
            node_fp += 1
            error_classes["false_positive_entity"] += 1
        for s in g_set - p_set:
            node_fn += 1
            error_classes["missed_entity"] += 1

        # Relations: match on (src_surface, rel, tgt_surface) via gold entity ids
        id_to_surf = {e["id"]: e["surface"].lower() for e in r.get("entities") or []}
        gold_rels = set()
        gold_typed = set()
        for rel in r.get("relations") or []:
            ss = id_to_surf.get(rel["source"])
            ts = id_to_surf.get(rel["target"])
            if not ss or not ts:
                continue
            gold_rels.add((ss, rel["relation"], ts))
            gold_typed.add((ss, rel["relation"], ts))

        pred_id_surf = {n.id: n.surface.lower() for n in pred.nodes}
        pred_rels = set()
        for e in pred.edges:
            pred_rels.add((pred_id_surf.get(e.source, ""), e.relation, pred_id_surf.get(e.target, "")))

        for trip in gold_rels & pred_rels:
            rel_tp += 1
            typed_tp += 1
        for trip in pred_rels - gold_rels:
            rel_fp += 1
            typed_fp += 1
            # classify
            same_ends = [g for g in gold_rels if g[0] == trip[0] and g[2] == trip[2]]
            if same_ends and all(g[1] != trip[1] for g in same_ends):
                error_classes["wrong_relation_type"] += 1
            elif any(g[1] == trip[1] for g in gold_rels):
                error_classes["wrong_endpoint"] += 1
            else:
                error_classes["false_positive_relation"] += 1
        for trip in gold_rels - pred_rels:
            rel_fn += 1
            typed_fn += 1
            error_classes["missed_relation"] += 1

        _, _, nf = _f1(
            len(tp_s),
            len(p_set - g_set),
            len(g_set - p_set),
        )
        passage_node_f1.append(nf)
        _, _, rf = _f1(len(gold_rels & pred_rels), len(pred_rels - gold_rels), len(gold_rels - pred_rels))
        passage_rel_f1.append(rf)

    np_, nr, nf = _f1(node_tp, node_fp, node_fn)
    rp, rr, rf = _f1(rel_tp, rel_fp, rel_fn)
    tp_, tr, tf = _f1(typed_tp, typed_fp, typed_fn)

    # Bootstrap by passage
    rng = np.random.default_rng(0)
    boot_n, boot_r = [], []
    idx = np.arange(len(passage_node_f1))
    for _ in range(500):
        samp = rng.choice(idx, size=len(idx), replace=True)
        boot_n.append(float(np.mean([passage_node_f1[i] for i in samp])))
        boot_r.append(float(np.mean([passage_rel_f1[i] for i in samp])))

    n = len(locked)
    payload = {
        "status": "EVALUATED_VS_STUDENT_GOLD",
        "evidence_role": "DEVELOPMENT_VALIDATION",
        "extractor_version": EXTRACTOR_VERSION,
        "n_passages": n,
        "node": {"precision": np_, "recall": nr, "f1": nf},
        "relation": {"precision": rp, "recall": rr, "f1": rf},
        "typed_relation": {"precision": tp_, "recall": tr, "f1": tf},
        "coverage": {
            "pct_passages_with_ge1_node": with_node / n,
            "pct_passages_with_ge1_relation": with_rel / n,
            "empty_extraction_rate": 1.0 - (with_node / n),
        },
        "error_classes": dict(error_classes),
        "bootstrap_passage": {
            "node_f1_ci95": [float(np.percentile(boot_n, 2.5)), float(np.percentile(boot_n, 97.5))],
            "relation_f1_ci95": [float(np.percentile(boot_r, 2.5)), float(np.percentile(boot_r, 97.5))],
        },
    }
    out = root / "results/isef2027/validation/extractor_gold_evaluation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
