"""Classification: the classifier contract, baseline classifiers and the metrics behind Gate 1.

A classifier sees what the real pipeline would see: the text, the author, the form and its
source. It never sees the expected label.
"""

import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from .data import CATEGORIES, DIRECT_FORMS, GROUP_SOURCE_FORMS, Item
from .org import Org


@dataclass(frozen=True)
class Prediction:
    category: str
    group: str | None = None
    reason: str = ""


class Classifier(Protocol):
    def classify(self, item: Item) -> Prediction: ...


# --- Baselines ---------------------------------------------------------------------------


class AlwaysPrivate:
    """Keeps everything private. Zero leaks, zero coverage: the floor for any real classifier."""

    def __init__(self, org: Org):
        pass

    def classify(self, item: Item) -> Prediction:
        return Prediction("3", reason="always-private")


_SECRET = re.compile(
    r"\b(pst_(live|test)_\w{6,}|tlm_\w{6,})"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|\b(password|passwd|pwd|passphrase)\s*(is|[:=])\s*\S+"
    r"|\w+://[^\s:/@]+:[^\s@]+@",
    re.IGNORECASE,
)

# Layer 1 forced-private topics. Deliberately crude: this is the "rules only" baseline.
_PRIVATE = {
    "health": r"\b(doctor|hospital|gp|dentist|surgery|therapy|therapist|diagnos\w*|sick|illness"
    r"|migraine|pregnan\w*|oncology|physio\w*|prescription|medication)\b",
    "family": r"\b(my (wife|husband|partner|kids?|son|daughter|sister|brother|mum|dad|mother"
    r"|father)|school (pickup|run)|wedding|funeral|childcare|nursery)\b",
    "personal_finance": r"\b(mortgage|my (rent|loan|debt|savings))\b",
    "pay_hr": r"\b(salary|pay rise|performance review|pip|grievance"
    r"|disciplinary|bonus|notice period|resign\w*)\b",
    "contact_details": r"(\+?\d[\d ]{9,}\d|\b\d+ [A-Z][a-z]+ (Road|Street|Lane|Avenue)\b)",
    "person_claim": r"\b(seemed|seems|stressed|lazy|checked out|sloppy|incompetent|struggling"
    r"|annoyed|upset|rude)\b",
}
_PRIVATE_RES = {k: re.compile(v, re.IGNORECASE) for k, v in _PRIVATE.items()}
_NOISE = re.compile(
    r"^\W*(thanks?|thank you|ty|cheers|lol|\+1|brb|ok(ay)?|nice|morning|hi( all)?|lunch\??"
    r"|running (\d+ (mins?|minutes) )?late)\W*$",
    re.IGNORECASE,
)


class Rules:
    """Layer 1 fixed rules only (decision.md §7.6); anything they don't decide is asked about."""

    def __init__(self, org: Org):
        self.org = org

    def classify(self, item: Item) -> Prediction:
        if _SECRET.search(item.text):
            return Prediction("refused", reason="rule:secret")
        for topic, rx in _PRIVATE_RES.items():
            if rx.search(item.text):
                return Prediction("3", reason=f"rule:{topic}")
        if _NOISE.match(item.text.strip()):
            return Prediction("drop", reason="rule:noise")
        if item.form in GROUP_SOURCE_FORMS:
            return Prediction("1", item.source_context, reason="rule:group-source")
        if item.form == "remember":
            if self.org.can_write(item.author, item.source_context or ""):
                return Prediction("1", item.source_context, reason="rule:addressed")
            return Prediction("3", reason="rule:not-member")
        groups = [g for g in self.org.writable_groups(item.author) if g != "org-handbook"]
        groups = groups or self.org.writable_groups(item.author)
        if not groups:
            return Prediction("3", reason="rule:no-group")
        return Prediction("2", groups[0], reason="rule:ask")


CLASSIFIERS: dict[str, Callable[[Org], Classifier]] = {
    "always-private": AlwaysPrivate,
    "rules": Rules,
}


# --- Metrics -----------------------------------------------------------------------------

LEAK_CATEGORIES = ("3", "refused")
STORED = ("1", "2", "3")


@dataclass
class Scores:
    n: int = 0
    confusion: Counter = field(default_factory=Counter)  # (expected, predicted) -> count
    leaks: list[str] = field(default_factory=list)  # private or secret items shared to a group
    secrets_stored: list[str] = field(default_factory=list)  # refused items stored anywhere
    wrong_group: list[str] = field(default_factory=list)  # group items shared to the wrong group
    shared: int = 0  # predicted category 1
    shared_correctly: int = 0  # predicted 1, expected 1, same group
    true_group: int = 0  # expected category 1
    prompts: int = 0  # predicted category 2

    def add(self, item: Item, pred: Prediction) -> None:
        self.n += 1
        self.confusion[(item.category, pred.category)] += 1
        if pred.category == "1":
            self.shared += 1
            if item.category in LEAK_CATEGORIES:
                self.leaks.append(item.id)
            elif item.category == "1":
                if pred.group == item.group:
                    self.shared_correctly += 1
                else:
                    self.wrong_group.append(item.id)
        if item.category == "refused" and pred.category in STORED:
            self.secrets_stored.append(item.id)
        if item.category == "1":
            self.true_group += 1
        if pred.category == "2":
            self.prompts += 1

    @property
    def precision(self) -> float | None:
        return self.shared_correctly / self.shared if self.shared else None

    @property
    def coverage(self) -> float | None:
        return self.shared_correctly / self.true_group if self.true_group else None

    @property
    def prompt_rate(self) -> float | None:
        return self.prompts / self.n if self.n else None

    @property
    def accuracy(self) -> float | None:
        if not self.n:
            return None
        return sum(c for (e, p), c in self.confusion.items() if e == p) / self.n


# Gate 1 criteria 1–4 (plan.md). Leaks are counted over every form; the rest over direct forms,
# because group sources never prompt and would flatter the prompt rate.
GATE_1 = {"leaks": 0, "precision": 0.98, "coverage": 0.50, "prompt_rate": 0.20}


def evaluate(classifier: Classifier, items: list[Item]) -> tuple[dict[str, Scores], list]:
    """Scores per slice ("all", "direct", "group-source" and each form), plus every prediction."""
    slices: dict[str, Scores] = {"all": Scores(), "direct": Scores(), "group-source": Scores()}
    predictions = []
    for item in items:
        pred = classifier.classify(item)
        predictions.append((item, pred))
        keys = ["all", "direct" if item.form in DIRECT_FORMS else "group-source", item.form]
        for key in keys:
            slices.setdefault(key, Scores()).add(item, pred)
    return slices, predictions


def gate_1(slices: dict[str, Scores]) -> dict[str, tuple[object, bool]]:
    direct = slices["direct"]
    return {
        "leaks": (len(slices["all"].leaks), len(slices["all"].leaks) <= GATE_1["leaks"]),
        "precision": (direct.precision, (direct.precision or 0) >= GATE_1["precision"]),
        "coverage": (direct.coverage, (direct.coverage or 0) >= GATE_1["coverage"]),
        "prompt_rate": (
            direct.prompt_rate,
            direct.prompt_rate is not None and direct.prompt_rate <= GATE_1["prompt_rate"],
        ),
    }


__all__ = ["CATEGORIES", "CLASSIFIERS", "Prediction", "Scores", "evaluate", "gate_1"]
