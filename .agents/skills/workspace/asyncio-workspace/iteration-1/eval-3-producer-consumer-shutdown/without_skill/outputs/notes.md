# Producer/Consumer shutdown strategy notes

## Design choices

- **Bounded queue (`maxsize=100`)**: `await queue.put()` suspends the producer
  when full, giving natural backpressure — the producer can't outrun consumers.
- **Sentinel values (`None`) for shutdown**: after producing all jobs, the
  producer enqueues exactly one `None` per consumer. Consumers loop until they
  see a sentinel, so every real item enqueued *before* it is drained first.
- **`queue.join()` before awaiting consumers**: guarantees that by the time we
  wait on consumer tasks, no unprocessed items remain. Combined with sentinels,
  this makes "drain then exit" explicit rather than relying on task scheduling.
- **`task_done()` in a `finally` block**: even if a consumer raises while
  processing an item, `join()` can still unblock and exceptions propagate via
  `gather`, avoiding a hung shutdown.
- **Why not cancel consumers?** Cancelling is fine for abort-on-error, but it
  risks losing in-flight items. Sentinel + join gives at-least-drained semantics
  with zero data loss. Cancellation would be the right tool if we needed a hard
  deadline (e.g., wrap the drain in `asyncio.wait_for(..., timeout=...)`).
- **Alternative considered**: `queue.shutdown()` (added in Python 3.13) supports
  half-close semantics natively; since the target is 3.12, sentinels are the
  idiomatic approach.

## Verified

Script runs to completion under Python 3.12: producer finishes, all 500 jobs
are processed across the 4 workers, consumers exit after their sentinels, and
`main` returns cleanly (no pending-task warnings from `asyncio.run`).
