# Chapter 19 — Concurrency Models in Python

## The decision

- **Threads:** overlap blocking I/O and share memory; protect shared mutable state.
- **Processes:** achieve CPU parallelism for picklable top-level functions; pay serialization
  and process-start costs.
- **`asyncio`:** cooperative concurrency on one event loop; every task must reach an `await`.

Concurrency overlaps progress; parallelism executes simultaneously. Pick the model from the
workload and the boundary, not from syntax preference.

## P19.1 — Make coordination explicit

Use `threading.Event` for cooperative stop signals and queues/sentinels for worker messages. Never
use `Queue.empty()` as proof that all workers are finished: the queue can be empty while workers
are still computing. Use `join()`, explicit completion sentinels, or an executor abstraction.

Keep worker output as data and report it from one coordinating layer when deterministic logs matter.

## P19.2 — Async syntax does not make blocking code asynchronous

This is still blocking:

```python
async def wrong():
    time.sleep(1)
```

Use an async library, `await asyncio.sleep(...)`, or deliberately offload the blocking function
with `asyncio.to_thread(...)`. A CPU-heavy pure-Python loop still needs a process or native code;
`await asyncio.sleep(0)` only yields control and does not create parallelism.

## P19.3 — Preserve lifecycle and cancellation

Background tasks need an owner. Store task handles, cancel them in `finally`, and await their
completion while suppressing only the expected cancellation exception. Do not let a helper create
fire-and-forget tasks without documenting who shuts them down.

## Agentic repository evidence

- **Agent-S:** BBoN fact generation uses semaphore-bounded tasks, `asyncio.to_thread`, and
  `asyncio.gather`; the OSWorld runner creates and restarts environment processes.
- **ClawGUI Nanobot:** per-session `asyncio.Lock`, tracked tasks, shutdown gathering, and
  `asyncio.to_thread` for synchronous GUI/network tools.
- **LlamaIndex Workflows:** runtime control loops manage tasks, queues, locks, and cancellation.
- **AG2/AutoGen:** dependent chats use futures/tasks and async dependency solving.
- **TuriX-CUA:** the CLI owns an asyncio task and adapts synchronous registered actions with
  `asyncio.to_thread`.
- **DeepSeek Harness:** subprocess communication is serviced by reader/stderr threads and queues.
- **TongUI-agent:** `MiniWoBInstance` is a thread-backed Selenium environment.

Local evidence is under `/home/tinhanhnguyen/Desktop/project/reference/`; see the source paths
listed in the repository research notes for exact symbols.

## Local examples worth comparing

The three spinner implementations are the simplest comparison:

- `spinner_thread.py` — thread plus `Event`.
- `spinner_proc.py` — process plus cross-process `Event`.
- `spinner_async.py` — cooperative task cancellation.

The prime examples compare sequential work, raw threads, processes, and the broken async CPU
variant. The broken async version is valuable because it shows that an `async def` wrapper around
a blocking function does not make the work nonblocking.

## Review checklist

- Is the workload I/O-bound, CPU-bound, or cooperative?
- What owns each thread/process/task?
- Is completion signaled explicitly?
- Can cancellation happen at every awaitable boundary?
- Is shared state protected or replaced with message passing?
- Is the benchmark conclusion tied to the interpreter, hardware, and worker count?
