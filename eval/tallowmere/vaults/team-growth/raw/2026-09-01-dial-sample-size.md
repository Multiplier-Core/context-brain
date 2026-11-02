---
title: Dial sample size review
type: meeting
tags: [dial, experiments, statistics]
---
# Dial sample size review

Meeting on 1 September 2026. Present: erin, frank, ivan.

## Sample size
- ivan showed that tests with 4,000 users per arm were missing real effects of around 2%. From today Dial requires at least 6,000 users per arm before a result can be read.
- Experiments still run for at least 14 days, to cover two full weekends.
- Significance threshold stays at p < 0.05.

## Holdout
- erin wants a 5% global holdout that never sees any experiment, to keep more traffic for tests.
- ivan wants 10% so the holdout is large enough to measure long-term effects. Not decided.

## Primary metric
- The default primary metric for Dial experiments is weekly active buyers: anyone with a paid order in the last 7 days.
