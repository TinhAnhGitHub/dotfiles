# Chapter 12 — Special Methods for Sequences

## Core rule

Implement the smallest complete protocol that your object promises. If an object looks like a
sequence, users reasonably expect consistent indexing, slicing, iteration, length, membership,
errors, and—if mutable—mutation methods.

## Immutable sequence recipe

```python
from collections.abc import Iterator
from operator import index
from typing import Generic, TypeVar

T = TypeVar("T")


class SequenceValue(Generic[T]):
    def __init__(self, items: tuple[T, ...]) -> None:
        self._items = items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, key: int | slice):
        if isinstance(key, slice):
            return type(self)(self._items[key])
        return self._items[index(key)]
```

Use `operator.index`, not `int`, when a value must be an integer index. `int(2.5)` silently
truncates; `operator.index(2.5)` rejects it and still accepts integer-like objects such as
NumPy integer scalars.

## Protocol details that must agree

- `__len__` returns a non-negative integer and controls `bool(obj)` unless `__bool__` exists.
- `__getitem__` should accept integer indices and, when promised, slices.
- A slice should normally return the same conceptual type, not an unrelated list.
- Out-of-range integer access raises `IndexError`; invalid index types raise `TypeError`.
- `__iter__` should yield values, not expose storage internals.
- `__contains__` is optional; if absent, Python may fall back to iteration or indexed access.
- Mutable sequences need coherent `__setitem__`, `__delitem__`, and insertion semantics.
- Mapping-like objects need consistent `__getitem__`, `get`, `__contains__`, `update`, and
  missing-key behavior.

## Use the standard ABC when it fits

Subclass `collections.abc.Sequence` or `MutableSequence` when you want its documented mixins
and are prepared to satisfy its contract. The local `frenchdeck2.py` and the book's vector
examples show the difference between a small informal protocol and a full sequence surface.

Do not inherit from an ABC merely to make a type annotation look official. A narrow
`Protocol` is often better for a consumer that only needs `__getitem__` and `__len__`.

## Mapping subclass warning

Built-in subclasses can bypass overridden methods in surprising paths. The local
`14-inheritance/strkeydict_dictsub.py` demonstrates a `dict` subclass that must override
`__missing__`, `__contains__`, `__setitem__`, `get`, and `update` to maintain its string-key
invariant. Prefer `collections.UserDict` or composition when normalization must apply to every
mutation path and you do not need the exact built-in type.

## Framework analogies

- Hugging Face `ModelOutput` and `BatchEncoding` are strong examples of carefully controlled
  mapping/sequence hybrids with overloads for string, integer, and slice access.
- LangGraph's typed state is usually a mapping-shaped `TypedDict`, while its checkpoint APIs
  expose iterator/async-iterator methods rather than pretending the saver is a sequence.
- vLLM streams outputs through async generators instead of making output objects themselves
  iterable; keep the stream protocol separate from the value object when that is clearer.

## Anti-patterns

- Implementing only `__getitem__` and advertising “list-like” behavior.
- Returning a mutable internal list from a supposedly immutable object.
- Accepting floats or strings as indices by coercing with `int`.
- Returning `NotImplemented` for an invalid index instead of raising `TypeError`.
- Overriding one mapping method while allowing inherited methods to violate normalization.
