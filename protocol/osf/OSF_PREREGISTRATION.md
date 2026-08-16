# OSF Preregistration — RISHI-Q / ISEF2027

**Content frozen:** 2026-08-16  
**Registration type:** Preregistration of confirmatory analysis plan (OSF Preregistration / similar)  
**Machine-readable twin:** `../isef2027_prereg_TEMPLATE.yaml`  
**Hash manifest:** `FREEZE_MANIFEST.sha256`

## Study information

**Title:** Beyond Metaphor: A Blinded, Cluster-Aware Computational Test of Quantum-Specific Structural Correspondence in Classical Sanskrit Natural Philosophy (RISHI-Q / ISEF2027)

**Research question:** Do selected classical Sanskrit natural-philosophy corpora exhibit greater quantum-specific structural correspondence (QS) with modern QM/QFT fingerprints than matched historical philosophical control corpora, after prespecified masking, clustering, and classical-theory controls?

## Hypotheses

- **H0:** Δ_Q ≤ 0 after prespecified controls.
- **H1:** Δ_Q > 0 (one-sided). Quantum-specific enrichment required.
- **Secondary:** H2–H5, H7–H8 as in YAML. **H6 (humans) deferred** — no human data collection for confirmatory unlock.

## Design

- Three-way split: development (contaminated) / calibration / confirmatory_sealed (locked).
- Primary metric: weighted Jaccard ontology similarity with NA exclusion.
- Primary test: work-level permutation of Δ_Q, seed `20270816`, α = 0.05.
- Minimum interesting effect: 0.10.
- Sample size target: ≥20 works/arm, ≥10 passages/work (≥200 passages/arm).
- Masked + unmasked analyses using `configs/physics_vocab_v0.1.json`.
- Blinding/scrubbing enabled for any annotation pipelines.

## Controls

- Approved matched **families:** Greek atomist/Epicurean; Greek Platonic/Aristotelian.
- DEV Lucretius / Timaeus / DDJ / Dhammapada / Vaiśeṣika / Praśastapāda: **excluded from confirmatory scoring** (contamination).
- Confirmatory primary controls: **new** matched PD works (Aristotle Physics/De Caelo; Epicurus letters) — to acquire before analysis unlock.
- Sealed on-disk candidate: Upanishads PD (hash locked; not scored yet).

## Explicit non-claims

This registration does **not** claim ancient discovery of EM/QM. Exploratory flagship numbers (9/9, 6/6, 0/5, fair-coin P=1/64) remain exploratory only.

## Human subjects

None for confirmatory primary path. See `ethics/isef2027_SRC_IRB_DETERMINATION.md`.

## Analysis code

Repository: https://github.com/arjunkshah12345-hash/rishi-q  
Config: `configs/isef2027.yaml` (`allow_open_sealed: false` until unlock).

## Timestamp strategy

1. Prefer OSF registration URL (run `scripts/submit_osf_prereg.sh` with `OSF_TOKEN`).
2. Interim public timestamp: GitHub Release tag `prereg-isef2027-v1` attaching this file + YAML + sha256 manifest.
