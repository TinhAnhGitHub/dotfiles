# Chapter 11 — A Pythonic Object

## Core rule

Design the public behavior first. A Python object is “Pythonic” when it participates naturally
in the operations users already know, while preserving clear invariants and useful debugging
output. Do not add every possible dunder method just because it exists.

## High-value patterns

### 1. Start with a value-object contract

For a small value object, decide these together:

- `__repr__`: unambiguous, useful for debugging, ideally constructor-like.
- `__str__`: user-facing form; omit it if `repr` is already sufficient.
- `__eq__`: compare the semantic value, not incidental storage.
- `__hash__`: define only when the object is immutable for all fields participating in equality.
- `__bool__`: define only when there is an obvious domain meaning for truthiness.
- `__format__`: add when the object has a meaningful display format or multiple coordinate forms.
- `__bytes__`: add when a stable binary representation is part of the API.

The local `Vector2d` progression demonstrates this design in
`11-pythonic-obj/vector2d_v3_prophash.py`: read-only properties, iteration, `repr`, `str`,
`bytes`, equality, hashing, magnitude, truthiness, and formatting are added deliberately rather
than through a generic base class.

### 2. Make equality and hashing obey one invariant

If `a == b`, then `hash(a) == hash(b)` must hold. The safest pattern is to hash the same
immutable value used for equality:

```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, type(self)):
        return NotImplemented
    return (self.x, self.y) == (other.x, other.y)

def __hash__(self) -> int:
    return hash((self.x, self.y))
```

If any equality-participating field can change, do not make the object hashable. Prefer a
frozen value object or leave `__hash__ = None`.

### 3. Use properties to protect representation

Expose a stable public attribute while retaining freedom to change storage internally. The
local vector uses private storage and read-only `@property` accessors. Avoid `__getattr__` or
`__setattr__` interception unless a real dynamic-attribute protocol requires it; if you use
them, delegate ordinary behavior to `super()` and raise a precise `AttributeError`.

### 4. Use `__match_args__` only as a deliberate API

Pattern matching makes positional attributes part of the public contract. Prefer keyword
patterns when the positional order is not obvious. If positional matching is supported, keep
`__match_args__` short, stable, and aligned with the constructor's conceptual fields.

### 5. Prefer class methods for alternate constructors

Use `@classmethod` factories such as `frombytes` when subclasses should receive the factory
result. Use `@staticmethod` only when the operation has no need for class or instance state.

### 6. Keep `repr` deterministic and safe

Do not include secrets, tokens, full prompt contents, or huge payloads in `repr`. Truncate or
summarize large data. Frameworks such as MLflow, LangChain, and LlamaIndex commonly treat
serialization and representation as part of their public object contract; follow that lead.

## Anti-patterns

- Defining `__hash__` on a mutable object.
- Returning `False` from `__eq__` for an unrelated type when `NotImplemented` is correct.
- Making `__repr__` perform I/O or expensive model/API calls.
- Exposing internal mutable lists directly from a value object.
- Using `__getattr__` to hide a typo or silently return `None`.
- Implementing `__bool__` when both “empty” and “invalid/uninitialized” would be conflated.

## Production analogies

- MLflow `Model`/`PyFuncModel`: representation, equality, and controlled public behavior.
- Hugging Face `ModelOutput`: a value-like object with carefully defined serialization and
  indexing semantics.
- LangChain serializable objects and LlamaIndex Pydantic components: framework-provided
  validation/serialization is preferable to duplicating ad hoc dunder logic.
