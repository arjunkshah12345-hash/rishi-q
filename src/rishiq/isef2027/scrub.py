"""Aggressive text scrubbing for blinded annotation inputs."""

from __future__ import annotations

import re
from dataclasses import dataclass


# Tradition / author / geography / school markers (annotation-side leakage)
SCRUB_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("tradition_vaisesika", re.compile(r"\bvai[sś]e[sṣ]ika\b", re.I)),
    ("author_kanada", re.compile(r"\bka[nṇ][aā]da\b", re.I)),
    ("term_akasa", re.compile(r"\b[aā]k[aā][sś]a\b", re.I)),
    ("term_sabda", re.compile(r"\b[sś]abda\b", re.I)),
    ("geo_india", re.compile(r"\b(india|indian|sanskrit|hindu|vedic|veda|vedānta|vedanta)\b", re.I)),
    ("work_upanishad", re.compile(r"\bupani[sṣ]ad\b", re.I)),
    ("work_gita", re.compile(r"\bbhagavad\b", re.I)),
    ("greek_names", re.compile(r"\b(lucretius|epicurus|plato|aristotle|timaeus|stoic|democritus)\b", re.I)),
    ("chinese_names", re.compile(r"\b(dao|tao|laozi|lao[- ]?tzu|confucius)\b", re.I)),
    ("buddhist_names", re.compile(r"\b(dhammapada|buddha|buddhist|abhidhamma|abhidharma)\b", re.I)),
    ("modern_physics_names", re.compile(r"\b(maxwell|einstein|newton|schr[oö]dinger|heisenberg|feynman|dirac)\b", re.I)),
    ("quantum_word", re.compile(r"\bquantum\b", re.I)),
]


@dataclass
class ScrubResult:
    text: str
    n_replacements: int
    patterns_hit: list[str]


def scrub_text(text: str, *, replacement: str = "[SCRUBBED]") -> ScrubResult:
    out = text
    hits: list[str] = []
    n = 0
    for name, pat in SCRUB_PATTERNS:
        if pat.search(out):
            hits.append(name)
            out, c = pat.subn(replacement, out)
            n += c
    # Strip editorial prefixes
    lines = []
    for line in out.splitlines():
        if line.strip().lower().startswith(("commentary:", "editor:", "note:", "translator:")):
            n += 1
            hits.append("editorial_line")
            continue
        lines.append(line)
    return ScrubResult(text="\n".join(lines).strip(), n_replacements=n, patterns_hit=sorted(set(hits)))
