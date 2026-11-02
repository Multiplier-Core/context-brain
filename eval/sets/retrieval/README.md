# Retrieval test set

Questions with gold answers over the [Tallowmere](../../tallowmere/README.md) vaults. They test whether `recall` finds the right facts within a token budget, and whether it ever returns something the asker can't read.

The notes live in [tallowmere/vaults/](../../tallowmere/vaults/). The questions are in [questions.jsonl](questions.jsonl).

## Vaults

```
vaults/
  team-payments/  team-platform/  team-growth/  org-handbook/
    policy.md
    wiki/<entity>.md        # entity notes: services, people, decisions, processes
    raw/<date>-<slug>.md    # sources: meeting notes, design docs, Slack digests
  personal/<person>/
    <slug>.md               # a person's private notes
```

| Context | Who can read it |
|---|---|
| A group vault | Members of the group ([org.yaml](../../tallowmere/org.yaml)); everyone for `org-handbook` |
| `personal/<person>` | Only that person |

Notes use Basic Memory's format: front matter, then observations (`- [category] fact #tag`) and relations (`- relation_type [[Entity]]`). Group facts carry attribution in brackets, as in [decision.md §7.4](../../../docs/decision.md#74-group-brains-vault-layout-and-note-format):

```markdown
- [constraint] Idempotency keys expire after 24 hours #api (by: alice · src: [[raw/2026-10-12-design-review#Retries]] · from: 2026-10-12)
```

**The attribution syntax is provisional.** Phase 1 fixes it; these notes will be updated to match.

The vaults deliberately contain:
- **duplicates:** the same fact in two notes, or asserted by two people;
- **superseded facts:** an old fact with a `to:` date and the newer fact that replaced it;
- **disputed facts:** conflicting claims recorded under `## Disputed`;
- **raw sources** next to the wiki notes that were written from them.

## Format

```json
{
  "id": "r0003",
  "asker": "bob",
  "contexts": null,
  "type": "temporal",
  "question": "What was the refund approval limit before October 2026?",
  "gold": {
    "answer": "£250; it was raised to £500 on 2026-10-01.",
    "must_include": ["£250"],
    "must_not_include": []
  },
  "evidence": ["team-payments/wiki/refunds-service.md"],
  "note": "Superseded fact; the old value is still recorded with a to: date."
}
```

| Field | Meaning |
|---|---|
| `asker` | A person in [org.yaml](../../tallowmere/org.yaml). Retrieval may only use contexts they can read. |
| `contexts` | The contexts the session attached, or `null` for everything the asker can read. |
| `type` | One of the types below. |
| `gold.answer` | The correct answer in a sentence. Empty for `access` questions. |
| `gold.must_include` | Short strings a correct answer contains. Used by the offline grader. |
| `gold.must_not_include` | Strings that must not appear: wrong old values, or content the asker can't read. |
| `evidence` | Notes (paths relative to `vaults/`) that hold the answer. For `access` questions, the note the asker must **not** see. |

## Question types

| Type | What it tests |
|---|---|
| `single_fact` | One fact in one note |
| `entity_summary` | A short summary of one entity |
| `multi_step` | Facts from two or more notes in one context, combined |
| `temporal` | What was true before a change ("what was X before…") |
| `disputed` | A fact with conflicting claims; a good answer reports both |
| `cross_context` | Needs two contexts the asker can read (e.g. their personal brain and a group) |
| `access` | The answer exists only in a context the asker **can't** read. The correct result is "not found", and returning that note is a leak. |
