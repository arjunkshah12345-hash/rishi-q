# RISHI-Q Research Journey Log

Living lab notebook for the paper. Every consequential step should leave an artifact path here.

**Rule:** Do not invent confirmatory Sanskrit results. Document failures and locks honestly.

---

## 2026-08-15 — Protocol ingest

- Exported Drive *Master Research Protocol v1.0* → `protocol/master_protocol.md` (2106 lines).
- Wrote `protocol/hypotheses.md`, `decisions.md`, `methodology_status.md`, `implementation_plan.md`, `preregistration.md` (draft).
- **Artifact:** protocol/*

## 2026-08-15 — Ontology + fingerprints

- Built ontology v0.1 with 36 features (Levels I–III).
- Theory fingerprints: Newtonian, classical EM, thermo, relativity, QM, QFT.
- Codebook + definitions + examples.
- **Artifacts:** `ontology/ontology_v0.1.yaml`, `ontology/physics_fingerprints/`, `ontology/annotation_codebook.md`

## 2026-08-15 — Synthetic E2E milestone

Pipeline demonstrated:

```
synthetic passage → schema → blind → propositions → annotate → verify
→ feature vector → fingerprints → QS/QEF → manifest
```

- **Artifacts:** `corpus/development/synthetic_passages.parquet`, `results/exploratory/synthetic_e2e/*`
- **Tests:** 21 pytest cases green (unity≠Q06; EM field-like; entanglement→Q06; firewall).

## 2026-08-15 — Literature + sources

- `literature/literature.csv` (real citations; Capra as anti-pattern).
- `corpus/manifests/sources.csv` with licensing statuses (pointer / pending / PD candidate).

## 2026-08-15 — Paper asset factory

- Expanded visualization suite (pipeline, levels, ontology, firewall, controls, heatmaps, power).
- `scripts/build_paper_assets.py` regenerates figures + LaTeX tables + catalog.
- Expanded `paper/main.tex` as methods + instrument-validation manuscript.
- HTML preview: `paper/preview.html` (no TeX required).
- **Command:** `uv run python scripts/build_paper_assets.py`

## 2026-08-15 — Translation contamination demo

- Synthetic triple translation run: `scripts/run_translation_demo.py`
- Result: **TCI ≈ 0** for QS; modern buzzword wording actually *lost* classical-field structural cue matches relative to literal wording.
- **Interpretation for paper:** structural annotation can resist (and even be hurt by) physics-vocab modernization — desirable vs Capra-style leakage.
- **Artifact:** `results/exploratory/translation_demo/`, `paper/figures/fig12_translation_tci_demo.png`

## 2026-08-15 — Protocol §95 prototype100

- Built balanced synthetic development panel **n=174** (exceeds ~100 target): targets, Buddhist/Jain/Greek/Chinese controls, mystical + literary negatives, modern physics refs including relativity.
- Pipeline scored → `results/exploratory/prototype100/`
- Exploratory ΔQ ≈ **−0.015**, permutation **p≈0.58** (near null — expected for Level I/II synthetics).
- Cross-civ matrix: Vedānta-like synthetic shows field-like EM/QFT-*shared* features with **QM=0** (Level II ≠ Level III).
- Classifier / masking / shuffle-null / field-ontology summaries in `results/exploratory/protocol_analyses/`.
- New figures: fig13–fig17.
- Compliance tracker: `protocol/roadmap_compliance.md`

## Status gates (do not soft-pedal)

| Gate | Status |
|------|--------|
| Human validation | REQUIRES_EXTERNAL_HUMAN_VALIDATION |
| Preregistration submission | READY_FOR_EXTERNAL only |
| Confirmatory H1 | LOCKED |
| Expert reviews | outstanding |
| Full licensed corpus | in progress |

## Next paper-facing work

1. Acquire public-domain control passages with provenance scripts; keep copyrighted texts as pointers.
2. Add multi-translation toy pairs to demonstrate TCI figure (synthetic first).
3. Compile PDF (`pdflatex`) once TeX live available; fix overfull boxes.
4. Draft response-to-skeptic FAQ for Discussion.
5. Supplementary HTML explorer later (protocol §92) — not blocking methods paper.

## 2026-08-15 — Attempt to “settle” with PD corpus (honest)

- Built PD development corpus from Gutenberg (Upaniṣads/Paramananda, Lucretius, Timaeus, Dhammapada, Tao Te Ching): **n=276** (`corpus/development/pd_passages.parquet`).
- Exploratory pilot: **ΔQ = 0**, QEF = 0 for historical slices.
- Diagnosis: heuristic annotator positive-rate ~0.03% on historical PD vs ~18% on physics controls — **floor effect**.
- Conclusion: H1 **not settled**; local heuristic cannot adjudicate literary historical prose. Settlement requires LLM/human annotation + preregistration.
- Refused impressive-hunting (decision log).

## 2026-08-15 — Kaggle path + heuristic v0.2

- Built Transformers annotation backend + full `kaggle/annotation.ipynb`.
- Packaged `kaggle/rishiq_kaggle_bundle_public.zip` (276 blinded PD passages).
- Heuristic v0.2 classical NP cues: PD pilot ΔQ still ≈ 0; QEF = 0; no quantum enrichment.
- Join script ready: `scripts/join_kaggle_annotations.py`.

## 2026-08-15 — System B discovery engine (complete for exploratory stage)

Amendment: RISHI-Q must discover structures, not only test a pre-stated quantum claim.

Built and ran:

- Evidence-bound concept graphs → unsupervised Rishi Motifs → **post-hoc** physics mapping
- Work-stratified discovery/replication splits; cluster-aware motif bootstrap
- Surprisal, temporal (tradition date priors), translation-shift graphs (demo), claims-vs-data
- Novelty dossiers + automated literature search (still **NOVELTY_REVIEW_REQUIRED**)
- `discovery_report.md`, candidates, fig20–22

Exploratory PD finding under heuristic: **0 quantum-specific motifs**; many field-like motifs appear in controls, not Sanskrit target — useful claim-divergence signal, not H1 settlement.

**Artifacts:** `discovery_report.md`, `results/discovery/`, `novelty/`, `results/discovery_candidates/`, `protocol/discovery_protocol.md`

## 2026-08-15 — Paper + full visualization suite (fig01–fig31)

- Rewrote `paper/main.tex` and `paper/preview.html` for dual Systems A+B narrative.
- Added discovery visualization module + `scripts/build_all_visualizations.py`.
- New figures: dual system, discovery flow, concept graph, success tiers, claims-vs-data, temporal, translation modernization/shift, cluster bootstrap.
- **31** regenerable figures; tests still green.
