---
title: Orders API retries design review
type: design-doc
tags: [orders-api, payments-gateway, retries]
---
# Orders API retries design review

Design review held on 12 October 2026. Present: alice (author), bob, grace, ivan.

## Context
Duplicate orders were created when the Checkout Service retried a timed-out call to the Orders API. The review agreed how retries and idempotency should work end to end, from the Orders API through the Payments Gateway to Paystream.

## Retries
- Every `POST /orders` call must carry an `Idempotency-Key` header. Keys expire after 24 hours; a repeat call with the same key inside that window returns the original order.
- The Payments Gateway reuses the same key when it calls Paystream, so a retried charge is never taken twice.
- The gateway retries a Paystream call at most 3 times, with exponential backoff starting at 200 ms.
- The gateway gives up on a single Paystream call after 8 seconds.

## Latency
- alice proposed a p99 latency target of 300 ms for `POST /orders`.
- bob argued 300 ms is unrealistic while Paystream sits on the hot path and proposed 450 ms. Not settled; grace asked for a week of Lookout data before deciding.

## Pagination
- `GET /orders` stays cursor-based. Offset pagination was deprecated in September and will be removed.

## Actions
- alice: update the Orders API wiki page.
- bob: add the idempotency behaviour to the Payments Gateway page.
