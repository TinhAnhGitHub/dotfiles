# Chapter 20 — Concurrent Executors

## P20.1 — Let the executor own worker lifecycle

Prefer:

```python
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(fetch, urls))
```

The context manager shuts down workers even when the body raises. Do not inspect private fields
such as `_max_workers` in application logic.

## P20.2 — Choose ordered or completion-order consumption deliberately

- `executor.map()` returns results in input order. A slow first item can delay later results.
- `submit()` plus `as_completed()` processes whichever future finishes first and lets each future
  carry metadata for diagnostics.

Use `map` when positional alignment matters. Use `as_completed` for progress reporting, partial
success, or per-item error handling. Always call `future.result()` so worker exceptions are observed.

## P20.3 — Keep worker functions portable

Process-pool functions should be top-level and picklable. Keep side effects, client creation,
timeouts, and error classification explicit. Bound network concurrency and reuse one HTTP client
per batch rather than creating a client inside every task.

## P20.4 — Do not lose async executor work

If `run_in_executor()` or `to_thread()` returns a future whose completion matters, await it. A
fire-and-forget file write can lose exceptions and let the caller report success too early.

## Agentic repository evidence

- **Agent-S:** accessibility-tree construction uses `ThreadPoolExecutor` and `as_completed`.
- **DeerFlow:** a shared thread executor adapts async tools for synchronous LangChain calls.
- **SCALE-CUA:** environment work is submitted to a `ThreadPoolExecutor` and awaited with
  `future.result()`.
- **Open-AgentRL:** reward computation combines process pools, `run_in_executor`, timeouts, and
  async gathering.
- **MAI-UI:** evaluation cases are submitted to a thread pool and consumed with `as_completed`.
- **LangGraph:** JSON encoding/decoding is offloaded with `run_in_executor` while transport
  futures remain tracked by the async client.
- **LlamaIndex Workflows:** synchronous steps run in the event loop’s executor; migrations use a
  one-worker `ThreadPoolExecutor` when already inside an event loop.
- **AG2/AutoGen:** async LLM replies use `run_in_executor` and `functools.partial`.

Verified local repository paths are under `/home/tinhanhnguyen/Desktop/project/reference/`.

## Local examples worth comparing

The `getflags` progression compares sequential download, `ThreadPoolExecutor.map`, explicit
futures, and async executor bridges. `proc_pool.py` compares a CPU-bound process pool. These are
teaching examples: network variants need a local test server and should not stress shared servers.

## Review checklist

- Is executor shutdown guaranteed?
- Does result ordering match the caller’s contract?
- Are all future exceptions observed?
- Are process-pool callables top-level and picklable?
- Is async offloaded work awaited before success is reported?
- Are network concurrency, timeouts, and client reuse explicit?
