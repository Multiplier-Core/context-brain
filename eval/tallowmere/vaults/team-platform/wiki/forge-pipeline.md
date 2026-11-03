---
title: Forge Pipeline
type: service
tags: [forge, ci, builds]
---
# Forge Pipeline
Tallowmere's CI/CD pipeline. Every repository builds, tests and deploys through Forge. Owned by the platform team.

## Facts
- [limit] Build timeout is 45 minutes #builds (by: dave · from: 2025-09-01 · to: 2026-09-30)
- [limit] Build timeout is 30 minutes #builds (by: dave, carol · src: [[raw/2026-09-30-forge-slack-digest#Build timeout]] · from: 2026-09-30)
- [limit] Forge allows 12 concurrent builds per repository; further builds queue #builds (by: dave · src: [[raw/2026-09-30-forge-slack-digest#Concurrency]] · from: 2026-09-30)
- [schedule] Forge caches are wiped every Sunday at midnight UTC #caches (by: carol · src: [[raw/2026-09-30-forge-slack-digest#Caches]] · from: 2026-09-30)

## Relations
- owned_by [[Platform Team]]
- deploys_to [[Kubernetes Clusters]]
- reports_to [[Lookout]]

## Disputed
- [rule] A test is quarantined automatically after 3 flaky failures in a week (by: carol · src: [[raw/2026-09-30-forge-slack-digest#Flaky tests]]) vs after 5 flaky failures in a week (by: dave · src: [[raw/2026-09-30-forge-slack-digest#Flaky tests]])
