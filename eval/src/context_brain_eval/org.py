"""The fictional organisation: people, groups and who can read or write each context."""

from dataclasses import dataclass
from pathlib import Path

import yaml

PERSONAL_PREFIX = "personal/"


@dataclass(frozen=True)
class Org:
    people: dict[str, list[str]]  # person -> groups, in the order listed
    writers: dict[str, frozenset[str]]  # group -> people who can write to it
    vaults: Path

    @classmethod
    def load(cls, root: Path) -> "Org":
        data = yaml.safe_load((root / "tallowmere" / "org.yaml").read_text())
        people = {name: list(p["groups"]) for name, p in data["people"].items()}
        writers = {}
        for group, g in data["groups"].items():
            if g["writers"] == "members":
                writers[group] = frozenset(p for p, gs in people.items() if group in gs)
            else:
                writers[group] = frozenset(g["writers"])
        return cls(people=people, writers=writers, vaults=root / "tallowmere" / "vaults")

    @property
    def groups(self) -> list[str]:
        return list(self.writers)

    def can_read(self, person: str, context: str) -> bool:
        if context.startswith(PERSONAL_PREFIX):
            return context == PERSONAL_PREFIX + person
        return context in self.people.get(person, [])

    def can_write(self, person: str, context: str) -> bool:
        if context.startswith(PERSONAL_PREFIX):
            return context == PERSONAL_PREFIX + person
        return person in self.writers.get(context, ())

    def readable(self, person: str) -> list[str]:
        """Every context the person can read: their personal brain, then their groups."""
        return [PERSONAL_PREFIX + person, *self.people.get(person, [])]

    def writable_groups(self, person: str) -> list[str]:
        return [g for g in self.people.get(person, []) if self.can_write(person, g)]


def context_of(note_path: str) -> str:
    """The context a note belongs to, from its path relative to vaults/."""
    parts = note_path.split("/")
    if parts[0] == "personal":
        return "/".join(parts[:2])
    return parts[0]
