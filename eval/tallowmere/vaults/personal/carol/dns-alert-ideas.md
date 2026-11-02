---
title: DNS alert ideas
type: note
tags: [dns, lookout, private]
---
# DNS alert ideas
Rough thinking after the eu-west DNS incident, before I propose anything.

## Facts
- [idea] Alert when CoreDNS memory passes 150Mi, well before it gets near the limit #dns
- [idea] Build a personal Lookout dashboard called `carol-dns-watch` with CoreDNS memory and resolution errors side by side #lookout
- [question] Is a fixed 150Mi threshold still right now that the limit has been raised, or should it be a percentage? #dns
