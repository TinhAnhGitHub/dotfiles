"""Small, dependency-free examples used by the Python design-pattern references."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
Strategy = Callable[[str], str]


def compose_logger(emit: Callable[[str], None], accept: Callable[[str], bool]) -> Callable[[str], None]:
    """Compose filtering and output without a subclass for every combination."""

    def log(message: str) -> None:
        if accept(message):
            emit(message)

    return log


def registry(decorators: dict[str, Callable[[], str]], name: str) -> Callable[[Callable[[], str]], Callable[[], str]]:
    """Return a duplicate-safe registration decorator."""

    def register(factory: Callable[[], str]) -> Callable[[], str]:
        if name in decorators:
            raise ValueError(f"duplicate registration: {name}")
        decorators[name] = factory
        return factory

    return register


def apply_strategy(value: str, strategy: Strategy) -> str:
    return strategy(value)


def counted(fn: Callable[P, R]) -> Callable[P, R]:
    """A typed decorator that keeps callable metadata."""

    calls = 0

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        nonlocal calls
        calls += 1
        return fn(*args, **kwargs)

    return wrapper


class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


ALLOWED: dict[Status, set[Status]] = {
    Status.PENDING: {Status.RUNNING},
    Status.RUNNING: {Status.DONE, Status.FAILED},
    Status.DONE: set(),
    Status.FAILED: {Status.PENDING},
}


@dataclass
class WorkflowState:
    status: Status = Status.PENDING

    def transition(self, new_status: Status) -> None:
        if new_status not in ALLOWED[self.status]:
            raise ValueError(f"invalid transition: {self.status} -> {new_status}")
        self.status = new_status


class EventBus:
    def __init__(self) -> None:
        self._listeners: list[Callable[[str], None]] = []

    def subscribe(self, listener: Callable[[str], None]) -> None:
        self._listeners.append(listener)

    def publish(self, event: str) -> None:
        for listener in tuple(self._listeners):
            listener(event)


def nonempty(values: Iterable[str]) -> Iterable[str]:
    return (value for value in values if value.strip())
