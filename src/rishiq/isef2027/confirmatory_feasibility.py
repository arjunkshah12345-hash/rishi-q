"""Confirmatory corpus feasibility inventory (metadata only — no scoring)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def assess_confirmatory_feasibility(root: Path) -> dict[str, Any]:
    sealed = root / "corpus/confirmatory_sealed/lock.json"
    sealed_meta: dict[str, Any] = {}
    if sealed.exists():
        sealed_meta = json.loads(sealed.read_text(encoding="utf-8"))

    meta_path = root / "data/theory_validation_v2/passages/corpus_meta.json"
    method_meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}

    candidate_final_families = [
        {
            "source_family": "planck_theory_of_heat_radiation_pd",
            "license": "public_domain",
            "theories_possible": ["thermodynamics", "quantum_mechanics"],
            "status": "CANDIDATE_ELIGIBLE_PD",
        },
        {
            "source_family": "heaviside_em_pd",
            "license": "public_domain",
            "theories_possible": ["classical_em"],
            "status": "CANDIDATE_ELIGIBLE_PD",
        },
        {
            "source_family": "bohr_atomic_theory_pd",
            "license": "public_domain",
            "theories_possible": ["quantum_mechanics", "atomistic_corpuscular"],
            "status": "CANDIDATE_ELIGIBLE_PD",
        },
        {
            "source_family": "minkowski_spacetime_pd",
            "license": "public_domain",
            "theories_possible": ["relativity"],
            "status": "CANDIDATE_ELIGIBLE_PD",
        },
        {
            "source_family": "dirac_principles_qm_check_rights",
            "license": "copyright_status_verify",
            "theories_possible": ["quantum_mechanics", "quantum_field_theory"],
            "status": "LICENSE_GATE",
        },
    ]

    power_path = root / "results/isef2027/validation/power_sensitivity_table.json"
    power = json.loads(power_path.read_text(encoding="utf-8")) if power_path.exists() else {}

    n_candidate_independent = sum(1 for c in candidate_final_families if c["status"].startswith("CANDIDATE"))
    sealed_ids = sealed_meta.get("sealed_ids") or sealed_meta.get("confirmatory_sealed_ids") or []
    if isinstance(sealed_ids, dict):
        n_sealed = len(sealed_ids)
    else:
        n_sealed = len(sealed_ids) if sealed_ids else sealed_meta.get("n_sealed", "UNKNOWN")

    if isinstance(n_sealed, int) and n_sealed >= 10 and n_candidate_independent >= 4:
        feasibility = "PROJECT_FEASIBLE_WITH_REDUCED_EFFECT_SENSITIVITY"
        detail = "Candidate families exist; confirmatory arm size may limit small-effect power."
    elif isinstance(n_sealed, int) and n_sealed >= 6:
        feasibility = "PRIMARY_QUESTION_NEEDS_RESCOPING"
        detail = "Sealed confirmatory N may be too small for ambitious work-level effects."
    else:
        feasibility = "PROJECT_FEASIBLE_WITH_REDUCED_EFFECT_SENSITIVITY"
        detail = "Treat confirmatory N as constrained; do not manufacture independence."

    payload = {
        "assessment_id": "ISEF2027-CONFIRMATORY-FEASIBILITY-v1",
        "ancient_confirmatory_status": "LOCKED_NOT_READY",
        "scored": False,
        "n_method_dev_passages": method_meta.get("n_passages"),
        "n_method_dev_works": method_meta.get("n_works"),
        "n_method_dev_source_families": method_meta.get("n_source_families"),
        "n_sealed_confirmatory_units": n_sealed,
        "independent_candidate_final_families": candidate_final_families,
        "n_independent_candidate_families": n_candidate_independent,
        "matched_controls_rule": "prespecified matching variables — not outcome",
        "feasibility": feasibility,
        "detail": detail,
        "power_table_ref": "results/isef2027/validation/power_sensitivity_table.json",
        "power_sample": power.get("rows", [])[:5] if isinstance(power, dict) else [],
    }
    out = root / "results/isef2027/validation/confirmatory_corpus_feasibility.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
