# MCP Registry source ledger

Reviewed 2026-08-30. Verify `/latest/` APIs against the installed MLflow release and the remote
MCP server/transport; Registry behavior is experimental.

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/mcp-registry/ | Concepts, entity model, quickstart; experimental since MLflow 3.15.0 |
| https://mlflow.org/docs/latest/genai/mcp-registry/register-mcp-servers/ | Payload/URL/UI registration, discovery, versions, endpoint auto-create |
| https://mlflow.org/docs/latest/genai/mcp-registry/manage-versions-and-aliases/ | Semver, statuses, transitions, aliases, reserved latest, tags, deletion |
| https://mlflow.org/docs/latest/genai/mcp-registry/connect-to-servers/ | Version/alias endpoints, transports, management, instructions, tool refresh |
| https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html | Exact MCP Registry Python API signatures; all are experimental |
| https://registry.modelcontextprotocol.io/docs | Open MCP Registry `server.json` standard referenced by MLflow |
| https://modelcontextprotocol.io/ | Model Context Protocol concepts referenced by MLflow |
| https://mlflow.org/docs/latest/genai/mcp/ | MLflow MCP Server; separate product from MCP Registry |
| https://mlflow.org/docs/latest/genai/flavors/responses-agent-intro/ | Agent MCP/tool output items and packaging |
| https://mlflow.org/docs/latest/genai/tracing/ | Tool-call and agent tracing |
| https://mlflow.org/docs/latest/genai/eval-monitor/ | Agent/tool evaluation and production feedback loop |

## Status notes

- MCP Registry is experimental and introduced in MLflow 3.15.0; pin client/server together.
- Tool discovery requires `mlflow[mcp]` and may soft-fail to `tools=None`.
- Tool definitions are snapshots and do not auto-sync; refresh and review schema drift.
- `latest` is reserved and dynamically resolves; it is unsuitable as reproducible release input.
- Official docs expose Python SDK and UI workflows; do not invent an MLflow MCP Registry CLI.
- The MLflow MCP Server is the separate tracking-data access layer for coding agents; route those
  requests to `../mcp-server/SKILL.md`.
