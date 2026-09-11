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

## Triage Workflow (MUST FOLLOW)

When evaluating a Python request, you MUST execute this exact workflow:
1. **Analyze the Request**: Determine if the problem is at the micro, meso, or macro level.
2. **Select ONE Primary Skill**: Pick the most specific child skill from the routing rules below.
3. **Read the Child Skill**: You MUST read the child skill's `SKILL.md` file before proposing any code.

## Agent Routing Rules (STRICT INSTRUCTIONS)

You are STRICTLY REQUIRED to route requests to the following child skills based on these constraints:
- **IF** the request involves "make this Pythonic", local refactors, typing, decorators, generators, or guard clauses -> **YOU MUST** read `python-clean-code`.
- **IF** the request involves component-level GoF patterns (Strategy, Factory, Registry), plugin boundaries, or DI containers -> **YOU MUST** read `python-design-patterns`.
- **IF** the request involves full system architecture, Clean Architecture, DDD aggregates, Unit of Work, Message Bus, or refactoring monoliths -> **YOU MUST** read `python-software-architecture`.
- **IF** you need to see a real-world open-source production example of any pattern -> **YOU MUST** read `python-real-world-examples`.

- **COMBINED WORKFLOWS**:
  - **Start System Design** -> Read `python-software-architecture` first.
  - **Internal Component Design** -> Read `python-design-patterns`.
  - **Implementation/Syntax** -> Read `python-clean-code`.
