---
name: python-real-world-examples
description: Case studies and reference architectures of production open-source Python projects demonstrating Clean Code, Design Patterns, and Clean Software Architecture in practice. Use when seeking real-world implementations of DDD, Repository, Unit of Work, CQRS, Registries, DI, Protocols, or multi-layer architectures.
---

# Real-World Open-Source Python Pattern Examples

This skill provides **applied, production-grade open-source case studies** grounding the theoretical patterns from the Python craftsmanship triad:
- [**Micro: Clean Code**](../python-clean-code/SKILL.md) — Idiomatic syntax, protocols, typing, context managers, guard clauses.
- [**Meso: Design Patterns**](../python-design-patterns/SKILL.md) — GoF patterns, registries, composition, policy pipelines, Dishka DI.
- [**Macro: Software Architecture**](../python-software-architecture/SKILL.md) — Clean Architecture 4-layer ladder, DDD, Unit of Work, CQRS, Message Bus.

---

## 1. Quick Navigation & Reference Files

- [**`cheatsheet.md`**](cheatsheet.md) — Pattern lookup table, architectural archetypes, and real-world smell detection.
- [**`templates/project-case-study.md`**](templates/project-case-study.md) — Standardized template for analyzing and documenting any open-source repository.
- [**`projects/`**](projects/) — In-depth architectural teardowns and annotated code tours of individual open-source repositories.

---

## 2. Real-World Architectural Ladder

Real-world production systems map cleanly across the 4-layer Clean Architecture ladder:

```
┌────────────────────────────────────────────────────────┐
│  Layer 4: External Frameworks & Drivers (Perimeter)    │
│  - Web Frameworks (FastAPI, Flask, Django, Litestar)   │
│  - Databases (PostgreSQL, SQLite, Redis, Mongo)        │
│  - CLI / Schedulers (Typer, Click, Celery, APScheduler)│
└──────────────────────────┬─────────────────────────────┘
                           │ calls into
                           ▼
┌────────────────────────────────────────────────────────┐
│  Layer 3: Interface Adapters & Gateways                │
│  - Repositories (SQLAlchemy, Redis implementations)    │
│  - External Client Gateways (Stripe, S3, Sendgrid)    │
│  - Presenters & ViewModels                             │
└──────────────────────────┬─────────────────────────────┘
                           │ implements ports of
                           ▼
┌────────────────────────────────────────────────────────┐
│  Layer 2: Application Layer (Use Cases / Services)     │
│  - Interactors / Use Case Commands                     │
│  - Abstract Input/Output Ports (Protocols / ABCs)      │
│  - Message Bus / Event Orchestrators                   │
└──────────────────────────┬─────────────────────────────┘
                           │ manipulates
                           ▼
┌────────────────────────────────────────────────────────┐
│  Layer 1: Enterprise Domain Core                       │
│  - Pure Entities & Aggregates                          │
│  - Immutable Value Objects                             │
│  - Domain Invariants & Exceptions (Zero dependencies)  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Workflow for Answering Requests

When a developer or user asks how to implement a pattern in a production environment:

1. **Identify Abstraction Level**:
   - *Micro* (syntax, typing, context managers) $\rightarrow$ Consult [`python-clean-code`](../python-clean-code/SKILL.md) and examine micro-craftsmanship sections.
   - *Meso* (component design, registries, factories, DI) $\rightarrow$ Consult [`python-design-patterns`](../python-design-patterns/SKILL.md) and examine meso pattern sections.
   - *Macro* (system boundaries, DDD, layering) $\rightarrow$ Consult [`python-software-architecture`](../python-software-architecture/SKILL.md) and examine macro architecture sections.
2. **Find the Matching Case Study**:
   - Check the [Pattern-to-Repository Matrix](cheatsheet.md#1-pattern-to-repository-matrix) for relevant open-source projects.
3. **Present Real-World Mechanics**:
   - Quote concrete directory layouts, class seams (`typing.Protocol`), and composition root wiring.
   - Point out pragmatic trade-offs (where the real project adapted textbook theory to meet production performance or library constraints).
4. **Provide Dual Perspective**:
   - Provide the textbook theoretical ideal (from sister skills) followed by the battle-tested open-source implementation.

---

## 4. Ingesting New Open-Source Projects

To add an open-source project to this skill:
1. Clone or inspect the repository.
2. Fill out [`templates/project-case-study.md`](templates/project-case-study.md) and save it as `projects/<repo-name>.md`.
3. Highlight:
   - Clean Architecture boundaries & Inward Dependency Rule compliance.
   - Repository & Unit of Work implementations.
   - Dependency Injection & Composition Root wiring.
   - Real-world compromises & test harness design.
4. Add the repository to `cheatsheet.md` and the master matrix below.

---

## 5. Active Case Studies Catalog

*Case studies are being populated based on user-selected open-source repositories.*

| Repository | Domain | Primary Architectural Patterns | Key Highlights |
| :--- | :--- | :--- | :--- |
| *Awaiting user input* | *TBD* | *Repository, Unit of Work, Clean Onion, Registries* | *Will be populated upon repo ingestion* |

---

## 6. Relationship to Sister Skills

- [**`../python-clean-code/`**](../python-clean-code/SKILL.md): Provides micro-level Pythonic idioms, type hints, protocols, and clean functions that power individual modules.
- [**`../python-design-patterns/`**](../python-design-patterns/SKILL.md): Provides tactical GoF patterns, registries, factories, and Dishka DI containers.
- [**`../python-software-architecture/`**](../python-software-architecture/SKILL.md): Provides comprehensive theoretical foundations from *Architecture Patterns with Python*, *Clean Architecture with Python*, and *Software Design for Python Programmers*.
