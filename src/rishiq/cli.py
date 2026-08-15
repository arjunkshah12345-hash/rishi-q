"""RISHI-Q command-line interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint

from rishiq.experiments import passages_from_parquet, run_pipeline_on_passages
from rishiq.experiments.firewall import ConfirmatoryLockedError, assert_confirmatory_allowed
from rishiq.leakage import audit_leakage, write_leakage_report
from rishiq.models.ontology import validate_ontology_file
from rishiq.provenance import sha256_file

app = typer.Typer(add_completion=False, no_args_is_help=True, help="RISHI-Q research CLI")


@app.command("validate-ontology")
def validate_ontology(path: Path) -> None:
    """Validate ontology YAML schema and feature set."""
    result = validate_ontology_file(path)
    rprint(result)


@app.command("validate-corpus")
def validate_corpus(path: Path) -> None:
    """Validate passage Parquet against Pydantic schema."""
    passages = passages_from_parquet(path)
    rprint({"ok": True, "n_passages": len(passages), "hash": sha256_file(path)})


@app.command("blind")
def blind_cmd(path: Path, out: Path = Path("results/exploratory/blinded.json")) -> None:
    """Blind a corpus for annotation (writes anonymous texts; mapping is private)."""
    from rishiq.blinding import blind_corpus

    passages = passages_from_parquet(path)
    mapping_path = out.with_suffix(".private.json")
    blinded, _ = blind_corpus(passages, mapping_path=mapping_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps([b.model_dump() for b in blinded], indent=2),
        encoding="utf-8",
    )
    rprint({"n": len(blinded), "blinded": str(out), "mapping_private": str(mapping_path)})


@app.command("annotate")
def annotate_cmd(
    config: Path = Path("configs/development.yaml"),
) -> None:
    """Run annotation+scoring pipeline from a YAML config."""
    import yaml

    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
    passages = passages_from_parquet(cfg["corpus_path"])
    result = run_pipeline_on_passages(
        passages,
        ontology_path=cfg["ontology_path"],
        fingerprint_dir=cfg["fingerprint_dir"],
        out_dir=cfg["out_dir"],
        experiment_id=cfg.get("experiment_id", "development"),
        metric=cfg.get("metric", "weighted_jaccard"),
        seed=cfg.get("seed", 42),
        repo_root=cfg.get("repo_root", "."),
    )
    rprint(result)


@app.command("score")
def score_cmd(config: Path = Path("configs/development.yaml")) -> None:
    """Alias for annotate (scores produced in same pipeline)."""
    annotate_cmd(config)


@app.command("analyze")
def analyze_cmd(
    scores: Path = Path("results/exploratory/synthetic_e2e/passage_scores.parquet"),
) -> None:
    """Print descriptive QS summary by role/tradition."""
    import pandas as pd

    df = pd.read_parquet(scores)
    rprint(df.groupby(["role", "tradition"])["QS"].agg(["mean", "std", "count"]).to_string())


@app.command("robustness")
def robustness_cmd(
    config: Path = Path("configs/development.yaml"),
) -> None:
    """Run placeholder robustness table from primary exploratory delta."""
    import yaml
    import pandas as pd
    from rishiq.robustness import run_robustness_battery

    cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
    scores = Path(cfg["out_dir"]) / "passage_scores.parquet"
    df = pd.read_parquet(scores)
    t = df[df["role"] == "target"]["QS"]
    c = df[df["role"] == "control"]["QS"]
    primary = float(t.mean() - c.mean()) if len(t) and len(c) else 0.0
    rows = run_robustness_battery(primary_delta=primary, variants={"N_no_embeddings": primary})
    out = Path(cfg["out_dir"]) / "robustness.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    rprint({"primary_delta": primary, "wrote": str(out)})


@app.command("leakage-audit")
def leakage_cmd(
    path: Path,
    out: Path = Path("results/exploratory/leakage_report.json"),
) -> None:
    passages = passages_from_parquet(path)
    report = audit_leakage(passages)
    write_leakage_report(report, out)
    rprint(report["status"], str(out))


@app.command("discover")
def discover_cmd(
    repo: Path = Path("."),
) -> None:
    """Run System B discovery engine (exploratory; does not unlock confirmatory)."""
    import subprocess
    import sys

    script = Path(repo) / "scripts" / "run_discovery_engine.py"
    if not script.exists():
        rprint(f"[red]missing[/red] {script}")
        raise typer.Exit(code=1)
    proc = subprocess.run([sys.executable, str(script)], cwd=str(repo))
    raise typer.Exit(code=proc.returncode)


@app.command("confirmatory")
def confirmatory_cmd(repo: Path = Path(".")) -> None:
    """Blocked until preregistration unlock."""
    try:
        assert_confirmatory_allowed(repo)
    except ConfirmatoryLockedError as e:
        rprint(f"[red]LOCKED[/red]: {e}")
        raise typer.Exit(code=2)
    rprint("Unlocked — confirmatory runner not yet enabled (await preregistration).")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
