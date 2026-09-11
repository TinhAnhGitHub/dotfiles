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

## 3. Agent Instructions & Workflow (MUST FOLLOW)

When citing or presenting real-world implementations, you MUST follow these explicit steps:
1. **Identify Abstraction Level**: Pick Micro, Meso, or Macro.
2. **Load Case Study**: You MUST read the relevant markdown file inside `projects/` (e.g., `projects/openviking.md`).
3. **Cite the Source**: You MUST explicitly name the open-source repository and link to the source file path.
4. **Contrast Theory vs. Practice**: Provide the textbook theoretical ideal followed by the pragmatic, battle-tested compromise made in the repository.

## Strict Constraints (MUST / NEVER)
- **NEVER** invent or hallucinate code patterns for these repositories. Rely ONLY on the documented `projects/*.md` files.
- **ALWAYS** provide exact markdown file paths when quoting architecture features from the `projects/` directory.

## Output Format Requirements
Your reference to a real-world case study MUST be structured as:
```markdown
### Theoretical Ideal
(How the book/skill describes the pattern)

### Production Pragmatism: [Repo Name]
(How the open-source project actually implemented it)
- **Source**: [projects/repo_name.md](file:///.../projects/repo_name.md)
- **Trade-off**: (Why they broke the rule or adapted the pattern)
```

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

| Repository / Project | Domain | Primary Architectural Patterns | Key Highlights |
| :--- | :--- | :--- | :--- |
| [**OpenViking**](projects/openviking.md) | Agent Context Database & Memory | Virtual Filesystem (`viking://`), Storage Adapter (`CollectionAdapter`), Layered Context Ladder (L0/L1/L2) | Hierarchical directory-recursive retrieval, sidecar metadata files, 36.7k+ stars. |
| [**CowAgent**](projects/cowagent.md) | Multi-Agent Harness & Super Assistant | Agent Harness Decoupling, Mediator Team Pattern, 3-Tier Memory Lifecycle | Multi-channel normalization (WeChat/Feishu/Web), Deep Dream memory distillation, native MCP integration. |
| [**Agent-Reach**](projects/agent-reach.md) | Agent Web Access & Tool Layer | Contract-Based Channel Strategy (`BaseChannel`), Multi-Backend Fallback Gateway | Resilient social site extraction (Twitter/Reddit/Bilibili), self-healing diagnostics (`doctor.py`). |
| [**Graphify**](projects/graphify.md) | Multimodal Codebase Knowledge Graph | Staged Processing Pipeline, Deterministic AST vs Semantic Extraction, Multi-Format Exporter | Tree-Sitter AST parsing, SHA256 content-addressable cache, 71.5x token reduction for agent navigation. |
| [**Canonical AI Frameworks**](projects/framework-canonical.md) | Serving, RL, Agent Workflows & Fine-Tuning | Dynamic Registry (`AutoModel.register`), Typed DI (`Agent[DepsT, OutputT]`), Universal Adapter (`Router`) | 17 verified production frameworks (Transformers, PydanticAI, LangGraph, vLLM, LiteLLM, Agno, verl, etc.). |

---

## 6. Relationship to Sister Skills

- [**`../python-clean-code/`**](../python-clean-code/SKILL.md): Provides micro-level Pythonic idioms, type hints, protocols, and clean functions that power individual modules.
- [**`../python-design-patterns/`**](../python-design-patterns/SKILL.md): Provides tactical GoF patterns, registries, factories, and Dishka DI containers.
- [**`../python-software-architecture/`**](../python-software-architecture/SKILL.md): Provides comprehensive theoretical foundations from *Architecture Patterns with Python*, *Clean Architecture with Python*, and *Software Design for Python Programmers*.
