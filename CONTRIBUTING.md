# Contributing

Thanks for helping make RepoBrain better.

## Development Setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
pytest
```

## Contribution Expectations

- Keep the local-first story intact.
- Prefer explicit evidence over implicit magic.
- Add or update tests for retrieval, graph extraction, or CLI behavior when you change them.
- Document public-facing changes in `README.md`, `docs/`, or `CHANGELOG.md`.

## Pull Request Checklist

- Tests added or updated
- Docs updated when behavior changes
- No secrets or machine-local paths committed
- New provider integrations degrade cleanly when the SDK is missing

## Good First Areas

- Better TypeScript symbol extraction
- Richer confidence scoring
- More benchmark fixtures
- MCP transport hardening
