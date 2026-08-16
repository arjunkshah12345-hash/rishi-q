"""Canonical source-family taxonomy for theory-validation independence.

Splits must enforce no source_family overlap (and preferably no author_family
overlap) between development and any true final method holdout.
Volume/article-level work_ids are NOT independent families.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FamilyIds:
    work_id: str
    author_id: str
    author_family: str
    source_family: str
    publisher_family: str
    edition_family: str


# Map work_id → canonical families (explicit; do not invent volume-level families)
WORK_FAMILY: dict[str, FamilyIds] = {
    "newton_opticks": FamilyIds(
        "newton_opticks", "isaac_newton", "isaac_newton", "newton_opticks_editions", "archive_pd", "opticks_1718"
    ),
    "thomson_tait_np": FamilyIds(
        "thomson_tait_np", "thomson_tait", "thomson_tait", "treatise_natural_philosophy", "archive_pd", "np_1883"
    ),
    "carnot_motive_power": FamilyIds(
        "carnot_motive_power", "sadi_carnot", "sadi_carnot", "carnot_motive_power", "archive_pd", "carnot_tr"
    ),
    "clausius_mechanical_heat": FamilyIds(
        "clausius_mechanical_heat", "rudolf_clausius", "rudolf_clausius", "clausius_mechanical_heat", "archive_pd", "clausius_tr"
    ),
    "maxwell_theory_of_heat": FamilyIds(
        "maxwell_theory_of_heat", "james_clerk_maxwell", "james_clerk_maxwell", "maxwell_theory_of_heat", "archive_pd", "heat_1872"
    ),
    "maxwell_treatise_em_v1": FamilyIds(
        "maxwell_treatise_em_v1", "james_clerk_maxwell", "james_clerk_maxwell", "maxwell_treatise_em", "archive_pd", "treatise_v1"
    ),
    "maxwell_elementary_electricity": FamilyIds(
        "maxwell_elementary_electricity", "james_clerk_maxwell", "james_clerk_maxwell", "maxwell_elementary_electricity", "archive_pd", "elem_1881"
    ),
    "faraday_experimental_v1": FamilyIds(
        "faraday_experimental_v1", "michael_faraday", "michael_faraday", "faraday_experimental_researches", "gutenberg_pd", "exp_v1"
    ),
    "huygens_light": FamilyIds(
        "huygens_light", "christiaan_huygens", "christiaan_huygens", "huygens_treatise_on_light", "gutenberg_pd", "light_tr"
    ),
    "einstein_relativity_popular": FamilyIds(
        "einstein_relativity_popular", "albert_einstein", "albert_einstein", "einstein_relativity_popular", "archive_pd", "rel_1920"
    ),
    "lucretius_drn": FamilyIds(
        "lucretius_drn", "lucretius", "lucretius", "lucretius_de_rerum_natura", "gutenberg_pd", "leonard_tr"
    ),
    "dalton_chemical_philosophy": FamilyIds(
        "dalton_chemical_philosophy", "john_dalton", "john_dalton", "dalton_chemical_philosophy", "archive_pd", "new_system"
    ),
    "tesla_high_frequency": FamilyIds(
        "tesla_high_frequency", "nikola_tesla", "nikola_tesla", "tesla_high_frequency", "gutenberg_pd", "lecture"
    ),
    # OpenStax volumes share ONE source family
    "openstax_university-physics-volume-1": FamilyIds(
        "openstax_university-physics-volume-1",
        "openstax",
        "openstax",
        "openstax_university_physics",
        "openstax",
        "up_v1",
    ),
    "openstax_university-physics-volume-2": FamilyIds(
        "openstax_university-physics-volume-2",
        "openstax",
        "openstax",
        "openstax_university_physics",
        "openstax",
        "up_v2",
    ),
    "openstax_university-physics-volume-3": FamilyIds(
        "openstax_university-physics-volume-3",
        "openstax",
        "openstax",
        "openstax_university_physics",
        "openstax",
        "up_v3",
    ),
    # All Wikipedia physics pages share ONE source family
    "wikipedia_qft": FamilyIds("wikipedia_qft", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_qed": FamilyIds("wikipedia_qed", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_particle": FamilyIds("wikipedia_particle", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_qm": FamilyIds("wikipedia_qm", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_sr": FamilyIds("wikipedia_sr", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_gr": FamilyIds("wikipedia_gr", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_thermo": FamilyIds("wikipedia_thermo", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_cm": FamilyIds("wikipedia_cm", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_maxwell": FamilyIds("wikipedia_maxwell", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
    "wikipedia_atomism": FamilyIds("wikipedia_atomism", "wikipedia_contributors", "wikipedia_contributors", "wikipedia_physics", "wikimedia", "en_wp"),
}


def family_for_work(work_id: str) -> FamilyIds:
    if work_id in WORK_FAMILY:
        return WORK_FAMILY[work_id]
    # Fail closed: unknown works get unique but flagged families
    return FamilyIds(
        work_id=work_id,
        author_id=f"unknown_{work_id}",
        author_family=f"unknown_{work_id}",
        source_family=f"unknown_{work_id}",
        publisher_family="unknown",
        edition_family="unknown",
    )


def annotate_row(row: dict) -> dict:
    fam = family_for_work(row["work_id"])
    out = dict(row)
    out["author_id"] = fam.author_id
    out["author_family"] = fam.author_family
    out["source_family"] = fam.source_family
    out["publisher_family"] = fam.publisher_family
    out["edition_family"] = fam.edition_family
    return out


def assert_no_family_overlap(rows: list[dict], field: str = "source_family") -> list[str]:
    by_split: dict[str, set[str]] = {}
    for r in rows:
        by_split.setdefault(r["split"], set()).add(r[field])
    issues: list[str] = []
    pairs = [
        ("train", "development"),
        ("train", "final_holdout"),
        ("development", "final_holdout"),
        # demoted constructed set uses same key as final_holdout historically
        ("train", "constructed_unevaluated"),
        ("development", "constructed_unevaluated"),
    ]
    for a, b in pairs:
        if a not in by_split or b not in by_split:
            continue
        inter = by_split[a] & by_split[b]
        if not inter:
            continue
        involves_holdout = "final" in a or "final" in b or "constructed" in a or "constructed" in b
        if field == "source_family":
            # Any source_family overlap across splits is a hard failure for independence claims
            issues.append(f"HARD_source_family_overlap {a}∩{b}: {sorted(inter)}")
        elif field == "author_family" and involves_holdout:
            issues.append(f"HARD_author_family_overlap {a}∩{b}: {sorted(inter)}")
        elif field == "author_family":
            issues.append(f"WARN_author_family_overlap {a}∩{b}: {sorted(inter)}")
    return issues
