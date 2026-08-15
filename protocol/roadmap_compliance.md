# Protocol Roadmap Compliance

Tracked against Master Protocol v1.0 §93 (Full Experimental Roadmap) and the autonomous build brief.
Updated: 2026-08-15.

Legend: **DONE** | **PARTIAL** | **BLOCKED_EXTERNAL** | **LOCKED** | **NOT_STARTED**

| Phase | Protocol goal | Status | Evidence / notes |
|------|----------------|--------|------------------|
| 0 | Protocol local copy | DONE | `protocol/master_protocol.md` |
| 1 | Literature DB | PARTIAL | `literature/literature.csv` (21 rows, real/pending-verify); expand before freeze |
| 2 | Source manifest | DONE | `corpus/manifests/sources.csv` (licensing-aware) |
| 3 | Ontology v0.1 | DONE | YAML + definitions + examples + codebook |
| 4 | Physics validation set | DONE | Synthetic Newton/EM/Thermo/QM/QFT/entangle (+ relativity TBD in 100-set) |
| 5 | Dev corpus 500–800 | PARTIAL | **174 synthetic prototype** (§95 exceeded); licensed historical texts mostly pointers |
| 6 | Annotation prototype | DONE | extract → annotate → verify; heuristic backend |
| 7 | Human audit | BLOCKED_EXTERNAL | Package ready; `REQUIRES_EXTERNAL_HUMAN_VALIDATION` |
| 8 | Translation prototype | PARTIAL | Synthetic TCI demo done; real multi-translation pairs pending licenses |
| 9 | Freeze ontology confirmatory | NOT_STARTED | Must follow human audit + more piloting |
| 10 | Power analysis | PARTIAL | Simulation framework + exploratory curves; n not frozen |
| 11 | Confirmatory corpus | LOCKED | Empty by design |
| 12 | Preregister | BLOCKED_EXTERNAL | Draft `READY_FOR_EXTERNAL_PREREGISTRATION` |
| 13–19 | Confirmatory runs | LOCKED | Firewall enforced |
| 20 | Paper | PARTIAL | Methods + instrument manuscript with prototype100 exhibits |
| 21 | External review | BLOCKED_EXTERNAL | Not obtained |
| 22 | Public release | PARTIAL | Repo scaffold ready; no arXiv claim |

## Software milestones (§96–99)

| Milestone | Status |
|-----------|--------|
| One passage → propositions/features/evidence | DONE |
| passages.parquet → annotations.parquet | DONE |
| annotations + fingerprints → theory_scores.parquet | DONE |
| theory_scores → primary_effect + plots | DONE (exploratory `primary_effect.json` + figs 13–17) |

## Hard rules still enforced in tests

Unity ≠ Q06; EM field-like not auto-quantum; entanglement → Q06; confirmatory locked; NA excluded from Jaccard; evidence required for positives.

## What “done” means for this autonomous build

Everything that can be built without fabricating humans, expert approval, OSF submission, or illegal text redistribution.
Not: confirmatory H1 answer.
