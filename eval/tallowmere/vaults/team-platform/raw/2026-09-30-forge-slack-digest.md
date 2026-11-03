---
title: "#platform-forge Slack digest, 30 September"
type: slack-digest
tags: [forge, ci, slack]
---
# #platform-forge Slack digest, 30 September 2026

## Build timeout
- **dave:** Forge builds have been hanging for the full 45 minutes when a test container deadlocks. From today the build timeout is 30 minutes. Nothing healthy takes longer than 22.
- **carol:** +1. Changed in the shared Forge config, takes effect for every repo.

## Concurrency
- **dave:** reminder that Forge allows 12 concurrent builds per repository; further builds queue.

## Flaky tests
- **carol:** I'd like Forge to quarantine a test automatically after 3 flaky failures in a week.
- **dave:** 3 is too aggressive, we'll quarantine half the checkout suite. 5 failures in a week.
- No agreement yet.

## Caches
- **carol:** Forge caches are still wiped every Sunday at midnight UTC; if your Monday build is slow, that's why.
