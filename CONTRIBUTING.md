# Contributing

This is a student research repository (RISHI-Q / ISEF2027).

## Hard rules

- Do **not** open `corpus/confirmatory_sealed` for analysis while tuning.
- Do **not** invent human annotation ratings.
- Do **not** claim ancient EM/QM discovery.
- Do **not** replace the student’s paper/abstract authorship.
- Append to `AI_USAGE_LOG.md` when an agent makes substantial changes.
- Prefer `arjunkshah12345-hash/rishi-q` as the GitHub remote.

## Dev loop

```bash
uv pip install -e ".[dev]"
make test
make validate-freeze
make reproduce
```

## Pull requests

Keep changes scoped. Update `docs/STATUS.md` if readiness gates change.
