"""Report generation for SparkTest results."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sparktest.models import CreativityScore, NarrativeScore, TorranceProfile


def render_creativity_report(
    scores: list[CreativityScore],
    profile: TorranceProfile | None = None,
    console: Console | None = None,
) -> None:
    """Render creativity test results as a rich report."""
    console = console or Console()
    console.print(Panel("[bold cyan]SparkTest Creativity Report[/bold cyan]", expand=False))

    if profile:
        t = Table(title="Torrance Creativity Profile")
        t.add_column("Dimension", style="magenta")
        t.add_column("Score", justify="right", style="green")
        t.add_row("Fluency", f"{profile.fluency:.1f}")
        t.add_row("Flexibility", f"{profile.flexibility:.1f}")
        t.add_row("Originality", f"{profile.originality:.1f}")
        t.add_row("Elaboration", f"{profile.elaboration:.1f}")
        t.add_row("[bold]Composite Index[/bold]", f"[bold]{profile.composite_creativity_index:.1f}[/bold]")
        console.print(t)

    for cs in scores:
        t = Table(title=f"Task: {cs.response.task.prompt[:50]}...")
        t.add_column("Dimension", style="magenta")
        t.add_column("Score", justify="right", style="green")
        t.add_column("Details", max_width=50)
        for d in cs.dimensions:
            t.add_row(d.dimension.value, f"{d.score:.1f}/{d.max_score:.0f}", d.details[:50])
        t.add_row("[bold]Total[/bold]", f"[bold]{cs.total_score:.1f}[/bold]", "")
        console.print(t)


def render_narrative_report(
    scores: list[NarrativeScore], console: Console | None = None
) -> None:
    """Render narrative creativity scores."""
    console = console or Console()
    t = Table(title="Narrative Creativity Scores")
    t.add_column("Story #", style="cyan")
    t.add_column("Originality", justify="right")
    t.add_column("Coherence", justify="right")
    t.add_column("Surprise", justify="right")
    t.add_column("Composite", justify="right", style="green")

    for i, s in enumerate(scores, 1):
        t.add_row(
            str(i),
            f"{s.originality:.2f}", f"{s.coherence:.2f}",
            f"{s.surprise:.2f}", f"{s.composite:.2f}",
        )
    console.print(t)
