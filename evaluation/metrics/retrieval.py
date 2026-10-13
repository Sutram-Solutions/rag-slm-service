"""Metrics for answerable retrieval examples."""

from collections.abc import Sequence


def recall_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if not relevant:
        raise ValueError("recall is undefined for unanswerable examples")
    return float(bool(set(retrieved[:k]) & relevant))


def reciprocal_rank(retrieved: Sequence[str], relevant: set[str]) -> float:
    if not relevant:
        raise ValueError("reciprocal rank is undefined for unanswerable examples")
    for index, source_id in enumerate(retrieved, start=1):
        if source_id in relevant:
            return 1.0 / index
    return 0.0


def abstention_accuracy(*, abstained: bool, answerable: bool) -> float:
    return float(abstained is (not answerable))
