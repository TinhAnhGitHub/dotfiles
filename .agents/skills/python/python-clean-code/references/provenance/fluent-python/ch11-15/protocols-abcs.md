# Chapter 13 — Interfaces, Protocols, and ABCs

## Decision rule

Choose the mechanism based on what the boundary needs:

| Need | Prefer |
|---|---|
| A function only needs a few capabilities | `typing.Protocol` |
| Third-party implementations should work without inheritance | `Protocol` |
| Shared implementation and enforced abstract methods | `abc.ABC` |
| Runtime registration of a known external class | ABC `.register()` |
| Runtime capability detection | `@runtime_checkable` Protocol, with validation caveats |
| A built-in protocol already exists | `collections.abc` / `typing` `Supports*` |

## Capability-sized protocols

Define the protocol from the consumer's needs, not from the largest implementation:

```python
from collections.abc import Iterable
from typing import Protocol, TypeVar

T = TypeVar("T")


class Picker(Protocol[T]):
    def pick(self) -> T: ...


class Loader(Protocol[T]):
    def load(self, items: Iterable[T]) -> None: ...
```

Compose capabilities when a consumer truly needs both:

```python
class LoadablePicker(Picker[T], Loader[T], Protocol[T]):
    pass
```

This follows the local `randompick.py`, `randompickload.py`, and generic picker examples.

## Generic protocol rules

- Use a covariant type variable when the protocol only produces `T`.
- Use a contravariant type variable when it only consumes `T`.
- Keep a type variable invariant when it is both read and written.
- Bind a `TypeVar` to a protocol when a function must preserve the concrete input type, as in
  the local `double_protocol.py`.
- Do not use `Any` to hide an unclear contract; parameterize the protocol instead.

Example:

```python
from typing import Protocol, TypeVar

T = TypeVar("T")


class Repeatable(Protocol):
    def __mul__(self: T, count: int) -> T: ...


R = TypeVar("R", bound=Repeatable)


def double(value: R) -> R:
    return value * 2
```

## ABCs and template methods

Use an ABC when the abstraction owns an invariant or reusable algorithm:

```python
from abc import ABC, abstractmethod


class Store(ABC):
    @abstractmethod
    def put(self, key: str, value: bytes) -> None: ...

    def has(self, key: str) -> bool:
        try:
            self.get(key)
        except KeyError:
            return False
        return True

    @abstractmethod
    def get(self, key: str) -> bytes: ...
```

The local `tombola.py` is the canonical example: abstract `load`/`pick` methods support
concrete `loaded`/`inspect` algorithms. `tombolist.py` shows virtual registration for a class
that supplies the required behavior without inheriting the implementation.

## Runtime protocol caution

`@runtime_checkable` is a shallow capability check. `isinstance(x, Protocol)` confirms required
attributes exist; it does not prove argument signatures, return types, semantic invariants, or
side effects. Use it for dispatch at a boundary, then validate the actual operation and handle
failure. Prefer static checking for normal application code.

## Keep protocols behavioral

Document semantics, not just names:

- Does `pick()` raise `LookupError` when empty?
- Does `load()` consume the iterable once or retain it?
- Is `close()` idempotent?
- Is a stream single-pass?
- Does a method mutate the object or return a new value?

The type checker cannot express most of these rules. Tests and docstrings are part of the
interface.

## Production analogies

- **vLLM:** `TokenizerLike(Protocol)` for structural tokenizer behavior; `EngineClient(ABC)`
  for a lifecycle-heavy engine boundary.
- **LlamaIndex:** runtime-checkable `VectorStore` Protocol beside an ABC-based vector-store
  base class—an excellent direct comparison.
- **LangChain:** `Runnable` ABC plus small callable Protocols such as `SupportsAdd`.
- **LangGraph:** `SerializerProtocol` lets pickle/JSON/orjson-compatible implementations plug
  in without inheriting a framework class.
- **Hugging Face Hub:** dataclass-shaped Protocols describe model configuration capabilities.

## Anti-patterns

- A “god protocol” with unrelated methods.
- `@runtime_checkable` used as a substitute for input validation.
- An ABC used only as a nominal label when no shared behavior or invariant exists.
- `Any` everywhere because generic variance was not designed.
- Protocol methods whose annotations disagree with the actual runtime semantics.
