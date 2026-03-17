"""Flexibility scorer: counts category switches."""

from __future__ import annotations

from sparktest.models import CreativityDimension, CreativityResponse, DimensionScore


# Semantic categories for flexibility scoring
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "construction": ["build", "wall", "house", "bridge", "stack", "support", "foundation"],
    "weapon": ["throw", "weapon", "hit", "smash", "break", "hammer", "projectile"],
    "art": ["paint", "draw", "sculpt", "art", "decoration", "display", "canvas"],
    "tool": ["tool", "grind", "sharpen", "weight", "measure", "press", "anchor"],
    "furniture": ["seat", "table", "stand", "shelf", "bookend", "doorstop"],
    "sport": ["exercise", "game", "sport", "workout", "lift", "catch", "throw"],
    "container": ["hold", "carry", "store", "container", "fill", "pot", "vessel"],
    "education": ["teach", "learn", "example", "demonstrate", "study", "lesson"],
    "food": ["cook", "bake", "grill", "eat", "kitchen", "recipe", "ingredient"],
    "technology": ["computer", "device", "digital", "electronic", "machine", "robot"],
    "nature": ["garden", "plant", "animal", "soil", "water", "earth", "natural"],
    "social": ["gift", "share", "communicate", "symbol", "trade", "exchange"],
}


class FlexibilityScorer:
    """Counts category switches in creativity responses.

    Flexibility measures how many different conceptual categories
    the responses span, per Torrance's framework.
    """

    def __init__(self, categories: dict[str, list[str]] | None = None) -> None:
        self.categories = categories or _CATEGORY_KEYWORDS

    def score(self, response: CreativityResponse) -> DimensionScore:
        """Score the flexibility of a creativity response."""
        categories_used: set[str] = set()

        for item in response.responses:
            cat = self._categorize(item)
            if cat:
                categories_used.add(cat)

        count = len(categories_used)
        # Normalize: 10+ categories is exceptional
        normalized = min(count / 10 * 100, 100.0)

        return DimensionScore(
            dimension=CreativityDimension.FLEXIBILITY,
            score=round(normalized, 1),
            max_score=100.0,
            details=f"{count} distinct categories: {', '.join(sorted(categories_used))}",
        )

    def _categorize(self, text: str) -> str | None:
        """Assign a text to a semantic category."""
        text_lower = text.lower()
        best_cat = None
        best_count = 0

        for category, keywords in self.categories.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > best_count:
                best_count = matches
                best_cat = category

        return best_cat
