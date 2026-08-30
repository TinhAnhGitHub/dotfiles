# Async and concurrency boundaries

## Use when

Choose asyncio for cooperative I/O, threads for blocking I/O that releases the GIL, processes for
CPU-heavy independent work, and executors when a caller needs explicit future ownership.

## Why

The execution model should match the bottleneck and lifecycle. Explicit task ownership prevents
lost exceptions, leaks, and accidental unbounded concurrency.

## Rules

- Bound queues and concurrency.
- Await every task or future whose result matters.
- Preserve cancellation and clean up in `finally` blocks.
- Keep blocking functions out of the event loop.
- Make ordering and completion-order behavior explicit.

## Tests

Test cancellation, timeouts, queue backpressure, worker shutdown, exception propagation, and no
event-loop blocking. For durable workflows and state machines, consult the design-pattern skill.

## Framework examples

### OpenAI Python SDK — explicit async client ownership

```python
async def fetch_all(prompts: list[str]) -> list[object]:
    async with AsyncOpenAI() as client:
        return await asyncio.gather(
            *(client.responses.create(model="provider:model", input=prompt)
              for prompt in prompts)
        )
```

The async client keeps I/O off the event loop’s blocking path, while `gather` makes task ownership
and completion explicit. See the [official OpenAI Python SDK](https://github.com/openai/openai-python).

### vLLM — queue work, then await completion

```python
async def run_request(engine, request):
    future = engine.enqueue(request)
    return await future
```

`enqueue()` separates submission from result collection, which supports batching and bounded worker
lifecycles instead of blocking the caller. See the vLLM [architecture overview](https://docs.vllm.ai/en/stable/design/arch_overview/).

### Google ADK — parallel workflow agents

```python
workflow = ParallelAgent(
    name="research",
    sub_agents=[news_agent, filings_agent],
)
```

`ParallelAgent` expresses independent work as a framework-owned concurrency boundary; the caller
does not need to manage each child task directly. See [Google ADK workflow agents](https://adk.dev/agents/workflow-agents/).

### OpenRLHF — separate rollout execution from PPO roles

```python
class ToolRollout(MultiTurnAgentExecutor):
    async def run_turn(self, state):
        return await self.step_with_tools(state)
```

The executor abstraction keeps multi-turn, potentially remote agent work separate from the PPO
driver and its Ray actor placement. See OpenRLHF [agent training](https://openrlhf.readthedocs.io/en/latest/agent_training.html).

### slime — hook asynchronous rollout customization

```python
async def custom_generate(requests, model):
    return await model.generate(requests)
```

An injected generation hook lets rollout I/O evolve independently of the training loop; the async
boundary makes waiting and cancellation testable. See [slime customization](https://thudm.github.io/slime/get_started/customization.html).

## When not to use

Do not use asyncio for CPU-bound work or blocking I/O without an explicit offload boundary. Avoid
unbounded task creation when a bounded queue or worker pool expresses the workload more clearly.

## Trade-offs

Async code can overlap I/O efficiently, but cancellation, task ownership, and shutdown become part
of the contract. Threads, processes, or a synchronous call may be simpler when concurrency is small.

## ArjanCodes 2026 examples (adapted)

### Keep async features at an async boundary

An optional feature should not accidentally turn a coroutine into a blocking function. Select the
behavior before scheduling work and keep each feature callable asynchronous.

```python
from collections.abc import Awaitable, Callable


AsyncFeature = Callable[[str], Awaitable[str]]


async def run_feature(feature: AsyncFeature, value: str) -> str:
    return await feature(value)


async def normalize(value: str) -> str:
    return value.strip().lower()
```

The [2026 `features` examples](https://github.com/ArjanCodes/examples/tree/main/2026/features) are
a useful reminder to model variation explicitly. The [2026 `props/with_async.py`](https://github.com/ArjanCodes/examples/blob/main/2026/props/with_async.py)
supports the boundary rule: a property should not hide an awaitable operation or create a task as a
side effect.

### Make concurrent ownership testable

```python
import asyncio


async def gather_bounded(
    values: list[str],
    feature: AsyncFeature,
    limit: int,
) -> list[str]:
    semaphore = asyncio.Semaphore(limit)

    async def run(value: str) -> str:
        async with semaphore:
            return await feature(value)

    return await asyncio.gather(*(run(value) for value in values))
```

Test the maximum active count, cancellation while waiting on the semaphore, and propagation of a
feature exception. The point is not to make every function concurrent; it is to keep the chosen
feature and its lifecycle visible.
