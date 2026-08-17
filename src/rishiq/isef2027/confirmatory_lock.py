"""Ancient confirmatory lock — real verification (no hardcoded True)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rishiq.experiments.firewall import CONFIRMATORY_UNLOCK


# Paths that must not contain scored confirmatory outcomes while locked.
_FORBIDDEN_RESULT_GLOBS = [
    "results/confirmatory/**/*.json",
    "results/confirmatory/**/*.jsonl",
    "results/confirmatory/**/*.parquet",
    "results/isef2027/confirmatory/**/*.json",
    "results/isef2027/confirmatory/**/*.jsonl",
    "corpus/confirmatory_sealed/**/*score*",
    "corpus/confirmatory_sealed/**/*result*",
    "corpus/confirmatory_sealed/**/*qs*",
]

_SCORE_KEYS = {
    "qs",
    "primary_score",
    "primary_effect",
    "ontology_score",
    "confirmatory_score",
    "sealed_score",
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _json_contains_score_payload(obj: Any) -> bool:
    if isinstance(obj, dict):
        keys = {str(k).lower() for k in obj}
        if keys & _SCORE_KEYS:
            return True
        for v in obj.values():
            if _json_contains_score_payload(v):
                return True
    elif isinstance(obj, list):
        return any(_json_contains_score_payload(x) for x in obj)
    return False


def _collect_split_ids(root: Path) -> dict[str, set[str]]:
    sm = _load_json(root / "artifacts/isef2027/split_manifest.json") or {}
    return {
        "development": set(sm.get("development_ids") or []),
        "calibration": set(sm.get("calibration_ids") or []),
        "train": set(sm.get("train_ids") or []),
        "confirmatory_sealed": set(sm.get("confirmatory_sealed_ids") or []),
    }


def verify_ancient_confirmatory_lock(root: Path) -> dict[str, Any]:
    """Inspect canonical confirmatory state. Does not repair.

    Returns:
      {
        "ok": bool,
        "ancient_confirmatory_locked": bool,
        "status_label": "LOCKED_NOT_READY" | "LOCK_BROKEN",
        "failing_invariants": [str, ...],
        "details": {...},
      }
    """
    root = Path(root)
    failing: list[str] = []
    details: dict[str, Any] = {}

    lock_path = root / "corpus/confirmatory_sealed/lock.json"
    lock = _load_json(lock_path)
    if lock is None:
        failing.append("lock.json missing or unreadable")
        lock = {}
    details["lock_path"] = str(lock_path.relative_to(root)) if lock_path.exists() else None

    if lock.get("status") != "LOCKED":
        failing.append(f"lock.status == {lock.get('status')!r} (required LOCKED)")
    if lock.get("allow_open_sealed") is not False:
        failing.append(f"allow_open_sealed == {lock.get('allow_open_sealed')!r} (required false)")

    unlock = root / CONFIRMATORY_UNLOCK
    if unlock.exists():
        failing.append(f"unlock file present at {CONFIRMATORY_UNLOCK}")
    details["unlock_file_present"] = unlock.exists()

    status = _load_json(root / "artifacts/isef2027/PROJECT_STATUS.json") or {}
    if status.get("confirmatory_opened") is not False:
        failing.append(f"confirmatory_opened == {status.get('confirmatory_opened')!r} (required false)")
    if status.get("confirmatory_scored") is not False:
        failing.append(f"confirmatory_scored == {status.get('confirmatory_scored')!r} (required false)")
    if status.get("sealed_outcomes_scored") is not False:
        failing.append(
            f"sealed_outcomes_scored == {status.get('sealed_outcomes_scored')!r} (required false)"
        )
    # accept either confirmatory_status or ancient_confirmatory_status
    conf_label = status.get("ancient_confirmatory_status") or status.get("confirmatory_status")
    if conf_label not in {None, "LOCKED_NOT_READY"}:
        # None is tolerated only if other fields prove lock; prefer explicit label
        if conf_label not in {"LOCKED", "LOCKED_NOT_READY"}:
            failing.append(f"project confirmatory status label == {conf_label!r}")

    sealed_from_lock = set(lock.get("confirmatory_sealed_ids") or [])
    splits = _collect_split_ids(root)
    sealed_from_manifest = splits["confirmatory_sealed"]
    details["sealed_ids_lock"] = sorted(sealed_from_lock)
    details["sealed_ids_manifest"] = sorted(sealed_from_manifest)

    if not sealed_from_lock:
        failing.append("lock.confirmatory_sealed_ids empty")
    if sealed_from_manifest and sealed_from_lock and sealed_from_lock != sealed_from_manifest:
        failing.append("lock sealed IDs do not match split_manifest.confirmatory_sealed_ids")

    sealed = sealed_from_lock or sealed_from_manifest
    for name in ("development", "calibration", "train"):
        overlap = sorted(sealed & splits[name])
        if overlap:
            failing.append(f"sealed IDs overlap {name}: {overlap}")

    # passage-level overlap via corpus ids if present in split records
    sm = _load_json(root / "artifacts/isef2027/split_manifest.json") or {}
    records = sm.get("records") or {}
    if isinstance(records, dict):
        for sid in sealed:
            rec = records.get(sid) or {}
            assigned = rec.get("split") or rec.get("assignment")
            if assigned in {"train", "development", "calibration", "dev"}:
                failing.append(f"sealed id {sid} assigned to {assigned} in split records")

    # Forbid scored confirmatory result artifacts
    scored_hits: list[str] = []
    for pattern in _FORBIDDEN_RESULT_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            if path.name in {"README.md", ".gitkeep", "lock.json"}:
                continue
            # feasibility metadata without scores is allowed under results/isef2027/validation/
            if "feasibility" in path.name.lower() and "confirmatory" in path.name.lower():
                data = _load_json(path)
                if data and _json_contains_score_payload(data):
                    scored_hits.append(str(path.relative_to(root)))
                continue
            if path.suffix in {".json", ".jsonl"}:
                try:
                    if path.suffix == ".json":
                        data = json.loads(path.read_text(encoding="utf-8"))
                        if _json_contains_score_payload(data):
                            scored_hits.append(str(path.relative_to(root)))
                    else:
                        for line in path.read_text(encoding="utf-8").splitlines():
                            if not line.strip():
                                continue
                            row = json.loads(line)
                            if _json_contains_score_payload(row):
                                scored_hits.append(str(path.relative_to(root)))
                                break
                except Exception:
                    scored_hits.append(str(path.relative_to(root)) + " (unreadable)")
            else:
                scored_hits.append(str(path.relative_to(root)))
    if scored_hits:
        failing.append("confirmatory result/score artifact present: " + ", ".join(scored_hits[:8]))
    details["scored_artifact_hits"] = scored_hits

    ok = len(failing) == 0
    return {
        "ok": ok,
        "ancient_confirmatory_locked": ok,
        "status_label": "LOCKED_NOT_READY" if ok else "LOCK_BROKEN",
        "failing_invariants": failing,
        "details": details,
    }
