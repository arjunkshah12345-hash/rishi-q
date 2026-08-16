# Your ISEF paper — write here

This file is a **workspace map**, not a draft paper. Agents must not fill abstract / conclusions / bibliography as your final voice.

## Suggested section map (you write the prose)

1. **Title** — your wording (prereg title is a starting point, not mandatory)
2. **Abstract** — you write last; ≤250 words; lead with method + honest Maxwell 0/5
3. **Introduction** — Capra-style claims → why structural comparison is needed
4. **Background** — Vaiśeṣika *ākāśa–śabda* vs *tejas*; Maxwell foil
5. **Methods** — cite frozen prereg YAML; splits; blinding; metrics; seed
6. **Exploratory results** — tables/figures from handoff; label EXPLORATORY
7. **Limitations** — contamination of DEV; confirmatory still locked; no human ratings
8. **Discussion** — comparative package ≠ ancient discovery
9. **Future work** — confirmatory unlock after acquisitions + school SRC
10. **References** — you compile

## Paste-ready evidence (do not invent numbers)

| Need | Path |
|------|------|
| Headline facts | `chatgpt-handoff/data/FACTS.json` |
| Scorecard figure | `chatgpt-handoff/figures/fig56_scorecard.png` |
| Rubric heatmap | `chatgpt-handoff/figures/fig54_rubric_heatmap.png` |
| Claim boundary | `chatgpt-handoff/figures/fig60_claim_boundary.png` |
| Kaṇāda table | `chatgpt-handoff/tables/T_kanada_attestation.csv` |
| Maxwell table | `chatgpt-handoff/tables/M_maxwell_confrontation.csv` |
| Constraints | `chatgpt-handoff/CONSTRAINTS.md` |
| Prompt for ChatGPT drafting help | `chatgpt-handoff/CHATGPT_PROMPT.md` |
| Frozen prereg | `protocol/isef2027_prereg_TEMPLATE.yaml` |
| Ethics memo | `ethics/isef2027_SRC_IRB_DETERMINATION.md` |

## Hard claim rules (copy into your draft)

- Maxwell structural hits: **0/5**
- Fair-coin P=1/64 is **descriptive / exploratory**, not confirmatory
- Verdict ceiling: comparative package, **not** ancient EM/QM
- Confirmatory analysis: **not yet run** (sealed locked)

## Optional LaTeX / Doc scaffold

Use `paper/` for your own `.tex` / `.docx`. Existing `paper/isef_report.tex` is optional scaffolding — rewrite freely; do not treat agent prose as final.
