# Implementation Plan

## Goal

Turn the current RepoBrain MVP into a credible open-source engine that feels intentional, explainable, and easy to extend.

## Epic 1: Indexing Quality

Outcome:

- better symbol boundaries
- better route/job/config role detection
- cleaner chunk metadata

Work:

- deepen the optional tree-sitter adapters now that the interface exists
- keep heuristic fallback as the always-available baseline
- attach more semantic hints such as test neighbors, config surfaces, and provider markers

Acceptance:

- indexing still works with zero optional dependencies
- tree-sitter path improves chunk boundaries without changing public CLI contracts

## Epic 2: Retrieval Quality

Outcome:

- top files feel less random
- confidence reflects evidence quality more honestly

Work:

- improve query rewriting by intent
- add reciprocal-rank or weighted-fusion logic
- strengthen path, symbol, and role-aware bonuses
- explicitly penalize weak single-file concentration when the query implies cross-file flow

Acceptance:

- acceptance queries still pass
- low-confidence warnings appear in more realistic edge cases

## Epic 3: Harness Reliability

Outcome:

- outputs become safer for downstream coding agents

Work:

- formalize self-check rules
- add contradiction detection across evidence sources
- make `build_change_context` more compact and deterministic
- add agent-facing guidance in warnings and next questions

Acceptance:

- change context never recommends files with no supporting evidence
- weak results degrade gracefully instead of sounding confident

## Epic 4: Provider Layer

Outcome:

- local-first remains default, but cloud adapters become production-credible

Work:

- define explicit provider capability checks
- add install docs and env var expectations
- keep missing-SDK failure mode user-readable

Acceptance:

- local mode works out of the box
- cloud mode fails clearly when credentials or client packages are missing

## Epic 5: OSS Polish

Outcome:

- repo feels maintained and understandable by contributors

Work:

- keep docs aligned with code
- keep `repobrain chat` and `chat.cmd` aligned with CLI contracts
- improve fixture pack realism
- add more examples to README and demo script
- document architectural decisions and review notes

Acceptance:

- a new contributor can read docs and know what to build next
- a user can understand the product without reading code first
