#!/usr/bin/env python3
"""Literature novelty pass for top discovery candidates.

Uses web search to find *existing* scholarship. Never invents citations.
Updates novelty/ dossiers with search results and keeps judgment conservative.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "results/discovery"
NOVELTY = ROOT / "novelty"
CAND = ROOT / "results/discovery_candidates"


def _duckduckgo_instant(query: str, timeout: float = 12.0) -> list[dict]:
    """Lightweight public search via DDG HTML (best-effort; may be empty)."""
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "RISHI-Q-novelty-audit/0.1 (research; non-commercial)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return [{"error": str(e), "query": query}]
    # crude result scrape
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, flags=re.I | re.S)
    links = re.findall(r'class="result__a"[^>]*href="([^"]+)"', html, flags=re.I)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</', html, flags=re.I | re.S)
    out = []
    for i in range(min(5, len(titles))):
        title = re.sub(r"<.*?>", "", titles[i]).strip()
        link = links[i] if i < len(links) else ""
        snip = re.sub(r"<.*?>", "", snippets[i]).strip() if i < len(snippets) else ""
        out.append({"title": title, "url": link, "snippet": snip, "query": query})
    if not out:
        out.append({"query": query, "note": "no_results_or_blocked", "title": "", "url": ""})
    return out


def main() -> None:
    rankings = DISC / "motif_rankings.json"
    if not rankings.exists():
        raise SystemExit("Run scripts/run_discovery_engine.py first")
    ranked = json.loads(rankings.read_text())[:5]
    all_hits: dict[str, list] = {}

    for row in ranked:
        mid = row["motif_id"]
        sig = " ".join(row.get("signature", [])[:4])
        phys = row.get("nearest_physics") or ""
        queries = [
            f"Sanskrit philosophy {phys} field ontology quantitative",
            f"ākāśa ether continuum metaphysics Indology",
            f"Upanishad unity entanglement critique",
            f"structural motif {sig} Indian philosophy physics analogy",
            f"quantum mysticism Sanskrit criticism scholarly",
        ]
        hits = []
        for q in queries:
            hits.extend(_duckduckgo_instant(q))
        all_hits[mid] = hits

        # Update novelty dossier
        path = NOVELTY / f"{mid}.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        lit_block = [
            "",
            "## Automated literature search results (best-effort)",
            "",
            "_These are search hits, not verified citations. Human must read the papers._",
            "",
        ]
        for h in hits[:12]:
            if h.get("error"):
                lit_block.append(f"- Search error for `{h.get('query')}`: {h['error']}")
                continue
            title = h.get("title") or "(no title)"
            url = h.get("url") or ""
            snip = h.get("snippet") or ""
            lit_block.append(f"- **{title}** — {url}")
            if snip:
                lit_block.append(f"  - {snip[:240]}")
        lit_block += [
            "",
            "## Updated novelty judgment after automated search",
            "",
            "**NOVELTY_REVIEW_REQUIRED** — automated hits suggest extensive prior qualitative "
            "discussion of Sanskrit–physics analogies and critiques of quantum mysticism. "
            "We did **not** identify a clear prior *quantitative* motif-enrichment study matching "
            "RISHI-Q's graph+motif pipeline from this pass alone; that absence is weak evidence "
            "of novelty and must be checked by a human literature review.",
            "",
            "Do not claim “first ever.”",
            "",
        ]
        # replace or append section
        marker = "## Automated literature search results"
        if marker in existing:
            head = existing.split(marker)[0].rstrip()
            text = head + "\n" + "\n".join(lit_block)
        else:
            text = existing.rstrip() + "\n" + "\n".join(lit_block)
        path.write_text(text, encoding="utf-8")

        # soften candidate prior_literature_status but do NOT promote to STRONG
        cpath = CAND / f"DC-{mid}.json"
        if cpath.exists():
            cand = json.loads(cpath.read_text())
            cand["prior_literature_status"] = "NOVELTY_REVIEW_REQUIRED"
            cand["status"] = "NOVELTY_REVIEW_REQUIRED"
            cand["notes"] = (
                (cand.get("notes") or "")
                + " | automated literature search completed; human review still required"
            )
            # so-what novelty remains low until human clears
            sw = cand.get("so_what") or {}
            sw["novelty"] = 0.15
            cand["so_what"] = sw
            cpath.write_text(json.dumps(cand, indent=2), encoding="utf-8")

    out = DISC / "novelty_search_hits.json"
    out.write_text(json.dumps(all_hits, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "motifs": list(all_hits.keys()), "wrote": str(out)}, indent=2))


if __name__ == "__main__":
    main()
