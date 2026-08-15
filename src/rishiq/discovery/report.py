"""Generate discovery_report.md from discovery pipeline outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_discovery_report(out_dir: Path, payload: dict[str, Any]) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "discovery_report.md"

    top = payload.get("top_findings", [])
    motifs = payload.get("ranked_motifs", [])[:15]
    enrich = payload.get("enrichments", {})
    temporal = payload.get("temporal", {})
    translation = payload.get("translation", {})
    anomalies = payload.get("anomalies", [])[:10]
    claims = payload.get("claims", [])
    atlas = payload.get("atlas", {})
    candidates = payload.get("candidates", [])
    failed_repl = payload.get("failed_replication", [])

    supported_claims = [
        c
        for c in claims
        if c.get("BEST_PHYSICS_MATCH") not in {"unsupported_in_sample"}
        and c.get("SUPPORTED_STRUCTURAL_COMPONENTS")
    ]
    unsupported_claims = [
        c
        for c in claims
        if not c.get("SUPPORTED_STRUCTURAL_COMPONENTS")
        or c.get("BEST_PHYSICS_MATCH") == "unsupported_in_sample"
    ]
    field_non_q = [
        c
        for c in claims
        if "field" in str(c.get("BEST_PHYSICS_MATCH", "")).lower()
        and not c.get("QUANTUM_SUPPORTED")
    ]
    q_cands = [
        m
        for m in motifs
        if m.get("physics_family") == "quantum_specific"
    ]

    def _bullets(items: list[str]) -> str:
        if not items:
            return "_None identified in this exploratory run._\n"
        return "\n".join(f"- {x}" for x in items) + "\n"

    strongest = candidates[0] if candidates else None

    md = f"""# RISHI-Q Discovery Report (System B)

**Status:** EXPLORATORY — not confirmatory H1.  
**Standard:** Motifs discovered without physics labels first; physics mapping applied afterward.  
**Integrity:** Numbers trace to `results/discovery/` code outputs. Do not claim Tier 5 without extraordinary evidence.

## 1. Top New Findings

{_bullets(top)}

## 2. Discovered Structural Motifs

| Rank | Motif | Support | Enrichment | Physics family (post-hoc) | Signature (abbrev) |
|------|-------|---------|------------|---------------------------|--------------------|
"""
    for m in motifs:
        enr = enrich.get(m["motif_id"], {})
        e = enr.get("enrichment")
        e_s = f"{e:.2f}" if isinstance(e, (int, float)) else "—"
        sig = ", ".join(m.get("signature", [])[:5])
        md += f"| {m.get('rank','')} | {m['motif_id']} | {m.get('support')} | {e_s} | {m.get('physics_family')} | `{sig}` |\n"

    md += f"""
## 3. Strongest Cross-Tradition Enrichments

"""
    enr_sorted = sorted(
        enrich.values(),
        key=lambda x: (x.get("enrichment") is not None, x.get("enrichment") or 0),
        reverse=True,
    )[:10]
    if not enr_sorted:
        md += "_No enrichments computed._\n"
    else:
        for e in enr_sorted:
            md += (
                f"- **{e.get('motif_id')}**: enrichment={e.get('enrichment')}, "
                f"n_target={e.get('n_target')}, n_control={e.get('n_control')}, "
                f"n_works={e.get('n_works')}, ci95={e.get('ci95')}\n"
            )

    cluster = payload.get("cluster_bootstrap") or {}
    if cluster:
        md += "\n### Work-cluster bootstrap (secondary to effect size)\n\n"
        for mid, cs in list(cluster.items())[:8]:
            md += (
                f"- **{mid}**: work-level enrichment={cs.get('enrichment_work_level')}, "
                f"ci95={cs.get('ci95')}, p_boot={cs.get('p_boot_two_sided')}\n"
            )

    combos = payload.get("feature_combinations") or []
    if combos:
        md += "\n### Combinatorial feature patterns (label-free)\n\n"
        for c in combos[:8]:
            md += f"- `{c.get('combo_id')}` support={c.get('support')}: {', '.join(c.get('features', []))}\n"

    md += f"""
## 4. Most Surprising Historical Patterns

- Features first-appearance count: {len(temporal.get('features', {}))}
- Combinations first-appearance count: {len(temporal.get('combinations', {}))}
- Note: {temporal.get('note', 'Date ranges only.')}

"""
    combos = list(temporal.get("combinations", {}).values())[:5]
    for c in sorted(combos, key=lambda x: x.get("midpoint") or 9999)[:5]:
        md += (
            f"- `{c.get('combination')}` earliest midpoint≈{c.get('midpoint')} "
            f"({c.get('tradition')}, {c.get('work_id')}) range=[{c.get('year_start')}, {c.get('year_end')}]\n"
        )

    md += f"""
## 5. Translation Modernization Findings

```json
{json.dumps(translation, indent=2)[:3000]}
```

## 6. Most Anomalous Passages

"""
    for a in anomalies:
        md += (
            f"- `{a.get('passage_id')}` surprisal={a.get('surprisal'):.3f} "
            f"status={a.get('status')} flags={a.get('artifact_flags')}\n"
        )
    if not anomalies:
        md += "_None._\n"

    md += """
## 7. Popular Claims Supported

"""
    for c in supported_claims:
        md += (
            f"- **{c['claim']}** ({c['claim_id']}): supported={c.get('SUPPORTED_STRUCTURAL_COMPONENTS')}; "
            f"best_match={c.get('BEST_PHYSICS_MATCH')}; quantum_supported={c.get('QUANTUM_SUPPORTED')}\n"
        )
    if not supported_claims:
        md += "_None with structural support in this sample._\n"

    md += """
## 8. Popular Claims Not Supported

"""
    for c in unsupported_claims:
        md += (
            f"- **{c['claim']}** ({c['claim_id']}): unsupported={c.get('UNSUPPORTED_COMPONENTS')}; "
            f"quantum_unsupported={c.get('QUANTUM_UNSUPPORTED')}\n"
        )

    md += """
## 9. Field-Like but Non-Quantum Findings

"""
    for c in field_non_q:
        md += f"- **{c['claim']}**: {c.get('BEST_PHYSICS_MATCH')} (quantum components absent in sample)\n"
    field_motifs = atlas.get("field_like_motifs", [])[:10]
    md += _bullets([f"Motif {m}" for m in field_motifs])

    md += """
## 10. Quantum-Specific Candidates

"""
    md += _bullets(
        [
            f"{m['motif_id']} → {m.get('nearest_physics')} (rank_score={m.get('rank_score'):.3f})"
            for m in q_cands
        ]
    )

    md += """
## 11. Novelty Literature Review

All high-ranking candidates remain **NOVELTY_REVIEW_REQUIRED**. See `novelty/` dossiers. Never claim “first ever” without completed literature search.

## 12. Alternative Explanations

- Generic metaphysics / Level I features
- Classical field-like ontology mistaken for quantum
- Translation modernization of scientific lexicon
- Annotator lexical bias (heuristic backend)
- Shared mystical tropes across civilizations (weakens Sanskrit-specific claims)
- OCR / editorial / duplicate commentary artifacts

## 13. Candidates That Failed Replication

"""
    if failed_repl:
        md += _bullets(failed_repl)
    else:
        md += (
            "_No top-motif signatures failed the replication-split presence check in this run. "
            "Presence ≠ confirmatory effect; freeze candidates before claiming replication of enrichment._\n"
        )

    md += """
## 14. Strongest Discovery Candidate

"""
    if strongest:
        md += f"""```json
{json.dumps(strongest if isinstance(strongest, dict) else strongest, indent=2)[:2500]}
```
"""
    else:
        md += "_No candidate graduated past RAW / NOVELTY_REVIEW_REQUIRED._\n"

    md += f"""
## 15. What Is Actually New

At this stage, what is new is primarily **methodological**: an unsupervised motif-discovery layer on evidence-bound concept graphs, with post-hoc physics mapping, claims-vs-data testing, and novelty gates that refuse to declare STRONG_DISCOVERY_CANDIDATE without literature review and robustness.

Empirical motif/enrichment numbers above are **exploratory** under the current annotator and corpus partition. They are candidates for replication — not confirmatory H1 results.

---

Atlas summary: traditions={atlas.get('traditions')}; shared_motifs={len(atlas.get('shared_across_traditions', []))}; quantum_specific_motifs={len(atlas.get('quantum_specific_motifs', []))}.
"""
    path.write_text(md, encoding="utf-8")
    # also copy to repo root results/
    root_copy = out_dir.parent.parent / "discovery_report.md"
    if out_dir.name == "discovery":
        (out_dir.parent / "discovery_report.md").write_text(md, encoding="utf-8")
    return path
