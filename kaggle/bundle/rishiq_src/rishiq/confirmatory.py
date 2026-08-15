"""Confirmatory entrypoint — locked until preregistration unlock."""

from __future__ import annotations

from pathlib import Path

from rishiq.experiments.firewall import ConfirmatoryLockedError, assert_confirmatory_allowed


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    try:
        assert_confirmatory_allowed(root)
    except ConfirmatoryLockedError as e:
        raise SystemExit(f"LOCKED: {e}") from e
    raise SystemExit(
        "Unlock present, but confirmatory runner is not enabled until "
        "ontology/prompts/stats are frozen and registration is complete."
    )


if __name__ == "__main__":
    main()
