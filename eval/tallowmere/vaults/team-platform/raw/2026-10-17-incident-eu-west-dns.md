---
title: "Incident: eu-west internal DNS outage"
type: meeting
tags: [incident, dns, kubernetes, eu-west]
---
# Incident: eu-west internal DNS outage, 17 October 2026

Postmortem notes written by carol; reviewed with dave and grace on 21 October.

## Summary
Internal DNS in the eu-west cluster failed for 47 minutes (09:12 to 09:59 UTC). Services could not resolve each other, and about 6% of checkout requests failed during that time. Declared SEV2.

## Cause
CoreDNS pods were running with a memory limit of 170Mi. After the move to 8 vCPU nodes the number of pods per node roughly doubled and CoreDNS's cache grew past the limit, so the pods were OOM-killed in a loop.

## Timeline
- 09:12 first resolution failures in Lookout.
- 09:20 carol paged as primary on-call.
- 09:41 cause identified.
- 09:59 CoreDNS memory limit raised and pods healthy.

## Follow-ups
- CoreDNS memory limit raised to 256Mi (done, dave).
- Add a Lookout alert on CoreDNS memory above 80% of the limit (carol).
- Re-run the eu-north failover game day before the end of November (dave).
