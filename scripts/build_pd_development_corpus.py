#!/usr/bin/env python3
"""Build a public-domain development corpus from Project Gutenberg texts.

Sampling is reproducible and NOT optimized for quantum-sounding content.
This is DEVELOPMENT / exploratory only — not confirmatory unlock.

Sources (PD):
- Swami Paramananda Upanishads (Gutenberg 3283) — target-like Vedānta
- Lucretius De Rerum Natura (785) — Greek/Roman atomism control
- Plato Timaeus (1572) — Greek cosmology control
- Dhammapada (2017) — Buddhist control
- Tao Te Ching (216) — Chinese control
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from rishiq.experiments import passages_to_parquet
from rishiq.models import DatasetSplit, Passage
from rishiq.provenance import sha256_text

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "corpus/raw/pd"
OUT = ROOT / "corpus/development/pd_passages.parquet"
META = ROOT / "corpus/development/pd_corpus_manifest.json"
SEED = 42


def strip_gutenberg(text: str) -> str:
    start = re.search(r"\*\*\*\s*START OF.*?\*\*\*", text, re.I)
    end = re.search(r"\*\*\*\s*END OF.*?\*\*\*", text, re.I)
    if start:
        text = text[start.end() :]
    if end:
        text = text[: end.start()]
    return text.strip()


def paragraphs(text: str) -> list[str]:
    chunks = re.split(r"\n\s*\n+", text)
    out = []
    for c in chunks:
        c = re.sub(r"\s+", " ", c).strip()
        # drop very short / TOC-like
        if len(c.split()) < 40:
            continue
        if len(c.split()) > 220:
            # split long paragraphs into ~sentence windows
            sents = re.split(r"(?<=[.!?])\s+", c)
            buf: list[str] = []
            for s in sents:
                buf.append(s)
                if len(" ".join(buf).split()) >= 60:
                    out.append(" ".join(buf).strip())
                    buf = []
            if buf and len(" ".join(buf).split()) >= 40:
                out.append(" ".join(buf).strip())
            continue
        out.append(c)
    return out


def sample_passages(
    paras: list[str],
    *,
    n: int,
    tradition: str,
    role: str,
    work: str,
    translator: str,
    year: int,
    source_file: str,
    rng: np.random.Generator,
) -> list[Passage]:
    if not paras:
        return []
    idx = np.arange(len(paras))
    rng.shuffle(idx)
    chosen = idx[: min(n, len(idx))]
    out: list[Passage] = []
    for i, j in enumerate(sorted(chosen)):
        text = paras[int(j)]
        pid = f"PD_{tradition[:8].upper()}_{i:03d}_{hashlib.sha1(text.encode()).hexdigest()[:8]}"
        out.append(
            Passage(
                passage_id=pid,
                tradition=tradition,
                school=tradition,
                work=work,
                section=f"para_{int(j)}",
                source_language="en",
                translation=text,
                translation_id=f"{source_file}:{int(j)}",
                translator=translator,
                translation_year=year,
                translation_style="older_scholarly",
                edition=f"Project Gutenberg / {source_file}",
                source_identifier=source_file,
                source_url="https://www.gutenberg.org/",
                license_status="public_domain",
                genre="philosophical",
                topic="pd_development",
                dataset_split=DatasetSplit.DEVELOPMENT,
                role=role,
                source_hash=sha256_text(text),
                notes="PD development sample; not confirmatory; not cherry-picked for quantum language",
            )
        )
    return out


def load_file(name: str) -> str:
    return strip_gutenberg((RAW / name).read_text(encoding="utf-8", errors="replace"))


def main() -> None:
    rng = np.random.default_rng(SEED)
    # Optional: restrict Upanishads to post-intro content by skipping early front matter paras
    upa = paragraphs(load_file("upanishads_paramananda_3283.txt"))
    # drop obvious front matter: first 15 long paras often prefatory
    upa_body = upa[15:] if len(upa) > 40 else upa

    specs = [
        (upa_body, 80, "vedanta_pd", "target", "Upanishads (Paramananda tr.)", "Swami Paramananda", 1919, "upanishads_paramananda_3283.txt"),
        (paragraphs(load_file("lucretius_785.txt")), 60, "greek_lucretius_pd", "control", "De Rerum Natura", "W. E. Leonard (Gutenberg ed.)", 1916, "lucretius_785.txt"),
        (paragraphs(load_file("plato_timaeus_1572.txt")), 50, "greek_timaeus_pd", "control", "Timaeus", "B. Jowett (Gutenberg ed.)", 1871, "plato_timaeus_1572.txt"),
        (paragraphs(load_file("dhammapada_2017.txt")), 40, "buddhist_dhammapada_pd", "control", "Dhammapada", "F. Max Müller (Gutenberg ed.)", 1881, "dhammapada_2017.txt"),
        (paragraphs(load_file("taoteching_216.txt")), 40, "chinese_ddj_pd", "control", "Tao Te Ching", "James Legge (Gutenberg ed.)", 1891, "taoteching_216.txt"),
    ]

    passages: list[Passage] = []
    report = {"seed": SEED, "sources": [], "warning": "DEVELOPMENT_EXPLORATORY_NOT_CONFIRMATORY"}
    for paras, n, tradition, role, work, translator, year, fname in specs:
        sampled = sample_passages(
            paras,
            n=n,
            tradition=tradition,
            role=role,
            work=work,
            translator=translator,
            year=year,
            source_file=fname,
            rng=rng,
        )
        passages.extend(sampled)
        report["sources"].append(
            {
                "file": fname,
                "tradition": tradition,
                "role": role,
                "available_paragraphs": len(paras),
                "sampled": len(sampled),
            }
        )

    # Add physics positive controls for instrument continuity
    from rishiq.ingest.synthetic import modern_physics_passages

    for p in modern_physics_passages():
        passages.append(p)

    passages_to_parquet(passages, OUT)
    report["n_total"] = len(passages)
    report["n_by_role"] = (
        pd.DataFrame([p.model_dump(mode="json") for p in passages])
        .groupby("role")
        .size()
        .to_dict()
    )
    report["n_by_tradition"] = (
        pd.DataFrame([p.model_dump(mode="json") for p in passages])
        .groupby("tradition")
        .size()
        .to_dict()
    )
    META.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
