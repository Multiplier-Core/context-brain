# Working on context-brain

This guide is for AI coding agents and new contributors. Read it before changing anything. `CLAUDE.md` imports this file, so Claude Code, Codex, Cursor and other agents all get the same instructions.

## Where things stand

- **The proposal is merged and is the working baseline.** [docs/decision.md](docs/decision.md) says what we are building and why; [docs/plan.md](docs/plan.md) says in what order.
- **There is no code yet.** The next work is [Phase 0: Foundations](docs/plan.md#phase-0-foundations-12-weeks).
- **Reviewer questions are still open.** The questions in [decision.md §13](docs/decision.md#13-questions-for-reviewers) have not been answered. Build to the default the docs describe, keep it easy to change, and don't settle a question silently (see [Open decisions](#open-decisions)).

## Read first

1. [README.md](README.md): what the project is, in a page.
2. [decision.md §2](docs/decision.md#2-foundational-principle-three-categories-of-information): the three-category principle. Everything else is built around it.
3. [decision.md §7](docs/decision.md#7-architecture): the architecture.
4. The phase of [plan.md](docs/plan.md) you are working on, including its gate criteria.

## Rules that must not be broken

These come from the decision doc. A change that weakens one of them needs an ADR and the maintainers' agreement, not just a PR.

**Sharing (decision.md §2):**
- Every item is sorted into category 1 (group, shared automatically), 2 (uncertain, author's consent asked) or 3 (private, never shared), relative to its author.
- When unsure, fall towards private. An unanswered consent prompt means private.
- Category 3 rules always beat category 1 rules.
- No human approves items on their way into a group brain. Don't add review queues or curator roles.
- Every item records why it was put in its category: the rule that fired, or the rubric scores.
- Authors can edit or retract their own group contributions at any time. A retraction removes the fact from the group vault and its index immediately.

**Personal brains (decision.md §7.3):**
- Personal-brain plaintext never reaches disk, logs, backups, telemetry, error messages or crash reports. Decrypt in memory only, for the owner's session.
- Don't log item content by default anywhere, including for group brains. Log IDs, sizes, categories and timings.
- The operator has no feature for reading a personal brain. Don't add an admin bypass.

**Access and safety:**
- The gateway checks access on every call: the caller's own brain, plus the groups they belong to.
- Credentials and secrets are refused at ingest; they are never stored.
- Never ingest email, Slack direct messages, or workspace-wide crawls (decision.md §7.2).

**Boundaries in the code:**
- Decision models are called only through the decision-model interface (`decision/`). No vendor SDK calls anywhere else.
- Basic Memory is AGPL-3.0. Run it unmodified as a separate process and talk to it over its interface; don't copy its code into this repository. Fixes to Basic Memory go upstream.
- Markdown files are the source of truth. Notes must stay valid Basic Memory and readable in Obsidian.

## Open-source hygiene

This repository is public.
- No real people's data, company-internal names, customer names, Slack workspaces, meeting notes or credentials. The test sets use a fictional organisation (plan.md, Phase 0).
- Nothing specific to one deployment or one sponsoring organisation. Deployment-specific configuration belongs in a fork or in ignored local files (`.env`, `*.local.*`).
- API keys for Jev, Clef or LLM providers come from environment variables and never appear in code, tests, fixtures or examples.

## Open decisions

When code needs one of these, use the default in the docs, keep it configurable where that is cheap, and say in the PR that you relied on it. Once a decision is agreed, record it as an ADR.

| Decision | Current default | Where |
|---|---|---|
| License | Apache-2.0 proposed; **don't add a `LICENSE` file until the sponsoring organisation's open-source policy owner confirms** | decision.md §10 |
| Implementation language | Python for the gateway and pipeline, TypeScript for the web UI | plan.md, repository layout |
| Exact attribution syntax in notes | Illustrative example only; fixed in phase 1 | decision.md §7.4 |
| Classifier thresholds | Starting numbers in §7.6; recalibrated from data | decision.md §7.6 |
| Gate criteria | As proposed; reviewers may change them | plan.md, Gates 1 and 2 |
| One engine instance per unlocked person vs a shared engine | One instance per person | decision.md §13 Q4 |
| Group sources only filter out category 3 | Yes | decision.md §13 Q6 |
| Git per group, with history compaction for retraction | Yes | decision.md §13 Q7 |
| Operator-blind personal brains vs organisation-held keys | Operator-blind, with org-held keys as a config option | decision.md §7.3, §9 |
| Default decision model | Jev; personal-brain judgments routable to self-hosted Clef | decision.md §7.7 |
| Project name | "context-brain" is a working name | decision.md §13 Q9 |

## Architecture decision records

- Store ADRs in `docs/adr/NNNN-short-title.md`, numbered from `0001`.
- Each one has these sections: **Status** (proposed, accepted or superseded), **Context**, **Decision** and **Consequences**.
- The first ADRs restate the agreed parts of decision.md, one decision each, once reviewers have agreed them.
- When an ADR changes something, update decision.md and plan.md in the same PR so the docs don't drift.

## Notes for builders

The docs summarise these points, but they matter when you write code.

**Basic Memory:**
- **Note format.** Notes use observations (`- [category] fact #tag`) and typed relations (`- relation_type [[Entity]]`). Check the [knowledge-format docs](https://docs.basicmemory.com/raw/concepts/knowledge-format.md) for the current syntax for dates and metadata before fixing our attribution format.
- **Deletes and the index.** The watcher's delete handling was fixed in v0.17.x. It is **unverified** whether deleting a note also removes its vector rows. Test it (Phase 1, "Verify"), and run a periodic reconcile; Basic Memory has a `doctor` command.
- **Cloud sync.** Basic Memory Cloud push/pull never deletes at the destination. Don't rely on it for retraction.

**Retrieval and tokens:**
- **Count everything against the budget.** Budget packing must count metadata (IDs, author, source, dates) towards `budget_tokens`, not only the text.
- **Keep tool definitions short.** Each tool definition costs context on every call: vendor figures say 140–320 tokens each **(unverified)**. Put long guidance in the `man` resource, and offer concise and detailed responses.
- **Simple first.** Plain section retrieval over the original text is a strong baseline. Add fact extraction, graph walks, reranking or summary layers only when the eval harness shows a gain.

**Clients:**
- **No automatic recall.** No client saves or recalls on its own. Ship client instructions and hooks with the gateway; Claude Code has session-start and session-end hooks.
- **Gemini.** It asks the person to confirm every write, which shapes the `remember` user experience there.
- **ChatGPT.** Custom remote MCP works reliably on Business and Enterprise plans.

**Vaults and decision models:**
- **Vaults.** Obsidian has no access control inside a vault, so the unit of isolation is one vault per context. Obsidian's headless sync client (`ob sync --continuous`, in beta) can keep a server copy of a group vault.
- **Jev and Clef.** Cloudflare says Clef is Jev-API compatible, so one `decision-api` adapter should serve both. That is a vendor claim: test it with both before relying on it.
- **Vendor numbers.** Treat every vendor benchmark, latency or price in the docs as unverified until our eval harness has measured it.

## Working conventions

**Branches and pull requests:**
- Branch from `main`, open a PR, and squash-merge it.
- Keep PRs small. Each PR says which plan phase and item it advances.

**Tests:**
- Code on a leak path needs tests: classification, access control, encryption, logging and retraction.
- Once the eval harness exists, CI fails if the leak count on the classification set is above zero.

**Docs:**
- Write in plain British English, as the existing docs do ("organisation").
- Use short sentences, tables and bullets.
- Mark unverified claims **(unverified)**, and cite sources.
- When the code and the docs disagree, fix whichever is wrong in the same PR.
