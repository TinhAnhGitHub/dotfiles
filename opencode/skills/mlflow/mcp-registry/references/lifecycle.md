# MCP Registry lifecycle

## Entities and mutability

| Entity | Identity | Mutable data | Operational meaning |
|---|---|---|---|
| `MCPServer` | namespaced name | display metadata, tags | logical product/catalog entry |
| `MCPServerVersion` | server name + semver | status/tags; server definition is versioned | reviewed configuration and tool snapshot |
| Alias | server name + alias | target version | controlled indirection for consumers |
| `MCPAccessEndpoint` | endpoint ID | URL/target subject to API | real connection path and transport |

Changing server configuration requires a new semver. Do not edit reality behind a version without
registering/validating the change; the registry's tool list is only a point-in-time snapshot.

## Status state machine

```text
draft ──→ active ──→ deprecated ──→ deleted
  └────────→ deleted       └──→ active
active ──→ draft
```

Documented transitions:

- `draft → active|deleted`
- `active → draft|deprecated`
- `deprecated → active|deleted`

```python
mlflow.genai.update_mcp_server_version(
    name="com.example/support-tools",
    version="1.1.0",
    status="active",
)
```

Activation should follow schema/security/integration/evaluation approval; status alone does not
enforce runtime authorization.

## Semantic versioning policy

- **PATCH:** compatible implementation/security fix with no tool contract break.
- **MINOR:** backward-compatible tools or optional fields.
- **MAJOR:** removed/renamed tools, changed required arguments, authorization or side-effect
  semantics, or incompatible output schema.
- **Prerelease:** experimental candidate such as `2.0.0-beta.1`; keep out of production aliases
  until policy permits.

Automated schema comparison cannot detect semantic side effects. Require human/security review for
tools that write data, trigger jobs, send messages, spend money, or cross tenant boundaries.

## Aliases

```python
mlflow.genai.set_mcp_server_alias(
    name="com.example/support-tools",
    alias="production",
    version="1.1.0",
)

resolved = mlflow.genai.get_mcp_server_version_by_alias(
    name="com.example/support-tools",
    alias="production",
)
```

Use aliases for controlled rollout, but record the resolved semver/tool digest on every app release
and production trace. An alias-following endpoint can change behavior without an app code change.

`latest` is reserved and automatically resolved; avoid it in production because it can move based
on active statuses.

## Tags

Recommended server tags: owner team, service tier, data classification, source repository,
security-review policy. Recommended version tags: release notes, source checksum, build ID,
evaluation run ID, schema digest, approval ticket, deprecation date.

```python
mlflow.genai.set_mcp_server_version_tag(
    name="com.example/support-tools",
    version="1.1.0",
    key="evaluation_run_id",
    value="<RUN_ID>",
)
```

Tags are metadata, not a secret store or authorization control.

## Deletion

Versions must be draft/deprecated before deletion. A server can be deleted only when all versions
are non-active. Before deletion, search access endpoints and consumer inventories, move aliases,
announce deprecation, observe remaining traffic, and retain required audit evidence.
