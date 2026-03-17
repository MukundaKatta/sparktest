"""Divergent thinking tests for creativity assessment."""

from __future__ import annotations

from sparktest.models import CreativityResponse, CreativityTask, TaskType


# Classic Alternative Uses Test (Guilford, Torrance)
_ALTERNATIVE_USES_PROMPTS = [
    "List as many unusual uses for a brick as you can think of.",
    "List as many unusual uses for a paperclip as you can think of.",
    "List as many unusual uses for a newspaper as you can think of.",
    "List as many unusual uses for a shoe as you can think of.",
]

# Consequences Test
_CONSEQUENCES_PROMPTS = [
    "What would happen if humans could fly?",
    "What would happen if everyone could read minds?",
    "What would happen if gravity was half as strong?",
    "What would happen if no one needed to sleep?",
]

# Associative Thinking
_ASSOCIATION_PROMPTS = [
    "Write as many words as you can that are associated with 'ocean'.",
    "Write as many words as you can that are associated with 'time'.",
    "Write as many words as you can that are associated with 'light'.",
]


class DivergentThinkingTest:
    """Administers divergent thinking tests: alternative uses, consequences, associations.

    Based on Torrance Tests of Creative Thinking (TTCT) and Guilford's
    Alternative Uses Task. Measures fluency, flexibility, originality,
    and elaboration.
    """

    def generate_alternative_uses_task(self, index: int = 0) -> CreativityTask:
        """Generate an alternative uses task."""
        prompt = _ALTERNATIVE_USES_PROMPTS[index % len(_ALTERNATIVE_USES_PROMPTS)]
        return CreativityTask(
            task_type=TaskType.ALTERNATIVE_USES,
            prompt=prompt,
            context="Divergent thinking: generate as many creative uses as possible.",
            time_limit_seconds=180,
        )

    def generate_consequences_task(self, index: int = 0) -> CreativityTask:
        """Generate a consequences task."""
        prompt = _CONSEQUENCES_PROMPTS[index % len(_CONSEQUENCES_PROMPTS)]
        return CreativityTask(
            task_type=TaskType.CONSEQUENCES,
            prompt=prompt,
            context="Divergent thinking: imagine as many consequences as possible.",
            time_limit_seconds=180,
        )

    def generate_associations_task(self, index: int = 0) -> CreativityTask:
        """Generate an associative thinking task."""
        prompt = _ASSOCIATION_PROMPTS[index % len(_ASSOCIATION_PROMPTS)]
        return CreativityTask(
            task_type=TaskType.ASSOCIATIONS,
            prompt=prompt,
            context="Divergent thinking: generate as many associated words as possible.",
            time_limit_seconds=120,
        )

    def generate_full_battery(self) -> list[CreativityTask]:
        """Generate a full battery of divergent thinking tasks."""
        tasks = []
        tasks.append(self.generate_alternative_uses_task(0))
        tasks.append(self.generate_alternative_uses_task(1))
        tasks.append(self.generate_consequences_task(0))
        tasks.append(self.generate_consequences_task(1))
        tasks.append(self.generate_associations_task(0))
        return tasks

    def parse_response(self, task: CreativityTask, raw_text: str) -> CreativityResponse:
        """Parse a raw text response into individual items."""
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        # Remove numbering
        cleaned = []
        for line in lines:
            stripped = line.lstrip("0123456789.-) ").strip()
            if stripped:
                cleaned.append(stripped)

        return CreativityResponse(task=task, responses=cleaned, raw_text=raw_text)
