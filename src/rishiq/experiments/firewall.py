"""Development vs confirmatory firewall."""

from __future__ import annotations

from pathlib import Path


CONFIRMATORY_UNLOCK = "protocol/.confirmatory_unlocked"


class ConfirmatoryLockedError(RuntimeError):
    pass


def assert_not_confirmatory_path(path: str | Path) -> None:
    p = Path(path).resolve()
    parts = {x.lower() for x in p.parts}
    if "confirmatory_locked" in parts or (
        "results" in parts and "confirmatory" in parts and p.name != "README.md"
    ):
        # Allow empty README/gitkeep; block analysis artifacts
        if p.name in {"README.md", ".gitkeep"}:
            return
        raise ConfirmatoryLockedError(
            f"Refusing to read/write confirmatory path before unlock: {p}"
        )


def confirmatory_unlocked(repo_root: str | Path) -> bool:
    return (Path(repo_root) / CONFIRMATORY_UNLOCK).exists()


def assert_confirmatory_allowed(repo_root: str | Path) -> None:
    if not confirmatory_unlocked(repo_root):
        raise ConfirmatoryLockedError(
            "Confirmatory analysis is locked until preregistration unlock file exists "
            f"at {CONFIRMATORY_UNLOCK}"
        )


def split_guard(dataset_split: str) -> None:
    if dataset_split == "confirmatory":
        raise ConfirmatoryLockedError(
            "Attempted to analyze confirmatory split while locked"
        )
