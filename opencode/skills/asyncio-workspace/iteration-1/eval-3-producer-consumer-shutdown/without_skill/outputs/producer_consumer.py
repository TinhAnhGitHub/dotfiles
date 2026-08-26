"""Asyncio producer/consumer system with clean shutdown.

One producer generates jobs into a bounded queue (maxsize=100 for
backpressure), 4 consumers process them. When production finishes, the
producer closes the queue; consumers drain remaining items and exit.

Run: python producer_consumer.py
"""

import asyncio
import random

QUEUE_MAXSIZE = 100
NUM_CONSUMERS = 4


async def produce_jobs(queue: asyncio.Queue[int], num_jobs: int) -> None:
    """Generate jobs and put them on the queue, then signal end-of-stream."""
    try:
        for i in range(num_jobs):
            # put() suspends when the queue is full -> backpressure on producer.
            await queue.put(i)
            print(f"[producer] enqueued job {i}")
            await asyncio.sleep(random.uniform(0.001, 0.01))
    finally:
        # Signal consumers: no more items will arrive. Each consumer that
        # gets None exits after draining everything queued before it.
        for _ in range(NUM_CONSUMERS):
            await queue.put(None)
        print("[producer] done, sent shutdown sentinels")


async def consume_jobs(worker_id: int, queue: asyncio.Queue[int]) -> None:
    """Process jobs until the None sentinel is seen."""
    while True:
        item = await queue.get()
        try:
            if item is None:
                print(f"[consumer-{worker_id}] received sentinel, exiting")
                return
            # Simulate work.
            await asyncio.sleep(random.uniform(0.005, 0.03))
            print(f"[consumer-{worker_id}] processed job {item}")
        finally:
            # Always mark the task done so queue.join() can unblock,
            # even if processing raised an exception.
            queue.task_done()


async def main() -> None:
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=QUEUE_MAXSIZE)

    producer = asyncio.create_task(produce_jobs(queue, num_jobs=500))
    consumers = [
        asyncio.create_task(consume_jobs(i, queue)) for i in range(NUM_CONSUMERS)
    ]

    # Wait until the producer is finished AND every queued item has been
    # processed (queue.join() unblocks when task_done() count reaches zero).
    await producer
    await queue.join()

    # At this point all real items are drained; consumers will see their
    # sentinels promptly. Cancel-safe because each consumer returns right
    # after its sentinel, but we still await them properly.
    await asyncio.gather(*consumers)
    print("all work complete, clean shutdown")


if __name__ == "__main__":
    asyncio.run(main())
