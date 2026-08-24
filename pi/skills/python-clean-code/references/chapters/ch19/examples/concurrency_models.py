"""Small Chapter 19 examples without network or process side effects."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterable
from queue import Queue
from threading import Thread
from typing import TypeVar, cast


T = TypeVar("T")
U = TypeVar("U")
_MISSING = object()


def threaded_map(
    function: Callable[[T], U], values: Iterable[T], workers: int = 2
) -> list[U]:
    """Use raw threads plus a queue while preserving input order."""
    if workers < 1:
        raise ValueError("workers must be positive")

    items = list(values)
    jobs: Queue[tuple[int, T] | None] = Queue()
    results: list[U | object] = [_MISSING] * len(items)

    def worker() -> None:
        while True:
            job = jobs.get()
            try:
                if job is None:
                    return
                index, value = job
                results[index] = function(value)
            finally:
                jobs.task_done()

    threads = [Thread(target=worker) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for index, value in enumerate(items):
        jobs.put((index, value))
    for _ in threads:
        jobs.put(None)
    jobs.join()
    for thread in threads:
        thread.join()
    return [cast(U, result) for result in results]


async def async_map(function: Callable[[T], U], values: Iterable[T]) -> list[U]:
    """Run cooperative tasks; the function must not block the event loop."""

    async def one(value: T) -> U:
        await asyncio.sleep(0)
        return function(value)

    return await asyncio.gather(*(one(value) for value in values))
