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


def _project_status(root: Path) -> dict:
    path = root / "artifacts/isef2027/PROJECT_STATUS.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


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
            "held_out_top1": summary.get("held_out_theory_validation_summary", {}).get("top1_accuracy"),
            "summary": summary["paths"],
        }
    )


@app.command("status")
def status_cmd() -> None:
    """Print PROJECT_STATUS.json + lock scorecard (single source of truth)."""
    root = _root()
    st = _project_status(root)
    lock = json.loads((root / "corpus/confirmatory_sealed/lock.json").read_text(encoding="utf-8"))
    try:
        assert_confirmatory_allowed(root)
        sealed = "UNLOCKED"
    except ConfirmatoryLockedError:
        sealed = "LOCKED"

    view = {
        "v1_prereg_release": st.get("v1_prereg_release"),
        "v1_label": st.get("v1_status_label"),
        "v2_status": st.get("v2_status"),
        "confirmatory_status": st.get("confirmatory_status", sealed),
        "confirmatory_opened": st.get("confirmatory_opened", False),
        "confirmatory_scored": st.get("confirmatory_scored", False),
        "osf_registered": st.get("osf_registered", False),
        "sealed_ids_reserved": len(lock.get("confirmatory_sealed_ids", [])),
        "physics_fingerprints_verified": st.get("physics_fingerprints_verified"),
        "power_analysis_valid": st.get("power_analysis_valid"),
        "method_validation_complete": st.get("method_validation_complete"),
    }
    rprint(view)
    for k, v in view.items():
        rprint(f"  · {k}: {v}")


@app.command("validate-freeze")
def validate_freeze_cmd() -> None:
    import subprocess
    import sys

    script = _root() / "scripts" / "validate_isef2027_freeze.py"
    raise typer.Exit(subprocess.call([sys.executable, str(script)]))


@app.command("confirmatory-status")
def confirmatory_status() -> None:
    root = _root()
    st = _project_status(root)
    try:
        assert_confirmatory_allowed(root)
        rprint({"status": "UNLOCKED_BUT_RUNNER_NOT_ENABLED"})
    except ConfirmatoryLockedError as e:
        rprint(
            {
                "status": "LOCKED",
                "project_status": st.get("confirmatory_status", "LOCKED_NOT_READY"),
                "detail": str(e),
            }
        )


@app.command("reproduce-all")
def reproduce_all_cmd(
    config: Path = typer.Option(Path("configs/isef2027.yaml"), "--config"),
) -> None:
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


@app.command("harden-v2")
def harden_v2_cmd() -> None:
    """Run v2 scientific hardening pipelines without opening sealed confirmatory."""
    root = _root()
    from rishiq.isef2027.corpus_manifest import build_confirmatory_candidate_manifest
    from rishiq.isef2027.fingerprint_review import run_fingerprint_sanity, write_fingerprint_review_packets
    from rishiq.isef2027.theory_validation import run_held_out_theory_validation
    from rishiq.isef2027.translation_pairs import write_translation_pair_manifest_stub

    held = run_held_out_theory_validation(root)
    cand = build_confirmatory_candidate_manifest(root)
    write_translation_pair_manifest_stub(root)
    sanity = run_fingerprint_sanity(root)
    write_fingerprint_review_packets(root)
    rprint(
        {
            "held_out_top1": held["held_out"]["top1_accuracy"],
            "weakest": held["held_out"]["weakest_theory_by_f1"],
            "corpus_feasibility": cand["feasibility"],
            "sanity_pass": sanity["pass_objective"],
        }
    )


@app.command("show-summary")
def show_summary(path: Path = Path("results/isef2027/dev/run_summary.json")) -> None:
    p = _root() / path if not path.is_absolute() else path
    rprint(json.loads(p.read_text(encoding="utf-8")))


if __name__ == "__main__":
    app()
