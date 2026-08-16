"""Blinded export integrity checks — ensure working inputs lack tradition/author labels."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from rishiq.blinding import blind_corpus, detect_label_leaks
from rishiq.experiments import passages_from_parquet
from rishiq.models import Passage  # noqa: F401 — type clarity for audits

EXTRA_LEAKS = [
    re.compile(r"\bvai[sś]e[sṣ]ika\b", re.I),
    re.compile(r"\bka[nṇ][aā]da\b", re.I),
    re.compile(r"\b[aā]k[aā][sś]a\b", re.I),
    re.compile(r"\bindia\b", re.I),
    re.compile(r"\bsanskrit\b", re.I),
    re.compile(r"\bveda\b", re.I),
    re.compile(r"\blucretius\b", re.I),
    re.compile(r"\btimaeus\b", re.I),
    re.compile(r"\bmaxwell\b", re.I),
]


def detect_extended_leaks(text: str) -> list[str]:
    hits = detect_label_leaks(text)
    for pat in EXTRA_LEAKS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


from rishiq.isef2027.scrub import scrub_text


def audit_blinded_export(passages: list[Passage], salt: str = "rishiq-isef2027", *, apply_scrub: bool = True) -> dict[str, Any]:
    # Work on copies with scrubbed translation text for the blind payload
    working: list[Passage] = []
    scrub_hits = 0
    for p in passages:
        text = p.translation or p.source_text
        if apply_scrub:
            sr = scrub_text(text)
            scrub_hits += sr.n_replacements
            text = sr.text
        working.append(p.model_copy(update={"translation": text}))

    blinded, mapping = blind_corpus(working, salt=salt, mapping_path=None)
    issues = []
    for b in blinded:
        leaks = detect_extended_leaks(b.text)
        if b.anonymous_id in b.text:
            issues.append({"type": "anon_id_in_text", "id": b.anonymous_id})
        if leaks:
            issues.append({"type": "label_leak_in_blind_text", "id": b.anonymous_id, "patterns": leaks})
    true_ids = set(mapping.values())
    for b in blinded:
        for tid in true_ids:
            if tid and tid in b.text:
                issues.append({"type": "true_id_in_blind_text", "id": b.anonymous_id, "true_id": tid})

    return {
        "n_passages": len(passages),
        "n_blinded": len(blinded),
        "scrub_replacements_total": scrub_hits,
        "apply_scrub": apply_scrub,
        "n_issues": len(issues),
        "issues_sample": issues[:50],
        "status": "FAIL" if issues else "PASS",
        "mapping_kept_separate": True,
        "note": "Unblinding key must remain private and off working annotation inputs.",
    }


def run_blind_audit(root: Path) -> dict[str, Any]:
    pq = root / "corpus/development/pd_passages.parquet"
    report: dict[str, Any]
    if not pq.exists():
        report = {"status": "SKIP", "reason": "missing pd_passages.parquet"}
    else:
        passages = list(passages_from_parquet(pq)[:40])
        try:
            report = audit_blinded_export(passages)
            blinded, _mapping = blind_corpus(
                passages[:20],
                salt="rishiq-isef2027",
                mapping_path=root / "results/isef2027/dev/blind_mapping.PRIVATE.json",
            )
            export = root / "results/isef2027/dev/blinded_sample.json"
            export.write_text(
                json.dumps([b.model_dump() for b in blinded], indent=2) + "\n",
                encoding="utf-8",
            )
            report["blinded_sample"] = str(export.relative_to(root))
            report["private_mapping"] = "results/isef2027/dev/blind_mapping.PRIVATE.json"
        except Exception as e:
            report = {"status": "ERROR", "error": str(e)}

    dirty = "This Vaiśeṣika passage from India cites Maxwell and the Veda."
    report["dirty_text_leak_patterns"] = detect_extended_leaks(dirty)
    report["dirty_text_detected"] = bool(report["dirty_text_leak_patterns"])

    out = root / "results/isef2027/dev/blind_audit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
