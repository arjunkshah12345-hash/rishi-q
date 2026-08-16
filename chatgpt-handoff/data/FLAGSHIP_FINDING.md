# Flagship finding — ISEF lead (v2 groundbreaking package)

**Author:** Arjun Shah  
**Report:** [`paper/isef_report.pdf`](paper/isef_report.pdf)  
**Figures:** `fig41`–`fig49`

## Safe groundbreaking claim
Open computational package: GRETIL Kaṇāda **9/9** + Praśastapāda **6/6** + six-tradition R2 uniqueness (only Vaiśeṣika) + Maxwell foil **0/5** + descriptive null \(P=1/64\) + novelty audit — while **refusing** Capra EM/QM anticipation.

## Headline numbers
| Gate | Score |
|------|-------|
| Kaṇāda attestation | **9/9** |
| Praśastapāda replication | **6/6** |
| Maxwell EM hits | **0/5** |
| R2 unique among 6 traditions | **Yes** |
| Fair-coin null \(P\) | **0.0156 (1/64)** |

**Verdict:** `GROUNDBREAKING_COMPARATIVE_PACKAGE_NOT_ANCIENT_EM`

## Reproduce
```bash
uv run python scripts/run_isef_akasa_sound_field.py
uv run python scripts/make_isef_extra_figures.py
uv run python scripts/run_isef_expansion_v2.py
cd paper && tectonic isef_report.tex
```
