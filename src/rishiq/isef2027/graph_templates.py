"""Generate TEMPLATE concept graphs for each physics fingerprint (+ historical)."""

from __future__ import annotations

import json
from pathlib import Path

from rishiq.isef2027.concept_graph import (
    ConceptGraph,
    EdgeKind,
    GraphEdge,
    GraphNode,
    NodeKind,
    write_schema_and_templates,
)


def _g(graph_id: str, nodes: list[GraphNode], edges: list[GraphEdge]) -> ConceptGraph:
    return ConceptGraph(
        graph_id=graph_id,
        domain="theory_fingerprint" if graph_id.startswith("template_fp_") else "historical_text",
        status="TEMPLATE",
        meta={"warning": "TEMPLATE — student must verify before freeze"},
        nodes=nodes,
        edges=edges,
    )


def build_all_theory_graph_templates(root: Path) -> list[Path]:
    out_dir = root / "ontology/concept_graph"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = list(write_schema_and_templates(root))

    graphs = [
        _g(
            "template_fp_newtonian",
            [
                GraphNode(id="mass", kind=NodeKind.particle_atom, label="mass point"),
                GraphNode(id="force", kind=NodeKind.interaction, label="force"),
                GraphNode(id="space", kind=NodeKind.space, label="absolute space"),
                GraphNode(id="time", kind=NodeKind.time, label="absolute time"),
                GraphNode(id="traj", kind=NodeKind.process, label="trajectory"),
            ],
            [
                GraphEdge(source="force", target="traj", kind=EdgeKind.CAUSES),
                GraphEdge(source="mass", target="space", kind=EdgeKind.LOCATED_IN),
                GraphEdge(source="traj", target="time", kind=EdgeKind.DEPENDS_ON),
            ],
        ),
        _g(
            "template_fp_classical_em",
            [
                GraphNode(id="em", kind=NodeKind.field_medium, label="EM field"),
                GraphNode(id="charge", kind=NodeKind.entity, label="charge"),
                GraphNode(id="light", kind=NodeKind.observable, label="light/radiation"),
                GraphNode(id="sound", kind=NodeKind.observable, label="sound"),
                GraphNode(id="air", kind=NodeKind.substance, label="material medium"),
            ],
            [
                GraphEdge(source="charge", target="em", kind=EdgeKind.CAUSES),
                GraphEdge(source="light", target="em", kind=EdgeKind.PROPAGATES_THROUGH),
                GraphEdge(source="em", target="light", kind=EdgeKind.CARRIES),
                GraphEdge(source="sound", target="em", kind=EdgeKind.DISTINCT_FROM),
                GraphEdge(source="sound", target="air", kind=EdgeKind.PROPAGATES_THROUGH),
            ],
        ),
        _g(
            "template_fp_thermodynamics",
            [
                GraphNode(id="heat", kind=NodeKind.process, label="heat flow"),
                GraphNode(id="entropy", kind=NodeKind.property, label="entropy"),
                GraphNode(id="eq", kind=NodeKind.state, label="equilibrium"),
                GraphNode(id="macro", kind=NodeKind.entity, label="macrostate"),
            ],
            [
                GraphEdge(source="heat", target="entropy", kind=EdgeKind.CAUSES),
                GraphEdge(source="macro", target="eq", kind=EdgeKind.HAS_PROPERTY),
                GraphEdge(source="heat", target="macro", kind=EdgeKind.TRANSFORMS_INTO),
            ],
        ),
        _g(
            "template_fp_relativity",
            [
                GraphNode(id="spacetime", kind=NodeKind.space, label="spacetime"),
                GraphNode(id="light_c", kind=NodeKind.property, label="invariant c"),
                GraphNode(id="frame", kind=NodeKind.measurement, label="inertial frame"),
                GraphNode(id="matter", kind=NodeKind.entity, label="matter-energy"),
            ],
            [
                GraphEdge(source="matter", target="spacetime", kind=EdgeKind.LOCATED_IN),
                GraphEdge(source="spacetime", target="light_c", kind=EdgeKind.HAS_PROPERTY),
                GraphEdge(source="frame", target="light_c", kind=EdgeKind.DEPENDS_ON),
            ],
        ),
        _g(
            "template_fp_quantum_mechanics",
            [
                GraphNode(id="state", kind=NodeKind.state, label="quantum state"),
                GraphNode(id="obs", kind=NodeKind.measurement, label="observable/operator"),
                GraphNode(id="obs2", kind=NodeKind.measurement, label="incompatible observable"),
                GraphNode(id="super", kind=NodeKind.property, label="superposition"),
                GraphNode(id="born", kind=NodeKind.process, label="Born-rule measurement"),
                GraphNode(id="hbar", kind=NodeKind.property, label="Planck scale"),
            ],
            [
                GraphEdge(source="state", target="super", kind=EdgeKind.HAS_PROPERTY),
                GraphEdge(source="obs", target="state", kind=EdgeKind.INTERACTS_WITH),
                GraphEdge(source="born", target="obs", kind=EdgeKind.DEPENDS_ON),
                GraphEdge(source="state", target="hbar", kind=EdgeKind.DEPENDS_ON),
                GraphEdge(source="obs", target="obs2", kind=EdgeKind.DISTINCT_FROM),
            ],
        ),
        _g(
            "template_fp_quantum_field_theory",
            [
                GraphNode(id="qfield", kind=NodeKind.field_medium, label="quantum field"),
                GraphNode(id="excit", kind=NodeKind.particle_atom, label="field excitation/particle"),
                GraphNode(id="fock", kind=NodeKind.state, label="Fock space"),
                GraphNode(id="vac", kind=NodeKind.state, label="vacuum"),
                GraphNode(id="intx", kind=NodeKind.interaction, label="local interaction"),
            ],
            [
                GraphEdge(source="excit", target="qfield", kind=EdgeKind.COMPOSED_OF),
                GraphEdge(source="excit", target="fock", kind=EdgeKind.LOCATED_IN),
                GraphEdge(source="intx", target="qfield", kind=EdgeKind.CAUSES),
                GraphEdge(source="vac", target="qfield", kind=EdgeKind.HAS_PROPERTY),
                GraphEdge(source="excit", target="qfield", kind=EdgeKind.OBSERVABLE_AS),
            ],
        ),
        _g(
            "template_fp_atomistic_corpuscular",
            [
                GraphNode(id="atom", kind=NodeKind.particle_atom, label="atom/corpuscle"),
                GraphNode(id="void", kind=NodeKind.space, label="void/empty"),
                GraphNode(id="motion", kind=NodeKind.process, label="atomic motion"),
                GraphNode(id="compound", kind=NodeKind.entity, label="compound body"),
                GraphNode(id="disc", kind=NodeKind.property, label="discrete"),
            ],
            [
                GraphEdge(source="compound", target="atom", kind=EdgeKind.COMPOSED_OF),
                GraphEdge(source="atom", target="void", kind=EdgeKind.LOCATED_IN),
                GraphEdge(source="motion", target="atom", kind=EdgeKind.HAS_PROPERTY),
                GraphEdge(source="atom", target="disc", kind=EdgeKind.HAS_PROPERTY),
            ],
        ),
    ]

    index = {"version": "0.1.0-TEMPLATE", "graphs": [], "status": "TEMPLATE"}
    for g in graphs:
        fp = out_dir / f"{g.graph_id}.json"
        issues = g.validate_refs()
        if issues:
            raise ValueError(f"{g.graph_id}: {issues}")
        fp.write_text(g.model_dump_json(indent=2) + "\n", encoding="utf-8")
        paths.append(fp)
        index["graphs"].append(g.graph_id)

    idx_path = out_dir / "index.json"
    idx_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    paths.append(idx_path)
    return paths
