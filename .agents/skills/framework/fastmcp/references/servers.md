# FastMCP Servers — Tools, Resources, Prompts, Context, Composition

Source: `https://gofastmcp.com/v3/servers/*` (see `source-ledger.md`).
All snippets are v3 unless marked.

## 1. Tools (`@mcp.tool`)

```python
from typing import Annotated
from pydantic import Field
from mcp.types import ToolAnnotations

@mcp.tool(
    name="find_products",  # default: function name
    description="Search the product catalog.",  # default: docstring
    tags={"catalog", "search"},
    meta={"version": "1.2"},
    timeout=30.0,  # seconds; MCP error -32000 on expiry; not for task=True
    version="2",
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
)
async def search_products(
    query: str,
    max_results: Annotated[int, "Maximum results"] = 10,
    category: str | None = None,
) -> list[dict]:
    """Search the product catalog with optional filtering."""
    ...
```

- Docstring summary → tool description; Google/NumPy/Sphinx `Args:` →
  parameter descriptions. Explicit `Annotated[..., "..."]` or
  `Field(description=...)` wins over docstring.
- Types: `int/float/str/bool`, `bytes` (raw, not base64-decoded), dates
  (ISO), `list/dict/set`, `X | None`, unions, `Literal`/`Enum` (client
  sends values), `Path`/`UUID` (auto-converted), Pydantic models (must be
  JSON objects, not strings). No `*args`/`**kwargs`.
- `Field` adds `ge/gt/le/lt`, `min_length/max_length`, `pattern`.
- `async def` preferred for I/O; sync runs in threadpool. Thread-affine
  libs (COM, tkinter): `@mcp.tool(run_in_thread=False)`; do not combine
  with `timeout` on sync functions.
- Returns: `str`→`TextContent`, `bytes`→blob, `Image/Audio/File`
  (`fastmcp.utilities.types`, `path=` or `data=`+`format=`)→media blocks,
  MCP blocks as-is, list→many blocks, `None`→empty. `dict`/Pydantic/
  dataclass→text + `structuredContent`; primitives need a return
  annotation to get `{"result": value}`. Full control:
  `ToolResult(content=..., structured_content={...}, meta={...})`.
- Errors: raise `ToolError("...")` for client-visible text; otherwise
  exceptions are logged + converted. `FastMCP(mask_error_details=True)`
  hides non-`ToolError` details.
- Hints: `readOnlyHint=True` skips confirmation in ChatGPT/Claude for
  safe reads; set `destructiveHint`/`idempotentHint` honestly.
- Registry: `FastMCP(on_duplicate_tools="warn"|"error"|"replace"|"ignore")`;
  visibility via `mcp.disable(keys={"tool:name"})`,
  `mcp.disable(tags={...})`, `mcp.enable(tags={...}, only=True)`;
  dynamic removal `mcp.local_provider.remove_tool("name")`.
- Methods: use standalone `@tool` then `mcp.add_tool(obj.method)` so
  `self` is excluded.

## 2. Resources (`@mcp.resource`)

```python
import json

@mcp.resource("data://config", mime_type="application/json")
def get_config() -> str:
    """Application configuration as JSON."""
    return json.dumps({"theme": "dark"})

@mcp.resource("weather://{city}/current")
def get_weather(city: str) -> str:
    return json.dumps({"city": city, "temp": 22})

@mcp.resource("files://{path*}{?encoding,lines}")
def read_file(path: str, encoding: str = "utf-8", lines: int = 100) -> str:
    ...
```

- Return `str | bytes | ResourceResult`. Serialize dicts with
  `json.dumps`. `ResourceResult(contents=[ResourceContent(...)], meta=...)`
  for multi-part/MIME control.
- URI kinds: static (`data://config`), template `{param}` (one segment),
  wildcard `{param*}` (many segments), query `{?opt1,opt2}` (must be
  optional params). Rules: required params must be in path; query params
  must have defaults; every URI param must exist as a function param.
  Omit an optional param from the URI to keep it server-side only.
- One function, many URIs: `mcp.resource("users://email/{email}")(fn)`.
- Classes for static content: `FileResource`, `TextResource`,
  `BinaryResource`, `HttpResource`, `DirectoryResource` + `mcp.add_resource(...)`.
- Filesystem safety: template values are decoded untrusted input.
  Resolve against an allowed root and check
  `path.is_relative_to(root)`; raise `ResourceError` on escape.
- Errors: `ResourceError` is always client-visible;
  `mask_error_details=True` hides the rest.

## 3. Prompts (`@mcp.prompt`)

```python
from fastmcp.prompts import Message, PromptResult

@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Explain a topic."""
    return f"Can you please explain '{topic}'?"

@mcp.prompt
def review(code: str) -> list[Message]:
    return [Message(f"Review:\n```\n{code}\n```"), Message("On it.", role="assistant")]

@mcp.prompt
def audit(code: str) -> PromptResult:
    return PromptResult(messages=[Message(f"Audit {code}")], meta={"priority": "high"})
```

- No `*args`/`**kwargs`. Required = no default; optional = default.
- MCP only sends strings: FastMCP auto-converts `list[int]` etc. from
  JSON strings and documents the schema in the arg description. Keep
  prompt arg types simple.
- `Message(content, role="user"|"assistant")`; other types JSON-serialized.

## 4. Context (request-scoped)

Preferred injection is explicit DI; legacy bare `ctx: Context` still works.

```python
from fastmcp import Context
from fastmcp.dependencies import CurrentContext
from fastmcp.server.dependencies import get_context

@mcp.tool
async def a(query: str, ctx: Context = CurrentContext()) -> str:
    await ctx.info(f"Processing {query}")
    await ctx.report_progress(progress=50, total=100)
    parts = await ctx.read_resource("data://config")
    summary = await ctx.sample(f"Summarize: {query[:200]}")
    r = await ctx.elicit("Your name?", response_type=str)
    await ctx.set_state("counter", (await ctx.get_state("counter") or 0) + 1)
    return summary.text
```

- Logging: `debug/info/warning/error`. Progress:
  `report_progress(progress, total)`. Resources:
  `list_resources()` / `read_resource(uri)`. Prompts:
  `list_prompts()` / `get_prompt(name, args)`. Sampling: `sample(...)`.
  Elicitation: `elicit(...)` with `accept/cancel` result.
- State: `get_state/set_state/delete_state`; JSON-serializable persists
  ~1 day, `serializable=False` lives for one request only. Custom store:
  `FastMCP(session_state_store=RedisStore(...))`. Mounted servers do not
  share state unless given the same store.
- Info: `request_id`, `client_id`, `session_id`, `transport`
  (`stdio|sse|streamable-http|None`), `fastmcp` server,
  `request_context` (may be `None` pre-handshake).
- Deep calls: `get_context()` inside helpers (request-only).
- Per-session visibility: `ctx.enable_components/disable_components/reset_visibility()`.

## 5. Dependency injection

```python
from fastmcp.dependencies import (
    Depends, CurrentContext, CurrentFastMCP, CurrentRequest,
    CurrentHeaders, CurrentAccessToken,
)
from fastmcp.server.dependencies import TokenClaim, get_http_request

def get_db(): return Database(os.environ["DB_URL"])

@mcp.tool
async def query(sql: str, db=Depends(get_db), user: str = TokenClaim("sub")) -> list:
    return await db.execute(sql, user)
```

- Built-ins: `CurrentContext()`, `CurrentFastMCP()`, `CurrentRequest()`
  (Starlette, HTTP-only), `CurrentHeaders()` (empty dict off-HTTP),
  `CurrentAccessToken()` (raises) / `get_access_token()` (None),
  `TokenClaim("oid"|"sub"|...)`. DI params are hidden from the schema.
- Custom: `Depends(fn)` with sync/async/context-manager callables; cached
  per-request; supports nesting. Use `@asynccontextmanager` for cleanup.
- Tasks (`fastmcp[tasks]`): `CurrentDocket()`, `CurrentWorker()`,
  `Progress()` inside `@mcp.tool(task=True)` only.

## 6. Middleware, lifespans, composition

```python
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.lifespan import lifespan

class LoggingMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        print(f"Calling {context.message.name}")
        return await call_next(context)

mcp.add_middleware(LoggingMiddleware())  # on_message -> on_request -> on_call_tool/on_read_resource/on_get_prompt

@lifespan
async def app_lifespan(server):
    db = await connect_db()
    try: yield {"db": db}
    finally: await db.close()

mcp = FastMCP("App", lifespan=a | b)  # composable with |
# inside tools: ctx.lifespan_context["db"]
```

```python
from fastmcp.server import create_proxy

main = FastMCP("Main")
main.mount(weather, namespace="weather")  # weather_get_forecast, data://weather/...
main.mount(create_proxy("http://api.example.com/mcp"), namespace="api")
main.mount(create_proxy("./other.py"), namespace="local")
```

- Mounts are live-linked; later child tools appear immediately.
  Same-name conflicts: last mount wins. Parent tag filters recurse.
- Custom routes (`@mcp.custom_route("/health", methods=["GET"])`) forward
  through mounts.
- Transforms: namespace, visibility, tool-search, code-mode,
  resources/prompts-as-tools, version-filter. Providers: local
  (decorators), filesystem (auto-discovery), proxy (remote), skills.
