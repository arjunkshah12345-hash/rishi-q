"""Core unit tests for RISHI-Q scientific invariants."""

from __future__ import annotations

from pathlib import Path

import pytest

from rishiq.annotation import HeuristicAnnotationBackend
from rishiq.blinding import anonymous_id, blind_passage
from rishiq.experiments.firewall import ConfirmatoryLockedError, assert_not_confirmatory_path
from rishiq.fingerprints import load_all_fingerprints
from rishiq.ingest.synthetic import modern_physics_passages, synthetic_philosophy_passages
from rishiq.models import AnnotationLabel, FeatureAnnotation, Passage
from rishiq.models.ontology import load_ontology, validate_ontology_file
from rishiq.provenance import build_manifest, sha256_text
from rishiq.similarity import (
    annotations_to_vector,
    quantum_exclusive_feature_score,
    quantum_specificity_score,
    score_all_theories,
    weighted_jaccard,
)
from rishiq.masking import make_variants
from rishiq.validation import verify_evidence

ROOT = Path(__file__).resolve().parents[1]
ONT = ROOT / "ontology" / "ontology_v0.1.yaml"
FP = ROOT / "ontology" / "physics_fingerprints"


def test_ontology_schema():
    r = validate_ontology_file(ONT)
    assert r["ok"]
    assert r["n_features"] >= 35
    assert r["n_quantum_specific"] >= 8


def test_passage_schema_requires_text():
    with pytest.raises(Exception):
        Passage(
            passage_id="x",
            tradition="t",
            work="w",
            source_language="en",
            translation="",
            source_text="",
        )


def test_positive_annotation_requires_evidence():
    with pytest.raises(Exception):
        FeatureAnnotation(
            passage_id="p",
            feature_id="Q06",
            label=AnnotationLabel.YES,
            evidence="",
            annotator="t",
            model_version="0",
        )


def test_unity_does_not_trigger_nonseparability():
    ont = load_ontology(ONT)
    backend = HeuristicAnnotationBackend()
    p = next(x for x in synthetic_philosophy_passages() if x.passage_id == "SYN_UNITY_001")
    b = blind_passage(p)
    props = backend.extract_propositions(b)
    anns = backend.verify(backend.annotate_features(b, props, ont), b, ont)
    q06 = next(a for a in anns if a.feature_id == "Q06")
    assert q06.label != AnnotationLabel.YES


def test_em_field_like_not_automatically_quantum():
    ont = load_ontology(ONT)
    fps = load_all_fingerprints(FP)
    backend = HeuristicAnnotationBackend()
    p = next(x for x in modern_physics_passages() if x.passage_id == "PHYS_EM_001")
    b = blind_passage(p)
    anns = backend.verify(
        backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
    )
    vec = annotations_to_vector(p.passage_id, anns, ont.feature_ids(), ont.version)
    scores = {s.theory_id: s.score for s in score_all_theories(vec, fps)}
    assert scores["classical_em"] > scores["newtonian"]
    # EM should not look more quantum-specific than classical EM match implies
    qs = quantum_specificity_score(score_all_theories(vec, fps))
    assert qs < 0.25  # classical field should not dominate as specifically quantum


def test_entanglement_triggers_nonseparability():
    ont = load_ontology(ONT)
    backend = HeuristicAnnotationBackend()
    p = next(x for x in modern_physics_passages() if x.passage_id == "PHYS_ENTANGLE_001")
    b = blind_passage(p)
    anns = backend.verify(
        backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
    )
    q06 = next(a for a in anns if a.feature_id == "Q06")
    assert q06.label == AnnotationLabel.YES
    assert q06.evidence


def test_qm_has_positive_qs_vs_newton():
    ont = load_ontology(ONT)
    fps = load_all_fingerprints(FP)
    backend = HeuristicAnnotationBackend()
    p = next(x for x in modern_physics_passages() if x.passage_id == "PHYS_QM_001")
    b = blind_passage(p)
    anns = backend.verify(
        backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
    )
    vec = annotations_to_vector(p.passage_id, anns, ont.feature_ids(), ont.version)
    scores = score_all_theories(vec, fps)
    by = {s.theory_id: s.score for s in scores}
    assert by["quantum_mechanics"] > by["newtonian"]
    assert quantum_specificity_score(scores) > 0
    assert quantum_exclusive_feature_score(vec, ["Q01", "Q02", "Q03", "Q05", "Q06", "Q07"]) > 0


def test_ignorance_not_fundamental_probability():
    ont = load_ontology(ONT)
    backend = HeuristicAnnotationBackend()
    p = next(x for x in modern_physics_passages() if x.passage_id == "PHYS_THERMO_001")
    b = blind_passage(p)
    anns = backend.verify(
        backend.annotate_features(b, backend.extract_propositions(b), ont), b, ont
    )
    q03 = next(a for a in anns if a.feature_id == "Q03")
    assert q03.label != AnnotationLabel.YES


def test_blinding_stable_and_strips_identity_fields():
    p = synthetic_philosophy_passages()[0]
    b = blind_passage(p)
    assert b.anonymous_id.startswith("PASSAGE_")
    assert anonymous_id(p.passage_id) == b.anonymous_id
    assert "tradition" not in b.model_dump()


def test_na_excluded_from_jaccard():
    x = {"A": 1.0, "B": None, "C": 0.0}
    t = {"A": 1.0, "B": 1.0, "C": 1.0}
    # B excluded; A contributes 1/1, C contributes 0/1 → 0.5
    assert weighted_jaccard(x, t) == pytest.approx(0.5)


def test_masking_reversible_audit():
    text = "Cosmic energy permeates the field of vibration."
    variants = make_variants(text)
    assert "[MASKED]" in variants["masked"]["text"]
    assert "energy" not in variants["neutralized"]["text"].lower()
    assert variants["original"]["text"] == text


def test_confirmatory_firewall():
    with pytest.raises(ConfirmatoryLockedError):
        assert_not_confirmatory_path(ROOT / "corpus" / "confirmatory_locked" / "secret.parquet")


def test_manifest_fields():
    m = build_manifest(
        experiment_id="t",
        dataset_hash=sha256_text("x"),
        ontology_version="0.1.0",
        prompt_version="ann-v0.1",
        model_name="heuristic",
    )
    assert m.experiment_id == "t"
    assert m.dataset_hash
    assert m.timestamp
