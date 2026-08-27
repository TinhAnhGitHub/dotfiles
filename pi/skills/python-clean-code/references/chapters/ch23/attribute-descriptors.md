# Chapter 23 — Attribute Descriptors

## P23.1 — Know the lookup precedence

For `obj.name`, Python gives priority to:

1. A data descriptor on the class (`__get__` plus `__set__` or `__delete__`).
2. `obj.__dict__`.
3. A non-data descriptor or ordinary class attribute.

This explains why a data descriptor cannot normally be shadowed by instance assignment, while a
method (a non-data descriptor) can be shadowed by `obj.method = value`.

## P23.2 — Use `__set_name__` to make descriptors reusable

```python
class Quantity:
    def __set_name__(self, owner, name):
        self.storage_name = f"_{owner.__name__}__{name}"
```

The descriptor learns its public field name during class creation. This is safer than passing a
different storage name to every field declaration.

Always handle `instance is None` in `__get__`; class-level access should return the descriptor for
introspection. Store under a collision-resistant private name or directly in the instance dict.

## P23.3 — Centralize repeated validation, not every field

Descriptors are justified when multiple classes/fields share storage and validation policy. For a
single field, a property is usually easier to understand. A reusable descriptor should raise
predictable domain exceptions rather than leak incidental `AttributeError` or `TypeError`.

## Agentic repository evidence

No meaningful repository-owned custom `__get__`, `__set__`, `__delete__`, or `__set_name__`
implementation was verified in the named agentic repositories. That absence matters: they consume
`property`/`cached_property` but do not add descriptor machinery without a strong framework need.

Verified consumers include:

- **LangGraph:** `PregelNode` uses `cached_property` for lazy graph components.
- **DeerFlow:** `SkillCatalog.names` uses a cached computed property.
- **TuriX-CUA:** macOS element wrappers expose ordinary computed properties.

Do not label a property consumer as a custom descriptor implementation. The local Chapter 23
examples are the canonical descriptor evidence.

## Local examples worth comparing

`method_is_descriptor.py` demonstrates that functions become bound methods through `__get__`.
`descriptorkinds.py` contrasts overriding/data descriptors with non-overriding/non-data
descriptors. The `bulkfood` v3–v5 progression builds reusable `Quantity` and `NonBlank` validators.

## Review checklist

- Is a descriptor genuinely reusable across fields/classes?
- Does `__get__` handle class-level access?
- Is data/non-data precedence intentional?
- Is storage separate from the public descriptor name?
- Does failed validation leave previous state intact?
- Are class and instance access both tested?
- Would a property communicate this behavior more clearly?
