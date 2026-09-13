# P11 — CQRS and Read Projections

## Problem

The model that protects write invariants is often a poor shape for dashboards, search, or high-volume reads. P11 separates command/write behavior from query read models and accepts the consistency cost explicitly.

## Use when

- Read and write workloads scale differently.
- A read view needs denormalization or a different index.
- Projections can be rebuilt from durable facts.

## Book theory

Percival ch12 separates rich write models from direct read queries and denormalized projections. Keen ch18 places use cases and ports around the boundary. The design is a scaling/complexity choice, not a mandatory layer.

## Minimal standard-library implementation

~~~python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderPlaced:
    order_id: str
    customer: str


class OrderWriteModel:
    def __init__(self) -> None:
        self._orders: set[str] = set()

    def place(self, event: OrderPlaced) -> None:
        if event.order_id in self._orders:
            raise ValueError("duplicate order")
        self._orders.add(event.order_id)


class OrderReadProjection:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, str]] = {}

    def apply(self, event: OrderPlaced) -> None:
        self.rows[event.order_id] = {
            "customer": event.customer,
            "status": "placed",
        }

    def for_customer(self, customer: str) -> list[dict[str, str]]:
        return [row for row in self.rows.values() if row["customer"] == customer]
~~~

In production, projection updates may be asynchronous. Document freshness, rebuild, schema migration, and duplicate-event behavior.

## Production evidence to inspect

Find separate write/query paths, projection updates, source-of-truth ownership, and tests for eventual consistency or rebuild. Do not label every read helper CQRS.

## Production compromise

Projects often begin with one model and introduce a specialized read path only for a proven bottleneck. Some projections are in-memory or cache-backed and can be recomputed; others require durable checkpoints and versioned schemas.

## When not to use it

Avoid CQRS when read/write scale and shape are similar or when eventual consistency would violate the user-facing contract. Two models double migrations and observability work.

## Tests and practice

Test command invariants, projection application, replay/rebuild, stale reads, and idempotency. Use the [event-driven training exercise](../exercises/event-driven-training.md).

## Related IDs

P02 (boundary), P04 (transaction), P10 (events), P13 (workflow).

