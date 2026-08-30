# Asyncio Bug Review

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

## Bugs and problems

### 1. `time.sleep(item)` blocks the entire event loop (critical)

`time.sleep()` is a *blocking* call inside a coroutine. asyncio is
cooperative single-threaded concurrency: while the worker sleeps, **no other
task can run** — not even `main()`'s `await asyncio.sleep(0.1)` timer. The
whole point of the event loop is defeated.

Fix: use the async equivalent `await asyncio.sleep(item)`, or if the work is
genuinely blocking (sync I/O, CPU), offload it:
`await asyncio.to_thread(blocking_fn, item)`.

### 2. Fire-and-forget task: never awaited, cancelled, or strongly referenced

`t = asyncio.create_task(worker(q))` creates a task that:

- Is **never awaited**, so if `worker` raised an exception it would never be
  retrieved ("Task exception was never retrieved").
- Holds only a **weak reference** on the loop — a fire-and-forget task with no
  saved reference can be garbage-collected mid-execution.
- Runs forever (`while True` with a sentinel-less queue), so when `main()`
  returns, `asyncio.run()` closes the loop with the task still pending →
  **"Task was destroyed but it is pending!"** warning at shutdown.

Fix: keep a strong reference, cancel explicitly, and reap with
`await asyncio.gather(t, return_exceptions=True)` (or better, bound its
lifetime to a scope). The canonical worker-pool pattern from the docs is:
process items → `queue.join()` → cancel workers → gather them.

### 3. No shutdown mechanism for the infinite worker

`while True: item = await q.get()` has no exit condition: no sentinel value,
no cancellation handling, and no `q.shutdown()` (Python ≥3.13). Combined with
bug 2, the program can only end by abandoning/destroying a pending task.
Cancellation also isn't handled gracefully — there's no `try/finally`
cleanup around processing.

### 4. Missing `queue.task_done()` bookkeeping

Every `get()` should be matched by exactly one `task_done()` in a
`try/finally`. It's required for `queue.join()` to ever unblock, and it's the
correct place for cleanup guarantees even if you don't call `join()` today.

### 5. Fragile timing: `await asyncio.sleep(0.1)` as a synchronization hack

The comment "assume program ends here" hides the real bug: `main()` waits a
fixed 0.1 s and exits regardless of whether items were processed. Items whose
"work" takes longer than ~0.1 s are silently dropped (and the pending-task
warning fires). Correct synchronization is deterministic: `await q.join()`
waits until all queued items are actually processed.

### 6. Single worker = no actual concurrency (design smell)

Even after fixing the blocking sleep, one worker processes items strictly
sequentially. If concurrent processing was intended, spawn N workers; the
queue distributes items among them automatically.

## Corrected code

Canonical pattern: fill queue → run workers under explicit lifecycle →
`join()` → cancel workers → reap.

```python
import asyncio


async def worker(name: str, q: asyncio.Queue) -> None:
    while True:
        item = await q.get()
        try:
            await asyncio.sleep(item)      # async sleep instead of time.sleep;
                                           # use asyncio.to_thread(fn, item)
                                           # for genuinely blocking work
            print("done", name, item)
        finally:
            q.task_done()                  # runs even on cancellation


async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()
    for i in range(5):
        q.put_nowait(i)

    workers = [
        asyncio.create_task(worker(f"w-{i}", q)) for i in range(3)
    ]  # multiple workers => real concurrency

    try:
        await q.join()                     # deterministic: wait until ALL items processed
    finally:
        for w in workers:
            w.cancel()                     # stop the while-True loops
        await asyncio.gather(*workers, return_exceptions=True)  # reap; retrieves CancelledError


if __name__ == "__main__":
    asyncio.run(main())
```

Notes on the fix:

- `await asyncio.sleep(item)` replaces `time.sleep(item)` so the loop stays
  responsive and workers overlap.
- `q.task_done()` in `finally` keeps join-bookkeeping correct even when the
  worker is cancelled mid-item (the re-raise of `CancelledError` is implicit —
  we don't catch it, so it propagates).
- `q.join()` + cancel + `gather(..., return_exceptions=True)` gives a clean,
  deterministic shutdown with no pending-task warnings and no lost items.
- On Python ≥3.13 you could alternatively use `q.shutdown()` /
  `QueueShutDown` for graceful drain-and-exit instead of manual cancellation.
