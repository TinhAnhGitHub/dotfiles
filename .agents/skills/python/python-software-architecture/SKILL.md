---
name: python-software-architecture
description: "Comprehensive software architecture and design engineering knowledge base synthesized from 'Architecture Patterns with Python' (Percival & Gregory), 'Clean Architecture with Python' (Sam Keen), and 'Software Design for Python Programmers' (Ronald Mak). Use when designing scalable Python systems, applying DDD, Clean Architecture, SOLID, and GoF design patterns, decomposing monolithic applications, refactoring legacy code, and establishing architectural test boundaries."
---

<!-- argument-hint: [topic, pattern name, or chapter number] -->

# Python Software Architecture & Design Patterns

**Authors**: Harry Percival & Bob Gregory (O'Reilly), Sam Keen (Packt), Ronald Mak (Manning)  
**Total Volumes**: 3 | **Total Chapters**: 41 | **Generated**: 2026-09-12

## Agent Instructions & Conversational Workflows

You are an expert Python software architect. You MUST follow these workflows when answering user requests:
- **IF user asks about monolithic decay or legacy migration**: You MUST read `chapters/ch24-keen-legacy-to-clean-refactoring.md` before responding.
- **IF user asks about decoupling DB logic**: You MUST read `chapters/ch02-percival-repository-pattern.md` and propose the Repository pattern.
- **IF user asks about cross-entity rules**: You MUST read `chapters/ch07-percival-aggregates-and-consistency-boundaries.md` and propose Aggregates.

## Strict Constraints (MUST / NEVER)
- **NEVER** allow Domain models (Layer 1) to import from Frameworks (Layer 4) or Adapters (Layer 3).
- **ALWAYS** enforce the Inward Dependency Rule.
- **ALWAYS** use Context Managers (`with` blocks) when proposing a Unit of Work.

## Output Format Requirements
When proposing a system architecture, your response MUST include:
1. **A Textual Diagram** (ASCII or Mermaid) visualizing the architecture.
2. **Layer Mapping**: Explicitly map components to the 4 Clean Architecture layers (Domain, Application, Adapters, Frameworks).
3. **Trade-off Analysis**: At least one drawback or complexity introduced by the architecture.

### The 4-Pillar Python Architecture & Craftsmanship Hierarchy

This skill operates as the macro-architectural tier of the Python design ecosystem:
- [python-clean-code](../python-clean-code/SKILL.md) (**Micro Level**): Fine-grained implementation idioms,
  typing protocols, closures, decorators, generators, fail-fast guard clauses, and sentinels.
- [python-design-patterns](../python-design-patterns/SKILL.md) (**Meso Level**): Component-level tactical
  patterns (Strategy, Factory, Registry, State, Adapter, Façade) and modern DI with Dishka.
- **`python-software-architecture`** (**Macro Level — This Skill**): Whole-system architecture: Clean
  Architecture (Onion) 4-layer ladder, Domain-Driven Design (Aggregates, Invariants), Unit of Work transactions,
  Message Bus orchestration, CQRS, and Event-Driven Microservices.
- [python-real-world-examples](../python-real-world-examples/SKILL.md) (**Reference Layer**): Applied open-source
  case studies demonstrating these patterns in battle-tested production repositories.

---

## Core Frameworks & Mental Models

### 1. The Unified 4-Layer Architecture Ladder
Clean Architecture organizes Python systems into four concentric circles where dependencies strictly point inward:

```
[ Frameworks & Drivers ]  ──► FastAPI, SQLAlchemy, Click, Celery, Redis, Postgres
           │
           ▼
[ Interface Adapters ]    ──► Controllers, Presenters, ViewModels, Gateways, DTO Mappers
           │
           ▼
[ Application Layer ]     ──► Use Case Interactors, Input/Output Ports, Message Bus Handlers
           │
           ▼
[ Enterprise Domain ]     ──► Aggregates, Entities, Value Objects, Domain Exceptions
```

- **Enterprise Domain (Center)**: Zero dependencies. Implemented in pure Python dataclasses and standard classes. Expresses ubiquitous business language and protects invariants.
- **Application Layer**: Orchestrates use case workflows. Accepts Request DTOs, coordinates domain aggregates and persistence ports, and returns Response DTOs.
- **Interface Adapters**: Translates data between external formats (HTTP JSON, SQL rows, terminal flags) and application DTOs.
- **Frameworks & Drivers (Perimeter)**: Ephemeral plugins. Databases, web frameworks, and cloud SDKs adapt to the application, never the reverse.

### 2. Tactical Domain-Driven Design (DDD)
- **Entities vs Value Objects**: Entities possess unique identity and lifecycles (`Batch`, `BankAccount`); Value Objects are immutable descriptors defined by attributes (`OrderLine`, `Money`).
- **Aggregate Root**: Enforces consistency boundaries. Outside callers hold references only to the root. One repository per aggregate root.
- **Unit of Work (UoW)**: Manages atomic database transactions using Python context managers (`with uow:`). Guarantees commit/rollback semantics across repositories.

### 3. Asynchronous & Event-Driven Decoupling
- **Commands vs. Events**: Commands (`Allocate`) express intent, have exactly one recipient, and fail loudly. Events (`Allocated`, `OutOfStock`) express past facts, broadcast to 0..N handlers, and decouple secondary side effects.
- **Internal Message Bus**: Enqueues and dispatches event chains, standardizing use cases into uniform message handlers.
- **CQRS**: Separates write operations (rich domain aggregates enforcing rules) from read operations (direct raw SQL queries returning flat dictionaries).

### 4. Gang of Four (GoF) Patterns in Modern Python
- **Creational**: Factory Method and Abstract Factory encapsulate object instantiation. In Python, module singletons and dictionary registries provide lightweight alternatives.
- **Structural**: Adapter bridges incompatible third-party interfaces; Façade provides high-level simplifications for noisy subsystems; Composite models part-whole trees; Decorator adds runtime behavior dynamically.
- **Behavioral**: Strategy decouples interchangeable algorithms via composition or first-class callables; State encapsulates finite state machines into polymorphic classes; Observer establishes reactive subscriptions; Visitor separates operations from tree structures.

---

## Unified Decision Matrix

| Architectural Challenge | Recommended Solution | Chapters |
|---|---|---|
| Invariants spanning multiple entities | Aggregate Root + Optimistic Concurrency | [ch07](chapters/ch07-percival-aggregates-and-consistency-boundaries.md), [ch17](chapters/ch17-keen-domain-driven-design-core.md) |
| Decoupling business logic from database | Repository Pattern + Imperative Mapping | [ch02](chapters/ch02-percival-repository-pattern.md), [ch20](chapters/ch20-keen-frameworks-and-drivers.md) |
| Managing atomic multi-repo transactions | Unit of Work Pattern with Context Manager | [ch06](chapters/ch06-percival-unit-of-work-pattern.md) |
| Decoupling side effects (email, alerts)| Domain Events + Internal Message Bus | [ch08](chapters/ch08-percival-events-and-the-message-bus.md), [ch09](chapters/ch09-percival-going-to-town-on-the-message-bus.md) |
| Complex, slow reporting queries | CQRS (Separate Read and Write Models) | [ch12](chapters/ch12-percival-cqrs.md) |
| Slow, fragile test suites | Shift to High Gear TDD with Fakes | [ch05](chapters/ch05-percival-tdd-in-high-gear-and-low-gear.md), [ch21](chapters/ch21-keen-clean-testing-patterns.md) |
| Formatting data for multiple clients | Presenter Pattern + ViewModels | [ch19](chapters/ch19-keen-interface-adapters-controllers-presenters.md), [ch22](chapters/ch22-keen-web-ui-interface-flexibility.md) |
| Telemetry without polluting domain | Boundary Instrumentation Decorators | [ch23](chapters/ch23-keen-observability-monitoring.md), [ch39](chapters/ch39-mak-singleton-composite-decorator.md) |
| Refactoring legacy monoliths | Strangler Fig + Anti-Corruption Layer | [ch24](chapters/ch24-keen-legacy-to-clean-refactoring.md), [ch35](chapters/ch35-mak-adapter-and-facade.md) |
| Sprawling algorithm `if/elif` switches | Strategy Pattern with Protocols/Callables | [ch33](chapters/ch33-mak-template-method-and-strategy.md) |
| State-dependent object behavior | State Pattern (Polymorphic FSM) | [ch38](chapters/ch38-mak-state-pattern.md) |
| Tree hierarchy uniform traversal | Composite + Iterator / Visitor | [ch36](chapters/ch36-mak-iterator-and-visitor.md), [ch39](chapters/ch39-mak-singleton-composite-decorator.md) |

---

## Chapter Index

### Part I: Architecture Patterns with Python (Percival & Gregory)
| # | Title | Key Frameworks & Patterns |
|---|---|---|
| [ch01](chapters/ch01-percival-domain-modeling.md) | Domain Modeling | Value Objects vs Entities, Pure Domain Models |
| [ch02](chapters/ch02-percival-repository-pattern.md) | Repository Pattern | AbstractRepository, FakeRepository, DIP in Data Access |
| [ch03](chapters/ch03-percival-coupling-and-abstractions.md) | Coupling and Abstractions | Abstraction Choice Framework, Fakes vs Mocks |
| [ch04](chapters/ch04-percival-flask-api-and-service-layer.md) | Service Layer & Flask API | Service Layer Pattern, Thin Controllers |
| [ch05](chapters/ch05-percival-tdd-in-high-gear-and-low-gear.md) | TDD in High and Low Gear | Gear-Shifting Framework, Test Pyramid Calibration |
| [ch06](chapters/ch06-percival-unit-of-work-pattern.md) | Unit of Work Pattern | Context Manager UoW, Atomic Transaction Boundaries |
| [ch07](chapters/ch07-percival-aggregates-and-consistency-boundaries.md) | Aggregates & Boundaries | Aggregate Root, Invariants, Optimistic Versioning |
| [ch08](chapters/ch08-percival-events-and-the-message-bus.md) | Events & Message Bus | Domain Events, Side Effect Decoupling, In-Memory Bus |
| [ch09](chapters/ch09-percival-going-to-town-on-the-message-bus.md) | Expanding the Message Bus | Event Loops, Cascading Event Queues, Reallocation |
| [ch10](chapters/ch10-percival-commands-and-command-handler.md) | Commands & Command Handlers | Command-Event Dichotomy, Dual Dispatch Bus |
| [ch11](chapters/ch11-percival-event-driven-microservices.md) | Event-Driven Microservices | External Integration Events, Redis/Broker Adapters |
| [ch12](chapters/ch12-percival-cqrs.md) | CQRS | Read vs Write Models, Denormalized Projections |
| [ch13](chapters/ch13-percival-dependency-injection-and-bootstrapping.md) | Dependency Injection & Bootstrap | Composition Root, Manual DI with Partials |

### Part II: Clean Architecture with Python (Sam Keen)
| # | Title | Key Frameworks & Patterns |
|---|---|---|
| [ch14](chapters/ch14-keen-clean-architecture-essentials.md) | Clean Architecture Essentials | Onion Architecture, The Inward Dependency Rule |
| [ch15](chapters/ch15-keen-solid-foundations-in-python.md) | SOLID Foundations | Modern SOLID in Python, Segregated Protocols |
| [ch16](chapters/ch16-keen-type-enhanced-python.md) | Type-Enhanced Python | Typing Spectrum, Protocols vs ABCs, Pydantic Borders |
| [ch17](chapters/ch17-keen-domain-driven-design-core.md) | DDD Business Logic Core | Rich vs Anemic Domain Models, Invariant Guards |
| [ch18](chapters/ch18-keen-application-layer-use-cases.md) | Application Layer Use Cases | Use Case Interactors, Input/Output Ports, DTOs |
| [ch19](chapters/ch19-keen-interface-adapters-controllers-presenters.md) | Interface Adapters | Presenter Pattern, ViewModels, Gateways |
| [ch20](chapters/ch20-keen-frameworks-and-drivers.md) | Frameworks & Drivers Layer | Plugin Architecture, ORM Isolation, CLI Drivers |
| [ch21](chapters/ch21-keen-clean-testing-patterns.md) | Clean Testing Patterns | Clean Test Pyramid, Fake-First Port Testing |
| [ch22](chapters/ch22-keen-web-ui-interface-flexibility.md) | Web UI Interface Flexibility | Multi-Delivery Interfaces, SSR vs REST Sharing |
| [ch23](chapters/ch23-keen-observability-monitoring.md) | Observability & Monitoring | Boundary Telemetry Pattern, Clean Logging Decorators |
| [ch24](chapters/ch24-keen-legacy-to-clean-refactoring.md) | Legacy to Clean Refactoring | Strangler Fig Pattern, Anti-Corruption Layer (ACL) |
| [ch25](chapters/ch25-keen-clean-architecture-journey.md) | Clean Architecture Journey | Contextual Architecture, Architecture Fitness Tests |

### Part III: Software Design for Python Programmers (Ronald Mak)
| # | Title | Key Frameworks & Patterns |
|---|---|---|
| [ch26](chapters/ch26-mak-path-to-well-designed-software.md) | Path to Well-Designed Software | Design Evaluation Framework, Leaking Changes Check |
| [ch27](chapters/ch27-mak-iterate-to-achieve-good-design.md) | Iterate to Achieve Good Design | Three-Phase Cycle (Work, Right, Fast), Spikes |
| [ch28](chapters/ch28-mak-requirements-engineering.md) | Requirements Engineering | Noun-Verb Translation, User Story Mapping |
| [ch29](chapters/ch29-mak-good-class-design.md) | Good Class Design | CRC Cards, Cohesion-Coupling Matrix, Demeter |
| [ch30](chapters/ch30-mak-encapsulation-information-hiding.md) | Information Hiding | Parnas Encapsulation, Defensive Copies, Properties |
| [ch31](chapters/ch31-mak-principle-of-least-astonishment.md) | Don't Surprise Your Users | POLA Audit Checklist, Pythonic Idioms, Magic Methods |
| [ch32](chapters/ch32-mak-subclass-design-inheritance.md) | Design Subclasses Right | Liskov Substitution (LSP), Favor Composition |
| [ch33](chapters/ch33-mak-template-method-and-strategy.md) | Template Method & Strategy | Algorithm Variance, Inheritance vs Composition |
| [ch34](chapters/ch34-mak-factory-method-and-abstract-factory.md) | Factory Patterns | Creational Encapsulation, Product Families, Registries |
| [ch35](chapters/ch35-mak-adapter-and-facade.md) | Adapter & Façade | Interface Mismatch Translation, Subsystem Façade |
| [ch36](chapters/ch36-mak-iterator-and-visitor.md) | Iterator & Visitor | Python Iterator Protocol, AST Double Dispatch |
| [ch37](chapters/ch37-mak-observer-pattern.md) | Observer Pattern | Subject-Observer Pub/Sub, Push vs Pull Models |
| [ch38](chapters/ch38-mak-state-pattern.md) | State Pattern | Finite State Machines, Polymorphic State Classes |
| [ch39](chapters/ch39-mak-singleton-composite-decorator.md) | Singleton, Composite, Decorator | Module Singletons, Part-Whole Trees, Dynamic Wrappers |
| [ch40](chapters/ch40-mak-recursion-and-backtracking-design.md) | Recursion & Backtracking | Recursive Decomposition, Backtracking Template, Pruning |
| [ch41](chapters/ch41-mak-multithreaded-program-design.md) | Multithreaded Program Design | Thread Synchronization, Producer-Consumer Queues |

---

## Topic Index

- **Abstract Factory** → [ch34](chapters/ch34-mak-factory-method-and-abstract-factory.md)
- **Adapter Pattern** → [ch02](chapters/ch02-percival-repository-pattern.md), [ch19](chapters/ch19-keen-interface-adapters-controllers-presenters.md), [ch35](chapters/ch35-mak-adapter-and-facade.md)
- **Aggregates & Aggregate Roots** → [ch07](chapters/ch07-percival-aggregates-and-consistency-boundaries.md), [ch17](chapters/ch17-keen-domain-driven-design-core.md)
- **Anti-Corruption Layer (ACL)** → [ch24](chapters/ch24-keen-legacy-to-clean-refactoring.md), [ch35](chapters/ch35-mak-adapter-and-facade.md)
- **Application Layer (Use Cases)** → [ch04](chapters/ch04-percival-flask-api-and-service-layer.md), [ch18](chapters/ch18-keen-application-layer-use-cases.md)
- **Backtracking & Recursion** → [ch40](chapters/ch40-mak-recursion-and-backtracking-design.md)
- **Bootstrapping / Composition Root** → [ch13](chapters/ch13-percival-dependency-injection-and-bootstrapping.md), [ch20](chapters/ch20-keen-frameworks-and-drivers.md)
- **Clean Architecture Fundamentals** → [ch14](chapters/ch14-keen-clean-architecture-essentials.md), [ch25](chapters/ch25-keen-clean-architecture-journey.md)
- **Commands vs. Events** → [ch10](chapters/ch10-percival-commands-and-command-handler.md)
- **Composite Pattern** → [ch39](chapters/ch39-mak-singleton-composite-decorator.md)
- **Concurrency & Multithreading** → [ch07](chapters/ch07-percival-aggregates-and-consistency-boundaries.md), [ch41](chapters/ch41-mak-multithreaded-program-design.md)
- **CQRS (Command-Query Segregation)** → [ch12](chapters/ch12-percival-cqrs.md)
- **CRC Cards** → [ch29](chapters/ch29-mak-good-class-design.md)
- **Decorator Pattern** → [ch23](chapters/ch23-keen-observability-monitoring.md), [ch39](chapters/ch39-mak-singleton-composite-decorator.md)
- **Dependency Inversion Principle (DIP)** → [ch02](chapters/ch02-percival-repository-pattern.md), [ch14](chapters/ch14-keen-clean-architecture-essentials.md), [ch15](chapters/ch15-keen-solid-foundations-in-python.md)
- **Domain Events** → [ch08](chapters/ch08-percival-events-and-the-message-bus.md), [ch09](chapters/ch09-percival-going-to-town-on-the-message-bus.md), [ch11](chapters/ch11-percival-event-driven-microservices.md)
- **Domain Modeling** → [ch01](chapters/ch01-percival-domain-modeling.md), [ch17](chapters/ch17-keen-domain-driven-design-core.md), [ch28](chapters/ch28-mak-requirements-engineering.md)
- **Entities & Value Objects** → [ch01](chapters/ch01-percival-domain-modeling.md), [ch17](chapters/ch17-keen-domain-driven-design-core.md)
- **Façade Pattern** → [ch35](chapters/ch35-mak-adapter-and-facade.md)
- **Factory Method** → [ch34](chapters/ch34-mak-factory-method-and-abstract-factory.md)
- **Information Hiding & Encapsulation** → [ch30](chapters/ch30-mak-encapsulation-information-hiding.md)
- **Iterator Pattern** → [ch36](chapters/ch36-mak-iterator-and-visitor.md)
- **Liskov Substitution Principle (LSP)** → [ch15](chapters/ch15-keen-solid-foundations-in-python.md), [ch32](chapters/ch32-mak-subclass-design-inheritance.md)
- **Message Bus** → [ch08](chapters/ch08-percival-events-and-the-message-bus.md), [ch09](chapters/ch09-percival-going-to-town-on-the-message-bus.md), [ch10](chapters/ch10-percival-commands-and-command-handler.md)
- **Microservices Integration** → [ch11](chapters/ch11-percival-event-driven-microservices.md), [ch24](chapters/ch24-keen-legacy-to-clean-refactoring.md)
- **Observability & Logging** → [ch23](chapters/ch23-keen-observability-monitoring.md)
- **Observer Pattern** → [ch37](chapters/ch37-mak-observer-pattern.md)
- **Optimistic Concurrency Control** → [ch07](chapters/ch07-percival-aggregates-and-consistency-boundaries.md)
- **Ports & Adapters** → [ch02](chapters/ch02-percival-repository-pattern.md), [ch18](chapters/ch18-keen-application-layer-use-cases.md), [ch20](chapters/ch20-keen-frameworks-and-drivers.md)
- **Presenter & ViewModel** → [ch19](chapters/ch19-keen-interface-adapters-controllers-presenters.md), [ch22](chapters/ch22-keen-web-ui-interface-flexibility.md)
- **Principle of Least Astonishment (POLA)** → [ch31](chapters/ch31-mak-principle-of-least-astonishment.md)
- **Repository Pattern** → [ch02](chapters/ch02-percival-repository-pattern.md), [ch06](chapters/ch06-percival-unit-of-work-pattern.md), [ch20](chapters/ch20-keen-frameworks-and-drivers.md)
- **Single Responsibility Principle (SRP)** → [ch08](chapters/ch08-percival-events-and-the-message-bus.md), [ch15](chapters/ch15-keen-solid-foundations-in-python.md), [ch29](chapters/ch29-mak-good-class-design.md)
- **SOLID Principles** → [ch15](chapters/ch15-keen-solid-foundations-in-python.md), [ch32](chapters/ch32-mak-subclass-design-inheritance.md)
- **State Pattern** → [ch38](chapters/ch38-mak-state-pattern.md)
- **Strangler Fig Pattern** → [ch24](chapters/ch24-keen-legacy-to-clean-refactoring.md)
- **Strategy Pattern** → [ch33](chapters/ch33-mak-template-method-and-strategy.md)
- **TDD (High Gear / Low Gear)** → [ch05](chapters/ch05-percival-tdd-in-high-gear-and-low-gear.md), [ch21](chapters/ch21-keen-clean-testing-patterns.md)
- **Template Method** → [ch33](chapters/ch33-mak-template-method-and-strategy.md)
- **Type-Enhanced Python & Protocols** → [ch16](chapters/ch16-keen-type-enhanced-python.md)
- **Unit of Work (UoW)** → [ch06](chapters/ch06-percival-unit-of-work-pattern.md), [ch13](chapters/ch13-percival-dependency-injection-and-bootstrapping.md)
- **Visitor Pattern** → [ch36](chapters/ch36-mak-iterator-and-visitor.md)

---

## Supporting Files

- [glossary.md](glossary.md) — Comprehensive alphabetical glossary of terms across DDD, Clean Architecture, and GoF.
- [patterns.md](patterns.md) — Catalog of design patterns with When to use, How, and Trade-offs.
- [cheatsheet.md](cheatsheet.md) — Quick reference tables, architectural decision rules, and code smells.

### Sister Skills in the Python Hierarchy
- [python-clean-code](../python-clean-code/SKILL.md) — Micro-level implementation idioms, typing protocols, closures, decorators, generators, fail-fast guard clauses, and sentinels.
- [python-design-patterns](../python-design-patterns/SKILL.md) — Meso-level tactical design patterns (Strategy, Factory, Registry, State, Adapter, Façade) and modern DI with Dishka.
- [python-real-world-examples](../python-real-world-examples/SKILL.md) — Reference layer providing real-world open-source case studies and code tours demonstrating these patterns in production.

---

## Scope & Limits

This skill synthesizes principles and patterns from the three authoritative texts on Python software architecture. For framework-specific documentation (FastAPI, SQLAlchemy, Pydantic, Django), refer to their respective official manuals or child skills.\n

## Canonical OSS architecture research

The applied architecture catalog uses stable IDs P01–P17. Start with the
[selection guide](references/architecture-selection-guide.md), then read the
[book-pattern matrix](references/book-pattern-matrix.md) and the relevant
[repository pattern matrix](references/repository-pattern-matrix.md).

Canonical pages are grouped under [patterns/](patterns/) and practice tasks under
[exercises/](exercises/). The real-world skill owns the repository dossiers; this
skill owns the theory, decisions, and book crosswalk. Do not create a second
definition of a canonical pattern in a sibling skill.

### OSS evidence workflow

For a repository claim, confirm the pinned revision in
[references/source-manifest.json](references/source-manifest.json), inspect the
definition, construction/registration site, runtime call site, tests, error
handling, and composition root, then classify evidence as A (direct), B (strong),
or C (inferred). Only A/B claims are authoritative.

When analyzing serving or training systems, explicitly separate Python
configuration/orchestration from C++, CUDA, Rust, or kernel execution. Record the
production compromise and the test that reveals its behavior. Every recommendation
must include when not to use the pattern and a simpler alternative.
