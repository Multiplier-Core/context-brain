---
title: Lookout
type: service
tags: [observability, metrics, logs]
---
# Lookout
Observability stack: metrics, logs, dashboards and alerts for every Tallowmere service. Owned by the platform team.

## Facts
- [limit] Logs are kept for 30 days; audit logs are kept for 90 days #retention (by: carol · src: [[raw/2026-10-20-oncall-retro#Logs]] · from: 2026-03-01)
- [config] Metrics are scraped every 15 seconds #metrics (by: dave · from: 2026-05-12)
- [slo] The Lookout query API has an availability SLO of 99.5% per month #slo (by: carol · from: 2026-06-01)
- [alert] An alert fires when CoreDNS memory exceeds 80% of its limit #alerts #dns (by: carol · src: [[raw/2026-10-17-incident-eu-west-dns#Follow-ups]] · from: 2026-10-22)

## Relations
- owned_by [[Platform Team]]
- monitors [[Kubernetes Clusters]]
- monitors [[Forge Pipeline]]
