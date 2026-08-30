# Shared agent catalog

Each agent directory contains native adapters for the coding agents managed by
this repository:

- `opencode.md` — OpenCode Markdown agent definition
- `pi.md` — Pi Markdown agent definition
- `codex.toml` — Codex TOML agent definition

The native agent directories link to these adapters. Keep the three adapters in
sync when changing an agent prompt or its permissions.

All adapters use GPT-5.6 Luna with high reasoning effort.
