"""Field-ontology secondary analysis (prāṇa / ākāśa / śakti / spanda)."""

from __future__ import annotations

from enum import Enum

from rishiq.models import FeatureVector


FIELD_CORE = ["F01", "F02", "F03", "F04", "F05", "F06"]
FIELD_QUANTUM = ["F07", "Q08"]


class FieldOntologyClass(str, Enum):
    METAPHOR_SUBSTRATE_ONLY = "metaphor_substrate_only"
    FIELD_LIKE = "field_like"
    CLASSICAL_FIELD_LIKE = "classical_field_like"
    POTENTIALLY_QFT_LIKE = "potentially_qft_like"
    INSUFFICIENT = "insufficient"


def classify_field_ontology(vector: FeatureVector) -> dict:
    """Conservative classification from field-like features only."""
    vals = vector.values

    def pos(fid: str) -> bool:
        return vals.get(fid) == 1.0

    n_core = sum(1 for f in FIELD_CORE if pos(f))
    has_quant = any(pos(f) for f in FIELD_QUANTUM)

    if n_core == 0 and not pos("O01") and not pos("O04"):
        cls = FieldOntologyClass.INSUFFICIENT
    elif n_core <= 1 and not has_quant:
        cls = FieldOntologyClass.METAPHOR_SUBSTRATE_ONLY
    elif n_core >= 3 and not has_quant:
        cls = FieldOntologyClass.CLASSICAL_FIELD_LIKE
    elif n_core >= 2 and not has_quant:
        cls = FieldOntologyClass.FIELD_LIKE
    elif has_quant and n_core >= 2:
        cls = FieldOntologyClass.POTENTIALLY_QFT_LIKE
    else:
        cls = FieldOntologyClass.METAPHOR_SUBSTRATE_ONLY

    return {
        "passage_id": vector.passage_id,
        "class": cls.value,
        "n_field_core_positive": n_core,
        "has_quantized_excitation": has_quant,
        "note": "Never label quantum solely because of energy language.",
    }
