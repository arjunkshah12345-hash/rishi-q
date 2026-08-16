# ISEF2027 Gap Audit (technical — NOT a research plan)

> **Update 2026-08-16:** STUDENT_DECISIONS + prereg content FROZEN; controls/graphs APPROVED; SRC/IRB determination documented (no humans for confirmatory); sealed IDs reserved; OSF packet ready (API submit needs OSF_TOKEN). Paper/abstract still student-only.

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
3. Method benchmark ontology top-1 (~0.8 on pedagogy panels) uses a crude keyword→feature proxy — not frozen human annotation.
4. Blind audit may FAIL on PD text that literally contains tradition names inside translations — requires stronger scrubbing / source-language pipelines.
5. Embedding baseline is a hashing proxy unless ML extras + real models are enabled.
6. Sealed confirmatory set is empty — contamination risk rises only when filled; process discipline still required.
7. Exploratory flagship numbers could be misread as confirmatory if not labeled everywhere.

## What “ready to freeze” means here

Technical pipeline for **writing and preregistering** a confirmatory protocol: **YES for scaffolding completeness** (splits, scrubbing, benchmarks, batteries, registry, visuals, blank prereg template, decision checklist).

**NO for scientific freeze** until `artifacts/isef2027/STUDENT_DECISIONS.yaml` items D01–D12 are completed by the student and OSF/AsPredicted is submitted.

