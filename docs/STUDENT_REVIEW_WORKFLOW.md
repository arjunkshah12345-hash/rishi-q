# Student review → freeze (last pre-freeze workflow)

Status while incomplete: **`AWAITING_STUDENT_REVIEW`**

## Commands

```bash
# Interactive menu (fingerprints + gold)
uv run rishiq-isef student-review

# Progress only
uv run rishiq-isef student-review --status-only

# Validate machine-checkable completeness
uv run rishiq-isef validate-student-review

# After gold complete: Stage-1 metrics
uv run rishiq-isef evaluate-extractor-gold

# Gate scorecard + refresh freeze CANDIDATE
uv run rishiq-isef check-freeze-gates

# Explicit freeze (refuses until all gates pass)
uv run rishiq-isef freeze-method
uv run rishiq-isef freeze-method --confirm FREEZE

# ONLY after freeze (separate ops)
uv run rishiq-isef build-final-validation-holdout
uv run rishiq-isef evaluate-final-validation-once
```

## Student-required blank files

- `artifacts/isef2027/extractor_acceptance_criterion_STUDENT_REQUIRED.json`
- `artifacts/isef2027/final_validation_success_criterion_STUDENT_REQUIRED.json`
- Reference (not a criterion): `artifacts/isef2027/final_validation_dev_reference_FOR_STUDENT.json`

## Rules

- No auto-approval.
- Extractor predictions hidden until gold annotation is `LOCK`ed.
- AI fingerprint drafts stay under `protocol/isef2027_v2/fingerprint_review/`; student decisions in `artifacts/isef2027/student_review/`.
- Ancient confirmatory stays `LOCKED_NOT_READY`.
- True final holdout stays `NOT_BUILT` until after freeze.
