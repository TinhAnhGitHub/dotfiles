# Chapter 6: Unit of Work Pattern

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part I: Building an Architecture to Support Domain Modeling

## Core Idea
The Unit of Work pattern provides an atomic transactional boundary around data operations, managing repositories and ensuring all domain mutations succeed or fail together.

## Frameworks Introduced
- **Unit of Work (UoW) Pattern with Python Context Managers**:
  - When to use: When services interact with multiple repositories or require explicit transaction control (commit, rollback) decoupled from database sessions.
  - How: Implement `AbstractUnitOfWork` inheriting from Python's context manager protocol (`__enter__`, `__exit__`). Expose repositories as attributes of the UoW.
- **Explicit vs. Implicit Commit Semantics**:
  - When to use: Deciding how transactions should close.
  - How: Default to rollback on exit unless `uow.commit()` is explicitly called. Any unhandled exception causes an automatic, safe rollback.

## Key Concepts
- **Unit of Work**: Maintains a list of business objects affected by a business transaction and coordinates the writing out of changes.
- **Atomic Transaction**: An operation where either all database updates take effect or none do, preserving data consistency.
- **Context Manager Protocol**: Python's `with` statement mechanism (`__enter__` and `__exit__`) providing deterministic setup and teardown.
- **FakeUnitOfWork**: A test double implementing the UoW interface with in-memory repositories and a flag recording whether `commit()` was invoked.

## Mental Models
- **Think of the UoW as a Transaction Guardian**: The UoW opens the door to the database, hands you repositories, watches the execution, and slams the door shut (rollback) if anything goes wrong.
- **Commit as the Explicit Seal of Success**: A transaction should never commit by accident; reaching the end of the `with` block without calling `.commit()` must safely discard changes.

## Anti-patterns
- **Passing Raw Sessions to Services**: Forcing service functions to know about `session.commit()` and `session.rollback()`.
- **Multiple Uncoordinated Commits**: Committing database updates halfway through a use case, leaving partial state if a subsequent step crashes.
- **Mixing UoW with Web Lifecycles**: Tying the database transaction directly to the HTTP request lifecycle rather than the specific use case.

## Code Examples

```python
import abc
from adapters.repository import AbstractRepository, SqlAlchemyRepository, FakeRepository

class AbstractUnitOfWork(abc.ABC):
    batches: AbstractRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
```
- **What it demonstrates**: Abstract Unit of Work using Python context manager with real SQLAlchemy and fake in-memory implementations.

## Reference Tables

| Dimension | Manual Session Management | Unit of Work Pattern |
|---|---|---|
| **Service Signature** | `def do_work(repo, session)` | `def do_work(uow: AbstractUnitOfWork)` |
| **Error Handling** | Manual `try...except...session.rollback()` | Automatic via `__exit__` context manager |
| **Repository Access** | Passed separately from session | Bound to `uow.batches` |
| **Testability** | Requires mocking DB session | Clean verification via `uow.committed` flag |

## Worked Example
Refactored Service Layer using the Unit of Work:

```python
def allocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    line = OrderLine(orderid, sku, qty)
    with uow:
        batches = uow.batches.list()
        if not any(b.sku == line.sku for b in batches):
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = model_allocate(line, batches)
        uow.commit()
        return batchref
```

Unit testing the service with `FakeUnitOfWork`:
```python
def test_allocate_commits_uow():
    uow = FakeUnitOfWork()
    uow.batches.add(Batch("b1", "BLUE-VASE", 50, eta=None))
    
    batchref = allocate("o1", "BLUE-VASE", 10, uow)
    
    assert batchref == "b1"
    assert uow.committed is True
```

## Key Takeaways
1. Unit of Work encapsulates the atomic transaction boundary.
2. Context managers (`with uow:`) provide idiomatic Python syntax for database sessions.
3. Default to rolling back transactions unless `.commit()` is explicitly executed.
4. UoW groups repositories together under a single consistency lifetime.

## Connects To
- **Ch 2**: UoW creates and owns repository instances.
- **Ch 4**: Eliminates raw `session` objects from service signatures.
- **Ch 7**: Aggregates define the boundary around what a single UoW modifies.
