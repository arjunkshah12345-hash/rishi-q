# RISHI-Q / ISEF2027 — project status

Last updated: 2026-08-16 (final pre-confirmatory readiness pass)

**Single source of truth:** [`artifacts/isef2027/PROJECT_STATUS.json`](../artifacts/isef2027/PROJECT_STATUS.json)

## Labels (read carefully)

| Label | Meaning |
|-------|---------|
| `V1_PUBLIC_TIMESTAMP_SUPERSEDED_FOR_FUTURE_ANALYSIS_BY_V2_DEVELOPMENT` | GitHub Release `prereg-isef2027-v1` remains; do not use v1 as-written for confirmatory |
| `V2_CANDIDATE_REQUIRES_STUDENT_FREEZE` | Method corrections in progress; not published; not OSF |
| `LOCKED_NOT_READY` | Confirmatory never opened / never scored |
| `SEALED_CANDIDATE_IDS_RESERVED; OUTCOMES_UNSCORED` | IDs exist; no analysis |
| `OSF_NOT_YET_SUBMITTED` | Only GitHub timestamp exists for v1 |
| `NOT_READY_TO_FREEZE` | Engineering + student gates incomplete |
| `CONSTRUCTED_UNEVALUATED_VALIDATION_SET` | Former final holdout demoted; not pristine |
| `NOT_BUILT` | True final method holdout not yet constructed |

## Overall

| Layer | Grade | Notes |
|-------|-------|-------|
| Exploratory flagship | **A** | Frozen; honest Maxwell 0/5 |
| V1 prereg timestamp | **Historical** | Untouched release; superseded for future confirmatory |
| V2 methodology | **In progress** | See `docs/V1_TO_V2_METHOD_CORRECTIONS.md` |
| Student review | **AWAITING_STUDENT_REVIEW** |
| Method validation | **Family-clean train/dev; true holdout NOT_BUILT** | Constructed set demoted; structural extractor live |
| Power / sample size | **Not freeze-ready** | Structural ICC from DEV; student N not frozen |
| Graph algorithm | **Unit-validated** | Typed coverage × Hungarian Option B |
| Confirmatory corpus | **Feasibility: reduced effect sensitivity** | Metadata only; LOCKED_NOT_READY |
| Fingerprint review | **Pending student** | Checklist in `docs/STUDENT_FINGERPRINT_REVIEW_CHECKLIST.md` |
| Competition paper | **Student** | You write |

## Do not do

- Open sealed confirmatory for score-tuning
- Publish v2 prereg/OSF until gates pass
- Treat SOFTWARE_DEMO or lexical proxy as claim-bearing structural evidence
- Fake student fingerprint approvals
- Build/evaluate true final holdout before student method freeze
