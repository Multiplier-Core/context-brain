"""Consistency checks for the test sets. CI runs these; a failure means the data is wrong."""

import re
from collections import Counter
from pathlib import Path

from .data import (
    CATEGORIES,
    FORMS,
    GROUP_SOURCE_FORMS,
    QUESTION_TYPES,
    load_items,
    load_notes,
    load_questions,
)
from .org import Org

REASONS = {
    "secret", "health", "family", "personal_finance", "pay_hr", "contact_details", "person_claim",
    "mixed", "transient", "group_source", "addressed", "not_member", "team_decision",
    "team_constraint", "ownership", "service_behaviour", "policy", "tentative", "opinion_on_work",
    "possible_convention", "unclear_audience", "multi_group", "personal_preference",
    "personal_plan", "personal_reminder",
}  # fmt: skip
TAGS = {
    "sensitive_as_work", "work_as_casual", "mixed", "addressed_but_private", "not_member",
    "near_secret", "neutral_person_fact", "cross_group",
}  # fmt: skip

# Real providers' key formats must never appear in this public repository.
REAL_SECRET_FORMATS = re.compile(
    r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abprs]-|sk_(live|test)_|AIza[0-9A-Za-z_-]{20,}"
)
ATTRIBUTION_BY = re.compile(r"\(by: ([a-z]+)")


def check_items(root: Path, org: Org) -> list[str]:
    errors = []
    items = load_items(root)
    for dup, n in Counter(i.id for i in items).items():
        if n > 1:
            errors.append(f"{dup}: duplicate id")
    for i in items:
        where = f"items {i.id}"
        if i.id != f"{i.base}-{i.form}":
            errors.append(f"{where}: id must be <base>-<form>")
        if i.author not in org.people:
            errors.append(f"{where}: unknown author {i.author!r}")
        if FORMS.get(i.form) != i.source_kind:
            errors.append(f"{where}: form {i.form!r} needs source kind {FORMS.get(i.form)!r}")
        if i.form == "chat" and i.source_context is not None:
            errors.append(f"{where}: chat items have no source context")
        if i.form != "chat" and i.source_context not in org.groups:
            errors.append(f"{where}: unknown source context {i.source_context!r}")
        if i.form in GROUP_SOURCE_FORMS and i.source_context not in org.people.get(i.author, []):
            errors.append(f"{where}: author is not a member of {i.source_context}")
        if i.category not in CATEGORIES:
            errors.append(f"{where}: unknown category {i.category!r}")
        if i.category in ("1", "2"):
            if i.group not in org.groups:
                errors.append(f"{where}: category {i.category} needs a group")
            elif not org.can_write(i.author, i.group):
                errors.append(f"{where}: {i.author} can't write to {i.group}")
        elif i.group is not None:
            errors.append(f"{where}: category {i.category} must have group null")
        if i.form in GROUP_SOURCE_FORMS and i.category == "2":
            errors.append(f"{where}: group sources are never category 2")
        if i.form in GROUP_SOURCE_FORMS and i.category == "1" and i.group != i.source_context:
            errors.append(f"{where}: group-source items go to the source group")
        if bad := set(i.reasons) - REASONS:
            errors.append(f"{where}: unknown reasons {sorted(bad)}")
        if bad := set(i.tags) - TAGS:
            errors.append(f"{where}: unknown tags {sorted(bad)}")
        if REAL_SECRET_FORMATS.search(i.text):
            errors.append(f"{where}: uses a real provider's secret format")
    bases: dict[str, set[str]] = {}
    for i in items:
        bases.setdefault(i.base, set()).add(i.form)
    for base, forms in bases.items():
        if missing := {"chat", *GROUP_SOURCE_FORMS} - forms:
            errors.append(f"items {base}: missing forms {sorted(missing)}")
    return errors


def check_vaults(org: Org) -> list[str]:
    errors = []
    for group in org.groups:
        if not (org.vaults / group / "policy.md").exists():
            errors.append(f"vaults: {group}/policy.md is missing")
    for note in load_notes(org.vaults):
        where = f"vaults {note.path}"
        if not note.meta.get("title") or not note.meta.get("type"):
            errors.append(f"{where}: front matter needs title and type")
        if note.context.startswith("personal/"):
            if note.context.removeprefix("personal/") not in org.people:
                errors.append(f"{where}: personal vault of an unknown person")
            continue
        if note.context not in org.groups:
            errors.append(f"{where}: unknown context")
            continue
        for author in ATTRIBUTION_BY.findall(note.body):
            if not org.can_write(author, note.context):
                errors.append(f"{where}: {author} can't write to {note.context}")
        if REAL_SECRET_FORMATS.search(note.body):
            errors.append(f"{where}: uses a real provider's secret format")
    return errors


def check_questions(root: Path, org: Org) -> list[str]:
    errors = []
    questions = load_questions(root)
    notes = {n.path: n for n in load_notes(org.vaults)}
    for dup, n in Counter(q.id for q in questions).items():
        if n > 1:
            errors.append(f"{dup}: duplicate id")
    for q in questions:
        where = f"questions {q.id}"
        if q.asker not in org.people:
            errors.append(f"{where}: unknown asker {q.asker!r}")
        if q.type not in QUESTION_TYPES:
            errors.append(f"{where}: unknown type {q.type!r}")
        if not q.evidence:
            errors.append(f"{where}: needs evidence")
        missing = [e for e in q.evidence if e not in notes]
        if missing:
            errors.append(f"{where}: evidence not found {missing}")
            continue
        readable = [org.can_read(q.asker, notes[e].context) for e in q.evidence]
        evidence_text = " ".join(notes[e].body for e in q.evidence).lower()
        if q.type == "access":
            if any(readable):
                errors.append(f"{where}: access evidence must be unreadable by the asker")
            if q.answer or q.must_include:
                errors.append(f"{where}: access questions have no answer")
            if not q.must_not_include:
                errors.append(f"{where}: access questions need must_not_include")
        else:
            if not all(readable):
                errors.append(f"{where}: asker can't read all the evidence")
            if not q.must_include:
                errors.append(f"{where}: needs must_include")
            for s in q.must_include:
                if s.lower() not in evidence_text:
                    errors.append(f"{where}: {s!r} isn't in the evidence")
        if q.contexts is not None:
            for c in q.contexts:
                if not org.can_read(q.asker, c):
                    errors.append(f"{where}: asker can't attach {c}")
    return errors


def validate(root: Path) -> list[str]:
    org = Org.load(root)
    return check_vaults(org) + check_items(root, org) + check_questions(root, org)
