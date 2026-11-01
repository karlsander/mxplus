---
name: Reproduction failure or hardware observation
about: Report a repeatable tool failure or a measured USB/audio result.
---

## What happened?

Describe the observed result and what you expected. Identify the path involved:
offline tools, USB1–4 host candidate, USB-B device candidate, or Linux bridge.

## Revision and environment

- Repository commit:
- Python/dependency versions and operating system:
- Original/candidate firmware SHA-256, if relevant:
- Exact command or application settings:

## Reproduction steps and evidence

Include the smallest repeatable sequence and the relevant error or log excerpt.
For offline failures, include the failing stage from `analysis/reproduction.json`
and its log in `build/reproduction-logs/`.

## Hardware details, if this is a physical test

Identify the mixer firmware actually installed, attached device and OS/app
versions, USB port roles, cable/adapter/power arrangement, sample rate, channel
count, and stream start order. Include descriptor or audio evidence when useful.

Keep measured hardware behavior distinct from conclusions drawn from offline
tests. A hardware test is not required to report an offline problem.
