# Skill Registry CLI and UI workflows

## CLI

```bash
# Local folder
mlflow skills register --source ./code-review

# External sources
mlflow skills register git --url URL --ref TAG --subpath PATH
mlflow skills register oci --image IMAGE --subpath PATH
mlflow skills register zip --url URL --subpath PATH

# Bulk import from a Git repository
mlflow skills import --source URL --skill-name NAME

# Discover
mlflow skills search

# Manage versions and aliases
mlflow skills set-alias skills:/name --alias production --version 2

# Install locally
mlflow skills pull skills:/name@production --destination .agents/skills/name
```

Verify exact flags with `mlflow skills --help` on the installed release; the
feature is experimental and CLI surface may change.

## UI

- **Skills → Create skill**: upload a folder or import from an external source.
- Manage versions, statuses (`draft`/`active`/`deprecated`/`deleted`), tags, and
  aliases from the skill detail page.
- **Use → Install for** selects the target agent: Claude Code, Codex, Cursor,
  GitHub Copilot, or an arbitrary directory. The 3.18.0 UI added agent icons in
  the selector and guidance for single- versus multi-skill registration.

## Installation destinations

| Target | Typical destination |
|---|---|
| Claude Code | `.claude/skills/<name>` |
| Codex | `.agents/skills/<name>` or `$CODEX_HOME/skills/<name>` |
| Cursor | `.cursor/skills/<name>` |
| GitHub Copilot | `.github/skills/<name>` |
| Arbitrary | any directory you choose |

MLflow writes files only. It does not register the skill with the agent runtime,
execute scripts, or add the skill to a prompt. Confirm the destination matches the
harness you actually run, and review pulled `SKILL.md` and scripts before use.
