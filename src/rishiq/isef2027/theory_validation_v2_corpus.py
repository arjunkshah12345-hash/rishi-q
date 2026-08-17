"""Build external theory-validation corpus v2 with source-grouped splits."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from rishiq.isef2027.contamination import ContaminationState, EvidenceRole
from rishiq.isef2027.source_eligibility import PRESPECIFIED_SOURCES, write_eligibility_manifest
from rishiq.isef2027.source_families import annotate_row, assert_no_family_overlap

THEORIES = [
    "newtonian",
    "thermodynamics",
    "classical_em",
    "relativity",
    "quantum_mechanics",
    "quantum_field_theory",
    "atomistic_corpuscular",
]

# Family-clean DEVELOPMENT splits (no source_family overlap train↔dev).
# Former final_holdout is demoted to constructed_unevaluated — NOT a pristine holdout.
# True FINAL_METHOD_HOLDOUT is NOT built in this pass (see docs).
WORK_SPLIT_PLAN: dict[str, str] = {
    # TRAIN — OpenStax family entirely here; Maxwell author entirely here
    "newton_opticks": "train",
    "carnot_motive_power": "train",
    "maxwell_treatise_em_v1": "train",
    "maxwell_elementary_electricity": "train",
    "maxwell_theory_of_heat": "train",
    "faraday_experimental_v1": "train",
    "lucretius_drn": "train",
    "einstein_relativity_popular": "train",
    "openstax_university-physics-volume-1": "train",
    "openstax_university-physics-volume-2": "train",
    "openstax_university-physics-volume-3": "train",
    # DEVELOPMENT — Wikipedia family entirely here; no OpenStax / Maxwell
    "thomson_tait_np": "development",
    "clausius_mechanical_heat": "development",
    "dalton_chemical_philosophy": "development",
    "huygens_light": "development",
    "tesla_high_frequency": "development",
    "wikipedia_qft": "development",
    "wikipedia_qed": "development",
    "wikipedia_particle": "development",
    "wikipedia_qm": "development",
    "wikipedia_sr": "development",
    "wikipedia_gr": "development",
    "wikipedia_thermo": "development",
    "wikipedia_cm": "development",
    "wikipedia_maxwell": "development",
    "wikipedia_atomism": "development",
}

# Historical constructed set (former final_holdout content) — demoted, not rebuilt as true holdout
CONSTRUCTED_UNEVALUATED_WORKS: set[str] = {
    "clausius_mechanical_heat",
    "tesla_high_frequency",
    "openstax_university-physics-volume-3",
    "wikipedia_maxwell",
    "wikipedia_qft",
    "wikipedia_thermo",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strip_gutenberg(text: str) -> str:
    start = re.search(r"\*\*\*\s*START OF.*?\*\*\*", text, re.I)
    end = re.search(r"\*\*\*\s*END OF.*?\*\*\*", text, re.I)
    if start:
        text = text[start.end() :]
    if end:
        text = text[: end.start()]
    return text.strip()


def _paragraphs(text: str, *, min_w: int = 40, max_w: int = 220) -> list[str]:
    chunks = re.split(r"\n\s*\n+", text)
    out: list[str] = []
    for c in chunks:
        c = re.sub(r"\s+", " ", c).strip()
        if len(c) < 20:
            continue
        # drop likely TOC / page-number garbage
        if re.fullmatch(r"[\d\sivxlcdmIVXLCDM.\- ]{1,40}", c):
            continue
        words = c.split()
        if len(words) < min_w:
            continue
        if len(words) > max_w:
            sents = re.split(r"(?<=[.!?])\s+", c)
            buf: list[str] = []
            for s in sents:
                buf.append(s)
                if len(" ".join(buf).split()) >= 60:
                    out.append(" ".join(buf).strip())
                    buf = []
            if buf and len(" ".join(buf).split()) >= min_w:
                out.append(" ".join(buf).strip())
            continue
        out.append(c)
    return out


def _hard_negative_flag(text: str, theory: str) -> bool:
    """Heuristic: passage mentions neighboring-theory vocabulary."""
    t = text.lower()
    cross = {
        "newtonian": ["entropy", "electromagnetic", "quantum", "relativity", "spacetime"],
        "thermodynamics": ["quantum", "photon", "relativity", "maxwell equation"],
        "classical_em": ["photon", "quantum", "relativity", "entropy"],
        "relativity": ["newton", "quantum", "photon", "entropy"],
        "quantum_mechanics": ["classical limit", "maxwell", "newtonian", "thermodynamic"],
        "quantum_field_theory": ["classical electromagnetism", "maxwell", "newton"],
        "atomistic_corpuscular": ["quantum", "relativity", "electromagnetic field"],
    }
    return any(k in t for k in cross.get(theory, []))


def _openstax_theory(page: str, hint: str | None, book: str) -> str:
    s = (page or "").lower()
    if re.match(r"^11-", s) or any(
        k in s for k in ("particle-physics", "quark", "standard-model", "gauge", "boson")
    ):
        return "quantum_field_theory"
    if "relativ" in s or "special-relativity" in s or "general-relativity" in s:
        return "relativity"
    if "quantum-field" in s or "standard-model" in s:
        return "quantum_field_theory"
    if any(
        k in s
        for k in (
            "quantum",
            "photoelectric",
            "bohr",
            "wave-function",
            "schrodinger",
            "heisenberg",
            "spin",
            "uncertainty",
            "wave-particle",
            "tunneling",
            "harmonic-oscillator",
        )
    ):
        return "quantum_mechanics"
    if any(k in s for k in ("thermo", "entropy", "heat", "kinetic-theory", "ideal-gas")):
        return "thermodynamics"
    if any(
        k in s
        for k in (
            "electric",
            "magnetic",
            "maxwell",
            "circuit",
            "capacit",
            "induct",
            "electromagnetic",
            "optics",
            "light",
            "wave",
        )
    ):
        return "classical_em"
    if any(k in s for k in ("atom", "nucleus", "radioactiv", "rutherford", "nuclear")):
        return "atomistic_corpuscular"
    if hint and hint in THEORIES:
        return hint
    if "volume-3" in book:
        return "quantum_mechanics"
    if "volume-2" in book:
        return "classical_em"
    return "newtonian"


def _passages_from_raw_book(root: Path, spec: dict[str, Any], max_passages: int = 80) -> list[dict[str, Any]]:
    raw_dir = root / "data/theory_validation_v2/raw"
    path = raw_dir / spec["raw_file"]
    if not path.exists() or path.stat().st_size < 1000:
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "gutenberg" in spec.get("license", "").lower() or "START OF" in text[:2000]:
        text = _strip_gutenberg(text)
    paras = _paragraphs(text)
    # Stable subsample: take evenly spaced paragraphs to avoid only front-matter
    if len(paras) > max_passages:
        step = len(paras) / max_passages
        paras = [paras[int(i * step)] for i in range(max_passages)]
    work_id = spec["work_id"]
    split = WORK_SPLIT_PLAN.get(work_id, "development")
    theory = spec["theory_label"]
    rows = []
    for i, p in enumerate(paras):
        hard = _hard_negative_flag(p, theory)
        rows.append(
            {
                "passage_id": f"{work_id}-{i:04d}",
                "theory_label": theory,
                "source_title": spec["source_title"],
                "source_author": spec["source_author"],
                "source_year": spec["source_year"],
                "source_url_or_identifier": spec["source_url_or_identifier"],
                "license": spec["license"],
                "source_type": spec["source_type"],
                "chapter_or_section": "unknown_ocr_paragraph",
                "page_if_available": None,
                "verbatim_or_excerpt_status": "excerpt_paragraph",
                "word_count": len(p.split()),
                "acquisition_date": str(date.today()),
                "sha256": sha256_text(p),
                "split": split,
                "work_id": work_id,
                "author_family": spec["author_family"],
                "source_id": spec["source_id"],
                "text": p,
                "hard_negative_or_cross_theory_context": hard,
                "label_tag": "HARD_NEGATIVE_OR_CROSS_THEORY_CONTEXT" if hard else "STANDARD",
                "ai_generated": False,
            }
        )
    return rows


def _passages_from_wikipedia(root: Path, max_passages: int = 40) -> list[dict[str, Any]]:
    """CC BY-SA encyclopedia articles — theory from article topic, not classifier scores.

    All Wikipedia physics pages share source_family=wikipedia_physics and must
    occupy a single split (see WORK_SPLIT_PLAN).
    """
    wiki_dir = root / "data/theory_validation_v2/raw/wikipedia"
    catalog = [
        ("quantum_field_theory.txt", "quantum_field_theory", "Quantum field theory", "wikipedia_qft"),
        ("quantum_electrodynamics.txt", "quantum_field_theory", "Quantum electrodynamics", "wikipedia_qed"),
        ("particle_physics.txt", "quantum_field_theory", "Particle physics", "wikipedia_particle"),
        ("quantum_mechanics.txt", "quantum_mechanics", "Quantum mechanics", "wikipedia_qm"),
        ("special_relativity.txt", "relativity", "Special relativity", "wikipedia_sr"),
        ("general_relativity.txt", "relativity", "General relativity", "wikipedia_gr"),
        ("thermodynamics.txt", "thermodynamics", "Thermodynamics", "wikipedia_thermo"),
        ("classical_mechanics.txt", "newtonian", "Classical mechanics", "wikipedia_cm"),
        ("maxwells_equations.txt", "classical_em", "Maxwell's equations", "wikipedia_maxwell"),
        ("atomism.txt", "atomistic_corpuscular", "Atomism", "wikipedia_atomism"),
    ]
    rows: list[dict[str, Any]] = []
    for fname, theory, title, work_id in catalog:
        path = wiki_dir / fname
        if not path.exists() or path.stat().st_size < 500:
            continue
        split = WORK_SPLIT_PLAN.get(work_id, "development")
        text = path.read_text(encoding="utf-8", errors="ignore")
        paras = _paragraphs(text, min_w=50, max_w=200)
        if len(paras) > max_passages:
            step = len(paras) / max_passages
            paras = [paras[int(i * step)] for i in range(max_passages)]
        for i, p in enumerate(paras):
            hard = _hard_negative_flag(p, theory)
            rows.append(
                {
                    "passage_id": f"{work_id}-{i:04d}",
                    "theory_label": theory,
                    "source_title": title,
                    "source_author": "Wikipedia contributors",
                    "source_year": 2026,
                    "source_url_or_identifier": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    "license": "CC BY-SA 4.0",
                    "source_type": "wikipedia_cc",
                    "chapter_or_section": "article_body",
                    "page_if_available": None,
                    "verbatim_or_excerpt_status": "excerpt_paragraph",
                    "word_count": len(p.split()),
                    "acquisition_date": str(date.today()),
                    "sha256": sha256_text(p),
                    "split": split,
                    "work_id": work_id,
                    "author_family": "wikipedia_contributors",
                    "source_id": work_id,
                    "text": p,
                    "hard_negative_or_cross_theory_context": hard,
                    "label_tag": "HARD_NEGATIVE_OR_CROSS_THEORY_CONTEXT" if hard else "STANDARD",
                    "ai_generated": False,
                }
            )
    return rows


def _passages_from_openstax(root: Path, fname: str, work_id: str, book: str, max_per_chapter: int = 3) -> list[dict[str, Any]]:
    path = root / "data/theory_validation_v2/raw" / fname
    if not path.exists():
        return []
    split = WORK_SPLIT_PLAN.get(work_id, "development")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ch = json.loads(line)
        theory = _openstax_theory(ch.get("page", ""), ch.get("theory_label_hint"), book)
        text = ch["text"]
        words = text.split()
        windows = []
        win, step = 120, 100
        if len(words) <= win:
            windows = [" ".join(words)]
        else:
            for start in range(0, len(words) - 40, step):
                windows.append(" ".join(words[start : start + win]))
                if len(windows) >= max_per_chapter:
                    break
        for i, w in enumerate(windows):
            if len(w.split()) < 40:
                continue
            hard = _hard_negative_flag(w, theory)
            pid = f"{work_id}-{ch.get('page','p')}-{i:02d}"
            rows.append(
                {
                    "passage_id": pid,
                    "theory_label": theory,
                    "source_title": f"OpenStax University Physics ({book})",
                    "source_author": "OpenStax contributors",
                    "source_year": 2022,
                    "source_url_or_identifier": ch.get("url", f"openstax:{book}:{ch.get('page')}"),
                    "license": "CC BY 4.0",
                    "source_type": "open_textbook",
                    "chapter_or_section": ch.get("page"),
                    "page_if_available": None,
                    "verbatim_or_excerpt_status": "excerpt_window",
                    "word_count": len(w.split()),
                    "acquisition_date": str(date.today()),
                    "sha256": sha256_text(w),
                    "split": split,
                    "work_id": work_id,
                    "author_family": "openstax",
                    "source_id": f"openstax_{book}",
                    "text": w,
                    "hard_negative_or_cross_theory_context": hard,
                    "label_tag": "HARD_NEGATIVE_OR_CROSS_THEORY_CONTEXT" if hard else "STANDARD",
                    "ai_generated": False,
                }
            )
    return rows


def assert_no_work_overlap(rows: list[dict[str, Any]]) -> list[str]:
    by_split: dict[str, set[str]] = {}
    for r in rows:
        by_split.setdefault(r["split"], set()).add(r["work_id"])
    issues = []
    splits = list(by_split)
    for i, a in enumerate(splits):
        for b in splits[i + 1 :]:
            inter = by_split[a] & by_split[b]
            if inter:
                issues.append(f"work_overlap {a}∩{b}: {sorted(inter)}")
    return issues


def demote_constructed_unevaluated_holdout(root: Path) -> dict[str, Any]:
    """Rename scientific status of the former final holdout; preserve hashes/files.

    Does NOT delete passages or rewrite sha256 history. True pristine holdout is NOT_BUILT.
    """
    hold_dir = root / "data/theory_validation_v2/final_holdout"
    lock_path = hold_dir / "lock_manifest.json"
    if not lock_path.exists():
        return {"status": "MISSING_PRIOR_HOLDOUT"}
    prior = json.loads(lock_path.read_text(encoding="utf-8"))
    prior_status = prior.get("status")
    prior["prior_status"] = prior_status
    prior["status"] = "CONSTRUCTED_UNEVALUATED_VALIDATION_SET"
    prior["scientific_status"] = "CONSTRUCTED_UNEVALUATED_VALIDATION_SET"
    prior["contamination_state"] = ContaminationState.DEVELOPMENT_CONTAMINATED.value
    prior["evidence_role"] = EvidenceRole.EXTERNAL_METHOD_DEVELOPMENT.value
    prior["evaluated"] = False
    prior["true_final_method_holdout"] = "NOT_BUILT"
    prior["demotion_note"] = (
        "Labels and texts were committed before family-clean splits; "
        "source-family overlap existed vs train/dev. Preserved for history; "
        "not pristine unseen final evidence. Do not evaluate as final method holdout."
    )
    # Preserve historical passage hash fields under explicit names
    if "holdout_passages_sha256" in prior:
        prior["constructed_passages_sha256"] = prior["holdout_passages_sha256"]
    lock_path.write_text(json.dumps(prior, indent=2) + "\n", encoding="utf-8")

    # Mirror status marker for discoverability (do not rewrite passage files)
    marker = hold_dir / "SCIENTIFIC_STATUS.json"
    marker.write_text(
        json.dumps(
            {
                "status": "CONSTRUCTED_UNEVALUATED_VALIDATION_SET",
                "true_final_method_holdout": "NOT_BUILT",
                "evaluated": False,
                "preserved_lock": str(lock_path.relative_to(root)),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return prior


def build_external_theory_corpus(root: Path) -> dict[str, Any]:
    write_eligibility_manifest(root)
    rows: list[dict[str, Any]] = []
    for spec in PRESPECIFIED_SOURCES:
        rows.extend(_passages_from_raw_book(root, spec))

    rows.extend(
        _passages_from_openstax(
            root,
            "openstax_up_v1_chapters.jsonl",
            "openstax_university-physics-volume-1",
            "university-physics-volume-1",
        )
    )
    rows.extend(
        _passages_from_openstax(
            root,
            "openstax_up_v2_chapters.jsonl",
            "openstax_university-physics-volume-2",
            "university-physics-volume-2",
        )
    )
    rows.extend(
        _passages_from_openstax(
            root,
            "openstax_up_v3_chapters.jsonl",
            "openstax_university-physics-volume-3",
            "university-physics-volume-3",
            max_per_chapter=4,
        )
    )
    rows.extend(_passages_from_wikipedia(root))

    # Canonical family fields (do not invent volume/article-level families)
    rows = [annotate_row(r) for r in rows]

    # Active development corpus: train + development only (no true final holdout)
    active = [r for r in rows if r["split"] in ("train", "development")]
    issues = assert_no_work_overlap(active)
    if issues:
        raise RuntimeError("source split leakage: " + "; ".join(issues))
    fam_issues = assert_no_family_overlap(active, "source_family")
    hard_fam = [x for x in fam_issues if x.startswith("HARD_")]
    if hard_fam:
        raise RuntimeError("source_family split leakage: " + "; ".join(hard_fam))
    author_issues = assert_no_family_overlap(active, "author_family")

    out_dir = root / "data/theory_validation_v2/passages"
    out_dir.mkdir(parents=True, exist_ok=True)

    all_path = out_dir / "corpus_external_v2.jsonl"
    with all_path.open("w", encoding="utf-8") as f:
        for r in active:
            f.write(json.dumps(r) + "\n")

    for split_name, fname in [
        ("train", "train.jsonl"),
        ("development", "development.jsonl"),
    ]:
        subset = [r for r in active if r["split"] == split_name]
        with (out_dir / fname).open("w", encoding="utf-8") as f:
            for r in subset:
                f.write(json.dumps(r) + "\n")

    # Do not materialize a new final_holdout from this rebuild.
    # Empty placeholder documents that true holdout is NOT_BUILT — unless already built/evaluated.
    (out_dir / "final_holdout_TEXTS_LOCKED.jsonl").write_text("", encoding="utf-8")
    status_path = out_dir / "TRUE_FINAL_HOLDOUT_STATUS.json"
    existing_hold = {}
    if status_path.exists():
        try:
            existing_hold = json.loads(status_path.read_text(encoding="utf-8"))
        except Exception:
            existing_hold = {}
    existing_status = existing_hold.get("status")
    if existing_status in {"BUILT_UNEVALUATED", "EVALUATED_ONCE_AFTER_METHOD_FREEZE"}:
        # Preserve post-freeze true holdout status; corpus rebuild must not wipe it.
        pass
    else:
        status_path.write_text(
            json.dumps(
                {
                    "status": "NOT_BUILT",
                    "reason": "True final method holdout may be built only AFTER student method freeze.",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    demoted = demote_constructed_unevaluated_holdout(root)

    corpus_hash = sha256_text("".join(sorted(r["sha256"] for r in active)))
    constructed_hash = demoted.get("constructed_passages_sha256") or demoted.get("holdout_passages_sha256")

    train_sf = sorted({r["source_family"] for r in active if r["split"] == "train"})
    dev_sf = sorted({r["source_family"] for r in active if r["split"] == "development"})
    train_af = sorted({r["author_family"] for r in active if r["split"] == "train"})
    dev_af = sorted({r["author_family"] for r in active if r["split"] == "development"})

    meta = {
        "corpus_id": "theory_validation_external_v2_family_clean",
        "evidence_role": EvidenceRole.EXTERNAL_METHOD_DEVELOPMENT.value,
        "n_passages": len(active),
        "n_works": len({r["work_id"] for r in active}),
        "n_authors": len({r["author_family"] for r in active}),
        "n_source_families": len({r["source_family"] for r in active}),
        "theories": THEORIES,
        "per_theory": {t: sum(1 for r in active if r["theory_label"] == t) for t in THEORIES},
        "splits": {
            s: {
                "n": sum(1 for r in active if r["split"] == s),
                "works": sorted({r["work_id"] for r in active if r["split"] == s}),
                "authors": sorted({r["author_family"] for r in active if r["split"] == s}),
                "source_families": sorted({r["source_family"] for r in active if r["split"] == s}),
            }
            for s in ("train", "development")
        },
        "source_family_overlap_train_dev": sorted(set(train_sf) & set(dev_sf)),
        "author_family_overlap_train_dev": sorted(set(train_af) & set(dev_af)),
        "work_overlap_issues": issues,
        "source_family_issues": fam_issues,
        "author_family_issues": author_issues,
        "hard_negative_n": sum(1 for r in active if r["hard_negative_or_cross_theory_context"]),
        "corpus_hash": corpus_hash,
        "constructed_unevaluated_hash": constructed_hash,
        "true_final_method_holdout": "NOT_BUILT",
        "constructed_unevaluated_status": demoted.get("status"),
        "note": (
            "Family-clean train/development only. Former final holdout demoted to "
            "CONSTRUCTED_UNEVALUATED_VALIDATION_SET. True final holdout NOT_BUILT."
        ),
    }
    (out_dir / "corpus_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    freeze = {
        "artifact": "theory_validation_v2_freeze",
        "corpus_hash": corpus_hash,
        "constructed_unevaluated_hash": constructed_hash,
        "true_final_method_holdout": "NOT_BUILT",
        "eligibility_rules": "data/theory_validation_v2/eligibility/source_eligibility_v1.json",
        "method_frozen": False,
        "final_holdout_evaluated": False,
        "created": str(date.today()),
    }
    freeze_path = root / "artifacts/isef2027/theory_validation_v2_freeze.json"
    freeze_path.write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")
    return meta
