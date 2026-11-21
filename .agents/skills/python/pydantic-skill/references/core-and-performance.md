# pydantic-core and performance

## Position of the core package

Pydantic defines models and adapters; the Rust-backed `pydantic-core` package
performs validation and serialization through a fixed `core_schema` vocabulary.
Use Pydantic's public API first. Core schemas are a lower-level, release-sensitive
extension: their contents are not a stable interchange format, can change between
minor releases, and the policy expects core to become more internal in v3.

## Main core APIs

`pydantic_core.SchemaValidator(schema, config=...)` exposes:

- `validate_python(value, *, strict, extra, from_attributes, context,
  allow_partial, by_alias, by_name)`;
- `validate_json(data, ...)` and `validate_strings(value, ...)`;
- `isinstance_python(value, ...)` without raising a validation error;
- `validate_assignment(...)` and `get_default_value(...)`.

`SchemaSerializer(schema, config=...)` exposes `to_python(...)` and `to_json(...)`.
Module-level `from_json`, `to_json`, and `to_jsonable_python` are standalone
counterparts. Core `to_json` returns `bytes`.

`ValidationError.errors()` returns machine-oriented details (`type`, `loc`, `msg`,
`input`, optional `ctx`/`url`). `PydanticCustomError`, `PydanticKnownError`,
`PydanticUseDefault`, `PydanticOmit`, `PydanticSerializationError`, and
`PydanticSerializationUnexpectedValue` are the important extension/error tools.

## `core_schema` families

Use constructor functions rather than hand-written dictionaries:

- leaves: `any_schema`, `none_schema`, `bool_schema`, `int_schema`, `float_schema`,
  `decimal_schema`, `str_schema`, bytes/temporal/URL/enum/literal schemas;
- containers: list, tuple, set, frozenset, generator, dict, and (v2.14+) deque,
  OrderedDict, Counter, frozendict, and Fraction schemas; named-tuple schemas
  validate sequences from v2.14.1 and serialize them from v2.14.2;

```python
from fractions import Fraction
from pydantic import TypeAdapter

# v2.14+ native schemas; gate by installed version.
ta = TypeAdapter(Fraction)
assert ta.validate_python('3/4') == Fraction(3, 4)
```
- flow: `nullable_schema`, `union_schema`, `tagged_union_schema`, `chain_schema`,
  `lax_or_strict_schema`, `json_or_python_schema`, `with_default_schema`, and
  `custom_error_schema`;
- functions: before/after/plain/wrap validator and serializer schema builders;
- objects: typed-dict, model, dataclass, arguments/call schemas;
- recursion: `definitions_schema` plus `definition_reference_schema` and `ref`.

For custom Pydantic types use `__get_pydantic_core_schema__`,
`GetPydanticSchema`, and `GetCoreSchemaHandler.generate_schema()` only after
`Annotated`/functional APIs are insufficient. Prefer `handler.generate_schema()`
for generic item types so outer field metadata does not accidentally propagate.

## Partial JSON and string caching

`from_json(data, allow_partial=True)` can return a complete prefix from an
unfinished JSON value and supports streaming/LLM output patterns (partial JSON
parsing, v2.7+). The docs recommend defaults for all model fields and a
`WrapValidator` that raises `PydanticUseDefault` for missing data where
appropriate. This is different from the experimental `experimental_allow_partial`
flag on Pydantic `TypeAdapter` (v2.10+), which may ignore errors in the final
item/field even on complete input. At the core layer the flag is named
`allow_partial` on `SchemaValidator.validate_*`; do not conflate the two. Neither
feature proves that the result is complete; add an application-level completeness
check. `cache_strings` (v2.7+) trades memory for repeated-string speed; measure
rather than enabling it blindly.

## Performance guidance from the official docs

1. Prefer `model_validate_json()`/`validate_json()` for encoded JSON rather than
   `json.loads()` followed by Python validation. Benchmark separately when
   before/wrap model validators dominate, as the docs note an exception.
2. Construct a `TypeAdapter` once and reuse it; schema construction is not free.
3. Prefer concrete `list`/`tuple` and `dict` over abstract `Sequence`/`Mapping` in
   hot validation paths.
4. Use `Any` only when the boundary genuinely needs no validation.
5. Prefer `TypedDict` for lightweight high-throughput shapes when model behavior
   is unnecessary; the docs show a substantial benchmark advantage.
6. Prefer tagged unions, avoid wrap validators in hot paths, and use `FailFast`
   for sequences when first-error behavior is acceptable.
7. Avoid subclassing primitive types to attach state; use a model or a dedicated
   type with an intentional schema.

Benchmark with representative data, error rates, JSON/Python paths, and the
target Python/Pydantic versions. Do not trade away validation, error quality, or
secret redaction for an unmeasured micro-optimization.

## Serializer options

`SchemaSerializer.to_python`/`to_json` and the high-level dump methods accept
`fallback` (a function used when serialization fails), `warnings` (whether to
emit `PydanticSerializationUnexpectedValue`), `exclude_computed_fields`, and
`polymorphic_serialization` (v2.13+, models/dataclasses only). Treat `fallback`
and duck-typed subclass serialization as security-sensitive because they can
expose fields not present in the annotated type.

```python
from pydantic import BaseModel

class Model(BaseModel):
    value: object

model = Model(value=object())  # not JSON-serializable by default
model.model_dump_json(fallback=lambda v: repr(v))  # explicit fallback
```

## Internals worth knowing

- `plugin_settings` provides an interception layer around `validate_python`,
  `validate_json`, and `validate_strings`; plugins are release-sensitive.
- Annotation resolution uses a namespace with defined priority; weak references
  and `_types_namespace` affect `model_rebuild()`. When a forward ref fails,
  define the name in the module namespace and rebuild rather than guessing.
