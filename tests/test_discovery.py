"""Tests for System B discovery layer."""

from __future__ import annotations

from rishiq.discovery import PassageGraph, RishiMotif
from rishiq.discovery.graphs import extract_passage_graph
from rishiq.discovery.motifs import map_motifs_to_physics, mine_motifs, motif_enrichment
from rishiq.discovery.ranker import novelty_gate, so_what_scores
from rishiq.discovery.surprisal import compute_surprisal
from rishiq.discovery import DiscoveryCandidate
from rishiq.models import AnnotationLabel, FeatureAnnotation


def _yes(pid: str, fid: str, ev: str = "evidence span here") -> FeatureAnnotation:
    return FeatureAnnotation(
        passage_id=pid,
        feature_id=fid,
        label=AnnotationLabel.YES,
        evidence=ev,
        reason="test",
        confidence=0.8,
        annotator="test",
        model_version="t",
        prompt_version="t",
        verified=True,
    )


def test_graph_requires_evidence():
    anns = [
        FeatureAnnotation(
            passage_id="p1",
            feature_id="F01",
            label=AnnotationLabel.YES,
            evidence="the ether pervades all space",
            reason="x",
            confidence=0.7,
            annotator="t",
            model_version="t",
        )
    ]
    g = extract_passage_graph("p1", anns)
    assert any(n.node_type == "substrate" for n in g.nodes)
    assert any(e.edge_type == "pervades" for e in g.edges)
    assert "N:substrate" in g.motif_signature()


def test_motif_mining_before_physics():
    graphs = []
    for i in range(5):
        pid = f"p{i}"
        g = extract_passage_graph(
            pid,
            [_yes(pid, "F01"), _yes(pid, "F03", "wave disturbance propagates")],
        )
        graphs.append(g)
    motifs = mine_motifs(
        graphs,
        meta={f"p{i}": {"tradition": "vedanta", "work_id": f"w{i}"} for i in range(5)},
        min_support=3,
    )
    assert motifs
    assert all(m.nearest_physics is None for m in motifs)
    mapped = map_motifs_to_physics(motifs, {"classical_em": {"F01", "F03"}})
    assert any(m.physics_family in {"field_like", "classical", "unknown", "unrelated"} for m in mapped)


def test_enrichment_and_surprisal():
    m = RishiMotif(
        motif_id="M001",
        signature=["N:substrate", "E:pervades"],
        support=4,
        traditions={"vedanta": 3, "greek": 1},
        works={"a": 2, "b": 2},
    )
    enr = motif_enrichment(m, {"vedanta"}, {"greek"}, n_target=10, n_control=10)
    assert abs(enr["enrichment"] - 3.0) < 1e-9
    g = PassageGraph(passage_id="p0", nodes=[], edges=[])
    # empty graphs skipped
    rows = compute_surprisal([])
    assert rows == []


def test_novelty_gate_never_auto_strong_without_literature():
    c = DiscoveryCandidate(
        candidate_id="DC-M001",
        title="test",
        discovery_type="rishi_motif",
        motif_id="M001",
        supporting_sources=["a", "b", "c"],
        n_independent_works=3,
        effect_size=2.0,
        prior_literature_status="NOVELTY_REVIEW_REQUIRED",
        status="RAW_CANDIDATE",
    )
    c = novelty_gate(c)
    assert c.status == "NOVELTY_REVIEW_REQUIRED"
    assert c.status != "STRONG_DISCOVERY_CANDIDATE"


def test_so_what_dimensions():
    d = so_what_scores(
        novelty=0.2,
        robustness=0.5,
        specificity=0.4,
        historical_importance=0.3,
        physics_relevance=0.4,
        interpretability=0.7,
        reproducibility=0.8,
        surprise=0.3,
    )
    assert "novelty" in d and "composite_optional" in d


def test_contamination_detector():
    from rishiq.discovery.contamination import find_anachronisms, summarize_by_tradition, passage_contamination_rows

    hits = find_anachronisms("It discovered atoms, then electrons in the field.")
    assert "electron" in hits["strong"]
    assert "atom" in hits["soft"]
    rows = passage_contamination_rows(
        [
            {
                "passage_id": "a",
                "tradition": "vedanta_pd",
                "translation": "electrons orbit",
            },
            {
                "passage_id": "b",
                "tradition": "vedanta_pd",
                "translation": "the self is immortal",
            },
        ]
    )
    s = summarize_by_tradition(rows)
    assert s["vedanta_pd"]["n_contaminated"] == 1
    from rishiq.visualization.discovery import (
        plot_dual_system,
        plot_success_tiers,
    )
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        p = plot_dual_system(Path(d) / "dual.png")
        assert p.exists() and p.stat().st_size > 1000
        p2 = plot_success_tiers(Path(d) / "tiers.png")
        assert p2.exists()


def test_cluster_bootstrap_and_combos():
    from rishiq.discovery.significance import (
        cluster_enrichment_bootstrap,
        mine_feature_combinations,
    )

    m = RishiMotif(
        motif_id="M001",
        signature=["N:substrate", "E:pervades"],
        support=3,
        passages=["p1", "p2", "p3"],
        traditions={"vedanta_pd": 2, "greek": 1},
        works={"w1": 1, "w2": 1, "w3": 1},
    )
    out = cluster_enrichment_bootstrap(
        m,
        passage_to_work={"p1": "w1", "p2": "w2", "p3": "w3"},
        passage_to_role={"p1": "target", "p2": "target", "p3": "control"},
        all_works={"w1": "target", "w2": "target", "w3": "control", "w4": "control"},
        n_boot=99,
        seed=1,
    )
    assert out["status"] == "ok"
    assert "ci95" in out
    combos = mine_feature_combinations(
        {"a": {"O01", "F01"}, "b": {"O01", "F01"}, "c": {"O01", "F01", "D01"}},
        {"a": {"tradition": "t"}, "b": {"tradition": "t"}, "c": {"tradition": "c"}},
        min_support=3,
    )
    assert combos
    assert combos[0]["support"] >= 3
