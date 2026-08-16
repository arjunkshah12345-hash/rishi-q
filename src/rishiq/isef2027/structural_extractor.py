"""Theory-agnostic structural extractor (deterministic, auditable).

Receives ONLY passage text. Does NOT receive theory labels or fingerprints.

Pipeline:
  Layer 1 — sentence split
  Layer 2 — entity/type mapping via fixed ontology lexicon (surface → role/kind)
  Layer 3 — explicit relation pattern extraction
  Layer 4 — optional LLM extraction is NOT used here (sensitivity analysis only elsewhere)

This is claim-bearing for structural validation. Lexical fingerprint-label matching
remains available as LEXICAL_GRAPH_PROXY_BASELINE only.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from rishiq.isef2027.concept_graph import ConceptGraph, EdgeKind, GraphEdge, GraphNode, NodeKind

EXTRACTOR_VERSION = "structural_extractor_deterministic_v1"

# Surface lexicon → (canonical_role, NodeKind). Theory-agnostic roles.
ENTITY_LEXICON: list[tuple[re.Pattern[str], str, NodeKind]] = [
    (re.compile(r"\b(particle|corpuscle|atom|molecule|electron|proton|neutron|photon|quark)\b", re.I), "particle", NodeKind.particle_atom),
    (re.compile(r"\b(field|medium|ether|æther|aether|vacuum|space)\b", re.I), "medium_or_field", NodeKind.field_medium),
    (re.compile(r"\b(force|interaction|collision|attraction|repulsion)\b", re.I), "interaction", NodeKind.interaction),
    (re.compile(r"\b(energy|momentum|charge|mass|entropy|temperature|pressure|potential|spin)\b", re.I), "property", NodeKind.property),
    (re.compile(r"\b(wave|radiation|light|sound|heat|current|flux)\b", re.I), "observable", NodeKind.observable),
    (re.compile(r"\b(state|equilibrium|ground state|excited state)\b", re.I), "state", NodeKind.state),
    (re.compile(r"\b(measurement|observer|apparatus|detector)\b", re.I), "measurement", NodeKind.measurement),
    (re.compile(r"\b(time|duration|simultaneity)\b", re.I), "time", NodeKind.time),
    (re.compile(r"\b(body|bodies|object|system|substance)\b", re.I), "entity", NodeKind.entity),
    (re.compile(r"\b(process|evolution|propagation|transformation|decay|emission|absorption)\b", re.I), "process", NodeKind.process),
]

# Explicit relation patterns: (regex with groups source, target), EdgeKind
RELATION_PATTERNS: list[tuple[re.Pattern[str], EdgeKind, float]] = [
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+causes?\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.CAUSES, 0.85),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+produces?\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.CAUSES, 0.8),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+(?:consists|composed)\s+of\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.COMPOSED_OF, 0.85),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+propagates?\s+through\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.PROPAGATES_THROUGH, 0.9),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+interacts?\s+with\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.INTERACTS_WITH, 0.85),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+depends?\s+on\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.DEPENDS_ON, 0.8),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+has\s+(?:the\s+)?propert(?:y|ies)\s+(?:of\s+)?(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.HAS_PROPERTY, 0.8),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+transforms?\s+into\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.TRANSFORMS_INTO, 0.85),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+is\s+distinct\s+from\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.DISTINCT_FROM, 0.85),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+measures?\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.OBSERVABLE_AS, 0.75),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+(?:is\s+)?located\s+in\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.LOCATED_IN, 0.75),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+carries?\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.CARRIES, 0.75),
    (re.compile(r"(?P<a>[A-Za-z][\w\-]*)\s+pervades?\s+(?P<b>[A-Za-z][\w\-]*)", re.I), EdgeKind.PERVADES, 0.8),
]


@dataclass
class ExtractedNode:
    id: str
    kind: str
    surface: str
    canonical_role: str
    confidence: float = 0.7


@dataclass
class ExtractedEdge:
    source: str
    relation: str
    target: str
    confidence: float
    evidence_span: str = ""


@dataclass
class ExtractionResult:
    nodes: list[ExtractedNode] = field(default_factory=list)
    edges: list[ExtractedEdge] = field(default_factory=list)
    extractor_version: str = EXTRACTOR_VERSION
    method: str = "deterministic_lexicon_patterns"
    notes: str = "Theory-agnostic; no theory label or fingerprint provided to extractor."

    def to_dict(self) -> dict[str, Any]:
        return {
            "extractor_version": self.extractor_version,
            "method": self.method,
            "notes": self.notes,
            "nodes": [asdict(n) for n in self.nodes],
            "edges": [asdict(e) for e in self.edges],
        }

    def to_concept_graph(self, graph_id: str = "extracted") -> ConceptGraph:
        nodes = [
            GraphNode(
                id=n.id,
                kind=NodeKind(n.kind) if n.kind in NodeKind.__members__.values() or n.kind in [k.value for k in NodeKind] else NodeKind.entity,
                label=n.surface,
                notes=n.canonical_role,
                provenance="STRUCTURAL_EXTRACTOR_V1",
            )
            for n in self.nodes
        ]
        # Fix kind assignment more carefully
        fixed_nodes = []
        for n in self.nodes:
            try:
                kind = NodeKind(n.kind)
            except ValueError:
                kind = NodeKind.entity
            fixed_nodes.append(
                GraphNode(
                    id=n.id,
                    kind=kind,
                    label=n.surface,
                    notes=n.canonical_role,
                    provenance="STRUCTURAL_EXTRACTOR_V1",
                )
            )
        id_set = {n.id for n in fixed_nodes}
        edges = []
        for e in self.edges:
            if e.source not in id_set or e.target not in id_set:
                continue
            try:
                ek = EdgeKind(e.relation)
            except ValueError:
                ek = EdgeKind.DEPENDS_ON
            edges.append(GraphEdge(source=e.source, target=e.target, kind=ek, weight=e.confidence, notes=e.evidence_span[:120]))
        return ConceptGraph(
            graph_id=graph_id,
            domain="historical_text",
            status="EXTRACTED",
            nodes=fixed_nodes,
            edges=edges,
            meta={"extractor_version": self.extractor_version},
        )


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 5]


def _node_id(surface: str, role: str) -> str:
    key = f"{role}:{surface.lower()}"
    return "n_" + hashlib.sha1(key.encode()).hexdigest()[:10]


def extract_structure(text: str) -> ExtractionResult:
    """Extract entities and explicit relations from passage text only."""
    if not text or not text.strip():
        return ExtractionResult()

    node_map: dict[str, ExtractedNode] = {}
    edges: list[ExtractedEdge] = []

    for sent in _sentences(text):
        # Layer 2: entities
        for pat, role, kind in ENTITY_LEXICON:
            for m in pat.finditer(sent):
                surface = m.group(0)
                nid = _node_id(surface, role)
                if nid not in node_map:
                    node_map[nid] = ExtractedNode(
                        id=nid,
                        kind=kind.value,
                        surface=surface.lower(),
                        canonical_role=role,
                        confidence=0.7,
                    )

        # Layer 3: relations
        for pat, ekind, conf in RELATION_PATTERNS:
            for m in pat.finditer(sent):
                a = m.group("a")
                b = m.group("b")
                # Map endpoints to roles if known, else entity
                def ensure(surface: str) -> str:
                    s = surface.lower()
                    for p2, role, kind in ENTITY_LEXICON:
                        if p2.search(s):
                            nid = _node_id(s, role)
                            if nid not in node_map:
                                node_map[nid] = ExtractedNode(
                                    id=nid, kind=kind.value, surface=s, canonical_role=role, confidence=0.65
                                )
                            return nid
                    nid = _node_id(s, "entity")
                    if nid not in node_map:
                        node_map[nid] = ExtractedNode(
                            id=nid, kind=NodeKind.entity.value, surface=s, canonical_role="entity", confidence=0.55
                        )
                    return nid

                sa, sb = ensure(a), ensure(b)
                if sa != sb:
                    edges.append(
                        ExtractedEdge(
                            source=sa,
                            relation=ekind.value,
                            target=sb,
                            confidence=conf,
                            evidence_span=sent[:200],
                        )
                    )

    return ExtractionResult(nodes=list(node_map.values()), edges=edges)


def lexical_graph_proxy_baseline(text: str, fingerprint_graphs: dict[str, ConceptGraph]) -> ConceptGraph:
    """DEPRECATED for claims — LEXICAL_GRAPH_PROXY_BASELINE only.

    Matches fingerprint node labels as substrings and fabricates DEPENDS_ON chains.
    """
    tl = text.lower()
    seen: dict[str, GraphNode] = {}
    for g in fingerprint_graphs.values():
        for n in g.nodes:
            lab = n.label.lower()
            if len(lab) >= 4 and lab in tl:
                seen[n.id] = n
    nodes = list(seen.values())[:20]
    edges = []
    ids = [n.id for n in nodes]
    for i in range(len(ids) - 1):
        edges.append(GraphEdge(source=ids[i], target=ids[i + 1], kind=EdgeKind.DEPENDS_ON))
    return ConceptGraph(
        graph_id="lexical_proxy",
        domain="historical_text",
        status="LEXICAL_GRAPH_PROXY_BASELINE",
        nodes=nodes,
        edges=edges,
        meta={"warning": "Not claim-bearing structural extraction"},
    )
