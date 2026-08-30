# Chapter 22 — Dynamic Attributes and Properties

## P22.1 — Use properties for stable attribute APIs

A property preserves attribute syntax while adding validation, computation, or controlled
mutation. Keep the invariant local and make invalid assignments fail before state changes.

Use `functools.cached_property` for a computed value that is expensive, stable for the instance,
and naturally invalidated by deleting the cached attribute. Document lifetime and invalidation;
`@cache` over a property retains strong references to instances and has no natural per-instance
clear operation.

## P22.2 — Use `__getattr__` only as a narrow fallback

`__getattr__` runs only after normal lookup fails. A JSON façade can use it to translate keys into
attribute access, but it must raise `AttributeError` for missing names so `hasattr` and normal
introspection keep their expected behavior. Guard collisions with methods such as `keys`, `items`,
and `get`, and adapt only valid Python identifiers.

Do not use `__getattribute__` when a property or `__getattr__` is enough; intercepting every lookup
makes debugging and recursion hazards much harder.

## P22.3 — Treat `__new__` as object construction, not initialization

`__new__` may return an instance of a different type, which is how the local `FrozenJSON` examples
turn mappings into façade objects and lists/primitives into their natural values. `__init__` only
runs when `__new__` returns an instance of the requested class. This is powerful for immutable
types, interning, and polymorphic construction, but a named factory is often clearer.

## Agentic repository evidence

- **LlamaIndex Workflows:** `DictLikeModel` stores undeclared event fields in `_data` and exposes
  them through `__getattr__`/`__setattr__`.
- **AG2/AutoGen:** `LLMConfig` forwards unknown attributes to its Pydantic model and redirects
  assignments.
- **LangGraph:** module-level `__getattr__` lazily exposes deprecated/constants, while `PregelNode`
  uses `cached_property` for lazy graph components.
- **DeerFlow:** package `__getattr__` lazily exposes agent implementations; `SkillCatalog.names`
  is a cached computed property on a frozen dataclass.
- **ClawGUI Nanobot:** provider implementations are lazily imported through module `__getattr__`.
- **Agent-S, ShowUI, TongUI-agent, and TuriX-CUA:** use ordinary properties but no meaningful
  custom dynamic-attribute protocol was verified; do not invent one from incidental properties.

## Local examples worth comparing

The `bulkfood` progression moves from public attributes to validated properties and then to
reusable descriptors. The OSCON schedule progression compares lazy properties, manual caches,
`cached_property`, and cached functions. `FrozenJSON` demonstrates the convenience and hazards of
attribute-style access over external mappings.

## Review checklist

- Is a property clearer than a method for this stable value-like attribute?
- Does a setter validate before mutating?
- Does cached state have an explicit invalidation policy?
- Does missing dynamic data raise `AttributeError`?
- Can JSON keys collide with methods or invalid identifiers?
- Is `__new__` really needed, or would a named factory explain the type change better?
- Is `__dict__` mutation bypassing validation or internal invariants?
