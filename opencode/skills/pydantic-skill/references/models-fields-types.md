# Models, fields, types, aliases, and configuration

## Decision guide

Use `BaseModel` for a named object, `RootModel[T]` for a named wrapper around one
value, and `TypeAdapter[T]` for a type that does not need model methods. Use
`Annotated` for reusable constraints and nested item constraints.

## Model lifecycle

```python
from pydantic import BaseModel, ConfigDict, Field

class User(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

    id: int
    nickname: str | None = None
    tags: list[str] = Field(default_factory=list)

user = User.model_validate({'id': '7', 'nickname': ' Ada '})
user.model_dump()
user.model_dump_json()
User.model_json_schema(mode='validation')
```

`model_validate()` accepts Python objects; `model_validate_json()` accepts JSON
bytes/strings; `model_validate_strings()` treats an object containing strings like
form/query input. Runtime flags such as `strict`, `extra`, `from_attributes`,
`context`, `by_alias`, and `by_name` can override model configuration for one call.

`model_construct()` creates an object from trusted/prevalidated values without
validation. `model_copy(update=...)` also does not validate the update. Both need
an explicit trust-boundary justification.

## Required, nullable, defaults, and fields

- `x: int` — required and non-nullable.
- `x: int | None` — required but nullable.
- `x: int | None = None` — optional at input and nullable.
- `Field(default_factory=list)` — fresh mutable value per instance.
- `validate_default=True` is needed on `BaseModel` when defaults must go through
  validation and validators. `BaseSettings` validates defaults by default.
- A one-argument `default_factory` can receive already validated data on versions
  that support it; make field order and target-version support explicit.

Prefer:

```python
from typing import Annotated

PositiveId = Annotated[int, Field(gt=0)]

class Order(BaseModel):
    items: list[Annotated[str, Field(min_length=1)]]
    customer_id: PositiveId
```

Do not put field-only metadata in a type alias. `alias`, `default`, and
`deprecated` belong on the field; type constraints and reusable validators belong
in the `Annotated` type. `Field(...)` for required fields can confuse type
checkers; annotation-only fields are clearer.

## Configuration

Use `ConfigDict` for model behavior. Common settings:

- `extra='ignore' | 'allow' | 'forbid'`; typed `__pydantic_extra__` when allowed.
- `strict`, `validate_default`, `validate_assignment`, `revalidate_instances`.
- `from_attributes`, `frozen`, `arbitrary_types_allowed`.
- string transforms and length limits.
- `validate_by_alias`, `validate_by_name`, `serialize_by_alias`.
- temporal/bytes/Infinity JSON settings, `regex_engine`, `cache_strings`, and
  `defer_build` when supported by the target release.

Configuration does not magically propagate through every model boundary. Set it
where the boundary is defined. Call-time `extra` and `strict` overrides are useful
for one-off hardening.

## Aliases

```python
from pydantic import AliasChoices, AliasPath, BaseModel, Field

class Person(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'surname'))
    public_id: str = Field(serialization_alias='id')

person = Person.model_validate({'names': ['Ada'], 'surname': 'Lovelace'})
person.model_dump(by_alias=True)
```

Use `alias` for the same spelling in and out; split with
`validation_alias`/`serialization_alias` when the protocols differ. Use an
`AliasGenerator` for systematic conventions. Explicit field aliases and
`alias_priority` determine generator precedence. Test both input and output—
validation by alias and serialization by alias have different v2 defaults.

## Types and unions

Pydantic validates standard library types, containers, `Literal`, `Enum`, UUID,
temporal values, `Decimal`, URL/email/network types, secrets, `Json[T]`, and
special constrained/strict types. The standard types API is the source of truth
for coercion and strictness; do not infer behavior from Python annotations alone.

For unions:

- `smart` is the v2 default and chooses the best match; its algorithm can evolve.
- `left_to_right` is explicit and order-sensitive; it can turn `'456'` into `456`
  for `int | str` in lax mode.
- Discriminated unions validate one branch and produce clearer schemas/errors:

```python
from typing import Literal
from pydantic import BaseModel, Field

class Cat(BaseModel):
    kind: Literal['cat']
    meows: int

class Dog(BaseModel):
    kind: Literal['dog']
    barks: float

class Pet(BaseModel):
    value: Cat | Dog = Field(discriminator='kind')
```

For a callable discriminator, add `Tag(...)` to every branch and support dicts as
well as already-created model instances because serialization also calls it.

## Strict mode and conversion

Use `strict=True` at call, model, or field level; `StrictInt` and friends are
conveniences for common cases. Strict Python input generally requires instances
of the target type, but strict JSON still accepts JSON representations such as a
date string because JSON has no native date type. Consult the conversion table
for every boundary where coercion matters. Avoid assuming that `bool` is a safe
integer or that strings will never coerce in lax mode.

## Dataclasses, forward references, and calls

`pydantic.dataclasses.dataclass` validates dataclass construction but does not
provide `model_dump*`; wrap it in `TypeAdapter` for validation/serialization.
Generic dataclass parameterizations need a `TypeAdapter` when the parameterized
type itself must be enforced. Standard-library dataclasses receive validation
when used as field types but do not become Pydantic models.

Quoted annotations and `from __future__ import annotations` support forward refs.
For unresolved names define the target and call `model_rebuild()`. Cyclic input is
reported as a validation error (`recursion_loop`), not an uncontrolled recursion.

`@validate_call` validates annotated function arguments. It does not validate
return values unless `validate_return=True` is configured. `.raw_function` bypasses
validation and should stay behind a trusted internal boundary.
