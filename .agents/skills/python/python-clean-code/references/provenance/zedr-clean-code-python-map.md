# zedr clean-code-python source map

Source: [`zedr/clean-code-python`](https://github.com/zedr/clean-code-python#table-of-contents)
(master, inspected 2026-08-30).

The repository is a compact clean-code checklist organized as Introduction, Variables, Functions,
Classes (SRP/OCP/LSP/ISP/DIP), and DRY. This map keeps that source discoverable while translating
its advice into the active pattern-first taxonomy. It is a provenance map, not a replacement for
the direct examples embedded in the pattern pages.

| Source topic | Reusable Python pattern | What to carry into a review |
|---|---|---|
| Meaningful, searchable names; one vocabulary; explanatory variables | [`functional.md`](../patterns/functional.md), [`typing.md`](../patterns/typing.md) | Name the domain operation and boundary type so callers do not perform mental translation. |
| Defaults instead of short-circuiting and conditionals | [`parameter-objects.md`](../patterns/parameter-objects.md), [`absence-values.md`](../patterns/absence-values.md) | Encode ordinary defaults in the signature or validated configuration; reserve `None` for meaningful absence. |
| One responsibility; one abstraction level; descriptive function names | [`functional.md`](../patterns/functional.md), [`solid-boundaries.md`](../patterns/solid-boundaries.md) | Split orchestration from transformations and side effects when each changes for a different reason. |
| Two-or-fewer arguments; cohesive parameter objects | [`parameter-objects.md`](../patterns/parameter-objects.md) | Bundle a stable, cohesive set of options as a dataclass, Pydantic model, TypedDict, or mapping according to the boundary. |
| Avoid boolean flags; avoid uncontrolled side effects | [`functional.md`](../patterns/functional.md), [`iteration-resources.md`](../patterns/iteration-resources.md), [`closures-decorators.md`](../patterns/closures-decorators.md) | Separate behaviors and make resource/state ownership visible at the edge. |
| SRP and OCP | [`solid-boundaries.md`](../patterns/solid-boundaries.md), [`oop.md`](../patterns/oop.md) | Inject the changing policy or capability and extend through a small callable/protocol before subclassing. |
| LSP and ISP | [`typing.md`](../patterns/typing.md), [`solid-boundaries.md`](../patterns/solid-boundaries.md) | Preserve the public behavioral contract and keep protocols small enough that implementations do not need dummy methods. |
| DIP and the Django `write()` example | [`typing.md`](../patterns/typing.md), [`iteration-resources.md`](../patterns/iteration-resources.md) | Depend on the smallest behavior required by the consumer, such as a file-like `.write()` method. |
| DRY with a warning about bad abstractions | [`functional.md`](../patterns/functional.md), [`oop.md`](../patterns/oop.md) | Remove duplication only when the shared concept is real; duplication is cheaper than a wrong abstraction. |

## Integration rule

The source's principles are diagnostic questions, not a mandate to introduce classes. The active
skill combines them with Python-specific choices: functions and mappings for small dispatch,
`Protocol` for behavioral boundaries, dataclasses or Pydantic for validated data, generators for
lazy work, and explicit state for lifecycle rules. The relevant pages contain the examples and
framework adaptations a learner should copy.
