"""Procedural guard for final method holdout — logging + freeze checks, not security theater."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_FREEZE_KEYS = [
    "method_config_frozen",
    "classifier_frozen",
    "preprocessing_frozen",
    "graph_weights_frozen",
    "theory_classes_frozen",
    "train_dev_results_saved",
    "final_test_hash_recorded",
]


def _log_access(root: Path, event: dict[str, Any]) -> None:
    path = root / "data/theory_validation_v2/final_holdout/access_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now(timezone.utc).isoformat(), **event}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def load_method_freeze_gate(root: Path) -> dict[str, Any]:
    path = root / "artifacts/isef2027/theory_validation_v2_method_freeze.json"
    if not path.exists():
        return {"ready": False, "missing": REQUIRED_FREEZE_KEYS, "path": str(path)}
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED_FREEZE_KEYS if not data.get(k)]
    return {"ready": len(missing) == 0, "missing": missing, "data": data, "path": str(path)}


def assert_final_holdout_access_allowed(root: Path, unlock_token: str | None) -> dict[str, Any]:
    """Raise PermissionError unless unlock token + freeze gates pass."""
    expected = "UNLOCK-FINAL-METHOD-HOLDOUT"
    lock_path = root / "data/theory_validation_v2/final_holdout/lock_manifest.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}

    if unlock_token != expected:
        _log_access(
            root,
            {
                "event": "ACCESS_DENIED",
                "reason": "missing_or_invalid_unlock_token",
                "token_provided": bool(unlock_token),
            },
        )
        raise PermissionError(
            "Final holdout access denied. Use: rishiq-isef validate-final-method "
            f"--unlock-token {expected} (only after method freeze)."
        )

    gate = load_method_freeze_gate(root)
    if not gate["ready"]:
        _log_access(
            root,
            {
                "event": "ACCESS_DENIED",
                "reason": "method_not_frozen",
                "missing": gate["missing"],
            },
        )
        raise PermissionError(
            "Method freeze incomplete; final holdout remains UNEVALUATED. "
            f"Missing: {gate['missing']}"
        )

    if lock.get("evaluated"):
        _log_access(root, {"event": "ACCESS_DENIED", "reason": "already_evaluated_once"})
        raise PermissionError(
            "Final holdout already evaluated once (EVALUATED_ONCE_FROZEN_METHOD). Refusing re-run."
        )

    _log_access(root, {"event": "ACCESS_GRANTED", "reason": "token_and_freeze_ok"})
    return {"lock": lock, "gate": gate}


def peek_blocked_message() -> str:
    return (
        "Normal development commands must not load final_holdout. "
        "Use train/development only, or validate-final-method after freeze."
    )
