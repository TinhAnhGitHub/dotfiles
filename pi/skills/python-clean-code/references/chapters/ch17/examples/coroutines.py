"""Typed classic-coroutine examples using send, throw, and close."""

from __future__ import annotations

from collections.abc import Generator
from typing import NamedTuple


class Result(NamedTuple):
    count: int
    average: float


class StopAveraging:
    """Sentinel type used to request a coroutine return its accumulated result."""

    def __repr__(self) -> str:
        return "<STOP>"


STOP = StopAveraging()


def averager() -> Generator[None, float | StopAveraging, Result]:
    """Receive numbers with ``send`` and return a result through StopIteration."""
    total = 0.0
    count = 0
    while True:
        term = yield
        if isinstance(term, StopAveraging):
            return Result(count, total / count if count else 0.0)
        total += term
        count += 1


class Snapshot(NamedTuple):
    count: int
    average: float


class ResetStats(Exception):
    """Exception that can be injected to reset the running statistics."""


def stats_tracker() -> Generator[Snapshot, float, None]:
    """A small bidirectional state machine with reset and guaranteed cleanup."""
    total = 0.0
    count = 0
    try:
        while True:
            try:
                value = yield Snapshot(count, total / count if count else 0.0)
            except ResetStats:
                total = 0.0
                count = 0
            else:
                total += value
                count += 1
    finally:
        # Real code could close a file, release a subscription, or flush metrics here.
        pass
