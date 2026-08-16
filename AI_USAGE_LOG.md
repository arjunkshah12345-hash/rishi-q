# AI Usage Log (append-only)

Mandatory transparency log for coding-agent assistance on RISHI-Q.
Do **not** delete entries. Student should mark review status.

---

## 2026-08-16 — Cursor agent (Composer / Auto)

- **Model/tool:** Cursor agent (Composer), local tools
- **User prompt reference:** ISEF2027 mega-upgrade + animated 3D visuals; preserve exploratory freeze; no paper/abstract writing; GitHub `arjunkshah12345-hash/rishi-q`
- **Task performed:**
  - Repository inventory + exploratory freeze manifest
  - ISEF2027 package: splits, registry, concept-graph schema/templates, baselines, adversarial battery, inference scaffolding, human-val prepare-only, reproduce CLI
  - Control-panel candidate YAML; atomistic fingerprint TEMPLATE
  - Gap audit (technical)
  - Animated/interactive 3D concept visuals under `visuals/isef2027/`
  - Tests for new modules
- **Files substantially AI-generated/modified:**
  - `src/rishiq/isef2027/**`
  - `configs/isef2027.yaml`
  - `scripts/build_isef2027_visuals.py`
  - `artifacts/isef2027/**`
  - `docs/ISEF2027_GAP_AUDIT.md`
  - `ontology/concept_graph/**`
  - `ontology/physics_fingerprints/atomistic_corpuscular.yaml`
  - `human_validation/isef2027/**`
  - `visuals/isef2027/**`
  - `tests/test_isef2027.py`
  - `pyproject.toml` (entry point)
  - `AI_USAGE_LOG.md` (this file)
  - `~/AGENTS.md` + `~/.cursor/rules/github-account-routing.mdc` (earlier same day; GitHub routing)
- **Student review required:** Yes — especially TEMPLATE graphs/fingerprints, control panel approvals, confirmatory protocol text (student-written), and any interpretation.
- **Review status:** PENDING_STUDENT

---

## 2026-08-16 (evening) — “all allowed, do whats left”

- **Task:** scrubbing, full fingerprint graph templates, control inventory, calibration adversarial/power scaffold, prereg blank template, student decisions YAML, reproduce-all, extra heatmap visual
- **Files:** `scrub.py`, `graph_templates.py`, `control_panel.py`, `calibration_batteries.py`, `protocol/isef2027_prereg_TEMPLATE.yaml`, `artifacts/isef2027/STUDENT_DECISIONS.yaml`, CLI/runner/visuals/tests
- **Still not done by AI (correctly):** official question freeze, OSF submit, human recruitment, paper/abstract, confirmatory unblinding
- **Review status:** PENDING_STUDENT


- **Model/tool:** Cursor agent (Composer)
- **User prompt:** continue finishing ISEF2027 upgrade; approval to proceed
- **Task performed:**
  - Method identification benchmark (lexical / hash-embed / ontology / graph)
  - Translation contamination + mask shift battery
  - Blind export audit + private mapping hygiene
  - Discovery→replication split demo
  - Calibration manifest builder from PD passages
  - Additional 3D/animated visuals (07–09)
  - GitHub Actions CI workflow
  - Wired all into `rishiq-isef reproduce`
- **Files substantially AI-generated/modified:**
  - `src/rishiq/isef2027/benchmark.py`
  - `src/rishiq/isef2027/translation_battery.py`
  - `src/rishiq/isef2027/blind_audit.py`
  - `src/rishiq/isef2027/discovery_replication.py`
  - `src/rishiq/isef2027/calibration.py`
  - `src/rishiq/isef2027/runner.py`, `cli.py`
  - `scripts/build_isef2027_visuals.py`
  - `.github/workflows/ci.yml`
  - tests updates
- **Review status:** PENDING_STUDENT

---

## 2026-08-16 (late) — student asked agent to freeze decisions / prereg / SRC / OSF

- **User prompt:** Fill STUDENT_DECISIONS + prereg template, approve controls/graphs, SRC/IRB for humans, then OSF; student writes paper only.
- **Task performed:**
  - Froze `artifacts/isef2027/STUDENT_DECISIONS.yaml` and `protocol/isef2027_prereg_TEMPLATE.yaml` (conservative, null-capable; no paper/abstract authorship)
  - Approved control panel families; DEV works excluded from confirmatory scoring
  - Promoted concept graphs + physics vocab to FROZEN; builder skips overwrite of FROZEN
  - SRC/IRB determination: no human subjects for confirmatory primary; Form 4 N/A; school stamp still required
  - Reserved confirmatory_sealed IDs + `lock.json` without scoring outcomes
  - OSF packet + `scripts/submit_osf_prereg.sh` (needs `OSF_TOKEN`); interim GitHub Release timestamp
- **Not done:** OSF API submit (no token on machine); school SRC wet-ink; paper/abstract; human ratings; confirmatory unlock/scoring
- **Review status:** DELEGATED_FREEZE_ACKNOWLEDGED

---

## 2026-08-16 (finish polish) — “make the repo finish it make really good”

- README rewrite (frozen status, badges, Make workflow)
- `docs/STATUS.md`, `paper/STUDENT_WRITE_HERE.md` (structure only — no paper prose)
- `Makefile`, freeze validator, `rishiq-isef status`, acquisition helper stub
- Visuals gallery index upgrade; CI runs full pytest + freeze check
- Version 0.2.0; CITATION.cff remote fixed to arjunkshah12345-hash
- Still student-only: paper/abstract; school SRC stamp; optional OSF token; sealed PD acquisitions

---

## 2026-08-16 — scientific hardening pass (v2 candidate)

- Fixed CI to `uv sync --extra dev`
- Sealed-lock invariants + tests; split manifest preserves reserved sealed IDs
- V1 release untouched; `docs/V1_TO_V2_METHOD_CORRECTIONS.md` + `protocol/isef2027_v2/`
- Evidence classes; registry enforcement; PROJECT_STATUS.json
- Structural graph similarity (typed relation + Hungarian)
- Held-out theory validation corpus (TF-IDF); keyword proxy quarantined as SOFTWARE_DEMO
- Hierarchical Δ_Q power with UNKNOWN variance; toy power labeled SOFTWARE_DEMO_NOT_SAMPLE_SIZE_EVIDENCE
- Confirmatory candidate metadata manifest (unscored); translation-pair schema
- Fingerprint review packets; sanity suite; judge attack matrix
- Confirmatory status remains LOCKED_NOT_READY

## 2026-08-16 — Cursor agent (Pass 3: external + graph validation)

- **Model/tool:** Cursor agent (Composer / Auto), local tools
- **User prompt reference:** Pass 3 external method validation and graph-metric validation; confirmatory LOCKED; no accuracy chasing
- **Task performed:**
  - Downgraded pedagogy corpus to CURATED_PEDAGOGY_DEVELOPMENT_BENCHMARK; documented holdout reset
  - Fixed Hungarian unmatched-node penalty (Option B coverage)
  - Graph transformation robustness benchmark
  - External PD/OpenStax corpus with eligibility rules + source-group splits
  - Dev-only method selection, masking, LOSO/LOAO, variance/power sensitivity, ledger, final-holdout guard
  - Fingerprint graph review packets (blank decisions); README/status cleanup
- **Files substantially AI-generated/modified:**
  - `src/rishiq/isef2027/graph_similarity.py`, `graph_robustness.py`, `theory_validation*.py`, `source_eligibility.py`, `final_holdout_guard.py`, …
  - `data/theory_validation_v2/**`, `docs/THEORY_VALIDATION_HOLDOUT_RESET.md`
  - `tests/test_graph_and_theory_val.py`, `README.md`, `artifacts/isef2027/PROJECT_STATUS.json`
- **Student must review:** fingerprint KEEP/MODIFY decisions; source eligibility; whether corpus size/coverage suffices; method freeze before any final holdout eval
- **Not done by AI:** official ISEF paper/abstract/poster; confirmatory unlock; final holdout evaluation

