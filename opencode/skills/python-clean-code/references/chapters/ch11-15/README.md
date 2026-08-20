# Fluent Python 2e — Chapters 11–15 reference bundle

This directory is a **reference bundle** for the parent `python-clean-code` skill. It is
intentionally not named `SKILL.md`: the parent skill is already installed and another agent
may be using it. Do not edit the parent `SKILL.md` merely to consume these references.

The material is distilled from the local `Fluent Python 2e` examples and checked against
current production patterns in MLflow, LlamaIndex, AutoGen/AG2, LangChain, LangGraph, vLLM,
and Hugging Face. Framework links are evidence for patterns, not rules that every project
must copy.

## Chapter map

The local repository maps these chapters as follows:

| Chapter | Topic | Local examples |
|---|---|---|
| 11 | A Pythonic Object | `11-pythonic-obj/` |
| 12 | Special Methods for Sequences | `12-seq-hacking/` |
| 13 | Interfaces, Protocols, and ABCs | `13-protocol-abc/` |
| 14 | Inheritance: For Better or For Worse | `14-inheritance/` |
| 15 | More About Type Hints | `15-more-types/` |

The repository's authoritative mapping is `example-code-2e/README.md`.

## How to use this bundle

Read only the chapter file relevant to the code under review, then consult
`framework-patterns.md` for a production analogy. Use `review-checklist.md` before proposing
a refactor. The default order is:

1. Identify the object's public protocol and invariants.
2. Prefer the smallest standard protocol or `typing.Protocol` that expresses the boundary.
3. Add special methods only when they make the object behave naturally in an existing Python
   operation (`len`, iteration, indexing, `with`, `|`, formatting, and so on).
4. Prefer composition or a narrow mixin over deep inheritance.
5. Use static typing to document and check the contract; use runtime validation only at a
   real boundary.
6. Test both the happy path and Python's protocol edge cases: empty input, invalid operands,
   slicing, exceptions, cancellation, and cleanup.

## The high-value pattern set

### P11 — Python data-model object

Implement the smallest coherent set of special methods, keep representation separate from
behavior, and make equality/hash/immutability decisions explicit.

### P12 — Native sequence or mapping behavior

Implement the protocol users already understand (`__len__`, `__getitem__`, iteration,
membership, slicing). Use `collections.abc` when its mixins and invariants fit; do not fake a
full sequence with only one convenient method.

### P13 — Consumer-defined interface

Use `Protocol` for structural, static contracts and ABCs for nominal contracts with shared
implementation, registration, or enforced abstract methods. Keep protocols capability-sized.

### P14 — Cooperative composition

Use composition first. If multiple inheritance is justified, use small stateless mixins,
cooperative `super()`, compatible signatures, and tests that exercise the complete MRO.

### P15 — Precise type boundary

Use `TypedDict` for dictionary-shaped data, generic protocols for reusable capabilities,
variance only when the direction is justified, `@overload` for input/output relationships,
and `cast` only after a runtime invariant has already established the type.

### P18 — Lifecycle companion

Although context managers are in a later Fluent Python 2e chapter, they are the natural
companion to Chapters 11–15 for resource-owning or traced objects. Prefer
`contextlib.contextmanager`/`asynccontextmanager` and guarantee cleanup with `try/finally`.

## Framework evidence

`framework-patterns.md` records concrete uses of these ideas:

- **MLflow:** `ActiveRun`/`ActiveModel` context managers, `PythonModel` ABC, typed overloads,
  and streaming model output.
- **vLLM:** tokenizer `Protocol`, engine ABC, generic output objects, overloads, and async
  generators.
- **Hugging Face:** `ModelOutput` and `BatchEncoding` sequence/mapping behavior,
  `PreTrainedModel`/Hub mixins, and async inference context management.
- **LangChain:** `Runnable` ABC/protocols, `|` composition, callable tools, routers, and
  sync/async streaming.
- **LlamaIndex:** runtime-checkable protocols, ABCs, prompt/instrumentation mixins,
  callback context managers, and generator-based responses.
- **LangGraph:** serializer protocols, typed graph state with `TypedDict`/`Annotated` reducers,
  iterator APIs, and template-method checkpoint savers.
- **AutoGen/AG2:** typed agent APIs, async `AgentRun` context managers, event-condition
  operator DSLs, and function dispatch/registration.

## One integrated example

```python
from collections.abc import AsyncIterator, Iterable, Iterator
from contextlib import asynccontextmanager
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Source(Protocol[T_co]):
    def __iter__(self) -> Iterator[T_co]: ...


class AsyncSource(Protocol[T_co]):
    def __aiter__(self) -> AsyncIterator[T_co]: ...


class Batch(Generic[T]):
    """A small, immutable-ish value object with native sequence behavior."""

    def __init__(self, items: Iterable[T]) -> None:
        self._items = tuple(items)

    def __iter__(self):
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int | slice):
        value = self._items[index]
        return type(self)(value) if isinstance(index, slice) else value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._items!r})"


@asynccontextmanager
async def traced_batch(source: AsyncSource[T]):
    # Acquire tracing/span state here.
    try:
        yield source
    finally:
        # Always close/flush/cancel owned resources here.
        pass
```

Choose mutability/hash semantics deliberately in real code. The design shows the desired
separation: a small protocol at the boundary, a native data model for the value, and a
lifecycle wrapper for ownership.
