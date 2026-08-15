# Paper assets

## Sources of truth
- LaTeX: `paper/main.tex`
- HTML preview (recommended for drafting): `paper/preview.html`
- Captions: `paper/assets/FIGURE_CAPTIONS.md`
- Catalog: `paper/assets/visualization_catalog.json`

## Regenerate everything

```bash
uv run python scripts/run_discovery_engine.py
uv run python scripts/build_all_visualizations.py   # fig01–fig31
uv run python scripts/build_paper_assets.py         # tables + catalog
```

## Honesty rules
- Do not present exploratory/synthetic/PD-pilot numbers as confirmatory H1.
- Do not invent human validation or OSF timestamps.
- System B discoveries stay exploratory until novelty review + replication.
