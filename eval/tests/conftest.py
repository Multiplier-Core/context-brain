import json
from pathlib import Path

import pytest

from context_brain_eval import DEFAULT_ROOT
from context_brain_eval.org import Org

ORG_YAML = """
organisation: test
people:
  ann: {role: engineer, groups: [team-a, handbook]}
  ben: {role: engineer, groups: [team-b, handbook]}
groups:
  team-a: {purpose: a, writers: members}
  team-b: {purpose: b, writers: members}
  handbook: {purpose: h, writers: [ann]}
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def note(title: str, body: str) -> str:
    return f"---\ntitle: {title}\ntype: note\n---\n# {title}\n{body}\n"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """A tiny organisation with two teams, a handbook and two personal brains."""
    write(tmp_path / "tallowmere" / "org.yaml", ORG_YAML)
    v = tmp_path / "tallowmere" / "vaults"
    for g in ("team-a", "team-b", "handbook"):
        write(v / g / "policy.md", note(f"{g} policy", "Purpose."))
    write(
        v / "team-a" / "wiki" / "widget.md",
        note(
            "Widget Service",
            "## Facts\n- [constraint] Widget timeout is 42 seconds (by: ann)\n"
            "- [limit] Widget batch size is 7 (by: ann)",
        ),
    )
    write(
        v / "team-b" / "wiki" / "secret-project.md",
        note(
            "Gadget Project",
            "## Facts\n- [decision] Gadget launch codename is Bluebird (by: ben)",
        ),
    )
    write(v / "personal" / "ann" / "prefs.md", note("Ann prefs", "- Ann prefers tea"))
    items = [
        {
            "id": "c1-chat",
            "base": "c1",
            "author": "ann",
            "form": "chat",
            "source": {"kind": "ai_session", "context": None},
            "text": "Widget timeout is 42s",
            "expected": {"category": "1", "group": "team-a"},
            "reasons": ["team_constraint"],
            "tags": [],
            "note": "",
        },
    ]
    for form, kind in (
        ("slack", "slack_channel"),
        ("meeting", "meeting_folder"),
        ("document", "group_document"),
    ):
        items.append(
            {
                **items[0],
                "id": f"c1-{form}",
                "form": form,
                "source": {"kind": kind, "context": "team-a"},
            }
        )
    write(
        tmp_path / "sets" / "classification" / "items.jsonl",
        "".join(json.dumps(i) + "\n" for i in items),
    )
    questions = [
        {
            "id": "r1",
            "asker": "ann",
            "contexts": None,
            "type": "single_fact",
            "question": "What is the widget timeout?",
            "gold": {
                "answer": "42 seconds",
                "must_include": ["42 seconds"],
                "must_not_include": [],
            },
            "evidence": ["team-a/wiki/widget.md"],
            "note": "",
        },
        {
            "id": "r2",
            "asker": "ann",
            "contexts": None,
            "type": "access",
            "question": "What is the gadget launch codename?",
            "gold": {"answer": "", "must_include": [], "must_not_include": ["Bluebird"]},
            "evidence": ["team-b/wiki/secret-project.md"],
            "note": "",
        },
    ]
    write(
        tmp_path / "sets" / "retrieval" / "questions.jsonl",
        "".join(json.dumps(q) + "\n" for q in questions),
    )
    return tmp_path


@pytest.fixture
def org(root: Path) -> Org:
    return Org.load(root)


@pytest.fixture
def real_root() -> Path:
    return DEFAULT_ROOT
