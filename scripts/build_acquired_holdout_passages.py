#!/usr/bin/env python3
"""Build true-final-holdout acquired passages from Wikisource PD HTML dumps."""
from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/theory_validation_v2/final_holdout_candidates/acquired/raw"
OUT = ROOT / "data/theory_validation_v2/final_holdout_candidates/acquired"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = [
    {
        "json": "minkowski2.json",
        "source_family": "minkowski_spacetime_pd",
        "work_id": "minkowski_space_and_time_saha",
        "author_family": "minkowski",
        "author": "Hermann Minkowski (tr. Meghnad Saha)",
        "theory_label": "relativity",
        "title": "Space and Time",
        "license": "public_domain",
        "url": "https://en.wikisource.org/wiki/Translation:Space_and_Time",
    },
    {
        "json": "heaviside.json",
        "source_family": "heaviside_electromagnetic_theory_pd",
        "work_id": "heaviside_moving_charge_1888",
        "author_family": "heaviside",
        "author": "Oliver Heaviside",
        "theory_label": "classical_em",
        "title": "Electromagnetic effects of a moving charge",
        "license": "public_domain",
        "url": "https://en.wikisource.org/wiki/Electromagnetic_effects_of_a_moving_charge",
    },
    {
        "json": "radiation.json",
        "source_family": "planck_theory_of_heat_radiation_pd",
        "work_id": "britannica_1911_radiation_theory",
        "author_family": "larmor_britannica",
        "author": "Joseph Larmor (1911 Encyclopædia Britannica)",
        "theory_label": "thermodynamics",
        "title": "Radiation, Theory of",
        "license": "public_domain",
        "url": "https://en.wikisource.org/wiki/1911_Encyclopædia_Britannica/Radiation,_Theory_of",
    },
    {
        "json": "bohr_atom.json",
        "source_family": "bohr_three_papers_pd",
        "work_id": "britannica_1926_atom_bohr",
        "author_family": "bohr",
        "author": "Niels Bohr (1926 Encyclopædia Britannica)",
        "theory_label": "quantum_mechanics",
        "title": "Atom",
        "license": "public_domain",
        "url": "https://en.wikisource.org/wiki/1926_Encyclopædia_Britannica/Atom",
    },
]


def html_to_plain(s: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", s, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def carve(text: str, *, n: int = 8, min_words: int = 60, max_words: int = 180) -> list[str]:
    # Prefer sentence packs
    sents = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if len(x.strip()) > 40]
    out: list[str] = []
    buf: list[str] = []
    wc = 0
    for sent in sents:
        # skip nav / css leftovers
        if any(bad in sent.lower() for bad in ("mw-parser-output", ".wst-", "login-button", "javascript")):
            continue
        words = sent.split()
        if not words:
            continue
        buf.append(sent)
        wc += len(words)
        if wc >= min_words:
            chunk = " ".join(buf)
            if len(chunk.split()) <= max_words + 40:
                out.append(chunk)
            buf, wc = [], 0
            if len(out) >= n:
                break
    return out


def main() -> None:
    rows = []
    acquisition_date = date.today().isoformat()
    for src in SOURCES:
        path = RAW / src["json"]
        data = json.loads(path.read_text(encoding="utf-8"))
        plain = html_to_plain(data["parse"]["text"])
        chunks = carve(plain, n=8)
        print(src["source_family"], "plain_chars", len(plain), "chunks", len(chunks))
        for i, text in enumerate(chunks):
            sha = hashlib.sha256(text.encode()).hexdigest()
            pid = f"{src['work_id']}-{i:04d}"
            rows.append(
                {
                    "passage_id": pid,
                    "work_id": src["work_id"],
                    "source_family": src["source_family"],
                    "author_family": src["author_family"],
                    "author": src["author"],
                    "source_title": src["title"],
                    "source_url_or_identifier": src["url"],
                    "license": src["license"],
                    "theory_label": src["theory_label"],
                    "split": "true_final_holdout",
                    "acquisition_date": acquisition_date,
                    "verbatim_or_excerpt_status": "excerpt_paragraph",
                    "ai_generated": False,
                    "word_count": len(text.split()),
                    "sha256": sha,
                    "text": text,
                    "hard_negative_or_cross_theory_context": False,
                    "label_tag": "STANDARD",
                }
            )

    out_path = OUT / "passages.jsonl"
    out_path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    meta = {
        "n_passages": len(rows),
        "source_families": sorted({r["source_family"] for r in rows}),
        "acquisition": "wikisource_public_domain_html_parse",
        "acquired_at": acquisition_date,
        "note": "Acquired after method freeze under owner authorization; archive.org OCR unavailable (5xx).",
    }
    (OUT / "acquisition_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    avail_path = ROOT / "data/theory_validation_v2/final_holdout_candidates/candidate_availability.json"
    avail = json.loads(avail_path.read_text(encoding="utf-8"))
    acquired = {r["source_family"] for r in rows}
    for c in avail.get("candidates", []):
        if c.get("source_family") in acquired:
            c["status"] = "ACQUIRED"
            c["acquired_passages"] = sum(1 for r in rows if r["source_family"] == c["source_family"])
    avail_path.write_text(json.dumps(avail, indent=2) + "\n", encoding="utf-8")
    print("wrote", out_path, "n=", len(rows))


if __name__ == "__main__":
    main()
