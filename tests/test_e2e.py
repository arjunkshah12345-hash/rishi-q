"""End-to-end synthetic pipeline test."""

from __future__ import annotations

from pathlib import Path

from rishiq.experiments import run_pipeline_on_passages
from rishiq.ingest.synthetic import modern_physics_passages, synthetic_philosophy_passages

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_e2e(tmp_path: Path):
    passages = modern_physics_passages() + synthetic_philosophy_passages()
    out = tmp_path / "e2e"
    result = run_pipeline_on_passages(
        passages,
        ontology_path=ROOT / "ontology" / "ontology_v0.1.yaml",
        fingerprint_dir=ROOT / "ontology" / "physics_fingerprints",
        out_dir=out,
        experiment_id="test-e2e",
        repo_root=ROOT,
    )
    assert result["n_passages"] == len(passages)
    assert (out / "manifest.json").exists()
    assert (out / "theory_scores.parquet").exists()
    assert (out / "passage_scores.parquet").exists()
    # Physics QM should tend toward higher QS than unity metaphor
    import pandas as pd

    df = pd.read_parquet(out / "passage_scores.parquet")
    qm = float(df.loc[df["passage_id"] == "PHYS_QM_001", "QS"].iloc[0])
    unity = float(df.loc[df["passage_id"] == "SYN_UNITY_001", "QS"].iloc[0])
    assert qm > unity
