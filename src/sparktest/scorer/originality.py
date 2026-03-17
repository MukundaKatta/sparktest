"""Originality scorer: computes statistical rarity of responses."""

from __future__ import annotations

from collections import Counter

from sparktest.models import CreativityDimension, CreativityResponse, DimensionScore


class OriginalityScorer:
    """Computes the statistical rarity of responses.

    Originality in the Torrance framework is inversely related to
    how common a response is. Responses given by fewer people
    receive higher originality scores.
    """

    def __init__(self, reference_responses: list[str] | None = None) -> None:
        """Initialize with optional reference population responses."""
        self._reference_counts: Counter[str] = Counter()
        if reference_responses:
            for r in reference_responses:
                self._reference_counts[r.lower().strip()] += 1
        self._total_reference = sum(self._reference_counts.values())

    def add_reference(self, responses: list[str]) -> None:
        """Add reference population responses for comparison."""
        for r in responses:
            self._reference_counts[r.lower().strip()] += 1
        self._total_reference = sum(self._reference_counts.values())

    def score(self, response: CreativityResponse) -> DimensionScore:
        """Score the originality of a creativity response."""
        if not response.responses:
            return DimensionScore(
                dimension=CreativityDimension.ORIGINALITY,
                score=0.0, details="No responses to score",
            )

        scores = []
        for item in response.responses:
            scores.append(self._score_item(item))

        avg_score = sum(scores) / len(scores) if scores else 0.0
        normalized = min(avg_score * 100, 100.0)

        return DimensionScore(
            dimension=CreativityDimension.ORIGINALITY,
            score=round(normalized, 1),
            max_score=100.0,
            details=f"Avg rarity: {avg_score:.3f} across {len(response.responses)} responses",
        )

    def _score_item(self, item: str) -> float:
        """Score a single item's originality."""
        key = item.lower().strip()

        if self._total_reference == 0:
            # Without reference data, use heuristic: longer/more complex = more original
            word_count = len(key.split())
            return min(word_count / 10.0, 1.0)

        frequency = self._reference_counts.get(key, 0)
        if frequency == 0:
            return 1.0  # Completely novel

        # Rarity: inverse frequency, normalized
        rarity = 1.0 - (frequency / self._total_reference)
        return max(rarity, 0.0)
