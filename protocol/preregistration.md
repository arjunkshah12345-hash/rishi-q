# RISHI-Q Preregistration Draft

**Status:** `CONTENT_FROZEN` (2026-08-16) — see `protocol/isef2027_prereg_TEMPLATE.yaml` + `protocol/osf/`  
**Public timestamp:** GitHub Release `prereg-isef2027-v1` (interim). OSF URL when `OSF_TOKEN` submit succeeds.

## Title

Beyond Metaphor: A Blinded, Cluster-Aware Computational Test of Quantum-Specific Structural Correspondence in Classical Sanskrit Natural Philosophy (RISHI-Q / ISEF2027)

## Primary hypotheses

- **H0:** \(\Delta_Q \le 0\) after prespecified controls.
- **H1:** \(\Delta_Q > 0\) (quantum-specific enrichment of Sanskrit targets vs matched historical controls).

See `protocol/hypotheses.md` and frozen YAML for H2–H8 and falsification criteria.

## Inclusion / exclusion (frozen summary)

### Include

- Passages from works meeting matching criteria in `artifacts/isef2027/control_panel_candidates.yaml`.
- Contiguous units expressing one proposition or tightly coupled set.
- Translations tagged by era/style; Sanskrit source text when available.

### Exclude

- All `development_ids` from confirmatory scoring (exploratory contamination).
- Modern editorial footnotes mentioning quantum physics.
- Weak ethics-only verse as primary matched controls (Dhammapada, DDJ).
- Unfiltered SBE dump until section-filtered.
- Copyrighted full text in public release when redistribution is forbidden.

## Sampling

- Development: exploratory only.
- Confirmatory: ≥20 works/arm, ≥10 passages/work; Δ_Q MIE = 0.10; seed `20270816`.
- Hierarchy: passage ⊂ section ⊂ work ⊂ tradition; inference cluster-aware.

## Ontology / prompts / metric (frozen)

- Ontology: `ontology-confirmatory-v1.0-from-v0.1`
- Prompts: `prop-v0.1`, `ann-v0.1`
- Primary similarity: weighted Jaccard with NA exclusion
- Primary test: work-level permutation (one-sided)
- Humans: not collected for confirmatory primary path

## Explicit non-claims

Exploratory flagship numbers are not confirmatory. No ancient EM/QM discovery claims.
