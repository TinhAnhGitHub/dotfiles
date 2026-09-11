# FastMCP Source Ledger — URLs and Version Notes

Authoritative roots: `https://gofastmcp.com/v3/...` (v3, stable for this
skill), `https://gofastmcp.com/...` (v4/latest), index
`https://gofastmcp.com/llms.txt`, MCP endpoint
`https://gofastmcp.com/mcp` (`search_fast_mcp`). Any page → markdown by
appending `.md`. Community structure adapted from
`https://github.com/jxnxts/fastmcp-skill` (SKILL + tools,
resources-prompts, context-di-middleware, composition-providers, testing,
deployment references over bundled v3 docs).

## Getting started / server core

- Welcome: `/v3/getting-started/welcome`
- Installation: `/v3/getting-started/installation` (extras `fastmcp[tasks]`,
  `fastmcp[apps]`; 3.3+ pip-upgrade reinstall note; pin exact versions)
- Quickstart: `/v3/getting-started/quickstart` (`mcp.run()` stdio vs
  `transport="http"`, `Client("http://localhost:8000/mcp")`, `app=True`
  Prefab preview `fastmcp dev apps`)
- Server: `/v3/servers/server` (constructor: `name/instructions/version`,
  `auth/lifespan`, `on_duplicate`, `strict_input_validation`,
  `list_page_size`, `mask_error_details`, `dereference_schemas`)
- Tools: `/v3/servers/tools` — v2.10 output schemas/structured content,
  v2.11 meta, v2.13 icons/strict-validation, v2.14 DI-hide, v3.0
  timeout/versioning/visibility
- Resources: `/v3/servers/resources` — v2.2 wildcards, v2.13 query params,
  v3.0 `ResourceResult`/visibility/versioning
- Prompts: `/v3/servers/prompts` — v2.9 typed args via JSON strings, v3.0
  `Message`/`PromptResult`/visibility/versioning, v3.2 docstring
  descriptions
- Context: `/v3/servers/context` — v2.2 `get_context()`, v2.10 elicitation,
  v2.13 prompts access, v2.14 `CurrentContext()`, v3.0 session state +
  per-session visibility
- DI: `/v3/servers/dependency-injection` — Docket-backed; `Depends`,
  `Current*`, `TokenClaim`, task deps need `fastmcp[tasks]`
- Middleware: `/v3/servers/middleware` (`on_message→on_request→tool/resource/prompt`)
- Lifespan: `/v3/servers/lifespan` (composable with `|`)
- Composition: `/v3/servers/composition` (v2.2 mount liveness, v2.4 custom
  routes, v3.0 namespaces/conflicts/tag filters); providers
  `/v3/servers/providers/*` (local/filesystem/proxy/skills/custom)
- Transforms: `/v3/servers/transforms/*`, visibility `/v3/servers/visibility`,
  versioning `/v3/servers/versioning`, tasks `/v3/servers/tasks`,
  sessions `/v3/servers/sessions` (v4 stateful-on-stateless changes),
  telemetry `/v3/servers/telemetry`, testing `/v3/servers/testing`

## Clients / apps / deploy

- Client: `/v3/clients/client` (v2.0+; in-memory/stdio/HTTP/config),
  transports `/v3/clients/transports`, ops `tools/resources/prompts`,
  callbacks `sampling/elicitation/progress/logging/roots/notifications`,
  auth `auth/{oauth,client-credentials,cimd,bearer}`, `fastmcp-remote`,
  `client-only-package`
- Apps: `/v3/apps/{overview,quickstart,fastmcp-app,prefab,generative,low-level,development,examples,architecture,providers/*}`
  (v3.0+; needs `fastmcp[apps]`)
- Auth: `/v3/servers/auth/{authentication,token-verification,remote-oauth,oauth-proxy,oidc-proxy,full-oauth-server,multi-auth}`
  (HTTP-only; v2.11+; v3.1 `MultiAuth`)
- Deploy: `/v3/deployment/{running-server,http,server-configuration,prefect-horizon,sandboxed-agents}`;
  CLI `cli/{overview,running,install-mcp,inspecting,client,generate-cli,auth}`;
  integrations `/v3/integrations/*` (fastapi/openapi/chatgpt/claude-code/desktop/cursor/...)
- Upgrades: `/getting-started/upgrading/from-fastmcp-{3,2}`,
  `from-{mcp-sdk-v1,mcp-sdk-v2,low-level-sdk-v1,low-level-sdk-v2}`;
  changes `/getting-started/whats-new`, `/changelog`, `/updates`, `/more/faq`
