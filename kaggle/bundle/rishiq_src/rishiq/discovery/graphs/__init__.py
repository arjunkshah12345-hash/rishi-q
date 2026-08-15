"""Evidence-bound concept graph extraction from ontology annotations.

Maps positive features → nodes/edges. Does not invent structure without evidence.
Physics theory labels are NOT used at extraction time.
"""

from __future__ import annotations

from rishiq.discovery import GraphEdge, GraphNode, PassageGraph
from rishiq.models import AnnotationLabel, FeatureAnnotation

# Feature → structural graph elements (physics-agnostic)
FEATURE_GRAPH_MAP: dict[str, dict] = {
    "O01": {"nodes": ["substrate"], "edges": []},
    "O02": {"nodes": ["whole", "constituent"], "edges": [("whole", "composed_of", "constituent")]},
    "O03": {"nodes": ["constituent"], "edges": []},
    "O04": {"nodes": ["substrate", "space"], "edges": [("substrate", "pervades", "space")]},
    "O05": {
        "nodes": ["substrate", "manifestation"],
        "edges": [("substrate", "manifests_as", "manifestation")],
    },
    "O06": {
        "nodes": ["whole", "property"],
        "edges": [("property", "emerges_from", "whole")],
    },
    "D01": {"nodes": ["state"], "edges": []},
    "D02": {
        "nodes": ["state"],
        "edges": [("state", "transforms_into", "state")],
    },
    "D03": {"nodes": ["motion"], "edges": []},
    "D04": {
        "nodes": ["disturbance", "space"],
        "edges": [("disturbance", "propagates_through", "space")],
    },
    "D05": {"nodes": ["property"], "edges": []},
    "R01": {
        "nodes": ["cause", "effect"],
        "edges": [("cause", "interacts_with", "effect")],
    },
    "R02": {
        "nodes": ["matter", "matter"],
        "edges": [("matter", "correlates_with", "matter")],
    },
    "R03": {
        "nodes": ["whole", "constituent"],
        "edges": [("whole", "cannot_be_reduced_to", "constituent")],
    },
    "R04": {"nodes": ["property"], "edges": [("property", "depends_on", "matter")]},
    "M01": {
        "nodes": ["observer", "matter"],
        "edges": [("observer", "observes", "matter")],
    },
    "M02": {
        "nodes": ["measurement", "state"],
        "edges": [("measurement", "changes", "state")],
    },
    "M03": {"nodes": ["observer", "property"], "edges": []},
    "M04": {"nodes": ["potential_state"], "edges": []},
    "F01": {"nodes": ["substrate", "space"], "edges": [("substrate", "pervades", "space")]},
    "F02": {"nodes": ["state", "space"], "edges": [("state", "is_state_of", "space")]},
    "F03": {
        "nodes": ["disturbance", "substrate"],
        "edges": [("disturbance", "propagates_through", "substrate")],
    },
    "F04": {
        "nodes": ["substrate", "manifestation"],
        "edges": [("substrate", "manifests_as", "manifestation")],
    },
    "F05": {
        "nodes": ["substrate", "matter"],
        "edges": [("substrate", "interacts_with", "matter")],
    },
    "F06": {
        "nodes": ["disturbance", "substrate"],
        "edges": [("disturbance", "is_state_of", "substrate")],
    },
    # Quantum-specific features still map to graph structure without naming "quantum"
    "Q01": {"nodes": ["state"], "edges": []},
    "Q02": {"nodes": ["potential_state", "state"], "edges": []},
    "Q03": {"nodes": ["state"], "edges": []},
    "Q04": {
        "nodes": ["measurement", "state"],
        "edges": [("measurement", "changes", "state")],
    },
    "Q05": {"nodes": ["property", "property"], "edges": []},
    "Q06": {
        "nodes": ["whole", "constituent"],
        "edges": [("whole", "cannot_be_reduced_to", "constituent")],
    },
    "Q07": {
        "nodes": ["measurement", "property"],
        "edges": [("property", "depends_on", "measurement")],
    },
    "Q08": {
        "nodes": ["manifestation", "substrate"],
        "edges": [("manifestation", "emerges_from", "substrate")],
    },
    "F07": {
        "nodes": ["manifestation", "substrate"],
        "edges": [("manifestation", "emerges_from", "substrate")],
    },
}


def extract_passage_graph(
    passage_id: str,
    annotations: list[FeatureAnnotation],
    ontology_version: str = "0.1.0",
) -> PassageGraph:
    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []
    edge_i = 0

    for ann in annotations:
        if ann.label != AnnotationLabel.YES:
            continue
        spec = FEATURE_GRAPH_MAP.get(ann.feature_id)
        if not spec:
            continue
        evidence = ann.evidence.strip()
        if not evidence:
            continue  # never add structure without evidence span
        local_ids = []
        for nt in spec["nodes"]:
            nid = f"{passage_id}:{nt}"
            local_ids.append(nid)
            if nid not in nodes:
                nodes[nid] = GraphNode(
                    node_id=nid,
                    node_type=nt,
                    label=nt,
                    evidence_span=evidence,
                    feature_ids=[ann.feature_id],
                )
            else:
                if ann.feature_id not in nodes[nid].feature_ids:
                    nodes[nid].feature_ids.append(ann.feature_id)
                if evidence and evidence not in nodes[nid].evidence_span:
                    nodes[nid].evidence_span = (
                        nodes[nid].evidence_span + " | " + evidence
                    )[:500]
        for src_t, etype, tgt_t in spec.get("edges", []):
            src = f"{passage_id}:{src_t}"
            tgt = f"{passage_id}:{tgt_t}"
            if src not in nodes or tgt not in nodes:
                continue
            eid = f"{passage_id}:E{edge_i}"
            edge_i += 1
            edges.append(
                GraphEdge(
                    edge_id=eid,
                    edge_type=etype,
                    source=src,
                    target=tgt,
                    evidence_span=evidence,
                    feature_ids=[ann.feature_id],
                    confidence=float(ann.confidence),
                )
            )

    return PassageGraph(
        passage_id=passage_id,
        nodes=list(nodes.values()),
        edges=edges,
        ontology_version=ontology_version,
        extractor="feature_map_v0.1",
        notes="Edges require positive labels with evidence spans.",
    )
