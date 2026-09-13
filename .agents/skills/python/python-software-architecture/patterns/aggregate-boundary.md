# P02 — Aggregate and Consistency Boundary

## Problem

Several related objects can be individually valid while their combination is invalid. An aggregate gives one root ownership of cross-object invariants and defines what must be changed atomically.

## Use when

- A rule spans multiple records or child objects.
- Concurrent callers must not observe an invalid combination.
- Transaction scope needs a domain-level explanation.

## Book theory

Percival & Gregory (ch07) treat the aggregate root as the only entry point for mutating a consistency boundary. Keen (ch17) places invariant guards in the domain. Mak (ch29) supplies the cohesion/coupling test: keep the boundary small enough that it has one reason to change.

## Minimal standard-library implementation

~~~python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Line:
    sku: str
    quantity: int


@dataclass
class Order:  # Aggregate root.
    order_id: str
    _lines: dict[str, Line] = field(default_factory=dict, init=False)

    def add(self, sku: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        current = self._lines.get(sku)
        next_quantity = (current.quantity if current else 0) + quantity
        if next_quantity > 100:
            raise ValueError("order limit exceeded")
        self._lines[sku] = Line(sku, next_quantity)

    def lines(self) -> tuple[Line, ...]:
        return tuple(self._lines.values())
~~~

Callers receive the root, not a mutable reference to `_lines`. A repository and transaction should normally address the root, not each child independently.

## Production evidence to inspect

Verify the root’s mutation methods, locking/version checks, persistence scope, and tests for concurrent or cross-object rules. A directory named `aggregate` is not proof; record A/B evidence only when the runtime path and tests agree.

## Production compromise

Distributed systems frequently choose eventual consistency between aggregates and use events or compensating actions instead of one large transaction. This scales better, but failures become workflow states rather than immediate exceptions.

## When not to use it

Do not create a large aggregate merely because objects are related in a schema. If the rule is local, keep the objects separate; if a report is read-only, a projection is usually a better boundary.

## Tests and practice

Test every invariant through the root and test that child references cannot bypass it. Practice by adding optimistic versioning and a conflict test to the [repository/UoW exercise](../exercises/repository-uow.md).

## Related IDs

P01 (model), P04 (transaction), P10 (events), P11 (projections).

