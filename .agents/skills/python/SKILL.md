---
name: python
description: Route Python development, maintenance, testing, packaging, dependency-management,
  architecture, design-pattern, and code-quality tasks to the most appropriate child skill. Use
  this skill whenever a request involves Python code or a Python project, including clean-code
  improvements, design patterns, Pydantic, pytest, PySpark/Databricks testing, or uv.
---

# Python skills

Choose the child skill that matches the primary concern. Read it before acting.

- [python-clean-code](python-clean-code/SKILL.md) — micro-level implementation idioms, refactoring, closures,
  decorators, typing, protocols, object-model behavior, iteration, resources, and concurrency.
- [python-design-patterns](python-design-patterns/SKILL.md) — meso-level design patterns, composition,
  factories, strategies, registries, workflows, lifecycle, state machines, and modern DI (Dishka).
- [python-software-architecture](python-software-architecture/SKILL.md) — macro-level system architecture:
  Clean Architecture 4-layer ladder, Domain-Driven Design (DDD), Aggregates, Unit of Work, Repository,
  Message Bus, CQRS, Event-Driven Microservices, and Legacy Strangler Fig refactoring.
- [python-real-world-examples](python-real-world-examples/SKILL.md) — real-world open-source case studies
  and reference architectures demonstrating Clean Code, Design Patterns, and Clean Architecture in production.
- [pydantic-skill](pydantic-skill/SKILL.md) — Pydantic models, validation, settings, and serialization.
- [pytest-skill](pytest-skill/SKILL.md) — production-grade pytest guidance.
- [pytest-databricks](pytest-databricks/SKILL.md) — pytest for Databricks, PySpark, and Databricks Connect.
- [uv](uv/SKILL.md) — Python project and dependency management with uv.

## The 4-Pillar Python Architecture & Craftsmanship Hierarchy

```
┌────────────────────────────────────────────────────────┐
│  [ Reference Layer ] python-real-world-examples        │
│  Production OSS case studies & annotated code tours    │
└──────────────────────────┬─────────────────────────────┘
                           │ grounds & demonstrates
                           ▼
[ Macro: System Architecture ] ──► python-software-architecture
  - 4-layer Clean Architecture (Onion / Hexagonal), Dependency Rule
  - Domain-Driven Design (Aggregates, Invariants, Entities, Value Objects)
  - Persistence & Orchestration (Repository, Unit of Work, Message Bus)
  - Distributed Systems (Commands vs. Events, Microservices, CQRS, Strangler Fig)
           │
           ▼ (composed of)
[ Meso: Tactical Design Patterns ] ──► python-design-patterns
  - GoF Patterns (Strategy, Factory, Adapter, Façade, Observer, State, Composite)
  - Composition over inheritance, Policy pipelines, Command Registries
  - Extensibility & Modern Dependency Injection (Dishka)
           │
           ▼ (built on)
[ Micro: Code Craftsmanship & Idioms ] ──► python-clean-code
  - Functions, closures, decorators, generator pipelines
  - Structural typing (Protocols), TypeVar, absence of values (sentinels)
  - Context managers, fail-fast guard clauses, exception boundaries, Pythonic OOP
```

## Routing rules

- **Micro level**: Use `python-clean-code` for “make this Pythonic”, local refactors, typing, decorator,
  generator, resource management, guard clauses, or absence of value questions.
- **Meso level**: Use `python-design-patterns` for component-level design patterns (Strategy, Factory,
  Registry, State, Adapter, Observer), plugin boundaries, or modern DI with Dishka.
- **Macro level**: Use `python-software-architecture` for whole-application architecture, Clean Architecture
  layering, DDD aggregates/invariants, Repository/Unit of Work, Message Bus, CQRS, or monolith migration.
- **Reference & Case Studies**: Use `python-real-world-examples` when seeking real-world production implementations
  of patterns, concrete open-source case studies, or comparing architectural trade-offs in battle-tested projects.
- **Combined workflows**:
  - When designing a system end-to-end, start with `python-software-architecture` for layer boundaries and aggregates,
    use `python-design-patterns` for internal adapter/strategy patterns, use `python-clean-code` for
    implementation-level idioms and typing, and consult `python-real-world-examples` for concrete reference codebases.
- Prefer the most specific child skill when the task is primarily Pydantic, pytest, Databricks, or uv.
