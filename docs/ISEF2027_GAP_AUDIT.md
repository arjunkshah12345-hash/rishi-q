# ISEF2027 Gap Audit (technical)

> **2026-08-16 freeze:** Decisions + prereg **FROZEN**; controls/graphs **APPROVED**; SRC determination documented (no humans for confirmatory primary); sealed IDs reserved; public timestamp via GitHub Release `prereg-isef2027-v1`. Paper/abstract remain student-authored.

This document maps **technical** readiness. It does **not** claim an ISEF win and does **not** write the student’s paper.

| Criterion | Status | Notes |
|-----------|--------|-------|
| Testability | **Ready** | Frozen question/hypotheses in prereg YAML |
| Variables / graphs | **Frozen** | Concept graphs FROZEN; spot-check still wise before finals |
| Controls | **Families approved** | DEV exemplars contaminated; new matched works TO_ACQUIRE for unlock |
| Sample size | **Target frozen** | ≥20 works/arm, MIE Δ_Q=0.10, seed 20270816 |
| Reproducibility | **Strong** | `make reproduce`, CI, freeze SHA256 validator |
| Statistical plan | **Frozen** | Primary = work-level permutation; sensitivities listed |
| Independence | **Designed** | Work/tradition clustering in confirmatory design |
| Falsifiability | **Declared** | Prereg falsification triggers + claim boundary |
| Leakage / blinding | **Tooling ready** | Scrubbing + blind audit in harness |
| Human validation | **Deferred** | No ratings; Form 4 N/A for primary path |
| AI transparency | **Logged** | `AI_USAGE_LOG.md` |

## Remaining work (not software gaps)

1. School SRC stamp (Forms 1/1A/1B).
2. Acquire sealed PD: Aristotle Physics (EN), Epicurus letters, Nyāya/Sāṃkhya sections.
3. Optional OSF mirror (`OSF_TOKEN` + `scripts/submit_osf_prereg.sh`).
4. Student writes paper/abstract/poster.
5. Only then: confirmatory unlock + single analysis pass.

## Skeptic attacks still valid until confirmatory completes

1. Confirmatory corpus incomplete (TO_ACQUIRE slots).
2. Method benchmark uses lexical/ontology proxies — not human gold labels.
3. Exploratory flagship must stay labeled exploratory everywhere in the paper.
4. Embedding baselines need optional `.[ml]` extras for real models.

## Bottom line

**Repo / protocol package:** finished for drafting + school review.  
**Confirmatory science unlock:** blocked on acquisitions + SRC + your written unlock — correctly.
