"""Acquire final-holdout candidate sources AFTER method freeze.

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
