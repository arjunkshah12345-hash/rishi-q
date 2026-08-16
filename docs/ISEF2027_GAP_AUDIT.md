# ISEF2027 Gap Audit (technical — NOT a research plan)

This document maps **technical** readiness against generic scientific criteria.
It does **not** claim the project is “ISEF-winning.” It does **not** write the student’s research plan, abstract, paper, or conclusions.

| Criterion | Current status | Concrete technical fix | Code can solve? | Student judgment required? | External approval may be required? |
|-----------|----------------|------------------------|-----------------|----------------------------|------------------------------------|
| Testability | Partial — exploratory checklists exist; confirmatory protocol not frozen | Freeze hypotheses + metrics in prereg draft; sealed holdout tooling now present | Partial | **Yes** — official question/hypotheses | Possibly school fair forms |
| Variables | Ontology v0.1 + R1–R6 exploratory; concept-graph TEMPLATES added | Student verifies concept-graph + fingerprint content; freeze versions | Partial | **Yes** | Expert physics/Sanskrit review recommended |
| Controls | Thin 6-tradition panel (exploratory) | Matched control candidate manifest; expand calibration set with student-approved works | Partial | **Yes** — approve works | Licensing for non-PD texts |
| Sample size | Exploratory / underpowered for confirmatory claims | Power analysis on calibration; student sets N | Partial (`run_power`) | **Yes** | — |
| Reproducibility | Strong local scripts; new `rishiq-isef reproduce` | Keep lockfiles; registry append-only; CI optional | **Yes** | Minor | — |
| Statistical rigor | Cluster bootstrap/permutation exist; fair-coin null is exploratory-only | Student freezes primary inferential procedure; multiple-testing plan | Partial | **Yes** | Stats mentor helpful |
| Independence | Passage non-independence known; firewall exists | Work/tradition clustering enforced in confirmatory design | Partial | **Yes** | — |
| Novelty | Exploratory package novelty dossier exists | Confirmatory novelty = method+design, not “discovered QM” | N/A | **Yes** | Literature search by student |
| Falsifiability | Adversarial battery scaffolding added | Run full battery on calibration; predeclare failure criteria | Partial | **Yes** | — |
| Data provenance | Provenance schema + split manifest skeleton | Fill passage-level metadata for all included works | Partial | **Yes** | — |
| Leakage | Basic audit + split overlap checks; sealed sentinel | Blinded exports; translator-year strata; mask battery | Partial | **Yes** mask list freeze | — |
| Robustness | Placeholder robustness + new adversarial module | Execute LOO, masking, permutation on calibration | Partial | **Yes** | — |
| Limitations | Documented in docs/LIMITATIONS.md | Keep updated; never hide Maxwell 0/5 exploratory | **Yes** | **Yes** | — |
| Human validation | Scaffold only; **no data collected** | Packets/schemas ready; do not recruit yet | Packets yes | **Yes** + ethics | **Likely SRC/IRB/school** |
| AI use transparency | `AI_USAGE_LOG.md` required | Append every agent session | **Yes** | Student review of AI code | Fair rules on AI disclosure |

## Critical methodological attacks a skeptic can still make

1. Control panel still too small / poorly matched for confirmatory claims.
2. Concept graphs and atomistic fingerprint are TEMPLATES — not verified.
3. Positive-control harness uses synthetic/toy texts — not yet a full theory-identification benchmark on real physics corpora.
4. Embedding baseline not fully wired without optional ML extras.
5. Sealed confirmatory set is empty — contamination risk is low only because nothing is there yet; process discipline still required.
6. Exploratory flagship numbers could be misread as confirmatory if not labeled everywhere.

## What “ready to freeze” means here

Technical pipeline for **writing and preregistering** a confirmatory protocol: **approaching yes** for scaffolding, **no** for scientific freeze until student decisions in the table above are completed.
