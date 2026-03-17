"""Data models for SparkTest."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TestType(str, Enum):
    DIVERGENT = "divergent"
    CONVERGENT = "convergent"
    NARRATIVE = "narrative"


class TaskType(str, Enum):
    ALTERNATIVE_USES = "alternative_uses"
    CONSEQUENCES = "consequences"
    ASSOCIATIONS = "associations"
    RAT = "remote_associates"
    INSIGHT_PUZZLE = "insight_puzzle"
    STORY = "story"


class CreativityDimension(str, Enum):
    """Torrance-style creativity dimensions."""
    FLUENCY = "fluency"
    FLEXIBILITY = "flexibility"
    ORIGINALITY = "originality"
    ELABORATION = "elaboration"


class CreativityTask(BaseModel):
    """A creativity task to administer."""
    task_type: TaskType
    prompt: str
    context: str = ""
    time_limit_seconds: Optional[int] = None
    expected_answer: Optional[str] = None  # for convergent tasks


class CreativityResponse(BaseModel):
    """An AI's response to a creativity task."""
    task: CreativityTask
    responses: list[str] = Field(default_factory=list)
    raw_text: str = ""


class DimensionScore(BaseModel):
    """Score for a single creativity dimension."""
    dimension: CreativityDimension
    score: float = Field(ge=0.0)
    max_score: float = 100.0
    details: str = ""


class CreativityScore(BaseModel):
    """Complete creativity score for one response."""
    response: CreativityResponse
    dimensions: list[DimensionScore] = Field(default_factory=list)
    total_score: float = 0.0
    percentile: Optional[float] = None  # vs reference population

    @property
    def dimension_dict(self) -> dict[CreativityDimension, float]:
        return {d.dimension: d.score for d in self.dimensions}


class NarrativeScore(BaseModel):
    """Score for narrative creativity."""
    originality: float = Field(default=0.0, ge=0.0, le=1.0)
    coherence: float = Field(default=0.0, ge=0.0, le=1.0)
    surprise: float = Field(default=0.0, ge=0.0, le=1.0)
    composite: float = Field(default=0.0, ge=0.0, le=1.0)
    details: str = ""


class TorranceProfile(BaseModel):
    """Torrance Tests of Creative Thinking (TTCT) style profile."""
    fluency: float = 0.0
    flexibility: float = 0.0
    originality: float = 0.0
    elaboration: float = 0.0
    composite_creativity_index: float = 0.0

    def compute_composite(self) -> float:
        """Compute the composite creativity index (equal weighting)."""
        self.composite_creativity_index = (
            self.fluency + self.flexibility + self.originality + self.elaboration
        ) / 4.0
        return self.composite_creativity_index
