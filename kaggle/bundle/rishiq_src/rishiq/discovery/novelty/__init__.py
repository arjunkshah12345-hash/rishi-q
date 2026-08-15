"""Novelty dossier scaffolding — never claim 'first ever' without literature."""

from __future__ import annotations

from pathlib import Path

NOVELTY_TEMPLATE = """# Novelty dossier: {candidate_id}

## Candidate finding

{title}

## Exact empirical result

{empirical}

## Relevant source passages

{passages}

## Existing scholarship found

_REQUIRES_EXTERNAL_LITERATURE_REVIEW — do not invent citations._

## Closest known prior result

_Pending dedicated search._

## What prior work already establishes

_Pending._

## What appears different/new here

{apparent_new}

## Search terms used

{search_terms}

## Sources searched

- Google Scholar (pending)
- PhilPapers / JSTOR (pending)
- Domain histories of science / Indology (pending)

## Reasons novelty may be overstated

- Components may be individually well-known
- Combination may appear in qualitative scholarship without quantification
- Heuristic annotator may induce artifactual structure
- Translation English may modernize ontology

## Current novelty judgment

**NOVELTY_REVIEW_REQUIRED**

Preferred wording until cleared: *We did not yet identify prior quantitative characterization of…* — never *first ever*.
"""


def write_novelty_dossier(
    path: Path,
    *,
    candidate_id: str,
    title: str,
    empirical: str,
    passages: str,
    apparent_new: str,
    search_terms: list[str],
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = NOVELTY_TEMPLATE.format(
        candidate_id=candidate_id,
        title=title,
        empirical=empirical,
        passages=passages,
        apparent_new=apparent_new,
        search_terms="\n".join(f"- {t}" for t in search_terms),
    )
    path.write_text(text)
    return path
