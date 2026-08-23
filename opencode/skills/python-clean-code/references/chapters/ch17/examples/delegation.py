"""Recursive generators and ``yield from`` delegation."""

from __future__ import annotations

from collections.abc import Generator, Iterable, Iterator
from typing import Any


def flatten(items: Iterable[Any]) -> Iterator[Any]:
    """Flatten nested lists/tuples while preserving lazy traversal."""
    for item in items:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


def _emit_with_total(values: Iterable[int]) -> Generator[int, None, int]:
    total = 0
    for value in values:
        total += value
        yield value
    return total


def report(values: Iterable[int]) -> Iterator[int | dict[str, int]]:
    """Forward values, then emit the delegated generator's return value."""
    total = yield from _emit_with_total(values)
    yield {"total": total}


def subclass_tree(cls: type, level: int = 0) -> Iterator[tuple[str, int]]:
    """Walk a class tree recursively using generator delegation."""
    yield cls.__name__, level
    for child in cls.__subclasses__():
        yield from subclass_tree(child, level + 1)
