import json

from context_brain_eval.validate import validate


def test_fixture_is_valid(root):
    assert validate(root) == []


def test_group_source_items_cannot_be_category_2(root):
    path = root / "sets" / "classification" / "items.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[1]["expected"]["category"] = "2"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert any("never category 2" in e for e in validate(root))


def test_real_secret_formats_are_rejected(root):
    path = root / "sets" / "classification" / "items.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[0]["text"] = "key AKIA" + "ABCDEFGHIJKLMNOP"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert any("real provider" in e for e in validate(root))


def test_shipped_test_sets_are_valid(real_root):
    assert validate(real_root) == []
