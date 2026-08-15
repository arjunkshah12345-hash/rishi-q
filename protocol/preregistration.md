# RISHI-Q Preregistration Draft

**Status:** `READY_FOR_EXTERNAL_PREREGISTRATION`  
**Not submitted.** Do not treat this file as an OSF/AsPredicted timestamp.

## Title

Beyond Metaphor: A Blinded Computational Test of Quantum-Structural Analogues in Classical Sanskrit Thought (RISHI-Q)

## Primary hypotheses

- **H0:** \(\Delta_Q \le 0\) after prespecified controls.
- **H1:** \(\Delta_Q > 0\) (quantum-specific enrichment of Sanskrit targets vs matched historical controls).

See `protocol/hypotheses.md` for H2–H8 and falsification criteria.

## Inclusion / exclusion (draft)

### Include

- Passages from works listed in `corpus/manifests/sources.csv` with `availability_status` permitting analysis.
- Contiguous units expressing one proposition or tightly coupled set (protocol §35).
- Translations tagged by era/style; Sanskrit source text when available.

### Exclude

- Modern editorial footnotes mentioning quantum physics.
- Commentary mixed into primary text without separation.
- Duplicate / near-duplicate passages (keep one by preregistered rule).
- Copyrighted full text in public release when redistribution is forbidden (analyze under license; release metadata/hashes only).

## Sampling

- Development corpus: exploratory; contaminated by design decisions; **not** used for confirmatory H1 test.
- Confirmatory sample size: to be set by power simulation (`rishiq` statistics module) after development variance/ICC estimates — **not** chosen to force significance.
- Hierarchy: passage ⊂ section ⊂ work ⊂ tradition; inference cluster-aware.

## Ontology / prompts / metric (to freeze at registration)

- Ontology version: currently `0.1.0` (PILOTED) → freeze as `ontology-confirmatory-v1.0` at registration.
- Prompt versions: `prop-v0.1`, `ann-v0.1` (or successors frozen then).
- Primary similarity: weighted Jaccard with NA exclusion; weights fixed independent of Sanskrit outcomes.
- Primary endpoint: \(\Delta_Q\) via mixed-effects / cluster permutation as in protocol §42–44.
- Minimum scientifically interesting effect: **TBD at freeze** from development estimates + power curves.
- Stopping rule: analyze confirmatory corpus once; no sequential peeking; deviations disclosed.

## Secondary analyses

QEF; theory matrix; field-ontology substudy; TCI; school comparisons; FDR-controlled feature tests; classifier (exploratory); embeddings (exploratory only).

## Robustness (A–S)

As protocol §50; human-only arm requires completed external validation.

## Multiple testing

One primary test; secondary FDR.

## Deviations policy

Any post-registration change disclosed in a deviations appendix; exploratory follow-ups separated from confirmatory results.

## Explicit non-claims

This draft does **not** constitute preregistration. Confirmatory corpus remains locked until external registration + unlock file.
