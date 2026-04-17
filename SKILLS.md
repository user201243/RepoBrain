# RepoBrain Skills

## Why This Exists

This file defines the recurring working modes that should be used while building RepoBrain. It is the practical counterpart to `RULES.md`.

## Skill: Ship A Feature

Use this when adding product capability.

Steps:

1. confirm which release line the change belongs to
2. implement the smallest meaningful capability end to end
3. update docs and changelog
4. verify with tests or manual smoke flow
5. write the next direction into `feat.md`

## Skill: Improve Retrieval

Use this for `0.2.x` work.

Focus:

- better query rewriting
- better lexical/vector fusion
- better structural ranking
- better benchmark behavior

Guardrails:

- keep outputs explainable
- keep fallback behavior working without optional dependencies

## Skill: Improve Trust

Use this for `0.3.x` work.

Focus:

- confidence calibration
- low-evidence penalties
- contradiction warnings
- safer change-context packaging

Guardrails:

- do not hide uncertainty
- do not make edit-target recommendations without evidence

## Skill: Improve Integration

Use this for `0.5.x` work.

Focus:

- provider adapters
- MCP ergonomics
- better examples and runbooks
- contributor onboarding

Guardrails:

- keep local mode first-class
- fail clearly when remote setup is incomplete

## Skill: End Each Cycle

At the end of every meaningful cycle:

1. summarize what actually shipped
2. note risks or limitations honestly
3. update `feat.md` with the next highest-leverage move
