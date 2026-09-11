# Chapter 1: Domain Modeling

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part I: Building an Architecture to Support Domain Modeling

## Core Idea
A domain model is a mental model of business rules implemented entirely in pure Python objects without dependencies on databases, web frameworks, or third-party infrastructure.

## Frameworks Introduced
- **Domain-Driven Design (DDD) Tactical Modeling**:
  - When to use: When business rules have non-trivial logic, constraints, and state transitions that must remain independent of I/O.
  - How: Translate domain experts' ubiquitous language into pure Python classes, methods, and exceptions. Keep zero infrastructure imports in `domain/model.py`.
- **Value Object vs. Entity Distinction**:
  - When to use: When designing domain objects to model business concepts.
  - How:
    - **Value Object**: Defined entirely by its attributes; immutable. If two instances have identical attributes, they are equal.
    - **Entity**: Defined by an explicit identity (ID/reference) that persists across state and attribute mutations.

## Key Concepts
- **Ubiquitous Language**: Shared, unambiguous vocabulary agreed upon between software developers and domain business experts.
- **Entity**: A domain object with an persistent identity; equality is based strictly on identity, not attribute values.
- **Value Object**: An immutable domain concept without identity; equality is based on attribute equality.
- **Domain Service Function**: A standalone domain function modeling a business process that doesn't naturally belong inside a single entity.
- **Domain Exception**: Custom exception classes expressing business rule violations (e.g., `OutOfStock`, `InvalidSku`) rather than technical errors.
- **Pure Domain Model**: Business logic classes that have no imports from SQLAlchemy, Django, Redis, or Flask.

## Mental Models
- **Think of the Domain Model as an Engine**: The domain model is the pure mechanical engine; UI, HTTP, and databases are swappable chassis and controls.
- **Use Value Objects for Quantities and IDs, Entities for Tracked Lifecycle Items**: Use dataclasses with `frozen=True` for order lines and money; use mutable classes with reference IDs for batches and inventory.
- **Let Python Magic Methods Express Business Rules**: Implement `__eq__`, `__hash__`, and `__gt__` to make domain objects sortable and comparable using idiomatic Python operators.

## Anti-patterns
- **Anemic Domain Model**: Creating classes that are mere bags of getters and setters while business logic leaks into service functions or UI controllers.
- **Database-First Domain Design**: Coupling domain classes to ORM base classes (e.g., `class Batch(Base)`), forcing domain code to mirror relational database schemas.
- **Framework Creep in Domain**: Importing web framework helpers (`request`, `jsonify`) or persistence libraries into domain models.

## Code Examples

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional, Set

class OutOfStock(Exception):
    pass

@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self) -> int:
        return hash(self.reference)

    def __gt__(self, other: "Batch") -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
```
- **What it demonstrates**: Pure domain modeling using an Entity (`Batch`) with business rules (`allocate`, `can_allocate`), comparison magic methods, and a frozen Value Object (`OrderLine`).

## Reference Tables

| Aspect | Entity (`Batch`) | Value Object (`OrderLine`) |
|---|---|---|
| **Identity** | Persistent unique identifier (`reference`) | None; defined by data attributes |
| **Equality** | `self.reference == other.reference` | Attribute-by-attribute (`frozen=True`) |
| **Mutability** | Mutable state (`_allocations`) | Immutable |
| **Python Tool** | Standard class or `@dataclass(unsafe_hash=False)` | `@dataclass(frozen=True)` or `NamedTuple` |
| **Lifecycle** | Tracked across transitions over time | Disposable, interchangeable |

## Worked Example
Consider an allocation rule: *"Allocate orders against the earliest available batch first (in-stock batches before shipments arriving later)."*
Instead of a database query with `ORDER BY eta ASC`, we implement a pure domain function:

```python
def allocate(line: OrderLine, batches: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
```

Test execution in high-speed isolation:
```python
def test_prefers_earlier_batches():
    earliest = Batch("b1", "RETRO-CLOCK", 100, eta=date(2025, 1, 1))
    medium = Batch("b2", "RETRO-CLOCK", 100, eta=date(2025, 2, 1))
    latest = Batch("b3", "RETRO-CLOCK", 100, eta=date(2025, 3, 1))
    line = OrderLine("o1", "RETRO-CLOCK", 10)
    
    selected_ref = allocate(line, [medium, latest, earliest])
    
    assert selected_ref == "b1"
    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
```
This test runs in milliseconds without spinning up PostgreSQL, SQLite, or an API server.

## Key Takeaways
1. Keep the domain layer free of all external I/O and framework dependencies.
2. Use `@dataclass(frozen=True)` for Value Objects and regular classes with equality based on identity for Entities.
3. Express business constraints through domain methods and domain exceptions, not generic status codes or boolean flags.
4. Domain logic should be testable without database or network connections.

## Connects To
- **Ch 2**: Persisting domain entities without coupling them to tables via the Repository Pattern.
- **Ch 7**: Aggregates and consistency boundaries across multiple entities.
- **Ch 17**: Clean Architecture DDD Core in Sam Keen's model.
