# Security Policy

## Supported Scope

RepoBrain is a local-first developer tool. The main security expectations are:

- never exfiltrate code without explicit configuration
- degrade safely when remote providers are configured incorrectly
- keep local indexes scoped to the selected repository root
- treat MCP input as untrusted and validate it before use
- surface provider readiness and security posture explicitly in diagnostics

## Reporting

If you find a security issue, open a private disclosure with:

- affected version or commit
- reproduction steps
- impact assessment
- suggested remediation if available

## Sensitive Areas

- provider credential handling
- path traversal during indexing
- MCP transport exposure
- local launcher scripts that execute commands from the repo root
- any future remote sync or hosted features

## Current Hardening

- local mode is the default path
- remote providers require explicit config plus credential presence
- doctor output includes provider readiness and a security posture summary
- MCP tool calls validate tool name, argument type, required query, and maximum query length
- retrieval warns when evidence is weak or contradicts the requested provider/surface
- `chat.cmd` only runs local CLI commands and does not expose a network listener
- optional parser packages are treated as quality upgrades, not required trusted infrastructure

## Operational Guidance

- prefer local providers unless remote quality is clearly needed
- do not commit provider API keys into `repobrain.toml` or any repo file
- treat `serve-mcp` as a local stdio tool surface, not a public network service
- inspect launcher scripts before running them in untrusted forks
- review warnings before acting on edit-target suggestions in security-sensitive codepaths
