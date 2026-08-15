# RISHI-Q Discovery Report (System B)

**Status:** EXPLORATORY — not confirmatory H1.  
**Standard:** Motifs discovered without physics labels first; physics mapping applied afterward.  
**Integrity:** Numbers trace to `results/discovery/` code outputs. Do not claim Tier 5 without extraordinary evidence.

## 1. Top New Findings

- System B discovery pipeline executed: graphs → unsupervised motifs → post-hoc physics map.
- No candidate auto-promoted to STRONG_DISCOVERY_CANDIDATE (novelty gate + literature review required).
- Combinatorial mining found 7 feature co-occurrence patterns (min_support=3).
- Cluster-aware bootstrap computed for 15 top motifs (work-level).
- 23 motifs appear in historical controls but not target under current annotator — weakens Sanskrit-specific quantum readings for those structures.
- Claims-vs-data: 'ākāśa = quantum field' best matches classical_field_like_ontology (quantum components unsupported in this sample).
- Popular claim divergence: 'ākāśa = quantum field' lacks quantum-specific features in sample.
- Popular claim divergence: 'spanda = quantum vibration' lacks quantum-specific features in sample.
- Claims-vs-data: 'Brahman = unified field' best matches classical_or_field_like_ontology (quantum components unsupported in this sample).
- Claims-vs-data: 'oneness = entanglement' best matches classical_or_field_like_ontology (quantum components unsupported in this sample).
- Popular claim divergence: 'aṇu = quantum particle' lacks quantum-specific features in sample.
- Surprisal engine flagged 4 anomaly candidates after artifact guards.
- Translation-shift graphs built for 1 aligned passage families (demo).


## 2. Discovered Structural Motifs

| Rank | Motif | Support | Enrichment | Physics family (post-hoc) | Signature (abbrev) |
|------|-------|---------|------------|---------------------------|--------------------|
| 1 | M006 | 20 | 6.33 | field_like | `E:manifests_as, N:manifestation, N:substrate` |
| 2 | M012 | 13 | 6.33 | field_like | `E:manifests_as, N:substrate` |
| 3 | M001 | 36 | 1.73 | field_like | `E:pervades, N:space, N:substrate` |
| 4 | M003 | 21 | 1.73 | field_like | `E:pervades, N:space` |
| 5 | M004 | 21 | 1.73 | field_like | `E:pervades, N:substrate` |
| 6 | M011 | 13 | 6.33 | unrelated | `E:manifests_as, N:manifestation` |
| 7 | M013 | 13 | 6.33 | unrelated | `N:manifestation, N:substrate` |
| 8 | M046 | 4 | 4.75 | field_like | `E:composed_of, E:manifests_as, N:constituent, N:manifestation, N:substrate` |
| 9 | M062 | 3 | 4.75 | field_like | `E:composed_of, E:manifests_as, N:substrate` |
| 10 | M071 | 3 | 4.75 | field_like | `E:manifests_as, N:constituent, N:substrate` |
| 11 | M076 | 3 | 4.75 | field_like | `E:manifests_as, N:substrate, N:whole` |
| 12 | M084 | 3 | 4.75 | field_like | `E:composed_of, E:manifests_as, N:constituent, N:substrate` |
| 13 | M086 | 3 | 4.75 | field_like | `E:composed_of, E:manifests_as, N:manifestation, N:substrate` |
| 14 | M088 | 3 | 4.75 | field_like | `E:composed_of, E:manifests_as, N:substrate, N:whole` |
| 15 | M095 | 3 | 4.75 | field_like | `E:manifests_as, N:constituent, N:manifestation, N:substrate` |

## 3. Strongest Cross-Tradition Enrichments

- **M006**: enrichment=6.333333333333333, n_target=8, n_control=3, n_works=5, ci95=[1.7243801714668323, 23.261176261955548]
- **M011**: enrichment=6.333333333333333, n_target=8, n_control=3, n_works=5, ci95=[1.7243801714668323, 23.261176261955548]
- **M012**: enrichment=6.333333333333333, n_target=8, n_control=3, n_works=5, ci95=[1.7243801714668323, 23.261176261955548]
- **M013**: enrichment=6.333333333333333, n_target=8, n_control=3, n_works=5, ci95=[1.7243801714668323, 23.261176261955548]
- **M046**: enrichment=4.75, n_target=2, n_control=1, n_works=2, ci95=[0.43687878032266064, 51.64476055196884]
- **M050**: enrichment=4.75, n_target=2, n_control=1, n_works=2, ci95=[0.43687878032266064, 51.64476055196884]
- **M051**: enrichment=4.75, n_target=2, n_control=1, n_works=2, ci95=[0.43687878032266064, 51.64476055196884]
- **M053**: enrichment=4.75, n_target=2, n_control=1, n_works=2, ci95=[0.43687878032266064, 51.64476055196884]
- **M055**: enrichment=4.75, n_target=2, n_control=1, n_works=2, ci95=[0.43687878032266064, 51.64476055196884]
- **M057**: enrichment=4.75, n_target=2, n_control=1, n_works=2, ci95=[0.43687878032266064, 51.64476055196884]

### Work-cluster bootstrap (secondary to effect size)

- **M006**: work-level enrichment=2.0, ci95=[1.0, 50.0], p_boot=1.0
- **M012**: work-level enrichment=2.0, ci95=[1.0, 50.0], p_boot=1.0
- **M001**: work-level enrichment=1.3333333333333333, ci95=[1.0, 4.0], p_boot=1.0
- **M003**: work-level enrichment=1.3333333333333333, ci95=[1.0, 4.0], p_boot=1.0
- **M004**: work-level enrichment=1.3333333333333333, ci95=[1.0, 4.0], p_boot=1.0
- **M011**: work-level enrichment=2.0, ci95=[1.0, 50.0], p_boot=1.0
- **M013**: work-level enrichment=2.0, ci95=[1.0, 50.0], p_boot=1.0
- **M046**: work-level enrichment=4.0, ci95=[1.3333333333333333, 50.0], p_boot=1.0

### Combinatorial feature patterns (label-free)

- `C001` support=6: O01, O05
- `C002` support=6: F01, O04
- `C003` support=3: D02, O01
- `C004` support=3: O01, O02
- `C005` support=3: O04, O05
- `C006` support=3: O02, O05
- `C007` support=3: D02, O04

## 4. Most Surprising Historical Patterns

- Features first-appearance count: 32
- Combinations first-appearance count: 150
- Note: Date ranges only; wide ranges indicate low chronological precision.

- `O01+O05` earliest midpoint≈0.0 (vedanta_pd, Upanishads (Paramananda tr.)) range=[-800, 800]
- `F01+O04` earliest midpoint≈0.0 (vedanta_pd, Upanishads (Paramananda tr.)) range=[-800, 800]
- `D02+O01` earliest midpoint≈0.0 (vedanta_pd, Upanishads (Paramananda tr.)) range=[-800, 800]
- `M03+O01` earliest midpoint≈0.0 (vedanta_pd, Upanishads (Paramananda tr.)) range=[-800, 800]
- `M03+O02` earliest midpoint≈0.0 (vedanta_pd, Upanishads (Paramananda tr.)) range=[-800, 800]

## 5. Translation Modernization Findings

```json
{
  "decade_modernization": [
    {
      "decade": 1870,
      "n_translations": 50,
      "lexicon_totals": {
        "particle": 4,
        "matter": 3,
        "atom": 4,
        "energy": 1,
        "force": 2,
        "vibration": 1
      },
      "mean_modern_term_mentions": 0.3,
      "mean_qs": -0.02
    },
    {
      "decade": 1880,
      "n_translations": 40,
      "lexicon_totals": {
        "energy": 1,
        "matter": 1
      },
      "mean_modern_term_mentions": 0.05,
      "mean_qs": -0.05
    },
    {
      "decade": 1890,
      "n_translations": 40,
      "lexicon_totals": {
        "force": 1
      },
      "mean_modern_term_mentions": 0.025,
      "mean_qs": 0.0
    },
    {
      "decade": 1910,
      "n_translations": 140,
      "lexicon_totals": {
        "energy": 6,
        "matter": 8,
        "force": 9,
        "field": 3,
        "atom": 7,
        "wave": 7,
        "particle": 3
      },
      "mean_modern_term_mentions": 0.30714285714285716,
      "mean_qs": -0.051190476190476196
    }
  ],
  "aligned_shift_graphs": [
    {
      "nodes": [
        {
          "id": "DEMO_SUBSTRATE_001-literal",
          "year": 1880,
          "lexicon_hits": {},
          "n_modern_terms": 0,
          "qs": 0.0,
          "features": [
            "O01",
            "O04",
            "O05"
          ]
        },
        {
          "id": "DEMO_SUBSTRATE_001-older_scholarly",
          "year": 1920,
          "lexicon_hits": {},
          "n_modern_terms": 0,
          "qs": 0.0,
          "features": [
            "O01",
            "O04",
            "O05"
          ]
        },
        {
          "id": "DEMO_SUBSTRATE_001-recent_scholarly",
          "year": 2018,
          "lexicon_hits": {
            "energy": 1,
            "field": 2,
            "vibration": 1,
            "particle": 1,
            "quantum": 1
          },
          "n_modern_terms": 6,
          "qs": 0.0,
          "features": []
        }
      ],
      "edges": [
        {
          "from": "DEMO_SUBSTRATE_001-literal",
          "to": "DEMO_SUBSTRATE_001-older_scholarly",
          "year_from": 1880,
          "year_to": 1920,
          "lexicon_gained": {},
          "features_gained": [],
          "features_lost": [],
          "delta_qs": 0
        },
        {
          "from": "DEMO_SUBSTRATE_001-older_scholarly",
          "to": "DEMO_SUBSTRATE_001-recent_scholarly",
          "year_from": 1920,
          "year_to": 2018,
          "lexicon_gained": {
            "energy": 1,
            "field": 2,
            "vibration": 1,
            "particle": 1,
            "quantum": 1
          },
          "features_gained": [],
          "features_lost": [
            "O01",
            "O04",
            "O05"
          ],
          "delta_qs": 0
        }
      ],
      "status": "exploratory",
      "passage_family": "DEMO_SUBSTRATE_001"
    }
  ],
  "status": "exploratory",
  "note": "Decade lexicon vs QS is exploratory. Aligned shift 
```

## 6. Most Anomalous Passages

- `PHYS_EM_001` surprisal=27.631 status=ANOMALY_CANDIDATE flags=[]
- `PHYS_QM_001` surprisal=27.631 status=ANOMALY_CANDIDATE flags=[]
- `PHYS_QFT_001` surprisal=27.631 status=ANOMALY_CANDIDATE flags=[]
- `PHYS_NEWTON_001` surprisal=27.518 status=ANOMALY_CANDIDATE flags=[]
- `PHYS_ENTANGLE_001` surprisal=21.198 status=TYPICAL flags=[]
- `PD_VEDANTA__053_c2059922` surprisal=20.854 status=TYPICAL flags=[]
- `PD_GREEK_LU_010_2fa7cb8b` surprisal=19.205 status=TYPICAL flags=[]
- `PD_VEDANTA__038_ae712a5f` surprisal=16.411 status=TYPICAL flags=[]
- `PD_VEDANTA__063_57c07e83` surprisal=15.025 status=TYPICAL flags=[]
- `PD_GREEK_LU_023_ae912e85` surprisal=12.747 status=TYPICAL flags=[]

## 7. Popular Claims Supported

- **ākāśa = quantum field** (C02): supported=['F01', 'O04']; best_match=classical_field_like_ontology; quantum_supported=[]
- **Brahman = unified field** (C04): supported=['O01', 'F01', 'O05']; best_match=classical_or_field_like_ontology; quantum_supported=[]
- **oneness = entanglement** (C06): supported=['O01', 'O02']; best_match=classical_or_field_like_ontology; quantum_supported=[]

## 8. Popular Claims Not Supported

- **prāṇa = energy** (C01): unsupported=['D03', 'F03']; quantum_unsupported=[]
- **spanda = quantum vibration** (C03): unsupported=['F06', 'D03']; quantum_unsupported=['Q01', 'Q02']
- **observer consciousness = measurement effect** (C05): unsupported=['M01', 'M02']; quantum_unsupported=['Q04', 'Q07']
- **aṇu = quantum particle** (C07): unsupported=['O03']; quantum_unsupported=['Q05', 'Q01']

## 9. Field-Like but Non-Quantum Findings

- **ākāśa = quantum field**: classical_field_like_ontology (quantum components absent in sample)
- **Brahman = unified field**: classical_or_field_like_ontology (quantum components absent in sample)
- **oneness = entanglement**: classical_or_field_like_ontology (quantum components absent in sample)
- Motif M001
- Motif M003
- Motif M004
- Motif M006
- Motif M012
- Motif M025
- Motif M027
- Motif M031
- Motif M032
- Motif M033

## 10. Quantum-Specific Candidates

_None identified in this exploratory run._

## 11. Novelty Literature Review

All high-ranking candidates remain **NOVELTY_REVIEW_REQUIRED**. See `novelty/` dossiers. Never claim “first ever” without completed literature search.

## 12. Alternative Explanations

- Generic metaphysics / Level I features
- Classical field-like ontology mistaken for quantum
- Translation modernization of scientific lexicon
- Annotator lexical bias (heuristic backend)
- Shared mystical tropes across civilizations (weakens Sanskrit-specific claims)
- OCR / editorial / duplicate commentary artifacts

## 13. Candidates That Failed Replication

- M046 signature not recovered on replication works
- M062 signature not recovered on replication works
- M071 signature not recovered on replication works

## 14. Strongest Discovery Candidate

```json
{
  "candidate_id": "DC-M006",
  "title": "Structural motif M006: E:manifests_as + N:manifestation + N:substrate",
  "discovery_type": "rishi_motif",
  "motif_id": "M006",
  "supporting_sources": [
    "Upanishads (Paramananda tr.)",
    "De Rerum Natura",
    "Tao Te Ching",
    "Synthetic classical EM description",
    "Synthetic QFT description"
  ],
  "n_independent_works": 5,
  "estimated_historical_period": "unknown",
  "effect_size": 2.0,
  "confidence_interval": [
    1.7243801714668323,
    23.261176261955548
  ],
  "control_comparison": "{\"passage_enrichment\": {\"motif_id\": \"M006\", \"n_target\": 8, \"n_control\": 3, \"p_target\": 0.1, \"p_control\": 0.015789473684210527, \"enrichment\": 6.333333333333333, \"enrichment_infinite\": false, \"ci95\": [1.7243801714668323, 23.261176261955548], \"n_works\": 5}, \"cluster_bootstrap\": {\"motif_id\": \"M006\", \"status\": \"ok\", \"n_target_works\": 1, \"n_control_works\": 4, \"n_present_works\": 5, \"enrichment_work_level\": 2.0, \"enrichment_infinite\": false, \"ci95\": [1.0, 50.0], \"p_boot_two_sided\": 1.0, \"note\": \"Work-cluster bootstrap; p is secondary to effect size / replication.\"}}",
  "translation_robustness": "untested",
  "model_robustness": "untested",
  "human_validation_status": "REQUIRES_EXTERNAL_HUMAN_VALIDATION",
  "nearest_physics_analogue": "classical_field_like",
  "classical_vs_quantum_specificity": "field_like",
  "prior_literature_status": "NOVELTY_REVIEW_REQUIRED",
  "alternative_explanations": [
    "generic metaphysics",
    "translation modernization",
    "annotator lexical bias",
    "shared mystical tropes across civilizations"
  ],
  "novelty_confidence": 0.0,
  "scientific_importance": 0.6875,
  "status": "NOVELTY_REVIEW_REQUIRED",
  "so_what": {
    "novelty": 0.0,
    "robustness": 1.0,
    "specificity": 1.0,
    "historical_importance": 0.4,
    "physics_relevance": 0.6,
    "interpretability": 0.7,
    "reproducibility": 0.8,
    "surprise": 1.0,
    "composite_optional": 0.6875
  },
  "notes": "gate:{'not_trivial_ontology': True, 'not_single_passage': True, 'multi_work': True, 'translation_ok': True, 'model_ok': True, 'has_effect': True, 'precise': True, 'literature_reviewed': False, 'not_rejected': True, 'not_artifact': True}"
}
```

## 15. What Is Actually New

At this stage, what is new is primarily **methodological**: an unsupervised motif-discovery layer on evidence-bound concept graphs, with post-hoc physics mapping, claims-vs-data testing, and novelty gates that refuse to declare STRONG_DISCOVERY_CANDIDATE without literature review and robustness.

Empirical motif/enrichment numbers above are **exploratory** under the current annotator and corpus partition. They are candidates for replication — not confirmatory H1 results.

---

Atlas summary: traditions=['buddhist_dhammapada_pd', 'chinese_ddj_pd', 'greek_lucretius_pd', 'greek_timaeus_pd', 'modern_physics', 'vedanta_pd']; shared_motifs=127; quantum_specific_motifs=0.
