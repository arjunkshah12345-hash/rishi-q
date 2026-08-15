"""Level I metaphysical English cues (instrument v0.3).

Purpose: detect substrate/unity/manifestation language in philosophical English
translations WITHOUT any quantum-family cues.

Hard rules preserved:
- unity / oneness / Brahman-as-one MUST NOT set Q06
- no mystical→quantum shortcuts
"""

from __future__ import annotations

import re

METAPHYSICAL_CUES: dict[str, list[re.Pattern[str]]] = {
    "O01": [
        re.compile(r"\b(brahman|atman|absolute|supreme (self|reality|being)|ultimate reality)\b", re.I),
        re.compile(r"\bthe (one|infinite|unchanging) (reality|self|ground)\b", re.I),
        re.compile(r"\bunderlying (self|reality|being|principle)\b", re.I),
    ],
    "O02": [
        re.compile(r"\b(part and whole|whole and (its )?parts|higher self|lower self)\b", re.I),
        re.compile(r"\b(rooted above|branches downward|tree of creation)\b", re.I),
    ],
    "O04": [
        re.compile(r"\b(all[- ]pervad\w+|omnipresent|fills? (all|the) (space|world))\b", re.I),
        re.compile(r"\b(ether|akasha|ākāśa|space itself)\b", re.I),
    ],
    "O05": [
        re.compile(r"\b(manifests?|manifestation|appears? as|phenomenal world)\b", re.I),
        re.compile(r"\b(names? and forms?|nama[- ]rupa)\b", re.I),
    ],
    "D02": [
        re.compile(r"\b(birth and death|mortal and immortal|becoming|samsara)\b", re.I),
        re.compile(r"\b(change|changing conditions|impermanent)\b", re.I),
    ],
    "F01": [
        re.compile(r"\b(pervad\w+|all[- ]pervad\w+|present in all)\b", re.I),
    ],
    "M03": [
        re.compile(r"\b(beyond (all )?human conception|ineffable|cannot be (defined|spoken))\b", re.I),
        re.compile(r"\b(unknown|unknowable) to (the )?senses\b", re.I),
    ],
}
