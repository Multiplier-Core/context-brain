---
title: Ledger Service
type: service
tags: [ledger, reconciliation, payments]
---
# Ledger Service
Double-entry ledger of every payment, refund and payout. Reconciled nightly against Paystream settlement files. Owned by the payments team.

## Facts
- [schedule] The nightly reconciliation runs at 02:00 UTC #reconciliation (by: alice · from: 2025-11-01 · to: 2026-10-20)
- [schedule] The nightly reconciliation runs at 03:30 UTC, moved to avoid the platform cluster backup window #reconciliation (by: alice, bob · src: [[raw/2026-10-22-payments-slack-digest#Ledger reconciliation moved]] · from: 2026-10-20)
- [constraint] Ledger entries are immutable; corrections are new reversing entries #ledger (by: alice · from: 2025-11-01)
- [behaviour] A reconciliation mismatch above £50 pages the payments on-call engineer #alerts (by: bob · from: 2026-04-01)

## Relations
- owned_by [[Payments Team]]
- reconciles_with [[Paystream]]
- written_by [[Orders API]]
- written_by [[Refunds Service]]
