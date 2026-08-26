# Shutdown strategy notes

Target: Python 3.12 (so `asyncio.Queue.shutdown()` / `QueueShutDown` from 3.13+ is unavailable).

## Chosen strategy: `queue.join()` → cancel → reap

1. Producer `await queue.put(job)` into `Queue(maxsize=100)`. When full, the
   producer blocks — that *is* the backpressure; no drops, no unbounded growth.
2. Consumers run `while True: item = await queue.get()` with
   `queue.task_done()` in a `finally:` block. The `finally` matters: if a task
   were ever cancelled mid-processing, the get/task_done pairing stays intact.
3. After the producer finishes, main awaits `queue.join()`. This unblocks only
   when every produced item has been processed (each `get()` matched by exactly
   one `task_done()`), i.e. consumers have drained all remaining items.
4. Then consumers are cancelled and reaped with
   `gather(..., return_exceptions=True)`, which collects the expected
   `CancelledError`s and avoids "Task exception was never retrieved" warnings.

## Alternatives considered

- **Sentinels (one `None` per worker after production).** Works on 3.12 too,
  but the sentinel count must exactly match the worker count, sentinels occupy
  slots in a bounded queue (interacting with backpressure), and the consumer
  loop needs a special-case branch. More moving parts for the same guarantee.
- **`queue.shutdown()` (3.13+).** The cleanest option once available:
  graceful mode stops puts, lets consumers drain, then raises `QueueShutDown`
  out of `get()`. If the project moves to ≥3.13, replace the cancel/reap step
  with `queue.shutdown()` + catching `QueueShutDown` in consumers.
- **`wait_for(queue.get(), timeout=...)` polling.** Avoided: the timeout can
  cancel `get()` just as an item arrives, silently losing it.

## Other choices

- Tasks are held in a list (strong references) — the loop keeps only weak refs,
  so fire-and-forget tasks can be garbage-collected.
- `CancelledError` is never swallowed by consumers (`except Exception` wouldn't
  catch it anyway since it subclasses `BaseException`; there's no broad handler).
- No blocking calls in coroutines; simulated work uses `asyncio.sleep`.
- Single `asyncio.run(main())` entry point.
