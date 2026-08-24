"""Dependency-free Chapter 18 examples."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
from typing import Iterator


@contextmanager
def captured_text() -> Iterator[StringIO]:
    """Own a temporary text buffer and close it on every exit path."""
    buffer = StringIO()
    try:
        yield buffer
    finally:
        buffer.close()


@contextmanager
def suppress_zero_division() -> Iterator[None]:
    """Suppress only the one expected, documented exception."""
    try:
        yield
    except ZeroDivisionError:
        return


@dataclass(frozen=True)
class Click:
    x: int
    y: int


@dataclass(frozen=True)
class TypeText:
    text: str


@dataclass(frozen=True)
class KeyPress:
    key: str


def describe_action(action: Click | TypeText | KeyPress) -> str:
    """Dispatch a closed action vocabulary with structural matching."""
    match action:
        case Click(x=x, y=y):
            return f"click({x}, {y})"
        case TypeText(text=text) if text:
            return f"type({text!r})"
        case KeyPress(key=key):
            return f"press({key})"
        case TypeText():
            raise ValueError("text must not be empty")
        case _:
            raise ValueError(f"unsupported action: {action!r}")


def find_first_even(values: list[int]) -> int | None:
    for value in values:
        if value % 2 == 0:
            return value
    else:
        return None
