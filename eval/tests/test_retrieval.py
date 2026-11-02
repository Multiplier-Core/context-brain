from context_brain_eval.data import load_notes, load_questions
from context_brain_eval.retrieval import (
    BM25,
    RETRIEVERS,
    Hit,
    Result,
    allowed_contexts,
    evaluate,
    facts,
    grade,
)


def test_budget_is_honoured_including_metadata(org):
    notes = load_notes(org.vaults)
    bm25 = BM25([u for n in notes for u in facts(n)])
    result = bm25.retrieve("widget timeout batch", ["team-a"], budget_tokens=30)
    assert result.hits
    assert result.tokens <= 30


def test_baselines_never_return_unreadable_contexts(org, root):
    notes = load_notes(org.vaults)
    for name, make in RETRIEVERS.items():
        summary = evaluate(org, make(notes), load_questions(root), 1500)
        assert summary.leaks == [], name


def test_returning_a_forbidden_note_is_a_leak(org, root):
    access = load_questions(root)[1]
    hit = Hit(
        "team-b/wiki/secret-project.md", "team-b/wiki/secret-project.md", "team-b", "Bluebird"
    )
    assert grade(org, access, Result([hit])).access_leak


def test_answerable_needs_every_gold_string(org, root):
    q = load_questions(root)[0]
    hit = Hit("x", "team-a/wiki/widget.md", "team-a", "Widget timeout is 42 seconds")
    assert grade(org, q, Result([hit])).answerable
    assert not grade(org, q, Result([])).answerable


def test_allowed_contexts_drop_unreadable_attachments(org, root):
    q = load_questions(root)[0]
    assert allowed_contexts(org, q) == ["personal/ann", "team-a", "handbook"]
