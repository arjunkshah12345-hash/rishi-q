# RISHI-Q

**Computational comparative history of physics** — classical Sanskrit natural philosophy tested against Greek, Chinese, Buddhist, and modern electromagnetic controls.

[![CI](https://github.com/arjunkshah12345-hash/rishi-q/actions/workflows/ci.yml/badge.svg)](https://github.com/arjunkshah12345-hash/rishi-q/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Prereg](https://img.shields.io/badge/prereg-frozen%20v1-15803d)](https://github.com/arjunkshah12345-hash/rishi-q/releases/tag/prereg-isef2027-v1)
[![Confirmatory](https://img.shields.io/badge/confirmatory-LOCKED-b91c1c)](corpus/confirmatory_sealed/lock.json)
[![Maxwell](https://img.shields.io/badge/Maxwell%20hits-0%2F5-b91c1c)](chatgpt-handoff/tables/M_maxwell_confrontation.csv)

> **Not** a Capra-style claim that ancient India discovered electromagnetism or quantum mechanics.  
> **Yes** an open, falsifiable, multi-civilization structural comparison package.

**Your job as author:** write the paper / abstract / poster.  
**This repo** contains the exploratory evidence and a V2 research framework currently undergoing external method validation (reproducibility tooling, freezes, visuals). It is **not** finished science: confirmatory analysis remains locked, fingerprints await student review, and the final method holdout is unevaluated.

---

## Status at a glance

Machine-readable: [`artifacts/isef2027/PROJECT_STATUS.json`](artifacts/isef2027/PROJECT_STATUS.json)

| Gate | Status |
|------|--------|
| Flagship exploratory (`ISEF-AKASA-SOUND-FIELD`) | **Frozen & public** (exploratory) |
| V1 prereg GitHub Release | **Untouched historical timestamp** ([link](https://github.com/arjunkshah12345-hash/rishi-q/releases/tag/prereg-isef2027-v1)) — **superseded for future confirmatory by v2 development** |
| V2 methodology | **`V2_CANDIDATE_REQUIRES_STUDENT_FREEZE`** — see [`docs/V1_TO_V2_METHOD_CORRECTIONS.md`](docs/V1_TO_V2_METHOD_CORRECTIONS.md) |
| Pedagogy theory benchmark | **Development contaminated** — not final holdout ([reset doc](docs/THEORY_VALIDATION_HOLDOUT_RESET.md)) |
| External method validation | **In progress** — source-grouped corpus v2; final holdout **UNEVALUATED** |
| Confirmatory sealed | **IDs reserved; outcomes unscored; analysis LOCKED_NOT_READY** |
| OSF | **Not submitted** |
| Human ratings | **Not collected** |
| Paper / abstract | **You write** — [`paper/STUDENT_WRITE_HERE.md`](paper/STUDENT_WRITE_HERE.md) |

Full dashboard: [`docs/STATUS.md`](docs/STATUS.md) · Judge attacks: [`docs/JUDGE_ATTACK_MATRIX.md`](docs/JUDGE_ATTACK_MATRIX.md)

---

## Flagship result — ISEF-AKASA-SOUND-FIELD

| Gate | Score |
|------|------:|
| Kaṇāda primary attestation (T1–T9) | **9/9** |
| Praśastapāda commentarial replication (C1–C6) | **6/6** |
| Maxwell EM structural hits (M1–M5) | **0/5** |
| R2 (sound ↔ pervasive medium) unique among 6 traditions | **Yes** |
| Fair-coin descriptive null \(P\) | **1/64 = 0.015625** |

**Doctrine under test:** In Vaiśeṣika (Kaṇāda), *ākāśa* is a pervasive substance whose distinctive mark is sound (*śabda*); light/heat belong to *tejas*.

**Verdict:** `GROUNDBREAKING_COMPARATIVE_PACKAGE_NOT_ANCIENT_EM`

<p align="center">
  <img src="chatgpt-handoff/figures/fig56_scorecard.png" width="720" alt="Primary scorecard" />
</p>

---

## Quick start

```bash
git clone https://github.com/arjunkshah12345-hash/rishi-q.git
cd rishi-q
uv venv && uv pip install -e ".[dev]"

make status          # freeze / lock scorecard
make reproduce       # ISEF2027 harness (never opens sealed)
make visuals         # open interactive 3D index
make flagship        # re-run exploratory flagship scripts
make validate-freeze # check prereg SHA256 manifest
```

Or without Make:

```bash
uv run rishiq-isef status
uv run rishiq-isef reproduce-all --config configs/isef2027.yaml
open visuals/isef2027/index.html
```

---

## Where to go

| You want… | Go to |
|-----------|--------|
| **Write the ISEF paper** | [`paper/STUDENT_WRITE_HERE.md`](paper/STUDENT_WRITE_HERE.md) |
| **Evidence pack for drafting** | [`chatgpt-handoff/`](chatgpt-handoff/) |
| **Frozen prereg** | [`protocol/isef2027_prereg_TEMPLATE.yaml`](protocol/isef2027_prereg_TEMPLATE.yaml) · [Release](https://github.com/arjunkshah12345-hash/rishi-q/releases/tag/prereg-isef2027-v1) |
| **Decisions log** | [`artifacts/isef2027/STUDENT_DECISIONS.yaml`](artifacts/isef2027/STUDENT_DECISIONS.yaml) |
| **SRC / ethics** | [`ethics/`](ethics/) |
| **3D / animated visuals** | [`visuals/isef2027/`](visuals/isef2027/) |
| **Gap audit** | [`docs/ISEF2027_GAP_AUDIT.md`](docs/ISEF2027_GAP_AUDIT.md) |
| **AI transparency** | [`AI_USAGE_LOG.md`](AI_USAGE_LOG.md) |

---

## Claim boundary

| CLAIM | REFUSE |
|-------|--------|
| Recoverable sound-medium ontology | Ancient Maxwell discovery |
| Primary + commentarial attestation | Ancient quantum mechanics |
| R2 unique on 6-tradition panel | *ākāśa* = EM / quantum vacuum |
| Open falsification vs Maxwell | Lab detection of *ākāśa* |
| Descriptive null + novelty audit | “First notice of *ākāśa*–sound” |

<p align="center">
  <img src="chatgpt-handoff/figures/fig60_claim_boundary.png" width="720" alt="Claim boundary" />
</p>

---

## Repository map

```
rishi-q/
├── FLAGSHIP_FINDING.md          exploratory lead claim (frozen)
├── chatgpt-handoff/             report-writing evidence pack
├── paper/STUDENT_WRITE_HERE.md  your paper workspace
├── protocol/                    prereg + hypotheses (frozen)
├── ethics/                      SRC/IRB determination packet
├── artifacts/isef2027/          decisions, splits, freeze manifests
├── ontology/concept_graph/      FROZEN structural graphs
├── corpus/confirmatory_sealed/  LOCKED holdout
├── visuals/isef2027/            interactive method visuals
├── src/rishiq/isef2027/         confirmatory firewall + harness
└── results/                     exploratory + harness outputs
```

---

## License · Citation · Author

MIT — [`LICENSE`](LICENSE). Citation: [`CITATION.cff`](CITATION.cff).  
Flagship experiment ID: `ISEF-AKASA-SOUND-FIELD`.

**Arjun Shah** — Stratford Preparatory Milpitas · Independent research / RISHI-Q
