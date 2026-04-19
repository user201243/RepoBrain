# Architecture

## Overview

RepoBrain is split into four runtime layers:

1. scanner and parser
2. metadata and vector storage
3. retrieval and reranking
4. grounding harness and transport

## Ingestion

- walk the repository root
- apply `.gitignore`, `.repobrainignore`, and configured excludes
- detect supported languages
- choose the best parser adapter for each language
- extract symbols, imports, hints, and lightweight call edges
- build symbol-aware chunks with fallback line windows

Parser selection is intentionally conservative. RepoBrain prefers the optional tree-sitter adapter when the runtime and grammar package are available, but it always falls back to the built-in heuristic parser so local indexing does not depend on native parser packages.

## Storage

- `.repobrain/metadata.db`
  - `files`
  - `symbols`
  - `chunks`
  - `chunk_fts`
  - `edges`
- `.repobrain/vectors/chunks.jsonl`
  - persisted embedding vectors keyed by chunk id

## Retrieval Pipeline

- classify query intent
- rewrite into keyword, semantic, and symbol-friendly variants
- run FTS/BM25 search
- run vector similarity search
- fuse hits and rerank them
- build evidence snippets, file rankings, dependency edges, and edit targets

## Harness Pipeline

- planner
- retriever
- file selector
- evidence collector
- edit-target scorer
- self-check gate

The self-check gate does not invent missing evidence. It lowers confidence and produces follow-up questions instead.

## Trust Model

RepoBrain is intentionally conservative:

- no autonomous repo mutation in v1
- explicit warnings when evidence is sparse
- local providers by default
- remote providers only via explicit configuration

## Extension Points

- tree-sitter-backed parsing for deeper symbol ranges
- remote embedding and reranking providers
- richer call graph extraction
- future MCP transports beyond the current stdio JSON adapter
