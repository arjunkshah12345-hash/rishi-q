# Constructed unevaluated validation set (demoted former final holdout)

## Status

`CONSTRUCTED_UNEVALUATED_VALIDATION_SET`

## Why demoted

The previous "final holdout" had:

- labels committed in the repository
- texts committed in the repository
- source-family overlap with train/development (OpenStax volumes / Wikipedia pages / related partitions)

It is **not** pristine unseen final evidence.

## Preserved

- Passage files under `data/theory_validation_v2/final_holdout/`
- Historical `holdout_passages_sha256` / `constructed_passages_sha256`
- Access log path

## True final method holdout

`NOT_BUILT`

May be constructed only after student-approved method freeze via a separate
`BUILD_FINAL_VALIDATION_HOLDOUT` operation, using eligibility rules in
`data/theory_validation_v2/final_holdout_candidates/`.

## Prospective reset before evaluation

Do not evaluate the constructed set as final method validation.
Do not retune the method using it.
After freeze, build a new family-clean holdout, hash it once, evaluate once.
