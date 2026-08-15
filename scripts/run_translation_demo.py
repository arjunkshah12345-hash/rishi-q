"""Generate synthetic multi-translation pairs to demonstrate TCI without claiming Sanskrit results."""

from __future__ import annotations

from pathlib import Path

from rishiq.experiments import passages_to_parquet, run_pipeline_on_passages
from rishiq.models import DatasetSplit, Passage
from rishiq.normalize.translation import summarize_tci, translation_contamination_index
from rishiq.provenance import sha256_text
import pandas as pd


def pair(
    family: str,
    style: str,
    text: str,
    year: int,
) -> Passage:
    return Passage(
        passage_id=f"{family}__{style}",
        tradition="synthetic_translation_demo",
        school="demo",
        work="Synthetic multi-translation demo",
        section=family,
        source_language="en",
        translation=text,
        translation_id=f"{family}-{style}",
        translator="synthetic",
        translation_year=year,
        translation_style=style,
        license_status="synthetic",
        dataset_split=DatasetSplit.SYNTHETIC,
        role="control",
        genre="method_demo",
        topic="translation_contamination",
        source_hash=sha256_text(text),
        notes=f"passage_family_id={family}",
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    # Same structural claim; modern wording injects physics vocabulary (should be maskable later)
    family = "DEMO_SUBSTRATE_001"
    passages = [
        pair(
            family,
            "literal",
            "An underlying reality persists while visible forms change. A continuous medium extends through space. Local forms appear within that broader reality.",
            1880,
        ),
        pair(
            family,
            "older_scholarly",
            "An underlying reality persists while visible forms change. A continuous medium extends through space. Local forms appear within that broader reality.",
            1920,
        ),
        pair(
            family,
            "recent_scholarly",
            "An underlying quantum-like field of energy permeates space while observable particles arise as localized vibrations of that field.",
            2018,
        ),
    ]
    out_corpus = root / "corpus/development/translation_demo_passages.parquet"
    passages_to_parquet(passages, out_corpus)
    out_dir = root / "results/exploratory/translation_demo"
    run_pipeline_on_passages(
        passages,
        ontology_path=root / "ontology/ontology_v0.1.yaml",
        fingerprint_dir=root / "ontology/physics_fingerprints",
        out_dir=out_dir,
        experiment_id="translation-demo-v0.1",
        repo_root=root,
    )
    scores = pd.read_parquet(out_dir / "passage_scores.parquet")
    scores["passage_family_id"] = family
    scores["translation_style"] = scores["passage_id"].str.split("__").str[-1]
    tci = translation_contamination_index(scores)
    summary = summarize_tci(tci)
    tci.to_csv(out_dir / "tci_pairs.csv", index=False)
    (out_dir / "tci_summary.json").write_text(
        __import__("json").dumps(summary, indent=2), encoding="utf-8"
    )
    print(summary)
    print("wrote", out_dir)


if __name__ == "__main__":
    main()
