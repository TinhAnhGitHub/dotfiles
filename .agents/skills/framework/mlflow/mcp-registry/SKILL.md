---
name: mcp-registry
description: >
  MLflow MCP Registry for registering, versioning, discovering, governing, and connecting
  Model Context Protocol servers, including server.json, semantic versions, statuses,
  aliases, access endpoints, tool snapshots, refresh workflows, CI/CD, and agent lineage.
  Use whenever users mention MLflow MCP Registry, server catalogs, tool discovery,
  MCP version promotion, or governed agent tool dependencies. Load parent `mlflow` first.
compatibility: MLflow 3.15.0+; MCP Registry is experimental and tool discovery requires the mcp extra; 3.17 adds sub-resource RBAC, 3.18 changes version identity case sensitivity
metadata:
  version: "0.3.0"
  docs-reviewed: "2026-11-21"
---

# MLflow MCP Registry

The registry is a **catalog and lifecycle plane**, not an MCP runtime, proxy, runtime
authorization system, or evaluation engine. It records server definitions, immutable semantic
versions, tool snapshots, aliases, and connection endpoints. The live server still enforces
runtime security and availability. MLflow RBAC **does** govern registry resources, including
`mcp_server_version`, from MLflow 3.17.0 (wildcard-only grants such as
`mcp_server_version:*`, with explicit `DENY` overriding positive grants and parent
`mcp_server` permission still required). Use `mcp-server` for the separate MLflow MCP
Server that exposes MLflow trace operations to coding agents.

### Version gates and migration (3.17–3.18)

- **3.17.0**: fine-grained sub-resource RBAC (see above).
- **3.18.0 breaking change**: MCP server version identity is case-sensitive on MySQL
  and SQL Server. Correct case-mismatched references **before** upgrading; the
  database migration checks exact-case matches and stops before its own schema
  changes if correction is required. On case-insensitive databases, registry and
  MCP permissions now use stored resource names — re-save differently cased grants
  under the stored spelling. Admin deletes also require the stored name spelling.
- 3.17.0 and 3.18.0 require a coordinated SQL upgrade (`mlflow db upgrade`) with all
  writers stopped; mixed-version rolling upgrades are not supported.

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

Promote to active, pin an alias, and create an access endpoint:

```python
import mlflow

name = "com.example/support-tools"
mlflow.genai.update_mcp_server_version(name=name, version="1.0.0", status="active")
mlflow.genai.set_mcp_server_alias(name=name, alias="production", version="1.0.0")
resolved = mlflow.genai.get_mcp_server_version_by_alias(name=name, alias="production")
print(resolved.version)

endpoint = mlflow.genai.create_mcp_access_endpoint(
    server_name=name,
    url="https://mcp.example.com/support",
    transport_type="streamable-http",
    server_alias="production",
)
print(endpoint.id, endpoint.url)
```

Lower-level `MlflowClient` equivalents include `create_mcp_server_version`,
`create_mcp_access_endpoint`, `search_mcp_servers`, `search_mcp_server_versions`,
`search_mcp_access_endpoints`, getters, updates, and deletes. Search APIs accept
`filter_string`, `order_by`, `max_results`, and `page_token`. `update_mcp_server_version`
supports per-key `connect_options`; `ConnectOptionSettings(hidden=False)` controls
whether a value is masked. Tool refresh prefers endpoints that resolve to the
requested version; if configured endpoints do not resolve, refresh fails without
falling back to `server_json.remotes`.

Never put a literal bearer token in committed code. Supply short-lived headers at execution time
from an approved secret/identity mechanism and ensure logs redact them.

## Registry/runtime boundary

An access endpoint can resolve a pinned version for reproducibility or an alias for deliberate
live switching. Store the resolved version, tool-schema digest, endpoint identity, and consuming
app version in release evidence. A registry snapshot does not prove the remote server is healthy,
authorized, or unchanged at runtime; refresh and observe it.

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
