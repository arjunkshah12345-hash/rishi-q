"""Data leakage audit."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from rishiq.models import Passage

QUANTUM_EDITORIAL = re.compile(r"\bquantum\b|\bSchr[oö]dinger\b|\bHeisenberg\b", re.I)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def audit_leakage(
    passages: Iterable[Passage],
    *,
    development_ids: set[str] | None = None,
    confirmatory_ids: set[str] | None = None,
) -> dict:
    passages = list(passages)
    by_hash: dict[str, list[str]] = defaultdict(list)
    by_norm: dict[str, list[str]] = defaultdict(list)
    issues: list[dict] = []

    for p in passages:
        text = p.translation or p.source_text
        h = hashlib.sha256(text.encode()).hexdigest()
        by_hash[h].append(p.passage_id)
        by_norm[_norm(text)].append(p.passage_id)
        if QUANTUM_EDITORIAL.search(text) and p.role not in {
            "physics_reference",
            "synthetic",
        }:
            issues.append(
                {
                    "type": "modern_physics_editorial_language",
                    "passage_id": p.passage_id,
                    "detail": "quantum/physics proper names in non-physics passage",
                }
            )
        if "commentary:" in text.lower() or "editor note" in text.lower():
            issues.append(
                {
                    "type": "possible_commentary_mix",
                    "passage_id": p.passage_id,
                }
            )

    duplicates = {h: ids for h, ids in by_hash.items() if len(ids) > 1}
    near = {t: ids for t, ids in by_norm.items() if len(ids) > 1}

    if development_ids and confirmatory_ids:
        leak = sorted(development_ids & confirmatory_ids)
        if leak:
            issues.append({"type": "dev_confirmatory_id_overlap", "ids": leak})

    report = {
        "n_passages": len(passages),
        "exact_duplicate_groups": len(duplicates),
        "normalized_duplicate_groups": len(near),
        "duplicates": duplicates,
        "issues": issues,
        "status": "FAIL" if duplicates or any(i["type"] == "dev_confirmatory_id_overlap" for i in issues) else "PASS_WITH_WARNINGS" if issues else "PASS",
    }
    return report


def write_leakage_report(report: dict, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path
