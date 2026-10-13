"""Golden JSONL evaluation record validation."""

from pydantic import BaseModel, ConfigDict, Field


class GoldenExample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    relevant_source_ids: list[str] = Field(default_factory=list)
    answerable: bool

    def validate_relevance(self) -> None:
        if not self.answerable and self.relevant_source_ids:
            raise ValueError("unanswerable examples cannot contain relevant sources")
