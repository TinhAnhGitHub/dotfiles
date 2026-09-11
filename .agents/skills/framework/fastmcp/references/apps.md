# FastMCP Apps — Interactive UIs in the Conversation

Source: `https://gofastmcp.com/v3/apps/*`. Requires `pip install "fastmcp[apps]"`.
Pin `prefab-ui==x.y.z` in production (Prefab has frequent breaking changes).

## 1. Pick your path

| Need | Pattern | Entry |
|---|---|---|
| Chart/table/dashboard, client-side toggles/tabs/filter | Interactive Tools (`app=True` + Prefab) | `apps/prefab` |
| Form saves, button triggers backend, DB search | `FastMCPApp` (UI↔tool wiring, stable IDs across composition) | `apps/fastmcp-app` |
| LLM writes custom UI per request | Generative UI provider | `apps/generative` |
| Map/3D/video, own framework | Custom HTML via MCP Apps extension | `apps/low-level` |

## 2. Interactive Tools (start here)

```python
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, Text, Badge, Row
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool(app=True)
def greet(name: str) -> PrefabApp:
    """Greet someone with a visual card."""
    with Column(gap=4, css_class="p-6") as view:
        Heading(f"Hello, {name}!")
        with Row(gap=2, align="center"):
            Text("Status")
            Badge("Greeted", variant="success")
    return PrefabApp(view=view)
```

- Tool still receives args and returns a result; the host renders the
  component tree instead of text. Preview locally without a host:
  `fastmcp dev apps my_server.py`.

## 3. FastMCPApp (server callbacks)

Use when the UI must call back (save, trigger work, live search).
`FastMCPApp` wires UI actions to backend tools with managed visibility
and composition-safe IDs. See `apps/fastmcp-app` for the wiring pattern.

## 4. Generative UI

```python
mcp.add_provider(GenerativeUI())
```

One provider lets the model author Prefab code for the current data and
request; the user watches it build. See `apps/generative`.

## 5. Ready-made providers (one line each)

- Approval: human-in-the-loop gates (`apps/providers/approval`)
- Choice: clickable options (`apps/providers/choice`)
- File upload: drag-and-drop (`apps/providers/file-upload`)
- Form input: Pydantic-model forms (`apps/providers/form`)

## 6. Develop and learn

- `apps/quickstart` — working app in a minute.
- `apps/examples` — runnable sample servers.
- `apps/development` — local preview and testing.
- `apps/architecture` — Python→pixels pipeline.
