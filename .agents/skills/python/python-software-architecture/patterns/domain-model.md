# P01 — Domain Model, Entity, and Value Object

## Problem

Business rules become fragile when an application passes strings, numbers, and unvalidated dictionaries between handlers. P01 gives important concepts names and places their invariants close to the state they protect.

## Use when

- A value has domain meaning or a non-trivial invariant.
- Identity and lifecycle distinguish an entity from an interchangeable value.
- The same rule is duplicated across endpoints, jobs, and tests.

## Book theory

*Architecture Patterns with Python* (ch01) starts with a pure domain model and uses value objects and entities to express business language. Keen (ch17) contrasts rich models with anemic records. Mak (ch28, ch30) connects requirements and information hiding: a class should own the knowledge needed to protect its representation.

## Minimal standard-library implementation

~~~python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Sku:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("SKU cannot be empty")


@dataclass
class Batch:  # Entity: identity is its reference.
    reference: str
    sku: Sku
    quantity: int
    _allocations: set[str] = field(default_factory=set, init=False)

    def allocate(self, order_id: str) -> None:
        if len(self._allocations) >= self.quantity:
            raise ValueError("batch is full")
        self._allocations.add(order_id)
~~~

`Sku` is immutable and compared by value; `Batch` has identity and a lifecycle. For a single stable rule, a function plus a frozen dataclass is usually enough.

## Production evidence to inspect

Look for domain classes, constructors that reject invalid values, and tests that exercise the invariant without starting a framework. The repository dossiers identify exact paths; do not infer a domain model from class names alone.

## Production compromise

Large ML and serving systems often use Pydantic models, tensors, or configuration objects as both transport and domain data. This reduces mapping overhead but can leak serialization or framework constraints into core policy. Keep the boundary small, and use a separate value object when the invariant is important enough to test independently.

## When not to use it

Do not wrap every primitive in a class. A plain `str`, `TypedDict`, or small function is clearer when there is no identity, invariant, or domain vocabulary.

## Tests and practice

Test invalid construction, equality semantics, and the entity invariant with fast unit tests. Practice by adding `Money` and `OrderLine` value objects to the [repository/UoW exercise](../exercises/repository-uow.md).

## Related IDs

P02 (aggregate boundary), P05 (use case), P17 (testing seams).

