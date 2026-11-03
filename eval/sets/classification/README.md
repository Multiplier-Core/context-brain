# Classification test set

Labelled items for testing the three-category classifier ([decision.md §2](../../../docs/decision.md#2-foundational-principle-three-categories-of-information), [§7.6](../../../docs/decision.md#76-the-three-category-classifier)). Every item is written by a person in the fictional [Tallowmere](../../tallowmere/README.md) organisation and labelled with the outcome the classifier should reach **for that author**.

The file is [items.jsonl](items.jsonl): one item per line.

## Format

```json
{
  "id": "c0007-slack",
  "base": "c0007",
  "author": "alice",
  "form": "slack",
  "source": {"kind": "slack_channel", "context": "team-payments"},
  "text": "fyi idempotency keys on the orders api expire after 24h now",
  "expected": {"category": "1", "group": "team-payments"},
  "reasons": ["group_source", "team_constraint"],
  "tags": ["work_as_casual"],
  "note": "Service constraint stated in the team channel."
}
```

| Field | Meaning |
|---|---|
| `id` | `<base>-<form>`. Unique. |
| `base` | The underlying item. Every form of one base item says the same thing, phrased for that form. |
| `author` | A person in [org.yaml](../../tallowmere/org.yaml). |
| `form` | `chat`, `remember`, `slack`, `meeting` or `document` (see below). |
| `source` | Where the item came from. `context` is the group for group sources and for `remember`, otherwise `null`. |
| `text` | The item, as the classifier receives it. |
| `expected.category` | `"1"`, `"2"`, `"3"`, `"refused"` or `"drop"`. |
| `expected.group` | The group for `"1"`, the group to ask about for `"2"`, otherwise `null`. |
| `reasons` | Codes for why the label is what it is (list below). |
| `tags` | Hard-case tags (list below). Empty for ordinary items. |
| `note` | One line for a human reviewer. |

## Forms

Each base item comes in the four standard forms. Some also have a `remember` form.

| Form | `source.kind` | `source.context` | What it simulates |
|---|---|---|---|
| `chat` | `ai_session` | `null` | A model calling `remember` during a normal AI session, with no group named |
| `remember` | `remember` | the named group | The person says "remember this for team-x" |
| `slack` | `slack_channel` | the channel's group | A message in a Slack channel mapped to a group |
| `meeting` | `meeting_folder` | the folder's group | A statement attributed to the author in meeting notes |
| `document` | `group_document` | the group | A passage from a document dropped into the group's context |

The chat form reads like something a model would save ("Alice prefers…", "Decision: …") or the person's own words. The other forms read like the medium: Slack is short and casual, meeting notes are terse and third-person ("Alice: …"), documents are fuller prose.

In group-source forms the author can always write to the source group (a member, and on its write list). If the base item has no such group, use the author's first writable group in [org.yaml](../../tallowmere/org.yaml).

## Categories

| Label | Meaning | Stored |
|---|---|---|
| `"1"` | Group: shared automatically with `expected.group` | In the group brain |
| `"2"` | Uncertain: the author is asked about sharing with `expected.group` | In the author's personal brain |
| `"3"` | Private | In the author's personal brain; **discarded** for group sources |
| `"refused"` | Contains a credential or secret | Nowhere |
| `"drop"` | Not worth keeping: chit-chat, transient logistics, acknowledgements | Nowhere |

## Labelling rules

Apply these in order. The first rule that fires decides the label.

1. **Secrets → `refused`.** Passwords, API keys, tokens, private keys, connection strings with credentials. Talking *about* a secret ("Paystream keys rotate every 90 days") is not a secret.
2. **Forced private → `"3"`.** Whatever the form, and even if a group was named:
   - health, family, relationships and personal finances;
   - pay, performance reviews, promotions, HR cases;
   - personal contact details (phone numbers, home addresses, personal email);
   - claims about a named person's behaviour, performance, mood or private life (neutral facts like "alice owns the ledger" are not claims);
   - items that mix work content with any of the above (`mixed`). The whole item is private: category 3 beats category 1.
3. **Noise → `"drop"`.** Greetings, thanks, "running 5 minutes late", "lunch?", "+1". Only if nothing in it is forced private.
4. **Group sources (`slack`, `meeting`, `document`) → `"1"` for the source group**, unless the item is about the author rather than the group: their own preferences, plans or reminders → `"3"` (discarded). The audience is already defined, so the classifier filters out only personal content and rules 1–3 ([decision.md §7.2](../../../docs/decision.md#72-ways-in-ingestion)). A tentative idea about the work said in the team channel is still group content.
5. **Explicit addressing (`remember`) → `"1"` for the named group**, if the author can write to it. If they can't (not a member, or not on the write list), → `"3"` with reason `not_member`.
6. **Chat form, judged against the author's groups** (only groups they can write to):
   - **`"1"`:** clearly the group's shared work, matches the group's `policy.md`, durable, useful to other members, and stated as settled. Decisions, constraints, limits, ownership, how a service behaves.
   - **`"2"`:** might belong to a group but isn't clear-cut. Tentative ideas ("thinking we should…"), opinions about the work, personal workflow that might be a team convention, facts whose audience is unclear, or that fit two groups.
   - **`"3"`:** about the author rather than the group: preferences, habits, plans, personal reminders. Also work facts that fit none of the author's writable groups (`not_member`).

When unsure between two labels, choose the more private one: 1 vs 2 → 2, 2 vs 3 → 3.

Standing share rules and personal "always private" lists are not modelled yet. Labels assume none exist.

## Reason codes

| Code | Used for |
|---|---|
| `secret` | Rule 1 |
| `health`, `family`, `personal_finance`, `pay_hr`, `contact_details`, `person_claim` | Rule 2 |
| `mixed` | Rule 2, work content mixed with private content |
| `transient` | Rule 3 |
| `group_source` | Rule 4 |
| `addressed` | Rule 5 |
| `not_member` | Rule 5 or 6: no writable group fits |
| `team_decision`, `team_constraint`, `ownership`, `service_behaviour`, `policy` | What makes it group content |
| `tentative`, `opinion_on_work`, `possible_convention`, `unclear_audience`, `multi_group` | Why it is only category 2 |
| `personal_preference`, `personal_plan`, `personal_reminder` | Why it is category 3 without a forced rule |

## Hard-case tags

| Tag | Meaning |
|---|---|
| `sensitive_as_work` | Private content phrased like a work fact ("blocked Thursday pm: oncology follow-up") |
| `work_as_casual` | Group content phrased casually ("lol the ledger job runs at 2am now") |
| `mixed` | Work and private content in one item |
| `addressed_but_private` | A group was named, but a forced-private rule fires |
| `not_member` | Work content for a group the author can't write to |
| `near_secret` | Talks about credentials without containing one |
| `neutral_person_fact` | Mentions a person neutrally (ownership, role), so not a claim |
| `cross_group` | Fits more than one group |

## Secrets in test data

Every secret in this file is fake. Use made-up formats only (`pst_live_…` for Paystream, `tlm_…` for internal tokens, plain passwords). Never use the formats of real providers (AWS, GitHub, Slack, Stripe, Google and so on), so that secret scanners don't flag this public repository.
