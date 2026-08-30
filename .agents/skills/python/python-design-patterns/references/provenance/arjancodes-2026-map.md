# ArjanCodes 2026 coverage map

This is an audit map for the 29 directories and 148 Python files in the
[ArjanCodes 2026 examples](https://github.com/ArjanCodes/examples/tree/main/2026)
tree. It is an index, not a substitute for the examples embedded in the pattern pages. Each
destination page contains the reusable shape, conditions, trade-offs, and a concise adapted
snippet; this table keeps the source coverage visible.

| Source directory | Distilled design pressure | Design-pattern destination | Clean-code destination |
|---|---|---|---|
| `apidata` | Keep API schemas, ORM models, and partial-update rules at separate boundaries. | [AI boundaries](../architecture/ai-boundaries.md) | `typing.md` |
| `clean` | Use cohesive configuration/results and resource-safe report pipelines. | [Parameter Object](../construction/parameter-object.md) | `parameter-objects.md`, `iteration-resources.md` |
| `composite` | Treat leaves and groups through one recursive protocol. | [Composite](../composition/composite.md) | `oop.md` |
| `coupling` | Pass domain values and narrow ports instead of leaking integration details. | [SOLID boundaries](../principles/solid.md), [Protocols](../extensibility/protocols.md) | `typing.md`, `oop.md` |
| `cqrs` | Separate write commands from denormalized read projections. | [CQRS](../architecture/cqrs.md) | `functional.md`, `async-concurrency.md` |
| `dataclass` | Make value construction, defaults, derived fields, and mutability explicit. | [Value Object](../construction/value-object.md) | `oop.md`, `parameter-objects.md` |
| `dctricks` | Use dataclass hooks, decorators, descriptors, and context managers only for a clear contract. | [Registry and DI](../extensibility/registry-di.md), [Sentinel and lazy resources](../python-specific/sentinel-lazy.md) | `dynamic-classes.md`, `closures-decorators.md` |
| `descriptors` | Understand attribute precedence before introducing reusable lazy or validated fields. | [Sentinel and lazy resources](../python-specific/sentinel-lazy.md) | `dynamic-classes.md`, `oop.md` |
| `dry` | Remove meaningful duplication without creating flag-heavy generic code. | [Anti-patterns](../anti-patterns/singleton-inheritance.md) | `functional.md` |
| `facade` | Hide a multi-step SDK workflow and translate provider errors into domain results. | [Facade](../composition/facade.md) | `oop.md`, `typing.md` |
| `features` | Use standard-library caching, `replace`, `pairwise`, `ExitStack`, context variables, and matching when semantics stay visible. | [Decorator](../composition/decorator.md), [Sentinel and lazy resources](../python-specific/sentinel-lazy.md) | `closures-decorators.md`, `iteration-resources.md` |
| `flexible` | Validate external dictionaries once, then use stable domain types. | [AI boundaries](../architecture/ai-boundaries.md), [Value Object](../construction/value-object.md) | `typing.md`, `parameter-objects.md` |
| `fluent` | Make ordered construction readable while keeping steps interchangeable. | [Builder](../construction/builder.md) | `oop.md` |
| `generators` | Make lazy pull flow, backpressure, `send`, return values, and async iteration explicit. | [Command](../behavior/command.md) | `iteration-resources.md`, `async-concurrency.md` |
| `god` | Split orchestration, transformation, evaluation, persistence, and reporting. | [SOLID boundaries](../principles/solid.md) | `solid-boundaries.md`, `functional.md` |
| `libraries` | Prefer focused libraries and explicit boundaries over bespoke infrastructure. | [Simplest design](../anti-patterns/singleton-inheritance.md) | `typing.md`, `oop.md` |
| `nested` | Replace nested loops with named, independently testable transformations. | [Composition](../principles/composition.md) | `functional.md` |
| `none` | Normalize raw optional data at the edge and keep the domain strict. | [Sentinel and lazy resources](../python-specific/sentinel-lazy.md) | `absence-values.md` |
| `oop` | Prefer composition, narrow protocols, value configuration, and YAGNI over subclass matrices. | [Composition](../principles/composition.md), [Protocols](../extensibility/protocols.md) | `oop.md`, `typing.md` |
| `param` | Group cohesive arguments into an immutable, validated value object. | [Parameter Object](../construction/parameter-object.md) | `parameter-objects.md` |
| `pattern` | Start with functions and mappings; introduce a protocol when a real provider boundary appears. | [Strategy](../behavior/strategy.md), [Adapter](../composition/adapter.md) | `functional.md`, `typing.md` |
| `policy` | Compose one-rule policies, select them by registry/configuration, and preserve order. | [Policy Pipeline](../behavior/policy-pipeline.md) | `functional.md`, `solid-boundaries.md` |
| `ports` | Keep use cases independent of HTTP, SQL, and framework adapters. | [SOLID boundaries](../principles/solid.md), [Adapter](../composition/adapter.md) | `typing.md`, `oop.md` |
| `props` | Keep I/O and concurrency visible instead of hiding them behind async properties. | [Protocols](../extensibility/protocols.md) | `async-concurrency.md`, `oop.md` |
| `spec` | Compose named predicates and keep rule registration separate from evaluation. | [Specification](../behavior/specification.md), [Registry and DI](../extensibility/registry-di.md) | `functional.md`, `typing.md` |
| `state` | Encode `(state, event) -> (next state, action)` explicitly and reject illegal transitions. | [State Machine](../lifecycle/state-machine.md) | `oop.md`, `typing.md` |
| `type` | Model plan variation as data before composing genuinely different pricing behavior. | [Strategy](../behavior/strategy.md), [Value Object](../construction/value-object.md) | `oop.md`, `parameter-objects.md` |
| `value` | Enforce invariants at construction so invalid values cannot travel through the domain. | [Value Object](../construction/value-object.md) | `oop.md`, `typing.md` |
| `webhook` | Separate event publication, typed payloads, and delivery adapters. | [Observer](../behavior/observer.md), [Adapter](../composition/adapter.md) | `typing.md`, `async-concurrency.md` |

## Source interpretation

The repository examples are teaching material, so the snippets in the destination pages are
adapted rather than presented as drop-in framework code. Preserve the source's design lesson, then
re-check current APIs, persistence, retries, cancellation, error mapping, and ownership before
using an example in production.
