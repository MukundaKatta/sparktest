"""Fluency scorer: counts unique valid ideas."""

from __future__ import annotations

from sparktest.models import CreativityDimension, CreativityResponse, DimensionScore


class FluencyScorer:
    """Counts the number of unique, valid ideas in a creativity response.

    Fluency is the foundational Torrance dimension -- the raw quantity
    of ideas produced, after removing duplicates and irrelevant entries.
    """

    def __init__(self, min_word_length: int = 2) -> None:
        self.min_word_length = min_word_length

    def score(self, response: CreativityResponse) -> DimensionScore:
        """Score the fluency of a creativity response."""
        unique_ideas = self._deduplicate(response.responses)
        valid = [r for r in unique_ideas if len(r) >= self.min_word_length]
        count = len(valid)

        # Normalize to 0-100 scale (assuming max ~30 ideas is exceptional)
        normalized = min(count / 30 * 100, 100.0)

        return DimensionScore(
            dimension=CreativityDimension.FLUENCY,
            score=round(normalized, 1),
            max_score=100.0,
            details=f"{count} unique valid ideas generated",
        )

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        """Remove duplicate ideas (case-insensitive)."""
        seen: set[str] = set()
        unique = []
        for item in items:
            key = item.lower().strip()
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return unique
