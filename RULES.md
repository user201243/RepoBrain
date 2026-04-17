# RepoBrain Rules

## Purpose

These rules keep RepoBrain development consistent. The point is to make each cycle feel like a deliberate product step, not a random code drop.

## Product Rules

- Build RepoBrain as a local-first codebase memory engine.
- Prefer trust, clarity, and evidence over feature breadth.
- Do not add hosted or autonomous behavior until local grounding is genuinely strong.
- Every user-facing capability should map cleanly to a release line in `feat.md` and `ROADMAP.md`.

## Engineering Rules

- Keep the dependency-light baseline working.
- Treat optional dependencies as quality upgrades, not hard requirements.
- Do not break CLI or JSON contracts casually.
- If a heuristic is added, document the tradeoff and add a verification path.
- Keep runtime state local under `.repobrain/`.

## Retrieval Rules

- Never rely on one signal only when multiple signals are available.
- Prefer hybrid evidence over embedding-only intuition.
- Surface warnings when evidence is weak, narrow, or structurally incomplete.
- Ranking should favor grounded files, not clever-looking guesses.

## Workflow Rules

- Finish a concrete capability, then note the next direction.
- Update docs when behavior or product direction changes.
- Add or update tests when logic changes.
- If pytest is blocked by the environment, run a manual smoke verification and record what was checked.

## Scope Rules

- `0.2.x` is about retrieval quality.
- `0.3.x` is about trust and change planning.
- `0.5.x` is about integrations and workflow adoption.
- Defer omniretrieval, SaaS, and autonomous mutation until the core engine is strong.
