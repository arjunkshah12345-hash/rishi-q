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
    from rishiq.isef2027.graph_robustness import run_graph_transformation_benchmark
    from rishiq.isef2027.theory_validation import run_held_out_theory_validation
    from rishiq.isef2027.theory_validation_v2_corpus import build_external_theory_corpus
    from rishiq.isef2027.translation_pairs import write_translation_pair_manifest_stub

    held = run_held_out_theory_validation(root)
    grap = run_graph_transformation_benchmark(root)
    try:
        meta = build_external_theory_corpus(root)
    except Exception as e:
        meta = {"error": str(e)}
    cand = build_confirmatory_candidate_manifest(root)
    write_translation_pair_manifest_stub(root)
    sanity = run_fingerprint_sanity(root)
    write_fingerprint_review_packets(root)
    rprint(
        {
            "pedagogy_dev_top1": held["held_out"]["top1_accuracy"],
            "pedagogy_role": held["held_out"].get("evidence_role"),
            "graph_identical": grap["results"]["identical"]["hungarian_role_alignment"],
            "external_corpus": meta,
            "corpus_feasibility": cand["feasibility"],
            "sanity_pass": sanity["pass_objective"],
        }
    )


@app.command("build-external-theory-corpus")
def build_external_corpus_cmd() -> None:
    from rishiq.isef2027.theory_validation_v2_corpus import build_external_theory_corpus

    meta = build_external_theory_corpus(_root())
    rprint(meta)


@app.command("select-method-dev")
def select_method_dev_cmd() -> None:
    """Train/dev model selection only — never loads final holdout."""
    from rishiq.isef2027.theory_validation_v2 import run_development_method_selection

    out = run_development_method_selection(_root())
    rprint(
        {
            "selected_task_a": out["selected_task_a_on_dev"]["model"],
            "macro_f1": out["selected_task_a_on_dev"]["metrics"]["macro_f1"],
            "graph_weights": out["graph_weight_selection"]["selected"],
            "method_freeze": out["method_freeze"]["status"],
            "final_holdout": "UNEVALUATED",
        }
    )


@app.command("graph-robustness")
def graph_robustness_cmd() -> None:
    from rishiq.isef2027.graph_robustness import run_graph_transformation_benchmark

    out = run_graph_transformation_benchmark(_root())
    rprint({"wrote": "results/isef2027/validation/graph_transformation_robustness.json", "n_curve": len(out["results"]["robustness_curve"])})


@app.command("validate-final-method")
def validate_final_method_cmd(
    unlock_token: str = typer.Option(..., "--unlock-token", help="Required deliberate unlock"),
) -> None:
    """Deprecated alias — use evaluate-final-validation-once after freeze + holdout build."""
    rprint(
        {
            "status": "USE_evaluate-final-validation-once",
            "note": "True holdout remains NOT_BUILT until student freeze + build-final-validation-holdout.",
        }
    )
    raise typer.Exit(code=3)


@app.command("student-review")
def student_review_cmd(
    status_only: bool = typer.Option(False, "--status-only", help="Print progress; no prompts"),
    fingerprints: bool = typer.Option(False, "--fingerprints", help="Fingerprint review only"),
    gold: bool = typer.Option(False, "--gold", help="Next gold passage only"),
    theory: str | None = typer.Option(None, "--theory", help="Single theory id for fingerprint review"),
) -> None:
    """Interactive student review: fingerprints → gold (extractor hidden until lock)."""
    from rishiq.isef2027.student_review_workflow import (
        ensure_student_artifacts,
        review_status,
        run_fingerprint_review_interactive,
        run_gold_annotation_interactive,
        run_student_review_menu,
    )

    root = _root()
    ensure_student_artifacts(root)
    if status_only:
        rprint(review_status(root))
        return
    if fingerprints:
        rprint(run_fingerprint_review_interactive(root, theory_id=theory))
        return
    if gold:
        rprint(run_gold_annotation_interactive(root))
        return
    rprint(run_student_review_menu(root))


@app.command("validate-student-review")
def validate_student_review_cmd() -> None:
    """Fail unless fingerprints + gold are complete and machine-valid."""
    from rishiq.isef2027.student_review_validate import validate_student_review

    out = validate_student_review(_root())
    rprint(out)
    if not out.get("ok"):
        raise typer.Exit(code=1)


@app.command("evaluate-extractor-gold")
def evaluate_extractor_gold_cmd() -> None:
    """Stage-1 metrics vs student gold only (development)."""
    from rishiq.isef2027.extractor_gold_eval import evaluate_extractor_gold

    out = evaluate_extractor_gold(_root())
    rprint(out)
    if out.get("status", "").startswith("NOT_AVAILABLE"):
        raise typer.Exit(code=2)


@app.command("finalize-after-student-review")
def finalize_after_student_review_cmd(
    n_sim: int = typer.Option(2000, "--n-sim", help="Monte Carlo sims per power cell (min 2000 when post-student)"),
) -> None:
    """DEV revalidation + weight reselection + power after student review. Refuses if review incomplete."""
    from rishiq.isef2027.post_student_finalize import finalize_after_student_review

    out = finalize_after_student_review(_root(), n_sim=n_sim)
    rprint(out)
    if out.get("status") == "REFUSED":
        raise typer.Exit(code=2)


@app.command("pre-freeze-summary")
def pre_freeze_summary_cmd() -> None:
    """Print the required pre-freeze status block (no auto-approve)."""
    from rishiq.isef2027.post_student_finalize import pre_freeze_summary

    rprint(pre_freeze_summary(_root()))


@app.command("check-freeze-gates")
def check_freeze_gates_cmd() -> None:
    from rishiq.isef2027.method_freeze_gates import write_freeze_candidate_if_ready

    rprint(write_freeze_candidate_if_ready(_root()))


@app.command("verify-frozen-method")
def verify_frozen_method_cmd() -> None:
    """Recompute every claim-bearing hash in the frozen manifest. Never updates it."""
    from rishiq.isef2027.frozen_method_integrity import verify_frozen_method

    out = verify_frozen_method(_root())
    rprint(out)
    if not out.get("ok"):
        raise typer.Exit(code=2)


@app.command("freeze-method")
def freeze_method_cmd(
    confirm: str | None = typer.Option(None, "--confirm", help="Must be FREEZE to commit"),
) -> None:
    """Immutable method freeze — refuses unless all student + engineering gates pass."""
    from rishiq.isef2027.method_freeze_gates import freeze_method

    out = freeze_method(_root(), confirm=confirm)
    rprint(out)
    if out.get("status") not in {"FROZEN", "CONFIRMATION_REQUIRED"}:
        raise typer.Exit(code=2)


@app.command("build-final-validation-holdout")
def build_final_holdout_cmd() -> None:
    """Post-freeze only. Does not score."""
    from rishiq.isef2027.method_freeze_gates import build_final_validation_holdout

    out = build_final_validation_holdout(_root())
    rprint(out)
    if out.get("status") == "REFUSED":
        raise typer.Exit(code=2)


@app.command("evaluate-final-validation-once")
def evaluate_final_once_cmd() -> None:
    """One-shot final validation after freeze + holdout build. No retune."""
    from rishiq.isef2027.method_freeze_gates import evaluate_final_validation_once

    out = evaluate_final_validation_once(_root())
    rprint(out)
    if out.get("status") == "REFUSED":
        raise typer.Exit(code=2)


@app.command("show-summary")
def show_summary(path: Path = Path("results/isef2027/dev/run_summary.json")) -> None:
    p = _root() / path if not path.is_absolute() else path
    rprint(json.loads(p.read_text(encoding="utf-8")))


if __name__ == "__main__":
    app()
