# context-brain

> **Status: proposal, under review.** There is no code yet. This repository currently holds the design decision and the delivery plan for engineering review.

context-brain is an open-source memory and context engine for AI assistants. Every person gets a **private brain**, and every team or organisation gets a **shared brain**. Any AI tool can use them: Claude, ChatGPT, Gemini, Cursor, coding agents and local models. The brains fill themselves as people work, models pull only the context they need, and people stay in control of everything they contribute.

## Why

- **AI memory is locked to one vendor and one user.** Claude's memory, ChatGPT's memory and every IDE agent's memory are separate silos. Switching model, or working with a colleague, means starting over.
- **Teams know things that no single chat holds.** That includes decisions, constraints, conventions, who owns what, and what changed last week. Today this knowledge is re-explained to every model in every session.
- **Loading "everything" is expensive and makes answers worse.** A brain should hand a model about 1–2k tokens of the right facts, not a 40k-token wiki.
- **Nobody will curate a knowledge base by hand.** The brain has to capture knowledge as a side effect of normal work.
- **People won't adopt a brain that feels like surveillance.** Their personal context must be visibly theirs, and the group must only get what belongs to the group.

## The proposal in brief

- **One principle decides what is shared.** Everything the brain learns is sorted into three categories, relative to the person who contributed it:
  1. **Group:** definitely relevant to the group. It goes to the group brain automatically.
  2. **Uncertain:** the author is asked for consent before it is shared.
  3. **Private:** never leaves the author's personal brain.

  Authors can edit or pull back anything they contributed to a group, at any time. No curator or approval queue sits in the flow.
- **Capture as people work:**
  - AI assistants save durable facts during normal sessions;
  - documents and meeting notes are ingested;
  - Slack channels connected to a group feed that group's brain.
- **Personal brains are private from the operator.** Each one is isolated and encrypted with keys only its owner controls, inside the central deployment.
- **Fact-shaped markdown** in the open-source [Basic Memory](https://github.com/basicmachines-co/basic-memory) format, so models get small, attributed facts within a token budget, and people can read and edit the same files.
- **A thin gateway** is the part this project builds. It is a remote MCP server with OAuth/OIDC, six small tools, the ingest and classification pipeline, and encryption.
- **Any decision model.** Classification runs through a pluggable decision-model interface. TypeSafe's **Jev** is the default; Cloudflare's open-weight **Clef**, an LLM or simple rules can be plugged in per judgment.
- **One codebase, three hosting profiles:** a single person, an organisation behind SSO, and anyone self-hosting. Only the configuration differs.

## Documents

| Document | What it covers |
|---|---|
| [docs/decision.md](docs/decision.md) | The three-category principle, requirements, options evaluated, architecture (ingestion, encrypted personal brains, classification, decision models), hosting profiles, security, risks, and the questions for reviewers |
| [docs/plan.md](docs/plan.md) | Phased delivery plan, go/no-go gates, the evaluation method, and the proposed repository layout |

## How to review

Please comment on the pull request, or open an issue for anything bigger. The decisions we most need challenged are listed in [docs/decision.md § Questions for reviewers](docs/decision.md#13-questions-for-reviewers).

## License

To be decided as part of this review. The proposal is Apache-2.0 for this repository's code; see [docs/decision.md § Licensing](docs/decision.md#10-licensing).
