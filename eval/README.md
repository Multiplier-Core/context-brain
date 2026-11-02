# Evaluation

Public test sets and the harness that measures context-brain against them ([plan.md, Phase 0](../docs/plan.md#phase-0-foundations-12-weeks)). Everything here is built around **Tallowmere**, a fictional organisation, so the sets can be published and reused by anyone.

| Path | What it is |
|---|---|
| [tallowmere/](tallowmere/) | The fictional organisation: people, groups, group policies and vaults of notes |
| [sets/classification/](sets/classification/) | Items labelled with their correct category for their author |
| [sets/retrieval/](sets/retrieval/) | Questions with gold answers over the Tallowmere vaults |
| [src/context_brain_eval/](src/context_brain_eval/) | The harness: loaders, validation, metrics and baselines |

> **Status: pilot.** The sets hold a first batch (about 60 classification items and 25 questions) to settle the formats and labelling rules. They grow to the plan's sizes (about 600 items, 200 notes and 100 questions) once the rules are agreed.

## Running it

Needs [uv](https://docs.astral.sh/uv/).

```bash
cd eval
uv run cb-eval validate                 # check the sets are consistent
uv run cb-eval classify --classifier rules
uv run cb-eval retrieve                 # all retrievers at 500 / 1,500 / 3,000 tokens
uv run pytest
```

`classify` and `retrieve` print Markdown reports. Add `--out results/<name>.json` to keep the raw results.

## What it measures

**Classification** (Gate 1, criteria 1–4):

| Metric | Meaning |
|---|---|
| Leaks | Items labelled category 3 or refused that a classifier put in a group. Counted over every form. Must be zero. |
| Secrets stored | Refused items stored anywhere, personal brains included |
| Auto-share precision | Of the items put in category 1, the share that belong to that group |
| Coverage | Of the items that belong in category 1, the share that got there without a prompt |
| Prompt rate | The share of items that would trigger a consent prompt |
| Wrong group | Group items shared to a different group |

Precision, coverage and prompt rate for the gate are measured on the **direct** forms (`chat`, `remember`). Group sources never prompt, so including them would flatter the prompt rate. Group sources are reported as their own slice.

**Retrieval:**

| Metric | Meaning |
|---|---|
| Answerable | Every gold string appears in the returned context. An upper bound on answer accuracy. |
| Evidence found | At least one evidence note was returned |
| Mean tokens, vs whole | Tokens returned, and as a share of loading every readable note |
| Access passed, leaks | Whether anything came back from a context the asker can't read |

The harness checks every hit against the organisation itself, so a retriever that ignores access control fails even if its answers look right.

## Baselines

| Name | What it does |
|---|---|
| `always-private` | Keeps everything private: zero leaks and zero coverage, the floor |
| `rules` | The layer 1 fixed rules from [decision.md §7.6](../docs/decision.md#76-the-three-category-classifier) as crude regexes; everything else is asked about |
| `whole` | Every note the asker can read, no budget: the comparison point |
| `bm25-sections` | Keyword ranking over note sections, packed into the budget |
| `bm25-facts` | The same over single fact lines, closer to the fact-first `recall` |

## Not done yet

- **LLM-graded answer accuracy.** The plan grades answers with an LLM and checks a sample by hand. The offline "answerable" check comes first because it needs no API key.
- **Real token counts.** Tokens are approximated at four characters per token.
- **Decision-model classifiers.** Jev, Clef and LLM classifiers arrive with the decision-model interface in Phase 1. They will plug in as new entries in `CLASSIFIERS`.
- **Latency and tool-definition tokens.** Measured once there is a gateway to call.

## Private test sets

A deployment can add its own sets in the same format: point `--root` at a directory with the same layout (`tallowmere/org.yaml`, `tallowmere/vaults/`, `sets/…`). Keep private sets out of this repository.
