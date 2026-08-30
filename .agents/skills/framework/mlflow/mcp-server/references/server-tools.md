# MLflow MCP Server Tools and Security

## Configuration

```json
{
  "mcpServers": {
    "mlflow-mcp": {
      "command": "uv",
      "args": ["run", "--with", "mlflow[mcp]>=3.5.1", "mlflow", "mcp", "run"],
      "env": {
        "MLFLOW_TRACKING_URI": "<tracking-uri>",
        "MLFLOW_EXPERIMENT_ID": "<experiment-id>",
        "MLFLOW_MCP_TOOLS": "traces,scorers,experiments"
      }
    }
  }
}
```

`MLFLOW_TRACKING_URI` selects the server. `MLFLOW_EXPERIMENT_ID` supplies a default experiment.
`MLFLOW_MCP_TOOLS` accepts `genai`, `ml`, `all`, or a comma-separated allow-list. The exact
available categories and client configuration keys are version/client-specific.

## Field selection

Prefer narrow fields in `search_traces` and `get_trace`:

```text
info.trace_id,info.state,info.execution_duration,
info.tags.*,data.spans.*.name
```

The documented dot notation supports wildcards and backticks for names containing dots. Retrieve
assessments or span attributes only when needed. Narrowing fields reduces response size, assistant
token usage, and accidental disclosure; it does not replace server-side authorization.

## Tool capabilities

| Tool | Use | Risk |
|---|---|---|
| `search_traces` | Find traces in an experiment | Can expose broad user content |
| `get_trace` | Inspect one trace | May expose full prompts, outputs, and attachments |
| `set_trace_tag` / `delete_trace_tag` | Add/remove metadata | Can affect downstream filtering and reports |
| `log_feedback` | Record an assessment of behavior | Should preserve source and rationale |
| `log_expectation` | Record ground truth | Human approval required for consequential labels |
| `get_assessment` / `update_assessment` | Review/correct an assessment | Prefer override/audit-preserving semantics |
| `delete_assessment` | Remove an assessment | Destructive; audit impact |
| `delete_traces` | Remove trace data | Destructive; require explicit policy |

## Source and approval

Assistant-generated feedback is not automatically human ground truth. Use `source_type`, stable
assessment names, rationale, reviewer identity, and an incident/app-version reference. Convert a
verified trace to an expectation and evaluation dataset record only after privacy review and human
approval.

## Sources

- https://mlflow.org/docs/latest/genai/mcp/
- https://mlflow.org/docs/latest/genai/tracing/search-traces/
- https://mlflow.org/docs/latest/genai/tracing/collect-user-feedback/
- https://mlflow.org/docs/latest/genai/assessments/expectations/
- https://modelcontextprotocol.io/
