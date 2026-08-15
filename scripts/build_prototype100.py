"""Build the protocol §95 ~100-passage development prototype.

Balanced across target-like, Indian controls, external controls, negative controls,
and modern-physics references. Synthetic / clearly licensed instrument text only.
NOT confirmatory. NOT cherry-picked for quantum resemblance.
"""

from __future__ import annotations

from pathlib import Path

from rishiq.experiments import passages_to_parquet, run_pipeline_on_passages
from rishiq.ingest.synthetic import modern_physics_passages, synthetic_philosophy_passages
from rishiq.models import DatasetSplit, Passage
from rishiq.provenance import sha256_text


ROOT = Path(__file__).resolve().parents[1]


def _p(passage_id: str, tradition: str, role: str, work: str, text: str, **kw) -> Passage:
    return Passage(
        passage_id=passage_id,
        tradition=tradition,
        school=kw.get("school", tradition),
        work=work,
        section=kw.get("section", ""),
        source_language=kw.get("source_language", "en"),
        translation=text,
        translation_style=kw.get("translation_style", "synthetic"),
        license_status="synthetic",
        dataset_split=DatasetSplit.DEVELOPMENT,
        role=role,
        genre=kw.get("genre", "philosophical"),
        topic=kw.get("topic", ""),
        source_hash=sha256_text(text),
        notes="100-passage prototype; instrument development only",
    )


# Templates deliberately mix Level I metaphors, Level II structure, atomism, and literary noise.
LEVEL_I = [
    "Everything is one beneath the play of appearances.",
    "All things are interconnected in a hidden unity.",
    "Consciousness witnesses the world and gives it meaning.",
    "Reality has a deeper layer than ordinary experience reveals.",
    "All forms change while the eternal remains.",
    "Invisible powers move through living beings.",
    "The many are expressions of the one.",
    "What is unseen is more real than what is seen.",
]

FIELD_LIKE = [
    "An underlying reality persists while visible forms change. Local forms appear within an all-pervading substrate.",
    "A continuous medium fills space. Different locations may possess different states of that medium.",
    "A disturbance travels through the medium. Localized observable phenomena arise from that distributed entity.",
    "Influences between bodies are mediated by an extended continuous entity present throughout a spatial region.",
    "A localized pulse is a dynamical disturbance of the medium that propagates through space over time.",
    "The broader substrate has localized manifestations that arise and dissolve while the substrate remains.",
]

ATOMISM = [
    "Bodies are aggregates of indivisible particles. Ultimate atoms cannot be further divided.",
    "Macroscopic objects are composed from more elementary entities that combine and separate.",
    "Motion belongs to particles; composite bodies inherit motion from their constituents.",
    "There are smallest units of matter that cannot be split further by natural processes.",
    "Qualities inhere in substances built from elementary constituents.",
]

LITERARY = [
    "The hero crossed the river at dawn and greeted the king with gifts.",
    "Spring flowers opened along the path where the poets walked.",
    "She sang of friendship and the duties of hospitality.",
    "The merchant counted coins and argued about the price of grain.",
    "Rain fell on the thatched roofs of the village for three nights.",
]

GREEKISH = [
    "Bodies are aggregates of indivisible particles moving in the void. Influences are transmitted through neighboring interactions.",
    "The cosmos is ordered by measure and proportion among elements.",
    "Change proceeds by recombination of enduring elementary constituents.",
    "Separated regions of the void do not themselves cause motion; atoms collide locally.",
]

CHINESEISH = [
    "The process of transformation never ceases; forms arise and return within a continuous ordering.",
    "Balance is maintained through complementary tendencies rather than a single fixed substance.",
    "What flows through the world is a pervasive pattern of change, not a countable set of atoms.",
    "Names and forms shift while the Way of transformation continues.",
]

BUDDHISTISH = [
    "Composite things are analyzed into momentary factors without an enduring substantial self.",
    "What appears solid is a heap of conditioned factors arising in dependence.",
    "No permanent substance underlies the stream of experiences.",
    "Causation proceeds through dependent arising rather than eternal atoms.",
]

JAINISH = [
    "Matter consists of ultimately minute constituents that combine into gross bodies.",
    "Souls and matter are distinct; material particles may bind according to rules of combination.",
    "Space provides room for substances without itself being a material atom.",
]

SPANDAISH = [
    "A dynamic throb underlies manifestation; forms appear as localized stirrings of that power.",
    "Creative power appears as vibration-like dynamism within consciousness, described metaphorically.",
]

RELATIVITY = (
    "Physical quantities such as velocity are defined relative to a reference body. "
    "The laws are unchanged under specified transformations of coordinates. "
    "We distinguish the measuring apparatus frame from the measured system's description. "
    "Influences are transmitted through neighboring interactions and do not require a preferred absolute rest."
)


def build_100() -> list[Passage]:
    out: list[Passage] = []
    out.extend(modern_physics_passages())
    out.append(
        _p(
            "PHYS_REL_001",
            "modern_physics",
            "physics_reference",
            "Synthetic relativity description",
            RELATIVITY,
            school="relativity",
            topic="relativity",
            translation_style="physics_reference",
            genre="physics",
        ).model_copy(update={"dataset_split": DatasetSplit.PHYSICS_CONTROL})
    )
    # Force dataset_split for physics already set in modern_physics_passages

    def add_many(prefix: str, tradition: str, role: str, work: str, texts: list[str], start: int = 1):
        for i, t in enumerate(texts, start=start):
            out.append(_p(f"{prefix}_{i:03d}", tradition, role, work, t, topic=prefix.lower()))

    # ~20 target-like (Vedanta-ish Level I + field-like + spanda) — not cherry-picked quantum
    add_many("TGT_VED", "vedanta_synthetic", "target", "Synthetic Vedanta-like panel", LEVEL_I[:8] + FIELD_LIKE[:6] + SPANDAISH)
    # ~20 Vaisheshika-like atomism
    add_many("TGT_VAI", "vaisheshika_synthetic", "target", "Synthetic Vaisesika-like panel", ATOMISM * 3 + FIELD_LIKE[:2] + LEVEL_I[:3])
    # Yoga/Samkhya-ish mix
    add_many(
        "TGT_SAM",
        "samkhya_synthetic",
        "target",
        "Synthetic Samkhya/Yoga-like panel",
        [
            "Higher-level properties arise from lower-level organization of material nature.",
            "An observer and observed system are explicitly distinguished in cognition.",
            "States of material nature transform according to identifiable relationships.",
            "Complex properties arise when elementary parts are organized.",
        ]
        + LEVEL_I[:4]
        + FIELD_LIKE[:4],
    )
    # Indian controls
    add_many("CTL_BUD", "buddhist_synthetic", "control", "Synthetic Buddhist-like panel", BUDDHISTISH * 3 + LEVEL_I[:4] + LITERARY[:4])
    add_many("CTL_JAIN", "jain_synthetic", "control", "Synthetic Jain-like panel", JAINISH * 3 + ATOMISM[:4] + LITERARY[:3])
    # External controls
    add_many("CTL_GRK", "greek_synthetic", "control", "Synthetic Greek-like panel", GREEKISH * 3 + ATOMISM[:4] + LEVEL_I[:4])
    add_many("CTL_CHN", "chinese_synthetic", "control", "Synthetic Chinese-like panel", CHINESEISH * 3 + LEVEL_I[:4] + LITERARY[:4])
    # Mystical generic + Sanskrit literary negatives
    add_many("NEG_MYS", "mystical_synthetic", "negative_control", "Synthetic mystical panel", LEVEL_I * 2 + [
        "Cosmic energy permeates all things as a sacred vibration.",
        "The observer creates reality by mere attention.",
    ])
    add_many("NEG_LIT", "sanskrit_literary_synthetic", "negative_control", "Synthetic literary negative panel", LITERARY * 4)

    # Deduplicate by id
    seen = set()
    unique = []
    for p in out:
        if p.passage_id in seen:
            continue
        seen.add(p.passage_id)
        # normalize physics split already ok; force development for non-physics
        if p.role != "physics_reference":
            p = p.model_copy(update={"dataset_split": DatasetSplit.DEVELOPMENT})
        unique.append(p)
    return unique


def main() -> None:
    passages = build_100()
    # Include original synthetic philosophy set if not already
    existing_ids = {p.passage_id for p in passages}
    for p in synthetic_philosophy_passages():
        if p.passage_id not in existing_ids:
            passages.append(p.model_copy(update={"dataset_split": DatasetSplit.DEVELOPMENT}))

    out_path = ROOT / "corpus/development/prototype100_passages.parquet"
    passages_to_parquet(passages, out_path)
    print(f"n_passages={len(passages)} wrote={out_path}")

    # Balance report
    import pandas as pd

    df = pd.DataFrame([p.model_dump(mode="json") for p in passages])
    bal = df.groupby(["role", "tradition"]).size().reset_index(name="n")
    bal_path = ROOT / "corpus/development/prototype100_balance.csv"
    bal.to_csv(bal_path, index=False)
    print(bal.to_string(index=False))
    print("balance", bal_path)

    # Run pipeline
    result = run_pipeline_on_passages(
        passages,
        ontology_path=ROOT / "ontology/ontology_v0.1.yaml",
        fingerprint_dir=ROOT / "ontology/physics_fingerprints",
        out_dir=ROOT / "results/exploratory/prototype100",
        experiment_id="dev-prototype100-v0.1",
        repo_root=ROOT,
    )
    print(result["mean_QS_by_role"])


if __name__ == "__main__":
    main()
