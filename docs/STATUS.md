# RISHI-Q / ISEF2027 — project status

Last updated: 2026-08-16 (v2 hardening)

**Single source of truth:** [`artifacts/isef2027/PROJECT_STATUS.json`](../artifacts/isef2027/PROJECT_STATUS.json)

## Labels (read carefully)

| Label | Meaning |
|-------|---------|
| `V1_PUBLIC_TIMESTAMP_SUPERSEDED_FOR_FUTURE_ANALYSIS_BY_V2_DEVELOPMENT` | GitHub Release `prereg-isef2027-v1` remains; do not use v1 as-written for confirmatory |
| `V2_CANDIDATE_REQUIRES_STUDENT_FREEZE` | Method corrections in progress; not published; not OSF |
| `LOCKED_NOT_READY` | Confirmatory never opened / never scored |
| `SEALED_CANDIDATE_IDS_RESERVED; OUTCOMES_UNSCORED` | IDs exist; no analysis |
| `OSF_NOT_YET_SUBMITTED` | Only GitHub timestamp exists for v1 |

## Overall

| Layer | Grade | Notes |
|-------|-------|-------|
| Exploratory flagship | **A** | Frozen; honest Maxwell 0/5 |
| V1 prereg timestamp | **Historical** | Untouched release; superseded for future confirmatory |
| V2 methodology | **In progress** | See `docs/V1_TO_V2_METHOD_CORRECTIONS.md` |
| Method validation | **External corpus built; final holdout UNEVALUATED** | Pedagogy v1 = development contaminated; see `docs/THEORY_VALIDATION_HOLDOUT_RESET.md` |
| Power / sample size | **Not freeze-ready** | Provisional ICC from dev proxy; N not frozen |
| Graph algorithm | **Unit-validated** | Coverage size-mismatch penalty + transform bench |
| Confirmatory corpus | **Inadequate** | Metadata inventory; few independent works |
| Fingerprint review | **Pending student** | Feature + graph packets blank (KEEP/MODIFY/…) |
| Competition paper | **Student** | You write |

## Do not do

- Open sealed confirmatory for score-tuning
- Publish v2 prereg/OSF until gates pass
- Treat SOFTWARE_DEMO as scientific evidence
- Fake student fingerprint approvals
