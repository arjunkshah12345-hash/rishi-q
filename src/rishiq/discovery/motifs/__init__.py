"""Rishi Motif discovery — unsupervised structural pattern mining.

Physics labels are applied ONLY after motifs are discovered.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

import numpy as np

from rishiq.discovery import PassageGraph, RishiMotif


def _sig_key(sig: frozenset[str]) -> str:
    return "|".join(sorted(sig))


def mine_motifs(
    graphs: list[PassageGraph],
    meta: dict[str, dict[str, str]] | None = None,
    min_support: int = 3,
    max_signature_size: int = 6,
) -> list[RishiMotif]:
    """Discover recurring structural signatures without physics priors.

    A motif signature is a frozenset of node-types and edge-types present
    in a passage graph. We also mine subsets of size 2..max for combinatorial
    patterns (frequent itemset style).
    """
    meta = meta or {}
    # Collect all atomic elements per passage
    passage_atoms: dict[str, frozenset[str]] = {}
    for g in graphs:
        if not g.nodes and not g.edges:
            continue
        passage_atoms[g.passage_id] = g.motif_signature()

    if not passage_atoms:
        return []

    # Count full signatures and frequent subsets
    support: Counter[frozenset[str]] = Counter()
    owners: dict[frozenset[str], list[str]] = defaultdict(list)

    for pid, atoms in passage_atoms.items():
        # full signature
        if len(atoms) >= 2:
            support[atoms] += 1
            owners[atoms].append(pid)
        # all subsets of size 2..min(max, len)
        items = sorted(atoms)
        for k in range(2, min(max_signature_size, len(items)) + 1):
            for combo in combinations(items, k):
                s = frozenset(combo)
                support[s] += 1
                if pid not in owners[s]:
                    owners[s].append(pid)

    motifs: list[RishiMotif] = []
    mid = 0
    for sig, n in support.most_common():
        if n < min_support:
            continue
        # Prefer non-redundant: skip if identical support to a larger supersignature already kept?
        mid += 1
        pids = owners[sig]
        traditions: Counter[str] = Counter()
        works: Counter[str] = Counter()
        for pid in pids:
            m = meta.get(pid, {})
            traditions[m.get("tradition", "unknown")] += 1
            works[m.get("work_id", m.get("source_id", "unknown"))] += 1
        motifs.append(
            RishiMotif(
                motif_id=f"M{mid:03d}",
                signature=sorted(sig),
                support=n,
                passages=pids[:50],
                traditions=dict(traditions),
                works=dict(works),
            )
        )
        if mid >= 200:  # cap for tractability
            break
    return motifs


def map_motifs_to_physics(
    motifs: list[RishiMotif],
    fingerprints: dict[str, set[str]],
) -> list[RishiMotif]:
    """AFTER discovery: compare motif feature atoms to theory fingerprints.

    Motif signatures use N:/E: tokens. We also accept O/D/R/M/F/Q feature ids
    if present in an extended signature. For structure-only motifs, map via
    edge/node families to coarse physics families.
    """
    field_nodes = {"substrate", "disturbance", "space"}
    field_edges = {"pervades", "propagates_through", "manifests_as"}
    quantum_edges = {"cannot_be_reduced_to"}  # weak proxy; Q-features stronger
    classical_nodes = {"matter", "motion", "cause", "effect"}

    for m in motifs:
        nodes = {s[2:] for s in m.signature if s.startswith("N:")}
        edges = {s[2:] for s in m.signature if s.startswith("E:")}
        feats = {s for s in m.signature if not s.startswith(("N:", "E:"))}

        # Prefer feature-overlap with fingerprints when features available
        best_name = "unrelated"
        best_j = 0.0
        if feats and fingerprints:
            for name, fp in fingerprints.items():
                inter = len(feats & fp)
                union = len(feats | fp) or 1
                j = inter / union
                if j > best_j:
                    best_j = j
                    best_name = name

        if best_j >= 0.25:
            m.nearest_physics = best_name
            qish = bool(feats & {"Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "Q07", "Q08"})
            fieldish = bool(feats & {"F01", "F02", "F03", "F04", "F05", "F06", "F07"})
            if qish and best_name in {"quantum_mechanics", "quantum_field_theory"}:
                m.physics_family = "quantum_specific"
            elif fieldish or best_name in {"classical_electromagnetism", "classical_field"}:
                m.physics_family = "field_like"
            elif best_name in {"newtonian_mechanics", "thermodynamics"}:
                m.physics_family = "classical"
            else:
                m.physics_family = "classical" if not qish else "quantum_specific"
        else:
            # structure-only heuristic
            if nodes & field_nodes and edges & field_edges:
                m.nearest_physics = "classical_field_like"
                m.physics_family = "field_like"
            elif edges & quantum_edges and "whole" in nodes:
                m.nearest_physics = "possible_nonseparability_structure"
                m.physics_family = "unknown"
            elif nodes & classical_nodes:
                m.nearest_physics = "classical_mechanics_like"
                m.physics_family = "classical"
            else:
                m.nearest_physics = "unrelated_or_generic"
                m.physics_family = "unrelated"
    return motifs


def motif_enrichment(
    motif: RishiMotif,
    target_traditions: set[str],
    control_traditions: set[str],
    n_target: int,
    n_control: int,
) -> dict[str, Any]:
    """Enrichment(M,T) = P(M|T) / P(M|Controls) with Wilson-ish crude CI."""
    n_m_t = sum(v for k, v in motif.traditions.items() if k in target_traditions)
    n_m_c = sum(v for k, v in motif.traditions.items() if k in control_traditions)
    p_t = n_m_t / max(n_target, 1)
    p_c = n_m_c / max(n_control, 1)
    if n_m_t == 0 and n_m_c == 0:
        enrichment = 1.0
        ci = None
    elif p_c == 0:
        enrichment = float("inf") if p_t > 0 else 1.0
        ci = None
    else:
        enrichment = p_t / p_c
        se = np.sqrt(
            (1 / max(n_m_t, 1) - 1 / max(n_target, 1))
            + (1 / max(n_m_c, 1) - 1 / max(n_control, 1))
        )
        log_e = np.log(enrichment) if enrichment > 0 else 0.0
        ci = [float(np.exp(log_e - 1.96 * se)), float(np.exp(log_e + 1.96 * se))]
    return {
        "motif_id": motif.motif_id,
        "n_target": n_m_t,
        "n_control": n_m_c,
        "p_target": p_t,
        "p_control": p_c,
        "enrichment": float(enrichment) if enrichment != float("inf") else None,
        "enrichment_infinite": enrichment == float("inf"),
        "ci95": ci,
        "n_works": len(motif.works),
    }
