"""Claims-vs-data contradiction / popular-claim divergence reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_claims_report(path: Path, claim_results: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Claims vs Data (System B)",
        "",
        "**Status:** EXPLORATORY under current annotator. Divergence from popular claims is a valid finding.",
        "",
        "| Claim | Kind | Best match | Structural support | Quantum support | Evidence quality |",
        "|-------|------|------------|--------------------|-----------------|------------------|",
    ]
    supported = []
    unsupported = []
    contradicted_popular = []
    for c in claim_results:
        qsup = c.get("QUANTUM_SUPPORTED") or []
        ssup = c.get("SUPPORTED_STRUCTURAL_COMPONENTS") or []
        best = c.get("BEST_PHYSICS_MATCH", "")
        lines.append(
            f"| {c.get('claim')} | {c.get('kind')} | {best} | "
            f"{', '.join(ssup) or '—'} | {', '.join(qsup) or '—'} | {c.get('EVIDENCE_QUALITY')} |"
        )
        if ssup and not qsup and "quantum" in c.get("claim", "").lower():
            contradicted_popular.append(
                f"**{c['claim']}**: popular quantum reading unsupported; best_match={best}; "
                f"structural={ssup}; quantum_missing={c.get('QUANTUM_UNSUPPORTED')}"
            )
        if ssup:
            supported.append(c["claim"])
        else:
            unsupported.append(c["claim"])

    lines += [
        "",
        "## Popular quantum claims that diverge from structural analysis",
        "",
    ]
    if contradicted_popular:
        lines += [f"- {x}" for x in contradicted_popular]
    else:
        lines.append("_None clearly divergent in this sample (or insufficient positives)._")

    lines += [
        "",
        "## Supported (structural components present)",
        "",
    ]
    lines += [f"- {x}" for x in supported] if supported else ["_None_"]
    lines += [
        "",
        "## Unsupported in sample",
        "",
    ]
    lines += [f"- {x}" for x in unsupported] if unsupported else ["_None_"]
    lines += [
        "",
        "## Machine-readable",
        "",
        "See `claims_vs_data.json`.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    summary_path = path.parent / (path.stem + "_summary.json")
    summary_path.write_text(
        json.dumps(
            {
                "supported": supported,
                "unsupported": unsupported,
                "popular_quantum_divergences": contradicted_popular,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return path
