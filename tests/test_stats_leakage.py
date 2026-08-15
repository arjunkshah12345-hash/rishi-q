"""Additional tests: leakage, stats, firewall, masking vocab file."""

from __future__ import annotations

import json
from pathlib import Path

from rishiq.ingest.synthetic import modern_physics_passages, synthetic_philosophy_passages
from rishiq.leakage import audit_leakage
from rishiq.statistics import bh_fdr, mean_difference
from rishiq.experiments.firewall import ConfirmatoryLockedError, assert_confirmatory_allowed
from rishiq.normalize.translation import translation_contamination_index
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_leakage_audit_pass_on_synthetic():
    report = audit_leakage(modern_physics_passages() + synthetic_philosophy_passages())
    assert report["exact_duplicate_groups"] == 0
    assert report["status"] in {"PASS", "PASS_WITH_WARNINGS"}


def test_bh_fdr_basic():
    rejected = bh_fdr([0.001, 0.01, 0.2, 0.5], q=0.05)
    assert rejected[0] is True
    assert rejected[-1] is False


def test_mean_difference():
    assert mean_difference([1.0, 1.0], [0.0, 0.0]) == 1.0


def test_power_grid_nonempty():
    from rishiq.statistics import power_simulation

    sim = power_simulation(
        effect=0.2,
        n_clusters_per_arm=8,
        passages_per_cluster=3,
        n_sim=20,
        seed=0,
    )
    assert 0.0 <= sim["power"] <= 1.0
    assert "effect" in sim


def test_confirmatory_cli_lock():
    try:
        assert_confirmatory_allowed(ROOT)
        raised = False
    except ConfirmatoryLockedError:
        raised = True
    assert raised


def test_vocab_config_exists():
    data = json.loads((ROOT / "configs/physics_vocab_v0.1.json").read_text())
    assert "energy" in data["terms"]
    assert "quantum" in data["terms"]


def test_tci_empty_without_pairs():
    df = pd.DataFrame(
        {
            "passage_family_id": ["a", "b"],
            "translation_style": ["recent_scholarly", "literal"],
            "QS": [0.2, 0.1],
        }
    )
    # different families → no pairs
    out = translation_contamination_index(df)
    assert out.empty
