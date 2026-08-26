"""Asyncio producer/consumer system with backpressure and clean shutdown.

One producer generates jobs into a bounded asyncio.Queue (maxsize=100),
4 consumers process them, and when production finishes everything shuts
down cleanly: the producer completes, consumers drain all remaining items,
then exit.

Shutdown strategy (Python 3.12):
    queue.join() waits until every produced item has been processed
    (each get() is paired with exactly one task_done()), then the
    infinite-loop consumer tasks are cancelled and reaped with
    gather(..., return_exceptions=True).

    On Python >= 3.13 you would instead call ``await queue.put(SENTINEL)``
    per worker or simply ``queue.shutdown()`` -- see notes.md.
"""

from __future__ import annotations

import asyncio
import itertools
import logging

QUEUE_MAXSIZE = 100
NUM_CONSUMERS = 4
TOTAL_JOBS = 500
PRODUCE_DELAY = 0.001
PROCESS_DELAY = 0.005

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(message)s",
)
log = logging.getLogger("producer_consumer")


async def produce(queue: asyncio.Queue[int], total: int) -> int:
    """Generate *total* jobs into the bounded queue, applying backpressure.

    ``await put()`` blocks when the queue is full (maxsize=100), so the
    producer naturally slows down to the pace of the consumers instead of
    letting the queue grow without bound.
    """
    counter = itertools.count(1)
    for _ in range(total):
        job_id = next(counter)
        await queue.put(job_id)  # blocks when full -> backpressure
        if job_id % 100 == 0:
            log.info("produced job %d/%d (queue size=%d)", job_id, total, queue.qsize())
        # Simulate upstream work; NEVER time.sleep() in a coroutine.
        await asyncio.sleep(PRODUCE_DELAY)
    log.info("producer finished after %d jobs", total)
    return total


async def consume(name: str, queue: asyncio.Queue[int]) -> int:
    """Process items forever until cancelled.

    Runs until the main coroutine cancels it after ``queue.join()``
    confirms every item has been processed.
    """
    processed = 0
    while True:
        item = await queue.get()
        try:
            # Simulate I/O-bound processing (e.g. an HTTP request).
            await asyncio.sleep(PROCESS_DELAY)
            processed += 1
            log.info("%s processed job %d", name, item)
        finally:
            # Paired with get(): required for join() bookkeeping.
            # In finally so cancellation mid-processing still counts
            # the item as handled before we re-raise.
            queue.task_done()
    return processed  # pragma: no cover - unreachable, task ends via cancel


async def main() -> None:
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=QUEUE_MAXSIZE)

    # Strong references: the event loop only keeps weak refs to tasks,
    # so fire-and-forget tasks can be garbage-collected mid-flight.
    consumers = [
        asyncio.create_task(consume(f"consumer-{i}", queue))
        for i in range(NUM_CONSUMERS)
    ]

    await produce(queue, TOTAL_JOBS)

    # Unblocks once every produced item has had task_done() called --
    # i.e. all consumers finished draining the remaining items.
    await queue.join()

    # All work is done; stop the infinite-loop consumers and reap them.
    # gather(return_exceptions=True) collects the CancelledErrors so no
    # "Task exception was never retrieved" warning is logged.
    for c in consumers:
        c.cancel()
    results = await asyncio.gather(*consumers, return_exceptions=True)

    cancelled = sum(isinstance(r, asyncio.CancelledError) for r in results)
    log.info(
        "shutdown clean: %d/%d consumers exited via cancellation",
        cancelled,
        NUM_CONSUMERS,
    )


if __name__ == "__main__":
    asyncio.run(main())
