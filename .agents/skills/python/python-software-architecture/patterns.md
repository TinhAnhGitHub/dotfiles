# Canonical architecture pattern catalog

The canonical pattern vocabulary is P01–P17. Detailed pages live in
[patterns/](patterns/) and are indexed by
[book-pattern-matrix.md](references/book-pattern-matrix.md).

Use [architecture-selection-guide.md](references/architecture-selection-guide.md) to
choose a pattern from the problem pressure. Use the
[repository-pattern-matrix.md](references/repository-pattern-matrix.md) to move
from book theory to verified open-source evidence.

| ID range | Canonical page |
|---|---|
| P01 | [Domain model, entity, value object](patterns/domain-model.md) |
| P02 | [Aggregate and consistency boundary](patterns/aggregate-boundary.md) |
| P03–P04 | [Repository and Unit of Work](patterns/repository-unit-of-work.md) |
| P05–P06 | [Use cases, ports, and adapters](patterns/ports-and-adapters.md) |
| P07 | [Composition root and dependency injection](patterns/dependency-injection.md) |
| P08 | [Factory, registry, and plugins](patterns/registry-factory.md) |
| P09 | [Strategy, policy, and Template Method](patterns/strategy-policy.md) |
| P10 | [Commands, events, and message bus](patterns/events-message-bus.md) |
| P11 | [CQRS and read projections](patterns/cqrs.md) |
| P12 | [Adapters, façades, and provider routers](patterns/adapter-provider-router.md) |
| P13 | [State machines, workflows, and sagas](patterns/state-workflow.md) |
| P14 | [Decorators, middleware, and observability](patterns/middleware-observability.md) |
| P15 | [Composites, iterators, visitors, and pipelines](patterns/pipelines-and-composites.md) |
| P16 | [Concurrency, scheduling, and resource lifecycle](patterns/concurrency-lifecycle.md) |
| P17 | [Testing seams, fitness tests, ACL, and Strangler migration](patterns/testing-boundaries.md) |

The older chapter index remains the book-oriented entry point; these pages are the
single cross-skill pages for applied pattern decisions. Existing tactical pages in
the sister design-patterns skill are supporting deep dives, not alternate IDs.
