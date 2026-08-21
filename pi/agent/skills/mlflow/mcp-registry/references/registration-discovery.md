# Registration, discovery, and tool drift

## Register from reviewed payload

```python
import mlflow

server_json = {
    "name": "com.example/support-tools",
    "version": "1.0.0",
    "description": "Read-only support tools",
    "packages": [
        {
            "registryType": "pypi",
            "identifier": "example-support-mcp",
            "version": "1.0.0",
            "transport": {"type": "stdio"},
        }
    ],
    "remotes": [
        {"url": "https://mcp.example.com/support", "type": "streamable-http"}
    ],
}

registered = mlflow.genai.register_mcp_server(
    server_json=server_json,
    status="draft",
    source="https://github.com/example/support-mcp/releases/tag/v1.0.0",
    tools=[],
)
```

Required top-level fields are `name` and `version`; `description`, `icons`, `packages`, and
`remotes` are optional. Record immutable source release/digest, not a moving branch URL.

## Register from URL or file

```python
registered = mlflow.genai.register_mcp_server_from_url(
    url="https://raw.githubusercontent.com/example/support-mcp/v1.0.0/server.json",
    status="draft",
)
```

Fetch into a controlled review pipeline when supply-chain integrity matters. Validate schema,
allowed package registries, remote host allow-list, HTTPS, source signature/checksum, semver, and
ownership before registration.

## Tool auto-discovery behavior

When `tools` is omitted, MLflow attempts to connect to the first usable remote. It requires:

```bash
pip install 'mlflow[mcp]'
```

Discovery errors (network, auth, timeout) soft-fail: registration still succeeds with
`tools=None`. Therefore CI must assert the expected tool snapshot rather than treating a returned
version as success.

Controls:

- `tools=[]` skips discovery deliberately;
- `MLFLOW_ENABLE_MCP_TOOL_DISCOVERY=false` disables it globally;
- `mcp_server_access_headers=...` supplies protected-server headers for that operation;
- `create_access_endpoints_from_remotes=True` can create version-pinned endpoints when registering
  an active version.

Avoid automatic discovery in untrusted CI networks because it performs outbound connections to
payload-provided URLs. Apply DNS/IP/redirect controls and egress allow-lists outside the registry.

## Review-first refresh

```python
preview = mlflow.genai.refresh_mcp_server_version_tools(
    name="com.example/support-tools",
    version="1.0.0",
    dry_run=True,
)

for tool in preview.tools or []:
    print(tool.name, tool.description)
```

After approval, rerun without `dry_run=True` to save. For protected remotes, retrieve a short-lived
credential at runtime and pass it in `mcp_server_access_headers`; never log/print it.

## Schema diff checklist

For each tool compare:

- added/removed/renamed tools;
- argument types, required fields, enum/range/default changes;
- output schema and error model;
- read versus write/irreversible side effects;
- permission scopes and data accessed;
- timeout, idempotency, pagination, and rate limits;
- prompt-injection/data-exfiltration exposure;
- human-approval requirements.

Snapshots are not health checks and are not kept in sync automatically. Schedule drift detection,
but do not overwrite approved snapshots automatically when a live server changes unexpectedly;
alert, quarantine, and register a reviewed new version.
