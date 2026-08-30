# MLflow MCP Server Source Ledger

Reviewed 2026-08-30. The server is experimental; verify tool names, configuration, auth, and
filter behavior against the installed MLflow release.

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/mcp/ | MLflow MCP Server prerequisites, install, client setup, tools, fields, use cases, env config |
| https://mlflow.org/docs/latest/genai/tracing/ | Traces and observability exposed through MCP |
| https://mlflow.org/docs/latest/genai/tracing/search-traces/ | Search/filter semantics and backend limits |
| https://mlflow.org/docs/latest/genai/tracing/collect-user-feedback/ | Feedback assessment lifecycle |
| https://mlflow.org/docs/latest/genai/assessments/expectations/ | Human ground-truth expectations |
| https://mlflow.org/docs/latest/genai/eval-monitor/ai-insights/ai-issue-discovery/ | AI-assisted experiment analysis via MCP/CLI |
| https://mlflow.org/docs/latest/genai/getting-started/try-assistant/ | MLflow AI Assistant using coding-agent context |
| https://modelcontextprotocol.io/ | Protocol concepts and client/server context |

## Status notes

- MLflow 3.5.1+ and the `mcp` extra are required by the current page.
- This server manages/accesses MLflow trace data; it is not the MCP Registry and does not host
  application inference.
- `extract_fields` and `MLFLOW_MCP_TOOLS` are useful least-privilege/context controls, but retain
  tracking-server authorization and human approval for destructive or ground-truth operations.
