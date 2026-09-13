# P16 — Concurrency, Scheduling, and Resource Lifecycle

## Problem

Concurrent systems must define ownership, backpressure, cancellation, cleanup, and fairness. A clean class boundary is not enough if a worker, socket, GPU pool, or native handle outlives its owner.

## Use when

- Work runs concurrently or is scheduled across workers.
- Resources need deterministic cleanup.
- Python coordinates a performance-critical native implementation.

## Book theory

Mak ch41 covers synchronization and producer/consumer design. Percival ch09 shows queued event processing. Keen ch23 treats lifecycle and telemetry as boundary concerns.

## Minimal standard-library implementation

~~~python
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractContextManager


class WorkerPool(AbstractContextManager["WorkerPool"]):
    def __init__(self, workers: int) -> None:
        self._executor = ThreadPoolExecutor(max_workers=workers)

    def map(self, jobs: Iterable[Callable[[], object]]) -> list[object]:
        return list(self._executor.map(lambda job: job(), jobs))

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self._executor.shutdown(wait=exc_type is None, cancel_futures=True)
        return False
~~~

The owner uses `with WorkerPool(...)` and therefore defines teardown even when a job raises. Real schedulers add queues, admission control, retries, and metrics.

## Python/native boundary

In ML systems, Python commonly owns configuration, scheduling, orchestration, and error policy; C++, CUDA, Rust, or kernels own tensor operations, memory movement, and latency-sensitive loops. Document that boundary separately instead of assuming Python abstractions cover the hot path.

## Production evidence to inspect

Find queue/scheduler construction, worker lifecycle, cancellation, resource cleanup, and tests for backpressure or failure injection. Record which side of the Python/native boundary owns each resource.

## Production compromise

High-throughput systems may use global pools, asynchronous cleanup, or native handles that cannot be closed immediately. These trade simple ownership for throughput; expose health and shutdown diagnostics and bound queues where possible.

## When not to use it

Do not add threads or an actor scheduler to hide a slow algorithm that could be made synchronous or vectorized. Concurrency is a semantic and operational cost.

## Tests and practice

Test cancellation, bounded submission, shutdown, worker failure, and no leaked handles. Use the [workflow-state exercise](../exercises/workflow-state.md).

## Related IDs

P09 (scheduling policy), P13 (workflow), P14 (observability), P17 (failure tests).

