"""Fingerprint semantic sanity suite + student review packet builder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from rishiq.fingerprints import load_all_fingerprints


# Objective bans: classical fingerprints must not assert quantum-specific features.
CLASSICAL_FORBIDDEN_Q = {"Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08", "F07", "M02", "M04"}
NEWTON_FORBIDDEN = CLASSICAL_FORBIDDEN_Q | {"R03"}  # add if R03 is relativistic nonlocality — check later


def run_fingerprint_sanity(root: Path) -> dict[str, Any]:
    fps = load_all_fingerprints(root / "ontology/physics_fingerprints")
    issues = []
    review_tasks = []

    for tid, fp in fps.items():
        feats = {k: int(v) for k, v in fp.features.items()}
        if getattr(fp, "classical", False) or tid in {
            "newtonian",
            "classical_em",
            "thermodynamics",
            "atomistic_corpuscular",
        }:
            for q in CLASSICAL_FORBIDDEN_Q:
                if feats.get(q, 0) == 1:
                    issues.append(
                        {
                            "theory": tid,
                            "severity": f"classical_fingerprint_asserts_{q}",
                            "severity": "objective",
                        }
                    )
        if tid == "classical_em":
            for q in ("Q01", "Q03", "Q08", "F07"):
                if feats.get(q, 0) == 1:
                    issues.append(
                        {
                            "theory": tid,
                            "severity": f"maxwell_like_fingerprint_has_{q}",
                            "severity": "objective",
                        }
                    )
        if tid == "newtonian":
            # relativity / QFT markers if present as 1
            for q in CLASSICAL_FORBIDDEN_Q:
                if feats.get(q, 0) == 1:
                    issues.append({"theory": tid, "severity": f"newton_has_{q}", "severity": "objective"})

        # Overlap diagnostics (judgment)
        if tid == "quantum_mechanics" and "quantum_field_theory" in fps:
            qm = feats
            qft = {k: int(v) for k, v in fps["quantum_field_theory"].features.items()}
            shared = sum(1 for k in qm if qm.get(k) == 1 and qft.get(k) == 1)
            only_qm = sum(1 for k in qm if qm.get(k) == 1 and qft.get(k) != 1)
            only_qft = sum(1 for k in qft if qft.get(k) == 1 and qm.get(k) != 1)
            if shared > 0 and only_qm == 0 and only_qft == 0:
                issues.append(
                    {
                        "theory": "qm_vs_qft",
                        "severity": "qm_and_qft_identical_positive_features",
                        "severity": "objective",
                    }
                )
            review_tasks.append(
                {
                    "task": "Confirm QM vs QFT distinguishable feature sets",
                    "shared_positives": shared,
                    "only_qm": only_qm,
                    "only_qft": only_qft,
                    "severity": "REQUIRES_STUDENT_REVIEW",
                }
            )

    payload = {
        "suite_id": "ISEF2027-FP-SANITY-v2",
        "n_objective_failures": len([i for i in issues if i["severity"] == "objective"]),
        "issues": issues,
        "review_tasks": review_tasks,
        "pass_objective": all(i["severity"] != "objective" for i in issues) or len(issues) == 0,
    }
    # fix pass logic
    payload["pass_objective"] = payload["n_objective_failures"] == 0
    out = root / "results/isef2027/validation/fingerprint_sanity.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def write_graph_fingerprint_review_packets(root: Path) -> Path:
    """Student review templates for concept-graph fingerprints (choices left blank)."""
    gdir = root / "ontology/concept_graph"
    out_dir = root / "protocol/isef2027_v2/fingerprint_review/graph_packets"
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for path in sorted(gdir.glob("template_fp_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        tid = path.stem.replace("template_fp_", "")
        packet = {
            "theory_id": tid,
            "graph_file": str(path.relative_to(root)),
            "provenance": "AI_DRAFT_PENDING_STUDENT_REVIEW",
            "instructions": (
                "For each node and edge, set decision to KEEP|MODIFY|DELETE|UNSURE|SOURCE_NEEDED. "
                "Fill required_source only when citing a textbook/paper you have read. "
                "Do not invent citations. Leave decisions blank until reviewed."
            ),
            "nodes": [
                {
                    "node_id": n.get("id"),
                    "kind": n.get("kind"),
                    "label": n.get("label"),
                    "why_relation_or_role": n.get("notes", ""),
                    "central_or_optional": "",
                    "ambiguity_flag": "",
                    "required_source": "",
                    "decision": "",
                }
                for n in data.get("nodes", [])
            ],
            "edges": [
                {
                    "source": e.get("source"),
                    "target": e.get("target"),
                    "relation_type": e.get("kind"),
                    "why_relation_exists": e.get("notes", ""),
                    "central_or_optional": "",
                    "ambiguity_flag": "",
                    "required_source": "",
                    "decision": "",
                }
                for e in data.get("edges", [])
            ],
            "student_signoff": "",
            "date": "",
        }
        out = out_dir / f"graph_review_{tid}.yaml"
        out.write_text(yaml.safe_dump(packet, sort_keys=False), encoding="utf-8")
        index.append(str(out.relative_to(root)))
    (out_dir / "index.json").write_text(json.dumps({"packets": index}, indent=2) + "\n", encoding="utf-8")
    return out_dir


def write_fingerprint_review_packets(root: Path) -> Path:
    """One packet per theory: student KEEP/MODIFY/DELETE/UNSURE/SOURCE_NEEDED."""
    fps = load_all_fingerprints(root / "ontology/physics_fingerprints")
    out_dir = root / "protocol/isef2027_v2/fingerprint_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for tid, fp in fps.items():
        packet = {
            "theory_id": tid,
            "provenance": "AI_DRAFT_PENDING_STUDENT_REVIEW",
            "instructions": (
                "For each feature, set decision to KEEP|MODIFY|DELETE|UNSURE|SOURCE_NEEDED "
                "and a short rationale. Do not invent citations. Choices must not be auto-filled."
            ),
            "features": [
                {
                    "feature_id": fid,
                    "value": int(val),
                    "decision": "",
                    "rationale": "",
                    "source_needed": False,
                    "required_source": "",
                }
                for fid, val in sorted(fp.features.items())
            ],
            "student_signoff": "",
            "date": "",
        }
        path = out_dir / f"review_{tid}.yaml"
        path.write_text(yaml.safe_dump(packet, sort_keys=False), encoding="utf-8")
        index.append(str(path.relative_to(root)))
    write_graph_fingerprint_review_packets(root)
    (out_dir / "README.md").write_text(
        "# Fingerprint review packets\n\n"
        "All AI-drafted fingerprints await real student review.\n"
        "Feature packets: `review_*.yaml`.\n"
        "Graph packets: `graph_packets/graph_review_*.yaml`.\n"
        "Do not treat v1 `STUDENT_APPROVED_VIA_DELEGATION` as v2 scientific approval.\n"
        "Do not auto-fill KEEP/MODIFY/DELETE decisions.\n",
        encoding="utf-8",
    )
    (out_dir / "index.json").write_text(json.dumps({"packets": index}, indent=2) + "\n", encoding="utf-8")
    return out_dir
