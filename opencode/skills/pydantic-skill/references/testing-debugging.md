# Testing and debugging Pydantic behavior

## Focused test matrix

For each model or adapter at an external boundary, cover:

- a valid canonical payload and a nested payload;
- missing required field versus explicit `None`;
- coercible values in lax mode and rejected values in strict mode;
- wrong container item types and union branch selection;
- extra keys for the selected `extra` policy;
- default factories and `validate_default` behavior;
- aliases on input and `model_dump(by_alias=True)` on output;
- Python versus JSON validation/dump paths;
- validation and serialization JSON Schema if it is published;
- assignment validation if enabled;
- forward-reference rebuilds if annotations cross modules;
- secret redaction and subclass serialization if sensitive values exist.

## Stable assertions

Prefer stable error slugs. Locations are useful when they are part of a pinned
application contract, but can change across minor versions, aliases, and
configuration; do not treat them as universally stable:

```python
from pydantic import BaseModel, ValidationError

class Payload(BaseModel):
    count: int

try:
    Payload.model_validate({'count': 'nope'})
except ValidationError as exc:
    errors = exc.errors(include_url=False)
    assert errors[0]['type'] == 'int_parsing'
    assert errors[0]['loc'] == ('count',)  # only if this location is contractual
```

Human messages can vary across versions and locales. Use `include_input=False`
when asserting or logging data that could contain secrets.

## Debugging checklist

1. Print/import the actual package versions, not just the lockfile declaration.
2. Confirm whether the input reached `model_validate`, `model_validate_json`,
   `TypeAdapter`, settings sources, or a framework wrapper.
3. Inspect `Model.model_fields` on the class (instance access is deprecated for
   future v3), aliases, defaults, and `model_config`.
4. Compare `strict=True` and lax behavior and consult the conversion table.
5. For validators, check mode, declaration order, `ValidationInfo.data`, and the
   value returned by every validator.
6. For unresolved annotations, define names then call `model_rebuild()`.
7. For schemas, compare validation versus serialization modes and check whether a
   before/plain/wrap validator declares `json_schema_input_type`.
8. For settings, log source *names and keys* only; never dump source values.
9. Reproduce a failing behavior in a minimal script before changing production
   configuration.

Run the project's formatter, type checker, and pytest suite after the focused
tests. For async settings sources or framework integrations, test concurrency and
side effects separately.
