"""Stage-1 structural extraction gold templates (blank — student fills).

Agent must NOT fabricate student labels. Templates are for development/calibration
modern physics passages only. Confirmatory ancient texts are never included.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BLANK_FIELDS = {
    "entities": [],
    "entity_types": [],
    "relations": [],
    "relation_types": [],
    "uncertain_relations": [],
    "student_status": "BLANK_AWAITING_STUDENT",
    "student_decision": None,
}


def create_blank_gold_templates(root: Path, *, n: int = 40, seed: int = 0) -> dict[str, Any]:
    path = root / "data/theory_validation_v2/passages/development.jsonl"
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    # Stable subsample across works
    by_work: dict[str, list[dict]] = {}
    for r in rows:
        by_work.setdefault(r["work_id"], []).append(r)
    selected: list[dict] = []
    works = sorted(by_work)
    i = 0
    while len(selected) < min(n, len(rows)) and works:
        w = works[i % len(works)]
        if by_work[w]:
            selected.append(by_work[w].pop(0))
        else:
            works = [x for x in works if by_work[x]]
            if not works:
                break
            continue
        i += 1

    out_dir = root / "data/theory_validation_v2/extraction_gold"
    out_dir.mkdir(parents=True, exist_ok=True)
    templates = []
    for r in selected:
        templates.append(
            {
                "passage_id": r["passage_id"],
                "work_id": r["work_id"],
                "source_family": r.get("source_family"),
                "sha256": r["sha256"],
                "text": r["text"],
                "theory_label_hidden_from_annotator_ui": True,
                **BLANK_FIELDS,
            }
        )
    out = out_dir / "gold_templates_BLANK.jsonl"
    out.write_text("".join(json.dumps(t) + "\n" for t in templates), encoding="utf-8")
    meta = {
        "n_templates": len(templates),
        "status": "BLANK_AWAITING_STUDENT_REVIEW",
        "student_approved_n": 0,
        "note": "Do not treat machine-filled labels as gold. Student reviews own project annotations.",
        "path": str(out.relative_to(root)),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def evaluate_extractor_vs_gold(root: Path) -> dict[str, Any]:
    """Precision/recall only when student-approved gold exists; else report blocked."""
    from rishiq.isef2027.structural_extractor import EXTRACTOR_VERSION, extract_structure

    gold_path = root / "data/theory_validation_v2/extraction_gold/gold_templates_BLANK.jsonl"
    if not gold_path.exists():
        return {"status": "NO_GOLD_TEMPLATES", "extractor_version": EXTRACTOR_VERSION}
    rows = [json.loads(l) for l in gold_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    approved = [r for r in rows if r.get("student_status") == "APPROVED" and r.get("entities")]
    if not approved:
        return {
            "status": "AWAITING_STUDENT_GOLD_APPROVAL",
            "n_templates": len(rows),
            "n_approved": 0,
            "extractor_version": EXTRACTOR_VERSION,
            "node_precision": None,
            "node_recall": None,
            "node_f1": None,
            "relation_precision": None,
            "relation_recall": None,
            "relation_f1": None,
            "typed_relation_f1": None,
        }

    # Minimal set-based evaluation against approved annotations
    node_tp = node_fp = node_fn = 0
    rel_tp = rel_fp = rel_fn = 0
    for r in approved:
        pred = extract_structure(r["text"])
        gold_ents = {e.lower() for e in r.get("entities", [])}
        pred_ents = {n.surface.lower() for n in pred.nodes}
        node_tp += len(gold_ents & pred_ents)
        node_fp += len(pred_ents - gold_ents)
        node_fn += len(gold_ents - pred_ents)
        gold_rels = {tuple(x) if isinstance(x, (list, tuple)) else x for x in r.get("relations", [])}
        pred_rels = {(e.source, e.relation, e.target) for e in pred.edges}
        # surface-level: compare relation type multisets only if gold uses typed triples
        if gold_rels and isinstance(next(iter(gold_rels)), tuple):
            rel_tp += len(gold_rels & pred_rels)
            rel_fp += len(pred_rels - gold_rels)
            rel_fn += len(gold_rels - pred_rels)

    def _f1(tp, fp, fn):
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        return p, r, (2 * p * r / (p + r) if (p + r) else 0.0)

    np_, nr, nf = _f1(node_tp, node_fp, node_fn)
    rp, rr, rf = _f1(rel_tp, rel_fp, rel_fn)
    return {
        "status": "EVALUATED_VS_STUDENT_GOLD",
        "n_approved": len(approved),
        "extractor_version": EXTRACTOR_VERSION,
        "node_precision": np_,
        "node_recall": nr,
        "node_f1": nf,
        "relation_precision": rp,
        "relation_recall": rr,
        "relation_f1": rf,
        "typed_relation_f1": rf,
    }
