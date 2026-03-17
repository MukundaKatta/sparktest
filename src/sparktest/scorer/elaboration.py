"""Elaboration scorer: measures detail richness."""

from __future__ import annotations

import re

from sparktest.models import CreativityDimension, CreativityResponse, DimensionScore


class ElaborationScorer:
    """Measures the richness of detail in creativity responses.

    Elaboration in the Torrance framework captures how much detail,
    nuance, and development each idea receives.
    """

    def score(self, response: CreativityResponse) -> DimensionScore:
        """Score the elaboration of a creativity response."""
        if not response.responses:
            return DimensionScore(
                dimension=CreativityDimension.ELABORATION,
                score=0.0, details="No responses to score",
            )

        scores = [self._score_item(item) for item in response.responses]
        avg = sum(scores) / len(scores) if scores else 0.0
        normalized = min(avg * 100, 100.0)

        return DimensionScore(
            dimension=CreativityDimension.ELABORATION,
            score=round(normalized, 1),
            max_score=100.0,
            details=f"Avg elaboration: {avg:.3f} across {len(response.responses)} responses",
        )

    def _score_item(self, text: str) -> float:
        """Score elaboration of a single response item."""
        score = 0.0

        # Word count (more words = more elaboration, up to a point)
        words = text.split()
        word_score = min(len(words) / 20.0, 0.3)
        score += word_score

        # Adjective/adverb density (simple heuristic: words ending in -ly, -ful, -ous, etc.)
        descriptors = re.findall(
            r"\b\w+(?:ly|ful|ous|ive|ible|able|ish|like|ing)\b", text.lower()
        )
        desc_ratio = len(descriptors) / max(len(words), 1)
        score += min(desc_ratio * 2, 0.25)

        # Specific details: numbers, proper nouns (capitalized words), measurements
        specifics = re.findall(r"\b[A-Z][a-z]+\b|\b\d+\b", text)
        score += min(len(specifics) / 5.0, 0.25)

        # Clause complexity (commas, semicolons suggest embedded clauses)
        clauses = text.count(",") + text.count(";") + text.count("--")
        score += min(clauses / 5.0, 0.2)

        return min(score, 1.0)
