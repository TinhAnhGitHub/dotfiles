"""Small, runnable Chapter 17 examples for lazy iteration."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator
from itertools import islice
from typing import Any, TypeVar


T = TypeVar("T")
RE_WORD = re.compile(r"\w+")


def take(count: int, iterable: Iterable[T]) -> list[T]:
    """Materialize only the requested prefix of an iterable."""
    if count < 0:
        raise ValueError("count must be non-negative")
    return list(islice(iterable, count))


def chunked(iterable: Iterable[T], size: int) -> Iterator[tuple[T, ...]]:
    """Yield bounded-size tuples without loading the whole input."""
    if size <= 0:
        raise ValueError("size must be positive")

    source = iter(iterable)
    while chunk := tuple(islice(source, size)):
        yield chunk


def read_until(read: Callable[[], T], sentinel: T) -> Iterator[T]:
    """Adapt a zero-argument pull function to a lazy iterator."""
    yield from iter(read, sentinel)


def arithmetic_progression(
    begin: Any, step: Any, end: Any | None = None
) -> Iterator[Any]:
    """Yield ``begin + step * index`` while avoiding accumulated float drift."""
    result_type = type(begin + step)
    result = result_type(begin)
    index = 0
    while end is None or result < end:
        yield result
        index += 1
        result = begin + step * index


class Sentence:
    """A reusable iterable whose word extraction stays lazy."""

    def __init__(self, text: str) -> None:
        self.text = text

    def __iter__(self) -> Iterator[str]:
        for match in RE_WORD.finditer(self.text):
            yield match.group()


def fibonacci() -> Iterator[int]:
    """An intentionally infinite lazy sequence."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
