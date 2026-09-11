# FastMCP Clients — Connect, Call, Observe

Source: `https://gofastmcp.com/v3/clients/*` (see `source-ledger.md`).

## 1. Creating a client (transport is inferred)

```python
import asyncio
from fastmcp import Client, FastMCP

server = FastMCP("TestServer")
in_memory = Client(server)                    # tests / same process
http = Client("https://example.com/mcp")      # production HTTP
script = Client("my_server.py")               # stdio subprocess
script_env = Client("my_server.py", env={"API_KEY": "secret"})

async def main():
    async with http:  # connect + handshake
        await http.ping()
        print(await http.list_tools())
        print(await http.list_resources())
        print(await http.list_prompts())

asyncio.run(main())
```

- Every operation needs `async with client:`. Handshake exposes
  `client.initialize_result` (name, instructions, capabilities).
- `Client(..., auto_initialize=False)` + `await client.initialize(timeout=10)`
  for manual control.
- Transports: in-memory (no network, shares env), stdio (isolated
  subprocess, pass `env=` explicitly), Streamable HTTP (many clients).
  Details: `clients/transports`.
- Config-based multi-server (Claude-Desktop style):
  `Client({"mcpServers": {"weather": {"url": "..."}, "asst": {"command": "python", "args": [...]}}})`.
  Tools become `weather_get_forecast`; resource URIs gain prefixes.

## 2. Calling tools / reading resources / getting prompts

```python
async with client:
    tools = await client.list_tools()
    result = await client.call_tool("multiply", {"a": 5, "b": 3})
    print(result.data)          # structured value
    print(result.content)       # raw MCP blocks

    content = await client.read_resource("file:///config/settings.json")
    print(content[0].text)

    prompt = await client.get_prompt("analyze_data", {"data": "[1,2,3]"})
    print(prompt.messages)
```

- `call_tool(name, args_dict)` → `result.data` (structured) +
  `result.content` (display). Version selection and error mapping are in
  `clients/tools`.
- Templates/binary: see `clients/resources`; argument serialization:
  `clients/prompts`.

## 3. Callbacks (server-initiated requests)

```python
from fastmcp.client.logging import LogMessage

async def log_handler(msg: LogMessage): print(f"log: {msg.data}")
async def progress_handler(progress, total, message): print(f"{progress}/{total} {message}")
async def sampling_handler(messages, params, context): return "Generated response"

client = Client(
    "my_server.py",
    log_handler=log_handler,
    progress_handler=progress_handler,
    sampling_handler=sampling_handler,
    timeout=30.0,
)
```

- Handlers: sampling (`clients/sampling`), elicitation
  (`clients/elicitation`), progress (`clients/progress`), logging
  (`clients/logging`), roots (`clients/roots` — local paths the server
  may reach), notifications (`clients/notifications` — refresh lists on
  `tools/list_changed` etc.).

## 4. Client auth

- Bearer: `Client(url, auth="<token>")` or header-based bearer config
  (`clients/auth/bearer`).
- OAuth 2.1: browser-based flow with token cache
  (`clients/auth/oauth`); machine-to-machine client-credentials
  (`clients/auth/client-credentials`); CIMD domain identity
  (`clients/auth/cimd`).
- `fastmcp-remote` bridges remote HTTP servers into stdio-only hosts:
  `uvx fastmcp-remote https://.../mcp`.
- Client-only installs avoid the server framework:
  `clients/client-only-package`.
