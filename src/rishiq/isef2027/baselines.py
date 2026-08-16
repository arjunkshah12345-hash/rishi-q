"""Baseline similarity methods: lexical (TF-IDF), bag embedding proxy, ontology Jaccard."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def tfidf_pairwise(texts_a: Sequence[str], texts_b: Sequence[str]) -> np.ndarray:
    """Cosine TF-IDF similarity matrix |A| x |B|."""
    all_texts = list(texts_a) + list(texts_b)
    vec = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
    X = vec.fit_transform(all_texts)
    na = len(texts_a)
    return cosine_similarity(X[:na], X[na:])


def mean_tfidf_similarity(query_texts: Sequence[str], ref_texts: Sequence[str]) -> float:
    if not query_texts or not ref_texts:
        return 0.0
    M = tfidf_pairwise(query_texts, ref_texts)
    return float(np.mean(M))


def binary_vector_jaccard(a: dict[str, int], b: dict[str, int]) -> float:
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    inter = sum(1 for k in keys if a.get(k, 0) == 1 and b.get(k, 0) == 1)
    union = sum(1 for k in keys if a.get(k, 0) == 1 or b.get(k, 0) == 1)
    return 0.0 if union == 0 else inter / union


def ranking_accuracy(scores: dict[str, float], correct_key: str) -> dict:
    """Whether correct_key ranks #1 among theory scores."""
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    rank = next(i for i, (k, _) in enumerate(ordered, start=1) if k == correct_key)
    return {
        "correct_key": correct_key,
        "rank": rank,
        "top1": ordered[0][0] if ordered else None,
        "top1_correct": bool(ordered) and ordered[0][0] == correct_key,
        "scores": scores,
    }
