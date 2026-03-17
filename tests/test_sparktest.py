"""Tests for SparkTest."""

from sparktest.models import (
    CreativityDimension,
    CreativityResponse,
    CreativityTask,
    NarrativeScore,
    TaskType,
    TorranceProfile,
)
from sparktest.scorer.elaboration import ElaborationScorer
from sparktest.scorer.flexibility import FlexibilityScorer
from sparktest.scorer.fluency import FluencyScorer
from sparktest.scorer.originality import OriginalityScorer
from sparktest.tests.convergent import ConvergentThinkingTest
from sparktest.tests.divergent import DivergentThinkingTest
from sparktest.tests.narrative import NarrativeCreativityTest


def _make_response(items: list[str], task_type: TaskType = TaskType.ALTERNATIVE_USES) -> CreativityResponse:
    task = CreativityTask(task_type=task_type, prompt="Test prompt")
    return CreativityResponse(task=task, responses=items, raw_text="\n".join(items))


class TestDivergentThinkingTest:
    def setup_method(self):
        self.test = DivergentThinkingTest()

    def test_generate_alternative_uses(self):
        task = self.test.generate_alternative_uses_task(0)
        assert task.task_type == TaskType.ALTERNATIVE_USES
        assert "brick" in task.prompt.lower()

    def test_generate_consequences(self):
        task = self.test.generate_consequences_task(0)
        assert task.task_type == TaskType.CONSEQUENCES

    def test_generate_associations(self):
        task = self.test.generate_associations_task(0)
        assert task.task_type == TaskType.ASSOCIATIONS

    def test_full_battery(self):
        tasks = self.test.generate_full_battery()
        assert len(tasks) >= 4

    def test_parse_response(self):
        task = self.test.generate_alternative_uses_task()
        raw = "1. Build a wall\n2. Use as a doorstop\n3. Paperweight"
        cr = self.test.parse_response(task, raw)
        assert len(cr.responses) == 3
        assert "Build a wall" in cr.responses


class TestConvergentThinkingTest:
    def setup_method(self):
        self.test = ConvergentThinkingTest()

    def test_generate_rat(self):
        task = self.test.generate_rat_task(0)
        assert task.task_type == TaskType.RAT
        assert task.expected_answer is not None

    def test_evaluate_rat_correct(self):
        task = self.test.generate_rat_task(0)
        correct, score = self.test.evaluate_rat_response(task, task.expected_answer)
        assert correct is True
        assert score == 1.0

    def test_evaluate_rat_wrong(self):
        task = self.test.generate_rat_task(0)
        correct, score = self.test.evaluate_rat_response(task, "xyzzy")
        assert correct is False

    def test_generate_insight(self):
        task = self.test.generate_insight_task(0)
        assert task.task_type == TaskType.INSIGHT_PUZZLE

    def test_full_battery(self):
        tasks = self.test.generate_full_battery()
        assert len(tasks) >= 5


class TestNarrativeCreativityTest:
    def setup_method(self):
        self.test = NarrativeCreativityTest()

    def test_generate_task(self):
        task = self.test.generate_task(0)
        assert task.task_type == TaskType.STORY

    def test_score_story(self):
        story = (
            "The last human sat alone. Suddenly, there was a knock. "
            "He opened the door to find a robot holding flowers. "
            "However, the robot was actually his old friend, transformed. "
            "The twist revealed that humanity had evolved, not perished."
        )
        score = self.test.score(story)
        assert 0 <= score.originality <= 1
        assert 0 <= score.coherence <= 1
        assert 0 <= score.surprise <= 1
        assert 0 <= score.composite <= 1

    def test_empty_story(self):
        score = self.test.score("")
        assert score.originality == 0.0


class TestFluencyScorer:
    def setup_method(self):
        self.scorer = FluencyScorer()

    def test_basic_fluency(self):
        cr = _make_response(["idea one", "idea two", "idea three"])
        result = self.scorer.score(cr)
        assert result.dimension == CreativityDimension.FLUENCY
        assert result.score > 0

    def test_deduplication(self):
        cr = _make_response(["doorstop", "Doorstop", "DOORSTOP", "paperweight"])
        result = self.scorer.score(cr)
        assert "2 unique" in result.details

    def test_empty(self):
        cr = _make_response([])
        result = self.scorer.score(cr)
        assert result.score == 0.0


class TestFlexibilityScorer:
    def setup_method(self):
        self.scorer = FlexibilityScorer()

    def test_multi_category(self):
        cr = _make_response([
            "Build a wall with it",
            "Throw it as a weapon",
            "Use as art display decoration",
            "Cook on it in kitchen",
        ])
        result = self.scorer.score(cr)
        assert result.score > 0
        assert result.dimension == CreativityDimension.FLEXIBILITY

    def test_single_category(self):
        cr = _make_response(["build wall", "build house", "build bridge"])
        result = self.scorer.score(cr)
        assert "1 distinct" in result.details


class TestOriginalityScorer:
    def test_without_reference(self):
        scorer = OriginalityScorer()
        cr = _make_response(["a short idea", "a much longer and more elaborate creative idea"])
        result = scorer.score(cr)
        assert result.score > 0

    def test_with_reference(self):
        reference = ["doorstop", "paperweight", "doorstop", "doorstop", "weapon"]
        scorer = OriginalityScorer(reference_responses=reference)
        cr = _make_response(["doorstop", "spacecraft launcher"])
        result = scorer.score(cr)
        assert result.score > 0

    def test_novel_response(self):
        scorer = OriginalityScorer(reference_responses=["common answer"] * 10)
        cr = _make_response(["completely unique never seen before idea"])
        result = scorer.score(cr)
        assert result.score == 100.0


class TestElaborationScorer:
    def setup_method(self):
        self.scorer = ElaborationScorer()

    def test_elaborate_response(self):
        cr = _make_response([
            "Use the brick as a beautifully painted, carefully decorated doorstop "
            "for the 200-year-old Victorian mansion, placing it precisely by the "
            "ornamental garden entrance -- ensuring it matches the surrounding aesthetic."
        ])
        result = self.scorer.score(cr)
        assert result.score > 10

    def test_minimal_response(self):
        cr = _make_response(["stop door"])
        result = self.scorer.score(cr)
        assert result.score < 50

    def test_empty(self):
        cr = _make_response([])
        result = self.scorer.score(cr)
        assert result.score == 0.0


class TestTorranceProfile:
    def test_compute_composite(self):
        profile = TorranceProfile(
            fluency=80, flexibility=60, originality=70, elaboration=50,
        )
        result = profile.compute_composite()
        assert result == 65.0
        assert profile.composite_creativity_index == 65.0
