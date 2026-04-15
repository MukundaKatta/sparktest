"""Creativity-benchmark scorers for open-ended responses.

sparktest's CLI runs AI systems through prompts designed to elicit
creative output. This module is the *scoring* side: a handful of
metrics drawn from the divergent-thinking literature (fluency,
flexibility, originality, elaboration) computed over a set of
candidate responses to a single prompt.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log
from typing import Iterable, Sequence
import re


_WORD_RE = re.compile(r"[A-Za-z]+")


def _tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


@dataclass(frozen=True)
class DivergenceScores:
    fluency: int
    flexibility: int
    originality: float
    elaboration: float
    raw_count: int


def score(
    responses: Sequence[str],
    *,
    corpus_counts: dict[str, int] | None = None,
    similar_jaccard: float = 0.7,
) -> DivergenceScores:
    """Score a bag of responses to a single prompt.

    - **fluency** — number of responses after deduplicating near-copies.
    - **flexibility** — number of conceptually distinct clusters.
    - **originality** — mean surprisal of content words vs. a corpus
      (higher = rarer words used).
    - **elaboration** — mean tokens per unique response.
    """
    if not responses:
        return DivergenceScores(0, 0, 0.0, 0.0, 0)

    # Dedup near-copies by Jaccard overlap of content-word sets.
    unique: list[tuple[str, set[str]]] = []
    for r in responses:
        toks = set(_tokens(r))
        if not toks:
            continue
        if any(_jaccard(toks, prev) >= similar_jaccard for _, prev in unique):
            continue
        unique.append((r, toks))

    fluency = len(unique)

    # Cluster by agglomerative Jaccard linkage — single-pass greedy.
    clusters: list[set[str]] = []
    for _, toks in unique:
        placed = False
        for c in clusters:
            if _jaccard(toks, c) >= 0.35:
                c.update(toks)
                placed = True
                break
        if not placed:
            clusters.append(set(toks))
    flexibility = len(clusters)

    # Originality: surprisal using corpus counts if given, else local counts.
    if corpus_counts:
        total = sum(corpus_counts.values()) or 1
        def surprisal(tok: str) -> float:
            c = corpus_counts.get(tok, 0) + 1
            return -log(c / (total + 1))
    else:
        all_toks = Counter(t for _, ts in unique for t in ts)
        total = sum(all_toks.values()) or 1
        def surprisal(tok: str) -> float:
            c = all_toks.get(tok, 0) + 1
            return -log(c / (total + 1))

    surps: list[float] = []
    for _, toks in unique:
        if toks:
            surps.append(sum(surprisal(t) for t in toks) / len(toks))
    originality = sum(surps) / len(surps) if surps else 0.0

    elaboration = sum(len(_tokens(r)) for r, _ in unique) / fluency if fluency else 0.0

    return DivergenceScores(
        fluency=fluency,
        flexibility=flexibility,
        originality=round(originality, 3),
        elaboration=round(elaboration, 2),
        raw_count=len(responses),
    )


def compare(a: DivergenceScores, b: DivergenceScores) -> dict:
    """Head-to-head deltas, A minus B, for a tournament leaderboard."""
    return {
        "fluency": a.fluency - b.fluency,
        "flexibility": a.flexibility - b.flexibility,
        "originality": round(a.originality - b.originality, 3),
        "elaboration": round(a.elaboration - b.elaboration, 2),
    }


def prepare_corpus(texts: Iterable[str]) -> dict[str, int]:
    """Build a background corpus count table for originality scoring."""
    c: Counter[str] = Counter()
    for t in texts:
        c.update(_tokens(t))
    return dict(c)
