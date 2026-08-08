# Pydantic v1 to v2 migration

Read the official migration guide:
<https://pydantic.dev/docs/validation/latest/get-started/migration/>.

## Core mapping

| v1 | v2 |
|---|---|
| `parse_obj` | `model_validate` |
| `parse_raw` | `model_validate_json` |
| `parse_obj_as` | `TypeAdapter(T).validate_python(...)` |
| `dict()` | `model_dump()` |
| `json()` | `model_dump_json()` |
| `schema()` / `schema_json()` | `model_json_schema()` / serialize the schema dict |
| inner `Config` | `model_config = ConfigDict(...)` |
| `orm_mode=True` / `from_orm` | `from_attributes=True` + `model_validate` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |
| `@validate_arguments` | `@validate_call` |
| `__root__` | `RootModel[T]` |
| `GenericModel` | standard `BaseModel` generics (`class Box[T](BaseModel)` on Python 3.12+, `TypeVar`/`Generic` syntax on older Python) |
| `__get_validators__` / `__modify_schema__` | core-schema and JSON-schema hooks, or better `Annotated` APIs |
| `json_encoders` | field/model serializers |
| `each_item=True` | annotate the item type, e.g. `list[Annotated[T, ...]]` |
| `allow_mutation=False` | `frozen=True` |
| `min_items`/`max_items` | `min_length`/`max_length` |
| `Field(regex=...)` | `Field(pattern=...)` |
| `schema_extra` | `json_schema_extra` |
| `Constrained*` helpers | `Annotated[T, Field(...)]` or `StringConstraints` |
| `parse_file` / `parse_raw` | load explicitly, then `model_validate`/`model_validate_json` |
| `BaseSettings.parse_env_var` | settings source customization, `NoDecode`, or a validator |

V1 extra types such as `Color` and `PaymentCardNumber` moved to the separate
`pydantic-extra-types` package. V1 `allow_population_by_field_name` maps to
`populate_by_name` for older v2 releases, then to explicit
`validate_by_name=True` plus `validate_by_alias=True` on v2.11+.

## Migration cautions

- Optional annotations no longer imply a `None` default. Preserve intended
  required/nullable semantics explicitly.
- v2 validators no longer accept v1 `field`/`config` parameters; use
  `ValidationInfo` and `info.field_name`/`info.config`.
- `TypeError` raised by a validator is not silently converted to a
  `ValidationError`; raise a deliberate validation exception.
- `@model_validator(mode='before')` sees raw input and may receive a non-dict
  object under assignment/from-attributes flows. `mode='after'` must return `self`.
- `from_attributes=True` enables attribute lookup; it does not solve ORM lazy
  loading or serialization side effects.
- URL types may no longer be `str` subclasses; call `str(url)` at string-only
  boundaries.
- Regex defaults use Rust's regex engine, so lookarounds/backreferences may need
  `regex_engine='python-re'`.
- Do not mix v1 and v2 model instances. Use `pydantic.v1` only for deliberate,
  temporary compatibility boundaries.

## Migration workflow

1. Inventory deprecated imports, decorators, config names, root models, custom
   validators, and serialization hooks.
2. Migrate one boundary at a time and preserve tests for requiredness, coercion,
   aliases, error locations, serialization, and schemas.
3. Check the installed package versions before using APIs added in later v2
   minors. Do not treat the rolling latest docs as a compatibility promise.
4. Remove compatibility shims only after all consumers and serialized contracts
   are updated.
