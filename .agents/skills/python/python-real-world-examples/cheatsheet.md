# Real-World Python Patterns Cheatsheet

Quick-reference guide for identifying, comparing, and applying architectural and design patterns derived from production open-source Python codebases.

---

## 1. Pattern-to-Repository Matrix

| Pattern Category | Pattern Name | Key Problem Solved | Key Seams / Mechanics | Production OSS Reference | Sister Skill |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Macro (Storage)** | **Storage Adapter Seam** | Decouple vector DB from filesystem logic | `CollectionAdapter` (`ICollection`) | [`OpenViking`](projects/openviking.md#3-b-storage-decoupling-via-collectionadapter) | [`architecture`](../python-software-architecture/SKILL.md) |
| **Macro (Context)** | **Tiered Context Ladder**| Eliminate LLM token waste | L0 Abstract $\rightarrow$ L1 Overview $\rightarrow$ L2 Detail | [`OpenViking`](projects/openviking.md#3-a-the-3-tier-progressive-loading-ladder) | [`architecture`](../python-software-architecture/SKILL.md) |
| **Macro (Harness)** | **Agent Harness Decoupling**| Decouple IM platforms from reasoning core | Channel Gateway $\leftrightarrow$ Core $\leftrightarrow$ Models | [`CowAgent`](projects/cowagent.md#1-executive-architecture-summary) | [`architecture`](../python-software-architecture/SKILL.md) |
| **Macro (Memory)** | **3-Tier Memory Lifecycle** | Distill daily conversations into core knowledge | Context $\rightarrow$ Daily $\rightarrow$ Core (Deep Dream) | [`CowAgent`](projects/cowagent.md#3-a-the-3-tier-memory--deep-dream-distillation) | [`architecture`](../python-software-architecture/SKILL.md) |
| **Meso (Routing)** | **Contract Channel Strategy**| Unified interface across diverse social sites | `BaseChannel` (`can_handle`, `read`, `check`) | [`Agent-Reach`](projects/agent-reach.md#3-a-contract-based-channel-seam) | [`patterns`](../python-design-patterns/SKILL.md) |
| **Meso (Resilience)**| **Multi-Backend Fallback** | Automatic failover when web endpoints break | Ordered trial with fallback catching | [`Agent-Reach`](projects/agent-reach.md#3-b-multi-backend-fallback-strategy) | [`patterns`](../python-design-patterns/SKILL.md) |
| **Meso (Pipeline)** | **Staged Ingestion Pipeline**| Decouple code parsing from artifact export | Scan $\rightarrow$ Cache $\rightarrow$ AST $\rightarrow$ Semantic $\rightarrow$ Export | [`Graphify`](projects/graphify.md#3-a-the-staged-ingestion--extraction-pipeline) | [`patterns`](../python-design-patterns/SKILL.md) |
| **Meso (Cache)** | **Content-Addressable Cache**| Zero recomputation on unchanged files | SHA256 chunked file hash index | [`Graphify`](projects/graphify.md#3-b-content-addressable-sha256-incremental-cache) | [`clean-code`](../python-clean-code/SKILL.md) |
| **Meso (Registry)** | **Dynamic Extension Registry**| Third-party model/tool registration | `@registry.register()`, `AutoModel.register()` | [`Canonical Frameworks`](projects/framework-canonical.md#3-a-factory--registry-hugging-face-automodelregister) | [`patterns`](../python-design-patterns/SKILL.md) |
| **Meso (DI)** | **Typed Dependency Injection**| Type-safe runtime resource wiring | `Agent[DepsT, OutputT]`, `RunContext` | [`Canonical Frameworks`](projects/framework-canonical.md#3-b-typed-dependency-injection-pydanticai-agentdepst-outputt) | [`patterns`](../python-design-patterns/SKILL.md) |
| **Meso (Adapter)** | **Universal Provider Adapter**| Normalize 100+ LLM API differences | Provider-normalized `completion()`, `Router` | [`Canonical Frameworks`](projects/framework-canonical.md#3-c-the-universal-adapter--fallback-router-litellm) | [`patterns`](../python-design-patterns/SKILL.md) |
| **Micro (Idioms)** | **Protocol Seams** | Duck typing with static type checker safety | `@runtime_checkable` `typing.Protocol` | [`OpenViking`](projects/openviking.md), [`CowAgent`](projects/cowagent.md) | [`clean-code`](../python-clean-code/SKILL.md) |
| **Micro (Idioms)** | **Resource Lifecycle** | Guarantee deterministic socket/pool cleanup | Context-managed streams, chunked read buffers | [`Graphify`](projects/graphify.md), [`OpenAI SDK`](projects/framework-canonical.md) | [`clean-code`](../python-clean-code/SKILL.md) |

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


## 5. Canonical topic index

| Topic | Canonical page | Repository evidence |
|---|---|---|
| Registry / factory / plugins | [P08](../python-software-architecture/patterns/registry-factory.md) | Transformers, vLLM, pytest, Django, smolagents, Ray |
| Strategy / policy | [P09](../python-software-architecture/patterns/strategy-policy.md) | TRL, verl, SGLang, DeepSpeed, Transformers |
| Provider adapter / router | [P06/P12](../python-software-architecture/patterns/adapter-provider-router.md) | LiteLLM, HTTPX, smolagents, Transformers, TensorRT-LLM, LMDeploy |
| Workflow / state / saga | [P13/P16](../python-software-architecture/patterns/state-workflow.md) | verl, LangGraph, CrewAI, OpenAI Agents, Ray, Home Assistant |
| Commands / events / projections | [P10/P11](../python-software-architecture/patterns/events-message-bus.md) | Home Assistant, AutoGen, OpenRLHF, CrewAI, MCP Python SDK |
| Dependency injection / composition | [P06/P07](../python-software-architecture/patterns/dependency-injection.md) | PydanticAI, FastAPI, OpenAI Agents |
| Testing seams / fitness | [P17](../python-software-architecture/patterns/testing-boundaries.md) | pytest, HTTPX, FastAPI, Django, Transformers, vLLM, MLflow |
| Python versus native execution | [P16](../python-software-architecture/patterns/concurrency-lifecycle.md) | vLLM, SGLang, Megatron-LM, TensorRT-LLM, llama.cpp, MLC-LLM |

## 6. Research corpus navigation

The full 45-project source and revision inventory is
[the pinned manifest](../python-software-architecture/references/source-manifest.json).
The normalized crosswalk is
[the repository pattern matrix](../python-software-architecture/references/repository-pattern-matrix.md).
Read each dossier’s source and test paths before treating its claims as proven;
C-level inferences remain explicitly labeled.
