---
title: Dial
type: service
tags: [dial, experiments, analytics]
---
# Dial
The experiment framework for the marketing site and checkout. Assigns users to arms, logs exposures and computes results. Owned by the growth team.

## Facts
- [rule] Dial requires at least 4,000 users per arm before a result can be read #sample-size (by: ivan · from: 2025-10-01 · to: 2026-09-01)
- [rule] Dial requires at least 6,000 users per arm before a result can be read #sample-size (by: ivan · src: [[raw/2026-09-01-dial-sample-size#Sample size]] · from: 2026-09-01)
- [rule] Experiments run for at least 14 days #duration (by: ivan · src: [[raw/2026-09-01-dial-sample-size#Sample size]] · from: 2025-10-01)
- [rule] The significance threshold is p < 0.05 #statistics (by: ivan · src: [[raw/2026-09-01-dial-sample-size#Sample size]] · from: 2025-10-01)
- [definition] The default primary metric is weekly active buyers: anyone with a paid order in the last 7 days #metrics (by: erin · src: [[raw/2026-09-01-dial-sample-size#Primary metric]] · from: 2026-09-01)

## Relations
- owned_by [[Growth Team]]
- uses_metric [[Weekly Active Buyers]]
- ran [[Decision: Keep the old free-delivery banner]]

## Disputed
- [rule] The global holdout is 5% of users (by: erin · src: [[raw/2026-09-01-dial-sample-size#Holdout]]) vs 10% of users (by: ivan · src: [[raw/2026-09-01-dial-sample-size#Holdout]])
