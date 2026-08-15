"""Source-label blinding for annotation inputs."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from rishiq.models import BlindedPassage, Passage

LEAKY_PATTERNS = [
    re.compile(r"\bupani[sṣ]ad\b", re.I),
    re.compile(r"\bved[aā]nta\b", re.I),
    re.compile(r"\bbhagavad\b", re.I),
    re.compile(r"\bquantum\b", re.I),
    re.compile(r"\bch[aā]ndogya\b", re.I),
    re.compile(r"\bb[rṛ]had[aā]ra[nṇ]yaka\b", re.I),
]


def anonymous_id(passage_id: str, salt: str = "rishiq-blind-v1") -> str:
    digest = hashlib.sha256(f"{salt}:{passage_id}".encode()).hexdigest()[:10]
    return f"PASSAGE_{digest}"


def strip_metadata_text(text: str) -> str:
    """Remove common editorial markers; conservative."""
    lines = []
    for line in text.splitlines():
        if line.strip().lower().startswith(("commentary:", "editor:", "note:")):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def blind_passage(passage: Passage, salt: str = "rishiq-blind-v1") -> BlindedPassage:
    text = strip_metadata_text(passage.translation or passage.source_text)
    return BlindedPassage(
        anonymous_id=anonymous_id(passage.passage_id, salt=salt),
        text=text,
        source_language=passage.source_language,
        word_count=len(text.split()),
        prompt_safe=True,
    )


def blind_corpus(
    passages: list[Passage],
    *,
    salt: str = "rishiq-blind-v1",
    mapping_path: str | Path | None = None,
) -> tuple[list[BlindedPassage], dict[str, str]]:
    blinded: list[BlindedPassage] = []
    mapping: dict[str, str] = {}
    for p in passages:
        b = blind_passage(p, salt=salt)
        blinded.append(b)
        mapping[b.anonymous_id] = p.passage_id
    if mapping_path is not None:
        path = Path(mapping_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(mapping, indent=2, sort_keys=True), encoding="utf-8")
    return blinded, mapping


def detect_label_leaks(text: str) -> list[str]:
    return [pat.pattern for pat in LEAKY_PATTERNS if pat.search(text)]
