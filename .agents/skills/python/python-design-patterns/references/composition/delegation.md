# Delegation

## Intent

Let one object fulfill a responsibility by forwarding part of the work to another object with a
smaller, explicit contract.

## Use when

Use delegation when the outer object owns policy or lifecycle but a collaborator owns execution,
storage, transport, or a specialized algorithm.

## Why

Delegation keeps responsibilities local and enables replacement with a fake or alternate backend
without inheritance.

```python
class ReportService:
    def __init__(self, renderer) -> None:
        self.renderer = renderer

    def render(self, data: dict[str, object]) -> str:
        return self.renderer.render(data)
```

This solves a report service becoming coupled to one rendering implementation.

## When not to use

Do not add a forwarding class that owns no policy, state, or contract. Pass the collaborator
directly when no boundary is needed.

## Trade-offs and tests

Forwarding can obscure where errors and resources belong. Test the delegated contract and verify
that cancellation, tracing, and cleanup cross the boundary as intended.

## Framework examples

### PydanticAI — `RunContext` dependencies (adapted)

```python
from pydantic_ai import Agent, RunContext

agent = Agent("model", deps_type=SearchService)

@agent.tool
async def search(ctx: RunContext[SearchService], query: str) -> list[str]:
    return await ctx.deps.search(query)
```

This solves an agent needing search, storage, or another external service without owning its
transport details. It fits Delegation because the tool keeps agent-facing policy while forwarding
execution to the injected `SearchService`, which tests can replace. See the official [PydanticAI
dependencies documentation](https://pydantic.dev/docs/ai/core-concepts/dependencies/).

### OpenRLHF — `AgentExecutorBase` (adapted)

```python
class BrowserExecutor(AgentExecutorBase):
    async def execute(self, tool_call):
        return await browser.run(tool_call)

executor = BrowserExecutor()
```

This solves adapting a multi-turn training agent to a concrete browser or tool runtime. It fits
Delegation because the executor owns the framework boundary while the browser collaborator owns
the specialized operation. See the official [OpenRLHF agent training
documentation](https://openrlhf.readthedocs.io/en/latest/agent_training.html).
