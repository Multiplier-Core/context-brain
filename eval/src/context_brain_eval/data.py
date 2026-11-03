"""Loading the test sets and the Tallowmere vaults."""

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .org import context_of

CATEGORIES = ("1", "2", "3", "drop", "refused")
FORMS = {
    "chat": "ai_session",
    "remember": "remember",
    "slack": "slack_channel",
    "meeting": "meeting_folder",
    "document": "group_document",
}
GROUP_SOURCE_FORMS = ("slack", "meeting", "document")
DIRECT_FORMS = ("chat", "remember")
QUESTION_TYPES = (
    "single_fact",
    "entity_summary",
    "multi_step",
    "temporal",
    "disputed",
    "cross_context",
    "access",
)


@dataclass(frozen=True)
class Item:
    id: str
    base: str
    author: str
    form: str
    source_kind: str
    source_context: str | None
    text: str
    category: str
    group: str | None
    reasons: tuple[str, ...]
    tags: tuple[str, ...]
    note: str

    @property
    def is_group_source(self) -> bool:
        return self.form in GROUP_SOURCE_FORMS


@dataclass(frozen=True)
class Question:
    id: str
    asker: str
    contexts: tuple[str, ...] | None
    type: str
    question: str
    answer: str
    must_include: tuple[str, ...]
    must_not_include: tuple[str, ...]
    evidence: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class Note:
    path: str  # relative to vaults/, e.g. "team-payments/wiki/orders-api.md"
    context: str
    title: str
    meta: dict
    body: str


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path.name}:{n}: {e}") from e
    return rows


def load_items(root: Path) -> list[Item]:
    items = []
    for r in read_jsonl(root / "sets" / "classification" / "items.jsonl"):
        items.append(
            Item(
                id=r["id"],
                base=r["base"],
                author=r["author"],
                form=r["form"],
                source_kind=r["source"]["kind"],
                source_context=r["source"]["context"],
                text=r["text"],
                category=r["expected"]["category"],
                group=r["expected"]["group"],
                reasons=tuple(r.get("reasons", ())),
                tags=tuple(r.get("tags", ())),
                note=r.get("note", ""),
            )
        )
    return items


def load_questions(root: Path) -> list[Question]:
    qs = []
    for r in read_jsonl(root / "sets" / "retrieval" / "questions.jsonl"):
        gold = r["gold"]
        qs.append(
            Question(
                id=r["id"],
                asker=r["asker"],
                contexts=tuple(r["contexts"]) if r["contexts"] is not None else None,
                type=r["type"],
                question=r["question"],
                answer=gold["answer"],
                must_include=tuple(gold.get("must_include", ())),
                must_not_include=tuple(gold.get("must_not_include", ())),
                evidence=tuple(r["evidence"]),
                note=r.get("note", ""),
            )
        )
    return qs


_FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def parse_note(path: str, text: str) -> Note:
    meta: dict = {}
    body = text
    if m := _FRONT_MATTER.match(text):
        meta = yaml.safe_load(m.group(1)) or {}
        body = text[m.end() :]
    title = str(meta.get("title") or Path(path).stem)
    return Note(path=path, context=context_of(path), title=title, meta=meta, body=body)


def load_notes(vaults: Path) -> list[Note]:
    return [
        parse_note(p.relative_to(vaults).as_posix(), p.read_text())
        for p in sorted(vaults.rglob("*.md"))
    ]
