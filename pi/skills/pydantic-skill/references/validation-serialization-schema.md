# Validation, JSON, serialization, schemas, and errors

## Validator selection

| Need | Tool |
|---|---|
| Normalize/check one field after type validation | `@field_validator(..., mode='after')` |
| Inspect raw input before Pydantic parses it | `mode='before'` |
| Replace Pydantic's validation intentionally | `mode='plain'` |
| Retry, branch, or catch inner errors | `mode='wrap'` |
| Invariant across fields | `@model_validator(mode='after')` |
| Normalize a whole raw object | `@model_validator(mode='before')` |
| Reusable type behavior | `Annotated[T, BeforeValidator/AfterValidator/WrapValidator]` |

```python
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

class Credentials(BaseModel):
    password: str
    password_repeat: str

    @field_validator('password')
    @classmethod
    def nonempty(cls, value: str) -> str:
        if not value:
            raise ValueError('password must not be empty')
        return value

    @model_validator(mode='after')
    def match(self) -> 'Credentials':
        if self.password != self.password_repeat:
            raise ValueError('passwords do not match')
        return self
```

`ValidationInfo.data` contains only fields already validated in declaration
order. `ValidationInfo.context` comes from `model_validate(..., context=...)`.
Raise `ValueError`, `AssertionError` only for non-critical convenience checks, or
`PydanticCustomError` for structured error types/messages. `TypeError` is not a
general replacement for validation errors in v2. Avoid mutating a raw input in a
before/wrap validator and then raising, since another union branch may see the
mutation. Validators must return the value they intend to keep.

## JSON and partial JSON

Use `model_validate_json()`/`TypeAdapter.validate_json()` for encoded input. JSON
and Python validation are not interchangeable in strict mode because JSON has no
date, tuple, or bytes type. `pydantic_core.from_json(..., allow_partial=True)` is
available for incomplete/streamed JSON; pair it with defaults and, when needed,
`PydanticUseDefault` so missing trailing fields become defaults rather than
fatal errors. Gate this feature by the target version.

Do not confuse that **partial JSON parsing** (v2.7+) with the experimental
`experimental_allow_partial` validation mode (v2.10+). The latter can ignore some
errors in the final item/field, including on otherwise complete input. Both are
advanced recovery tools, not an indication that an incomplete or partially
accepted payload is complete or safe to use without an application-level check.

`Json[T]` is a field type for a JSON string that should be parsed into `T`.
`round_trip=True` preserves a re-validatable representation during serialization.

## Serialization

- `model_dump(mode='python')` keeps Python values such as tuples and dates.
- `model_dump(mode='json')` returns JSON-compatible Python values.
- `model_dump_json()` returns a JSON `str`.
- `TypeAdapter.dump_python()`/`dump_json()` provide the same boundary for
  arbitrary types; adapter JSON output is `bytes`.
- `include`, `exclude`, `exclude_unset`, `exclude_defaults`, `exclude_none`,
  `exclude_computed_fields`, `round_trip`, `context`, and `by_alias` are separate
  switches; test the combination actually required by the protocol.

Use `field_serializer` for one field and `model_serializer` for a model-wide
representation. Plain serializers replace the inner serializer; wrap serializers
receive a handler and should call it unless intentionally short-circuiting. One
serializer per field/model is supported. Prefer serializers over deprecated
`json_encoders`.

Pydantic v2 serializes a subclass according to the annotated field type by
default, which helps prevent accidental secret-field leakage. `SerializeAsAny`
and `serialize_as_any=True` opt into broad duck-typed serialization. The newer
`polymorphic_serialization` option (v2.13+) is a narrower model/dataclass feature;
it is not a synonym for `serialize_as_any`. Use either only with a security review,
an exact version gate, and tests for subclass-sensitive fields.

## JSON Schema

`Model.model_json_schema()` and `TypeAdapter.json_schema()` return JSON-compatible
dictionaries. Use `mode='validation'` to describe accepted input and
`mode='serialization'` to describe emitted output; computed fields generally
appear only in the latter. `Field` metadata, `WithJsonSchema`, `SkipJsonSchema`,
`json_schema_extra`, and a `GenerateJsonSchema` subclass cover local-to-global
customization. Use `json_schema_input_type` on before/plain/wrap validators when
the accepted raw input differs from the annotated output type.

Do not confuse a schema dict with serialized model data. `$defs`/`$ref`, union
`anyOf`, aliases, requiredness, and validation/serialization modes are part of the
consumer contract; snapshot or contract-test them when another system depends on
them.

## Errors and debugging

Catch `pydantic.ValidationError` (the pydantic-core error is re-exported). Use:

```python
try:
    Model.model_validate(payload)
except ValidationError as exc:
    for error in exc.errors(include_url=False):
        print(error['type'], error['loc'], error.get('ctx'))
```

Error dictionaries contain a stable machine-oriented `type`, a location tuple,
message, input, optional context, and an error URL. Prefer asserting `type` in
cross-version tests. Assert `loc` only when it is part of a pinned application
contract: locations and human details can change with minor versions, aliases,
and configuration. `include_input=False` removes input from the structured error
details returned by that call; `hide_input_in_errors=True` primarily changes the
rendered error text, so do not treat it as a complete structured-data redaction
mechanism. Use both deliberately when inputs may contain secrets or personal data.

## Custom types

Start here, from least to most coupled:

1. `Annotated` + `Field`/`annotated-types`.
2. Annotated functional validators/serializers and `WithJsonSchema`.
3. `GetPydanticSchema` or a frozen marker class with
   `__get_pydantic_core_schema__`/`__get_pydantic_json_schema__`.
4. A custom type implementing those hooks.

For generic custom types, use `handler.generate_schema(item_type)` for an
unrelated item schema so outer metadata does not leak into the item. Prefer the
high-level layers because core-schema hooks are a lower-stability v2 extension.
