"""JSONL loader for stable, versioned evaluation examples."""

import json
from collections.abc import Iterator
from pathlib import Path

from evaluation.schema import GoldenExample


def load_jsonl(path: Path) -> Iterator[GoldenExample]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                example = GoldenExample.model_validate(json.loads(line))
                example.validate_relevance()
            except (ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"invalid evaluation record at line {line_number}") from exc
            yield example
