# asyncio Synchronization Primitives — Deep Reference

Distilled from https://docs.python.org/3/library/asyncio-sync.html and the
Concurrency & Multithreading section of https://docs.python.org/3/library/asyncio-dev.html
(Python 3.14).

## Contents
1. [Global caveats](#global-caveats)
2. [Lock](#lock)
3. [Event](#event)
4. [Condition](#condition)
5. [Semaphore / BoundedSemaphore](#semaphore--boundedsemaphore)
6. [Barrier](#barrier)
7. [Thread-safety model (asyncio-dev)](#thread-safety-model-asyncio-dev)

## Global caveats

Apply to ALL primitives:

1. **Not thread-safe** — never use for OS-thread synchronization; use `threading`.
2. **No timeout parameters** — wrap operations in `asyncio.wait_for()` or
   `asyncio.timeout()`:
   ```python
   async with asyncio.timeout(10):
       async with lock:
           ...
   ```
3. Prefer `async with` over manual acquire/release.
4. Version notes: `loop` param removed 3.10; old forms (`await lock`,
   `with await lock`) removed 3.9; Barrier added 3.11.

## Lock

```python
lock = asyncio.Lock()

async with lock:          # preferred
    # access shared state

# equivalent to:
await lock.acquire()
try:
    ...
finally:
    lock.release()
```

| Method | Semantics |
|---|---|
| `await acquire()` | Waits until unlocked, locks, returns True |
| `release()` | Unlocks; `RuntimeError` if already unlocked |
| `locked()` | True if locked |

**Fairness guarantee:** acquisition is fair — among blocked waiters, the one
that started waiting first proceeds (FIFO by wait-start order).

## Event

One-shot broadcast flag, initially False. Notifies *multiple* tasks at once.

| Method | Semantics |
|---|---|
| `await wait()` | Returns True immediately if set; else blocks until `set()` |
| `set()` | Sets flag; wakes ALL waiters immediately |
| `clear()` | Resets flag; subsequent `wait()` blocks again |
| `is_set()` | True if set |

```python
event = asyncio.Event()
waiter_task = asyncio.create_task(waiter(event))  # await event.wait()
await asyncio.sleep(1)
event.set()
```

Use Event for "has X happened yet" gates (startup readiness, shutdown flags).
For state-dependent waiting with a condition, prefer Condition.wait_for.

## Condition

Combines Event + Lock: wait for an event, then get exclusive access.
Multiple Condition objects can share one Lock to coordinate different states
of a shared resource.

```python
cond = asyncio.Condition()      # or asyncio.Condition(shared_lock)

async with cond:                # acquires underlying lock
    await cond.wait_for(lambda: ready)   # recommended over manual loop
    consume()
    cond.notify_all()           # OK: lock held inside async-with
```

| Method | Semantics |
|---|---|
| `await acquire()` / `release()` / `locked()` | Underlying Lock API |
| `notify(n=1)` | Wake up to n waiters; **lock must be held** or RuntimeError |
| `notify_all()` | Wake all waiters; same lock requirement |
| `await wait()` | Requires held lock; releases it, blocks until notified, re-acquires, returns True |
| `await wait_for(predicate)` | Repeatedly waits until predicate true; returns final value |

**Spurious wakeup:** a task may return from `wait()` spuriously — always
re-check state in a loop, i.e. just use `wait_for(predicate)`.

## Semaphore / BoundedSemaphore

```python
sem = asyncio.Semaphore(10)

async with sem:              # cap concurrency at 10
    return await fetch(url)
```

Internal counter decremented by `acquire()`, incremented by `release()`; never
below zero; `acquire()` blocks at zero. `ValueError` if initial value < 0.

| Method | Semantics |
|---|---|
| `await acquire()` | Decrement if >0 (True); else block until release() |
| `release()` | Increment counter; may wake a waiter |
| `locked()` | True if not immediately acquirable |

Difference: plain `Semaphore` allows more releases than acquisitions (counter
can exceed initial value); `BoundedSemaphore.release()` raises `ValueError`
above the initial value — catches over-release bugs. Prefer BoundedSemaphore
when release sites are scattered.

Classic uses: rate-limiting concurrent HTTP requests, connection-pool sizing,
bounding fan-out work.

## Barrier

```python
b = asyncio.Barrier(parties)     # 3.11+
```

Blocks until `parties` tasks call `wait()`; then all unblock simultaneously.
Reusable any number of times (filling → draining → filling...).

| Member | Semantics |
|---|---|
| `await wait()` | Passes barrier when all parties arrive. **Returns unique int in 0..parties−1** for each task — usable for electing housekeeping duty. Raises `BrokenBarrierError` if broken/reset while waiting |
| `async with b as position:` | Alternative form binding the position index |
| `await reset()` | Back to empty state; current waiters get BrokenBarrierError. If broken, prefer creating a new barrier |
| `await abort()` | Put into broken state; active/future wait() fails — use when one task must abort to avoid infinite waits |
| `parties` | Required task count |
| `n_waiting` | Tasks currently waiting while filling |
| `broken` | True if broken |

```python
async with barrier as position:
    if position == 0:
        print('only one task does this')
```

A cancelled waiting task exits without changing barrier state (n_waiting
decrements while filling). `BrokenBarrierError` subclasses `RuntimeError`.

## Thread-safety model (asyncio-dev)

- The event loop runs in ONE thread and executes all callbacks/tasks there;
  only one task runs at a time; tasks interleave only at await points.
- **Almost all asyncio objects are not thread-safe.** This rarely matters
  unless touched from outside tasks/callbacks (i.e., another OS thread).
- Thread-safe crossing points ONLY:
  - `loop.call_soon_threadsafe(cb, *args)` — schedule a callback from another
    thread (e.g., `loop.call_soon_threadsafe(fut.cancel)`).
  - `asyncio.run_coroutine_threadsafe(coro, loop)` — submit a coroutine;
    returns `concurrent.futures.Future`.
- Debug mode makes wrong-thread calls to non-threadsafe APIs raise.
- Blocking code: never call directly in coroutines/callbacks — offload via
  `loop.run_in_executor(...)` or `asyncio.to_thread(...)`. Callbacks slower
  than 100 ms are logged in debug mode (`loop.slow_callback_duration`).
- No way to schedule callbacks/coroutines directly from a different *process*;
  use pipes/fd-watching, subprocess APIs, or ProcessPoolExecutor.
- Signal handling requires the loop to run in the main thread.
- Async generators: close explicitly (`aclose()`/`contextlib.aclosing()`);
  don't iterate concurrently or across loops.
- Enable debug mode via `PYTHONASYNCIODEBUG=1`, `-X dev`, `asyncio.run(debug=True)`,
  or `loop.set_debug(True)` — surfaces never-awaited coroutines,
  never-retrieved exceptions, slow callbacks, wrong-thread calls.
