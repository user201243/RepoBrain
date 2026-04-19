# Product Spec

## One-Sentence Pitch

RepoBrain is a local-first codebase memory engine that gives coding agents grounded evidence about where logic lives, how flows connect, and which files are safest to inspect or edit next.

## Problem Statement

AI coding tools fail most often before generation. They:

- read the wrong files
- miss route-to-service and job-to-handler flow
- over-trust shallow keyword matches
- propose edits without showing evidence

RepoBrain exists to make the pre-generation step explicit, inspectable, and grounded.

## Target Users

- solo developers working in medium or large repositories
- teams adopting Cursor, Codex, Claude Code, or similar tools
- OSS maintainers who want a local-first retrieval layer without a hosted backend

## Core User Jobs

1. Find where a feature, flow, or bug-related logic actually lives.
2. Trace how a request moves through route, service, background job, or config.
3. Estimate which files are likely affected by a change.
4. Hand a planning or coding agent a compact, grounded change context.

## v1 Scope

- Local CLI and stdio MCP-style transport
- Python and TS/JS indexing
- Hybrid retrieval using BM25 plus embeddings plus reranking
- Lightweight dependency edges and role detection
- Evidence snippets, top files, call-chain hints, edit targets, confidence, warnings

## Explicit Non-Goals

- browser search in v1
- personal omniretrieval across docs/email/PDF/history
- autonomous code mutation
- hosted dashboard or multi-user SaaS

## User Stories

### Locate

As a developer, I want to ask "where is payment retry logic implemented?" and get the top files plus evidence snippets with citations.

### Trace

As an agent operator, I want to ask "trace login with Google from route to service" and receive likely entrypoints and flow edges.

### Impact

As a maintainer, I want to ask "what breaks if I change auth callback handling?" and see likely affected files.

### Change Planning

As a coding agent, I want a compact payload of edit targets and warnings so I can plan a patch before I touch the repo.

## Success Criteria

- a fresh repo can be indexed locally with one command
- queries return ranked evidence in a consistent JSON shape
- low-confidence cases visibly warn instead of faking certainty
- edit-target suggestions are grounded in retrieved evidence, not hidden heuristics
- the product remains usable even when tree-sitter and cloud SDKs are unavailable

## What Makes The Product Credible

- local-first storage
- explicit trust model
- pluggable providers
- benchmarkable acceptance queries
- engineering docs that explain how retrieval and harness decisions are made
