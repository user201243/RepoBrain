# User Experience

RepoBrain has three user surfaces:

- terminal-first commands for developers and automation
- one-click Windows launchers for people who do not want to memorize commands
- a local HTML report for people who want a visual overview
- a local browser UI for import-and-query flows

JSON remains the default output format because agents and scripts depend on stable machine-readable payloads. Humans can opt into text summaries.

## Terminal UX

Use `--format text` when reading output directly:

```bash
repobrain init --repo /path/to/your-project --format text
repobrain review --format text
repobrain doctor --format text
repobrain index --format text
repobrain query "Where is payment retry logic implemented?" --format text
repobrain trace "Trace login with Google from route to service" --format text
repobrain targets "Which files should I edit to add GitHub login?" --format text
```

Text output includes:

- concise project-review findings with severity and fix-next guidance
- top files with role and score
- concise snippet previews
- call-chain hints
- edit targets
- warnings and next questions

`repobrain init --repo /path/to/your-project` remembers the active repo. After that, users can run `index`, `query`, `chat`, and `report` without repeating the repo path.

Use JSON when integrating with tools:

```bash
repobrain query "Where is payment retry logic implemented?" --format json
```

## Chat UX

Start local chat:

```bash
repobrain chat
```

Chat commands:

- `/trace <question>`: trace route/service/job-like flows
- `/impact <question>`: inspect likely affected surfaces
- `/targets <question>`: rank files to inspect or edit
- `/doctor`: show local health
- `/index`: rebuild the local index
- `/review`: generate the one-page repo review
- `/report`: generate the local HTML dashboard
- `/json`: switch chat output to raw JSON
- `/text`: switch chat output back to readable text
- `/exit`: quit

On Windows, `chat.cmd` launches the same flow and prefers the project virtualenv.

## One-Click UX

Windows launchers live in the repo root:

- `chat.cmd`: initialize/index if needed, then open local chat
- `report.cmd`: initialize/index if needed, generate `.repobrain/report.html`, then open it in the default browser

Both launchers set `PYTHONPATH=src` and prefer `venv\Scripts\python.exe`, then `.venv\Scripts\python.exe`, then global `python`.

## Local Report UX

Generate a visual report:

```bash
repobrain report --format text
repobrain report --open
```

Default output:

- `.repobrain/report.html`

Custom output:

```bash
repobrain report --output ./repobrain-report.html
```

The report includes:

- review score and readiness
- top project findings
- what to fix first
- indexed/not-indexed status
- files, chunks, symbols, and edges
- provider mode
- security posture
- parser selection by language
- suggested next commands

The report is static HTML and local-only. RepoBrain does not start a web server or send source code to any hosted service.

For a web-style import flow, initialize the target project once, then open the report without repeating the path:

```bash
repobrain init --repo /path/to/your-project --format text
repobrain index --format text
repobrain report --open
```

## Browser Import UX

For users who want a web-style import flow instead of repeating CLI flags:

```bash
repobrain serve-web --open
```

Then:

- paste the project path
- click `Import + Index`
- click `Scan Project Review` for the short audit pass
- run `query`, `trace`, `impact`, or `targets` from the page
- open the generated report from the same UI

## Recommended New-User Flow

```bash
repobrain quickstart
repobrain init --repo /path/to/your-project
repobrain review --format text
repobrain index --format text
repobrain report --format text
repobrain report --open
repobrain chat
```
