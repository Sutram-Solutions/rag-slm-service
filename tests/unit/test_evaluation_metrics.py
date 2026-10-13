import pytest

from evaluation.metrics.retrieval import recall_at_k, reciprocal_rank


def test_recall_and_reciprocal_rank() -> None:
    retrieved = ["a", "b", "c"]
    assert recall_at_k(retrieved, {"b"}, 2) == 1.0
    assert reciprocal_rank(retrieved, {"b"}) == 0.5


def test_unanswerable_examples_are_not_scored_as_recall() -> None:
    with pytest.raises(ValueError):
        recall_at_k(["a"], set(), 1)
