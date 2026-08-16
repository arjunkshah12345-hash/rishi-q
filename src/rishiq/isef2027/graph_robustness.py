"""Synthetic graph-transformation robustness benchmark (algorithm validation).

Synthetic data is appropriate here: ground-truth relationship is known by construction.
Not used for confirmatory ancient-text claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from rishiq.isef2027.concept_graph import ConceptGraph, EdgeKind, GraphEdge, GraphNode, NodeKind
from rishiq.isef2027.evidence import EvidenceClass, ProvenanceEnvelope, attach_provenance
from rishiq.isef2027.graph_similarity import (
    structural_similarity_bundle,
)


def _base_graph() -> ConceptGraph:
    return ConceptGraph(
        graph_id="base_em_like",
        domain="theory_fingerprint",
        status="SYNTHETIC_BENCH",
        nodes=[
            GraphNode(id="charge", kind=NodeKind.entity, label="charge"),
            GraphNode(id="field", kind=NodeKind.field_medium, label="field"),
            GraphNode(id="force", kind=NodeKind.interaction, label="force"),
            GraphNode(id="space", kind=NodeKind.space, label="space"),
        ],
        edges=[
            GraphEdge(source="charge", target="field", kind=EdgeKind.CAUSES),
            GraphEdge(source="field", target="force", kind=EdgeKind.CARRIES),
            GraphEdge(source="force", target="charge", kind=EdgeKind.INTERACTS_WITH),
            GraphEdge(source="field", target="space", kind=EdgeKind.LOCATED_IN),
        ],
    )


def _rename_ids(g: ConceptGraph) -> ConceptGraph:
    g = g.model_copy(deep=True)
    mapping = {n.id: f"n{i}" for i, n in enumerate(g.nodes)}
    for n in g.nodes:
        n.id = mapping[n.id]
        n.label = f"L-{n.label}"
    for e in g.edges:
        e.source = mapping[e.source]
        e.target = mapping[e.target]
    g.graph_id = "renamed_ids"
    return g


def _rename_labels(g: ConceptGraph) -> ConceptGraph:
    g = g.model_copy(deep=True)
    for i, n in enumerate(g.nodes):
        n.label = f"alias_{i}"
    g.graph_id = "renamed_labels"
    return g


def _reorder(g: ConceptGraph) -> ConceptGraph:
    g = g.model_copy(deep=True)
    g.nodes = list(reversed(g.nodes))
    g.edges = list(reversed(g.edges))
    g.graph_id = "reordered"
    return g


def _add_isolated(g: ConceptGraph, k: int = 18) -> ConceptGraph:
    g = g.model_copy(deep=True)
    for i in range(k):
        g.nodes.append(
            GraphNode(id=f"junk_{i}", kind=NodeKind.entity, label=f"junk{i}")
        )
    g.graph_id = f"plus_{k}_isolated"
    return g


def _add_irrelevant_subgraph(g: ConceptGraph) -> ConceptGraph:
    g = g.model_copy(deep=True)
    g.nodes.extend(
        [
            GraphNode(id="x1", kind=NodeKind.process, label="x1"),
            GraphNode(id="x2", kind=NodeKind.process, label="x2"),
            GraphNode(id="x3", kind=NodeKind.state, label="x3"),
        ]
    )
    g.edges.extend(
        [
            GraphEdge(source="x1", target="x2", kind=EdgeKind.TRANSFORMS_INTO),
            GraphEdge(source="x2", target="x3", kind=EdgeKind.DEPENDS_ON),
        ]
    )
    g.graph_id = "plus_irrelevant_subgraph"
    return g


def _delete_edges(g: ConceptGraph, frac: float = 0.5) -> ConceptGraph:
    g = g.model_copy(deep=True)
    n_del = max(1, int(round(len(g.edges) * frac)))
    g.edges = g.edges[n_del:]
    g.graph_id = f"delete_edges_{frac}"
    return g


def _change_edge_types(g: ConceptGraph) -> ConceptGraph:
    g = g.model_copy(deep=True)
    alt = [
        EdgeKind.DISTINCT_FROM,
        EdgeKind.DISCRETE,
        EdgeKind.NONLOCAL,
        EdgeKind.COMPOSED_OF,
    ]
    for i, e in enumerate(g.edges):
        e.kind = alt[i % len(alt)]
    g.graph_id = "changed_edge_types"
    return g


def _change_node_kinds(g: ConceptGraph) -> ConceptGraph:
    g = g.model_copy(deep=True)
    kinds = [NodeKind.time, NodeKind.measurement, NodeKind.process, NodeKind.transformation]
    for i, n in enumerate(g.nodes):
        n.kind = kinds[i % len(kinds)]
    g.graph_id = "changed_node_kinds"
    return g


def _duplicate_nodes(g: ConceptGraph) -> ConceptGraph:
    g = g.model_copy(deep=True)
    extras = []
    for i, n in enumerate(list(g.nodes)):
        extras.append(
            GraphNode(id=f"{n.id}_dup", kind=n.kind, label=n.label)
        )
    g.nodes.extend(extras)
    g.graph_id = "duplicated_nodes"
    return g


def _random_rewire(g: ConceptGraph, seed: int = 0) -> ConceptGraph:
    g = g.model_copy(deep=True)
    rng = np.random.default_rng(seed)
    ids = [n.id for n in g.nodes]
    kinds = list(EdgeKind)
    new_edges = []
    for _ in g.edges:
        a, b = rng.choice(ids, size=2, replace=False)
        new_edges.append(GraphEdge(source=str(a), target=str(b), kind=kinds[int(rng.integers(0, len(kinds)))]))
    g.edges = new_edges
    g.graph_id = "random_rewire"
    return g


def _unrelated_same_size(g: ConceptGraph) -> ConceptGraph:
    g2 = ConceptGraph(
        graph_id="unrelated",
        domain="theory_fingerprint",
        status="SYNTHETIC_BENCH",
        nodes=[
            GraphNode(id=f"u{i}", kind=NodeKind.time, label=f"u{i}") for i in range(len(g.nodes))
        ],
        edges=[
            GraphEdge(source=f"u{i}", target=f"u{(i+1)%len(g.nodes)}", kind=EdgeKind.DISTINCT_FROM)
            for i in range(len(g.edges))
        ],
    )
    return g2


def _empty() -> ConceptGraph:
    return ConceptGraph(graph_id="empty", domain="theory_fingerprint", status="SYNTHETIC_BENCH")


TRANSFORMS: dict[str, Callable[[ConceptGraph], ConceptGraph]] = {
    "rename_ids": _rename_ids,
    "rename_labels": _rename_labels,
    "reorder": _reorder,
    "add_isolated_18": lambda g: _add_isolated(g, 18),
    "add_irrelevant_subgraph": _add_irrelevant_subgraph,
    "delete_edges_50pct": lambda g: _delete_edges(g, 0.5),
    "change_edge_types": _change_edge_types,
    "change_node_kinds": _change_node_kinds,
    "duplicate_nodes": _duplicate_nodes,
    "random_rewire": _random_rewire,
}


def run_graph_transformation_benchmark(root: Path) -> dict[str, Any]:
    base = _base_graph()
    identical = base.model_copy(deep=True)
    results: dict[str, Any] = {}

    bund_id = structural_similarity_bundle(base, identical)
    results["identical"] = bund_id

    ren = _rename_ids(base)
    results["isomorphic_renamed"] = structural_similarity_bundle(base, ren)

    small = ConceptGraph(
        graph_id="two_node",
        domain="theory_fingerprint",
        nodes=base.nodes[:2],
        edges=[e for e in base.edges if e.source in {n.id for n in base.nodes[:2]} and e.target in {n.id for n in base.nodes[:2]}],
    )
    bloated = _add_isolated(small, 18)
    results["size_mismatch_2_vs_20"] = structural_similarity_bundle(small, bloated)

    results["empty_vs_nonempty"] = structural_similarity_bundle(_empty(), base)
    results["unrelated_same_size"] = structural_similarity_bundle(base, _unrelated_same_size(base))
    results["duplicate_inflation"] = structural_similarity_bundle(base, _duplicate_nodes(base))

    curve = []
    for name, fn in TRANSFORMS.items():
        other = fn(base)
        bund = structural_similarity_bundle(base, other)
        curve.append(
            {
                "transform": name,
                "typed_relation": bund["typed_relation_multiset"],
                "hungarian": bund["hungarian_role_alignment"],
                "primary": bund["primary_structural"],
            }
        )
    results["robustness_curve"] = curve

    # Qualitative expectations (for tests / report)
    results["expectations"] = {
        "stable_under": ["rename_ids", "rename_labels", "reorder"],
        "gradual_degrade": ["delete_edges_50pct", "add_isolated_18", "add_irrelevant_subgraph"],
        "strong_degrade": ["change_edge_types", "random_rewire", "change_node_kinds"],
    }

    payload = attach_provenance(
        {
            "benchmark_id": "ISEF2027-GRAPH-TRANSFORM-ROBUSTNESS-v1",
            "size_mismatch_policy": "Option_B_quality_times_coverage",
            "results": results,
        },
        ProvenanceEnvelope(
            evidence_class=EvidenceClass.SOFTWARE_DEMO,
            synthetic=True,
            real_text=False,
            phase="validation",
            source_split="synthetic_algorithm_bench",
            method_version="graph_transform_v1",
            notes="Algorithm validation only; not ancient-text evidence.",
        ),
    )
    out = root / "results/isef2027/validation/graph_transformation_robustness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
