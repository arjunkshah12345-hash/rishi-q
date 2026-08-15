# RISHI-Q Hypotheses

Derived from Master Research Protocol v1.0 (§4–7, §39–40, §82).  
Status: **PROPOSED** (not preregistered).

## Primary research question

Do selected classical Sanskrit philosophical corpora exhibit statistically greater structural correspondence with modern quantum mechanics and quantum field theory than appropriately matched historical philosophical control corpora?

## H0 — Null hypothesis

There is no meaningful difference between the quantum-specific structural correspondence of the Sanskrit target corpus and matched historical philosophical controls after prespecified corrections and controls.

Formally:

\[
H_0: \Delta_Q \le 0
\]

where

\[
\Delta_Q = E(QS_{\text{target}}) - E(QS_{\text{control}})
\]

and \(QS_i = S(X_i, Q) - \max_{C \in \text{Classical}} S(X_i, C)\).

## H1 — Primary alternative

The Sanskrit target corpus exhibits significantly greater quantum-specific structural correspondence than matched historical controls:

\[
H_1: \Delta_Q > 0
\]

**Quantum-specific** is required. Generic statements about unity, change, hidden reality, interconnectedness, consciousness, or vibration cannot by themselves establish H1.

## Secondary hypotheses

| ID | Name | Claim |
|----|------|-------|
| H2 | Quantum specificity | Target texts match QM/QFT more strongly than classical physical theories |
| H3 | Translation robustness | Any observed effect survives older and more literal translations |
| H4 | Vocabulary robustness | Effect survives masking/neutralization of modern physics vocabulary |
| H5 | Cross-model robustness | Result does not depend on one embedding or language model |
| H6 | Human reproducibility | Independent humans reproduce main ontology assignments with acceptable reliability |
| H7 | School specificity | Different Sanskrit traditions may have significantly different fingerprints |
| H8 | Feature specificity | Positive results are explainable by identifiable structural features, not one opaque similarity score |

## Primary endpoint

Cluster-aware estimate of \(\Delta_Q\) (target vs control), with work-level clustering, one-sided test of \(H_0: \beta_1 \le 0\) in the primary mixed-effects model (protocol §42–43).

## Secondary endpoints

- Quantum-Exclusive Feature Score (QEF)
- Theory similarity matrix (Newton, EM, Thermo, Relativity, QM, QFT)
- Field-ontology classifications for prāṇa / ākāśa / śakti / spanda passages
- Translation Contamination Index (TCI)
- Feature-level enrichment with FDR control
- School-specific QS comparisons
- Physics-classifier class probabilities (exploratory only)

## Falsification criteria

Treat the exciting hypothesis as unsupported if any of the following hold (protocol §82):

1. Target–control difference is negligible.
2. Confidence intervals include only scientifically trivial effects.
3. Translation masking removes the effect.
4. Generic metaphysical controls perform equally well.
5. Classical field theory explains the resemblance as well as QM/QFT.
6. Human annotation does not reproduce labels.
7. One model family causes most of the effect.
8. One source text creates the entire effect.
9. Results fail cluster-aware inference.
10. Quantum-specific features remain rare.

## Interpretation ladder (ceiling)

Even strong enrichment of quantum-specific features does **not** establish that ancient authors discovered quantum mechanics. Historical discovery requires mathematical theory, empirical methods, prediction, and knowledge transmission (protocol §84).

---

## System B — Discovery goals (not H1)

These are **exploratory** discovery objectives. They do **not** redefine success as a positive quantum result.

| ID | Goal |
|----|------|
| D1 | Discover recurring structural **Rishi Motifs** without physics labels first |
| D2 | Quantify motif enrichment vs matched controls with cluster-aware uncertainty |
| D3 | Identify structurally anomalous passages after artifact guards |
| D4 | Map temporal first-appearances of features/combinations (date ranges only) |
| D5 | Measure translation-shift / lexical modernization effects on ontology scores |
| D6 | Test curated popular/scholarly claims against structural evidence |
| D7 | Build cross-civilization motif atlas (shared vs unique vs field-like vs quantum-specific) |
| D8 | Graduate candidates only via novelty gate + literature review (no “first ever” without evidence) |

Discovery success tiers: methodological → quantitative → conceptual/historical → physics-relevant → transformative (extraordinary evidence only).
