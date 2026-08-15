"""Ensure paper asset factory outputs exist after exploratory run."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "paper/figures/fig01_pipeline.png",
    "paper/figures/fig05_positive_controls.png",
    "paper/figures/fig08_qs_qef_scatter.png",
    "paper/tables/tab_project_status.tex",
    "paper/assets/exploratory_numbers.json",
    "paper/preview.html",
    "docs/RESEARCH_JOURNEY.md",
]


def test_paper_assets_present():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    assert not missing, f"missing paper assets: {missing}"


def test_exploratory_numbers_honest():
    import json

    data = json.loads((ROOT / "paper/assets/exploratory_numbers.json").read_text())
    assert data["warning"] == "EXPLORATORY_ONLY_NOT_H1"
    assert data["mean_QS_qm_passage"] > data["mean_QS_unity_control"]
