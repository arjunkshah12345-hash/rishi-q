# Theory-validation holdout reset (Pass 3)

**Date:** 2026-08-16  
**Scope:** Method validation only. Does **not** unlock or score confirmatory ancient-text outcomes.

## 1. Why the old corpus was useful

`data/theory_validation/corpus_v1.jsonl` is a small set of short, internally curated pedagogy sentences covering seven theory labels. It was useful for:

- wiring train/dev/test loaders and metrics;
- debugging TF-IDF / SVM plumbing;
- spotting QM vs QFT confusion under centroid scoring;
- sanity-checking that the software stack runs end-to-end.

It remains in the repository as a **development benchmark**. Old scores are preserved under a downgraded evidence class (not deleted).

## 2. Why it was not externally sourced

Passages were authored inside this codebase as pedagogical one-liners. They are not independently authored textbook excerpts, not multi-work / multi-author samples, and not legally attributed external sources. Calling them strong “real text” holdout evidence overstated independence.

Relabel:

- **evidence class:** `CURATED_PEDAGOGY_DEVELOPMENT_BENCHMARK` (via `DEVELOPMENT_ANALYSIS` envelope + contamination state)
- **contamination state:** `DEVELOPMENT_CONTAMINATED` for the former test split
- **not:** `HELD_OUT_METHOD_VALIDATION` in the strong scientific sense

## 3. Why the previous test became development-contaminated

During Pass 2 hardening, developers observed test-set behavior (centroid QM/QFT confusion, overall accuracy) and then changed the primary scorer toward LinearSVC partly because of that behavior. Once a split influences method selection, it is no longer a pristine final holdout.

State for former v1/v2 pedagogy **test**:

`DEVELOPMENT_CONTAMINATED`

Train/dev on that corpus may still be used for software checks. Scores are **development results**, not final method evidence.

## 4. Why a new untouched validation set is needed

Trustworthy method validation requires:

- independently authored, legally usable physics passages with provenance;
- source-group (work/author) separation across train / development / final holdout;
- method freeze **before** a single final-holdout evaluation;
- Task A (theory classification) and Task B (structural fingerprint retrieval);
- masking / hard-negative / leave-one-source analyses on development data only until freeze.

That corpus lives under `data/theory_validation_v2/` with eligibility rules fixed before performance cherry-picking.

## 5. Timing relative to confirmatory ancient-text analysis

This reset occurred **before** any confirmatory ancient-text scoring. Sealed confirmatory outcomes remain:

`LOCKED_NOT_READY`

No confirmatory passage content was used to build, tune, or evaluate theory-validation methods in this pass.

## Contamination-state vocabulary

| State | Meaning |
|-------|---------|
| `UNSEEN` | Labels/texts not used for fitting or selection; not yet evaluated |
| `EVALUATED_ONCE_FROZEN_METHOD` | Evaluated once after method freeze; no further tuning |
| `DEVELOPMENT_CONTAMINATED` | Influenced design or was inspected during method choice |
| `RETIRED` | Kept for history; not used for claims |

## Related artifacts

- Pedagogy corpus: `data/theory_validation/corpus_v1.jsonl` + `corpus_v1_meta.json`
- Prior scores: `results/isef2027/validation/held_out_theory_identification.json` (reclassified as development)
- External corpus: `data/theory_validation_v2/`
- Ledger: `results/isef2027/validation/VALIDATION_LEDGER.jsonl`
