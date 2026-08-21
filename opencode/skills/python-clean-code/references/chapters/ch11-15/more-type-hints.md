# Chapter 15 — More About Type Hints

## Type hints are executable design documentation

Use annotations to make boundaries discoverable and statically checkable. They do not replace
runtime validation for untrusted JSON, model output, plugin code, or network input.

## Select the shape that matches the data

| Data/contract | Type shape |
|---|---|
| Fixed dictionary fields | `TypedDict` |
| Behavior implemented by unrelated classes | `Protocol` |
| A callable's input/output | `Callable`, `ParamSpec`, or a callable Protocol |
| Several input forms with different return types | `@overload` |
| Reusable producer/consumer | Generic class or generic Protocol |
| Narrowing after a checked predicate | `TypeGuard` |
| Value known after a runtime invariant | `cast`, sparingly |

## `TypedDict` for wire-shaped records

```python
from typing import TypedDict


class ToolCall(TypedDict):
    name: str
    arguments: dict[str, object]


def route(call: ToolCall) -> object:
    ...
```

`TypedDict` documents dictionary keys without changing the runtime representation. Validate
untrusted data before treating it as a `ToolCall`; an annotation alone does not validate JSON.

## Overloads for relationships, not convenience

Use overloads when the return type depends on a literal, argument shape, or mode. Keep one
implementation below the overload set and ensure every overload is behaviorally true.

```python
from typing import Literal, overload


@overload
def fetch(*, mode: Literal["raw"]) -> bytes: ...


@overload
def fetch(*, mode: Literal["text"]) -> str: ...


def fetch(*, mode: str) -> bytes | str:
    return b"..." if mode == "raw" else "..."
```

LangGraph's overloaded graph-building methods, vLLM's tokenizer/request overloads, and
Hugging Face's `BatchEncoding.__getitem__` are good production examples.

## Variance

- A producer can usually be covariant: `Source[Sub]` can stand in for `Source[Base]`.
- A consumer can usually be contravariant: `Sink[Base]` can stand in for `Sink[Sub]`.
- A mutable read/write container is usually invariant.

The local cafeteria examples demonstrate why a `BeverageDispenser` is covariant while a
`TrashCan` is contravariant. Do not mark variance merely to silence a type checker; prove the
direction from the methods that use the type variable.

## `cast` is a proof obligation

`cast(T, value)` changes the static view only. Use it after a runtime check, a validated
deserialization step, or a framework invariant that is visible to the reader. If the proof is
not local and obvious, add a type guard or validation function instead.

## Framework typing patterns

- LangChain combines `TypedDict`, overloaded `Runnable` methods, `ParamSpec`, and Protocol
  bounds to keep composable pipelines typed.
- LlamaIndex uses generic ABCs, runtime-checkable Protocols, and `Annotated` metadata for tool
  and prompt schemas.
- LangGraph models state as `TypedDict` fields, often `Annotated[..., reducer]`, so the type
  and state-update semantics travel together.
- AG2 uses overloads and generic agent results to refine the type of `run()`/`ask()` calls.
- MLflow uses overloads/Literals for result modes and typed model/config records.
- vLLM uses generic output objects, Protocols, and overloads for tokenizer/request variants.

## Anti-patterns

- `Any` at every public boundary.
- `cast` immediately after `json.loads` with no validation.
- Overloads that describe an ideal API but not actual runtime behavior.
- Invariant mutable containers marked covariant.
- `TypedDict` used as if it were runtime validation.
- Framework-specific base classes used where a small structural Protocol is enough.
