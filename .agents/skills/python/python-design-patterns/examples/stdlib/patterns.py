"""Small, dependency-free examples used by the Python design-pattern references."""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache, wraps
from typing import ParamSpec, Protocol, TypeVar, runtime_checkable

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


class CommandRegistry:
    """A scoped, testable hierarchical command registry."""

    def __init__(self) -> None:
        self._commands: dict[tuple[str, str], Callable[..., object]] = {}

    def register(self, group: str, name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
        def decorator(fn: Callable[..., object]) -> Callable[..., object]:
            key = (group, name)
            if key in self._commands:
                raise ValueError(f"duplicate command registration: {group}:{name}")
            self._commands[key] = fn
            return fn

        return decorator

    def get_commands(self) -> dict[tuple[str, str], Callable[..., object]]:
        """Return a defensive shallow copy of registered commands."""
        return self._commands.copy()

    def dispatch(self, group: str, name: str, *args: object, **kwargs: object) -> object:
        key = (group, name)
        command = self._commands.get(key)
        if command is None:
            raise KeyError(f"unknown command: {group}:{name}")
        return command(*args, **kwargs)


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


@runtime_checkable
class OrderReader(Protocol):
    def get_orders(self) -> list[str]: ...


@runtime_checkable
class OrderWriter(Protocol):
    def enqueue(self, order_id: str) -> None: ...


class OrderHistory:
    """Read-only collection satisfying OrderReader without pretending to write (preserving LSP)."""

    def __init__(self, orders: Iterable[str] = ()) -> None:
        self._orders = list(orders)

    def get_orders(self) -> list[str]:
        return self._orders.copy()


class OrderQueue:
    """Read-write collection satisfying both OrderReader and OrderWriter."""

    def __init__(self, orders: Iterable[str] = ()) -> None:
        self._orders = list(orders)

    def enqueue(self, order_id: str) -> None:
        self._orders.append(order_id)

    def get_orders(self) -> list[str]:
        return self._orders.copy()


@dataclass(frozen=True)
class SyncOptions:
    validate: bool = False
    max_attempts: int = 1


@dataclass(frozen=True)
class SyncSummary:
    synced_count: int
    attempts: int


class RecordSink(Protocol):
    def save_records(self, records: list[str]) -> None: ...


def sync_records(
    sink: RecordSink,
    records: list[str],
    options: SyncOptions = SyncOptions(),
) -> SyncSummary:
    """Synchronize records using data options instead of a subclass matrix."""
    if options.validate and any(not r.strip() for r in records):
        raise ValueError("records cannot be blank")

    for attempt in range(1, options.max_attempts + 1):
        try:
            sink.save_records(records)
            return SyncSummary(synced_count=len(records), attempts=attempt)
        except ConnectionError:
            if attempt == options.max_attempts:
                raise
    raise AssertionError("unreachable")


class TokenBucketRateLimiter:
    """A deterministic token bucket rate limiter for abuse prevention."""

    def __init__(
        self,
        rate: float,
        capacity: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if rate <= 0 or capacity <= 0:
            raise ValueError("rate and capacity must be positive")
        self.rate = float(rate)
        self.capacity = float(capacity)
        self._tokens = float(capacity)
        self._clock = clock
        self._last_updated = self._clock()

    def allow_request(self, tokens: float = 1.0) -> bool:
        """Check and consume tokens if available."""
        now = self._clock()
        elapsed = max(0.0, now - self._last_updated)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_updated = now

        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False


@dataclass(frozen=True)
class AppSettings:
    api_url: str
    database_url: str
    log_level: str = "INFO"
    rate_limit_per_minute: int = 60


def load_settings(env: dict[str, str] | None = None) -> AppSettings:
    """Load settings from environment mapping with typed defaults (12-Factor)."""
    source = os.environ if env is None else env
    return AppSettings(
        api_url=source.get("API_URL", "http://localhost:8000"),
        database_url=source.get("DATABASE_URL", "sqlite:///./app.db"),
        log_level=source.get("LOG_LEVEL", "INFO"),
        rate_limit_per_minute=int(source.get("RATE_LIMIT_PER_MINUTE", "60")),
    )


class DomainError(Exception):
    """Base exception for all domain-level invariant violations."""


class InvalidQuantity(DomainError):
    """Raised when an order quantity is non-positive."""


class UnknownSku(DomainError):
    """Raised when a requested product SKU is not recognized."""


class OutOfStock(DomainError):
    """Raised when the inventory cannot fulfill the requested quantity."""


@dataclass(frozen=True)
class OrderRequest:
    sku: str
    quantity: int


@dataclass(frozen=True)
class OrderPlaced:
    sku: str
    quantity_reserved: int


@runtime_checkable
class InventoryPort(Protocol):
    """Port defining the operations required by the domain for inventory management."""

    def exists_sku(self, sku: str) -> bool: ...

    def get_stock(self, sku: str) -> int: ...

    def reserve(self, sku: str, quantity: int) -> None: ...


def place_order(req: OrderRequest, inventory: InventoryPort) -> OrderPlaced:
    """Pure domain use case: verifies stock invariants and reserves inventory."""
    if req.quantity <= 0:
        raise InvalidQuantity(f"Quantity must be positive: {req.quantity}")
    if not inventory.exists_sku(req.sku):
        raise UnknownSku(f"Unknown SKU: {req.sku}")
    if inventory.get_stock(req.sku) < req.quantity:
        raise OutOfStock(
            f"Insufficient stock for {req.sku}: available {inventory.get_stock(req.sku)}, requested {req.quantity}"
        )

    inventory.reserve(req.sku, req.quantity)
    return OrderPlaced(sku=req.sku, quantity_reserved=req.quantity)


class InMemoryInventoryAdapter:
    """A pure dictionary-backed adapter implementing InventoryPort for tests or prototyping."""

    def __init__(self, stock: dict[str, int] | None = None) -> None:
        self._stock: dict[str, int] = dict(stock) if stock else {}

    def exists_sku(self, sku: str) -> bool:
        return sku in self._stock

    def get_stock(self, sku: str) -> int:
        return self._stock.get(sku, 0)

    def reserve(self, sku: str, quantity: int) -> None:
        if self._stock.get(sku, 0) < quantity:
            raise ValueError("Cannot reserve more than available stock")
        self._stock[sku] -= quantity


class TTLCache:
    """A thread-safe, time-limited cache decorator with custom clock support."""

    def __init__(
        self,
        seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if seconds <= 0:
            raise ValueError("TTL seconds must be positive")
        self.seconds = float(seconds)
        self._clock = clock
        self._lock = threading.Lock()
        self._cache: dict[tuple[tuple[object, ...], tuple[tuple[str, object], ...]], tuple[object, float]] = {}

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, tuple(sorted(kwargs.items())))
            now = self._clock()
            with self._lock:
                if key in self._cache:
                    cached_val, timestamp = self._cache[key]
                    if now - timestamp < self.seconds:
                        return cached_val  # type: ignore[return-value]

            result = func(*args, **kwargs)

            with self._lock:
                self._cache[key] = (result, self._clock())
            return result

        return wrapper


def lazy_stream(
    source: Iterable[R],
    limit: int | None = None,
) -> Iterator[R]:
    """Stream items lazily from an iterable with optional early termination."""
    if limit is not None and limit <= 0:
        return
    count = 0
    iterator = iter(source)
    while limit is None or count < limit:
        try:
            item = next(iterator)
        except StopIteration:
            break
        yield item
        count += 1


class BackgroundPreloader:
    """Preloads expensive resources in a background daemon thread."""

    def __init__(self, loader: Callable[[], R]) -> None:
        self._loader = loader
        self._result: R | None = None
        self._error: Exception | None = None
        self._done = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            self._result = self._loader()
        except Exception as exc:
            self._error = exc
        finally:
            self._done.set()

    def get(self, timeout: float | None = None) -> R:
        """Wait for and return preloaded result."""
        if not self._done.wait(timeout=timeout):
            raise TimeoutError("Background preloader timed out")
        if self._error is not None:
            raise self._error
        return self._result  # type: ignore[return-value]




