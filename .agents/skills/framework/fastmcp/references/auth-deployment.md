# FastMCP Auth & Deployment — HTTP, CLI, Config, Integrations

Sources: `v3/servers/auth/*`, `v3/deployment/*`, `cli/*`, `v3/integrations/*`.

## 1. Auth decision table (HTTP-only; stdio needs none)

| Situation | Use | Why |
|---|---|---|
| You already issue JWTs (gateway, SSO) | `JWTVerifier(jwks_uri=..., issuer=..., audience=...)` | Pure validation; see `auth/token-verification` |
| Provider supports DCR (Descope, WorkOS AuthKit) | `RemoteAuthProvider` e.g. `AuthKitProvider(authkit_domain=..., base_url=...)` | Auto client registration; see `auth/remote-oauth` |
| Provider lacks DCR (GitHub, Google, Azure, AWS, most enterprise) | `OAuthProxy` subclass e.g. `GitHubProvider(client_id=..., client_secret=..., base_url=...)` | DCR-compliant front, fixed creds upstream; see `auth/oauth-proxy` / `oidc-proxy` |
| Interactive + machine tokens together | `MultiAuth(server=OAuthProxy(...), verifiers=[JWTVerifier(...)])` | First success wins; server owns OAuth routes; see `auth/multi-auth` |
| Air-gapped / full control | Custom `OAuthProvider` | You own users, tokens, UI, lifecycle; avoid unless required; see `auth/full-oauth-server` |

```python
import os
from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

auth = GitHubProvider(
    client_id=os.environ["GITHUB_CLIENT_ID"],
    client_secret=os.environ["GITHUB_CLIENT_SECRET"],
    base_url=os.environ.get("BASE_URL", "http://localhost:8000"),
)
mcp = FastMCP("My Server", auth=auth)
```

Access identity inside tools via `CurrentAccessToken()` /
`TokenClaim("sub"|"oid"|...)`. Load secrets from env, never commit them.

## 2. Running and deploying HTTP

```python
if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)  # -> http://localhost:8000/mcp

app = mcp.http_app()  # ASGI for uvicorn/workers; mcp.http_app(path="/api/mcp/")
```

- `mcp.run()` cannot run inside an async function; use
  `await mcp.run_async(...)` there.
- Custom endpoints alongside MCP:
  `@mcp.custom_route("/health", methods=["GET"])` (forwarded through mounts).
- CORS: pass Starlette `Middleware(CORSMiddleware, ...)` to `http_app`.
- FastAPI: `fastapi_app.mount("/mcp", mcp.http_app())`; combine lifespans
  with `combine_lifespans(...)`. See `integrations/fastapi`,
  `integrations/openapi` (generate servers from OpenAPI).
- Session state: default in-memory; distributed needs
  `FastMCP(session_state_store=RedisStore(...))` (`servers/storage-backends`).
- Background tasks: `@mcp.tool(task=True)` + `pip install "fastmcp[tasks]"`.
- Horizon (managed hosting): push `server.py` to GitHub, entrypoint
  `server.py:mcp` → `https://<project>.fastmcp.app/mcp`.

## 3. `fastmcp.json` and CLI

```bash
fastmcp run server.py:mcp --transport http --port 8000
fastmcp run server.py --python 3.11 --with pandas --reload
fastmcp inspect server.py:mcp
fastmcp install server.py:mcp --name "My Server"   # Claude/Cursor/Gemini clients
fastmcp client list-tools server.py:mcp
fastmcp client call-tool server.py:mcp greet '{"name": "World"}'
fastmcp generate-cli server.py:mcp > cli.py
```

- CLI finds `mcp`/`server`/`app` and ignores `__main__`. `--with`,
  `--with-requirements`, `--project`, `--python` re-exec via `uv run`.
- Declarative projects use `fastmcp.json`
  (`deployment/server-configuration`).

## 4. Integrations (per-product pages under `v3/integrations/`)

Clients/hosts: ChatGPT, Claude Code (`fastmcp install` / MCP config),
Claude Desktop (stdio), Cursor, Gemini CLI, Goose. LLM SDKs: Anthropic,
Gemini, OpenAI, Pydantic AI (`FastMCPToolset`). Auth providers: Auth0,
AuthKit/WorkOS, Cognito, Entra/Azure, Descope, Discord, GitHub, Google,
Hugging Face, Keycloak, OCI, PropelAuth, Scalekit, Supabase. Authorization
add-ons: Eunomia, Permit.io.
