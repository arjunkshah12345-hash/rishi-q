# Worked examples (exploratory instrument checks)

> Not Sanskrit confirmatory results.

## Strongest QS (physics references)

- `PHYS_QM_001` — QS=0.900, QEF=1.000, QM=1.000
- `PHYS_ENTANGLE_001` — QS=0.800, QEF=1.000, QM=0.800
- `PHYS_QFT_001` — QS=0.333, QEF=1.000, QM=0.200

## Unity metaphor (must fail Q06)

{
  "passage_scores": [
    {
      "passage_id": "SYN_UNITY_001",
      "QS": 0.0,
      "QEF": 0.0
    }
  ],
  "Q06_annotation": [
    {
      "passage_id": "SYN_UNITY_001",
      "label": "0",
      "evidence": "Everything is one",
      "reason": "generic unity/interconnection does not support nonseparability"
    }
  ],
  "lesson": "Generic unity must not count as nonseparability."
}

## Entanglement control (should support Q06)

{
  "passage_scores": [
    {
      "passage_id": "PHYS_ENTANGLE_001",
      "QS": 0.8,
      "QEF": 1.0,
      "quantum_mechanics": 0.8
    }
  ],
  "Q06_annotation": [
    {
      "passage_id": "PHYS_ENTANGLE_001",
      "label": "1",
      "evidence": "For two systems prepared jointly, the joint state cannot be represented as independent component states.",
      "reason": "matched structural cue for Q06"
    }
  ],
  "lesson": "Explicit non-factorizable joint state supports Q06."
}
