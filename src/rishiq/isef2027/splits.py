"""Three-way split architecture: development / calibration / sealed confirmatory."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Split(str, Enum):
    development = "development"
    calibration = "calibration"
    confirmatory_sealed = "confirmatory_sealed"
    excluded = "excluded"


class PassageProvenance(BaseModel):
    """Minimum provenance fields for every passage/document record."""

    anonymous_id: str
    work: str
    tradition: str
    approximate_date: str = ""
    genre: str = ""
    language: str = ""
    translator: str = ""
    translation_date: str = ""
    source_edition: str = ""
    passage_section_id: str = ""
    token_count: int = 0
    licensing_public_domain: bool = True
    content_sha256: str
    split: Split
    inclusion_reason: str = ""
    exclusion_reason: str = ""
    role: str = ""  # target / control / physics_reference / etc.
    extra: dict[str, Any] = Field(default_factory=dict)


class SplitManifest(BaseModel):
    version: str = "isef2027-splits-v1"
    generated_at: str = ""
    sealed: bool = True
    note: str = (
        "confirmatory_sealed IDs must not be opened for analysis until "
        "configuration freeze + preregistration unlock."
    )
    development_ids: list[str] = Field(default_factory=list)
    calibration_ids: list[str] = Field(default_factory=list)
    confirmatory_sealed_ids: list[str] = Field(default_factory=list)
    excluded_ids: list[str] = Field(default_factory=list)
    records: list[PassageProvenance] = Field(default_factory=list)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def assert_no_split_overlap(manifest: SplitManifest) -> list[str]:
    issues: list[str] = []
    sets = {
        "development": set(manifest.development_ids),
        "calibration": set(manifest.calibration_ids),
        "confirmatory_sealed": set(manifest.confirmatory_sealed_ids),
    }
    for a, b in (("development", "calibration"), ("development", "confirmatory_sealed"), ("calibration", "confirmatory_sealed")):
        leak = sorted(sets[a] & sets[b])
        if leak:
            issues.append(f"overlap_{a}_{b}:{len(leak)}")
    return issues


def build_skeleton_manifest(root: Path) -> SplitManifest:
    """Seed development IDs from known exploratory corpora; sealed stays empty until student fills."""
    records: list[PassageProvenance] = []
    dev_ids: list[str] = []

    # Known exploratory sources (hashes of files, not passage-level yet)
    seeds = [
        ("dev-vais-gretil", "Vaiśeṣika Sūtra (GRETIL)", "Indian:Vaiśeṣika", "development", "flagship_primary"),
        ("dev-pras-gretil", "Praśastapāda PDS (GRETIL)", "Indian:Vaiśeṣika", "development", "flagship_commentary"),
        ("dev-lucretius-pd", "Lucretius PD panel", "Greek:Epicurean", "development", "flagship_control"),
        ("dev-timaeus-pd", "Plato Timaeus PD panel", "Greek:Platonic", "development", "flagship_control"),
        ("dev-ddj-pd", "Dao De Jing PD panel", "Chinese", "development", "flagship_control"),
        ("dev-dhammapada-pd", "Dhammapada PD panel", "Buddhist", "development", "flagship_control"),
    ]
    for aid, work, trad, split, reason in seeds:
        blob = f"{aid}|{work}|{trad}"
        rec = PassageProvenance(
            anonymous_id=aid,
            work=work,
            tradition=trad,
            content_sha256=content_hash(blob),
            split=Split(split),
            inclusion_reason=reason,
            licensing_public_domain=True,
        )
        records.append(rec)
        if split == "development":
            dev_ids.append(aid)

    return SplitManifest(
        generated_at=datetime.now(timezone.utc).isoformat(),
        development_ids=dev_ids,
        calibration_ids=[],
        confirmatory_sealed_ids=[],  # intentionally empty — student populates without AI peeking
        excluded_ids=[],
        records=records,
        sealed=True,
    )


def write_split_manifest(root: Path) -> Path:
    """Write/update split manifest without wiping reserved sealed IDs."""
    out = root / "artifacts/isef2027/split_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    man = build_skeleton_manifest(root)
    payload = man.model_dump(mode="json")

    if out.exists():
        prev = json.loads(out.read_text(encoding="utf-8"))
        # Preserve reserved sealed + calibration + excluded + non-dev records
        payload["confirmatory_sealed_ids"] = prev.get("confirmatory_sealed_ids", [])
        payload["calibration_ids"] = prev.get("calibration_ids", []) or payload["calibration_ids"]
        payload["excluded_ids"] = prev.get("excluded_ids", [])
        prev_records = prev.get("records", [])
        sealed_recs = [r for r in prev_records if r.get("split") == "confirmatory_sealed"]
        cal_recs = [r for r in prev_records if r.get("split") == "calibration"]
        # Keep skeleton development records; append preserved sealed/cal
        payload["records"] = payload["records"] + cal_recs + sealed_recs
        if prev.get("note"):
            payload["note"] = prev["note"]

    issues = assert_no_split_overlap(SplitManifest.model_validate(payload))
    payload["leakage_check"] = {"issues": issues, "status": "PASS" if not issues else "FAIL"}
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    sealed = root / "corpus/confirmatory_sealed"
    sealed.mkdir(parents=True, exist_ok=True)
    lock = sealed / "lock.json"
    n_sealed = len(payload.get("confirmatory_sealed_ids", []))
    if not lock.exists():
        (sealed / "README.md").write_text(
            "# CONFIRMATORY SEALED\n\n"
            "**DO NOT** score sealed payloads during development.\n"
            f"Reserved IDs: {n_sealed}. See lock.json + split_manifest.json.\n"
            "Status: LOCKED\n",
            encoding="utf-8",
        )
    else:
        (sealed / "README.md").write_text(
            "# CONFIRMATORY SEALED\n\n"
            "**Status: LOCKED / RESERVED**\n\n"
            f"Reserved IDs: {n_sealed}. Outcomes unscored. See `lock.json`.\n",
            encoding="utf-8",
        )
    cal = root / "corpus/calibration"
    cal.mkdir(parents=True, exist_ok=True)
    (cal / "README.md").write_text(
        "# Calibration split\n\n"
        "New materials for software/variance/power tests — not confirmatory.\n"
        "Student-approved works only; see `control_panel_candidates.yaml`.\n",
        encoding="utf-8",
    )
    return out
