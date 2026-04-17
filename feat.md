# FEAT Direction

## Why This File Exists

This file is the blunt strategic note for what RepoBrain should become next. It is not marketing copy. It is the feature direction that should shape the next coding cycles.

## Current Position

RepoBrain already has:

- a credible local-first narrative
- a working CLI
- a working MCP-style adapter
- indexing, retrieval, scoring, and docs

RepoBrain still lacks:

- deeper parser quality
- stronger confidence calibration
- stronger change-planning trust
- smoother integration with external agent stacks

## Current Execution

This cycle is focused on making the repo easier to operate and making retrieval less naive.

Shipped in this cycle:

- human-readable terminal output with `--format text`
- active repo memory after `repobrain init --repo <path>` so daily commands stay short
- local browser import flow with `repobrain serve-web --open`
- local static HTML report with `repobrain report`
- browser-opening dashboard flow with `repobrain report --open`
- new-user onboarding command with `repobrain quickstart`
- chat output modes with `/text` and `/json`
- MIT license and package metadata for public OSS readiness
- GitHub Actions CI workflow for Python `3.12` and `3.13`
- manual GitHub release workflow for wheel/sdist artifact builds and explicit PyPI publishing
- release checklist for human launch gates
- production readiness checklist and OSS release gates
- runtime query ranking penalty for test files unless tests are explicitly requested
- confidence calibration band tests for grounded vs weak evidence
- repo-level `RULES.md`
- repo-level `SKILLS.md`
- more structured retrieval fusion
- stronger warnings when evidence is too narrow
- more compact `build_change_context`
- provider readiness and security posture in diagnostics
- SDK-backed optional provider adapters for Gemini embeddings/reranking, OpenAI embeddings, Voyage embeddings, and Cohere reranking
- `.env.example` plus automatic repo-root `.env` loading for remote-provider setup
- safer MCP validation for local tool usage
- interactive local chat through `repobrain chat`
- Windows one-click launcher through `chat.cmd`
- Windows one-click dashboard launcher through `report.cmd`
- source-tree module entrypoint through `python -m repobrain.cli`
- optional tree-sitter parser adapter interface with heuristic fallback
- parser usage counts in index stats

## Best Next Direction

The strongest next move is not "add more features everywhere".

The strongest next move is:

- make retrieval quality obviously better
- make trust signals obviously safer
- make the engine obviously easier to plug into real agents

That means the next serious push should be:

1. `0.2.x` retrieval quality
2. `0.3.x` trust and change planning
3. `0.5.x` integrations

## Feature Bets Worth Making

### Bet 1: Optional Tree-Sitter Layer

Why:

- biggest quality gain without abandoning the current architecture

What to build:

- parser adapters behind the current scanner interface
- keep heuristic fallback alive
- add richer symbol boundaries and call edges

### Bet 2: Better Fusion And Confidence

Why:

- current retrieval is good enough for MVP, not yet strong enough for trust

What to build:

- weighted fusion improvements
- explicit weak-evidence penalties
- contradiction detection
- calibration tests for confidence

### Bet 3: Better Change Context

Why:

- RepoBrain becomes much more valuable when planning agents can consume a compact, high-signal payload

What to build:

- deterministic `build_change_context`
- smaller payloads
- stronger edit-target rationale
- better warning messages for agents

### Bet 4: Real Provider Integrations

Why:

- pluggable provider architecture already exists and now needs to become real

Shipped now:

- SDK-backed OpenAI embedding adapter
- Voyage embedding adapter
- Cohere reranker adapter
- Gemini embedding adapter with `gemini-embedding-001`
- Gemini Flash reranker adapter with `gemini-3-flash-preview`
- `.env.example` setup template
- install and env docs that do not confuse contributors

What remains:

- live-key smoke tests outside CI, especially Gemini cheap setup
- model-specific quality benchmarks
- clearer examples for provider selection by repo size and privacy needs
- first dry-run release artifact inspection with `publish = false`

## What Not To Do Yet

- do not jump to omniretrieval
- do not build a SaaS dashboard
- do not add autonomous repo mutation
- do not over-expand browser search before RepoBrain is truly strong at codebase memory

## Practical 3-Step Path

### Step 1

Ship `0.2.x` with noticeably better retrieval quality.

Current move inside this step:

- better fusion
- better signal diversity
- better compact change context

### Step 2

Ship `0.3.x` with confidence and change-planning improvements that make outputs safer to trust.

Next concrete move after the current cycle:

- stronger contradiction detection across provider, route, job, and config surfaces
- package release automation and real repository URLs
- live-key provider smoke checks that keep the secure local-first default intact

### Step 3

Ship `0.5.x` with real provider integrations and better MCP usage examples so adoption becomes easier.

## Founder Note

If you want RepoBrain to be respected, optimize for trust and clarity before breadth. A smaller product that consistently helps agents choose the right files will travel further than a wider product that does many things half-right.
