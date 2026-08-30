---
name: pydantic-skill
description: >-
  Use when Pydantic behavior is central to a Python task: validation, schemas,
  serialization, settings, or typed boundaries. Trigger whenever the user mentions
  Pydantic, BaseModel, BaseSettings, SettingsConfigDict, Field, ConfigDict,
  ValidationError, TypeAdapter, RootModel, model_validate, model_dump,
  model_json_schema, field_validator, model_validator, pydantic.v1, pydantic-core,
  pydantic-settings, pydantic-extra-types, Pydantic-backed FastAPI request or
  response models, DTOs, ORM validation, or a v1-to-v2 migration. Prefer this
  skill over generic Python typing, JSON, dotenv, FastAPI, or ORM advice whenever
  Pydantic behavior is central; do not trigger for unrelated work merely because
  a repository happens to contain Pydantic.
compatibility: Pydantic v2/current documentation; inspect the project's pinned versions before using release-sensitive APIs.
---

# Pydantic skill

Use this skill to design, implement, migrate, debug, review, and test Pydantic
models and the packages around them. Treat validation as a trust-boundary
operation: it produces typed output, but it is not authorization, a database
constraint, or a substitute for domain invariants.

## First: establish the version and boundary

1. Inspect `pyproject.toml`, `uv.lock`, `poetry.lock`, `requirements*.txt`, imports,
   and the installed environment. Identify the Python version and the versions of
   `pydantic`, `pydantic-core`, `pydantic-settings`, and `pydantic-extra-types`
   separately. Prefer the project's interpreter for runtime checks; do not use an
   unrelated global environment as evidence.
2. Read `references/current-docs.md` for release-sensitive lookups, unknown
   versions, or documentation citations; otherwise load only the routed reference.
   The `latest` documentation is a rolling reference, not proof that an API exists
   in the repository's version.
3. Gate newer APIs explicitly: partial JSON parsing is v2.7+, experimental partial
   validation is v2.10+, `validate_by_*` and `serialize_by_alias` are v2.11+,
   and `polymorphic_serialization` is v2.13+. Use the compatible alternative
   rather than silently upgrading.
4. Never silently upgrade or downgrade dependencies. If a version is unknown,
   state that it is unknown and prefer stable v2 APIs. Pydantic v2 supports Python
   3.9+, but the examples in this skill use Python 3.10 union syntax; use
   `Optional`/`Union` syntax or add a future-annotations import on Python 3.9.
5. Keep `BaseModel`/validation DTOs separate from persistence models, domain
   behavior, secrets handling, and authorization decisions.

For release-sensitive questions, consult the official Pydantic docs or Context7
(`/pydantic/pydantic`, `/pydantic/pydantic-settings`) and cite the page used.
Read the narrow reference file below rather than loading the whole corpus into
context.

## Classify the request and choose the smallest abstraction

| Need | Prefer |
|---|---|
| Named, structured validated object | `BaseModel` |
| One validated root value with a named type | `RootModel[T]` |
| An arbitrary collection, union, `TypedDict`, or dataclass | `TypeAdapter[T]` |
| Reusable constraints or validation | `Annotated[T, Field(...)]` and functional validators |
| Application configuration | `BaseSettings` from `pydantic-settings` |
| Runtime model creation | `create_model()` only when the schema is genuinely dynamic and annotations are trusted |
| Low-level schema engine work | `pydantic-core` only with a concrete reason; prefer Pydantic hooks |

Read the relevant references:

| Situation | Read |
|---|---|
| Release-sensitive lookup, unknown version, or citation | `references/current-docs.md` |
| Models, fields, aliases, config, types, unions, strictness, dataclasses | `references/models-fields-types.md` |
| Validators, JSON, serialization, JSON Schema, errors, custom types | `references/validation-serialization-schema.md` |
| Environment, dotenv, secrets, CLI, custom settings sources | `references/settings.md` |
| `pydantic-extra-types` values or installation | `references/extra-types.md` |
| `pydantic-core`, partial JSON, custom core schemas, performance | `references/core-and-performance.md` |
| Official examples and integrations | `references/examples.md` |
| v1 APIs or migration | `references/migration.md` |
| Regression tests, debugging, or error assertions | `references/testing-debugging.md` |

## Implementation rules

### Models and fields

- Declare fields with annotations. `x: T | None` is nullable but still required;
  give it `= None` when it may be omitted.
- Use `model_validate()`, `model_validate_json()`, and `model_validate_strings()`;
  use `model_dump()`, `model_dump_json()`, and `model_json_schema()`.
- Use `model_config = ConfigDict(...)`, not the deprecated v1 inner `Config`.
- Prefer `Annotated` for reusable/type-level constraints and item constraints:
  `list[Annotated[int, Field(gt=0)]]`. Keep field metadata (aliases, defaults,
  deprecation) on the field itself.
- Use `Field(default_factory=...)` for mutable defaults. Defaults on `BaseModel`
  are not validated unless `validate_default=True`; settings defaults are
  validated by default.
- Make `extra`, `strict`, `from_attributes`, `validate_assignment`, aliases,
  default validation, and revalidation explicit at an external-data boundary.
- `model_construct()` and `model_copy(update=...)` skip validation. Use them only
  for trusted data and say so in code review.
- `create_model()` may evaluate string annotations. Never derive string annotations
  or other executable model definitions from untrusted input.

### Validation, unions, and custom types

- Use `@field_validator` for one or more fields and `@model_validator` for
  cross-field invariants. After validators receive validated values and must
  return them; after model validators must return `self`.
- Choose validator modes deliberately: `after` for type-safe post-validation,
  `before` for raw input normalization, `plain` only when intentionally replacing
  Pydantic's validation, and `wrap` when you must call/catch the inner handler.
- `ValidationInfo.data` contains only earlier validated fields, so field order is
  part of a cross-field validator's behavior. Avoid mutating raw values before a
  union branch can inspect them. Do not use `assert` for security-critical rules.
- Prefer discriminated unions for predictable behavior, useful errors, and speed.
  Use `Field(discriminator=...)` with `Literal` tags, or `Tag` plus a callable
  `Discriminator` that handles both dict and model inputs.
- Start custom types with `Annotated`, `Field`, `annotated-types`,
  `AfterValidator`, serializers, and `WithJsonSchema`. Use
  `__get_pydantic_core_schema__`/`GetPydanticSchema` only when those are not enough.

### JSON, schemas, and serialization

- For an already encoded JSON payload, prefer `Model.model_validate_json(data)`
  or `TypeAdapter.validate_json(data)`; it avoids an intermediate `json.loads`
  object and has the documented strict-JSON behavior.
- Distinguish `model_json_schema()` (a schema dict) from `model_dump_json()` (a
  JSON string). Generate validation and serialization schemas separately when
  consumers need to know accepted input versus emitted output.
- `model_dump()` defaults to Python mode; `mode='json'` produces JSON-compatible
  values. `BaseModel.model_dump_json()` returns `str`; `TypeAdapter.dump_json()`
  returns `bytes`.
- Use `field_serializer`/`model_serializer` or annotated serializers instead of
  deprecated `json_encoders`. Treat `serialize_as_any=True` and polymorphic output
  as security-sensitive because subclass fields can become visible.
- Use `by_alias=True` intentionally. Current v2 serialization-by-alias defaults
  differ from validation and are expected to change in v3; pin behavior in tests.

### Settings

- Import `BaseSettings` and `SettingsConfigDict` from `pydantic-settings`, never
  from `pydantic`. Read `references/settings.md` before designing source priority.
- Document precedence (CLI, init, environment, dotenv, secrets, defaults), the
  JSON encoding required for complex environment values, and any nested delimiter.
- Never log settings with secrets. Debug mode and CLI arguments can expose secret
  values; prefer secret managers or mounted secret files for credentials.

## Verification workflow

For an implementation or review, verify the behavior that matters rather than
only importing the model:

1. Valid input and representative nested input.
2. Missing versus nullable fields and default factories.
3. Invalid input with `ValidationError.errors()`; assert the stable machine error
   `type`. Assert `loc` only when the location is part of the pinned application
   contract, because minor releases/configuration can change locations.
4. Lax versus strict Python input, and strict JSON input when relevant.
5. Aliases on input and output, including `by_alias` and generated schema.
6. Python-mode versus JSON-mode dumps; redaction of secrets and subclass fields.
7. `model_json_schema(mode='validation')` and `mode='serialization'` when schemas
   are consumed by another service or tool.
8. Settings source precedence, nested env parsing, dotenv behavior, and secret
   paths without printing secret values.
9. Forward references, `model_rebuild()`, assignment validation, and union branch
   selection when those features are used.
10. Project formatter, type checker, and test suite. Run a focused example first
    when a release-sensitive API is involved.

## Response contract

Choose the format that matches the request:

- **Implementation:** detected (or explicitly unknown) versions and boundary,
  abstraction choice, code/tests, verification, and residual risks.
- **Review:** findings first with severity and `path:line`, followed by assumptions
  and residual risks.
- **Explanation:** behavior, relevant version caveat, and a minimal runnable
  example.

In all formats, state applicable coercion, strictness, aliases, defaults,
extra-field policy, and serialization choices. Do not claim documentation, tests,
or a live environment was checked unless it was actually checked. Keep examples
runnable and include imports.
