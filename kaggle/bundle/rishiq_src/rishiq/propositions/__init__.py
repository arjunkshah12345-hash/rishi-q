"""Atomic proposition extraction (auditable; no quantum-seeking prompts)."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from rishiq.models import BlindedPassage, Passage, Proposition


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


class PropositionExtractor(ABC):
    name: str
    prompt_version: str

    @abstractmethod
    def extract(self, passage: Passage | BlindedPassage) -> list[Proposition]:
        raise NotImplementedError


class HeuristicPropositionExtractor(PropositionExtractor):
    """Deterministic sentence/clause splitter for local development."""

    name = "heuristic-propositions"
    prompt_version = "prop-v0.1"

    def extract(self, passage: Passage | BlindedPassage) -> list[Proposition]:
        if isinstance(passage, BlindedPassage):
            pid = passage.anonymous_id
            text = passage.text
        else:
            pid = passage.passage_id
            text = passage.translation or passage.source_text
        sentences = [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]
        if not sentences:
            sentences = [text.strip()]
        out: list[Proposition] = []
        for i, sent in enumerate(sentences):
            # Prefer declarative clauses; skip pure questions
            if sent.endswith("?"):
                continue
            out.append(
                Proposition(
                    proposition_id=f"{pid}::P{i:03d}",
                    passage_id=pid,
                    text=sent,
                    evidence_span=sent,
                    model_name=self.name,
                    prompt_version=self.prompt_version,
                    confidence=0.6 if len(sent.split()) >= 5 else 0.4,
                )
            )
        if not out and text.strip():
            out.append(
                Proposition(
                    proposition_id=f"{pid}::P000",
                    passage_id=pid,
                    text=text.strip(),
                    evidence_span=text.strip(),
                    model_name=self.name,
                    prompt_version=self.prompt_version,
                    confidence=0.5,
                )
            )
        return out


def extract_propositions(
    passage: Passage | BlindedPassage,
    extractor: PropositionExtractor | None = None,
) -> list[Proposition]:
    extractor = extractor or HeuristicPropositionExtractor()
    return extractor.extract(passage)
