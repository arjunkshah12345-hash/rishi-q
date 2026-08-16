"""Typed concept-graph schema and utilities.

Ontology content for physics fingerprints must be student-verified.
This module provides structure only — not authoritative physics claims.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class NodeKind(str, Enum):
    entity = "entity"
    substance = "substance"
    field_medium = "field_medium"
    particle_atom = "particle_atom"
    property = "property"
    process = "process"
    interaction = "interaction"
    cause = "cause"
    observable = "observable"
    space = "space"
    time = "time"
    measurement = "measurement"
    state = "state"
    transformation = "transformation"


class EdgeKind(str, Enum):
    HAS_PROPERTY = "HAS_PROPERTY"
    COMPOSED_OF = "COMPOSED_OF"
    LOCATED_IN = "LOCATED_IN"
    PROPAGATES_THROUGH = "PROPAGATES_THROUGH"
    CAUSES = "CAUSES"
    INTERACTS_WITH = "INTERACTS_WITH"
    TRANSFORMS_INTO = "TRANSFORMS_INTO"
    DEPENDS_ON = "DEPENDS_ON"
    DISTINCT_FROM = "DISTINCT_FROM"
    PERVADES = "PERVADES"
    CARRIES = "CARRIES"
    OBSERVABLE_AS = "OBSERVABLE_AS"
    DISCRETE = "DISCRETE"
    CONTINUOUS = "CONTINUOUS"
    LOCAL = "LOCAL"
    NONLOCAL = "NONLOCAL"


class GraphNode(BaseModel):
    id: str
    kind: NodeKind
    label: str
    notes: str = ""
    provenance: str = "STUDENT_OR_TEMPLATE"  # never silently claim expert authority


class GraphEdge(BaseModel):
    source: str
    target: str
    kind: EdgeKind
    weight: float = 1.0
    notes: str = ""


class ConceptGraph(BaseModel):
    graph_id: str
    version: str = "0.1.0"
    domain: str  # theory_fingerprint | historical_text
    status: str = "TEMPLATE"  # TEMPLATE | STUDENT_DRAFT | FROZEN
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    def node_ids(self) -> set[str]:
        return {n.id for n in self.nodes}

    def validate_refs(self) -> list[str]:
        ids = self.node_ids()
        issues = []
        for e in self.edges:
            if e.source not in ids:
                issues.append(f"missing_source:{e.source}")
            if e.target not in ids:
                issues.append(f"missing_target:{e.target}")
        return issues


def edge_set(g: ConceptGraph) -> set[tuple[str, str, str]]:
    return {(e.source, e.target, e.kind.value) for e in g.edges}


def weighted_edge_jaccard(a: ConceptGraph, b: ConceptGraph) -> float:
    """Relation-aware Jaccard on typed edges (unweighted set form)."""
    sa, sb = edge_set(a), edge_set(b)
    if not sa and not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def node_kind_jaccard(a: ConceptGraph, b: ConceptGraph) -> float:
    ka = {(n.kind.value, n.label.lower()) for n in a.nodes}
    kb = {(n.kind.value, n.label.lower()) for n in b.nodes}
    if not ka and not kb:
        return 0.0
    return len(ka & kb) / len(ka | kb)


def graph_overlap_score(a: ConceptGraph, b: ConceptGraph, *, edge_w: float = 0.7) -> float:
    e = weighted_edge_jaccard(a, b)
    n = node_kind_jaccard(a, b)
    return edge_w * e + (1 - edge_w) * n


def write_schema_and_templates(root: Path) -> list[Path]:
    out_dir = root / "ontology/concept_graph"
    out_dir.mkdir(parents=True, exist_ok=True)
    schema = {
        "node_kinds": [k.value for k in NodeKind],
        "edge_kinds": [k.value for k in EdgeKind],
        "status_values": ["TEMPLATE", "STUDENT_DRAFT", "FROZEN"],
        "warning": (
            "Do not design fingerprints after seeing which features raise Sanskrit–QM scores. "
            "Student must verify scientific content."
        ),
    }
    paths = []
    p = out_dir / "schema.json"
    p.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    paths.append(p)

    # TEMPLATE graphs — illustrative structure only
    akasa_template = ConceptGraph(
        graph_id="template_vaisesika_akasa_sabda",
        domain="historical_text",
        status="TEMPLATE",
        meta={"warning": "TEMPLATE — student must verify against primary texts"},
        nodes=[
            GraphNode(id="akasa", kind=NodeKind.field_medium, label="akasa"),
            GraphNode(id="sabda", kind=NodeKind.observable, label="sabda/sound"),
            GraphNode(id="tejas", kind=NodeKind.substance, label="tejas"),
            GraphNode(id="heat", kind=NodeKind.property, label="heat"),
            GraphNode(id="pervasion", kind=NodeKind.property, label="all-pervasive"),
        ],
        edges=[
            GraphEdge(source="sabda", target="akasa", kind=EdgeKind.OBSERVABLE_AS),
            GraphEdge(source="akasa", target="pervasion", kind=EdgeKind.HAS_PROPERTY),
            GraphEdge(source="tejas", target="akasa", kind=EdgeKind.DISTINCT_FROM),
            GraphEdge(source="tejas", target="heat", kind=EdgeKind.HAS_PROPERTY),
            GraphEdge(source="sabda", target="akasa", kind=EdgeKind.PROPAGATES_THROUGH),
        ],
    )
    maxwell_template = ConceptGraph(
        graph_id="template_maxwell_em",
        domain="theory_fingerprint",
        status="TEMPLATE",
        meta={"warning": "TEMPLATE — student must verify against EM textbooks"},
        nodes=[
            GraphNode(id="em_field", kind=NodeKind.field_medium, label="EM field"),
            GraphNode(id="light", kind=NodeKind.observable, label="light/radiation"),
            GraphNode(id="charge", kind=NodeKind.entity, label="charge"),
            GraphNode(id="sound", kind=NodeKind.observable, label="sound"),
            GraphNode(id="air", kind=NodeKind.substance, label="material medium/air"),
        ],
        edges=[
            GraphEdge(source="light", target="em_field", kind=EdgeKind.PROPAGATES_THROUGH),
            GraphEdge(source="charge", target="em_field", kind=EdgeKind.CAUSES),
            GraphEdge(source="sound", target="em_field", kind=EdgeKind.DISTINCT_FROM),
            GraphEdge(source="sound", target="air", kind=EdgeKind.PROPAGATES_THROUGH),
            GraphEdge(source="em_field", target="light", kind=EdgeKind.CARRIES),
        ],
    )
    for g in (akasa_template, maxwell_template):
        fp = out_dir / f"{g.graph_id}.json"
        fp.write_text(g.model_dump_json(indent=2) + "\n", encoding="utf-8")
        paths.append(fp)

    (out_dir / "STUDENT_TODO.md").write_text(
        "# Student TODO — concept graphs\n\n"
        "1. Review `schema.json` node/edge kinds; add/remove only before freeze.\n"
        "2. Replace TEMPLATE graphs with verified drafts for each theory fingerprint.\n"
        "3. Do **not** tune graphs to maximize Sanskrit–QM similarity.\n"
        "4. Mark status `FROZEN` only after independent review.\n",
        encoding="utf-8",
    )
    paths.append(out_dir / "STUDENT_TODO.md")
    return paths
