"""Cross-civilization motif atlas."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from rishiq.discovery import RishiMotif


def build_motif_atlas(
    motifs: list[RishiMotif],
    tradition_roles: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Produce atlas of common / unique / shared / enriched motifs by tradition."""
    tradition_roles = tradition_roles or {}
    by_tradition: dict[str, list[str]] = defaultdict(list)
    for m in motifs:
        for t, n in m.traditions.items():
            if n > 0:
                by_tradition[t].append(m.motif_id)

    traditions = sorted(by_tradition)
    sets = {t: set(by_tradition[t]) for t in traditions}

    unique = {
        t: sorted(sets[t] - set().union(*(sets[o] for o in traditions if o != t)))
        for t in traditions
    }
    # shared by >=2 traditions
    shared: list[str] = []
    for m in motifs:
        present = [t for t, n in m.traditions.items() if n > 0]
        if len(present) >= 2:
            shared.append(m.motif_id)

    field_like = [m.motif_id for m in motifs if m.physics_family == "field_like"]
    atomistic = [
        m.motif_id
        for m in motifs
        if "N:constituent" in m.signature or "N:matter" in m.signature
    ]
    relational = [
        m.motif_id
        for m in motifs
        if any(x.startswith("E:") for x in m.signature)
    ]
    observer = [m.motif_id for m in motifs if "N:observer" in m.signature]
    quantumish = [
        m.motif_id for m in motifs if m.physics_family == "quantum_specific"
    ]

    return {
        "traditions": traditions,
        "counts_by_tradition": {t: len(v) for t, v in by_tradition.items()},
        "unique_motifs": unique,
        "shared_across_traditions": sorted(set(shared)),
        "field_like_motifs": field_like,
        "atomistic_motifs": atomistic,
        "relational_motifs": relational,
        "observer_related_motifs": observer,
        "quantum_specific_motifs": quantumish,
        "note": "Physics families assigned AFTER unsupervised motif discovery.",
    }
