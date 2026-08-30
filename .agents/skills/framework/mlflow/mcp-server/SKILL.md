---
name: mcp-server
description: >
  MLflow MCP Server for coding agents and MCP clients: search/get/delete traces,
  select fields, manage tags and assessments, log feedback/expectations, scope
  tools with `MLFLOW_MCP_TOOLS`, and connect to OSS or Databricks tracking.
  Use whenever a user asks an assistant to inspect or mutate MLflow data through
  MCP, configure `mlflow mcp run`, or use AI-assisted experiment analysis.
  Load the parent `mlflow` skill first.
compatibility: MLflow 3.5.1+; the MLflow MCP Server is experimental and requires the `mcp` extra
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-30"
---

# MLflow MCP Server

The MLflow MCP Server is an MCP access layer for MLflow tracking data. It lets compatible coding
agents search and inspect traces, analyze behavior, and record feedback/expectations. It is
separate from the **MCP Registry** (which catalogs external MCP servers) and from **Agent Server**
(which hosts an application). The server is experimental and exposes destructive operations, so
scope tools and permissions deliberately.

## Mandatory preflight

1. Inspect the MLflow version; current docs require MLflow 3.5.1 or newer.
2. Identify the MCP client (VS Code, Cursor, Claude, or another client), tracking URI, experiment,
   and auth method.
3. Decide whether the assistant needs read-only trace analysis, assessment writes, tag changes,
   or deletion. Start with the smallest tool category.
4. Classify trace contents and ensure the assistant/provider is allowed to see prompts, outputs,
   tool arguments, attachments, and assessment rationales.
5. Load `tracing-observability` for trace/schema/privacy semantics and `evaluation-monitoring`
   for the feedback → expectation → dataset workflow.
6. Load `mcp-registry` only when the task is registering or connecting an external MCP server;
   do not use the registry skill for this local MLflow data server.

## Install and configure

```bash
pip install 'mlflow[mcp]>=3.5.1'
```

A project-scoped `.mcp.json` can use an ephemeral `uv` environment:

```json
{
  "mcpServers": {
    "mlflow-mcp": {
      "command": "uv",
      "args": ["run", "--with", "mlflow[mcp]>=3.5.1", "mlflow", "mcp", "run"],
      "env": {
        "MLFLOW_TRACKING_URI": "<tracking-uri>",
        "MLFLOW_EXPERIMENT_ID": "<default-experiment-id>",
        "MLFLOW_MCP_TOOLS": "traces,scorers,experiments"
      }
    }
  }
}
```

Use the client-specific configuration shape: VS Code uses `servers`, while Cursor/Claude
configurations use their documented `mcpServers`/CLI forms. Keep credentials in the client or
environment secret mechanism, never in a committed config. For Databricks, use the supported
`databricks` tracking URI and workspace authentication rather than embedding a token.

## Tool scope

| Scope | Meaning |
|---|---|
| `genai` (default) | GenAI traces, scorers, experiments, and runs |
| `ml` | Traditional ML experiments, runs, models, and deployments |
| `all` | Both categories |
| comma-separated categories | Narrow allow-list such as `traces,scorers,experiments` |

`MLFLOW_MCP_TOOLS` reduces assistant context and limits exposed capabilities. A safe default for
incident analysis is trace/scorer/experiment access without deletion; confirm the target release's
category mapping before relying on it as a hard security boundary.

## Available GenAI operations

The current server documents tools for:

- `search_traces` and `get_trace` with `extract_fields` selection;
- deleting traces by IDs/timestamp;
- setting/deleting trace tags;
- logging feedback and expectations;
- retrieving, updating, and deleting assessments.

Use `extract_fields` such as `info.trace_id,info.state,data.spans.*.name` to reduce response size
and prevent unnecessary exposure. Search only the experiment/time slice needed. Validate filter
syntax against the target MLflow server; MCP examples and trace-search syntax are version/backend
dependent.

## Safe assistant workflow

```text
search a narrow slice
  → retrieve selected fields
  → inspect full trace only for representative cases
  → hypothesize and compare versions/latency/tool behavior
  → log feedback or human-approved expectations
  → send approved cases to the evaluation dataset workflow
```

Use AI-assisted experiment analysis (`mlflow ai-commands run genai/analyze_experiment`) or the
documented assistant command when available, but treat generated hypotheses as untrusted analysis.
Verify against traces before creating expectations, changing code, or declaring an issue resolved.

Do not let an assistant delete traces, overwrite human assessments, modify production tags, or
change deployment state without explicit project policy and human confirmation. Prefer assessment
override/update semantics where audit history matters.

## Privacy, auth, and operations

- The MCP server inherits tracking-server permissions; it is not a second authorization model.
- Use a separate low-privilege identity for analysis and a stricter identity for writes/deletion.
- Mask/redact sensitive trace fields before assistant access when possible.
- Do not send provider keys, bearer tokens, or raw tool credentials through trace fields.
- Restrict server config to approved projects/experiments and log MCP client activity where the
  deployment supports it.
- Test remote tracking latency, large traces, field-selection behavior, failed writes, and auth
  expiration. An assistant should fail closed for destructive actions.

## Reference router

| Need | Read |
|---|---|
| Installation, configuration, tools, field selection, and environment variables | [`references/server-tools.md`](references/server-tools.md) |
| Official MCP Server page and cross-feature sources | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Every MCP setup must state MLflow/client versions, tracking/auth context, exposed tool scope,
data classification, field-selection strategy, write/delete approval policy, and the path from
assistant findings to human-approved evaluation evidence.

## Related skills

- `tracing-observability` for trace instrumentation, semantics, masking, and retention.
- `evaluation-monitoring` for feedback, expectations, datasets, judges, and issue discovery.
- `ai-assistant` for the MLflow UI's local beta coding-agent experience.
- `mcp-registry` for cataloging external MCP servers and tool versions.
- `agent-serving` for hosting the application an MCP client may invoke.
