# Delivery plan

| | |
|---|---|
| **Status** | Draft for engineering review |
| **Depends on** | [decision.md](decision.md) |
| **Assumes** | Two engineers, roughly full-time, plus a part-time security engineer from phase 2 and a pilot team in phase 3. Durations are estimates for reviewers to challenge. |

---

## Overview

The riskiest assumption is that **automatic three-category classification is accurate enough to run without a human in the loop**. The plan tests that first, before building the rest.

| Phase | Goal | Estimate | Ends with |
|---|---|---|---|
| 0. Foundations | Repo, license, public test sets and harness | 1–2 weeks | Test sets for retrieval and classification, and a baseline script |
| 1. Prototype and gate | Prove the classifier and the token savings | 3–4 weeks | **Gate 1: is automatic classification trustworthy?** |
| 2. Gateway and personal brains | Remote MCP, six tools, classification on `remember`, encrypted personal brains, web UI v0 | 5–6 weeks | Individuals use it daily from any client |
| 3. Ways in and organisation | Documents, meeting notes, Slack, group maintenance, decision-model interface, organisation profile, pilot | 5–6 weeks | **Gate 2: pilot review** |
| 4. Tuning and public release | Decision-model bake-off, recalibration, community packaging, security review | 3–4 weeks | v0.1 public release |

That is about 4–5 months in total to a public v0.1. Gate 1, after about 5 weeks, is the cheap place to stop or change course.

## Phase 0: Foundations (1–2 weeks)

- Create the repository with its license (proposed Apache-2.0, pending the open-source policy owner), `CONTRIBUTING.md`, a code of conduct and a security policy.
- Record the decisions in [decision.md](decision.md) as ADRs once reviewers agree.
- **Public test sets,** built around a fictional organisation so they can be published and reused by anyone:
  - **Organisation:** about 10 personas across 4 groups, each group with a `policy.md`.
  - **Retrieval set:**
    - about 200 notes, with deliberate duplicates, superseded facts and conflicting claims;
    - about 100 questions with gold answers. They cover single facts, entity summaries, multi-step questions, "what was true before", disputed facts, questions that need two contexts, and **access** questions whose answer the caller must not see.
  - **Classification set:** about 600 items, each labelled with its correct category for its author. Examples:

    | Example item | Correct category |
    |---|---|
    | "Orders API idempotency keys expire after 24 hours" | 1: group |
    | "Thinking we should move standup to 10am" | 2: uncertain |
    | "I prefer tabs over spaces" | 3: private |
    | "My school pickup is at 3pm" | 3: private, sensitive |
    | "A colleague seemed checked out in standup" | 3: private, claim about a person |
    | An API key pasted into a chat | Refused |

    It deliberately includes hard cases: sensitive content phrased as work, work content phrased casually, and mixed items. Each item also comes in Slack, meeting-note and document form.
- **Harness:**
  - **Retrieval:** answer accuracy (LLM-graded, with a sample checked by hand), tokens returned, tool-definition tokens and latency.
  - **Classification:** a confusion matrix across the three categories, **leak count** (category 3 items that reached a group), auto-share precision, coverage, and prompts per 100 items.
- Each deployment can add **private** sets in the same format. The pilot will.

## Phase 1: Prototype and gate (3–4 weeks)

**Build** (throwaway quality is fine):
- Finalise the note format: observations, relations, attribution, valid-from/to, `## Disputed`, and the "why shared" field. It must stay valid Basic Memory and render well in Obsidian.
- Run Basic Memory over the test vaults; hand-write a budgeted, fact-first `recall`.
- **Classifier prototype:**
  - the layer 1 fixed rules;
  - the layer 2 rubric, against **Jev**, **Clef** and an **LLM**, each called directly;
  - layer 3 thresholds, with a first calibration per model.

**Measure:**

| What | Compared |
|---|---|
| Retrieval accuracy and tokens | Whole vault vs Basic Memory search as-is vs our recall at 500 / 1,500 / 3,000 tokens |
| Classification quality | Rules only vs rules + Jev vs rules + Clef vs rules + LLM |
| Classification on group sources | The category 3 filter on Slack, meeting-note and document versions of the items |

**Verify:**
- Edits and deletes in a vault reach the search index.
- Remote MCP and OAuth sign-in work from claude.ai, ChatGPT and Gemini, against a stub server.
- **Encryption spike:** passkey PRF key wrapping, plus decrypting a vault and its index in memory for one session with an engine instance per person. Measure memory use and time to unlock.

### Gate 1: is automatic classification trustworthy?

These are the proposed pass criteria. Reviewers, please challenge the numbers.

1. **Zero leaks.** No category 3 item reaches a group on the classification set, with the best decision model and thresholds.
2. **Auto-share precision ≥ 98%.** Items placed in category 1 really belong to the group.
3. **Coverage ≥ 50%.** At least half of the true category 1 items reach the group without a prompt. Below that, the group brain fills too slowly to be worth it.
4. **Prompt rate ≤ 20%.** At most a fifth of items trigger a consent prompt.
5. **Retrieval:** recall at ≤ 1.5k tokens reaches answer accuracy within 5 points of loading the whole vault, at ≤ 10% of its tokens.
6. **Encryption:** unlocking takes about 2 seconds or less for a vault of 5k notes, and memory per active person fits the expected hardware.

**If 1–2 pass but 3–4 don't,** we narrow category 1 to fixed rules only (explicit addressing and group sources) and send the rest through consent. **If 1 fails,** we stop and rethink the principle with reviewers before building anything more.

## Phase 2: Gateway and personal brains (5–6 weeks)

- **Gateway:**
  - remote MCP over streamable HTTP;
  - OAuth 2.1 with dynamic client registration;
  - a built-in single-user auth server, and OIDC federation.
- **Access control:** a person's own brain plus the groups they belong to, checked on every call.
- **The six tools:** `profile`, `recall`, `read`, `outline`, `remember` (classified on arrival, returns a receipt), `update` (share, keep private, edit, retract), plus the `man` resource.
- **Classifier in the write path:** fixed rules, then the rubric through a first version of the decision-model interface with Jev (default) and LLM adapters, then the thresholds.
- **Encrypted personal brains:**
  - **Keys:** a key pair per person; the private key wrapped by a passkey (PRF) or passphrase; a recovery key at enrolment.
  - **Writes while locked:** new items are encrypted to the person's public key.
  - **Session unlock:** the vault and index are decrypted in memory only, for that session, in an engine instance dedicated to that person. Idle instances are evicted.
  - **Export:** decrypted markdown.
- **Group vaults:** one per group, with `policy.md`.
- **Web UI v0:**
  - "my contributions": where each item went and why;
  - the consent digest;
  - edit and retract;
  - managing standing share rules and the "always private" list;
  - browsing group brains.
- **Personal profile recipe,** plus client setup guides and hooks: instructions for proactive `remember`, and Claude Code session-start and session-end hooks.
- **Tests:**
  - zero leakage on the access questions;
  - stored personal data is ciphertext (checked by inspecting disk and backups as an admin would);
  - token budgets are honoured.

**Exit:** the team uses it daily from at least three different clients, and has looked through its own auto-shared items.

## Phase 3: Ways in and the organisation (5–6 weeks)

- **Documents and meeting notes:**
  - upload in the web UI;
  - a drop folder per context;
  - connected folders per group (e.g. a Drive folder where meeting transcripts land);
  - speaker attribution for meeting notes where the transcript provides it.
- **Slack:**
  - an internal Slack app recipe, installed by each deployment in its own workspace;
  - channel-to-group mapping by inviting the app;
  - message-level authorship, so senders can retract.
- **End-of-session sweep,** opt-in per person.
- **Group maintenance:** entity matching, dedupe with co-asserters, supersede and dispute, all with conservative defaults; a profile compiler; a lint report.
- **Decision-model interface, complete:**
  - adapters: `decision-api` (Jev default, Clef hosted or self-hosted), `llm`, `classifier` and `rules`;
  - routing per judgment, with fallbacks;
  - a calibration step fitted from labels.
- **Author control, complete:**
  - retractions remove the fact from the group vault and index immediately;
  - git history is compacted after a configurable window;
  - retracting a fact that is also asserted by someone else keeps it under their name.
- **Security controls:**
  - secret scanning that refuses credentials;
  - a write list per group;
  - provenance framing in `recall` output;
  - audit export;
  - the external-processor declaration in config.
- **Organisation profile recipe:**
  - OIDC with IdP groups mapped to group brains;
  - a git repository per group;
  - Helm;
  - backups and retention;
  - documentation of the encryption guarantees and the compliance trade-off for legal review.
- **Pilot:** one or two volunteer teams for at least three weeks, with their Slack channels and meeting folders connected.

### Gate 2: pilot review

| Measure | Proposed target |
|---|---|
| Sensitive or personal items reaching a group | **Zero** found in an audit of all auto-shared items (any leak blocks the release) |
| Auto-shared items later retracted | ≤ 2% |
| Consent prompts per person per week | ≤ 5 after the second week |
| Group brain growth | Pilot teams' brains answer their private question set at or above whole-context loading, at ≤ 15% of the tokens |
| Cross-context leakage in access tests and the pilot | **Zero** |
| Pilot users | Would keep using it (a short survey); trust what is shared on their behalf; can fix or retract without help |

## Phase 4: Tuning and public release (3–4 weeks)

- **Decision-model bake-off:** Jev, Clef (hosted and self-hosted) and an LLM on every judgment.
  - **Test data:** the public sets plus the anonymised pilot labels.
  - **Measures:** accuracy, calibration, latency and cost per 1,000 items.
  - **Outcome:** publish the results and confirm the default (Jev unless the results say otherwise) and the recommended routing per hosting profile.
- **Recalibrate thresholds** from pilot consent and retraction labels.
- **Retrieval tuning,** adopted only where the test set shows a gain: reranking (decision model vs a local cross-encoder), entity matching in `recall`, and summary layers.
- **Stretch goals:**
  - an Obsidian sync client that decrypts personal brains on the person's device;
  - a confidential-computing deployment guide.
- **Community profile:** Docker Compose, a quick-start guide and an example vault and policy template.
- **Security review** of the gateway, the encryption and the organisation profile.
- **Release v0.1:** docs site, changelog, published test results and issue templates.

## Repository layout (proposed)

```
context-brain/
  docs/            decision.md, plan.md, adr/, guides/ (clients, hosting profiles, encryption)
  spec/            note format, tool contract, decision-model contract (versioned)
  gateway/         MCP server: auth, ACL, tools, budget packer, audit, storage adapter
  keys/            personal key management: wrapping, unlock, recovery
  ingest/          pipeline, classifier, group maintenance, lint, profile compiler
  sources/         documents, meeting notes, Slack, sweep
  decision/        decision-model interface + adapters: decision_api/ (Jev, Clef), llm/, classifier/, rules/
  web/             web UI
  deploy/          personal/, compose/, helm/
  eval/            public test sets, harness, published results
  examples/        vault and policy templates
```

The implementation language is open for review. The proposal is Python for the gateway and pipeline, to match Basic Memory and the MCP and ML tooling around it, and TypeScript for the web UI.

## What we need from reviewers and the organisation

- **Engineering leaders:** challenge the decision ([questions](decision.md#13-questions-for-reviewers)), the gate criteria and the estimates.
- **People:**
  - two engineers for about 4–5 months;
  - a part-time security engineer from phase 2 (encryption, threat model, review).
- **Pilot:** one or two volunteer teams for phase 3, with permission to connect their Slack channels and meeting folders.
- **Approvals:**
  - the open-source policy owner: license, and publishing under the org;
  - data protection: the decision model and LLM as processors;
  - legal: operator-blind personal brains and the compliance trade-off;
  - the Slack workspace admin: the internal app.
- **Budget:** small. It covers hosting for the pilot, decision-model and LLM usage during evaluation, and a GPU for the self-hosted Clef comparison.
