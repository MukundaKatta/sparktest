"""Convergent thinking tests for creativity assessment."""

from __future__ import annotations

from sparktest.models import CreativityResponse, CreativityTask, TaskType


# Remote Associates Test (RAT) - Mednick
_RAT_ITEMS = [
    {"words": ["falling", "actor", "dust"], "answer": "star"},
    {"words": ["dew", "comb", "bee"], "answer": "honey"},
    {"words": ["cream", "skate", "water"], "answer": "ice"},
    {"words": ["show", "life", "row"], "answer": "boat"},
    {"words": ["night", "wrist", "stop"], "answer": "watch"},
    {"words": ["rocking", "wheel", "high"], "answer": "chair"},
    {"words": ["out", "dog", "cat"], "answer": "house"},
    {"words": ["fish", "mine", "rush"], "answer": "gold"},
]

# Insight puzzles
_INSIGHT_PUZZLES = [
    {
        "puzzle": "A man walks into a bar and asks for a glass of water. "
                  "The bartender pulls out a gun and points it at him. "
                  "The man says 'thank you' and leaves. Why?",
        "answer": "The man had hiccups. The bartender scared them away.",
    },
    {
        "puzzle": "How can you throw a ball, have it stop, and come back to you, "
                  "without it bouncing off anything or having a string attached?",
        "answer": "Throw it straight up in the air.",
    },
    {
        "puzzle": "A man is found dead in a field with an unopened package next to him. "
                  "No other person or creature was involved. How did he die?",
        "answer": "The package was a parachute that didn't open.",
    },
]


class ConvergentThinkingTest:
    """Administers convergent thinking tests: RAT and insight puzzles.

    Remote Associates Test (RAT) measures the ability to find connections
    between seemingly unrelated words. Insight puzzles measure the ability
    to restructure problem representations.
    """

    def generate_rat_task(self, index: int = 0) -> CreativityTask:
        """Generate a Remote Associates Test item."""
        item = _RAT_ITEMS[index % len(_RAT_ITEMS)]
        words = ", ".join(item["words"])
        return CreativityTask(
            task_type=TaskType.RAT,
            prompt=f"What single word connects these three words: {words}?",
            context="Remote Associates Test: find the common associate.",
            expected_answer=item["answer"],
        )

    def generate_insight_task(self, index: int = 0) -> CreativityTask:
        """Generate an insight puzzle."""
        item = _INSIGHT_PUZZLES[index % len(_INSIGHT_PUZZLES)]
        return CreativityTask(
            task_type=TaskType.INSIGHT_PUZZLE,
            prompt=item["puzzle"],
            context="Insight puzzle: find the creative solution.",
            expected_answer=item["answer"],
        )

    def generate_full_battery(self) -> list[CreativityTask]:
        """Generate a full battery of convergent thinking tasks."""
        tasks = []
        for i in range(min(5, len(_RAT_ITEMS))):
            tasks.append(self.generate_rat_task(i))
        for i in range(len(_INSIGHT_PUZZLES)):
            tasks.append(self.generate_insight_task(i))
        return tasks

    def evaluate_rat_response(
        self, task: CreativityTask, response: str
    ) -> tuple[bool, float]:
        """Evaluate a RAT response. Returns (is_correct, partial_credit)."""
        if not task.expected_answer:
            return False, 0.0

        answer = task.expected_answer.lower().strip()
        response_clean = response.lower().strip()

        if answer == response_clean:
            return True, 1.0

        # Partial credit if answer appears in response
        if answer in response_clean:
            return True, 0.8

        return False, 0.0

    def evaluate_insight_response(
        self, task: CreativityTask, response: str
    ) -> tuple[bool, float]:
        """Evaluate an insight puzzle response with semantic similarity."""
        if not task.expected_answer:
            return False, 0.0

        answer_words = set(task.expected_answer.lower().split())
        response_words = set(response.lower().split())
        overlap = len(answer_words & response_words)

        if overlap >= len(answer_words) * 0.6:
            return True, min(overlap / len(answer_words), 1.0)

        return False, 0.0
