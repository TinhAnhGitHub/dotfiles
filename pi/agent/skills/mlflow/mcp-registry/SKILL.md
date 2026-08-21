---
name: mcp-registry
description: >
  MLflow MCP Registry for registering, versioning, discovering, governing, and connecting
  Model Context Protocol servers, including server.json, semantic versions, statuses,
  aliases, access endpoints, tool snapshots, refresh workflows, CI/CD, and agent lineage.
  Use whenever users mention MLflow MCP Registry, MCP server catalogs, tool discovery,
  MCP version promotion, or governed agent tool dependencies. Load parent `mlflow` first.
compatibility: MLflow 3.15.0+; MCP Registry is experimental and tool discovery requires the mcp extra
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-01"
---

# MLflow MCP Registry

The registry is a **catalog and lifecycle plane**, not an MCP runtime, proxy, authorization
system, or evaluation engine. It records server definitions, immutable semantic versions, tool
snapshots, aliases, and connection endpoints. The live server still enforces runtime security and
availability.

## Mandatory preflight

1. Load parent `mlflow`; require a compatible MLflow server/client and inspect exact signatures.
2. State that MCP Registry is experimental and pin the MLflow minor version.
3. Validate the `server.json` source, ownership, package/remotes, semver, and checksum.
4. Decide whether tool discovery may perform network egress; install `mlflow[mcp]` if needed.
5. Define lifecycle (`draft → active → deprecated → deleted`), aliases, and rollback.
6. Define runtime auth separately; do not persist tokens in server metadata, tags, or code.
7. Trace/evaluate the consuming agent before promotion.
8. Run `python scripts/inspect_mcp_registry.py` in the target environment.

## Entity model

```text
MCPServer: logical namespaced server
  ├─ MCPServerVersion: immutable semver server.json + tool snapshot + status
  ├─ alias: movable reference to a server version
  └─ MCPAccessEndpoint: separate connection record pinned to version or alias
```

Use reverse-DNS names such as `com.example/support-tools`. `latest` is reserved and resolves to
the highest active semver, falling back to the highest non-deleted version. Do not use it for
reproducible production releases.

## Canonical governed workflow

```text
reviewed server.json + source provenance
  → register draft version without uncontrolled discovery
  → discover/refresh tools from approved network boundary
  → diff schemas and security impact
  → integration + agent trace/evaluation tests
  → mark active and move staging/production alias
  → connect through governed access endpoint
  → monitor tool calls and periodically verify snapshot drift
  → deprecate old version, migrate consumers, then delete
```

## Quick implementation

```python
import mlflow

name = "com.example/support-tools"
version = mlflow.genai.register_mcp_server(
    server_json={
        "name": name,
        "version": "1.0.0",
        "description": "Read-only support knowledge tools",
        "remotes": [
            {"url": "https://mcp.example.com/support", "type": "streamable-http"}
        ],
    },
    status="draft",
    source="https://github.com/example/support-tools/releases/tag/v1.0.0",
    tools=[],  # Deliberately skip discovery during registration.
)

preview = mlflow.genai.refresh_mcp_server_version_tools(
    name=name,
    version="1.0.0",
    dry_run=True,
)
# Review and test preview.tools before saving and activation.
```

Never put a literal bearer token in committed code. Supply short-lived headers at execution time
from an approved secret/identity mechanism and ensure logs redact them.

## Reference router

| Need | Read |
|---|---|
| Entities, status transitions, semver, aliases, tags, deletion | [`references/lifecycle.md`](references/lifecycle.md) |
| Registration, source provenance, auto-discovery, refresh and drift | [`references/registration-discovery.md`](references/registration-discovery.md) |
| Access endpoints, transports, auth/security and operations | [`references/access-security.md`](references/access-security.md) |
| Agent versioning, tracing, evaluation, CI/CD, Databricks connections | [`references/llmops-integration.md`](references/llmops-integration.md) |
| Official docs and experimental/version notes | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

Every design should include immutable source provenance, owner and data classification, explicit
status/alias policy, tool-schema diff, egress/auth threat model, trace/evaluation gate, rollback,
drift refresh policy, and consumer migration plan. A successful registration with `tools=None`
does not mean discovery or server health succeeded.
