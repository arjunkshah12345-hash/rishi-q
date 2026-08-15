"""Generate synthetic + modern-physics validation passages."""

from __future__ import annotations

from pathlib import Path

from rishiq.experiments import passages_to_parquet
from rishiq.models import DatasetSplit, Passage
from rishiq.provenance import sha256_text


def _p(**kwargs) -> Passage:
    text = kwargs["translation"]
    kwargs.setdefault("source_hash", sha256_text(text))
    kwargs.setdefault("source_language", "en")
    kwargs.setdefault("license_status", "synthetic")
    return Passage(**kwargs)


def modern_physics_passages() -> list[Passage]:
    return [
        _p(
            passage_id="PHYS_NEWTON_001",
            tradition="modern_physics",
            school="classical_mechanics",
            work="Synthetic Newtonian description",
            translation=(
                "A particle follows a trajectory in space. Its state is a configuration of position "
                "and velocity that evolves according to deterministic equations. Composite systems "
                "are described by combining independent component states. Influences are transmitted "
                "through neighboring interactions. A specified mechanical quantity remains unchanged "
                "through the process. The transformation can be undone by the inverse process. "
                "We cannot know the exact microstate of every grain of sand, but each has definite values."
            ),
            translation_style="physics_reference",
            dataset_split=DatasetSplit.PHYSICS_CONTROL,
            role="physics_reference",
            genre="physics",
            topic="newtonian",
        ),
        _p(
            passage_id="PHYS_EM_001",
            tradition="modern_physics",
            school="electromagnetism",
            work="Synthetic classical EM description",
            translation=(
                "A continuous medium fills space: the electromagnetic field is present throughout a spatial region. "
                "The field takes different values at different locations. A change in the field travels through "
                "space over time. Local observables are manifestations of the extended field. Forces between "
                "charges are mediated by the electromagnetic field. A localized pulse is a dynamical disturbance "
                "of the medium. Local forms appear within an all-pervading substrate. The quantity oscillates periodically."
            ),
            translation_style="physics_reference",
            dataset_split=DatasetSplit.PHYSICS_CONTROL,
            role="physics_reference",
            genre="physics",
            topic="classical_em",
        ),
        _p(
            passage_id="PHYS_THERMO_001",
            tradition="modern_physics",
            school="thermodynamics",
            work="Synthetic thermodynamics description",
            translation=(
                "Complex properties arise when elementary parts are organized. Macroscopic state variables "
                "describe equilibrium. Probability only reflects our ignorance of hidden definite values. "
                "We cannot know the exact microstate. A specified quantity remains unchanged through the process "
                "in an isolated idealization."
            ),
            translation_style="physics_reference",
            dataset_split=DatasetSplit.PHYSICS_CONTROL,
            role="physics_reference",
            genre="physics",
            topic="thermodynamics",
        ),
        _p(
            passage_id="PHYS_QM_001",
            tradition="modern_physics",
            school="quantum_mechanics",
            work="Synthetic QM description",
            translation=(
                "Only discrete energy levels are allowed. The state jointly represents mutually exclusive outcomes "
                "prior to selection. Outcome probabilities are basic features of the theory, not just missing information. "
                "The recorded outcome is produced in association with a measurement interaction. Position and momentum "
                "cannot both have definite values in the same state. The joint state cannot be written as independent "
                "component states. Assigned values depend on which compatible measurement context is chosen. "
                "Measurement interaction alters the system's subsequent state. No definite value is predetermined "
                "prior to the interaction. We distinguish the measuring apparatus from the measured system."
            ),
            translation_style="physics_reference",
            dataset_split=DatasetSplit.PHYSICS_CONTROL,
            role="physics_reference",
            genre="physics",
            topic="quantum_mechanics",
        ),
        _p(
            passage_id="PHYS_QFT_001",
            tradition="modern_physics",
            school="quantum_field_theory",
            work="Synthetic QFT description",
            translation=(
                "A continuous medium fills space as a quantum field present throughout a spatial region. "
                "Particles are discrete excitations of the underlying field. The field admits only discrete "
                "excitation quanta. Forces between charges are mediated by the electromagnetic field. "
                "A change in the field travels through space over time. Local observables are manifestations "
                "of the extended field. Outcome probabilities are basic features of the theory, not just missing information."
            ),
            translation_style="physics_reference",
            dataset_split=DatasetSplit.PHYSICS_CONTROL,
            role="physics_reference",
            genre="physics",
            topic="quantum_field_theory",
        ),
        _p(
            passage_id="PHYS_ENTANGLE_001",
            tradition="modern_physics",
            school="quantum_mechanics",
            work="Synthetic entanglement description",
            translation=(
                "For two systems prepared jointly, the joint state cannot be represented as independent component states. "
                "Distant entities maintain specified correlations. Outcome probabilities are basic features of the theory, "
                "not just missing information."
            ),
            translation_style="physics_reference",
            dataset_split=DatasetSplit.PHYSICS_CONTROL,
            role="physics_reference",
            genre="physics",
            topic="entanglement",
        ),
    ]


def synthetic_philosophy_passages() -> list[Passage]:
    return [
        _p(
            passage_id="SYN_UNITY_001",
            tradition="synthetic_metaphysical",
            school="generic",
            work="Synthetic unity metaphor",
            translation="Everything is one. All things are interconnected. Reality is a deeper unity beneath appearances.",
            dataset_split=DatasetSplit.SYNTHETIC,
            role="negative_control",
            genre="metaphysical",
            topic="unity",
        ),
        _p(
            passage_id="SYN_FIELD_001",
            tradition="synthetic_target_like",
            school="synthetic",
            work="Synthetic field-like substrate",
            translation=(
                "An underlying reality persists while forms change. A continuous medium fills space. "
                "Local forms appear within an all-pervading substrate. A disturbance travels through the medium."
            ),
            dataset_split=DatasetSplit.SYNTHETIC,
            role="target",
            genre="philosophical",
            topic="substrate",
        ),
        _p(
            passage_id="SYN_ATOM_001",
            tradition="synthetic_vaisheshika_like",
            school="synthetic",
            work="Synthetic atomism",
            translation=(
                "Bodies are aggregates of indivisible particles. Ultimate atoms cannot be further divided. "
                "Macroscopic objects are composed from more elementary entities. Influences are transmitted "
                "through neighboring interactions."
            ),
            dataset_split=DatasetSplit.SYNTHETIC,
            role="target",
            genre="philosophical",
            topic="atomism",
        ),
        _p(
            passage_id="SYN_MYSTICAL_001",
            tradition="synthetic_mystical",
            school="generic",
            work="Synthetic mystical control",
            translation=(
                "Invisible powers vibrate through all beings. Cosmic energy permeates all things. "
                "Consciousness witnesses the dance of creation."
            ),
            dataset_split=DatasetSplit.SYNTHETIC,
            role="control",
            genre="mystical",
            topic="generic_mystical",
        ),
        _p(
            passage_id="SYN_GREEK_001",
            tradition="greek",
            school="atomism",
            work="Synthetic Democritean control",
            translation=(
                "Bodies are aggregates of indivisible particles moving in the void. "
                "Ultimate atoms cannot be further divided. Influences are transmitted through neighboring interactions."
            ),
            dataset_split=DatasetSplit.SYNTHETIC,
            role="control",
            genre="philosophical",
            topic="greek_atomism",
        ),
    ]


def build_synthetic_corpus(out_path: str | Path) -> Path:
    passages = modern_physics_passages() + synthetic_philosophy_passages()
    return passages_to_parquet(passages, out_path)


if __name__ == "__main__":
    p = build_synthetic_corpus("corpus/development/synthetic_passages.parquet")
    print("wrote", p)
