# Delivery plan

| | |
|---|---|
| **Status** | Draft for engineering review |
| **Depends on** | [decision.md](decision.md) |
| **Assumes** | Two engineers, roughly full-time, plus part-time help from security and a pilot team. Durations are estimates for reviewers to challenge. |

---

## Overview

| Phase | Goal | Estimate | Ends with |
|---|---|---|---|
| 0. Foundations | Repo, license, evaluation set and harness | 1 week | A public eval set and a baseline measurement script |
| 1. Prototype and gate | Prove the format and the token savings; compare against managed options | 2–3 weeks | **Gate 1: build or adopt** |
| 2. Gateway core | Remote MCP with auth, access control and the five tools; personal profile | 3–4 weeks | Usable by individuals from any MCP client |
| 3. Ingest, judges and groups | Ingest pipeline, judge interface (Jev + LLM), capture, organisation profile, pilot | 4–6 weeks | **Gate 2: pilot review** |
| 4. Tuning and public release | Judge bake-off, reranking, entity matching, community packaging, security review | 3–4 weeks | v0.1 public release |

That is about 3–4 months in total to a public v0.1, with a decision point after week 3–4 where we can stop cheaply.

## Phase 0: Foundations (1 week)

- Create the public repository, with the license (proposed Apache-2.0, pending the open-source policy owner), `CONTRIBUTING.md`, a code of conduct and a security policy.
- Record the decisions in [decision.md](decision.md) as ADRs once reviewers agree.
- **Build the public evaluation set.** It is a synthetic, fictional organisation, so it can be published and reused by anyone:
  - about 200 notes across 4 contexts, covering people, services, decisions and projects, with deliberate duplicates, superseded facts and conflicting claims
  - about 100 questions with gold answers, covering these types:

    | Type | Example |
    |---|---|
    | Single fact | "When do idempotency keys expire?" |
    | Entity summary | "What do we know about the Ledger Service?" |
    | Multi-hop | "Who owns the service the Orders API depends on?" |
    | Temporal | "What was the rate limit before October?" |
    | Disputed | "What is the p99 target?" (must surface both claims) |
    | Cross-context | Questions that need two attached contexts |
    | **Access** | Questions whose answer sits in a context the caller **cannot** read (must not leak) |
    | Sensitive | Writes containing secrets or personal data (must be blocked or kept private) |

- **Build the harness.** It runs a question set against a retrieval method and records answer accuracy (LLM-graded against the gold answers, with a sample checked by hand), tokens returned, tool-definition tokens and latency.
- Each deployment can add its own **private** question set in the same format. The organisation pilot will.

## Phase 1: Prototype and gate (2–3 weeks)

**Build** (throwaway quality is fine):
- Finalise the note format: observations, relations, attribution, valid-from/to, `## Disputed`. Check that it stays valid Basic Memory syntax and renders well in Obsidian.
- Run Basic Memory locally over the eval vaults, exposed over stdio to Claude Code and Claude Desktop.
- Hand-write a minimal `recall` that packs facts first and then sections into a budget, as a script or a thin MCP wrapper.

**Measure** on the public eval set:

| Method | What it tells us |
|---|---|
| Load the whole vault | Accuracy ceiling and token cost to beat |
| Basic Memory search + section reads, as is | What the engine gives for free |
| Fact-first budgeted recall (ours) at 500 / 1,500 / 3,000 tokens | Whether our layer earns its keep |
| Basic Memory Cloud/Teams, Supermemory, Shifu (where they can load the data) | The adopt-instead options |

**Verify:**
- Deleting or editing a note in Obsidian is reflected in search. If not, design the reconcile job.
- MCP connection and OAuth flow from claude.ai, ChatGPT and Gemini to a stub server, to confirm the client matrix.

### Gate 1: build or adopt

Proposed pass criteria for continuing with the build (reviewers, please challenge the numbers):
1. Fact-first recall at **≤1.5k tokens** reaches answer accuracy **within 5 points** of loading the whole vault, using **≤10% of its tokens**.
2. It beats Basic Memory's out-of-the-box search on accuracy per token by a clear margin. Otherwise we don't need our own recall layer, only the gateway.
3. No managed option matches it on accuracy and tokens while also meeting R4–R6 for the organisation profile.

If (3) fails, adopt the managed option. This repository then keeps the format spec, the eval set and the client setup guides.

## Phase 2: Gateway core (3–4 weeks)

- **Gateway service:**
  - remote MCP over streamable HTTP
  - OAuth 2.1 with dynamic client registration
  - a built-in single-user auth server, plus OIDC federation
- **Access control:** identity → contexts with read/write. Checked on every call; results are never merged across contexts the caller can't read.
- **The five tools:** `profile`, `recall` (budgeted, fact-first), `read`, `outline`, `remember` (to `inbox/` only), plus the `man` resource.
- **Storage adapter** over Basic Memory, run as a separate process. No changes to Basic Memory itself.
- **Audit log and token metering** per call.
- **Personal profile recipe:**
  - a laptop install (stdio)
  - a small VPS or tunnel for web clients
  - setup guides for Claude, ChatGPT, Gemini, Cursor and Claude Code (including a session-start hook).
- **Tests:** the access questions from the eval set pass with **zero leakage**, and token budgets are honoured, metadata included.

**Exit:** the team building it uses it daily from at least three different clients.

## Phase 3: Ingest, judges and groups (4–6 weeks)

- **Ingest worker,** a single writer per context. It takes inbox items and sweep transcripts and produces facts and relations in entity notes. It also dedupes, marks superseded facts, records disputes, recompiles `profile.md`, and makes a git commit per batch.
- **Judge interface** with three question types (Noul, Choice, Score), plus:
  - **Jev provider** (recommended)
  - **LLM provider** (OpenAI-compatible and Anthropic, structured output)
  - provider and thresholds configurable **per judgment**.
- **Judgments wired in:**
  - durable-fact gate
  - context and entity routing
  - duplicate and entity matching
  - supersede or contradict
  - **private or shareable**
- **Review queue:** `review/` in each vault, plus a simple web view, for decisions between the thresholds.
- **Capture:** `remember` (scoop), transcript sweep where the harness exposes it, and session-start hooks.
- **Security controls:** secret scanning on writes, write allowlists per context, provenance framing in `recall` output, and audit export.
- **Organisation profile recipe:**
  - OIDC to the org's identity provider, with IdP groups mapped to contexts
  - one git repository per context
  - a container deployment (Helm)
  - backups, retention settings, and a documented erasure procedure.
- **Pilot:** one or two volunteer teams in the sponsoring organisation, each with a team context plus personal contexts, for at least two weeks.

### Gate 2: pilot review

| Measure | Proposed target |
|---|---|
| Cross-context leakage in access tests and the pilot | **Zero** (any leak blocks the release) |
| Sensitive-write detection on the labelled set | ≥ 95% caught; misses reviewed one by one |
| Ingest fact precision (sampled by hand) | ≥ 90% |
| Duplicate detection (precision / recall) | ≥ 90% / ≥ 80% |
| Review-queue load | Small enough that a context owner clears it in about 10 minutes a week |
| Pilot answer accuracy on their private questions | At or above whole-context loading, at ≤ 15% of the tokens |
| Pilot users | Would keep using it (a short survey); can fix a wrong fact without engineering help |

## Phase 4: Tuning and public release (3–4 weeks)

- **Judge bake-off:** Jev, the LLM provider and a local small model on every judgment, on the public eval set. Measure accuracy, calibration, latency and cost per 1,000 writes. Publish the results and set the recommended defaults per profile from them.
- **Retrieval tuning,** adopted only where the eval set shows a gain:
  - reranking (Jev against a local cross-encoder)
  - entity matching in `recall`
  - summary layers per folder.
- **Community profile:** Docker Compose, a quick-start guide, an example vault template, and LLM-judge defaults so no proprietary service is needed.
- **Security review** of the gateway and the organisation profile, by the sponsoring organisation's security team.
- **Release v0.1:** docs site, changelog, the published eval results, and the issue templates.

## Repository layout (proposed)

```
context-brain/
  docs/            decision.md, plan.md, adr/, guides/ (clients, hosting profiles)
  spec/            note format and tool contract (versioned)
  gateway/         MCP server: auth, ACL, tools, budget packer, audit, storage adapter
  ingest/          ingest worker, lint, profile compiler
  judges/          interface + providers: jev/, llm/, local/
  deploy/          personal/, compose/, helm/
  eval/            public synthetic dataset, harness, published results
  examples/        vault template with AGENTS.md conventions
```

The implementation language is open for review. The proposal is Python, to match Basic Memory and the MCP and ML tooling around it.

## What we need from reviewers and the organisation

- **Engineering leaders:** challenge the decision ([questions](decision.md#13-questions-for-reviewers)), the gate criteria and the estimates.
- **People:** two engineers for about 3–4 months, and a part-time security reviewer from phase 3.
- **Pilot:** one or two volunteer teams for phase 3.
- **Approvals:** the open-source policy owner (license, publishing under the org), and data protection (Jev and LLM providers as processors for the organisation profile).
- **Budget:** small. It covers hosting for the pilot, judge and LLM usage during evaluation, and trial seats of the managed options for Gate 1.
