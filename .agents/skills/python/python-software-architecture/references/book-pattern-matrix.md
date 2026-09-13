# Canonical Python architecture pattern matrix

This is the canonical vocabulary shared by the architecture, design-patterns, and
real-world-examples skills. Use the `P##` identifier in case studies, repository
tables, exercises, and answers. A pattern name is an alias; the identifier is the
stable key.

## How to use this matrix

Start with the problem pressure, then choose the least powerful option that meets
the constraint. The standard-library implementation is the baseline. A repository
case study is authoritative only when its source and tests provide level A or B
evidence (see [repository-pattern-matrix](repository-pattern-matrix.md)).

| ID | Canonical concept | Problem it solves | Simpler alternative | Canonical page | Practice |
|---|---|---|---|---|---|
| P01 | Domain Model, Entity, Value Object | Express business meaning and invariants instead of passing unvalidated primitives | Functions plus `dataclass` records | [domain-model](../patterns/domain-model.md) | [repository-uow](../exercises/repository-uow.md) |
| P02 | Aggregate and Consistency Boundary | Protect invariants across related objects and define transaction scope | Validate at the application boundary | [aggregate-boundary](../patterns/aggregate-boundary.md) | [repository-uow](../exercises/repository-uow.md) |
| P03 | Repository | Keep persistence details out of domain and use-case code | A direct query function for one stable read | [repository-unit-of-work](../patterns/repository-unit-of-work.md) | [repository-uow](../exercises/repository-uow.md) |
| P04 | Unit of Work and Transaction Boundary | Make a group of writes atomic and coordinate repositories | One explicit transaction function | [repository-unit-of-work](../patterns/repository-unit-of-work.md) | [repository-uow](../exercises/repository-uow.md) |
| P05 | Application Service / Use Case | Orchestrate one user-visible operation without putting I/O in the domain | A small module-level function | [ports-and-adapters](../patterns/ports-and-adapters.md) | [repository-uow](../exercises/repository-uow.md) |
| P06 | Ports, Adapters, and Dependency Inversion | Change databases, transports, SDKs, or runtimes without changing core policy | Pass a callable or concrete object while variation is small | [ports-and-adapters](../patterns/ports-and-adapters.md) | [provider-adapter](../exercises/provider-adapter.md) |
| P07 | Composition Root and Dependency Injection | Make construction, ownership, and lifetimes explicit and testable | Manual wiring in `main()` or a fixture | [dependency-injection](../patterns/dependency-injection.md) | [provider-adapter](../exercises/provider-adapter.md) |
| P08 | Factory, Registry, and Plugin Architecture | Select or extend implementations without a growing central switch | A dictionary or direct constructor call | [registry-factory](../patterns/registry-factory.md) | [registry-plugin](../exercises/registry-plugin.md) |
| P09 | Strategy, Policy, and Template Method | Vary an algorithm or policy while keeping the workflow stable | A function, callable, or local conditional | [strategy-policy](../patterns/strategy-policy.md) | [registry-plugin](../exercises/registry-plugin.md) |
| P10 | Commands, Events, and Message Bus | Separate intent, completed facts, and side effects | Direct function calls for local synchronous work | [events-message-bus](../patterns/events-message-bus.md) | [event-driven-training](../exercises/event-driven-training.md) |
| P11 | CQRS and Read Projections | Optimize read shape/scale independently from invariant-enforcing writes | One model and one query path | [cqrs](../patterns/cqrs.md) | [event-driven-training](../exercises/event-driven-training.md) |
| P12 | Adapter, Façade, and Provider Router | Normalize incompatible external APIs and provider-specific errors | A thin wrapper around one dependency | [adapter-provider-router](../patterns/adapter-provider-router.md) | [provider-adapter](../exercises/provider-adapter.md) |
| P13 | State Machine, Workflow, and Saga | Make legal transitions, retries, compensation, and pause/resume explicit | Enum plus a small transition table | [state-workflow](../patterns/state-workflow.md) | [workflow-state](../exercises/workflow-state.md) |
| P14 | Decorator, Middleware, and Observability | Add cross-cutting behavior at a boundary without changing core logic | One explicit helper call | [middleware-observability](../patterns/middleware-observability.md) | [provider-adapter](../exercises/provider-adapter.md) |
| P15 | Composite, Iterator, Visitor, and Pipelines | Traverse trees or staged transformations while keeping steps composable | A list of functions or a recursive function | [pipelines-and-composites](../patterns/pipelines-and-composites.md) | [event-driven-training](../exercises/event-driven-training.md) |
| P16 | Concurrency, Scheduling, and Resource Lifecycle | Coordinate work, backpressure, cancellation, and cleanup | A synchronous loop or context manager | [concurrency-lifecycle](../patterns/concurrency-lifecycle.md) | [workflow-state](../exercises/workflow-state.md) |
| P17 | Testing Seams, Fitness Tests, ACL, and Strangler Migration | Change architecture safely and contain legacy or external coupling | Focused unit tests around a pure function | [testing-boundaries](../patterns/testing-boundaries.md) | [provider-adapter](../exercises/provider-adapter.md) |

## Book crosswalk

The chapter references below are paraphrased pointers, not reproduced book text.

| ID | *Architecture Patterns with Python* | *Clean Architecture with Python* | *Software Design for Python Programmers* | Practical emphasis |
|---|---|---|---|---|
| P01 | [ch01](../chapters/ch01-percival-domain-modeling.md) | [ch17](../chapters/ch17-keen-domain-driven-design-core.md) | [ch28](../chapters/ch28-mak-requirements-engineering.md), [ch30](../chapters/ch30-mak-encapsulation-information-hiding.md) | Name the domain and put invariants near the data they protect. |
| P02 | [ch07](../chapters/ch07-percival-aggregates-and-consistency-boundaries.md) | [ch17](../chapters/ch17-keen-domain-driven-design-core.md) | [ch29](../chapters/ch29-mak-good-class-design.md) | Keep the boundary small enough to be consistent in one transaction. |
| P03 | [ch02](../chapters/ch02-percival-repository-pattern.md) | [ch20](../chapters/ch20-keen-frameworks-and-drivers.md) | [ch35](../chapters/ch35-mak-adapter-and-facade.md) | Depend on a collection-shaped port, not a database session. |
| P04 | [ch06](../chapters/ch06-percival-unit-of-work-pattern.md) | [ch18](../chapters/ch18-keen-application-layer-use-cases.md), [ch20](../chapters/ch20-keen-frameworks-and-drivers.md) | [ch41](../chapters/ch41-mak-multithreaded-program-design.md) | Use context-managed ownership and explicit commit/rollback semantics. |
| P05 | [ch04](../chapters/ch04-percival-flask-api-and-service-layer.md) | [ch18](../chapters/ch18-keen-application-layer-use-cases.md) | [ch29](../chapters/ch29-mak-good-class-design.md) | Make one use case easy to invoke from HTTP, CLI, and workers. |
| P06 | [ch02](../chapters/ch02-percival-repository-pattern.md), [ch13](../chapters/ch13-percival-dependency-injection-and-bootstrapping.md) | [ch14](../chapters/ch14-keen-clean-architecture-essentials.md), [ch16](../chapters/ch16-keen-type-enhanced-python.md), [ch19](../chapters/ch19-keen-interface-adapters-controllers-presenters.md), [ch20](../chapters/ch20-keen-frameworks-and-drivers.md) | [ch30](../chapters/ch30-mak-encapsulation-information-hiding.md), [ch35](../chapters/ch35-mak-adapter-and-facade.md) | Point dependencies inward; let outer code implement inner ports. |
| P07 | [ch13](../chapters/ch13-percival-dependency-injection-and-bootstrapping.md) | [ch18](../chapters/ch18-keen-application-layer-use-cases.md), [ch20](../chapters/ch20-keen-frameworks-and-drivers.md) | [ch34](../chapters/ch34-mak-factory-method-and-abstract-factory.md) | Centralize object construction without hiding lifetime ownership. |
| P08 | — | [ch20](../chapters/ch20-keen-frameworks-and-drivers.md) | [ch34](../chapters/ch34-mak-factory-method-and-abstract-factory.md) | Prefer explicit registration and useful startup errors over magic discovery. |
| P09 | — | [ch15](../chapters/ch15-keen-solid-foundations-in-python.md) | [ch32](../chapters/ch32-mak-subclass-design-inheritance.md), [ch33](../chapters/ch33-mak-template-method-and-strategy.md) | Use composition and callables before a class hierarchy. |
| P10 | [ch08](../chapters/ch08-percival-events-and-the-message-bus.md), [ch09](../chapters/ch09-percival-going-to-town-on-the-message-bus.md), [ch10](../chapters/ch10-percival-commands-and-command-handler.md), [ch11](../chapters/ch11-percival-event-driven-microservices.md) | [ch18](../chapters/ch18-keen-application-layer-use-cases.md), [ch23](../chapters/ch23-keen-observability-monitoring.md) | [ch37](../chapters/ch37-mak-observer-pattern.md) | Commands have one owner; events describe facts and may have many consumers. |
| P11 | [ch12](../chapters/ch12-percival-cqrs.md) | [ch18](../chapters/ch18-keen-application-layer-use-cases.md) | [ch29](../chapters/ch29-mak-good-class-design.md) | Separate read performance concerns only when the consistency cost is understood. |
| P12 | [ch02](../chapters/ch02-percival-repository-pattern.md) | [ch19](../chapters/ch19-keen-interface-adapters-controllers-presenters.md), [ch20](../chapters/ch20-keen-frameworks-and-drivers.md) | [ch35](../chapters/ch35-mak-adapter-and-facade.md) | Translate external names, errors, retries, and capabilities at one boundary. |
| P13 | — | [ch18](../chapters/ch18-keen-application-layer-use-cases.md), [ch24](../chapters/ch24-keen-legacy-to-clean-refactoring.md) | [ch38](../chapters/ch38-mak-state-pattern.md) | Persist enough state to resume, retry, or compensate after failure. |
| P14 | [ch08](../chapters/ch08-percival-events-and-the-message-bus.md) | [ch23](../chapters/ch23-keen-observability-monitoring.md) | [ch39](../chapters/ch39-mak-singleton-composite-decorator.md) | Instrument boundaries and preserve the wrapped contract. |
| P15 | — | [ch18](../chapters/ch18-keen-application-layer-use-cases.md) | [ch36](../chapters/ch36-mak-iterator-and-visitor.md), [ch39](../chapters/ch39-mak-singleton-composite-decorator.md) | Keep each stage observable and independently testable. |
| P16 | [ch09](../chapters/ch09-percival-going-to-town-on-the-message-bus.md) | [ch23](../chapters/ch23-keen-observability-monitoring.md) | [ch41](../chapters/ch41-mak-multithreaded-program-design.md) | Treat cancellation, backpressure, cleanup, and native boundaries as architecture. |
| P17 | [ch03](../chapters/ch03-percival-coupling-and-abstractions.md), [ch05](../chapters/ch05-percival-tdd-in-high-gear-and-low-gear.md) | [ch21](../chapters/ch21-keen-clean-testing-patterns.md), [ch24](../chapters/ch24-keen-legacy-to-clean-refactoring.md), [ch25](../chapters/ch25-keen-clean-architecture-journey.md) | [ch26](../chapters/ch26-mak-path-to-well-designed-software.md), [ch27](../chapters/ch27-mak-iterate-to-achieve-good-design.md) | Prove boundaries with fakes, contracts, fitness tests, and incremental migration. |

## Evidence levels for repository mappings

- **A — Direct**: a definition, construction/registration site, runtime call site,
  and relevant tests are all identified.
- **B — Strong**: implementation is verified and tests exercise the boundary
  indirectly or through integration coverage.
- **C — Inferred**: documentation or naming suggests the pattern, but source
  verification is incomplete. C is a research lead, not an authoritative example.

Do not upgrade C to A/B because a project uses the pattern’s vocabulary. Record
missing tests, generated code, native implementations, and version uncertainty as
limitations.
