"""Retrieval: the retriever contract, baseline retrievers and offline metrics.

The harness hands each retriever the contexts the asker may use, and then checks every hit
against the organisation itself, so a retriever that ignores access control is caught.

Offline grading checks whether the returned context *contains* the gold strings. That is an
upper bound on what a model could answer from it. LLM-graded answer accuracy comes next.
"""

import math
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from .data import Note, Question
from .org import Org
from .tokens import count_tokens


@dataclass(frozen=True)
class Unit:
    """A retrievable piece of a note: a section, or a single fact line."""

    id: str  # "<note path>#<heading>" or "<note path>#<heading>:<line>"
    note: str
    context: str
    text: str


@dataclass(frozen=True)
class Hit:
    id: str
    note: str
    context: str
    text: str

    def render(self) -> str:
        # Metadata counts against the budget too (AGENTS.md, "Retrieval and tokens").
        return f"[{self.context}] {self.id}\n{self.text}\n"


@dataclass
class Result:
    hits: list[Hit]
    omitted: int = 0

    @property
    def text(self) -> str:
        return "".join(h.render() for h in self.hits)

    @property
    def tokens(self) -> int:
        return count_tokens(self.text)


class Retriever(Protocol):
    def retrieve(self, question: str, contexts: list[str], budget_tokens: int) -> Result: ...


# --- Splitting notes ---------------------------------------------------------------------

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_BULLET = re.compile(r"^\s*[-*]\s+")


def sections(note: Note) -> list[Unit]:
    units, heading, lines = [], note.title, []

    def flush():
        text = "\n".join(lines).strip()
        if text:
            units.append(Unit(f"{note.path}#{heading}", note.path, note.context, text))

    for line in note.body.splitlines():
        if m := _HEADING.match(line):
            flush()
            heading, lines = m.group(2).strip(), []
        else:
            lines.append(line)
    flush()
    return units


def facts(note: Note) -> list[Unit]:
    """Bullet lines as fact-sized units, prefixed with the note title; prose stays as sections."""
    units = []
    for sec in sections(note):
        bullets = [ln for ln in sec.text.splitlines() if _BULLET.match(ln)]
        if not bullets:
            units.append(sec)
            continue
        for i, ln in enumerate(bullets, 1):
            text = f"{note.title}: {_BULLET.sub('', ln).strip()}"
            units.append(Unit(f"{sec.id}:{i}", note.path, note.context, text))
    return units


# --- Baselines ---------------------------------------------------------------------------


class WholeVault:
    """Loads every note in the allowed contexts, ignoring the budget: the comparison point."""

    def __init__(self, notes: list[Note]):
        self.notes = notes

    def retrieve(self, question: str, contexts: list[str], budget_tokens: int) -> Result:
        hits = [
            Hit(n.path, n.path, n.context, n.body.strip())
            for n in self.notes
            if n.context in contexts
        ]
        return Result(hits)


_WORD = re.compile(r"\w+")


def _terms(text: str) -> list[str]:
    return _WORD.findall(text.lower())


class BM25:
    """Keyword ranking over units, greedily packed into the token budget."""

    def __init__(self, units: list[Unit], k1: float = 1.5, b: float = 0.75):
        self.units = units
        self.k1, self.b = k1, b
        self.tfs = [Counter(_terms(u.text)) for u in units]
        self.lengths = [sum(tf.values()) for tf in self.tfs]
        self.avg = sum(self.lengths) / len(units) if units else 0
        df = Counter(t for tf in self.tfs for t in tf)
        n = len(units)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def score(self, i: int, query: list[str]) -> float:
        tf, length, s = self.tfs[i], self.lengths[i], 0.0
        for t in query:
            if f := tf.get(t):
                s += (
                    self.idf[t]
                    * f
                    * (self.k1 + 1)
                    / (f + self.k1 * (1 - self.b + self.b * length / self.avg))
                )
        return s

    def retrieve(self, question: str, contexts: list[str], budget_tokens: int) -> Result:
        query = _terms(question)
        allowed = set(contexts)
        ranked = sorted(
            ((self.score(i, query), i) for i, u in enumerate(self.units) if u.context in allowed),
            reverse=True,
        )
        hits, used, omitted = [], 0, 0
        for score, i in ranked:
            if score <= 0:
                break
            u = self.units[i]
            hit = Hit(u.id, u.note, u.context, u.text)
            cost = count_tokens(hit.render())
            if used + cost <= budget_tokens:
                hits.append(hit)
                used += cost
            else:
                omitted += 1
        return Result(hits, omitted)


RETRIEVERS: dict[str, Callable[[list[Note]], Retriever]] = {
    "whole": WholeVault,
    "bm25-sections": lambda notes: BM25([u for n in notes for u in sections(n)]),
    "bm25-facts": lambda notes: BM25([u for n in notes for u in facts(n)]),
}


# --- Metrics -----------------------------------------------------------------------------


@dataclass
class QuestionResult:
    question: Question
    tokens: int
    answerable: bool  # every must_include string is in the returned context
    evidence_found: bool  # at least one evidence note was returned
    access_leak: bool  # a hit from a context the asker can't read, or forbidden content


def allowed_contexts(org: Org, q: Question) -> list[str]:
    readable = org.readable(q.asker)
    if q.contexts is None:
        return readable
    return [c for c in q.contexts if c in readable]


def grade(org: Org, q: Question, result: Result) -> QuestionResult:
    text = result.text.lower()
    returned = {h.note for h in result.hits}
    unreadable = any(not org.can_read(q.asker, h.context) for h in result.hits)
    if q.type == "access":
        forbidden = any(s.lower() in text for s in q.must_not_include)
        forbidden = forbidden or bool(returned & set(q.evidence))
        leak = unreadable or forbidden
        return QuestionResult(q, result.tokens, not leak, False, leak)
    return QuestionResult(
        q,
        result.tokens,
        answerable=all(s.lower() in text for s in q.must_include),
        evidence_found=bool(returned & set(q.evidence)),
        access_leak=unreadable,
    )


@dataclass
class Summary:
    results: list[QuestionResult] = field(default_factory=list)

    def of(self, kind: str | None = None) -> list[QuestionResult]:
        return [r for r in self.results if kind is None or r.question.type == kind]

    @staticmethod
    def rate(rs: list[QuestionResult], attr: str) -> float | None:
        return sum(getattr(r, attr) for r in rs) / len(rs) if rs else None

    @property
    def leaks(self) -> list[str]:
        return [r.question.id for r in self.results if r.access_leak]

    @property
    def mean_tokens(self) -> float:
        rs = [r for r in self.results if r.question.type != "access"]
        return sum(r.tokens for r in rs) / len(rs) if rs else 0.0


def evaluate(
    org: Org, retriever: Retriever, questions: list[Question], budget_tokens: int
) -> Summary:
    summary = Summary()
    for q in questions:
        result = retriever.retrieve(q.question, allowed_contexts(org, q), budget_tokens)
        summary.results.append(grade(org, q, result))
    return summary
