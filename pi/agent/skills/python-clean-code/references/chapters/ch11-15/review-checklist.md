# Chapters 11–15 review checklist

Use this checklist when reviewing or refactoring Python, especially tool/agent/framework code.

## Object model

- [ ] Is the public behavior clear from normal Python operations?
- [ ] Is `repr` deterministic, useful, bounded, and free of secrets?
- [ ] Do equality and hashing use the same immutable semantic fields?
- [ ] Is mutable internal state protected from accidental external mutation?
- [ ] Are properties, dynamic attributes, and pattern-matching fields intentional API surface?

## Sequence/mapping behavior

- [ ] Does the implementation provide the complete protocol it claims to provide?
- [ ] Are integer indices validated with `operator.index`?
- [ ] Do slices return the expected conceptual type?
- [ ] Are `IndexError`, `KeyError`, and `TypeError` used consistently?
- [ ] Do all mutation paths preserve normalization/invariants?
- [ ] Would `UserDict`/`UserList` or composition be safer than a built-in subclass?

## Protocols and ABCs

- [ ] Is the interface defined from the consumer's needs?
- [ ] Would a small `Protocol` avoid coupling external implementations to a base class?
- [ ] Is an ABC justified by shared implementation, an invariant, registration, or enforced hooks?
- [ ] Are generic type variables parameterized and variance justified?
- [ ] Is `@runtime_checkable` used only for shallow capability dispatch?
- [ ] Are semantic rules documented and tested beyond the type signature?

## Inheritance and mixins

- [ ] Could composition, a strategy callable, or an adapter express this more clearly?
- [ ] Does every cooperative override call `super()` exactly once?
- [ ] Are mixins narrow, stateless, and host-agnostic enough?
- [ ] Are signatures and keyword forwarding compatible across the MRO?
- [ ] Are built-in subclass invariants protected on every construction and mutation path?
- [ ] Is `__init_subclass__` predictable, calling `super()`, and tested for invalid subclasses?

## Type hints

- [ ] Is `TypedDict` used for dictionary shape rather than mistaken for runtime validation?
- [ ] Are overloads truthful and followed by one implementation?
- [ ] Is `cast` backed by an obvious runtime or framework invariant?
- [ ] Is `Any` limited to a deliberate boundary rather than hiding missing design?
- [ ] Are sync/async, stream/non-stream, and raw/validated result modes distinct in types?

## Lifecycle and streaming

- [ ] Does the owner of a resource also own its cleanup path?
- [ ] Is cleanup guaranteed on success, exception, cancellation, and partial initialization?
- [ ] Are async generators closed with `aclose`/`aclosing` when required?
- [ ] Are streams lazy and backpressure/cancellation behavior documented?
- [ ] Is context-local tracing/configuration reset in `finally`?

## Agent/tool-specific checks

- [ ] Is the tool schema derived from the function signature or kept in one source of truth?
- [ ] Are tool names/dispatch keys validated before invocation?
- [ ] Are malformed arguments and tool exceptions converted into uniform, observable errors?
- [ ] Are callbacks/hooks ordered, removable, and isolated per request/run?
- [ ] Do operator DSL objects reject invalid operands and preserve readable representations?
- [ ] Can a test replace a dependency by callable identity or Protocol rather than a fragile string?
