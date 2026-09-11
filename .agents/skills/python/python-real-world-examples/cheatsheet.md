# Real-World Python Patterns Cheatsheet

Quick-reference guide for identifying, comparing, and applying architectural and design patterns derived from production open-source Python codebases.

---

## 1. Pattern-to-Repository Matrix

| Pattern Category | Pattern Name | Key Problem Solved | Key Seams / Mechanics | Sister Skill Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Macro (DDD)** | **Repository & UoW** | Decouple persistence from domain logic | Abstract protocol `Protocol`, DB session context manager | [`python-software-architecture`](../python-software-architecture/SKILL.md) |
| **Macro (DDD)** | **Aggregate Root** | Maintain transactional consistency invariants | Entity enforcing business rules on child objects | [`python-software-architecture`](../python-software-architecture/SKILL.md) |
| **Macro (Clean)** | **Use Case Interactor** | Isolate single business workflow from delivery | Input DTO $\rightarrow$ Interactor $\rightarrow$ Output Port | [`python-software-architecture`](../python-software-architecture/SKILL.md) |
| **Macro (Clean)** | **Anti-Corruption Layer**| Protect new domain from legacy/external models | Translating adapter between two distinct domain models | [`python-software-architecture`](../python-software-architecture/SKILL.md) |
| **Macro (Events)**| **In-Memory Message Bus**| Decouple side effects (emails, notifications) | Handler dictionary: `dict[type[Event], list[Callable]]` | [`python-software-architecture`](../python-software-architecture/SKILL.md) |
| **Meso (GoF)** | **Command Registry** | Decouple dispatch without nested `if/elif` | Dict/decorator mapping: `@registry.register(name)` | [`python-design-patterns`](../python-design-patterns/SKILL.md) |
| **Meso (GoF)** | **Strategy / Policy** | Swap execution algorithms dynamically | Structural `@runtime_checkable` `Protocol` | [`python-design-patterns`](../python-design-patterns/SKILL.md) |
| **Meso (GoF)** | **Adapter / Gateway** | Bridge incompatible third-party interfaces | Wrapper class adhering to internal port protocol | [`python-design-patterns`](../python-design-patterns/SKILL.md) |
| **Meso (DI)** | **Composition Root** | Centralize application dependency graph wiring | Single bootstrap module (Dishka container or manual factory) | [`python-design-patterns`](../python-design-patterns/SKILL.md) |
| **Micro (Idioms)**| **Protocol Seams** | Duck typing with static type checker safety | `typing.Protocol` with method signatures | [`python-clean-code`](../python-clean-code/SKILL.md) |
| **Micro (Idioms)**| **Resource Lifecycle** | Guarantee deterministic cleanup of sockets/pools | `@contextmanager` generator with `try ... finally` | [`python-clean-code`](../python-clean-code/SKILL.md) |
| **Micro (Idioms)**| **Sentinel Objects** | Distinguish between missing, unset, and `None` | `MISSING = object()` or singleton enum | [`python-clean-code`](../python-clean-code/SKILL.md) |

---

## 2. Real-World Architectural Archetypes

### Archetype A: The Strict Clean Onion (Enterprise / Core Service)
- **Characteristics**: Pure Python core (entities, value objects) with zero third-party dependencies. Distinct `domain`, `application`, `adapters`, and `entrypoints` packages.
- **When to Choose**: Long-lived core systems, multi-delivery requirements (CLI + HTTP + Worker), high unit-test speed imperative.
- **Trade-off**: Additional boilerplate mapping between DTOs, domain models, and ORM schemas.

### Archetype B: The Pragmatic Hexagonal Monolith (High-Velocity Product)
- **Characteristics**: Domain logic uses Pydantic or dataclasses; repositories wrap SQLAlchemy sessions; handlers/services act directly as use-case boundaries.
- **When to Choose**: Fast-evolving SaaS products where extreme isolation overhead is prohibitive, but testability and clean database decoupling are required.
- **Trade-off**: Minimal framework leakage at boundaries in exchange for 3x faster initial velocity.

### Archetype C: The Plugin-Driven Microkernel (CLI / Extensible Tools)
- **Characteristics**: Minimal core runner with dynamic registration of commands, middlewares, and drivers.
- **When to Choose**: Developer tools, ETL engines, CLI suites, or applications with community plugins.
- **Trade-off**: Requires strict interface versioning and plugin compatibility checks.

---

## 3. Real-World Tells & Smells

| Tell / Smell | Real-World Observation | Pragmatic Fix |
| :--- | :--- | :--- |
| **ORM Leaking to Domain** | Domain entities inherit from `Base` (SQLAlchemy) or `models.Model` (Django) | Use Imperative Mapping (`sqlalchemy.orm.registry.map_imperatively`) or Dataclass domain models with repository translators. |
| **Web Framework in Use Cases** | `fastapi.Request`, `flask.g`, or `HTTPException` imported in service layer | Translate HTTP parameters into pure DTOs in controllers; throw domain exceptions (`DomainNotFoundException`) and catch them in custom exception handlers. |
| **Scattered Business Invariants** | Validation checks duplicated across route handlers and UI forms | Encapsulate invariant validation directly in Aggregate Root methods or Value Object constructors. |
| **Mock Hell in Tests** | Unit tests requiring 10+ `@patch` decorators for DB/APIs | Switch to Fake-First testing: define ports as `Protocol` and maintain in-memory `FakeRepository` implementations. |
| **God Service Layer** | Single `Service` class with 40+ methods and hundreds of injected dependencies | Decompose into granular Use Case Interactors (single `execute()` or `__call__()` method per use case). |

---

## 4. How to Ingest a New Project

When adding a new open-source repository to this skill:
1. Copy `templates/project-case-study.md` into `projects/<project-name>.md`.
2. Inspect directory structure and dependency flow with `find` and `grep`.
3. Check domain purity: check imports inside domain models.
4. Locate the composition root: find where DB connections, external clients, and services are instantiated.
5. Identify 2-3 prominent design patterns (Registries, Adapters, Pipelines).
6. Document realistic trade-offs and extract 3 curated code tours.
7. Update this cheatsheet and `SKILL.md`.
