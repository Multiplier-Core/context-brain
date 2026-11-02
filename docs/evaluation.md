# Evaluation

What we evaluate, how, and how far each part has got. The harness and test sets live in [eval/](../eval/); this page is the map. It follows [plan.md, Phase 0](plan.md#phase-0-foundations-12-weeks) and the gates in [plan.md](plan.md#gate-1-is-automatic-classification-trustworthy).

> **Status (November 2026): pilot.** The classification and retrieval sets exist at about a quarter of their planned size. Extraction from sources (including code repositories and bulk imports), capture during AI sessions and group maintenance are not evaluated yet.

## What we are evaluating

Every way into the brain feeds one pipeline ([decision.md §7.2](decision.md#72-ways-in-ingestion)), and the AI reads it back through `recall`. Each stage needs its own evaluation, because a failure at one stage hides behind the others.

| Stage | The question it answers | Evaluated? |
|---|---|---|
| 1. Capture | Does the right material get picked up? The model calls `remember` at the right moments in a session; the end-of-session sweep finds what it missed. | **No** |
| 2. Extraction | From a raw source (a Slack thread, meeting transcript, long document, repository, merged PR, bulk import), are the right facts pulled out, with the right author? For bulk sources, does selective extraction beat indexing sections alone? | **No** |
| 3. Secret scan | Are credentials refused before anything is stored? Repositories are where most of them live. | **Partly**: on single items, not on repository files |
| 4. Classification | Is each fact put in the right category (group, ask, private, refused, drop) and the right group? | **Yes** |
| 5. Group maintenance | Are duplicates merged, superseded facts marked and disputes recorded? Do facts about code follow the code as it changes, and do newer imported documents win over older ones? | **No** |
| 6. Retrieval | Does `recall` return what answers the question, within the token budget? | **Partly**: offline check only |
| 7. Access control | Does anything come back from a context the asker can't read? | **Yes**, on the retrieval set |

Encryption, logging and retraction are tested as code (unit and integration tests), not with eval sets. They arrive with the code in Phases 1–3.

## Coverage by way in

The ways in come from [decision.md §7.2](decision.md#72-ways-in-ingestion). Notion, PDFs and document folders arrive through **bulk import** ([§7.10](decision.md#710-bulk-import)) or as uploaded documents.

| Way in | Capture | Extraction | Classification | Freshness | Test form |
|---|---|---|---|---|---|
| AI saves as it works (incl. coding sessions) | Not started | Not needed: the model writes the fact | Done; the repository hint for coding sessions isn't tested | — | `chat` |
| "Remember this" (group named) | Not needed | Not needed | Done, thin (12 rows) | — | `remember` |
| End-of-session sweep | Not started | Not started | Covered by `chat` once facts are out | — | — |
| Slack channels | Not needed: the app reads every message | Not started | Done, one message at a time | — | `slack` |
| Meeting notes | Not needed | Not started | Done, one statement at a time | — | `meeting` |
| Documents | Not needed | Not started | Done, one passage at a time | — | `document` |
| Code repositories: merged PRs | Not needed: the CI step sends every merge | Not started | Not started (no PR form yet) | Not started | — |
| Code repositories: files | Not needed | Not started | Secret scan not tested on files | Not started | — |
| Bulk import (repositories, Notion, PDFs, folders) | Not needed | Not started | Covered by the group-source forms once facts are out | Not started: older vs newer documents | — |
| Direct edits, API and CLI | Not needed | Not needed | Secret scan only, not tested separately | — | — |

"Done" for a group source means the classifier is tested on a statement that has already been cut out of the source. Turning a whole thread, transcript, document or repository into those statements is the extraction stage, which isn't evaluated yet. "Freshness" means facts follow their source as it changes.

## What is done

### Fictional organisation

[eval/tallowmere/](../eval/tallowmere/) holds Tallowmere: 10 people, 4 groups (three teams and an org handbook with a restricted write list), a `policy.md` per group and vaults of notes. Everything in the public sets is built on it, so nothing real is published.

### Classification set

[eval/sets/classification/](../eval/sets/classification/): 60 base items, written in up to five forms, 252 rows. The labelling rules are in its README.

| Form | Simulates | Rows |
|---|---|---|
| `chat` | A model calling `remember` in an AI session, no group named | 60 |
| `remember` | "Remember this for team-x" | 12 |
| `slack` | A message in a channel mapped to a group | 60 |
| `meeting` | A statement attributed to someone in meeting notes | 60 |
| `document` | A passage from a document dropped into a group | 60 |

| Expected outcome | Rows |
|---|---|
| 1: group | 122 |
| 2: ask the author | 12 |
| 3: private | 69 |
| Refused (secret) | 25 |
| Drop (noise) | 24 |

Hard cases are tagged so they can be scored on their own:

| Tag | Rows |
|---|---|
| Sensitive content phrased as work | 31 |
| Work and private content mixed | 21 |
| Neutral fact about a person (not a claim) | 13 |
| Fits more than one group | 12 |
| Group content phrased casually | 8 |
| Talks about a credential without containing one | 8 |
| Author not a member of the group | 5 |
| Group named, but private content | 4 |

**Metrics** (Gate 1, criteria 1–4): leaks over every form; secrets stored anywhere; auto-share precision, coverage and prompt rate on the direct forms (`chat`, `remember`); items shared to the wrong group; a confusion matrix. Group sources are reported as their own slice, because they never prompt and would flatter the prompt rate.

### Retrieval set

[eval/sets/retrieval/](../eval/sets/retrieval/): 42 notes across the group vaults and three personal vaults, with deliberate duplicates, 10 superseded facts and 6 disputes. 25 questions:

| Type | Questions |
|---|---|
| Access (the asker must not see the answer) | 5 |
| Single fact | 4 |
| Temporal ("what was true before") | 4 |
| Entity summary | 3 |
| Multi-step | 3 |
| Disputed | 3 |
| Cross-context (personal plus group) | 3 |

**Metrics:** answerable (every gold string is in the returned context), evidence found, tokens returned and their share of loading the whole vault, and access leaks. Every hit is checked against the organisation's access rules, so a retriever that ignores access control fails even when its answers look right.

### Harness and baselines

`cb-eval` validates the sets, runs classifiers and retrievers, and prints Markdown reports ([eval/README.md](../eval/README.md)). CI runs validation, lint and tests on every PR.

| Baseline | Result on the pilot sets |
|---|---|
| `always-private` | 0 leaks, 0% coverage: the floor |
| `rules` (layer 1 regexes, everything else asked) | 33 leaks, 68% prompt rate: fails Gate 1, as expected |
| `whole` (every readable note) | The comparison point for retrieval |
| `bm25-facts` at 1,500 tokens | 100% answerable at about 35% of the whole vault's tokens; no access leaks |

The retrieval numbers say little yet: the pilot vault is about 4k tokens, so the whole vault is cheap. They become meaningful at the planned 200 notes.

## What is not done

### Missing evaluations

| Evaluation | What it would contain | What it would measure | Needed by |
|---|---|---|---|
| **Extraction from sources** | Raw Slack threads, meeting transcripts and long documents, each with the gold list of facts, their authors and their categories | Fact recall and precision against the gold list; author attribution (speakers in transcripts, senders in threads); leaks once the extracted facts are classified | Phase 1 |
| **Code set** | Three or four small fictional repositories for Tallowmere's services: READMEs, ADRs, `CODEOWNERS`, interface definitions, merged PR threads (some with remarks about people), fake secrets in the usual files, and a merge history that changes facts. Gold facts per repository, plus retrieval questions about the code. | Fact recall and precision; secrets refused; remarks about people filtered; after replaying the merge history, superseded facts marked and none left stale; answer accuracy on the code questions | Phase 1 |
| **Import set** | A Notion-style export (pages with headings, tables and comments) and a folder of PDFs and Office files spanning several years, where older documents contradict newer ones | Index-only vs selective extraction vs extracting everything: answer accuracy, tokens, and cost per 1,000 documents; conflicts resolved in favour of the newer source; undo removes everything the import added | Phase 1 |
| **Pull-request form** | A `pr` form for the classification items, like the Slack form | The category 3 filter on review threads | Phase 1 |
| **Capture in AI sessions** | Session transcripts with the facts the model should have saved marked up, plus chatter it shouldn't save | Save recall, unwanted saves, leaks; the same transcripts test the end-of-session sweep | Phase 2 |
| **Group maintenance** | Sequences of incoming facts against an existing vault | Duplicates merged, superseded facts marked with dates, disputes recorded rather than overwritten, no facts lost | Phase 3 |
| **LLM-graded answers** | The existing questions, answered by a model from the returned context | Answer accuracy, with a sample checked by hand (Gate 1, criterion 5) | Phase 1 |
| **Unanswerable questions** | Questions whose answer isn't in any readable context | Whether the answer says "not known" rather than guessing | Phase 1 |
| **Deciding to recall** | Sessions where the model should, and shouldn't, call `recall` | Recall calls made when needed; wasted calls | Phase 2 |
| **Repository hint** | Coding-session items with the repository's group as a hint, including personal remarks made while coding | The hint raises coverage without raising leaks | Phase 2 |
| **Real token counts, tool-definition tokens, latency** | — | Measured once there is a gateway to call | Phase 1–2 |

### Gaps in the existing sets

- **Size.** The plan calls for about 600 classification items, 200 notes and 100 questions. The pilot has 252 rows, 42 notes and 25 questions, so each question type has only three to five questions.
- **Category 2 and `remember` are thin** (12 rows each), so the prompt rate isn't reliable yet.
- **Facts don't line up across the sets.** Some facts in the classification items differ from the same facts in the retrieval notes (for example, when the ledger reconciliation runs). They should agree before the sets grow.
- **Labels to review.** Some pilot labels are debatable (hearsay, exam plans as HR, cross-group items). They are listed in the PR that added the sets.
- **Standing share rules** and personal "always private" lists aren't modelled; labels assume none exist.
- **Decision-model classifiers** (Jev, Clef, an LLM) plug into the harness in Phase 1, with the decision-model interface.

## Gate criteria and where they are measured

| Gate criterion | Measured by | Ready? |
|---|---|---|
| Gate 1.1: zero leaks | Classification set, every form | Yes, on the pilot set |
| Gate 1.2: auto-share precision ≥ 98% | Classification set, direct forms | Yes, on the pilot set |
| Gate 1.3: coverage ≥ 50% | Classification set, direct forms | Yes, on the pilot set |
| Gate 1.4: prompt rate ≤ 20% | Classification set, direct forms | Partly: too few category 2 rows |
| Gate 1.5: retrieval within 5 points of the whole vault at ≤ 10% of its tokens | Retrieval set | No: needs LLM grading and the full-size vault |
| Gate 1.6: encryption unlock time and memory | Encryption spike (Phase 1) | No |
| Extraction variants for repositories and bulk imports (not a gate; decides index-only or selective extraction) | Code and import sets | No: sets not built |
| Gate 2, including stale code facts, secrets from repositories and import cost | Pilot audit and the pilot's private sets | No: Phase 3 |

## Private test sets

A deployment can add its own sets in the same format and point `cb-eval --root` at them. The pilot will. Private sets stay out of this repository.
