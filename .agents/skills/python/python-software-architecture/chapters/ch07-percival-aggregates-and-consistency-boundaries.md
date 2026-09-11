# Chapter 7: Aggregates and Consistency Boundaries

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part I: Building an Architecture to Support Domain Modeling

## Core Idea
An Aggregate is a cluster of domain objects treated as a single unit for data changes, defining an unbreakable consistency boundary that protects business invariants under concurrent access.

## Frameworks Introduced
- **The Aggregate Pattern (DDD Tactical)**:
  - When to use: When business invariants span multiple related entities and must be protected against race conditions and concurrent modifications.
  - How:
    1. Select an *Aggregate Root* entity.
    2. Route all mutations to child entities exclusively through methods on the root.
    3. Allow outside code to hold references only to the aggregate root.
    4. One Repository per Aggregate Root (never create repositories for internal child entities).
- **Optimistic Concurrency Control with Version Numbers**:
  - When to use: When multiple processes may update the same aggregate simultaneously without wanting heavy database table locks.
  - How: Add a `version_number` column to the aggregate root. Increment it on every modification. When saving, execute `UPDATE ... WHERE version_number = :old_version`. If 0 rows are updated, raise a concurrency exception.

## Key Concepts
- **Invariant**: A business rule or constraint that must always be true (e.g. "allocated quantity cannot exceed total purchased quantity").
- **Consistency Boundary**: The smallest boundary within which an invariant is guaranteed to hold at all times.
- **Aggregate Root**: The single entry-point entity through which all access and modifications to the aggregate must pass.
- **Optimistic Locking**: Assuming transactions will not conflict; checking for concurrent changes at commit time via version comparison.
- **Pessimistic Locking**: Acquiring exclusive database locks (`SELECT FOR UPDATE`) to prevent concurrent access during the transaction.

## Mental Models
- **Think of an Aggregate Root as a Fortress Gatekeeper**: Outside callers cannot enter the fortress to talk directly to child entities; they speak only to the root at the gate, which enforces rules before delegating.
- **One Aggregate = One Repository = One Transaction**: Design transactions to touch only one aggregate instance at a time to ensure high scalability and minimal lock contention.

## Anti-patterns
- **God Aggregates**: Designing an aggregate that encompasses the entire system (e.g. a single `Company` or `Warehouse` aggregate), causing massive concurrency contention.
- **Bypassing the Root**: Directly querying or modifying an aggregate's child entity from outside the aggregate boundary.
- **Cross-Aggregate Transactions**: Modifying three different aggregate roots in a single Unit of Work; use eventual consistency via events instead.

## Code Examples

```python
from dataclasses import dataclass
from typing import List, Optional
from domain.model import Batch, OrderLine, OutOfStock

class Product:
    """Aggregate Root managing all Batches for a specific SKU."""
    def __init__(self, sku: str, batches: List[Batch], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            self.version_number += 1
            return batch.reference
        except StopIteration:
            raise OutOfStock(f"Out of stock for sku {self.sku}")

    def change_batch_quantity(self, ref: str, qty: int) -> None:
        batch = next(b for b in self.batches if b.reference == ref)
        batch.change_purchased_quantity(qty)
        self.version_number += 1
```
- **What it demonstrates**: `Product` acts as the Aggregate Root. Outside callers cannot allocate directly against a `Batch`; they ask `Product` to allocate, ensuring the version number increments and invariants hold.

## Reference Tables

| Concept | Entity | Aggregate Root |
|---|---|---|
| **Scope** | Single object with identity | Cluster of entities and value objects |
| **Direct Access** | Internal to aggregate | Accessible globally via Repository |
| **Repository** | Does NOT have its own repository | Exactly one repository per Aggregate Root |
| **Concurrency Boundary** | Individual state | Entire cluster locked/versioned together |

## Worked Example
Handling concurrent allocation requests using optimistic locking:

```python
# In repository or UoW commit:
def commit(self):
    for product in self.products.seen:
        res = self.session.execute(
            """
            UPDATE products 
            SET version_number = :new_version
            WHERE sku = :sku AND version_number = :old_version
            """,
            {
                "new_version": product.version_number,
                "sku": product.sku,
                "old_version": product.version_number - 1,
            }
        )
        if res.rowcount == 0:
            raise ConcurrentUpdateError(f"Concurrent update detected for sku {product.sku}")
    self.session.commit()
```
If two workers attempt to allocate the last item simultaneously, Worker 1 succeeds, increments version from 0 to 1, and commits. Worker 2's update finds 0 rows matching `version = 0` and fails safely with `ConcurrentUpdateError`, prompting a clean retry.

## Key Takeaways
1. Aggregates protect business invariants across multiple related objects.
2. Direct all modifications through the aggregate root method calls.
3. Keep repositories mapped 1:1 with aggregate roots.
4. Use version numbers for optimistic concurrency control to prevent data corruption without heavy locking.

## Connects To
- **Ch 1**: Transforms standalone `Batch` entities into a cohesive `Product` aggregate.
- **Ch 6**: Unit of Work commits aggregate state atomically.
- **Ch 8**: Aggregates raise domain events when their state changes.
