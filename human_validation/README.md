# Human Validation Package

**Status: `REQUIRES_EXTERNAL_HUMAN_VALIDATION`**

This package provides export formats, reviewer instructions, and agreement metrics.
It does **not** contain fabricated human labels.

## Contents

- `instructions/reviewer_instructions.md` — labeling rules
- `templates/annotation_template.csv` — columns for human entry
- `exports/` — blinded task exports (generated)
- `imports/` — place completed reviewer CSVs here

## Workflow

```bash
uv run python scripts/export_human_tasks.py
# send exports + instructions to reviewers
uv run python scripts/import_human_labels.py --path human_validation/imports/reviewer_a.csv
```

Until independent humans complete review, methodology status remains `REQUIRES_EXTERNAL_HUMAN_VALIDATION`.
