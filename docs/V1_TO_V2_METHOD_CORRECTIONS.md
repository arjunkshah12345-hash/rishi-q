# V1 → V2 methodological corrections

**Tone:** Normal prospective revision **before** confirmatory analysis.  
**Not:** misconduct, concealment, or rewriting history.

V1 public timestamp remains:  
https://github.com/arjunkshah12345-hash/rishi-q/releases/tag/prereg-isef2027-v1

Future confirmatory analysis must follow a **student-frozen v2** plan, not v1 as-written.

## Why v2 is needed

| Issue | What v1 did | Why it is insufficient | V2 direction |
|-------|-------------|------------------------|--------------|
| Power / sample size | D08 froze ≥20 works/arm using exploratory + toy logistic curves | Calibration contains `logistic_toy_power_curve` placeholder; not hierarchical Δ_Q power under real variance | `power_hier.py` Monte Carlo; variance params `UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE` until estimated |
| Concept graphs | Marked FROZEN / `STUDENT_APPROVED_VIA_DELEGATION` | Content was AI-drafted without substantive student review | Provenance → `AI_DRAFT_PENDING_STUDENT_REVIEW`; review packets |
| Graph similarity | Literal node-ID / label overlap | Near-zero overlaps across differently named isomorphic relations | Typed-relation multiset + Hungarian role alignment |
| Method benchmark | Handful of pedagogy panels + keyword proxy | Too small; keyword proxy is not structural validation | Train/dev/test theory corpus; TF-IDF held-out scorer |
| Thermodynamics ID | Failed under keyword→fingerprint proxy | Proxy lacked thermo feature coverage; looks like “method works” elsewhere | Investigate + held-out confusion matrix; fix method not hide score |
| Confirmatory corpus | Reserved IDs / TO_ACQUIRE slots | Far from powered matched panel | Metadata-only candidate inventory (no scoring) |
| Demo statistics | Synthetic LOO/permutation/translation-year demos | Can be mistaken for scientific evidence | Mandatory `evidence_class` on every artifact |
| CI at v1 freeze | Workflow used `uv pip install --system` | Red CI on Ubuntu externally managed Python | `uv sync --extra dev` |
| Documentation | README claimed finished scientific freeze | Overstated readiness vs actual verification | Single `PROJECT_STATUS.json` source of truth |
| Human validation | Deferred correctly | Fine | Keep deferred; no fabricated ratings |

## Explicit preservations

- Do **not** delete or alter the `prereg-isef2027-v1` GitHub Release.
- Do **not** open or score sealed confirmatory outcomes.
- Do **not** rewrite exploratory flagship numbers.
- Label old toy power outputs `SOFTWARE_DEMO_NOT_SAMPLE_SIZE_EVIDENCE`.

## V2 freeze gate (all required)

See `artifacts/isef2027/PROJECT_STATUS.json`. Confirmatory unlock remains forbidden while any gate is false / `LOCKED_NOT_READY`.
