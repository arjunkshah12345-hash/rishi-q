# PD pilot findings (heuristic v0.2 + classical NP cues)

**NOT confirmatory.**

## Contrast
- ΔQ = -0.0007 (p≈0.409)
- mean QS target=-0.0375 control=-0.0368
- QEF target=control=0.0

## Theory means
```
                        newtonian  classical_em  quantum_mechanics  quantum_field_theory     QS  QEF
tradition                                                                                           
buddhist_dhammapada_pd      0.050         0.000              0.000                 0.000 -0.050  0.0
chinese_ddj_pd              0.000         0.025              0.000                 0.025  0.000  0.0
greek_lucretius_pd          0.100         0.075              0.017                 0.075 -0.067  0.0
greek_timaeus_pd            0.050         0.080              0.030                 0.080 -0.020  0.0
vedanta_pd                  0.038         0.000              0.000                 0.000 -0.038  0.0
```

## Readout
No quantum-specific enrichment of PD Upaniṣads vs controls under heuristic v0.2.
Lucretius shows more classical/atomism hits (as expected for Level II instrument check).
Settlement still requires Kaggle LLM annotation.

## Kaggle next step
1. Upload `kaggle/rishiq_kaggle_bundle_public.zip` as dataset
2. Run `kaggle/annotation.ipynb` with GPU
3. `uv run python scripts/join_kaggle_annotations.py --annotations <downloaded>`
