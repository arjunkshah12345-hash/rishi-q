"""Human validation infrastructure (does not fabricate annotations)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from rishiq.models import AnnotationLabel


STATUS = "REQUIRES_EXTERNAL_HUMAN_VALIDATION"


def export_blinded_tasks(
    annotations: pd.DataFrame,
    out_path: str | Path,
    *,
    sample_n: int = 50,
    seed: int = 42,
) -> Path:
    """Export a subset for human review — empty human labels."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    # sample passage ids
    pids = annotations["passage_id"].unique()
    chosen = rng.choice(pids, size=min(sample_n, len(pids)), replace=False)
    sub = annotations[annotations["passage_id"].isin(chosen)].copy()
    sub["human_label"] = ""
    sub["human_evidence"] = ""
    sub["reviewer_id"] = ""
    sub["status"] = STATUS
    sub.to_csv(out_path, index=False)
    return out_path


def cohens_kappa(y1: list[str], y2: list[str]) -> float:
    labels = sorted(set(y1) | set(y2))
    idx = {l: i for i, l in enumerate(labels)}
    n = len(y1)
    if n == 0:
        return float("nan")
    mat = np.zeros((len(labels), len(labels)))
    for a, b in zip(y1, y2):
        mat[idx[a], idx[b]] += 1
    mat /= n
    po = float(np.trace(mat))
    pe = float(np.sum(mat.sum(0) * mat.sum(1)))
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)


def disagreement_report(df: pd.DataFrame) -> dict:
    """Expect columns model_label, human_label."""
    if "human_label" not in df.columns:
        return {"status": STATUS, "message": "no human labels present"}
    labeled = df[df["human_label"].astype(str).str.len() > 0]
    if labeled.empty:
        return {"status": STATUS, "n_labeled": 0}
    kappa = cohens_kappa(
        labeled["label"].astype(str).tolist(),
        labeled["human_label"].astype(str).tolist(),
    )
    return {
        "status": "PARTIAL" if len(labeled) else STATUS,
        "n_labeled": int(len(labeled)),
        "cohens_kappa": kappa,
    }


def write_reviewer_instructions(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """# Human Annotation Instructions (RISHI-Q)

Status: REQUIRES_EXTERNAL_HUMAN_VALIDATION

You are labeling structural features, not judging whether a text is "quantum."

## Labels
- 1 = explicitly supported by the passage
- 0 = explicitly contradicted
- NA = not specified / insufficient evidence
- U = ambiguous (use sparingly)

## Hard rules
- "Everything is one" does NOT imply nonseparability/entanglement.
- Interconnected ≠ nonlocal.
- Vibration ≠ QFT.
- Prefer NA over 1 when unsure.
- Every 1 requires an exact evidence span copied from the passage.

## Do not
- Use tradition names or book titles as evidence.
- Upgrade metaphors to physical claims.
- Discuss whether the overall project hypothesis is true while labeling.
""",
        encoding="utf-8",
    )
    return path
