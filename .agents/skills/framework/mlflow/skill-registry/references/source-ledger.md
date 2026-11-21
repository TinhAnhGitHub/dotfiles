# Skill Registry source ledger

Reviewed 2026-11-21 against MLflow 3.18.0 release notes and official docs. The
feature is experimental; verify installed signatures before relying on any API.

| Source | Use |
|---|---|
| <https://mlflow.org/docs/latest/genai/skill-registry/> | Concepts, entity model, quickstart |
| <https://mlflow.org/docs/latest/genai/skill-registry/register-and-import-skills/> | Local/Git/OCI/ZIP registration and bulk import |
| <https://mlflow.org/docs/latest/genai/skill-registry/manage-versions-and-aliases/> | Versions, statuses, aliases, `latest` resolution |
| <https://mlflow.org/docs/latest/genai/skill-registry/pull-skills/> | Pull/install, agent destinations, UI "Install for" |
| <https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html> | Fluent Skill Registry APIs (experimental) |
| <https://mlflow.org/docs/latest/api_reference/python_api/mlflow.client.html> | Lower-level `MlflowClient` skill APIs |
| <https://github.com/mlflow/mlflow/releases/tag/v3.18.0> | Release evidence: new experimental feature |

## Version facts

- Introduced in **MLflow 3.18.0**; all Skill Registry Python entities are experimental.
- No separate extra is documented; local uploads need an HTTP tracking server with
  artifact serving enabled.
- 3.18.0 UI added agent selection ("Install for") with agent icons and single- vs
  multi-skill registration guidance.

## Related but distinct

- `version-tracking`: app `LoggedModel` versions, not `SkillVersion`.
- `prompt-registry`: `prompts:/` prompt versions, not file-based skills.
- `mcp-registry`: MCP servers/tools, not agent skills.
- `agent-serving`: pull/install skills before serving; no automatic runtime loading.
