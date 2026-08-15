# RISHI-Q

**Beyond Metaphor: A Blinded Computational Test of Quantum-Structural Analogues in Classical Sanskrit Thought**

## What it is

RISHI-Q is a computational research framework for asking whether selected classical Sanskrit philosophical texts exhibit **quantum-specific structural correspondences** relative to matched historical controls — after source blinding, translation controls, vocabulary masking, and statistical safeguards.

A negative result is a successful scientific result.

RISHI-Q has two complementary systems:

| System | Role |
|--------|------|
| **A — Confirmatory** | Preregistered test of quantum-specific structural correspondence (locked until OSF) |
| **B — Discovery** | Unsupervised concept graphs → Rishi Motifs → post-hoc physics mapping, surprisal, temporal, translation-shift, claims-vs-data |

Success is **not** defined as proving ancient quantum anticipation. Prefer novel, robust structural findings — including negative/claim-contradicting ones.

## What it is NOT

- Not a proof that Hindu scriptures discovered quantum mechanics
- Not a cosine-similarity demo between Upaniṣads and QFT Wikipedia pages
- Not a spiritual affirmation project
- Not ready for confirmatory claims until preregistration and human validation

## Research question

> Do selected classical Sanskrit philosophical corpora exhibit statistically greater structural correspondence with modern quantum mechanics and quantum field theory than appropriately matched historical philosophical control corpora?

## Central distinction

| Level | Kind | Evidentiary weight |
|-------|------|--------------------|
| I | Generic metaphysical (unity, change, hidden reality) | Weak for quantum claims |
| II | Field-like / classical structure | May resemble classical fields, not automatically quantum |
| III | Quantum-specific (nonseparability, incompatible observables, quantized excitations, …) | Stronger, still not “discovery” |

Hard rules (examples): unity ≠ entanglement; vibration ≠ QFT; prāṇa ≠ energy; prefer **NA** over **YES** when ambiguous.

## Scientific safeguards

- Physics-derived ontology frozen before confirmatory testing
- Source-label blinding
- Evidence spans required for positive labels
- Development vs confirmatory firewall
- Translation treated as experimental variable
- Physics vocabulary masking
- Cluster-aware inference
- Negative controls and adversarial robustness battery
- Human validation required (not fabricated here)
- Preregistration required before confirmatory unlock

## Status (2026-08-15)

| Gate | Status |
|------|--------|
| Preregistration | `READY_FOR_EXTERNAL_PREREGISTRATION` (draft only) |
| Human validation | `REQUIRES_EXTERNAL_HUMAN_VALIDATION` |
| Confirmatory analysis | **LOCKED** |
| Expert Sanskrit / physics review | `REQUIRES_EXPERT_REVIEW` |

See `protocol/methodology_status.md`.

## Architecture

- **Local (MacBook Air):** corpus/metadata, DuckDB/Parquet, ontology, statistics, tests, paper
- **Kaggle (optional GPU):** transformer annotation, embeddings, multi-model replication, large simulations
- **Primary signal:** explicit ontology labels — embeddings are secondary only

## Installation

```bash
uv venv
uv pip install -e ".[dev]"
```

Optional ML extras (mainly for Kaggle): `uv pip install -e ".[ml]"`

## Quick start (synthetic end-to-end)

```bash
uv run python -m rishiq.ingest.synthetic
uv run rishiq validate-ontology ontology/ontology_v0.1.yaml
uv run rishiq annotate --config configs/development.yaml
uv run rishiq analyze
uv run pytest -q
```

### Protocol §95 development prototype

```bash
uv run python scripts/build_prototype100.py
uv run python scripts/run_protocol_analyses.py
uv run python scripts/build_paper_assets.py
open paper/preview.html
```

### System B discovery engine

```bash
uv run python scripts/run_pd_pilot.py          # if PD annotations missing
uv run python scripts/run_discovery_engine.py
uv run python scripts/run_novelty_search.py    # best-effort literature pass
uv run python scripts/build_all_visualizations.py
uv run python scripts/build_paper_assets.py
open paper/preview.html
# outputs: discovery_report.md, results/discovery/, novelty/, paper/figures/fig01–fig31
```

Confirmatory entrypoint stays locked:

```bash
uv run rishiq confirmatory   # exits locked until unlock file exists
```

## Dataset structure

- `corpus/development/` — exploratory (contaminated by design decisions)
- `corpus/confirmatory_locked/` — empty until preregistration
- `corpus/manifests/sources.csv` — bibliographic + licensing audit
- Copyrighted translations: metadata/pointers only unless redistribution is permitted

## Kaggle

See `kaggle/README.md`. Notebooks expect uploaded Parquet/YAML inputs and write compact outputs + manifests.

## Reproducibility

Every run should write an experiment manifest (`git_commit`, dataset/ontology hashes, model, seed, package versions). Results without provenance are invalid.

## Citation

See `CITATION.cff`.

## Paper drafting

- LaTeX: `paper/main.tex`
- HTML preview with figures: `paper/preview.html`
- Regenerate exhibits: `uv run python scripts/build_paper_assets.py`
- Journey log: `docs/RESEARCH_JOURNEY.md`
- Methods appendix: `docs/METHODS_APPENDIX.md`
- Skeptic FAQ: `docs/SKEPTIC_FAQ.md`

## License

MIT for software. Corpus texts remain under their own licenses (`docs/DATA_STATEMENT.md`).
