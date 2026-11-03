# Tallowmere

Tallowmere is a **fictional** online homeware marketplace, invented for context-brain's public test sets. None of its people, services or events are real. Any resemblance to a real organisation is coincidental.

It is small on purpose: enough people and groups to test sharing and access, and few enough that a reviewer can hold it in their head.

## People and groups

[org.yaml](org.yaml) is the source of truth. In summary:

| Person | Role | Groups |
|---|---|---|
| alice | Staff engineer, payments tech lead | team-payments |
| bob | Backend engineer | team-payments |
| carol | Site reliability engineer | team-platform |
| dave | Platform engineer | team-platform |
| erin | Product manager, growth | team-growth |
| frank | Product designer | team-growth |
| grace | Head of engineering | team-payments, team-platform |
| heidi | People operations lead | — |
| ivan | Data analyst | team-growth, team-payments |
| judy | Customer support lead | team-payments |

Everyone can read `org-handbook`. Only grace and heidi can write to it.

## The world

- **Payments** owns the Checkout Service, the Orders API, the Payments Gateway (which talks to a card processor called Paystream), the Refunds Service and the Ledger Service.
- **Platform** runs everything on Kubernetes in two regions, owns CI (the "Forge" pipeline), observability (metrics and logs in "Lookout") and the on-call rota.
- **Growth** owns the marketing site, the experiment framework ("Dial"), the weekly newsletter and promotional codes.
- **The handbook** covers leave, expenses, travel, security policy, the incident process and company holidays.

Group policies live in each group's vault: [vaults/](vaults/)`<group>/policy.md`. The classifier reads them to decide what belongs to a group.
