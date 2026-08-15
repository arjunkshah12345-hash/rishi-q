"""Secondary embeddings interface (never primary evidence)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    model_name: str
    model_revision: str
    vectors_path: str
    note: str = "SECONDARY_ONLY"


class EmbeddingBackend:
    """Placeholder; heavy models run on Kaggle."""

    name = "none"
    revision = "unspecified"

    def encode(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError(
            "Embeddings are secondary and intended for Kaggle GPU runs; "
            "see kaggle/embeddings.ipynb"
        )


def cosine(a: list[float], b: list[float]) -> float:
    import math

    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
