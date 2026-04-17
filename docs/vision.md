# Vision

RepoBrain exists to make coding agents less reckless.

## Problem

Large repositories punish shallow context gathering. Agents often hallucinate because they:

- inspect the wrong files
- miss route-to-service or job-to-handler relationships
- lack confidence signals when the evidence is weak

## Target User

- developers using Cursor, Codex, Claude Code, or similar tools
- teams with mid-sized to large repositories
- OSS maintainers who want grounded code search without a hosted service

## Product Thesis

Better retrieval and better evidence packaging produce more reliable agent behavior than simply switching models.

RepoBrain therefore focuses on:

- indexing code structure, not only raw text
- hybrid retrieval instead of embedding-only search
- explicit edit-target ranking
- confidence and warnings as first-class outputs

## Non-Goals For v1

- browser search
- omniretrieval across all personal data
- autonomous code mutation
- cloud-hosted dashboards

## Long-Term Direction

RepoBrain can grow into a broader retrieval substrate for coding agents, but the v1 narrative stays tightly focused on codebase memory and grounded change planning.
