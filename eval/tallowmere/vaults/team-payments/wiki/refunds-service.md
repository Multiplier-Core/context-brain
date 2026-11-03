---
title: Refunds Service
type: service
tags: [refunds, payments, support]
---
# Refunds Service
Handles customer refunds: approval in the admin tool, then payout to the original card through Paystream. Owned by the payments team; the support team are its main users.

## Facts
- [constraint] Refunds over £250 need a second approver in the admin tool #approvals (by: judy · src: [[raw/2026-10-01-refunds-limit-change]] · from: 2025-06-01 · to: 2026-10-01)
- [constraint] Refunds over £500 need a second approver in the admin tool; refunds of £500 or less need one approver #approvals (by: grace · src: [[raw/2026-10-01-refunds-limit-change#Discussion]] · from: 2026-10-01)
- [policy] Customers can request a refund within 30 days of delivery #refund-window (by: judy · src: [[raw/2026-10-01-refunds-limit-change#Discussion]] · from: 2026-10-01)
- [behaviour] Refunds are paid back to the original card through Paystream and normally arrive within 5 working days #paystream (by: bob · src: [[raw/2026-10-01-refunds-limit-change#Discussion]] · from: 2026-10-01)
- [behaviour] The refund batch job runs every 2 hours #batch (by: bob · src: [[raw/2026-10-01-refunds-limit-change#Queue target]] · from: 2026-10-01)

## Relations
- owned_by [[Payments Team]]
- depends_on [[Payments Gateway]]
- writes_to [[Ledger Service]]
- used_by [[Support Team]]

## Disputed
- [sla] The refund queue should be drained within 4 hours during support hours (by: judy · src: [[raw/2026-10-01-refunds-limit-change#Queue target]]) vs within 8 hours until the batch job is rewritten (by: bob · src: [[raw/2026-10-01-refunds-limit-change#Queue target]])
