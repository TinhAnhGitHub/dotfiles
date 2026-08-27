# Access endpoints, security, and operations

## Version-pinned versus alias-following endpoint

```python
fixed = mlflow.genai.create_mcp_access_endpoint(
    server_name="com.example/support-tools",
    url="https://mcp.example.com/support",
    transport_type="streamable-http",
    server_version="1.0.0",
)

production = mlflow.genai.create_mcp_access_endpoint(
    server_name="com.example/support-tools",
    url="https://mcp.example.com/support",
    transport_type="streamable-http",
    server_alias="production",
)
```

Use fixed versions for reproducible jobs and incident replay. Use alias-following endpoints for
managed rollout only when the promotion process includes evaluation, audit, observability, and
rollback. `streamable-http` is the documented recommended/default transport; `sse` remains
available.

## Manage endpoints

```python
endpoints = mlflow.genai.search_mcp_access_endpoints(
    server_name="com.example/support-tools"
)

endpoint = endpoints[0]
mlflow.genai.update_mcp_access_endpoint(
    server_name="com.example/support-tools",
    endpoint_id=endpoint.id,
    url="https://mcp-v2.example.com/support",
)
```

An endpoint URL update is operationally significant even if server version/alias does not change.
Capture endpoint ID, URL identity/digest, resolved version, gateway/proxy version, and timestamp in
release evidence.

## Security boundary

The registry does not replace:

- TLS/certificate validation;
- workload identity/OAuth and token rotation;
- per-user/tenant authorization inside tools;
- network egress/DNS/redirect controls;
- input/output validation and content controls;
- side-effect approval and idempotency;
- runtime rate limits, timeouts, circuit breakers, and audit logs.

Do not rely on tool descriptions as policy. The server must enforce authorization for every call.
Treat tool outputs as untrusted content that can contain prompt injection or sensitive data.

## Threat review

| Risk | Control |
|---|---|
| Malicious `server.json` remote | signed source, schema validation, hostname allow-list, controlled discovery runner |
| DNS rebinding/redirect to internal service | egress proxy, DNS/IP revalidation, redirect limits |
| Credential leakage | short-lived identity, redacted headers/traces, no metadata/tag secrets |
| Tool schema drift | dry-run refresh, digest alert, new reviewed semver |
| Excessive agent authority | least-privilege scopes, per-tool allow-list, user-bound auth |
| Irreversible side effect | explicit approval, idempotency key, audit/compensation workflow |
| Cross-tenant access | server-side tenant enforcement, tests, trace metadata and review |

## Operational checks

- endpoint reachability and MCP handshake;
- expected tools and schema digest;
- authentication/authorization denial paths;
- tool latency/error/rate-limit behavior;
- circuit-breaker and timeout behavior;
- alias resolution and rollback;
- logs/traces redact credentials and sensitive payloads;
- deprecation warnings and consumer inventory.

MLflow UI can generate Claude Code and `.mcp.json` connection instructions. Review generated
commands/config before use and keep credentials out of checked-in files.
