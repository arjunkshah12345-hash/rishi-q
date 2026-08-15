"""Discovery candidate ranking, novelty gates, and so-what dimensions."""

from __future__ import annotations

from typing import Any

from rishiq.discovery import DiscoveryCandidate, RishiMotif


def so_what_scores(
    *,
    novelty: float,
    robustness: float,
    specificity: float,
    historical_importance: float,
    physics_relevance: float,
    interpretability: float,
    reproducibility: float,
    surprise: float,
) -> dict[str, float]:
    dims = {
        "novelty": novelty,
        "robustness": robustness,
        "specificity": specificity,
        "historical_importance": historical_importance,
        "physics_relevance": physics_relevance,
        "interpretability": interpretability,
        "reproducibility": reproducibility,
        "surprise": surprise,
    }
    dims["composite_optional"] = sum(dims.values()) / len(dims)
    return dims


def novelty_gate(candidate: DiscoveryCandidate) -> DiscoveryCandidate:
    """Graduate to STRONG_DISCOVERY_CANDIDATE only if most criteria hold.

    Default path keeps NOVELTY_REVIEW_REQUIRED — never auto-claim STRONG
    without literature review + replication evidence.
    """
    checks = {
        "not_trivial_ontology": candidate.discovery_type != "single_feature",
        "not_single_passage": candidate.n_independent_works >= 2
        or len(candidate.supporting_sources) >= 3,
        "multi_work": candidate.n_independent_works >= 2,
        "translation_ok": candidate.translation_robustness
        in {"pass", "partial", "untested"},
        "model_ok": candidate.model_robustness in {"pass", "partial", "untested"},
        "has_effect": (candidate.effect_size or 0) > 1.2
        or candidate.effect_size is None,
        "precise": bool(candidate.title and candidate.motif_id),
        "literature_reviewed": candidate.prior_literature_status
        not in {"", "NOVELTY_REVIEW_REQUIRED"},
        "not_rejected": candidate.status != "REJECTED",
        "not_artifact": candidate.status != "ARTIFACT_SUSPECTED",
    }
    # Never auto-promote to STRONG without explicit literature clearance
    if candidate.prior_literature_status in {
        "APPARENTLY_NOVEL",
        "PARTIALLY_KNOWN",
    } and sum(checks.values()) >= 8:
        if candidate.translation_robustness == "pass" and candidate.model_robustness == "pass":
            candidate.status = "STRONG_DISCOVERY_CANDIDATE"
        else:
            candidate.status = "APPARENTLY_NOVEL"
    elif candidate.status == "RAW_CANDIDATE":
        candidate.status = "NOVELTY_REVIEW_REQUIRED"
    candidate.notes = (candidate.notes + " | gate:" + str(checks)).strip(" |")
    return candidate


def rank_motifs(
    motifs: list[RishiMotif],
    enrichments: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Multi-criteria rank — NOT p-value primary."""
    rows = []
    for m in motifs:
        enr = enrichments.get(m.motif_id, {})
        enrichment = enr.get("enrichment") or 0.0
        n_works = enr.get("n_works", len(m.works))
        specificity = 1.0 if m.physics_family in {"quantum_specific", "field_like"} else 0.4
        if m.physics_family == "unrelated":
            specificity = 0.2
        # composite without p
        score = (
            0.25 * min(enrichment / 5.0, 1.0)
            + 0.20 * min(n_works / 5.0, 1.0)
            + 0.15 * min(m.support / 20.0, 1.0)
            + 0.15 * specificity
            + 0.10 * (1.0 if m.physics_family == "field_like" else 0.5)
            + 0.15 * 0.5  # placeholder for translation/model until tested
        )
        rows.append(
            {
                "motif_id": m.motif_id,
                "rank_score": score,
                "enrichment": enrichment,
                "n_works": n_works,
                "support": m.support,
                "physics_family": m.physics_family,
                "nearest_physics": m.nearest_physics,
                "signature": m.signature,
                "criteria": {
                    "statistical_robustness": min(m.support / 10.0, 1.0),
                    "enrichment_magnitude": min((enrichment or 0) / 5.0, 1.0),
                    "cross_text_replication": min(n_works / 5.0, 1.0),
                    "conceptual_specificity": specificity,
                    "historical_interest": 0.5,
                    "literature_novelty": 0.0,  # filled after novelty review
                },
            }
        )
    rows.sort(key=lambda r: -r["rank_score"])
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


def motif_to_candidate(
    motif: RishiMotif,
    enrichment: dict[str, Any],
    rank_row: dict[str, Any] | None = None,
) -> DiscoveryCandidate:
    sw = so_what_scores(
        novelty=0.0,
        robustness=min(motif.support / 15.0, 1.0),
        specificity=rank_row["criteria"]["conceptual_specificity"] if rank_row else 0.3,
        historical_importance=0.4,
        physics_relevance=0.6
        if motif.physics_family in {"field_like", "quantum_specific"}
        else 0.3,
        interpretability=0.7 if len(motif.signature) <= 6 else 0.4,
        reproducibility=0.8,
        surprise=min((enrichment.get("enrichment") or 0) / 4.0, 1.0),
    )
    return DiscoveryCandidate(
        candidate_id=f"DC-{motif.motif_id}",
        title=f"Structural motif {motif.motif_id}: {' + '.join(motif.signature[:4])}",
        discovery_type="rishi_motif",
        motif_id=motif.motif_id,
        supporting_sources=list(motif.works.keys())[:20],
        n_independent_works=len(motif.works),
        effect_size=enrichment.get("enrichment"),
        confidence_interval=enrichment.get("ci95"),
        control_comparison=str(enrichment),
        nearest_physics_analogue=motif.nearest_physics or "",
        classical_vs_quantum_specificity=motif.physics_family,
        prior_literature_status="NOVELTY_REVIEW_REQUIRED",
        alternative_explanations=[
            "generic metaphysics",
            "translation modernization",
            "annotator lexical bias",
            "shared mystical tropes across civilizations",
        ],
        novelty_confidence=0.0,
        scientific_importance=sw["composite_optional"],
        status="RAW_CANDIDATE",
        so_what=sw,
    )
