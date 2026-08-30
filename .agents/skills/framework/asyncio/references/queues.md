# asyncio Queues — Deep Reference

Distilled from https://docs.python.org/3/library/asyncio-queue.html (Python 3.14).

## Contents
1. [Overview & global caveats](#overview--global-caveats)
2. [Queue API](#queue-api)
3. [PriorityQueue and the tie-breaker idiom](#priorityqueue-and-the-tie-breaker-idiom)
4. [LifoQueue](#lifoqueue)
5. [Exceptions](#exceptions)
6. [shutdown() semantics (3.13+)](#shutdown-semantics-313)
7. [Canonical worker pool](#canonical-worker-pool)
8. [Patterns & pitfalls](#patterns--pitfalls)

## Overview & global caveats

- asyncio queues mirror the `queue` module but are **not thread-safe** —
  single-event-loop use only.
- Methods have **no timeout parameter**; wrap in `asyncio.wait_for()` or
  `asyncio.timeout()`.
- `qsize()` is always exact (single loop, no race) — unlike threading queues.

## Queue API

```python
class asyncio.Queue(maxsize=0)
```

| Member | Semantics |
|---|---|
| `maxsize` | Max items; `<= 0` means infinite |
| `qsize()` | Current item count |
| `empty()` / `full()` | `full()` never True when maxsize=0 |
| `await get()` | Remove/return item; wait if empty; raises `QueueShutDown` if shut down and empty |
| `get_nowait()` | Immediate get or `QueueEmpty`; also raises `QueueShutDown` if shut down and empty |
| `await put(item)` | Put; blocks when full (maxsize>0); raises `QueueShutDown` if shut down |
| `put_nowait(item)` | Immediate put or `QueueFull`; raises `QueueShutDown` if shut down |
| `await join()` | Blocks until unfinished count reaches zero |
| `task_done()` | Marks one fetched item complete; `ValueError` if called more times than items put |
| `shutdown(immediate=False)` | Enter shutdown mode (3.13+) |

Bookkeeping: each `put()` increments the unfinished count; each `task_done()`
decrements it. `join()` unblocks at zero.

## PriorityQueue and the tie-breaker idiom

```python
class asyncio.PriorityQueue  # lowest priority first
```

Entries are typically `(priority_number, data)` tuples, compared element-wise.
On equal priorities Python compares `data` — which raises TypeError for
non-comparable data. Prevent this with a monotonic counter:

```python
import itertools

pq = asyncio.PriorityQueue()
counter = itertools.count()

await pq.put((priority, next(counter), data))   # data is never compared
priority, _, data = await pq.get()
```

This gives FIFO ordering among equal priorities. For custom orders wrap
entries in a class implementing `__lt__`.

## LifoQueue

```python
class asyncio.LifoQueue  # most recently added first
```

Same API as Queue; only retrieval order differs.

## Exceptions

| Exception | Raised by | When |
|---|---|---|
| `QueueEmpty` | `get_nowait()` | queue empty |
| `QueueFull` | `put_nowait()` | queue at maxsize |
| `QueueShutDown` (3.13+) | `put`, `put_nowait`, `get`, `get_nowait` | queue shut down |

Asymmetry: after graceful shutdown, `put()` raises immediately but `get()`
keeps working until the queue drains, then raises `QueueShutDown`.

## shutdown() semantics (3.13+)

### Graceful: `queue.shutdown()` (immediate=False)
1. No new items accepted; future `put()` raises `QueueShutDown`.
2. Blocked putters are unblocked with `QueueShutDown`.
3. Consumers keep calling `get()` to drain already-loaded items.
4. Once empty, `get()` raises `QueueShutDown`.
5. A pending `join()` unblocks normally if consumers call `task_done()` for
   remaining items.

### Abort: `queue.shutdown(immediate=True)`
1. Queue drained completely; unfinished count reduced by the number drained.
2. Blocked `join()` callers unblocked (⚠️ even though work wasn't done —
   violates the usual join invariant).
3. Blocked getters unblocked with `QueueShutDown`.

## Canonical worker pool

```python
async def worker(name, queue):
    while True:
        item = await queue.get()
        await process(item)          # e.g. await asyncio.sleep(sleep_for)
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    for item in workload:
        queue.put_nowait(item)

    tasks = [asyncio.create_task(worker(f'worker-{i}', queue)) for i in range(3)]

    await queue.join()               # all items produced AND processed
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)   # reap cancellations
```

Why each piece matters:
- `while True` + blocking `get()`: workers run until cancelled.
- `task_done()` per item: without it `join()` hangs forever.
- Cancel + `gather(return_exceptions=True)`: reaps the infinite-loop workers;
  without it they leak and asyncio warns on exit.

## Patterns & pitfalls

### Backpressure with bounded queues
```python
queue = asyncio.Queue(maxsize=100)   # producers block at 100 → backpressure
```
Unbounded queues let fast producers OOM slow consumers. With bounded queues,
decide explicitly: `await put()` (block) vs `put_nowait()` (drop or handle
QueueFull).

### Timeout on get
```python
try:
    item = await asyncio.wait_for(queue.get(), timeout=5.0)
except TimeoutError:
    ...
```
Edge case: if the timeout cancels `get()` just as an item arrives, the item
can be lost — design so occasional loss is tolerable, or re-check.

### Graceful shutdown pre-3.13: sentinels
```python
_SENTINEL = object()

async def worker(queue):
    while True:
        item = await queue.get()
        try:
            if item is _SENTINEL:
                break
            await process(item)
        finally:
            queue.task_done()

# one sentinel PER WORKER after producing:
for _ in workers:
    await queue.put(_SENTINEL)
```
Pitfalls: forgetting `finally: task_done()` hangs `join()`; sentinel count
must match worker count; sentinels interact badly with bounded queues.

### Graceful shutdown post-3.13: shutdown()
```python
async def worker(queue):
    while True:
        try:
            item = await queue.get()
        except asyncio.QueueShutDown:
            break
        try:
            await process(item)
        finally:
            queue.task_done()

queue.shutdown()               # drain mode
```

### Misc
- Not thread-safe: for cross-thread handoff use `queue.Queue` +
  `loop.call_soon_threadsafe`, or the third-party `janus` library.
- `qsize()/empty()/full()` are advisory between awaits — prefer exception
  handling around `_nowait()` variants over check-then-act.
- Version summary: `loop` param removed 3.10; `shutdown()`/`QueueShutDown` 3.13.
