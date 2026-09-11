---
name: fastmcp
description: Use whenever a user asks to build, debug, test, deploy, operate, or extend a FastMCP server, client, or app. Covers @mcp.tool/@mcp.resource/@mcp.prompt, Context, dependency injection, middleware, lifespans, composition/mount/proxy, testing with Client, auth (JWT/OAuth/proxy/MultiAuth), HTTP/STDIO deployment, fastmcp.json, CLI, FastAPI integration, and interactive Apps. Trigger on FastMCP, MCP server, Model Context Protocol, @mcp.tool, add a tool, or create an MCP endpoint.
compatibility: Python 3.10 or newer and FastMCP 3.x (v3 docs are authoritative; v4 adds session-state changes — check source-ledger before using v4-only APIs). Requires fastmcp package; fastmcp[tasks] only for background tasks, fastmcp[apps] only for Prefab apps.
---

# FastMCP

Use this skill to produce implementation-ready FastMCP code rather than a
catalog of concepts. Start with the smallest working server, then add the
transport boundary (stdio vs HTTP), then add reliability controls (validation,
timeouts, visibility, auth). Read only the reference file needed for the
requested topic; read `source-ledger.md` when a detail is version-sensitive.

## 1. Mandatory preflight

Before changing code or recommending commands, establish:

1. **Runtime and versions:** Python `>=3.10`, installed FastMCP version.
   Run:

   ```bash
   python --version
   uv pip show fastmcp 2>/dev/null || pip show fastmcp
   fastmcp version
   ```

   Install with `pip install fastmcp` or `uv add fastmcp`. Pin exact
   versions in production (`fastmcp==3.x.y`), never `>=`. If
   `import fastmcp` fails after a pip upgrade from 3.2 to 3.3+, reinstall
   cleanly: `pip uninstall -y fastmcp fastmcp-slim && pip install fastmcp`.

2. **Transport boundary:** stdio (local, default, one process per client —
   Claude Desktop, CLI) vs Streamable HTTP (remote, many clients, URL ends
   in `/mcp`). SSE is legacy — use HTTP for new projects. Auth applies
   only to HTTP transports; stdio inherits local security.

3. **Component boundary:** tools (LLM-callable functions) vs resources
   (read-only `uri://data`, incl. `{param}` templates) vs prompts
   (reusable message templates). Keep secrets and DB handles out of the
   LLM schema via `Depends()` / `CurrentContext()`.

## 2. Quick start: smallest successful implementation

Save as `my_server.py` and run `python my_server.py` (stdio) or with
`transport="http"` for remote:

```python
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()  # stdio; or mcp.run(transport="http", port=8000)
```

Call it (HTTP example):

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        result = await client.call_tool("greet", {"name": "Ford"})
        print(result.data)

asyncio.run(main())
```

CLI equivalents (CLI imports the object, ignores `__main__`):

```bash
fastmcp run my_server.py:mcp
fastmcp run my_server.py:mcp --transport http --port 8000
fastmcp inspect my_server.py:mcp
```

Expected result: `fastmcp version` prints versions, the tool appears in
`list_tools`, and `call_tool("greet", {"name": ...})` returns the greeting.

## 3. Mental model and end-to-end loop

1. A **server** (`FastMCP`) owns tools, resources, prompts and their
   schemas. Schemas come from type hints + docstrings; `Annotated` /
   `Field` add per-parameter help and constraints.
2. A **transport** moves MCP messages: in-memory object (tests), stdio
   subprocess, or HTTP URL. `async with Client(...)` handles connect +
   handshake.
3. **Context** (`ctx: Context`) is request-scoped: logging, progress,
   `read_resource`, `sample` (LLM), `elicit` (user), session state.
   Each request gets a fresh context.
4. **Composition** (`mount`, `create_proxy`) merges servers live with
   optional `namespace="..."` prefixing. Parent tag filters apply
   recursively.
5. The operational loop is **define → test in-memory → run locally
   (stdio/HTTP) → add visibility/auth → deploy (HTTP/ASGI/Horizon) →
   observe logs/progress → version**.

### Transport decision table

| Need | Prefer | Boundary |
|---|---|---|
| Local single-user, Claude Desktop, CLI | `mcp.run()` stdio | Client spawns process; no auth needed |
| Remote, many clients, web infra | `mcp.run(transport="http", port=8000)` | URL is `http://host:8000/mcp`; add auth |
| Production ASGI (uvicorn, workers) | `app = mcp.http_app()` | You own TLS, scaling, middleware |
| Embed in existing web app | Mount `mcp.http_app()` in FastAPI/Starlette | Combine lifespans; keep `/mcp` path |
| Tests, deterministic apps | `Client(server_object)` in-memory | No network or subprocess |

## 4. Canonical API contract

```python
from typing import Annotated
from fastmcp import FastMCP, Client, Context

mcp = FastMCP("Demo", instructions="Use greet to say hello.", version="1.0.0")

@mcp.tool(annotations={"readOnlyHint": True})
async def greet(name: str, ctx: Context) -> str:
    """Greet a user by name."""
    await ctx.info(f"Greeting {name}")
    return f"Hello, {name}!"

@mcp.resource("data://config", mime_type="application/json")
def get_config() -> str:
    """Application configuration as JSON."""
    return '{"theme": "dark"}'

@mcp.resource("users://{user_id}/profile")
async def get_profile(user_id: str) -> str:
    """Profile JSON for one user."""
    return '{"id": "%s"}' % user_id

@mcp.prompt
def review_code(code: str) -> str:
    """Ask for a code review."""
    return f"Please review:\n```\n{code}\n```"
```

Key shapes: tool args are typed params (no `*args`/`**kwargs`); resources
return `str | bytes | ResourceResult`; prompts return
`str | list[Message] | PromptResult`; `ctx` / `Depends()` params are hidden
from the LLM schema.

## 5. Topic routing

| Request | Read |
|---|---|
| Tools, resources/templates, prompts, Context, DI, middleware, lifespans, composition, visibility, versioning, error masking | `references/servers.md` |
| Client connect/call/list, transports, config-based multi-server, callbacks (sampling/elicitation/progress/logging/roots), client auth | `references/clients.md` |
| Interactive UIs: `app=True` Prefab, FastMCPApp callbacks, generative UI, custom HTML, approval/choice/form/file-upload providers | `references/apps.md` |
| Auth choice (JWTVerifier/RemoteAuthProvider/OAuthProxy/OIDC/MultiAuth), HTTP/ASGI deploy, FastAPI mount, `fastmcp.json`, CLI, Horizon, integrations | `references/auth-deployment.md` |
| In-memory/HTTP testing, fixtures, mocking, snapshots, markers | `references/testing.md` |
| Exact URL or version badge for a moving API | `references/source-ledger.md` |

## 6. Reliability and safety rules

- Write clear docstrings; they become the LLM-visible description. Use
  `Annotated[str, "..."]` or `Field(description=...)` for parameter help;
  explicit annotation wins over docstring.
- Never use `*args`/`**kwargs` on tools or prompts (templates may use
  `**kwargs` only because the URI defines names). Validate with Pydantic
  types; keep `strict_input_validation=False` (default) unless you need
  exact JSON-Schema rejection.
- Prefer `async def` for I/O; sync tools run in a threadpool. Use
  `run_in_thread=False` only for thread-affine libs (COM, tkinter, some
  GPU drivers) and never combine it with `timeout` on sync functions.
- Return `dict`/Pydantic/dataclass for `structuredContent`; primitives
  need a return annotation to get `{"result": ...}`. Use `ToolResult`
  only when you need explicit content + structured + meta control.
- Raise `ToolError`/`ResourceError`/`PromptError` for client-visible
  messages; set `mask_error_details=True` on the server to hide other
  exception text. Treat resource template values as untrusted; resolve
  filesystem paths against an allowed root.
- Control exposure with `mcp.disable(keys={...})` / `mcp.disable(tags=...)`
  or allowlist `mcp.enable(tags={...}, only=True)` — not the deprecated
  `enabled=` decorator arg. Mark safe tools `readOnlyHint=True`.
- Keep secrets in env vars, never in code or committed YAML. Auth only
  matters on HTTP; do not invent OAuth flows — pick from the decision
  table in `references/auth-deployment.md`.
- Pin `fastmcp==x.y.z` and `prefab-ui==x.y.z` (apps) in production.

## 7. Fast troubleshooting

| Symptom | First checks |
|---|---|
| `import fastmcp` fails after pip upgrade 3.2→3.3+ | `pip uninstall -y fastmcp fastmcp-slim && pip install fastmcp` |
| Tool schema missing params / shows `self` | Method registered via `@mcp.tool` instead of `@tool` + `mcp.add_tool(bound_method)` |
| `*args` tool rejected | Remove var-args; declare every param explicitly |
| Strict clients reject `{"a": "10"}` for `int` | Expected with `strict_input_validation=True`; relax or fix client payload |
| Resource returns dict, client sees string | Serialize with `json.dumps` or return `ResourceResult` |
| `ctx` appears in LLM schema | Use `ctx: Context` hint or `= CurrentContext()` — both are hidden; check for shadowing defaults |
| `get_context()` raises `RuntimeError` | Called outside a request; pass `ctx` explicitly or guard |
| HTTP 404 on `/mcp` | Path is `/mcp` by default; check custom `path=` and mount prefix |
| Auth works locally, fails remote | Auth is HTTP-only; verify `jwks_uri`/`issuer`/`audience`, `base_url`, env secrets, DCR support |
| Mounted tools slow | `list_tools` fans out to children; HTTP mounts cost 300–400 ms; limit depth, cache |

Read `references/testing.md` before changing timeouts, visibility, or auth
to fix a failing test; use in-memory `Client(server)` to reproduce first.

## Official documentation

Based on FastMCP v3 (`https://gofastmcp.com/v3/...`) with v4 deltas noted
in `source-ledger.md`, plus the community `jxnxts/fastmcp-skill` reference
structure (tools, resources-prompts, context-di-middleware,
composition-providers, testing, deployment). Prefer these roots and do not
invent APIs:

- <https://gofastmcp.com/v3/getting-started/welcome>
- <https://gofastmcp.com/v3/getting-started/installation>
- <https://gofastmcp.com/v3/getting-started/quickstart>
- <https://gofastmcp.com/llms.txt>
