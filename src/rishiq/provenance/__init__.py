"""Content hashing and experiment manifests."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rishiq.models import ExperimentManifest


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return sha256_text(payload)


def git_commit(repo: str | Path | None = None) -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except Exception:
        return "unknown"


def package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in (
        "numpy",
        "scipy",
        "pandas",
        "polars",
        "pydantic",
        "yaml",
        "sklearn",
        "statsmodels",
        "duckdb",
    ):
        try:
            if name == "yaml":
                import yaml as mod

                versions["pyyaml"] = getattr(mod, "__version__", "unknown")
            elif name == "sklearn":
                import sklearn as mod

                versions["scikit-learn"] = mod.__version__
            else:
                mod = __import__(name)
                versions[name] = getattr(mod, "__version__", "unknown")
        except Exception:
            versions[name] = "missing"
    try:
        from rishiq import __version__ as rq

        versions["rishiq"] = rq
    except Exception:
        versions["rishiq"] = "0.1.0"
    return versions


def build_manifest(
    *,
    experiment_id: str,
    dataset_hash: str,
    ontology_version: str,
    prompt_version: str,
    model_name: str,
    model_revision: str = "unspecified",
    random_seed: int = 42,
    config_hash: str = "",
    fingerprint_hash: str = "",
    notes: str = "",
    extra: dict[str, Any] | None = None,
    repo: str | Path | None = None,
) -> ExperimentManifest:
    return ExperimentManifest(
        experiment_id=experiment_id,
        git_commit=git_commit(repo),
        dataset_hash=dataset_hash,
        ontology_version=ontology_version,
        prompt_version=prompt_version,
        model_name=model_name,
        model_revision=model_revision,
        random_seed=random_seed,
        package_versions=package_versions(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        config_hash=config_hash,
        fingerprint_hash=fingerprint_hash,
        notes=notes,
        extra=extra or {},
    )


def write_manifest(manifest: ExperimentManifest, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return path
