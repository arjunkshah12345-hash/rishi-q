# RISHI-Q Implementation Plan

**Date:** 2026-08-15  
**Protocol:** Master Research Protocol v1.0  
**Status:** ACTIVE — autonomous build in progress

## Authority

The Drive document *Full Starting Plan — RISHI-Q Master Research Protocol v1.0* is authoritative.
Local copy: `protocol/master_protocol.md`.

## Scientific invariants (never quietly change)

1. Distinguish Level I (generic metaphysical), Level II (field-like/classical), Level III (quantum-specific).
2. Prefer NA/UNKNOWN over YES when ambiguous.
3. Positive labels require evidence spans.
4. Development vs confirmatory firewall.
5. Embeddings are secondary only.
6. Do not fabricate human validation, expert review, preregistration, or results.
7. Negative results are successful scientific results.

## Build sequence

| Stage | Deliverable | Done when |
|-------|-------------|-----------|
| A | Protocol docs, decisions log, hypotheses | Files present, H0/H1 explicit |
| B | Ontology v0.1 + codebook + fingerprints | Schema validates; positive-control tests pass |
| C | Passage schema + synthetic corpus | Pydantic + Parquet round-trip |
| D | Blinding → propositions → annotate → verify | Synthetic E2E green |
| E | Similarity, QS, QEF, field analysis | Scores reproducible from seed |
| F | Statistics, power, controls, robustness | Unit tests + exploratory run |
| G | Literature CSV + source manifest | Real citations only |
| H | Dev corpus acquisition pipeline + sample | Provenance recorded; licenses audited |
| I | Human-validation package | Marked REQUIRES_EXTERNAL_HUMAN_VALIDATION |
| J | Preregistration draft | READY_FOR_EXTERNAL_PREREGISTRATION |
| K | Kaggle notebooks + CLI + paper + README | Installable; tests pass |

## Engineering defaults

- Python 3.12 + `uv`
- DuckDB / Polars / Parquet / YAML / Pydantic
- Dummy/rule-based annotation backend first (no local giant LLM)
- Kaggle for GPU/transformer workloads
- Memory-conscious MacBook Air workflow

## First milestone (blocking)

```
synthetic passage → schema → blind → propositions → annotate → verify
→ feature vector → fingerprints → classical/field/quantum scores
→ experiment manifest → reproducible result
```

## External checkpoints (not faked)

- Independent human validation
- Sanskrit scholar review
- Physicist review
- OSF preregistration submission
- arXiv upload

---

## System B — Discovery Engine (amendment 2026-08-15)

**Authority:** `protocol/discovery_protocol.md`  
**Rule:** Do not weaken System A. Success ≠ positive quantum result. Rigor first; discovery second; extraordinary claims only with extraordinary evidence.

RISHI-Q is a **computational discovery** project, not only confirmatory H1. System B searches for previously unreported, quantitatively defensible structural patterns.

| # | Component | Location | Status |
|---|-----------|----------|--------|
| 1 | Graph extraction (evidence-bound) | `src/rishiq/discovery/graphs` | IMPLEMENTED |
| 2 | Rishi Motif mining (no physics labels first) | `src/rishiq/discovery/motifs` | IMPLEMENTED |
| 3 | Discovery / replication / confirmatory splits | `corpus/discovery_split`, `replication_split` | IMPLEMENTED |
| 4 | Surprisal / outlier engine | `src/rishiq/discovery/surprisal` | IMPLEMENTED |
| 5 | Temporal pattern analysis | `src/rishiq/discovery/temporal` | IMPLEMENTED |
| 6 | Translation-shift / lexical modernization | `src/rishiq/discovery/translation` | IMPLEMENTED |
| 7 | Cross-civilization motif atlas | `src/rishiq/discovery/atlas` | IMPLEMENTED |
| 8 | Claims-vs-data testing | `ontology/claims_vs_data.yaml`, `discovery/claims` | IMPLEMENTED |
| 9 | Literature novelty dossiers | `novelty/`, `discovery/novelty` | IMPLEMENTED (human review still required) |
| 10 | Discovery dossiers | `results/discovery_candidates/` | IMPLEMENTED |
| 11 | Novelty gating + so-what dimensions | `discovery/ranker` | IMPLEMENTED |
| 12 | `discovery_report.md` generation | `discovery/report.py`, `scripts/run_discovery_engine.py` | IMPLEMENTED |
| 13 | Cluster-aware motif bootstrap | `discovery/significance.py` | IMPLEMENTED |
| 14 | Combinatorial feature mining | `discovery/significance.py` | IMPLEMENTED |
| 15 | Claims contradiction report | `results/discovery/claims_vs_data.md` | IMPLEMENTED |
| 16 | Discovery figures | `scripts/build_discovery_figures.py` | IMPLEMENTED |

### Dual-system architecture

```
System A (Confirmatory)     System B (Discovery)
─────────────────────       ────────────────────
preregistered H0/H1    ||   graphs → motifs (label-free)
locked until OSF       ||   → enrichment / surprisal / temporal
physics fingerprints   ||   → THEN map to physics families
for confirmatory only  ||   → claims-vs-data, novelty gate
```

### Runner

```bash
uv run python scripts/run_discovery_engine.py
uv run python scripts/run_novelty_search.py
uv run python scripts/build_discovery_figures.py
```

Outputs: `results/discovery/`, `results/discovery_candidates/`, `novelty/`, `discovery_report.md`, `paper/figures/fig20–22`.
