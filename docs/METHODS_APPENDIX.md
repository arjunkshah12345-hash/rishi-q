# Methods Appendix (paper companion)

This document mirrors `paper/main.tex` with engineering detail for reviewers who want to reproduce every exhibit.

## Reproduce the exploratory exhibits

```bash
uv venv
uv pip install -e ".[dev]"
uv run python -m rishiq.ingest.synthetic
uv run rishiq annotate --config configs/development.yaml
uv run python scripts/run_power.py
uv run python scripts/build_paper_assets.py
uv run pytest -q
```

## Mapping: paper figure → generator

| Figure | File | Generator |
|--------|------|-----------|
| Pipeline | `fig01_pipeline.png` | `plot_pipeline_diagram` |
| Three levels | `fig02_three_levels.png` | `plot_three_level_cartoon` |
| Ontology | `fig03_ontology_overview.png` | `plot_ontology_overview` |
| Firewall | `fig04_firewall.png` | `plot_dev_confirmatory_firewall` |
| Positive controls | `fig05_positive_controls.png` | `plot_positive_control_validation` |
| QS by tradition | `fig06_qs_by_tradition.png` | `plot_qs_by_tradition` |
| Theory heatmap | `fig07_theory_heatmap.png` | `plot_theory_heatmap` |
| QS–QEF scatter | `fig08_qs_qef_scatter.png` | `plot_qs_qef_scatter` |
| Feature heatmap | `fig09_feature_heatmap.png` | `plot_feature_heatmap_from_annotations` |
| Robustness forest | `fig10_robustness_forest.png` | `plot_robustness_forest` |
| Power curves | `fig11_power_curves.png` | `plot_power_curves` |

## Mapping: paper table → source

All under `paper/tables/` and regenerated as `.tex` + `.csv`.

## Scientific non-negotiables encoded in software

1. Positive annotations require evidence (`FeatureAnnotation` validator).
2. Unity metaphors cannot silently become Q06 (`validation.verify_evidence` + heuristic negatives).
3. Confirmatory paths raise `ConfirmatoryLockedError`.
4. Experiment manifests hash datasets/ontology/models.
5. Embeddings module labeled SECONDARY_ONLY.

## What a skeptical physicist should check first

1. Positive-control figure: does EM stay classical-field-like?
2. Unity passage: is Q06 non-positive?
3. Manifest: can they regenerate identical scores at the same seed/backend?
4. Firewall: does confirmatory refuse to run?
