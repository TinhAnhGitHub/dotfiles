# P10 — Commands, Events, and Message Bus

## Problem

Direct calls couple a use case to every side effect. P10 distinguishes intent (command) from a fact that already happened (event), then gives dispatch and failure semantics a visible home.

## Use when

- One action has several independent side effects.
- Work should be queued, retried, or observed.
- A boundary needs one handler for intent and many consumers for facts.

## Book theory

Percival ch08–ch11 develops domain events, an in-process message bus, commands, and external integration events. Keen ch18 treats the bus as application orchestration. Mak ch37 provides the Observer analogy, with different delivery semantics.

## Minimal standard-library implementation

~~~python
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True)
class OrderPlaced:  # Event: a past fact.
    order_id: str


Message: TypeAlias = OrderPlaced
Handler = Callable[[Message], None]


class Bus:
    def __init__(self) -> None:
        self._handlers: dict[type[Message], list[Handler]] = defaultdict(list)
        self._queue: deque[Message] = deque()

    def subscribe(self, kind: type[Message], handler: Handler) -> None:
        self._handlers[kind].append(handler)

    def publish(self, message: Message) -> None:
        self._queue.append(message)
        while self._queue:
            current = self._queue.popleft()
            for handler in self._handlers[type(current)]:
                handler(current)
~~~

A command should have one owner and fail loudly; an event may have zero or many handlers. Add idempotency keys, retries, and durable storage when crossing a process boundary.

## Production evidence to inspect

Record sync/async dispatch, handler cardinality, retry and idempotency behavior, durability, and failure isolation. Tests should show what happens when one handler fails; names such as `publish` alone are not enough.

## Production compromise

Many Python projects use in-process callbacks for low latency and operational simplicity, then add a broker only for selected integration events. This avoids distributed infrastructure but does not provide durable replay or cross-process delivery.

## When not to use it

Use a direct call for one local operation whose failure must immediately reach the caller. A bus can obscure control flow and complicate transactions.

## Tests and practice

Test ordering, fan-out, failure policy, duplicate delivery, and handler idempotency. Practice in the [event-driven training exercise](../exercises/event-driven-training.md).

## Related IDs

P04 (transaction), P11 (projection), P13 (workflow), P14 (observability).

