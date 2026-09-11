# Software Architecture & Design Cheatsheet

A practitioner's quick-reference decision aid, rules of thumb, and diagnostic smells across DDD, Clean Architecture, and GoF patterns.

## 1. Architectural Decision Rules

- **When business rules have complex invariants**, use a **Pure Domain Model with Aggregates** (Ch 01, Ch 07).
- **When data persistence or ORM leaks into business logic**, introduce the **Repository Pattern** with an imperative mapper (Ch 02, Ch 20).
- **When multiple repositories must participate in a single atomic transaction**, use the **Unit of Work Pattern** with a context manager (Ch 06).
- **When a service function triggers secondary side-effects (email, search sync)**, publish **Domain Events to a Message Bus** (Ch 08, Ch 09).
- **When read queries require complex joins that strain domain aggregates**, apply **CQRS** and query raw SQL or denormalized views directly (Ch 12).
- **When algorithms vary at runtime or need testing in isolation**, prefer the **Strategy Pattern** over Template Method (Ch 33).
- **When an entity contains sprawling `if self.state == ...` conditionals**, refactor to the **State Pattern** (Ch 38).
- **When refactoring a legacy monolith**, use the **Strangler Fig Pattern** with an **Anti-Corruption Layer** (Ch 24).

---

## 2. The 4-Layer Clean Architecture Ladder

```
[ Outer: Frameworks & Drivers ] -> FastAPI, SQLAlchemy, Click, Redis, Postgres
           │ (depends inward)
           ▼
[ Interface Adapters ]           -> Controllers, Presenters, ViewModels, Gateways
           │ (depends inward)
           ▼
[ Application Business Rules ]  -> Use Case Interactors, Input/Output Ports, DTOs
           │ (depends inward)
           ▼
[ Center: Enterprise Domain ]    -> Entities, Value Objects, Domain Exceptions
```

**The Dependency Invariant**: Inner layers NEVER import from outer layers.
- If `domain/model.py` imports `fastapi` or `sqlalchemy` -> **Architecture Violation!**

---

## 3. Trade-Off Matrices

### Concurrency Control
| Approach | Contention Level | Implementation Tool | Best For |
|---|---|---|---|
| **Optimistic Locking** | Low to Medium | `version_number` on Aggregate Root | High throughput, web applications |
| **Pessimistic Locking** | High | `SELECT FOR UPDATE` | Financial transactions, zero-retry tolerance |

### Testing Doubles
| Double Type | Realism | Setup Cost | When to Use |
|---|---|---|---|
| **In-Memory Fake** | High (realistic state) | Moderate (written once) | Default for repositories & storage ports |
| **Mock (`unittest.mock`)**| Low (scripted returns) | Low per test | Verification of external calls (e.g. SMTP) |

### Creational Alternatives
| Need | Recommended Pattern | Python Idiom |
|---|---|---|
| Single instance globally | Python Module | Import singleton instance from module |
| Dynamic class selection | Registry Factory | Dictionary mapping strings to callables |
| Family of matching objects | Abstract Factory | Class implementing abstract creation port |

---

## 4. Tells, Smells & Fast Heuristics

| Code Smell | Underlying Architectural Defect | Prescribed Remedy |
|---|---|---|
| **Fat Controller** (> 30 lines) | Web handler doing business orchestration | Extract into a Use Case Interactor (Ch 18) |
| **Anemic Domain Entity** (all data, no rules) | Business logic leaking into services | Move methods and validations into Entity (Ch 01) |
| **Shotgun Surgery** (1 change touches 10 files)| Leaking changes, tight coupling | Apply Information Hiding & Encapsulation (Ch 26, Ch 30) |
| **Train Wreck** (`a.b().c().d()`) | Violates Law of Demeter | Provide shortcut method on root object (Ch 29) |
| **Feature Envy** (Method uses other class data)| Misplaced responsibility | Move method to the class owning the data (Ch 29) |
| **Mocking Hell** (15 patch calls per test) | Architecture coupled to implementation details| Shift to High Gear TDD using Fakes (Ch 05, Ch 21) |
| **Lapsed Listener** (Memory leak in subscribers)| Unmanaged Observer references | Use `weakref.WeakSet()` for subscriptions (Ch 37) |\n