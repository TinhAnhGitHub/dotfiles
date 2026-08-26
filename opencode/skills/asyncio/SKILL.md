---
name: asyncio
description: >-
  Best practices for Python asyncio: coroutines, Tasks, TaskGroups, cancellation,
  timeouts, asyncio.gather/wait/as_completed, running blocking code in threads,
  asyncio.Queue (FIFO/Priority/LIFO, shutdown), and synchronization primitives
  (Lock, Event, Condition, Semaphore, BoundedSemaphore, Barrier). Use this skill
  whenever the user writes or reviews async def / await code, mentions asyncio,
  create_task, gather, TaskGroup, CancelledError, TimeoutError in async code,
  event loops, concurrent I/O in Python, worker queues with asyncio, rate
  limiting concurrent requests, or asks "how do I run these functions
  concurrently" — even if they don't say "asyncio" explicitly.
---

# Python asyncio: Coroutines, Tasks, Queues, and Synchronization

Guidance distilled from the official Python docs (asyncio-task, asyncio-queue,
asyncio-sync). Follow the mental model first; the API details are in the
reference files.

## The mental model

asyncio is **cooperative single-threaded concurrency**. One event loop runs one
task at a time; tasks only yield control at `await` points. This has two big
consequences that drive most best practices:

1. **A blocking call anywhere freezes ALL tasks.** Never use `time.sleep()`,
   blocking file/DB/network calls, or CPU-heavy loops inside a coroutine.
   Offload them (`asyncio.to_thread`) or replace them with async equivalents.
2. **No data races on plain variables** (no preemption between awaits), but you
   still need locks/events/queues to coordinate *ordering* across await points.

## Core concepts

### Awaitables

Three kinds of objects can be awaited:

| Kind | What it is | Created by |
|---|---|---|
| Coroutine | object returned by calling an `async def` function | calling the function |
| Task | a coroutine scheduled to run concurrently on the loop | `create_task()`, `TaskGroup` |
| Future | low-level "eventual result"; bridging callback-based code | rarely created directly |

Key trap: **calling a coroutine does nothing.** `nested()` merely creates a
coroutine object; it never runs until awaited or wrapped in a task. An un-awaited
coroutine triggers `RuntimeWarning: coroutine was never awaited`.

```python
async def nested():
    return 42

nested()          # BUG: nothing runs, RuntimeWarning
await nested()    # runs sequentially, returns 42
```

### Running things: choose the right tool

- **Sequential** — just `await coro()` when order matters or there's no benefit
  to concurrency.
- **`asyncio.TaskGroup`** (Python ≥3.11) — the modern default for running
  multiple tasks. Structural concurrency: waits for all children, cancels
  siblings when one fails, collects errors into an `ExceptionGroup`.
- **`asyncio.gather()`** — fine for simple fan-out where results map 1:1 to
  inputs by position. Weaker guarantees than TaskGroup: if one child raises,
  other children keep running (they are NOT cancelled).
- **`asyncio.wait()`** — when you need `(done, pending)` sets, or
  FIRST_COMPLETED/FIRST_EXCEPTION semantics. Takes *tasks*, not bare coroutines;
  never raises TimeoutError, never cancels on timeout.
- **`asyncio.as_completed()`** — process results as they finish rather than in
  submission order.

```python
# Preferred: TaskGroup — fail-fast, safe cleanup
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch(url_a))
    t2 = tg.create_task(fetch(url_b))
print(t1.result(), t2.result())   # both done after the block

# gather: positional result mapping
results = await asyncio.gather(fetch(a), fetch(b))  # [res_a, res_b]

# as_completed: handle fastest-first
for fut in asyncio.as_completed(tasks):
    result = await fut
```

### Creating tasks safely

`asyncio.create_task(coro)` schedules a coroutine immediately — but the loop
only keeps a **weak reference** to tasks. A fire-and-forget task with no saved
reference can be garbage-collected mid-execution. Keep strong references:

```python
background_tasks = set()

task = asyncio.create_task(some_coro())
background_tasks.add(task)
task.add_done_callback(background_tasks.discard)
```

Caveats of fire-and-forget:
- Exceptions are never retrieved → asyncio logs "Task exception was never
  retrieved". Prefer TaskGroup, which holds references and propagates errors.
- Prefer `tg.create_task()` inside a TaskGroup whenever the task's lifetime
  should be bounded by the enclosing scope.

### Cancellation

Cancellation works by throwing `asyncio.CancelledError` into the task at its
next await point. Rules:

- Use `try/finally` (or async context managers) for cleanup — cleanup runs even
  on cancellation.
- If you catch `CancelledError`, **re-raise it** after cleanup unless you truly
  intend to suppress cancellation. Swallowing it breaks `TaskGroup` and
  `asyncio.timeout()`, which rely on cancellation internally.
- `CancelledError` subclasses `BaseException`, so a bare `except Exception`
  won't catch it — most code needs no special handling.
- Suppressing deliberately requires also calling `task.uncancel()` to clear the
  cancellation state (rare; needed e.g. inside library-level retry logic).
- `await task.cancel()` returns False if the task was already done.
- `shield(aw)` protects an operation from outer cancellation: the caller still
  gets `CancelledError`, but the shielded task keeps running. Always keep a
  reference to the shielded task.

```python
try:
    result = await long_operation()
except asyncio.CancelledError:
    log("cancelled, cleaning up")
    raise            # propagate! don't swallow
finally:
    release_resources()
```

### Timeouts

Prefer context managers over `wait_for` (Python ≥3.11):

```python
try:
    async with asyncio.timeout(10):        # relative seconds
        await long_running_task()
except TimeoutError:
    ...   # catch OUTSIDE the block — timeout() converts internal
          # CancelledError into TimeoutError at exit

# absolute deadline:
loop = asyncio.get_running_loop()
async with asyncio.timeout_at(loop.time() + 20):
    ...

# reschedule mid-flight (e.g., heartbeat keep-alive):
async with asyncio.timeout(None) as cm:
    cm.reschedule(loop.time() + 10)
    ...
```

Notes:
- `asyncio.timeout()` can be safely nested.
- `asyncio.wait_for(aw, timeout)` cancels `aw` on timeout then raises
  `TimeoutError`; wrap in `shield()` if `aw` must survive.
- `asyncio.wait(..., timeout=...)` does NOT cancel or raise — leftovers come
  back in the `pending` set.

### Sleeping & yielding

- `await asyncio.sleep(delay)` — always suspends; never blocks the loop.
- `await asyncio.sleep(0)` — cheap way to yield to other tasks inside
  long-running loops.
- Never `time.sleep()` in a coroutine.

### Blocking code and threads

```python
result = await asyncio.to_thread(blocking_io_function, arg1, kw=...)  # ≥3.9
```

- `to_thread` propagates the current `contextvars.Context`.
- Due to the GIL it's for **I/O-bound** work (files, DB drivers without async
  support); CPU-bound work needs processes or GIL-releasing extensions.
- To submit from another OS thread *into* the loop:
  `asyncio.run_coroutine_threadsafe(coro, loop)` → returns a
  `concurrent.futures.Future`. This is the only common asyncio API that is
  thread-safe and requires passing `loop` explicitly.

## Queues (producer/consumer)

`asyncio.Queue(maxsize=0)` — FIFO; `PriorityQueue` (lowest-priority tuples
first); `LifoQueue`. All are **not thread-safe**, have no timeout parameters
(wrap ops in `wait_for` if needed), and since 3.13 support graceful shutdown.

Canonical worker pool pattern:

```python
async def worker(name, queue: asyncio.Queue):
    while True:
        item = await queue.get()
        try:
            await process(item)
        finally:
            queue.task_done()      # required for join() bookkeeping

queue = asyncio.Queue()
for item in workload:
    queue.put_nowait(item)

workers = [asyncio.create_task(worker(f"w-{i}", queue)) for i in range(3)]

await queue.join()                 # all items produced AND processed
for w in workers:
    w.cancel()
await asyncio.gather(*workers, return_exceptions=True)  # reap cancelled workers
```

Graceful shutdown (Python ≥3.13):

```python
queue.shutdown()             # producers stop; consumers drain remaining items
queue.shutdown(immediate=True)  # discard pending items, unblock everyone with QueueShutDown
```

- `put()` blocks when full (if `maxsize > 0`); `get()` blocks when empty.
- Every `get()` must be matched by exactly one `task_done()` before `join()`
  unblocks; extra calls raise `ValueError`.
- Exceptions: `QueueEmpty`/`QueueFull` (nowait variants), `QueueShutDown` (≥3.13).

## Synchronization primitives

All are **not thread-safe** (use `threading` for OS threads) and none accept a
timeout argument (wrap in `wait_for`). Prefer `async with` forms.

| Primitive | Use for |
|---|---|
| `Lock` | exclusive access to shared state; acquisition is fair (FIFO of waiters) |
| `Event` | one-shot broadcast flag: many tasks wait until `set()` |
| `Condition` | wait for a predicate + exclusive access; combines Event+Lock |
| `Semaphore(n)` | limit concurrency to n (rate limiting, connection pools) |
| `BoundedSemaphore(n)` | same, but raises ValueError on over-release (catches bugs) |
| `Barrier(parties)` | rendezvous: block until N tasks arrive, reusable |

```python
# Semaphore: cap concurrent HTTP requests at 10
sem = asyncio.Semaphore(10)

async def fetch_limited(url):
    async with sem:
        return await fetch(url)

# Condition: always wait_for a predicate — wait() may wake spuriously
cond = asyncio.Condition()
async with cond:
    await cond.wait_for(lambda: items_ready)
    consume()

# Event: startup gate
ready = asyncio.Event()
...
ready.set()          # wakes all waiters
```

Condition gotcha: `notify()`/`notify_all()` require the lock to be held; prefer
`wait_for(predicate)` over manual `while not pred(): await cond.wait()`.

## Best-practice checklist

When writing or reviewing asyncio code, check:

1. No blocking calls (`time.sleep`, sync I/O, heavy CPU) inside coroutines —
   offload via `to_thread` or use async libraries.
2. Every created task is either awaited, owned by a TaskGroup, or strongly
   referenced with retrieved exceptions.
3. `CancelledError` is re-raised after cleanup; no bare swallowing.
4. Timeouts wrap external I/O; `TimeoutError` caught outside the CM.
5. TaskGroup over `gather` for fail-fast semantics; `gather(return_exceptions=True)`
   when partial results are acceptable.
6. `queue.task_done()` paired with every `get()` when using `join()`.
7. Shared mutable state across awaits is guarded by Lock/Condition when
   invariants span multiple steps.
8. Entry point is `asyncio.run(main())` — once per program, not per task.
9. Don't instantiate `Task`/`Future` manually; use high-level APIs.
10. Python version awareness: TaskGroup/timeout/Barrier need ≥3.11,
    `to_thread` ≥3.9, `Queue.shutdown` ≥3.13.

## Reference files

Read these for deeper API detail and more examples:

- `references/tasks.md` — Task object API, cancellation internals
  (`cancelling()`/`uncancel()`), eager task factory, terminating task groups,
  scheduling from other threads, introspection.
- `references/queues.md` — full Queue/PriorityQueue/LifoQueue API and shutdown semantics.
- `references/sync.md` — full Lock/Event/Condition/Semaphore/Barrier API details.
