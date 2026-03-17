"""CLI interface for SparkTest."""

from __future__ import annotations

import click
from rich.console import Console

from sparktest.models import CreativityResponse, CreativityScore, TorranceProfile
from sparktest.report import render_creativity_report, render_narrative_report
from sparktest.scorer.elaboration import ElaborationScorer
from sparktest.scorer.flexibility import FlexibilityScorer
from sparktest.scorer.fluency import FluencyScorer
from sparktest.scorer.originality import OriginalityScorer
from sparktest.tests.divergent import DivergentThinkingTest
from sparktest.tests.narrative import NarrativeCreativityTest

console = Console()


@click.group()
def cli() -> None:
    """SparkTest: Measure AI creativity with Torrance-style assessments."""


@cli.command()
@click.argument("responses", nargs=-1)
@click.option("--task-index", "-t", default=0, help="Alternative uses task index.")
def score_uses(responses: tuple[str, ...], task_index: int) -> None:
    """Score alternative uses responses for creativity."""
    test = DivergentThinkingTest()
    task = test.generate_alternative_uses_task(task_index)
    cr = CreativityResponse(task=task, responses=list(responses), raw_text="\n".join(responses))

    fluency = FluencyScorer().score(cr)
    flexibility = FlexibilityScorer().score(cr)
    originality = OriginalityScorer().score(cr)
    elaboration = ElaborationScorer().score(cr)

    cs = CreativityScore(
        response=cr,
        dimensions=[fluency, flexibility, originality, elaboration],
        total_score=sum(d.score for d in [fluency, flexibility, originality, elaboration]) / 4,
    )

    profile = TorranceProfile(
        fluency=fluency.score, flexibility=flexibility.score,
        originality=originality.score, elaboration=elaboration.score,
    )
    profile.compute_composite()

    render_creativity_report([cs], profile, console)


@cli.command()
@click.argument("story")
def score_story(story: str) -> None:
    """Score a story for narrative creativity."""
    test = NarrativeCreativityTest()
    result = test.score(story)
    render_narrative_report([result], console)


@cli.command()
def show_tasks() -> None:
    """Display available creativity test tasks."""
    dt = DivergentThinkingTest()
    console.print("[bold]Divergent Thinking Tasks:[/bold]")
    for task in dt.generate_full_battery():
        console.print(f"  [{task.task_type.value}] {task.prompt}")

    from sparktest.tests.convergent import ConvergentThinkingTest
    ct = ConvergentThinkingTest()
    console.print("\n[bold]Convergent Thinking Tasks:[/bold]")
    for task in ct.generate_full_battery():
        console.print(f"  [{task.task_type.value}] {task.prompt[:80]}...")


if __name__ == "__main__":
    cli()
