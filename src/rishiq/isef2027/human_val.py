"""Human-validation reliability tooling — NO data collection."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def cohens_kappa(a: list[str], b: list[str]) -> float:
    """Simple Cohen's kappa for categorical labels."""
    if len(a) != len(b) or not a:
        return float("nan")
    labels = sorted(set(a) | set(b))
    idx = {lab: i for i, lab in enumerate(labels)}
    n = len(a)
    mat = np.zeros((len(labels), len(labels)), dtype=float)
    for x, y in zip(a, b):
        mat[idx[x], idx[y]] += 1
    mat /= n
    po = float(np.trace(mat))
    pe = float(np.sum(mat.sum(0) * mat.sum(1)))
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def disagreement_matrix(a: list[str], b: list[str]) -> dict:
    labels = sorted(set(a) | set(b))
    m = {r: {c: 0 for c in labels} for r in labels}
    for x, y in zip(a, b):
        m[x][y] += 1
    return m


def write_human_validation_pack(root: Path) -> Path:
    out = root / "human_validation/isef2027"
    out.mkdir(parents=True, exist_ok=True)
    (out / "README.md").write_text(
        "# ISEF2027 human validation (PREPARE ONLY)\n\n"
        "**DO NOT recruit reviewers or collect annotations yet.**\n"
        "Wait for student determination of ISEF/SRC/IRB requirements.\n\n"
        "This folder strengthens schemas, reliability scripts, and packet templates only.\n",
        encoding="utf-8",
    )
    schema = {
        "fields": [
            "anonymous_passage_id",
            "feature_id",
            "label",
            "confidence_1_to_5",
            "ambiguity_flag",
            "evidence_span",
            "reviewer_id_blinded",
            "adjudication_status",
        ],
        "labels_allowed": ["1", "0", "NA", "U"],
        "no_fabricated_ratings": True,
        "collection_allowed": False,
    }
    (out / "annotation_schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    (out / "packet_template.json").write_text(
        json.dumps(
            {
                "packet_id": "HV-ISEF2027-TEMPLATE",
                "passages": [],
                "instructions_path": "human_validation/instructions/reviewer_instructions.md",
                "status": "NOT_SENT",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    # Demo kappa on toy labels to prove the function works (not scientific data)
    demo_a = ["1", "0", "NA", "1", "0"]
    demo_b = ["1", "0", "NA", "0", "0"]
    (out / "reliability_demo.json").write_text(
        json.dumps(
            {
                "note": "Synthetic demo only — proves metric code runs. NOT human data.",
                "cohens_kappa_demo": cohens_kappa(demo_a, demo_b),
                "disagreement_matrix_demo": disagreement_matrix(demo_a, demo_b),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return out
