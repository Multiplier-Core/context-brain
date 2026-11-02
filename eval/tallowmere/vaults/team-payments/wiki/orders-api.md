---
title: Orders API
type: service
tags: [orders, api, payments]
---
# Orders API
Public API for creating and tracking orders. Called by the Checkout Service and owned by the payments team.

## Facts
- [constraint] Idempotency keys expire after 24 hours #api (by: alice · src: [[raw/2026-10-12-design-review#Retries]] · from: 2026-10-12)
- [constraint] Every `POST /orders` call must carry an `Idempotency-Key` header #api (by: alice · src: [[raw/2026-10-12-design-review#Retries]] · from: 2026-10-12)
- [decision] Pagination is cursor-based; offset pagination is deprecated #api (by: bob · src: [[raw/2026-10-12-design-review#Pagination]] · from: 2026-09-01)
- [limit] Rate limit is 600 requests per minute per client #rate-limit (by: bob · from: 2026-03-01 · to: 2026-09-15)
- [limit] Rate limit is 1,200 requests per minute per client #rate-limit (by: alice · from: 2026-09-15)

## Relations
- owned_by [[Payments Team]]
- called_by [[Checkout Service]]
- depends_on [[Payments Gateway]]
- depends_on [[Ledger Service]]

## Disputed
- [sla] p99 latency target for `POST /orders` is 300 ms (by: alice · src: [[raw/2026-10-12-design-review#Latency]]) vs 450 ms (by: bob · src: [[raw/2026-10-12-design-review#Latency]])
