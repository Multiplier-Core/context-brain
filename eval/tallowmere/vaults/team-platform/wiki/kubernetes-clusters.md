---
title: Kubernetes Clusters
type: service
tags: [kubernetes, regions, capacity]
---
# Kubernetes Clusters
Tallowmere runs everything on Kubernetes in two regions, eu-west (primary) and eu-north (failover). Owned by the platform team.

## Facts
- [capacity] eu-west node pools use 4 vCPU nodes #capacity (by: dave · from: 2025-04-01 · to: 2026-10-05)
- [capacity] eu-west node pools use 8 vCPU nodes #capacity (by: dave · src: [[raw/2026-10-05-capacity-planning#Node pools]] · from: 2026-10-05)
- [capacity] eu-north node pools use 4 vCPU nodes #capacity (by: dave · src: [[raw/2026-10-05-capacity-planning#Node pools]] · from: 2025-04-01)
- [schedule] Cluster backups run nightly from 01:30 to 03:00 UTC #backups (by: carol · src: [[raw/2026-10-05-capacity-planning#Backups]] · from: 2026-10-05)
- [schedule] Cluster upgrades happen on Tuesdays between 06:00 and 08:00 UTC #upgrades (by: carol · src: [[raw/2026-10-05-capacity-planning#Upgrades]] · from: 2026-01-13)
- [config] CoreDNS memory limit is 170Mi #dns (by: dave · src: [[raw/2026-10-17-incident-eu-west-dns#Cause]] · from: 2025-04-01 · to: 2026-10-17)
- [config] CoreDNS memory limit is 256Mi, raised after the 17 October DNS incident #dns (by: dave · src: [[raw/2026-10-17-incident-eu-west-dns#Follow-ups]] · from: 2026-10-17)

## Relations
- owned_by [[Platform Team]]
- monitored_by [[Lookout]]
- deployed_by [[Forge Pipeline]]

## Disputed
- [rto] eu-north failover takes 15 minutes with the new runbook (by: carol · src: [[raw/2026-10-05-capacity-planning#Failover]]) vs 40 minutes as measured in the August game day (by: dave · src: [[raw/2026-10-05-capacity-planning#Failover]])
