# ISEF2027 scientific hardening — implementation report

Date: 2026-08-16  
Repo: https://github.com/arjunkshah12345-hash/rishi-q  
V1 release (untouched): https://github.com/arjunkshah12345-hash/rishi-q/releases/tag/prereg-isef2027-v1

## FIXED

- CI uses `uv sync --extra dev` (no `--system` on externally managed Python)
- Restored `src/rishiq/models/` (was wrongly gitignored by `models/`)
- Sealed-ID tests: reserved IDs allowed; must not overlap; must stay unscored/locked
- Split writer preserves sealed IDs across reproduce
- Evidence classes + registry refusal of synthetic×confirmatory
- `PROJECT_STATUS.json` single source of truth
- V2 candidate protocol + `V1_TO_V2_METHOD_CORRECTIONS.md` (no v2 release/OSF)
- Structural graph similarity (typed-relation multiset + Hungarian role alignment)
- Held-out theory validation (train/dev/test; TF-IDF centroids; keyword proxy quarantined)
- Hierarchical Δ_Q power simulation; toy logistic power labeled `SOFTWARE_DEMO_NOT_SAMPLE_SIZE_EVIDENCE`
- Confirmatory candidate metadata inventory (no scoring)
- Translation-pair schema/manifest (unscored)
- Fingerprint review packets; sanity suite; judge-attack matrix
- Graph provenance → `AI_DRAFT_PENDING_STUDENT_REVIEW` for v2

## CI

**PASS** (run after models fix): all unit/ISEF tests, freeze integrity, sealed invariants, reproduce harness, confirmatory LOCKED check.

## REAL VALIDATION RESULTS

## REAL VALIDATION RESULTS (latest)

Source: `results/isef2027/validation/held_out_theory_identification.json`  
`evidence_class: HELD_OUT_METHOD_VALIDATION` · scorer: `tfidf_linearsvc_train_only`

- top-1: **0.571** (centroid secondary: 0.500)
- macro-F1: **0.581**
- weakest theory (F1): **newtonian**
- n_train/dev/test: 48/14/14
- thermo F1: 0.6666666666666666
- qm F1: 0.6666666666666666

Interpretation: stratified held-out on a small pedagogy corpus is **not** yet strong enough to mark `method_validation_complete=true`. Confirmatory remains LOCKED_NOT_READY.


Source: `results/isef2027/validation/held_out_theory_identification.json`  
`evidence_class: HELD_OUT_METHOD_VALIDATION`

- Scorer: TF-IDF centroids fit on train only
- See latest file for top-1 / macro-F1 / confusion matrix / weakest theory
- Thermodynamics recovers under held-out TF-IDF (prior failure was keyword-proxy coverage)

## DEMO RESULTS

| Artifact | Class |
|----------|-------|
| `results/isef2027/dev/method_benchmark.json` | SOFTWARE_DEMO (keyword proxy) |
| `results/isef2027/validation/keyword_proxy_demo.json` | SOFTWARE_DEMO |
| `results/isef2027/dev/translation_battery.json` (year demo) | SOFTWARE_DEMO |
| Toy logistic power in calibration adversarial | SOFTWARE_DEMO_NOT_SAMPLE_SIZE_EVIDENCE |
| Hierarchical power with UNKNOWN variance | PROVISIONAL / not freeze-ready |

## GRAPH METHOD

Primary: `0.55 * typed_relation_multiset + 0.45 * hungarian_role_alignment`  
Literal ID overlap kept as diagnostic baseline only.  
Isomorphic differently labeled CAUSES patterns now score high on typed relation (unit-tested).

## THEORY IDENTIFICATION

Held-out TF-IDF is the claim-bearing method-validation path.  
Keyword→fingerprint Jaccard is plumbing only.  
Weakest theory and matrix: see held-out JSON (re-run after corpus expansions).

## POWER ANALYSIS

- Method: Monte Carlo work-level permutation of Δ_Q (`src/rishiq/isef2027/power_hier.py`)
- Between/within-work SD: `UNKNOWN_REQUIRES_EMPIRICAL_ESTIMATE`
- **Sample size not chosen for confirmatory freeze** until empirical variance exists
- V1 D08 (≥20 works/arm) **not** carried forward as established

## CORPUS FEASIBILITY

From `artifacts/isef2027/confirmatory_candidate_manifest.json`:

- Independent target-side candidates: ~3
- Independent primary control candidates: ~2
- On-disk unscored PD: 2
- TO_ACQUIRE: 4+
- **`v1_n20_realistic_with_current_inventory: false`**
- Do not split one work into fake independent works

## REMAINING JUDGE ATTACKS (top)

See `docs/JUDGE_ATTACK_MATRIX.md`. Still **UNRESOLVED**:

1. Fingerprints subjective until student KEEP/MODIFY/DELETE review completes
2. Sample size / power not justified (unknown ICC/variance)

Many others remain **PARTIAL**.

## STUDENT REVIEW REQUIRED

1. All packets in `protocol/isef2027_v2/fingerprint_review/review_*.yaml`
2. `artifacts/isef2027/STUDENT_DECISIONS_V2.yaml` (all `REQUIRES_STUDENT_REVIEW`)
3. Confirm/reject control acquisitions (Aristotle, Epicurus, Nyāya, Sāṃkhya, …)
4. Do **not** treat v1 `STUDENT_APPROVED_VIA_DELEGATION` as v2 approval
5. Paper/abstract remain student-authored

## CONFIRMATORY STATUS

**`LOCKED_NOT_READY`**

- Never opened, never scored
- No v2 GitHub Release
- No OSF
- Sealed candidate IDs reserved only
