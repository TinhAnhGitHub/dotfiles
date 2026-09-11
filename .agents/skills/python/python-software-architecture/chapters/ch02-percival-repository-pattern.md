# Chapter 2: Repository Pattern

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part I: Building an Architecture to Support Domain Modeling

## Core Idea
The Repository pattern abstracts data storage behind an interface that pretends all domain objects reside in an in-memory collection, decoupling domain logic from database infrastructure.

## Frameworks Introduced
- **Abstract Repository Interface**:
  - When to use: Whenever domain models need to be loaded from or saved to persistent storage.
  - How: Define an abstract base class (`AbstractRepository`) with `add(entity)` and `get(reference)` methods. Implement a production adapter (e.g. SQLAlchemy) and an in-memory fake for testing.
- **Dependency Inversion Principle (DIP) in Data Access**:
  - When to use: To break the conventional dependency where domain code depends on the database ORM.
  - How: Classical ORM maps objects to tables by inheriting from ORM base classes (`class Model(Base)`). Inverted ORM defines the domain model first, then uses classical mapping (`mapper_registry.map_imperatively`) to connect tables to pure classes.

## Key Concepts
- **Repository**: An abstraction over persistent storage that presents an interface like an in-memory `set` or list of domain entities.
- **Port and Adapter (Hexagonal Architecture)**: The `AbstractRepository` is the *Port* (defined inside the core application); the `SqlAlchemyRepository` is an *Adapter* (defined in infrastructure).
- **FakeRepository**: An in-memory repository implementation using a Python `set` or `dict`, enabling fast, deterministic unit tests without mocking.
- **Classical / Imperative Mapping**: In SQLAlchemy, imperatively linking a pure domain class to a `Table` object without inheriting from `declarative_base()`.

## Mental Models
- **Think of the Repository as an In-Memory Collection**: If all batches lived in a Python `set()`, how would you interact with them? With `.add()` and `.get()`.
- **Ports Belong Inside, Adapters Belong Outside**: The domain layer owns the abstract port; the infrastructure layer owns the concrete database adapter.

## Anti-patterns
- **Leaking ORM Queries into Domain Logic**: Writing `db.session.query(Batch).filter(...)` directly inside domain methods or API controllers.
- **Overcomplicating the Repository Interface**: Adding arbitrary querying methods like `find_by_sku_and_eta_between()`; prefer fetching the Aggregate or using CQRS for reads.
- **Over-Mocking the Database**: Using `unittest.mock.patch` on database sessions instead of swapping in a simple `FakeRepository`.

## Code Examples

```python
import abc
from typing import Set, Optional
from domain.model import Batch

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference: str) -> Optional[Batch]:
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: Batch) -> None:
        self.session.add(batch)

    def get(self, reference: str) -> Optional[Batch]:
        return self.session.query(Batch).filter_by(reference=reference).first()

class FakeRepository(AbstractRepository):
    def __init__(self, batches: Optional[list[Batch]] = None):
        self._batches: Set[Batch] = set(batches or [])

    def add(self, batch: Batch) -> None:
        self._batches.add(batch)

    def get(self, reference: str) -> Optional[Batch]:
        return next((b for b in self._batches if b.reference == reference), None)
```
- **What it demonstrates**: Abstract port definition with concrete database adapter and in-memory test double.

## Reference Tables

| Pattern / Technique | Conventional Active Record | Repository Pattern |
|---|---|---|
| **Class Inheritance** | Inherits from ORM Base | Pure Python class (POPO) |
| **Testability** | Requires running database or complex mocking | Trivial via `FakeRepository` |
| **Dependency Arrow** | Domain -> Database ORM | Infrastructure -> Domain (Inverted) |
| **Primary Interface** | `Model.save()`, `Model.objects.filter()` | `repo.add(entity)`, `repo.get(id)` |

## Worked Example
Testing an allocation service without touching PostgreSQL:

```python
def test_repository_can_save_and_retrieve_batch():
    repo = FakeRepository()
    batch = Batch("b-001", "RED-CHAIR", qty=20, eta=None)
    repo.add(batch)
    
    retrieved = repo.get("b-001")
    assert retrieved == batch
    assert retrieved.available_quantity == 20
```
This test runs in microsecond speed and guarantees that any service relying on `AbstractRepository` can be verified without database migrations.

## Key Takeaways
1. The Repository pattern isolates domain models from persistence details.
2. Keep the repository interface simple: `add()` and `get()` are the essential methods.
3. Invert ORM dependencies: map database tables to existing domain classes imperatively.
4. `FakeRepository` eliminates the need for brittle, mock-heavy unit tests.

## Connects To
- **Ch 1**: Provides persistence for pure domain models.
- **Ch 4**: Service layer uses repositories to execute use cases.
- **Ch 6**: Unit of Work manages repository instances across database transactions.
