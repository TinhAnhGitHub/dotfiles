"""Small Chapter 20 examples for ordered and completion-order futures."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import TypeVar


T = TypeVar("T")
U = TypeVar("U")


def ordered_map(
    function: Callable[[T], U], values: Iterable[T], workers: int = 2
) -> list[U]:
    """Return results aligned with the input iterable."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(function, values))


def completed_map(
    function: Callable[[T], U], values: Iterable[T], workers: int = 2
) -> list[U]:
    """Return results as futures complete, observing every exception."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures: dict[Future[U], T] = {
            executor.submit(function, value): value for value in values
        }
        return [future.result() for future in as_completed(futures)]


def collect_failures(
    function: Callable[[T], U], values: Iterable[T]
) -> list[Exception]:
    """Collect worker failures while still letting the executor shut down cleanly."""
    failures: list[Exception] = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(function, value) for value in values]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:  # intentionally aggregate at this boundary
                failures.append(exc)
    return failures
