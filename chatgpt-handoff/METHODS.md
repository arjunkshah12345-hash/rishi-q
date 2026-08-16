# Methods (operational)

## Materials
See `data/FACTS.json` → materials. Corpus files in `corpus_snippets/`.

## Procedure A — Primary attestation
- Input: GRETIL typed Sanskrit (cached).
- Checklist: T1–T9 in `tables/T_kanada_attestation.csv`.
- Pass rule: expected sutra ID(s) present AND pattern/content match on body (compact match allowed because GRETIL often omits spaces).

## Procedure B — Maxwell confrontation
- Items M1–M5 in `tables/M_maxwell_confrontation.csv`.
- Scored against attested Vaiśeṣika ontology, not against English metaphors.

## Procedure C — Comparative rubric
- Features R1–R6 defined in `data/FACTS.json`.
- Vectors in `tables/R_six_tradition_vectors.csv`.
- Lucretius/Timaeus: PD English keyword hits + scholarly overrides (documented in summary.json notes).
- Dao De Jing / Dhammapada: PD panels; no Vaiśeṣika-style sound-marked ether → R2=0.

## Procedure D — Praśastapāda replication
- Items C1–C6 in `tables/C_prasastapada_replication.csv`.

## Procedure E — Nulls
- See `tables/null_models.csv` and `data/expansion_v2.json` → null_models.
- Descriptive only — not a generative cultural model.

## Procedure F — Novelty
- See `data/NOVELTY.md` and expansion novelty block.

## Risk / ethics
- No human subjects, vertebrate animals, or hazardous agents.
- Public digital texts only.
