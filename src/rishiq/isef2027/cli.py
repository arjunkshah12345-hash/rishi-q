"""CLI: rishiq-isef — ISEF2027 technical runner (no paper writing)."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print as rprint

from rishiq.experiments.firewall import ConfirmatoryLockedError, assert_confirmatory_allowed
from rishiq.isef2027.freeze import freeze_dev
from rishiq.isef2027.inventory import write_inventory
from rishiq.isef2027.runner import run_dev_calibration
from rishiq.isef2027.splits import write_split_manifest

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="RISHI-Q ISEF2027 technical tooling (no abstract/paper generation)",
)


def _root() -> Path:
    return Path(__file__).resolve().parents[3]


@app.command("inventory")
def inventory_cmd() -> None:
    path = write_inventory(_root())
    rprint({"wrote": str(path)})


@app.command("freeze")
def freeze_cmd() -> None:
    path = freeze_dev(_root())
    rprint({"wrote": str(path)})


@app.command("splits")
def splits_cmd() -> None:
    path = write_split_manifest(_root())
    rprint({"wrote": str(path)})


@app.command("reproduce")
def reproduce_cmd(
    config: Path = typer.Option(Path("configs/isef2027.yaml"), "--config"),
) -> None:
    """Regenerate DEV/CALIBRATION harness artifacts. Never opens sealed confirmatory."""
    root = _root()
    # Prefer repo-relative config even if the shell resolved a relative Path.
    cfg = config if config.is_absolute() and config.exists() else (root / "configs/isef2027.yaml")
    if config.is_absolute() and config.exists():
        cfg = config
    elif (root / config).exists():
        cfg = root / config
    else:
        cfg = root / "configs/isef2027.yaml"
    summary = run_dev_calibration(root, cfg)
    rprint(
        {
            "run_id": summary["run_id"],
            "sealed_opened": summary["sealed_confirmatory_opened"],
            "summary": summary["paths"],
            "positive_control_top1_correct": summary["positive_control_ranking"]["top1_correct"],
        }
    )


@app.command("confirmatory-status")
def confirmatory_status() -> None:
    root = _root()
    try:
        assert_confirmatory_allowed(root)
        rprint({"status": "UNLOCKED_BUT_RUNNER_NOT_ENABLED"})
    except ConfirmatoryLockedError as e:
        rprint({"status": "LOCKED", "detail": str(e)})


@app.command("reproduce-all")
def reproduce_all_cmd(
    config: Path = typer.Option(Path("configs/isef2027.yaml"), "--config"),
) -> None:
    """Full DEV harness + rebuild interactive visuals."""
    import subprocess
    import sys

    reproduce_cmd(config=config)
    root = _root()
    script = root / "scripts" / "build_isef2027_visuals.py"
    proc = subprocess.run([sys.executable, str(script)], cwd=str(root))
    if proc.returncode != 0:
        raise typer.Exit(code=proc.returncode)
    rprint({"visuals": str((root / "visuals/isef2027/index.html"))})


@app.command("graphs")
def graphs_cmd() -> None:
    from rishiq.isef2027.graph_templates import build_all_theory_graph_templates

    paths = build_all_theory_graph_templates(_root())
    rprint({"n": len(paths), "wrote": [str(p) for p in paths[-8:]]})


@app.command("show-summary")
def show_summary(path: Path = Path("results/isef2027/dev/run_summary.json")) -> None:
    p = _root() / path if not path.is_absolute() else path
    rprint(json.loads(p.read_text(encoding="utf-8")))


if __name__ == "__main__":
    app()
