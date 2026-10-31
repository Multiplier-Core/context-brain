# context-brain

> **Status: proposal, under review.** There is no code yet. This repository currently holds the design decision and the delivery plan for engineering review.

context-brain is an open-source memory and context engine for AI assistants. It gives a person, a team or a whole organisation one shared "brain" that any AI tool can use: Claude, ChatGPT, Gemini, Cursor, coding agents and local models. Models can pull exactly the context they need, using as few tokens as possible. People can read, fix and delete everything in it with ordinary tools such as Obsidian, a web UI or git.

## Why

- **AI memory is locked to one vendor and one user.** Claude's memory, ChatGPT's memory and every IDE agent's memory are separate silos. Switching model, or working with a colleague, means starting over.
- **Teams know things that no single chat holds.** That includes decisions, constraints, conventions, who owns what, and what changed last week. Today this knowledge is re-explained to every model in every session.
- **Loading "everything" is expensive and makes answers worse.** A brain should hand a model about 1–2k tokens of the right facts, not a 40k-token wiki.
- **The people the brain describes must be able to see and correct it.** That rules out black-box vector stores.

## The proposal in one paragraph

Store the brain as **fact-shaped markdown files**, one folder (vault) per context, using the open-source [Basic Memory](https://github.com/basicmachines-co/basic-memory) format and engine. Put a **thin gateway** in front of it, which is the part this project builds. The gateway is a remote MCP server with OAuth/OIDC, access control per context, and five small tools with a token budget. It also runs an **ingest pipeline** that turns raw notes into deduplicated, attributed facts. The small judgments that pipeline makes run through a swappable **judge interface**. These are questions such as "keep or drop?", "duplicate?", "superseded?" and "private?". TypeSafe's **Jev** decision model is the recommended judge, and an LLM judge ships so the project has no required proprietary dependency. The same container image serves a single person on a laptop, an organisation behind SSO, and anyone self-hosting it publicly; only the configuration differs.

## Documents

| Document | What it covers |
|---|---|
| [docs/decision.md](docs/decision.md) | Requirements, the options we evaluated, the decision, the architecture, Jev's role, hosting profiles, risks, and the questions for reviewers |
| [docs/plan.md](docs/plan.md) | Phased delivery plan, go/no-go gates, the evaluation method, and the proposed repository layout |

## How to review

Please comment on the pull request, or open an issue for anything bigger. The decisions we most need challenged are listed in [docs/decision.md § Questions for reviewers](docs/decision.md#13-questions-for-reviewers).

## License

To be decided as part of this review. The proposal is Apache-2.0 for this repository's code; see [docs/decision.md § Licensing](docs/decision.md#10-licensing).
