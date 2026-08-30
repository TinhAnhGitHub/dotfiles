# MLflow AI Assistant Source Ledger

Reviewed 2026-08-30. Assistant availability and supported coding-agent backends are beta and
may change; confirm the target MLflow release and local UI behavior.

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/getting-started/try-assistant/ | Assistant capabilities, use cases, local setup, backend support, permissions, FAQ |
| https://mlflow.org/docs/latest/genai/tracing/quickstart/ | `uvx mlflow@latest agent setup` and tracing setup |
| https://mlflow.org/docs/latest/genai/mcp/ | MCP-based trace access for coding assistants |
| https://mlflow.org/docs/latest/genai/eval-monitor/ | Evaluation workflows the Assistant can help configure |
| https://mlflow.org/docs/latest/genai/prompt-registry/ | Prompt management/optimization workflows |
| https://mlflow.org/docs/latest/genai/version-tracking/ | App/agent version workflows |

## Status notes

- Current docs describe local tracking-server availability and beta status.
- Claude Code is described as fully supported, with OpenAI Codex, Gemini CLI, Open Code, and other
  integrations evolving.
- Permission settings are a safety boundary that must be reviewed alongside the coding agent's
  own filesystem/command permissions.
