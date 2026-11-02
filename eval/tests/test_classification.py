from dataclasses import replace

from context_brain_eval.classification import Prediction, Rules, Scores, evaluate, gate_1
from context_brain_eval.data import load_items


def item(root, **changes):
    return replace(load_items(root)[0], **changes)


def test_private_item_shared_is_a_leak(root):
    s = Scores()
    s.add(item(root, category="3", group=None), Prediction("1", "team-a"))
    assert s.leaks == ["c1-chat"]


def test_secret_stored_privately_is_counted_but_not_a_leak(root):
    s = Scores()
    s.add(item(root, category="refused", group=None), Prediction("3"))
    assert s.secrets_stored == ["c1-chat"]
    assert s.leaks == []


def test_wrong_group_hurts_precision_and_coverage(root):
    s = Scores()
    s.add(item(root), Prediction("1", "team-b"))
    s.add(item(root, id="c2-chat"), Prediction("1", "team-a"))
    assert s.wrong_group == ["c1-chat"]
    assert s.precision == 0.5
    assert s.coverage == 0.5


def test_rules_refuse_secrets_and_force_private(org, root):
    rules = Rules(org)
    assert rules.classify(item(root, text="key is pst_live_abc123xyz")).category == "refused"
    assert rules.classify(item(root, text="db password: hunter22")).category == "refused"
    assert rules.classify(item(root, text="Off Friday, hospital appointment")).category == "3"


def test_rules_send_group_sources_to_the_source_group(org, root):
    pred = Rules(org).classify(load_items(root)[1])
    assert (pred.category, pred.group) == ("1", "team-a")


def test_rules_refuse_addressing_a_group_you_cannot_write_to(org, root):
    i = item(root, author="ben", form="remember", source_kind="remember", source_context="handbook")
    assert Rules(org).classify(i).category == "3"


def test_gate_1_uses_direct_forms_for_rates(org, root):
    slices, _ = evaluate(Rules(org), load_items(root))
    gate = gate_1(slices)
    assert gate["leaks"] == (0, True)
    # The chat item is asked about, so direct coverage is zero even though group sources share.
    assert gate["coverage"][0] == 0.0
    assert slices["group-source"].coverage == 1.0
