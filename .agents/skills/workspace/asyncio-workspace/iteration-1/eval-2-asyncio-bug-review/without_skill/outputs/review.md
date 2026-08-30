# Asyncio Snippet Bug Review

```python
import asyncio, time

async def worker(q):
    while True:
        item = await q.get()
        time.sleep(item)
        print('done', item)

async def main():
    q = asyncio.Queue()
    for i in range(5):
        q.put_nowait(i)
    t = asyncio.create_task(worker(q))
    await asyncio.sleep(0.1)
    # assume program ends here

asyncio.run(main())
```

## Bugs and Problems

### 1. `time.sleep(item)` blocks the event loop (critical)

`worker` is a coroutine running on the event loop, but `time.sleep()` is a *blocking* call. While it sleeps, the entire event loop freezes: no other tasks, timers, callbacks, or I/O can run. This defeats the purpose of asyncio entirely.

**Fix:** use the non-blocking `await asyncio.sleep(item)`.

### 2. Worker never calls `q.task_done()`

Every `q.get()` should be paired with a `q.task_done()` call once processing finishes. Without it, `await q.join()` (the standard way to wait for queue drain) would block forever because unfinished-task counts never reach zero.

### 3. The worker task is never awaited, cancelled, or joined

`main()` starts `t = asyncio.create_task(worker(q))` but then just sleeps for 0.1 s and returns. Consequences:

- When `main()` returns, `asyncio.run()` cancels all pending tasks at shutdown. The worker gets cancelled mid-flight with no cleanup, and asyncio may emit `"Task was destroyed but it is pending!"`-style warnings depending on timing/state.
- The program's completion is decided by an arbitrary wall-clock guess (`0.1s`) rather than by actual work completion — items may or may not be printed before shutdown.
- Note that simply doing `await t` would hang forever, because the worker loops infinitely (see next point).

### 4. Infinite worker loop with no exit condition

`while True` with no `break`/sentinel means the worker can never finish gracefully. Even in a corrected version, you need either:
- a **sentinel value** (e.g. `None`) to signal shutdown, or
- explicit cancellation after `q.join()`, handled via `except asyncio.CancelledError`.

### 5. Only one worker → no concurrency even after fixing blocking sleep

If concurrency is intended, a single worker processes items strictly sequentially. Create multiple workers to consume the queue in parallel.

## Corrected Code

```python
import asyncio

NUM_WORKERS = 3

async def worker(name: str, q: asyncio.Queue):
    while True:
        item = await q.get()
        try:
            await asyncio.sleep(item)   # non-blocking sleep; loop stays responsive
            print(f'{name} done {item}')
        finally:
            q.task_done()               # always mark the item as handled

async def main():
    q = asyncio.Queue()
    for i in range(5):
        q.put_nowait(i)

    workers = [asyncio.create_task(worker(f'w{i}', q)) for i in range(NUM_WORKERS)]

    await q.join()          # deterministic: wait until every queued item is done

    for w in workers:       # graceful shutdown
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

asyncio.run(main())
```

Key changes:

| Problem | Fix |
|---|---|
| Blocking `time.sleep` | `await asyncio.sleep` |
| Missing `task_done` | Called in `finally`, so it fires even if processing raises |
| Arbitrary 0.1 s wait / dangling task | `await q.join()` waits for real completion |
| No exit path | Workers cancelled explicitly and gathered with `return_exceptions=True` to swallow `CancelledError` |
| Single sequential worker | Pool of 3 workers consuming concurrently |

Alternative pattern instead of cancellation: push one sentinel (`None`) per worker into the queue after filling it, and have workers `break` on receiving it.
