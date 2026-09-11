# FastMCP Testing — In-Memory First

Source: `v3/servers/testing`, `clients/*`. Requires `pytest-asyncio`
(`asyncio_mode = "auto"` in `pyproject.toml`).

## 1. In-memory (primary; no network)

```python
from fastmcp import FastMCP, Client

async def test_greet():
    server = FastMCP("Test")

    @server.tool
    def greet(name: str) -> str:
        return f"Hello, {name}!"

    async with Client(server) as client:
        result = await client.call_tool("greet", {"name": "Alice"})
        assert result.data == "Hello, Alice!"
```

Resources/prompts use `read_resource(uri)` / `get_prompt(name, args)`.
Errors: `pytest.raises(...)` around `call_tool` for `ToolError` paths.

## 2. Fixtures (return servers, not open clients)

```python
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def weather_server():
    server = FastMCP("Weather")

    @server.tool
    def get_temperature(city: str) -> dict:
        return {"city": city, "temp": {"LA": 85}.get(city, 70)}

    return server

async def test_temperature(weather_server):
    async with Client(weather_server) as client:
        result = await client.call_tool("get_temperature", {"city": "LA"})
        assert result.data == {"city": "LA", "temp": 85}
```

Mock externals with `AsyncMock`; keep one behavior per test with
self-contained servers. Schema snapshots via `inline-snapshot`
(`pytest --inline-snapshot=create|fix`); dynamic values via `dirty-equals`.

## 3. HTTP transport (when you must)

```python
from fastmcp.utilities.tests import run_server_async
from fastmcp.client.transports import StreamableHttpTransport

async def test_http():
    server = FastMCP("Test")

    @server.tool
    def greet(name: str) -> str: return f"Hello, {name}!"

    async with run_server_async(server) as url:
        async with Client(transport=StreamableHttpTransport(url)) as client:
            assert await client.ping() is True
            r = await client.call_tool("greet", {"name": "World"})
            assert r.data == "Hello, World!"
```

Subprocess isolation only for stdio/process behavior:
`run_server_in_process(...)`. Mark slow suites
`@pytest.mark.integration` / `@pytest.mark.client_process` and skip with
`pytest -m "not integration and not client_process"`.
