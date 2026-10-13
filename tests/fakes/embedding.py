"""Deterministic embedding provider for unit tests only."""

from collections.abc import Sequence


class FakeEmbeddingProvider:
    def __init__(self, dimensions: int = 3) -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed(self, text: str) -> Sequence[float]:
        value = float(len(text) % 10)
        return [value / 10.0] * self.dimensions
