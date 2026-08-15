# Decision Log

Every consequential methodological decision is recorded here.  
Rule: never quietly change a scientific rule. Prefer conservative interpretations.

---

## 2026-08-15T17:00:00Z — Local protocol ingest

- **Decision:** Export Drive Master Protocol v1.0 to `protocol/master_protocol.md` via authenticated Google Docs API (`gog docs cat`) and treat it as authoritative.
- **Alternatives:** Manual rewrite from memory; wait for Drive MCP auth.
- **Reason:** Need auditable local copy before coding; MCP Drive auth failed with client-registration error.
- **Target data inspected:** No.
- **Possible effect on results:** None (documentation only).

---

## 2026-08-15T17:05:00Z — Annotation backend default

- **Decision:** Ship a deterministic **rule/heuristic annotation backend** for local MacBook development and tests; treat Hugging Face / open LLM backends as Kaggle-optional.
- **Alternatives:** Require local LLM; stub-only with no runnable pipeline.
- **Reason:** Protocol forbids requiring giant local models; MacBook Air RAM limits; reproducibility without API keys.
- **Target data inspected:** No.
- **Possible effect on results:** Heuristic labels are weaker than expert/LLM labels; exploratory only. Confirmatory must declare backend in preregistration.

---

## 2026-08-15T17:06:00Z — Ambiguous label `U`

- **Decision:** Retain `U` (ambiguous) in development schemas; treat `U` as non-positive for scoring (equivalent to NA for QS/QEF numerators).
- **Alternatives:** Collapse U→NA immediately; model U as separate category in primary endpoint.
- **Reason:** Protocol §20 allows U during development; confirmatory freeze will choose NA vs separate modeling.
- **Target data inspected:** No.
- **Possible effect on results:** Slightly reduces positive counts vs aggressive YES coding — conservative.

---

## 2026-08-15T17:07:00Z — Similarity NA handling

- **Decision:** For Jaccard-family metrics, features labeled NA/U on the passage side are **excluded** from both numerator and denominator (pairwise complete on passage-supported features only when theory fingerprint is non-zero or passage is non-NA). Theory fingerprint zeros remain classical absences.
- **Alternatives:** Impute NA as 0; use three-valued metrics only.
- **Reason:** Missing information must never become positive evidence (protocol hard rule).
- **Target data inspected:** No.
- **Possible effect on results:** Sparse annotations yield lower absolute similarities; QS differences remain interpretable.

---

## 2026-08-15T17:08:00Z — Theory fingerprint weights

- **Decision:** Fix feature weights from physics centrality *before* any Sanskrit scoring. Quantum-specific family features receive higher weight in QM/QFT fingerprints only; Level I–style features never inflate QEF.
- **Alternatives:** Learn weights from Sanskrit outcomes; uniform weights only.
- **Reason:** Protocol §38 — weights must not be optimized using target Sanskrit outcomes.
- **Target data inspected:** No.
- **Possible effect on results:** Prevents tuning toward Sanskrit–quantum resemblance.

---

## 2026-08-15T17:09:00Z — Development corpus seed content

- **Decision:** Seed development with (1) synthetic structural examples, (2) modern-physics validation passages written for ontology checks, (3) short public-domain / clearly licensed excerpt pointers and bibliographic passages where redistribution of full copyrighted text is unclear.
- **Alternatives:** Scrape copyrighted translations into public dataset.
- **Reason:** Licensing integrity (protocol §72).
- **Target data inspected:** No confirmatory data.
- **Possible effect on results:** Development sample size initially smaller than 500–800 target; pipeline scales when licensed texts are added.

---

## 2026-08-15T17:10:00Z — Confirmatory firewall

- **Decision:** `corpus/confirmatory_locked/` and `results/confirmatory/` remain empty; CLI `rishiq confirmatory` raises until preregistration flag file exists and human unlock is recorded.
- **Alternatives:** Soft warning only.
- **Reason:** Protocol §32, §66, §74 — accidental confirmatory peeking invalidates the design.
- **Target data inspected:** No.
- **Possible effect on results:** Protects Type-I error control / researcher degrees of freedom.

---

## 2026-08-15T17:30:00Z — Prototype100 size and sampling

- **Decision:** Build a synthetic development panel of **n≈174** passages (≥ protocol §95 ~100), balanced across roles/traditions, without cherry-picking quantum-sounding Sanskrit claims. Licensed historical texts remain bibliographic pointers until redistribution rights are clear.
- **Alternatives:** Stop at 11 seed passages; scrape copyrighted translations into the public tree.
- **Reason:** Protocol §95 requires an instrument prototype before mass collection; §72 forbids illegal redistribution.
- **Target data inspected:** Synthetic only (no confirmatory Sanskrit outcomes).
- **Possible effect on results:** Near-null exploratory ΔQ expected and observed; does not speak to H1.

## 2026-08-15T17:45:00Z — Refuse impressive-hunting; run PD pilot instead

- **Decision:** Do **not** unlock confirmatory or tune methods to manufacture a Sanskrit–quantum positive for publication impact. Instead acquire Project Gutenberg PD texts and run an honest exploratory pilot.
- **Alternatives:** Fabricate/cherry-pick quantum-sounding verses; claim H1 settled.
- **Reason:** Protocol research-integrity rule and §32/§74 confirmatory firewall. An impressive false positive would destroy the project’s scientific value.
- **Target data inspected:** PD development sample after this decision (exploratory only).
- **Possible effect on results:** Protects validity; may yield a negative/methods headline rather than a sensational claim.

## 2026-08-15T17:50:00Z — PD pilot floor-effect finding

- **Decision:** Report that under the **heuristic** annotator, PD historical English passages are near annotation-floor (almost all features NA), while modern-physics controls still discriminate. Treat this as an instrument limitation finding, not as confirmatory evidence that traditions lack structure.
- **Alternatives:** Quietly expand regexes until Upanishads score high; declare ancient quantum discovery.
- **Reason:** Post-hoc cue expansion aimed at raising Sanskrit QS would be exactly the bias RISHI-Q forbids. Settlement requires LLM/human annotation + preregistration.
- **Target data inspected:** Yes — exploratory PD pilot only.
- **Possible effect on results:** Honest null/floor at heuristic stage; confirmatory still locked.

## 2026-08-15T18:05:00Z — Classical NP cue pack v0.2

- **Decision:** Add optional classical natural-philosophy English cues (atoms, void, first-beginnings, etc.) to reduce floor-effect on Lucretius-like prose. Do **not** add mystical→quantum shortcuts.
- **Alternatives:** Wait solely for LLM; expand quantum cues until Upaniṣads score.
- **Reason:** Instrument must detect classical atomism if present; expanding Q-family for Sanskrit would bias H1.
- **Target data inspected:** Yes (PD pilot already seen). Effect: Lucretius classical hits increase; ΔQ remains ~0; QEF stays 0.
- **Possible effect on results:** Improves Level II sensitivity; must not be mistaken for confirmatory quantum evidence.

## 2026-08-15T18:30:00Z — System B discovery amendment

- **Decision:** Add System B (discovery engine) atop System A without weakening confirmatory controls. Motifs mined without physics labels first; physics mapping post-hoc; novelty gate refuses STRONG without literature + robustness; success ≠ positive quantum result.
- **Alternatives:** Confirmatory-only pipeline; search directly for quantum patterns.
- **Reason:** Amendment requires computational discovery of previously unreported structural patterns; searching for QM first would bias discovery.
- **Target data inspected:** Reuses exploratory PD pilot annotations only.
- **Possible effect on results:** Enables exploratory candidates; does not unlock confirmatory H1.

## 2026-08-15T19:00:00Z — System B layer closed for exploratory stage

- **Decision:** Finish discovery layer: cluster bootstrap, combinatorial mining, translation-shift graphs (demo), claims report, automated novelty search, discovery figures fig20–22. Keep confirmatory locked; no STRONG_DISCOVERY_CANDIDATE without human literature review.
- **Alternatives:** Stop at motif scaffolding; claim novelty from model ignorance.
- **Reason:** Amendment requires computational discovery machinery with rigor; exploratory PD run shows 0 quantum-specific motifs under heuristic annotator.
- **Target data inspected:** Yes — exploratory only.
- **Possible effect on results:** Enables Tier-1/2 methodological + candidate findings; does not settle H1.

## 2026-08-15T19:30:00Z — Headline finding without impressive-hunting

- **Decision:** Ship heuristic v0.3 (Level I metaphysical cues + classical NP cues; still no Q-family shortcuts). Headline finding = contamination anachronisms + Vedānta Level-I without Q + Lucretius classical structure + near-null ΔQ. Refuse ancient-QM miracle narrative.
- **Alternatives:** Expand Q-cues until Upaniṣads score; claim Tier 5.
- **Reason:** Protocol integrity; amendment says claim-divergence and translation effects are valid major results.
- **Target data inspected:** PD development only.
- **Possible effect on results:** Stronger Level I/II sensitivity; QEF/ΔQ remain non-quantum; publishable Tier-2 story.

## 2026-08-15T19:50:00Z — Capra autopsy flagship (resources push)

- **Decision:** Use web literature + ablation + curated Capra-claim autopsy as the flagship impressive result. Kaggle dataset create returned 401; no local LLM API keys. Do not fake GPU results.
- **Finding:** 5/5 Capra-style claims CONTRADICTED_AS_QUANTUM on Vedānta PD; lexicon mask ΔQS≈0; electrons passage is anti-material-science commentary (Paramananda 1919).
- **Reason:** User asked to use internet/Kaggle/viz for something truly amazing; integrity forbids inventing ancient QM.
- **Target data inspected:** PD development.
- **Possible effect on results:** Strong Tier-2/3 paper narrative; H1 still unlocked only after preregistration + LLM/human.
