"""Narrative creativity testing and scoring."""

from __future__ import annotations

import re
from collections import Counter

from sparktest.models import CreativityTask, NarrativeScore, TaskType


_STORY_PROMPTS = [
    "Write a short story that begins with: 'The last human on Earth sat alone in a room. There was a knock on the door.'",
    "Write a short story incorporating these three elements: a broken clock, a stranger's letter, and rain.",
    "Write a short story where the ending completely redefines the beginning.",
]

# Common words that don't contribute to originality
_COMMON_WORDS = {
    "the", "a", "an", "is", "was", "were", "are", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "and", "but", "or", "nor", "for", "yet", "so", "in", "on", "at",
    "to", "of", "it", "he", "she", "they", "we", "i", "you", "that",
    "this", "with", "from", "by", "not", "his", "her", "its", "their",
}


class NarrativeCreativityTest:
    """Scores story originality, coherence, and surprise.

    Evaluates narrative creativity through lexical diversity,
    structural coherence, and unexpected plot elements.
    """

    def generate_task(self, index: int = 0) -> CreativityTask:
        """Generate a narrative creativity task."""
        prompt = _STORY_PROMPTS[index % len(_STORY_PROMPTS)]
        return CreativityTask(
            task_type=TaskType.STORY,
            prompt=prompt,
            context="Write a creative short story (100-500 words).",
        )

    def score(self, story: str) -> NarrativeScore:
        """Score a story on originality, coherence, and surprise."""
        originality = self._score_originality(story)
        coherence = self._score_coherence(story)
        surprise = self._score_surprise(story)
        composite = (originality + coherence + surprise) / 3.0

        return NarrativeScore(
            originality=round(originality, 3),
            coherence=round(coherence, 3),
            surprise=round(surprise, 3),
            composite=round(composite, 3),
            details=f"Originality={originality:.2f}, Coherence={coherence:.2f}, Surprise={surprise:.2f}",
        )

    def _score_originality(self, story: str) -> float:
        """Score originality via lexical diversity and rare word usage."""
        words = re.findall(r"\b\w+\b", story.lower())
        if not words:
            return 0.0

        # Type-token ratio (lexical diversity)
        unique = set(words)
        ttr = len(unique) / len(words)

        # Ratio of non-common words
        content_words = [w for w in words if w not in _COMMON_WORDS]
        unique_content = set(content_words)
        content_diversity = len(unique_content) / max(len(content_words), 1)

        # Hapax legomena ratio (words used only once)
        counts = Counter(words)
        hapax = sum(1 for c in counts.values() if c == 1)
        hapax_ratio = hapax / max(len(unique), 1)

        return min((ttr * 0.3 + content_diversity * 0.4 + hapax_ratio * 0.3), 1.0)

    def _score_coherence(self, story: str) -> float:
        """Score coherence via sentence connectivity and structure."""
        sentences = [s.strip() for s in re.split(r"[.!?]+", story) if s.strip()]
        if len(sentences) < 2:
            return 0.5

        # Measure word overlap between consecutive sentences (cohesion)
        overlaps = []
        for i in range(len(sentences) - 1):
            words_a = set(sentences[i].lower().split()) - _COMMON_WORDS
            words_b = set(sentences[i + 1].lower().split()) - _COMMON_WORDS
            if words_a and words_b:
                overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
                overlaps.append(overlap)

        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0.0

        # Temporal/causal connectors suggest coherence
        connectors = re.findall(
            r"\b(then|therefore|because|however|meanwhile|afterwards|"
            r"suddenly|finally|next|later|before|after|although)\b",
            story.lower(),
        )
        connector_ratio = min(len(connectors) / max(len(sentences), 1), 1.0)

        return min(avg_overlap * 0.5 + connector_ratio * 0.3 + 0.2, 1.0)

    def _score_surprise(self, story: str) -> float:
        """Score surprise via plot twist indicators and tonal shifts."""
        surprise_markers = [
            r"\b(suddenly|unexpectedly|to .+ surprise|twist|revealed|"
            r"but then|however|little did|never expected|shock)\b",
        ]
        sentences = [s.strip() for s in re.split(r"[.!?]+", story) if s.strip()]
        total_sentences = max(len(sentences), 1)

        # Count surprise markers
        marker_count = 0
        for pattern in surprise_markers:
            marker_count += len(re.findall(pattern, story.lower()))

        marker_score = min(marker_count / total_sentences, 1.0)

        # Check if ending differs in tone from beginning (simple heuristic)
        if len(sentences) >= 4:
            beginning_words = set(" ".join(sentences[:2]).lower().split()) - _COMMON_WORDS
            ending_words = set(" ".join(sentences[-2:]).lower().split()) - _COMMON_WORDS
            if beginning_words and ending_words:
                divergence = 1.0 - len(beginning_words & ending_words) / max(
                    len(beginning_words | ending_words), 1
                )
            else:
                divergence = 0.5
        else:
            divergence = 0.3

        return min(marker_score * 0.6 + divergence * 0.4, 1.0)
