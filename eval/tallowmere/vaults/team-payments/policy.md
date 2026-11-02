---
title: team-payments policy
type: policy
---
# team-payments

## Purpose
Shared knowledge for the payments team: checkout, the Orders API, the Payments Gateway, refunds and the ledger.

## In scope
- How payments services behave: limits, timeouts, retries, error codes, data flows.
- Decisions, constraints and conventions for those services, and why they were made.
- Who owns what, on-call handover notes, and links to runbooks.
- Incidents, outages and changes that affect payments, and what was learned.
- Paystream (the card processor): integration details, quirks, contract limits that engineers need.

## Always group
- Decisions about services the team owns.
- Constraints and limits of services the team owns.
- Ownership changes for payments services.

## Out of scope
- Anything personal: health, family, leave reasons, pay, performance, personal opinions of colleagues.
- Credentials, keys, tokens or passwords of any kind.
- Work that belongs to another team (platform infrastructure, growth experiments) unless it changes how payments works.

## Examples
| Item | Belongs here? |
|---|---|
| "Refunds over £500 need a second approver in the admin tool" | Yes |
| "We decided to keep Paystream as the only processor until Q3" | Yes |
| "The ledger nightly reconciliation runs at 02:00 UTC" | Yes |
| "I find the refunds code hard to read" | No (personal opinion) |
| "Bob seemed stressed in the retro" | No (claim about a person) |
