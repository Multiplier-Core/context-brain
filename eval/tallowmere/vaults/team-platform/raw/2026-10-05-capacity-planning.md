---
title: Platform capacity planning
type: meeting
tags: [kubernetes, capacity, backups]
---
# Platform capacity planning

Meeting on 5 October 2026. Present: carol, dave, grace.

## Node pools
- eu-west node pools move from 4 vCPU to 8 vCPU nodes from today; the 4 vCPU pool is drained by the end of the week.
- eu-north stays on 4 vCPU nodes for now.

## Backups
- Cluster backups will run from 01:30 to 03:00 UTC every night. dave to tell payments, whose ledger reconciliation currently runs at 02:00 UTC.

## Failover
- carol believes the eu-north failover can be done in 15 minutes with the new runbook.
- dave measured 40 minutes in the August game day and wants that figure kept until a new test is run.

## Upgrades
- Cluster upgrades stay in the Tuesday window, 06:00 to 08:00 UTC.
