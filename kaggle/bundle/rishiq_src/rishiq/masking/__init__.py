"""Physics vocabulary masking (auditable, reversible)."""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_VOCAB = [
    "energy",
    "field",
    "vibration",
    "frequency",
    "particle",
    "wave",
    "quantum",
    "dimension",
    "resonance",
    "information",
    "observer",
    "atom",
    "force",
    "electromagnetic",
    "photon",
    "electron",
    "spin",
    "entanglement",
    "superposition",
    "waveform",
]

NEUTRAL_MAP = {
    "energy": "pervasive principle",
    "field": "distributed entity",
    "vibration": "oscillatory change",
    "frequency": "rate of recurrence",
    "particle": "localized entity",
    "wave": "propagating disturbance",
    "quantum": "discrete unit",
    "dimension": "aspect",
    "resonance": "sympathetic response",
    "information": "structured content",
    "observer": "witnessing agent",
    "atom": "indivisible constituent",
    "force": "influence",
    "electromagnetic": "interaction-mediating",
    "photon": "light quantum-analogue term",
    "electron": "charged constituent",
    "spin": "intrinsic orientation",
    "entanglement": "nonseparable correlation",
    "superposition": "joint representation of alternatives",
    "waveform": "disturbance profile",
}


def load_vocab(path: str | Path | None = None) -> list[str]:
    if path is None:
        return list(DEFAULT_VOCAB)
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data["terms"])


def mask_text(text: str, vocab: list[str] | None = None) -> tuple[str, list[dict]]:
    vocab = vocab or DEFAULT_VOCAB
    edits: list[dict] = []
    out = text
    for term in sorted(vocab, key=len, reverse=True):
        pat = re.compile(rf"\b{re.escape(term)}\b", re.I)

        def repl(m: re.Match[str], term: str = term) -> str:
            edits.append({"start": m.start(), "end": m.end(), "original": m.group(0), "mode": "mask"})
            return "[MASKED]"

        out, n = pat.subn(repl, out)
    return out, edits


def neutralize_text(text: str, mapping: dict[str, str] | None = None) -> tuple[str, list[dict]]:
    mapping = mapping or NEUTRAL_MAP
    edits: list[dict] = []
    out = text
    for term, replacement in sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True):
        pat = re.compile(rf"\b{re.escape(term)}\b", re.I)

        def repl(m: re.Match[str], replacement: str = replacement, term: str = term) -> str:
            # preserve crude capitalization
            rep = replacement
            if m.group(0).istitle():
                rep = replacement[:1].upper() + replacement[1:]
            edits.append(
                {
                    "original": m.group(0),
                    "replacement": rep,
                    "mode": "neutralize",
                    "term": term,
                }
            )
            return rep

        out = pat.sub(repl, out)
    return out, edits


def make_variants(text: str) -> dict[str, dict]:
    masked, m_edits = mask_text(text)
    neut, n_edits = neutralize_text(text)
    return {
        "original": {"text": text, "edits": []},
        "masked": {"text": masked, "edits": m_edits},
        "neutralized": {"text": neut, "edits": n_edits},
    }
