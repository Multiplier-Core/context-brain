---
title: Payments Gateway
type: service
tags: [payments, paystream, gateway]
---
# Payments Gateway
Internal service that takes card payments by calling Paystream, the card processor. Owned by the payments team.

## Facts
- [constraint] Idempotency keys expire after 24 hours; the gateway passes the same key on to Paystream #api #retries (by: bob · src: [[raw/2026-10-12-design-review#Retries]] · from: 2026-10-12)
- [behaviour] A Paystream call is retried at most 3 times with exponential backoff starting at 200 ms #retries (by: bob · src: [[raw/2026-10-12-design-review#Retries]] · from: 2026-10-12)
- [limit] A single Paystream call times out after 8 seconds #timeouts (by: alice · src: [[raw/2026-10-12-design-review#Retries]] · from: 2026-10-12)
- [constraint] The Paystream contract caps Tallowmere at 40 transactions per second; above that Paystream returns `PS-429` #paystream #capacity (by: alice · src: [[raw/2026-10-22-payments-slack-digest#Paystream throughput]] · from: 2026-10-22)
- [error] `PS-417` means the card issuer timed out; it is safe to retry once with the same idempotency key #paystream #errors (by: bob · src: [[raw/2026-10-22-payments-slack-digest#Paystream error PS-417]] · from: 2026-10-21)
- [metric] September 2026 chargeback rate was 0.21%, inside Paystream's 0.5% threshold #chargebacks (by: ivan · src: [[raw/2026-10-22-payments-slack-digest#Chargebacks]] · from: 2026-10-23)

## Relations
- owned_by [[Payments Team]]
- depends_on [[Paystream]]
- called_by [[Orders API]]
- called_by [[Refunds Service]]
- governed_by [[Decision: Keep Paystream as sole processor]]
