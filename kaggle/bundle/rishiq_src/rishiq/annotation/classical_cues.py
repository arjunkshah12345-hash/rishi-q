"""Classical natural-philosophy English cues (instrument v0.2).

Purpose: reduce floor-effect on Lucretius-style atomism / continuum English.
Derived from classical physics/atomism language — NOT from tuning to raise Sanskrit QS.

Hard rule preserved: unity/interconnection still must NOT set Q06=1.
"""

from __future__ import annotations

import re

# Additive cues for Level I/II classical natural philosophy in English translations.
CLASSICAL_NP_CUES: dict[str, list[re.Pattern[str]]] = {
    "O01": [
        re.compile(r"\b(first[- ]beginnings|primordial|underlying (nature|substance))\b", re.I),
        re.compile(r"\bthat from which (all )?(things|beings) (arise|come|spring)\b", re.I),
    ],
    "O02": [
        re.compile(r"\b(atoms?|corpuscles?|seeds of things|first bodies)\b", re.I),
        re.compile(r"\bcomposed of|made up of|aggregat\w+\b", re.I),
    ],
    "O03": [
        re.compile(r"\bindivisible\b|\bcannot be (cut|split|divided)\b|\bvoid and atoms\b", re.I),
        re.compile(r"\bsmallest (bodies|parts|particles)\b", re.I),
    ],
    "O04": [
        re.compile(r"\b(void|vacuum|empty space)\b", re.I),
        re.compile(r"\bcontinuous (nature|substance|medium)\b", re.I),
    ],
    "D02": [
        re.compile(r"\b(come into being|pass away|arise and perish|transformation)\b", re.I),
    ],
    "D04": [
        re.compile(r"\b(motion through|travels? through|diffuse[sd]? through)\b", re.I),
    ],
    "R01": [
        re.compile(r"\b(collision|blow|impact|contact) of (atoms|bodies)\b", re.I),
    ],
    "F01": [
        re.compile(r"\bpervade[sd]?\b|\bfills? (all )?space\b|\bextended through\b", re.I),
    ],
    "M03": [
        re.compile(r"\bbeyond (our )?ken\b|\bcannot (be )?perceive\b|\bhidden from (the )?senses\b", re.I),
    ],
}
