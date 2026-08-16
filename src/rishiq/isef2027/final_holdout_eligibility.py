"""Eligibility + acquisition scaffolding for TRUE final method holdout.

Does NOT build or evaluate the holdout. Separate human/student trigger later:
BUILD_FINAL_VALIDATION_HOLDOUT — only after method freeze.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ELIGIBILITY_RULES = {
    "rules_id": "final_method_holdout_eligibility_v1",
    "require_unseen_source_family_vs_train_dev": True,
    "prefer_unseen_author_family": True,
    "min_works_per_theory": 1,
    "prefer_multiple_works_per_theory": True,
    "licenses_allowed": ["public_domain", "CC BY", "CC BY-SA", "CC0"],
    "exclude_confirmatory_ancient": True,
    "exclude_constructed_unevaluated_reuse_as_pristine": True,
    "do_not_materialize_labels_into_development_files": True,
    "evaluate_once_after_method_freeze": True,
}


def write_final_holdout_eligibility(root: Path) -> dict[str, Any]:
    out_dir = root / "data/theory_validation_v2/final_holdout_candidates"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "eligibility_rules.json").write_text(json.dumps(ELIGIBILITY_RULES, indent=2) + "\n", encoding="utf-8")
    candidates = [
        {
            "source_family": "planck_theory_of_heat_radiation_pd",
            "license": "public_domain",
            "acquisition": "archive.org / PD OCR",
            "theories": ["thermodynamics", "quantum_mechanics"],
            "status": "ELIGIBLE_NOT_ACQUIRED",
        },
        {
            "source_family": "heaviside_electromagnetic_theory_pd",
            "license": "public_domain",
            "acquisition": "archive.org",
            "theories": ["classical_em"],
            "status": "ELIGIBLE_NOT_ACQUIRED",
        },
        {
            "source_family": "bohr_three_papers_pd",
            "license": "public_domain",
            "acquisition": "public domain reprints",
            "theories": ["quantum_mechanics", "atomistic_corpuscular"],
            "status": "ELIGIBLE_NOT_ACQUIRED",
        },
        {
            "source_family": "minkowski_spacetime_pd",
            "license": "public_domain",
            "acquisition": "archive.org",
            "theories": ["relativity"],
            "status": "ELIGIBLE_NOT_ACQUIRED",
        },
    ]
    (out_dir / "candidate_availability.json").write_text(
        json.dumps(
            {
                "true_final_holdout": "NOT_BUILT",
                "build_command": "BUILD_FINAL_VALIDATION_HOLDOUT",
                "gate": "student-approved method freeze required",
                "candidates": candidates,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    # Acquisition tooling stub (does not download yet — avoids contaminating freeze)
    tool = out_dir / "acquire_candidates.py"
    tool.write_text(
        '''"""Acquire final-holdout candidate sources AFTER method freeze.

Usage (student/human gated):
  python data/theory_validation_v2/final_holdout_candidates/acquire_candidates.py --dry-run
"""
from __future__ import annotations
import argparse

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--build", action="store_true", help="Requires BUILD_FINAL_VALIDATION_HOLDOUT env gate")
    args = p.parse_args()
    if args.build:
        raise SystemExit(
            "Refusing: set explicit student-approved freeze + BUILD_FINAL_VALIDATION_HOLDOUT=1 "
            "in a separate operation after method freeze."
        )
    print("Dry-run only. Candidates listed in candidate_availability.json. NOT_BUILT.")

if __name__ == "__main__":
    main()
''',
        encoding="utf-8",
    )
    return {"eligibility": ELIGIBILITY_RULES, "n_candidates": len(candidates), "status": "NOT_BUILT"}
