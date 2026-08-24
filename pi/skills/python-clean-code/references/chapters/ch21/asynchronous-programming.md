# Chapter 21 — Asynchronous Programming

## P21.1 — A coroutine object is not concurrent by itself

`async def` creates a coroutine function. Calling it creates a coroutine object; it runs only when
awaited or scheduled. Use `asyncio.run()` at the top-level and `asyncio.create_task()` when a
background operation must overlap another operation.

## P21.2 — Keep blocking work out of the event loop

Use async libraries for network I/O. For unavoidable synchronous I/O, use `await asyncio.to_thread`
or an executor. For CPU-heavy pure Python, use a process or native extension. Do not use
`await asyncio.sleep(0)` as a fake parallelism mechanism; it only yields cooperatively.

## P21.3 — Bound concurrency and preserve cancellation

Use a semaphore or a structured task group for large input sets. Keep task handles, cancel them in
`finally`, await their completion, and do not swallow `CancelledError` broadly. Async generators
should close clients/resources in `finally` or `async with`.

## P21.4 — Async iterators and stream flow control

An async generator combines `async def`, `yield`, and `async for`:

```python
async def stream(reader):
    while chunk := await reader.read(4096):
        yield chunk
```

For TCP streams, `writer.write()` queues bytes and `await writer.drain()` provides flow-control
synchronization. Close with `writer.close()` and `await writer.wait_closed()`.

## Agentic repository evidence

- **LangGraph:** `AsyncThreadStream` creates watcher tasks/futures and cancels/gathers them in
  `close`; async clients expose lifecycle-aware streams.
- **LlamaIndex Workflows:** runtime contexts coordinate async steps, queues, locks, task sets, and
  cancellation.
- **AG2/AutoGen:** dependent chats are represented with futures/tasks and prerequisite ordering.
- **ClawGUI Nanobot:** inbound messages become tracked tasks serialized by per-session locks.
- **DeerFlow:** synchronous tools are bridged safely into async request paths.
- **Agent-S:** BBoN uses bounded concurrency and `asyncio.to_thread`.
- **TuriX-CUA:** agent execution, cancellation, and stop listeners are coordinated with asyncio.
- **CogAgent:** FastAPI lifespan manages async server startup/shutdown, but does not make the
  model computation itself asynchronous.

## Local examples worth comparing

The domain probe examples demonstrate completion-order results from `asyncio.as_completed`. The
Mojifinder examples demonstrate async TCP streams, `StreamWriter.drain`, and an ASGI service. The
Curio subtree is a useful comparison, not an asyncio dependency.

## Review checklist

- Is every coroutine awaited or intentionally scheduled and owned?
- Can one blocking call stall the whole event loop?
- Is task creation bounded for untrusted/large input?
- Does cancellation reach all child tasks and resources?
- Are async generators and network writers closed?
- Is completion order documented when using `as_completed`?
