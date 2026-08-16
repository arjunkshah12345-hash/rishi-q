"""Machine-checkable validation of student review artifacts.

Never sets approval flags by inference. Only verifies explicit student files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rishiq.isef2027.student_review_workflow import (
    DECISIONS,
    THEORIES,
    VALID_EDGE_KINDS,
    VALID_NODE_KINDS,
    ensure_student_artifacts,
    fingerprint_progress,
    gold_progress,
    load_fingerprint_graph,
    review_paths,
    review_status,
)


def validate_student_review(root: Path) -> dict[str, Any]:
    ensure_student_artifacts(root)
    paths = review_paths(root)
    errors: list[str] = []
    warnings: list[str] = []

    # --- Fingerprints ---
    dec = json.loads(paths["fingerprint_decisions"].read_text(encoding="utf-8"))
    if dec.get("ai_generated") is True:
        errors.append("fingerprint_decisions marked ai_generated=true")
    if dec.get("annotator_role") != "student_researcher":
        errors.append("fingerprint_decisions annotator_role must be student_researcher")

    fp_prog = fingerprint_progress(root)
    if fp_prog["completed"] < 7:
        errors.append(f"fingerprints incomplete: {fp_prog['completed']}/7")
    if fp_prog["unresolved_unsure"]:
        errors.append(f"unresolved UNSURE items: {fp_prog['unresolved_unsure']}")

    for tid in THEORIES:
        g = load_fingerprint_graph(root, tid)
        block = dec["theories"].get(tid) or {}
        for n in g.nodes:
            d = ((block.get("nodes") or {}).get(n.id) or {}).get("decision")
            if d not in DECISIONS:
                errors.append(f"{tid} node {n.id}: missing decision")
            if d == "MODIFY" and not ((block.get("nodes") or {}).get(n.id) or {}).get("replacement"):
                errors.append(f"{tid} node {n.id}: MODIFY requires replacement")
        for e in g.edges:
            eid = f"{e.source}->{e.kind.value}->{e.target}"
            d = ((block.get("edges") or {}).get(eid) or {}).get("decision")
            if d not in DECISIONS:
                errors.append(f"{tid} edge {eid}: missing decision")
            if d == "MODIFY" and not ((block.get("edges") or {}).get(eid) or {}).get("replacement"):
                errors.append(f"{tid} edge {eid}: MODIFY requires replacement")
        if not block.get("theory_complete"):
            errors.append(f"{tid}: theory_complete is false")

    # Fingerprint-related errors only
    fp_error_markers = (
        "fingerprint",
        "node ",
        "edge ",
        "theory_complete",
        "UNSURE",
        "fingerprints incomplete",
        "annotator_role",
        "ai_generated",
    )
    fp_errors = [e for e in errors if any(m in e for m in fp_error_markers)]
    fingerprints_ok = len(fp_errors) == 0 and fp_prog["completed"] == 7 and not fp_prog["unresolved_unsure"]

    if fingerprints_ok:
        dec["physics_fingerprints_verified"] = True
    else:
        dec["physics_fingerprints_verified"] = False
    paths["fingerprint_decisions"].write_text(json.dumps(dec, indent=2) + "\n", encoding="utf-8")

    # --- Gold ---
    gold = gold_progress(root)
    if gold["completed"] < gold["total"]:
        errors.append(f"gold incomplete: {gold['completed']}/{gold['total']}")

    if not paths["student_gold"].exists():
        errors.append("student_gold_v1.jsonl missing")
    else:
        rows = [
            json.loads(l)
            for l in paths["student_gold"].read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        by_id = {r["passage_id"]: r for r in rows}
        templates = [
            json.loads(l)
            for l in paths["templates"].read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        for t in templates:
            pid = t["passage_id"]
            r = by_id.get(pid)
            if not r:
                errors.append(f"gold missing passage {pid}")
                continue
            if r.get("ai_generated") is not False:
                errors.append(f"{pid}: ai_generated must be false")
            if r.get("annotator_role") != "student_researcher":
                errors.append(f"{pid}: annotator_role must be student_researcher")
            if not r.get("annotation_locked"):
                errors.append(f"{pid}: not locked")
            if not r.get("locked_at"):
                errors.append(f"{pid}: missing locked_at timestamp")
            if not r.get("annotation_sha256"):
                errors.append(f"{pid}: missing annotation_sha256")
            if r.get("extractor_prediction_hidden_during_annotation") is not True:
                errors.append(f"{pid}: extractor must have been hidden during annotation")
            ent_ids = {e.get("id") for e in r.get("entities") or []}
            for e in r.get("entities") or []:
                if e.get("canonical_entity_type") not in VALID_NODE_KINDS:
                    errors.append(f"{pid}: invalid entity type {e.get('canonical_entity_type')}")
            for rel in r.get("relations") or []:
                if rel.get("relation") not in VALID_EDGE_KINDS:
                    errors.append(f"{pid}: invalid relation {rel.get('relation')}")
                if rel.get("source") not in ent_ids or rel.get("target") not in ent_ids:
                    errors.append(f"{pid}: relation endpoints must exist")

    # Criteria files must exist; approval is separate
    ext_c = json.loads(paths["extractor_criterion"].read_text(encoding="utf-8"))
    suc_c = json.loads(paths["success_criterion"].read_text(encoding="utf-8"))
    if ext_c.get("student_approved") is not True:
        warnings.append("extractor_acceptance_criterion not student_approved")
    if suc_c.get("student_approved") is not True:
        warnings.append("final_validation_success_criterion not student_approved")

    ok = len(errors) == 0
    out = {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "fingerprint_progress": fp_prog,
        "gold_progress": gold,
        "physics_fingerprints_verified": fingerprints_ok,
        "extraction_gold_complete": gold["completed"] >= gold["total"] and ok,
        "review_status": review_status(root),
    }
    dest = root / "results/isef2027/validation/student_review_validation.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return out
