"""Source eligibility rules — fixed BEFORE performance evaluation (anti-cherry-picking)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


ALLOWED_LICENSES = {
    "public_domain",
    "CC0",
    "CC BY",
    "CC BY 4.0",
    "CC BY-SA",
    "CC BY-SA 4.0",
    "Project Gutenberg License",
}


@dataclass
class EligibilityRuleSet:
    version: str = "theory_val_v2_eligibility_v1"
    frozen_before_performance_eval: bool = True
    require_independent_author: bool = True
    require_known_theory_from_source_context: bool = True
    require_legal_reproducible_access: bool = True
    require_substantive: bool = True
    min_words: int = 40
    max_words: int = 400
    ban_used_in_fingerprint_construction: bool = True
    ban_used_in_ancient_text_analysis: bool = True
    ban_ai_generated: bool = True
    ban_selected_for_classifier_performance: bool = True
    allow_ai_paraphrase_as_external: bool = False
    notes: str = (
        "Eligibility decided before scoring. Do not drop difficult sources for accuracy."
    )


@dataclass
class SourceRecord:
    source_id: str
    source_title: str
    source_author: str
    source_year: int | str
    source_url_or_identifier: str
    license: str
    source_type: str  # public_domain_book | open_textbook | gov_edu | university_notes | wikipedia_cc
    theory_label: str
    author_family: str
    work_id: str
    eligible: bool = True
    eligibility_status: str = "ELIGIBLE"
    exclusion_reason: str = ""
    used_in_fingerprint_construction: bool = False
    used_in_ancient_text_analysis: bool = False
    ai_generated: bool = False
    selected_for_classifier_performance: bool = False
    unverified_metadata: bool = False
    notes: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def evaluate(self, rules: EligibilityRuleSet) -> "SourceRecord":
        if self.unverified_metadata:
            self.eligible = False
            self.eligibility_status = "UNVERIFIED_NOT_ELIGIBLE_FOR_FINAL_VALIDATION"
            self.exclusion_reason = "unverified_bibliographic_metadata"
            return self
        if self.ai_generated and rules.ban_ai_generated:
            self.eligible = False
            self.eligibility_status = "EXCLUDED"
            self.exclusion_reason = "ai_generated"
            return self
        if self.selected_for_classifier_performance and rules.ban_selected_for_classifier_performance:
            self.eligible = False
            self.eligibility_status = "EXCLUDED"
            self.exclusion_reason = "selected_for_classifier_performance"
            return self
        if self.used_in_fingerprint_construction and rules.ban_used_in_fingerprint_construction:
            self.eligible = False
            self.eligibility_status = "EXCLUDED"
            self.exclusion_reason = "used_in_fingerprint_construction"
            return self
        if self.used_in_ancient_text_analysis and rules.ban_used_in_ancient_text_analysis:
            self.eligible = False
            self.eligibility_status = "EXCLUDED"
            self.exclusion_reason = "used_in_ancient_text_analysis"
            return self
        lic = self.license.strip()
        ok_lic = lic in ALLOWED_LICENSES or lic.startswith("CC BY") or "public domain" in lic.lower() or "Gutenberg" in lic
        if not ok_lic:
            self.eligible = False
            self.eligibility_status = "EXCLUDED"
            self.exclusion_reason = f"license_not_allowed:{lic}"
            return self
        self.eligible = True
        self.eligibility_status = "ELIGIBLE"
        self.exclusion_reason = ""
        return self


# Prespecified catalog — theory labels from bibliographic context, NOT classifier scores.
PRESPECIFIED_SOURCES: list[dict[str, Any]] = [
    {
        "source_id": "newton_opticks_1718",
        "source_title": "Opticks",
        "source_author": "Isaac Newton",
        "source_year": 1718,
        "source_url_or_identifier": "archive.org/opticksortreatis1718newt",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "newtonian",
        "author_family": "newton",
        "work_id": "newton_opticks",
        "raw_file": "newton_opticks.txt",
    },
    {
        "source_id": "thomson_tait_natural_philosophy",
        "source_title": "Treatise on Natural Philosophy",
        "source_author": "William Thomson; P. G. Tait",
        "source_year": 1883,
        "source_url_or_identifier": "archive.org/b21987312",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "newtonian",
        "author_family": "thomson_tait",
        "work_id": "thomson_tait_np",
        "raw_file": "thomson_tait_natural_philosophy.txt",
    },
    {
        "source_id": "carnot_motive_power",
        "source_title": "Reflections on the Motive Power of Heat",
        "source_author": "Sadi Carnot",
        "source_year": 1890,
        "source_url_or_identifier": "archive.org/reflectionsonmot00carnrich",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "thermodynamics",
        "author_family": "carnot",
        "work_id": "carnot_motive_power",
        "raw_file": "carnot_motive_power.txt",
    },
    {
        "source_id": "clausius_mechanical_heat",
        "source_title": "The Mechanical Theory of Heat",
        "source_author": "Rudolf Clausius",
        "source_year": 1879,
        "source_url_or_identifier": "archive.org/cu31924101120883",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "thermodynamics",
        "author_family": "clausius",
        "work_id": "clausius_mechanical_heat",
        "raw_file": "clausius_mechanical_heat.txt",
    },
    {
        "source_id": "maxwell_theory_of_heat",
        "source_title": "Theory of Heat",
        "source_author": "James Clerk Maxwell",
        "source_year": 1872,
        "source_url_or_identifier": "archive.org/101591904.nlm.nih.gov",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "thermodynamics",
        "author_family": "maxwell",
        "work_id": "maxwell_theory_of_heat",
        "raw_file": "maxwell_theory_of_heat.txt",
    },
    {
        "source_id": "maxwell_em_treatise_v1",
        "source_title": "A Treatise on Electricity and Magnetism, Vol. I",
        "source_author": "James Clerk Maxwell",
        "source_year": 1873,
        "source_url_or_identifier": "archive.org/atreatiseonelec01thomgoog",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "classical_em",
        "author_family": "maxwell",
        "work_id": "maxwell_treatise_em_v1",
        "raw_file": "maxwell_em_vol1.txt",
    },
    {
        "source_id": "maxwell_elementary_electricity",
        "source_title": "An Elementary Treatise on Electricity",
        "source_author": "James Clerk Maxwell",
        "source_year": 1881,
        "source_url_or_identifier": "archive.org/elementarytreati00maxwrich",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "classical_em",
        "author_family": "maxwell",
        "work_id": "maxwell_elementary_electricity",
        "raw_file": "maxwell_elementary_electricity.txt",
    },
    {
        "source_id": "faraday_experimental_electricity",
        "source_title": "Experimental Researches in Electricity, Volume 1",
        "source_author": "Michael Faraday",
        "source_year": 1839,
        "source_url_or_identifier": "archive.org/experimentalrese14986gut",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "classical_em",
        "author_family": "faraday",
        "work_id": "faraday_experimental_v1",
        "raw_file": "faraday_electricity.txt",
    },
    {
        "source_id": "huygens_treatise_on_light",
        "source_title": "Treatise on Light",
        "source_author": "Christiaan Huygens",
        "source_year": 1690,
        "source_url_or_identifier": "gutenberg.org/ebooks/14725",
        "license": "Project Gutenberg License",
        "source_type": "public_domain_book",
        "theory_label": "classical_em",
        "author_family": "huygens",
        "work_id": "huygens_light",
        "raw_file": "huygens_treatise_on_light.txt",
        "notes": "Wave theory of light; classical EM/optics precursor — labeled classical_em for validation taxonomy.",
    },
    {
        "source_id": "einstein_relativity_popular",
        "source_title": "Relativity: The Special and General Theory",
        "source_author": "Albert Einstein",
        "source_year": 1920,
        "source_url_or_identifier": "archive.org/relativityspeci02einsgoog",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "relativity",
        "author_family": "einstein",
        "work_id": "einstein_relativity_popular",
        "raw_file": "einstein_relativity.txt",
    },
    {
        "source_id": "lucretius_de_rerum_natura",
        "source_title": "Of the Nature of Things",
        "source_author": "Titus Lucretius Carus (tr. Leonard)",
        "source_year": 1921,
        "source_url_or_identifier": "gutenberg.org/ebooks/785",
        "license": "Project Gutenberg License",
        "source_type": "public_domain_book",
        "theory_label": "atomistic_corpuscular",
        "author_family": "lucretius",
        "work_id": "lucretius_drn",
        "raw_file": "lucretius_drn.txt",
    },
    {
        "source_id": "dalton_chemical_philosophy",
        "source_title": "A New System of Chemical Philosophy",
        "source_author": "John Dalton",
        "source_year": 1808,
        "source_url_or_identifier": "archive.org/newsystemofchemi21dalt",
        "license": "public_domain",
        "source_type": "public_domain_book",
        "theory_label": "atomistic_corpuscular",
        "theory_label_primary": "atomistic_corpuscular",
        "author_family": "dalton",
        "work_id": "dalton_chemical_philosophy",
        "raw_file": "dalton_chemical_philosophy.txt",
    },
    {
        "source_id": "tesla_high_frequency",
        "source_title": "Experiments with Alternate Currents of High Potential and High Frequency",
        "source_author": "Nikola Tesla",
        "source_year": 1892,
        "source_url_or_identifier": "gutenberg.org/ebooks/13476",
        "license": "Project Gutenberg License",
        "source_type": "public_domain_book",
        "theory_label": "classical_em",
        "author_family": "tesla",
        "work_id": "tesla_high_frequency",
        "raw_file": "tesla_high_frequency.txt",
    },
]


def write_eligibility_manifest(root: Path) -> Path:
    rules = EligibilityRuleSet()
    raw_dir = root / "data/theory_validation_v2/raw"
    out_dir = root / "data/theory_validation_v2/eligibility"
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = []
    exclusions = []
    for spec in PRESPECIFIED_SOURCES:
        raw = spec.get("raw_file")
        path = raw_dir / raw if raw else None
        rec = SourceRecord(
            source_id=spec["source_id"],
            source_title=spec["source_title"],
            source_author=spec["source_author"],
            source_year=spec["source_year"],
            source_url_or_identifier=spec["source_url_or_identifier"],
            license=spec["license"],
            source_type=spec["source_type"],
            theory_label=spec["theory_label"],
            author_family=spec["author_family"],
            work_id=spec["work_id"],
            notes=spec.get("notes", ""),
            unverified_metadata=False,
            extra={"raw_file": raw},
        )
        if path is None or not path.exists() or path.stat().st_size < 1000:
            rec.eligible = False
            rec.eligibility_status = "EXCLUDED"
            rec.exclusion_reason = "raw_file_missing_or_too_small"
        else:
            rec.evaluate(rules)
        d = asdict(rec)
        sources.append(d)
        if not rec.eligible:
            exclusions.append({"source_id": rec.source_id, "reason": rec.exclusion_reason})

    # OpenStax entries (added if chapter jsonl present)
    for vol, theory_default, fname in [
        ("university-physics-volume-1", "newtonian", "openstax_up_v1_chapters.jsonl"),
        ("university-physics-volume-2", "classical_em", "openstax_up_v2_chapters.jsonl"),
        ("university-physics-volume-3", "quantum_mechanics", "openstax_up_v3_chapters.jsonl"),
    ]:
        path = raw_dir / fname
        rec = SourceRecord(
            source_id=f"openstax_{vol}",
            source_title=f"OpenStax University Physics ({vol})",
            source_author="OpenStax / Rice University contributors",
            source_year=2022,
            source_url_or_identifier=f"https://openstax.org/details/books/{vol}",
            license="CC BY 4.0",
            source_type="open_textbook",
            theory_label=theory_default,
            author_family="openstax",
            work_id=f"openstax_{vol}",
            notes="Chapter-level theory labels assigned from TOC context, not classifier performance.",
            extra={"raw_file": fname, "multi_theory": True},
        )
        if not path.exists() or path.stat().st_size < 100:
            rec.eligible = False
            rec.eligibility_status = "EXCLUDED"
            rec.exclusion_reason = "openstax_chapters_not_acquired"
        else:
            # Need enough chapters
            n = sum(1 for _ in path.open() if _.strip())
            if n < 5:
                rec.eligible = False
                rec.eligibility_status = "EXCLUDED"
                rec.exclusion_reason = f"openstax_insufficient_chapters:{n}"
            else:
                rec.evaluate(rules)
        sources.append(asdict(rec))
        if not rec.eligible:
            exclusions.append({"source_id": rec.source_id, "reason": rec.exclusion_reason})

    payload = {
        "rules": asdict(rules),
        "frozen_date": str(date.today()),
        "n_sources": len(sources),
        "n_eligible": sum(1 for s in sources if s["eligible"]),
        "sources": sources,
        "exclusions": exclusions,
        "anti_cherry_pick": (
            "Sources were listed and eligibility-checked before development model scoring. "
            "Do not remove difficult sources unless they violate these rules."
        ),
    }
    path = out_dir / "source_eligibility_v1.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
