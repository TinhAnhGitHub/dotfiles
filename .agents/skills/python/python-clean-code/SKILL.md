---
name: python-clean-code
description: >-
  Apply practical Python idioms and refactoring patterns to make code clearer, safer, more
  testable, and easier to extend. Use for cleanups involving functions, closures, decorators,
  type hints, Protocols, iterators, generators, context managers, async/concurrency, properties,
  descriptors, inheritance, metaprogramming, absence values, parameter objects, or questions
  such as “is this Pythonic?” and “how should I structure this Python code?”. For architecture-
  level pattern selection, also read python-design-patterns.
---

# Python clean code

Use this skill to improve Python implementation quality without mechanically applying patterns.
Choose the smallest pattern that addresses the actual design pressure, explain the trade-off, and
leave simple code simple.

## Workflow

1. Identify the pressure: duplication, unclear ownership, branching dispatch, weak typing, hidden
   state, resource leaks, blocking I/O, an overgrown class hierarchy, or ambiguous absence.
2. Load the matching family reference from `references/patterns/`.
3. Compare the current code with the pattern's “when to use” and “when not to use” conditions.
4. Prefer a small, local refactor before introducing a framework abstraction or class hierarchy.
5. Preserve public behavior, metadata, exceptions, cancellation, ordering, and resource ownership.
6. Add focused tests for the changed contract and explain why the selected pattern fits.
7. Read `python-design-patterns` when the change affects system architecture, plugins, providers,
   workflows, or cross-component composition.

## Pattern families

| Family | Use it for | Reference |
|---|---|---|
| Functional boundaries | First-class functions, accessors, operators, partial application, callable objects, dispatch, and registries | [`functional.md`](references/patterns/functional.md) |
| Closures and decorators | Configuration, wrapping, metadata preservation, scoped state, caching, and sync/async adapters | [`closures-decorators.md`](references/patterns/closures-decorators.md) |
| Typed boundaries | Callable types, `Protocol`, `ParamSpec`, `TypeVar`, `Self`, `Annotated`, `Literal`, `TypedDict`, and overloads | [`typing.md`](references/patterns/typing.md) |
| Object-oriented Python | Value objects, composition, delegation, special methods, properties, descriptors, and inheritance | [`oop.md`](references/patterns/oop.md) |
| Iteration and resources | Lazy iteration, generators, context managers, cleanup, and backpressure | [`iteration-resources.md`](references/patterns/iteration-resources.md) |
| Async and concurrency | Async boundaries, executors, queues, cancellation, bounded concurrency, and worker lifecycles | [`async-concurrency.md`](references/patterns/async-concurrency.md) |
| Dynamic class behavior | Class decorators, `__init_subclass__`, descriptors, and carefully bounded metaprogramming | [`dynamic-classes.md`](references/patterns/dynamic-classes.md) |
| Parameter objects | Cohesive workflow parameters, immutable configuration, validation, derived values, and narrow helper boundaries | [`parameter-objects.md`](references/patterns/parameter-objects.md) |
| Absence values | Defaults, strict boundary validation, explicit lifecycle states, Null Objects, and sentinel objects | [`absence-values.md`](references/patterns/absence-values.md) |
| SOLID boundaries | Single responsibility, extension points, substitutable contracts, small protocols, and dependency inversion | [`solid-boundaries.md`](references/patterns/solid-boundaries.md) |

## Decision rules

- Keep a one-use lambda when it is clearer; use a named function or callable object when behavior
  has a name, state, tests, or multiple consumers.
- Use `Protocol` when callers need behavior rather than a specific inheritance tree.
- Use a decorator when cross-cutting behavior should wrap a stable callable; preserve metadata and
  signatures deliberately.
- Use a generator when output is naturally lazy or streaming; make single-pass behavior explicit.
- Keep blocking work out of the event loop and make task cancellation observable.
- Prefer composition and delegation before inheritance; use metaclasses only after simpler class
  hooks cannot express the invariant.
- Keep `None` at untrusted edges only when it is meaningful; normalize it into a safe default,
  validated object, explicit state, or sentinel before core logic branches on it.
- Use SOLID as a diagnostic for change pressure, not as a reason to create abstractions in a
  throwaway script. A small callable plus a mapping is often the best first design.
- Treat `partial`, caches, global state, and dynamic attributes as contracts requiring tests, not
  merely conveniences.

## Source basis

This taxonomy is distilled from Fluent Python's relevant language chapters, `faif/python-patterns`,
`python-patterns.guide`, the ArjanCodes 2026 examples and companion videos, and
[`zedr/clean-code-python`](https://github.com/zedr/clean-code-python#table-of-contents). The zedr
guide contributes the cross-cutting checks for meaningful names, single-purpose functions,
small/cohesive argument objects, side-effect boundaries, SRP/OCP/LSP/ISP/DIP, and DRY. The pages
below translate those checks into Python-specific reusable patterns with direct examples from the
listed AI/ML frameworks. They are not a replacement for framework documentation.

## Framework examples

Each family page contains its own `## Framework examples` section with concise, adapted snippets,
the problem each snippet solves, and a source link. The [framework matrix](../python-design-patterns/references/frameworks/index.md)
is only a crosswalk for finding additional pages and source evidence; it is not a substitute for
embedding an example in the pattern being taught. Do not present a framework-shaped example as
verified source code unless its source and version are recorded.

## Review output

When reviewing or refactoring code, report:

1. The observed design pressure.
2. The selected pattern and its “when” condition.
3. Why it improves the code and what trade-off it introduces.
4. The smallest safe change.
5. Tests and behavior that must remain unchanged.

For architecture decisions, include alternatives that were rejected and why.
