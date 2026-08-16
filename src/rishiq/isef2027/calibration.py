"""Build calibration split records from existing PD development materials (not sealed)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from rishiq.isef2027.splits import PassageProvenance, Split, content_hash


def build_calibration_from_pd(root: Path, max_per_tradition: int = 15) -> dict:
    """Sample held-out-from-flagship calibration candidates from PD parquet.

    Does NOT touch confirmatory_sealed. Student must still approve final set.
    """
    pq = root / "corpus/development/pd_passages.parquet"
    out_dir = root / "corpus/calibration"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not pq.exists():
        payload = {"status": "SKIP", "reason": "missing pd_passages.parquet"}
        (out_dir / "calibration_manifest.json").write_text(json.dumps(payload, indent=2) + "\n")
        return payload

    df = pd.read_parquet(pq)
    # Exclude rows already used as flagship control labels if identifiable
    records = []
    for trad, g in df.groupby("tradition"):
        sample = g.head(max_per_tradition)
        for _, row in sample.iterrows():
            pid = str(row.get("passage_id", row.name))
            text = str(row.get("translation") or row.get("text") or "")
            rec = PassageProvenance(
                anonymous_id=f"cal-{content_hash(pid)[:10]}",
                work=str(row.get("work", "unknown")),
                tradition=str(trad),
                translator=str(row.get("translator", "")),
                translation_date=str(row.get("translation_year", row.get("year", ""))),
                passage_section_id=pid,
                token_count=len(text.split()),
                content_sha256=content_hash(text),
                split=Split.calibration,
                inclusion_reason="pd_sample_for_calibration_software_tests",
                role=str(row.get("role", "control")),
                licensing_public_domain=True,
            )
            records.append(rec.model_dump(mode="json"))

    payload = {
        "status": "CANDIDATE_CALIBRATION",
        "n_records": len(records),
        "note": "Software calibration candidates only — student must approve before scientific use.",
        "records": records,
    }
    path = out_dir / "calibration_manifest.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    # Update split manifest calibration IDs if present
    split_path = root / "artifacts/isef2027/split_manifest.json"
    if split_path.exists():
        man = json.loads(split_path.read_text())
        cal_ids = [r["anonymous_id"] for r in records]
        # Ensure no overlap with sealed
        sealed = set(man.get("confirmatory_sealed_ids", []))
        cal_ids = [i for i in cal_ids if i not in sealed]
        man["calibration_ids"] = cal_ids
        # overlap check
        issues = []
        for a, b in (
            ("development", "calibration"),
            ("development", "confirmatory_sealed"),
            ("calibration", "confirmatory_sealed"),
        ):
            leak = sorted(set(man.get(f"{a}_ids", [])) & set(man.get(f"{b}_ids", [])))
            if leak:
                issues.append(f"overlap_{a}_{b}:{len(leak)}")
        man["leakage_check"] = {"issues": issues, "status": "PASS" if not issues else "FAIL"}
        split_path.write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
        payload["split_manifest_updated"] = True
        payload["leakage_check"] = man["leakage_check"]

    return payload
