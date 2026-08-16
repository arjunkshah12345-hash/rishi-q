# ChatGPT handoff pack — ISEF-AKASA-SOUND-FIELD

Everything needed to write the ISEF report **outside** this repo (e.g. ChatGPT).

## Start here
1. Open `CHATGPT_PROMPT.md` and paste into ChatGPT
2. Upload this whole folder (or zip it)
3. ChatGPT should follow `CONSTRAINTS.md` + `data/FACTS.json`

## What’s inside
| Folder / file | Contents |
|---|---|
| `data/` | FACTS.json, summary.json, expansion_v2.json, verdicts, novelty |
| `tables/` | All result CSVs |
| `figures/` | Existing boards + new fig50–fig62 visualizations |
| `evidence/` | Sutra excerpts + evidence.json |
| `corpus_snippets/` | GRETIL Kaṇāda + Praśastapāda text caches |
| `scripts/` | Reproducibility scripts |
| `PROCESS.md` / `METHODS.md` | How the work was done |
| `CONSTRAINTS.md` | Hard claim boundaries |
| `ASSET_INDEX.md` | Full file list |
| `paper_legacy_do_not_use/` | Old PDF — **ignore style** |

## Headline numbers (do not change)
- Kaṇāda **9/9**
- Praśastapāda **6/6**
- Maxwell **0/5**
- R2 unique among 6 traditions
- Fair-coin null **P = 1/64 = 0.015625**
- Verdict: `GROUNDBREAKING_COMPARATIVE_PACKAGE_NOT_ANCIENT_EM`

## Rebuild
```bash
uv run python scripts/build_chatgpt_handoff.py
```
