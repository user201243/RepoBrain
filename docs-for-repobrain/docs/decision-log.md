# Decision Log

## D-001: Python As The Implementation Language

Chosen:

- implement the engine in Python

Why:

- fastest path to a practical local CLI and indexing engine
- strong ecosystem for parsing, SQLite work, evaluation tooling, and optional MCP integration

Tradeoff:

- cross-language indexing depth depends on parser quality, not implementation language parity

## D-002: Local-First Storage

Chosen:

- SQLite plus local vector artifacts under `.repobrain/`

Why:

- portable
- inspectable
- easy to reset
- no service dependency

Tradeoff:

- not yet optimized for very large multi-repo workspaces

## D-003: Heuristic Scanner First, Optional Tree-Sitter Later

Chosen:

- keep the base runtime dependency-light
- treat tree-sitter as an optional quality upgrade behind a parser adapter interface

Why:

- repo must run immediately in constrained environments
- the product story is stronger if it degrades gracefully

Tradeoff:

- parser quality improves when optional packages are installed, but the heuristic fallback still defines the compatibility floor

## D-004: Hybrid Retrieval Over Embedding-Only Search

Chosen:

- combine BM25/FTS, local embeddings, and reranking

Why:

- developer queries often contain precise tokens and filenames
- lexical signals matter too much to ignore

Tradeoff:

- retrieval logic is more complex than a single vector call

## D-005: No Autonomous Mutation In v1

Chosen:

- stop at grounded planning and edit targeting

Why:

- trust is easier to earn when the engine first proves it can gather evidence correctly

Tradeoff:

- the product stops short of end-to-end codegen workflows in v1

## D-006: Confidence And Warnings Are First-Class Outputs

Chosen:

- every query path should produce a confidence score and warnings when evidence is weak

Why:

- hiding uncertainty is a major source of agent failure

Tradeoff:

- confidence heuristics require iteration and can look simplistic early on

## D-007: Chat Is A CLI Loop, Not A Hosted Interface

Chosen:

- expose `repobrain chat` as a local interactive loop
- keep the Windows launcher as a thin wrapper around the CLI

Why:

- users get a one-click workflow without adding a server, browser UI, or hosted surface
- the same engine contracts remain testable and reusable by MCP or other agents

Tradeoff:

- early chat output is raw JSON; richer summaries can come later after retrieval confidence is stronger
