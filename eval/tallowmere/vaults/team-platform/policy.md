---
title: team-platform policy
type: policy
---
# team-platform

## Purpose
Shared knowledge for the platform team: Kubernetes clusters, CI/CD (Forge), observability (Lookout), networking and the on-call rota.

## In scope
- How the infrastructure is built and run: clusters, regions, capacity, deploys.
- Forge pipeline behaviour, build limits and conventions.
- Lookout dashboards, alerts, log retention and SLOs.
- Incident timelines and follow-ups for infrastructure.
- On-call rota rules and handover notes (not people's reasons for swapping shifts).

## Always group
- Decisions about clusters, Forge or Lookout.
- Limits, quotas and SLOs for platform-owned systems.
- Changes to the on-call process.

## Out of scope
- Anything personal: health, family, pay, performance, opinions about colleagues.
- Credentials, kubeconfigs, tokens or passwords.
- Product decisions of other teams unless they change platform load or process.

## Examples
| Item | Belongs here? |
|---|---|
| "Log retention in Lookout is 30 days, 90 for audit logs" | Yes |
| "Forge caches are wiped every Sunday at midnight" | Yes |
| "We are moving the eu-west cluster to node pools of 8 vCPU" | Yes |
| "I'm swapping my on-call week because of my sister's wedding" | No (personal reason) |
| "Dave should probably not lead the migration" | No (claim about a person) |
