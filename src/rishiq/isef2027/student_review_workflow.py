"""Student review workflow — fingerprints + gold annotation.

Never auto-approves. Never shows extractor predictions before gold lock.
AI draft fingerprints remain untouched; student decisions live separately.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from rishiq.isef2027.concept_graph import ConceptGraph, EdgeKind, NodeKind

THEORIES = [
    "newtonian",
    "thermodynamics",
    "classical_em",
    "relativity",
    "quantum_mechanics",
    "quantum_field_theory",
    "atomistic_corpuscular",
]

DECISIONS = {"KEEP", "MODIFY", "DELETE", "UNSURE", "SOURCE_NEEDED"}

VALID_NODE_KINDS = {k.value for k in NodeKind}
VALID_EDGE_KINDS = {k.value for k in EdgeKind}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review_paths(root: Path) -> dict[str, Path]:
    base = root / "artifacts/isef2027/student_review"
    gold = root / "data/theory_validation_v2/extraction_gold"
    return {
        "base": base,
        "fingerprint_decisions": base / "fingerprint_decisions_v1.json",
        "fingerprint_ledger": base / "fingerprint_review_ledger.jsonl",
        "gold_dir": gold,
        "templates": gold / "gold_templates_BLANK.jsonl",
        "student_gold": gold / "student_gold_v1.jsonl",
        "locks": gold / "locks",
        "progress": base / "review_progress.json",
        "extractor_criterion": root / "artifacts/isef2027/extractor_acceptance_criterion_STUDENT_REQUIRED.json",
        "success_criterion": root / "artifacts/isef2027/final_validation_success_criterion_STUDENT_REQUIRED.json",
        "dev_reference": root / "artifacts/isef2027/final_validation_dev_reference_FOR_STUDENT.json",
    }


def ensure_student_artifacts(root: Path) -> None:
    """Create blank student-required artifacts if missing. Never mark approved."""
    paths = review_paths(root)
    paths["base"].mkdir(parents=True, exist_ok=True)
    paths["locks"].mkdir(parents=True, exist_ok=True)

    if not paths["fingerprint_decisions"].exists():
        payload = {
            "schema": "fingerprint_decisions_v1",
            "template_created_by": "coding_agent",
            "template_generated_with_ai": True,
            "student_decisions_ai_generated": False,
            "student_decisions_present": False,
            "annotator_role": "student_researcher",
            "physics_fingerprints_verified": False,
            "theories": {
                tid: {
                    "theory_complete": False,
                    "nodes": {},
                    "edges": {},
                    "theory_level_notes": "",
                    "completed_at": None,
                }
                for tid in THEORIES
            },
            "note": "Blank scaffolding from coding agent. Student decisions only. AI drafts live under protocol/isef2027_v2/fingerprint_review/.",
        }
        paths["fingerprint_decisions"].write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    else:
        _migrate_fingerprint_provenance(paths["fingerprint_decisions"])

    if not paths["extractor_criterion"].exists():
        paths["extractor_criterion"].write_text(
            json.dumps(
                {
                    "minimum_node_f1": None,
                    "minimum_relation_f1": None,
                    "minimum_typed_relation_f1": None,
                    "maximum_empty_extraction_rate": None,
                    "student_approved": False,
                    "approved_at": None,
                    "metrics_viewed_before_approval": None,
                    "template_created_by": "coding_agent",
                    "template_generated_with_ai": True,
                    "student_decisions_ai_generated": False,
                    "student_decisions_present": False,
                    "annotator_role": "student_researcher",
                    "note": "Student fills thresholds BEFORE viewing aggregate extractor-gold metrics if feasible.",
                    "max_gold_guided_revisions": 1,
                    "revision_policy": "ONE_STUDENT_GOLD_GUIDED_EXTRACTOR_REVISION",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    else:
        _migrate_criterion_provenance(paths["extractor_criterion"])

    if not paths["success_criterion"].exists():
        paths["success_criterion"].write_text(
            json.dumps(
                {
                    "primary_metric": None,
                    "minimum_primary_value": None,
                    "secondary_requirements": [],
                    "masked_requirement": None,
                    "source_family_requirement": None,
                    "failure_rule": None,
                    "student_approved": False,
                    "approved_at": None,
                    "template_created_by": "coding_agent",
                    "template_generated_with_ai": True,
                    "student_decisions_ai_generated": False,
                    "student_decisions_present": False,
                    "annotator_role": "student_researcher",
                    "note": "Student decides BEFORE true final holdout construction. Do not optimize to make method pass.",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    else:
        _migrate_criterion_provenance(paths["success_criterion"])

    _ensure_gold_template_provenance(root)
    write_dev_reference_for_student(root)


def _migrate_fingerprint_provenance(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    if "template_created_by" not in data:
        data["template_created_by"] = "coding_agent"
        changed = True
    if "template_generated_with_ai" not in data:
        data["template_generated_with_ai"] = True
        changed = True
    if "student_decisions_ai_generated" not in data:
        data["student_decisions_ai_generated"] = False
        changed = True
    # Detect whether any student decision exists
    present = False
    for block in (data.get("theories") or {}).values():
        for node in (block.get("nodes") or {}).values():
            if isinstance(node, dict) and node.get("decision"):
                present = True
        for edge in (block.get("edges") or {}).values():
            if isinstance(edge, dict) and edge.get("decision"):
                present = True
    if data.get("student_decisions_present") is not present:
        data["student_decisions_present"] = present
        changed = True
    # Remove misleading bare ai_generated=false implying student authorship of blank file
    if data.get("ai_generated") is False and not present:
        data.pop("ai_generated", None)
        changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _migrate_criterion_provenance(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    defaults = {
        "template_created_by": "coding_agent",
        "template_generated_with_ai": True,
        "student_decisions_ai_generated": False,
        "annotator_role": "student_researcher",
    }
    for k, v in defaults.items():
        if k not in data:
            data[k] = v
            changed = True
    present = bool(data.get("student_approved")) or any(
        data.get(k) is not None
        for k in (
            "minimum_node_f1",
            "minimum_relation_f1",
            "minimum_typed_relation_f1",
            "maximum_empty_extraction_rate",
            "primary_metric",
            "minimum_primary_value",
        )
    )
    if data.get("student_decisions_present") is not present:
        data["student_decisions_present"] = present
        changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _ensure_gold_template_provenance(root: Path) -> None:
    meta_path = root / "data/theory_validation_v2/extraction_gold/meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    else:
        meta = {}
    meta.setdefault("template_created_by", "coding_agent")
    meta.setdefault("template_generated_with_ai", True)
    meta.setdefault("student_decisions_ai_generated", False)
    meta.setdefault("student_decisions_present", False)
    meta.setdefault("annotator_role", "student_researcher")
    meta.setdefault("status", "BLANK_AWAITING_STUDENT_REVIEW")
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def write_dev_reference_for_student(root: Path) -> Path:
    """Chance baselines + DEVELOPMENT metrics for informed criterion choice (not thresholds)."""
    paths = review_paths(root)
    sel_path = root / "results/isef2027/validation/external_dev_method_selection.json"
    sel = json.loads(sel_path.read_text(encoding="utf-8")) if sel_path.exists() else {}
    task_b = sel.get("task_b_dev") or {}
    task_b_m = sel.get("task_b_dev_masked") or {}
    task_a = (sel.get("selected_task_a_on_dev") or {}).get("metrics") or {}
    payload = {
        "purpose": "REFERENCE_ONLY_NOT_A_SUCCESS_CRITERION",
        "chance_baselines_7way": {
            "top1": 1.0 / 7.0,
            "top2": 2.0 / 7.0,
        },
        "development_structural_snapshot": {
            "top1": task_b.get("top1_retrieval"),
            "top2": task_b.get("top2_retrieval"),
            "mrr": task_b.get("mrr"),
            "masked_top1": task_b_m.get("top1_retrieval"),
            "empty_extraction_rate": (
                (task_b.get("empty_extraction_n") or 0) / max(1, task_b.get("n") or 1)
            )
            if task_b
            else None,
            "note": "Pre-student-review DEVELOPMENT snapshot; may change after fingerprint/extractor finalization.",
        },
        "development_lexical_task_a_snapshot": {
            "top1": task_a.get("top1_accuracy"),
            "top2": task_a.get("top2_accuracy"),
            "macro_f1": task_a.get("macro_f1"),
        },
        "warning": "Do not set final-holdout thresholds solely to pass these numbers.",
    }
    paths["dev_reference"].write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return paths["dev_reference"]


def load_fingerprint_graph(root: Path, theory_id: str) -> ConceptGraph:
    path = root / "ontology/concept_graph" / f"template_fp_{theory_id}.json"
    return ConceptGraph.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_pairwise_neighbors(root: Path) -> dict[str, Any]:
    path = root / "results/isef2027/validation/fingerprint_distinguishability.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint_progress(root: Path) -> dict[str, Any]:
    ensure_student_artifacts(root)
    dec = json.loads(review_paths(root)["fingerprint_decisions"].read_text(encoding="utf-8"))
    completed = 0
    unresolved_unsure = []
    per = {}
    for tid in THEORIES:
        block = dec["theories"].get(tid) or {}
        g = load_fingerprint_graph(root, tid)
        need_nodes = {n.id for n in g.nodes}
        need_edges = {f"{e.source}->{e.kind.value}->{e.target}" for e in g.edges}
        node_dec = block.get("nodes") or {}
        edge_dec = block.get("edges") or {}
        nodes_done = all(
            (node_dec.get(nid) or {}).get("decision") in DECISIONS for nid in need_nodes
        )
        edges_done = all(
            (edge_dec.get(eid) or {}).get("decision") in DECISIONS for eid in need_edges
        )
        unsure = []
        for nid in need_nodes:
            d = (node_dec.get(nid) or {}).get("decision")
            if d == "UNSURE":
                unsure.append(f"node:{nid}")
        for eid in need_edges:
            d = (edge_dec.get(eid) or {}).get("decision")
            if d == "UNSURE":
                unsure.append(f"edge:{eid}")
        ok = bool(block.get("theory_complete")) and nodes_done and edges_done and not unsure
        if ok:
            completed += 1
        if unsure:
            unresolved_unsure.append({"theory": tid, "items": unsure})
        per[tid] = {
            "theory_complete_flag": block.get("theory_complete"),
            "nodes_decided": sum(1 for n in need_nodes if (node_dec.get(n) or {}).get("decision") in DECISIONS),
            "nodes_total": len(need_nodes),
            "edges_decided": sum(1 for e in need_edges if (edge_dec.get(e) or {}).get("decision") in DECISIONS),
            "edges_total": len(need_edges),
            "has_unsure": bool(unsure),
            "passes_gate": ok,
        }
    return {
        "completed": completed,
        "total": 7,
        "physics_fingerprints_verified": completed == 7 and not unresolved_unsure and dec.get("physics_fingerprints_verified") is True,
        "unresolved_unsure": unresolved_unsure,
        "per_theory": per,
        "ai_generated_flag_on_file": dec.get("ai_generated"),
    }


def gold_progress(root: Path) -> dict[str, Any]:
    ensure_student_artifacts(root)
    paths = review_paths(root)
    templates = [
        json.loads(l)
        for l in paths["templates"].read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    locked_ids = set()
    if paths["student_gold"].exists():
        for line in paths["student_gold"].read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("annotation_locked") and row.get("ai_generated") is False:
                locked_ids.add(row["passage_id"])
    # also count lock files
    for p in paths["locks"].glob("*.json"):
        try:
            row = json.loads(p.read_text(encoding="utf-8"))
            if row.get("annotation_locked") and row.get("ai_generated") is False:
                locked_ids.add(row["passage_id"])
        except Exception:
            continue
    return {
        "completed": len(locked_ids),
        "total": len(templates),
        "locked_passage_ids": sorted(locked_ids),
        "remaining": [t["passage_id"] for t in templates if t["passage_id"] not in locked_ids],
    }


def review_status(root: Path) -> dict[str, Any]:
    ensure_student_artifacts(root)
    paths = review_paths(root)
    fp = fingerprint_progress(root)
    gold = gold_progress(root)
    ext_c = json.loads(paths["extractor_criterion"].read_text(encoding="utf-8"))
    suc_c = json.loads(paths["success_criterion"].read_text(encoding="utf-8"))
    status = "AWAITING_STUDENT_REVIEW"
    if (
        fp["completed"] == 7
        and not fp["unresolved_unsure"]
        and gold["completed"] >= gold["total"]
        and ext_c.get("student_approved") is True
        and suc_c.get("student_approved") is True
    ):
        status = "STUDENT_REVIEW_COMPLETE_PENDING_OTHER_GATES"
    holdout_status = "NOT_BUILT"
    hold_path = root / "data/theory_validation_v2/passages/TRUE_FINAL_HOLDOUT_STATUS.json"
    if hold_path.exists():
        try:
            holdout_status = json.loads(hold_path.read_text(encoding="utf-8")).get("status", "NOT_BUILT")
        except Exception:
            holdout_status = "NOT_BUILT"
    return {
        "method_freeze_status": status if status == "AWAITING_STUDENT_REVIEW" else "NOT_READY_TO_FREEZE",
        "workflow_status": status,
        "fingerprint_review": fp,
        "gold_extraction_review": gold,
        "extractor_acceptance_criterion": {
            "student_approved": ext_c.get("student_approved") is True,
            "path": str(paths["extractor_criterion"].relative_to(root)),
        },
        "final_validation_success_criterion": {
            "student_approved": suc_c.get("student_approved") is True,
            "path": str(paths["success_criterion"].relative_to(root)),
        },
        "true_final_method_holdout": holdout_status,
        "ancient_confirmatory": "LOCKED_NOT_READY",
        "dev_reference": str(paths["dev_reference"].relative_to(root)),
    }


def _prompt_decision(item_label: str) -> dict[str, Any]:
    print(f"\n--- {item_label} ---")
    print("Decide: KEEP | MODIFY | DELETE | UNSURE | SOURCE_NEEDED")
    while True:
        raw = input("> ").strip().upper().replace(" ", "_")
        if raw in DECISIONS:
            break
        print("Invalid. Enter one of:", ", ".join(sorted(DECISIONS)))
    out: dict[str, Any] = {
        "decision": raw,
        "decided_at": _utc_now(),
        "replacement": None,
        "source_citation": None,
        "notes": "",
    }
    if raw == "MODIFY":
        out["replacement"] = input("Enter replacement (required): ").strip()
        while not out["replacement"]:
            out["replacement"] = input("Replacement cannot be empty: ").strip()
    if raw == "SOURCE_NEEDED":
        print("Do not invent a source. Leave citation blank or paste a real source you will obtain.")
        cite = input("Source citation (optional now): ").strip()
        out["source_citation"] = cite or None
    notes = input("Notes (optional): ").strip()
    out["notes"] = notes
    return out


def run_fingerprint_review_interactive(root: Path, *, theory_id: str | None = None) -> dict[str, Any]:
    ensure_student_artifacts(root)
    paths = review_paths(root)
    dec = json.loads(paths["fingerprint_decisions"].read_text(encoding="utf-8"))
    neighbors = load_pairwise_neighbors(root)
    nearest = neighbors.get("nearest_neighbor") or {}
    theories = [theory_id] if theory_id else THEORIES
    for tid in theories:
        if tid not in THEORIES:
            raise ValueError(f"unknown theory {tid}")
        g = load_fingerprint_graph(root, tid)
        print("\n" + "=" * 72)
        print(f"FINGERPRINT REVIEW: {tid}")
        print(f"Provenance on graph: AI_DRAFT — student decisions stored separately")
        nn = nearest.get(tid)
        if nn:
            print(f"Nearest competing fingerprint: {nn.get('neighbor')} (sim={nn.get('similarity')})")
        block = dec["theories"].setdefault(
            tid,
            {"theory_complete": False, "nodes": {}, "edges": {}, "theory_level_notes": "", "completed_at": None},
        )
        for n in g.nodes:
            print(f"\nNODE id={n.id} kind={n.kind.value} label={n.label!r} notes={n.notes!r} provenance={n.provenance}")
            existing = (block.get("nodes") or {}).get(n.id)
            if existing and existing.get("decision") in DECISIONS:
                print(f"  already decided: {existing['decision']} (press Enter to keep, or type redo)")
                ans = input("  ").strip().lower()
                if ans != "redo":
                    continue
            block.setdefault("nodes", {})[n.id] = _prompt_decision(f"node {n.id}")
        for e in g.edges:
            eid = f"{e.source}->{e.kind.value}->{e.target}"
            print(f"\nEDGE {eid} weight={e.weight} notes={e.notes!r}")
            existing = (block.get("edges") or {}).get(eid)
            if existing and existing.get("decision") in DECISIONS:
                print(f"  already decided: {existing['decision']} (press Enter to keep, or type redo)")
                ans = input("  ").strip().lower()
                if ans != "redo":
                    continue
            block.setdefault("edges", {})[eid] = _prompt_decision(f"edge {eid}")
        # completeness check for this theory
        need_nodes = {n.id for n in g.nodes}
        need_edges = {f"{e.source}->{e.kind.value}->{e.target}" for e in g.edges}
        nodes_ok = all((block.get("nodes") or {}).get(n, {}).get("decision") in DECISIONS for n in need_nodes)
        edges_ok = all((block.get("edges") or {}).get(e, {}).get("decision") in DECISIONS for e in need_edges)
        unsure = any(
            (block.get("nodes") or {}).get(n, {}).get("decision") == "UNSURE" for n in need_nodes
        ) or any((block.get("edges") or {}).get(e, {}).get("decision") == "UNSURE" for e in need_edges)
        if nodes_ok and edges_ok and not unsure:
            block["theory_complete"] = True
            block["completed_at"] = _utc_now()
            print(f"\n{tid}: marked theory_complete=true")
        else:
            block["theory_complete"] = False
            if unsure:
                print(f"\n{tid}: has UNSURE items — cannot verify until resolved")
            else:
                print(f"\n{tid}: incomplete decisions")
        dec["theories"][tid] = block
        dec["student_decisions_present"] = True
        dec["student_decisions_ai_generated"] = False
        paths["fingerprint_decisions"].write_text(json.dumps(dec, indent=2) + "\n", encoding="utf-8")
        with paths["fingerprint_ledger"].open("a", encoding="utf-8") as f:
            f.write(json.dumps({"event": "theory_saved", "theory": tid, "at": _utc_now()}) + "\n")

    # Never auto-set verified true here without validate gate — student must finish all 7 without UNSURE
    prog = fingerprint_progress(root)
    if prog["completed"] == 7 and not prog["unresolved_unsure"]:
        print("\nAll 7 theories have complete non-UNSURE decisions.")
        print("Run: rishiq-isef validate-student-review")
        print("Then you may set physics_fingerprints_verified via validate (machine check).")
    return prog


def _next_unlocked_template(root: Path) -> dict[str, Any] | None:
    gold = gold_progress(root)
    paths = review_paths(root)
    templates = [
        json.loads(l)
        for l in paths["templates"].read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    for t in templates:
        if t["passage_id"] not in gold["locked_passage_ids"]:
            return t
    return None


def run_gold_annotation_interactive(root: Path, *, passage_id: str | None = None) -> dict[str, Any]:
    """Annotate gold WITHOUT showing extractor predictions until lock."""
    ensure_student_artifacts(root)
    paths = review_paths(root)
    templates = {
        json.loads(l)["passage_id"]: json.loads(l)
        for l in paths["templates"].read_text(encoding="utf-8").splitlines()
        if l.strip()
    }
    if passage_id:
        tmpl = templates.get(passage_id)
        if not tmpl:
            raise ValueError(f"unknown passage_id {passage_id}")
    else:
        tmpl = _next_unlocked_template(root)
        if not tmpl:
            print("All gold passages locked.")
            return gold_progress(root)

    pid = tmpl["passage_id"]
    lock_path = paths["locks"] / f"{pid}.json"
    if lock_path.exists():
        print(f"{pid} already locked. Skipping.")
        return gold_progress(root)

    print("\n" + "=" * 72)
    print(f"GOLD ANNOTATION — extractor predictions HIDDEN until lock")
    print(f"passage_id: {pid}")
    print(f"work_id: {tmpl.get('work_id')}  source_family: {tmpl.get('source_family')}")
    print("-" * 72)
    print(tmpl["text"])
    print("-" * 72)
    print("Entity kinds:", ", ".join(sorted(VALID_NODE_KINDS)))
    print("Relation types:", ", ".join(sorted(VALID_EDGE_KINDS)))
    print("\nEnter entities. Empty surface ends entity list.")
    entities = []
    while True:
        surface = input("entity surface span (or empty to finish): ").strip()
        if not surface:
            break
        print("canonical entity type:")
        kind = input("> ").strip()
        while kind not in VALID_NODE_KINDS:
            print("Invalid kind. Choose from ontology.")
            kind = input("> ").strip()
        note = input("optional note: ").strip()
        eid = f"e{len(entities)+1}"
        entities.append(
            {
                "id": eid,
                "surface": surface,
                "canonical_entity_type": kind,
                "note": note,
            }
        )

    print("\nEnter relations. Empty source ends relation list.")
    print("Use entity ids:", ", ".join(e["id"] for e in entities) or "(none)")
    relations = []
    while True:
        src = input("source entity id (or empty to finish): ").strip()
        if not src:
            break
        rel = input("relation type: ").strip()
        while rel not in VALID_EDGE_KINDS:
            print("Invalid relation type.")
            rel = input("relation type: ").strip()
        tgt = input("target entity id: ").strip()
        explicit = input("explicitly stated? yes/no: ").strip().lower()
        while explicit not in {"yes", "no", "y", "n"}:
            explicit = input("explicitly stated? yes/no: ").strip().lower()
        uncertain = input("uncertain? yes/no: ").strip().lower() in {"yes", "y"}
        relations.append(
            {
                "source": src,
                "relation": rel,
                "target": tgt,
                "explicitly_stated": explicit in {"yes", "y"},
                "uncertain": uncertain,
            }
        )

    confirm = input("\nLock this annotation? (type LOCK to confirm): ").strip()
    if confirm != "LOCK":
        print("Not locked.")
        return gold_progress(root)

    ent_ids = {e["id"] for e in entities}
    for r in relations:
        if r["source"] not in ent_ids or r["target"] not in ent_ids:
            print("ERROR: relation endpoints must exist among entities. Not locked.")
            return gold_progress(root)

    record = {
        "passage_id": pid,
        "work_id": tmpl.get("work_id"),
        "source_family": tmpl.get("source_family"),
        "passage_sha256": tmpl.get("sha256"),
        "text": tmpl["text"],
        "entities": entities,
        "relations": relations,
        "annotator_role": "student_researcher",
        "template_created_by": "coding_agent",
        "template_generated_with_ai": True,
        "student_decisions_ai_generated": False,
        "student_decisions_present": True,
        "ai_generated": False,
        "extractor_prediction_hidden_during_annotation": True,
        "annotation_locked": True,
        "locked_at": _utc_now(),
        "annotation_sha256": None,
    }
    record["annotation_sha256"] = _sha256_text(
        json.dumps({k: record[k] for k in ("passage_id", "entities", "relations", "locked_at")}, sort_keys=True)
    )
    lock_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    # append / upsert student_gold jsonl
    existing = {}
    if paths["student_gold"].exists():
        for line in paths["student_gold"].read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                existing[row["passage_id"]] = row
    existing[pid] = record
    paths["student_gold"].write_text(
        "".join(json.dumps(existing[k]) + "\n" for k in sorted(existing)),
        encoding="utf-8",
    )
    meta_path = paths["gold_dir"] / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["student_decisions_present"] = True
        meta["student_decisions_ai_generated"] = False
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"Locked {pid}. Hash={record['annotation_sha256'][:16]}…")
    # NOW optionally reveal extractor
    reveal = input("Reveal extractor prediction for comparison? (y/N): ").strip().lower()
    if reveal in {"y", "yes"}:
        from rishiq.isef2027.structural_extractor import extract_structure

        pred = extract_structure(tmpl["text"]).to_dict()
        print(json.dumps(pred, indent=2)[:4000])
        print("(Shown AFTER lock — not used as gold.)")
    return gold_progress(root)


def run_student_review_menu(root: Path) -> dict[str, Any]:
    ensure_student_artifacts(root)
    while True:
        st = review_status(root)
        print("\n=== RISHI-Q student review ===")
        print(f"Fingerprints: {st['fingerprint_review']['completed']}/7")
        print(f"Gold: {st['gold_extraction_review']['completed']}/{st['gold_extraction_review']['total']}")
        print(f"Extractor criterion approved: {st['extractor_acceptance_criterion']['student_approved']}")
        print(f"Success criterion approved: {st['final_validation_success_criterion']['student_approved']}")
        print(f"Status: {st['workflow_status']}")
        print("\n1) Review fingerprints")
        print("2) Annotate next gold passage")
        print("3) Show status JSON")
        print("4) Quit")
        choice = input("> ").strip()
        if choice == "1":
            run_fingerprint_review_interactive(root)
        elif choice == "2":
            run_gold_annotation_interactive(root)
        elif choice == "3":
            print(json.dumps(st, indent=2))
        elif choice == "4":
            break
        else:
            print("Invalid choice")
    return review_status(root)
