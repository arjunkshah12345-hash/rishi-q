"""Physics classifier trained only on modern physics ontology vectors."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from rishiq.models import FeatureVector

CLASSES = [
    "CLASSICAL_MECHANICS",
    "ELECTROMAGNETISM",
    "THERMODYNAMICS",
    "RELATIVITY",
    "QUANTUM_MECHANICS",
    "QUANTUM_FIELD_THEORY",
]


def vector_to_array(vector: FeatureVector, feature_ids: Sequence[str]) -> np.ndarray:
    return np.array(
        [0.0 if vector.values.get(f) is None else float(vector.values[f]) for f in feature_ids],
        dtype=float,
    )


class PhysicsOntologyClassifier:
    """Secondary exploratory classifier. Never train on Sanskrit labels."""

    def __init__(self) -> None:
        self.model = LogisticRegression(max_iter=1000)
        self.encoder = LabelEncoder()
        self.feature_ids: list[str] = []
        self.frozen = False

    def fit(
        self,
        vectors: list[FeatureVector],
        labels: list[str],
        feature_ids: list[str],
    ) -> PhysicsOntologyClassifier:
        if self.frozen:
            raise RuntimeError("classifier is frozen")
        self.feature_ids = list(feature_ids)
        X = np.vstack([vector_to_array(v, self.feature_ids) for v in vectors])
        y = self.encoder.fit_transform(labels)
        self.model.fit(X, y)
        return self

    def freeze(self) -> None:
        self.frozen = True

    def predict_proba(self, vector: FeatureVector) -> dict[str, float]:
        X = vector_to_array(vector, self.feature_ids).reshape(1, -1)
        probs = self.model.predict_proba(X)[0]
        classes = self.encoder.inverse_transform(np.arange(len(probs)))
        return {str(c): float(p) for c, p in zip(classes, probs)}
