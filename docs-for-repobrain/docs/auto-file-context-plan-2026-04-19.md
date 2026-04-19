# Auto File Context Plan - 2026-04-19

## Goal

When RepoBrain surfaces concrete file names in Web or CLI results, it should automatically attach those files to the user's repo memory and show a short improvement assessment for each file.

## Scope

- CLI query-like commands: `query`, `trace`, `impact`, `targets`
- CLI project commands with file evidence: `review`, `patch-review`, `ship`
- Web API actions: query modes, review, patch review, ship
- Browser UI result pane: show attached files and improvement guidance before the raw transcript
- Workspace memory: persist surfaced files into `top_files` so follow-up questions reuse them

## Non-goals

- Do not edit user source files automatically.
- Do not open files in an editor.
- Do not add generated, dependency, or temp files to memory.
- Do not build a full IDE-style file drawer in v1.

## Implementation Steps

1. Add shared file-context extraction from `QueryResult`, review reports, patch-review reports, ship reports, and workspace query payloads.
2. Add workspace memory helper to persist attached files.
3. Add CLI wrapper that augments JSON output and appends text guidance.
4. Add Web API wrapper that returns `file_context` and refreshes workspace summary.
5. Add Web UI panel for auto-attached files and improvement guidance.
6. Add tests for CLI and Web behavior.

## Progress

- [x] Requirements clarified from Vietnamese request.
- [x] Shared extractor implemented in `src/repobrain/file_context.py`.
- [x] Workspace memory auto-add implemented in `src/repobrain/workspace.py`.
- [x] CLI output implemented for query-like commands, `review`, `patch-review`, and `ship`.
- [x] Web API implemented with top-level `file_context` payloads and refreshed workspace summary.
- [x] Browser UI implemented with an auto-attached files panel in the result pane.
- [x] Tests added for CLI and Web behavior.
- [x] Verification completed.

## Verification

- `python -m pytest -q --basetemp=$env:TEMP\repobrain-pytest-file-context-full` -> `88 passed, 1 skipped`
- `npm run build` in `webapp` -> pass
- `npm run build` in `docs-for-repobrain` -> pass
- `npm run lint` in `docs-for-repobrain` -> pass

## Implemented Behavior

- Web results now return `file_context` when RepoBrain finds concrete file paths.
- Web result pane shows attached files, source, score, reason, and improvement guidance.
- CLI JSON output now includes `file_context` for file-bearing results.
- CLI text output appends a `RepoBrain Auto-Attached Files` section.
- Attached files are persisted into workspace `top_files` so follow-up questions reuse the same context.

## Review Notes

- "Add file" means adding the surfaced file path to RepoBrain workspace memory for the active repo, not modifying the user's source code.
- The feature should be deterministic and local-only.
- If a payload contains many file references, only the top-ranked/high-signal files should be attached.
