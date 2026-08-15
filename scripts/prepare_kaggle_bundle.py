#!/usr/bin/env python3
"""Package blinded PD corpus + ontology for Kaggle upload."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from rishiq.blinding import blind_corpus
from rishiq.experiments import passages_from_parquet
from rishiq.provenance import sha256_file

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "corpus/development/pd_passages.parquet"
BUNDLE = ROOT / "kaggle/bundle"


def main() -> None:
    if not SRC.exists():
        raise SystemExit("missing pd corpus; run build_pd_development_corpus.py")
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    BUNDLE.mkdir(parents=True)

    passages = passages_from_parquet(SRC)
    blinded, _mapping = blind_corpus(
        passages, mapping_path=BUNDLE / "blinding_map.PRIVATE.json"
    )
    rows = [
        {
            "anonymous_id": b.anonymous_id,
            "text": b.text,
            "source_language": b.source_language,
            "word_count": b.word_count,
        }
        for b in blinded
    ]
    pd.DataFrame(rows).to_parquet(BUNDLE / "blinded_passages.parquet", index=False)
    shutil.copy(SRC, BUNDLE / "pd_passages.parquet")
    shutil.copy(ROOT / "ontology/ontology_v0.1.yaml", BUNDLE / "ontology_v0.1.yaml")
    shutil.copytree(ROOT / "ontology/physics_fingerprints", BUNDLE / "physics_fingerprints")
    shutil.copy(ROOT / "prompts/ann-v0.1.yaml", BUNDLE / "ann-v0.1.yaml")
    shutil.copy(ROOT / "prompts/prop-v0.1.yaml", BUNDLE / "prop-v0.1.yaml")
    shutil.copy(ROOT / "configs/physics_vocab_v0.1.json", BUNDLE / "physics_vocab_v0.1.json")
    shutil.copytree(
        ROOT / "src/rishiq",
        BUNDLE / "rishiq_src/rishiq",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    meta = {
        "n_passages": len(passages),
        "n_blinded": len(blinded),
        "corpus_hash": sha256_file(SRC),
        "ontology_hash": sha256_file(BUNDLE / "ontology_v0.1.yaml"),
        "note": "Do NOT upload blinding_map.PRIVATE.json to a public dataset.",
        "exclude_from_public_upload": ["blinding_map.PRIVATE.json"],
    }
    (BUNDLE / "bundle_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (BUNDLE / "README.md").write_text(
        "# RISHI-Q Kaggle bundle\n\n"
        "1. Upload this folder as a Kaggle dataset (omit `blinding_map.PRIVATE.json` if public).\n"
        "2. Attach dataset to `annotation.ipynb`.\n"
        "3. Enable GPU; run all cells.\n"
        "4. Download `annotations.parquet` + `manifest.json`.\n"
        "5. On Mac join labels via private blinding map and score.\n",
        encoding="utf-8",
    )

    public = ROOT / "kaggle/rishiq_kaggle_bundle_public"
    if public.exists():
        shutil.rmtree(public)
    shutil.copytree(
        BUNDLE,
        public,
        ignore=shutil.ignore_patterns("blinding_map.PRIVATE.json"),
    )
    zip_path = ROOT / "kaggle/rishiq_kaggle_bundle_public"
    shutil.make_archive(str(zip_path), "zip", public)
    print(json.dumps(meta, indent=2))
    print("bundle", BUNDLE)
    print("zip", f"{zip_path}.zip")


if __name__ == "__main__":
    main()
