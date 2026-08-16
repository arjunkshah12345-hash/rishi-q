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

## 2026-08-16 (later) — Cursor agent continuation (“keep going finish”)

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
