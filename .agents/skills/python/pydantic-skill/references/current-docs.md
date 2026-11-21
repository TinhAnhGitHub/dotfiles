# Current Pydantic documentation map

Read this file first. It is a source map and compatibility guard, not a copy of
the full documentation. The official corpus is deliberately linked so a task can
follow the exact API page for the installed release.

## Canonical sources

- Validation docs: <https://pydantic.dev/docs/validation/latest/>
- Full machine-readable corpus: <https://pydantic.dev/docs/validation/latest/llms-full.txt>
- Page index: <https://pydantic.dev/docs/validation/latest/llms.txt>
- Migration: <https://pydantic.dev/docs/validation/latest/get-started/migration/>
- Version policy: <https://pydantic.dev/docs/validation/latest/get-started/version-policy/>
- Examples index: <https://pydantic.dev/docs/validation/latest/llms.txt> (search `examples/`)
- Example page: <https://pydantic.dev/docs/validation/latest/examples/custom_validators/index.md>
- Pydantic API page: <https://pydantic.dev/docs/validation/latest/api/pydantic/base_model/index.md>
- pydantic-core API: <https://pydantic.dev/docs/validation/latest/api/pydantic-core/pydantic_core/index.md>
- `core_schema`: <https://pydantic.dev/docs/validation/latest/api/pydantic-core/pydantic_core_schema/index.md>
- Settings API: <https://pydantic.dev/docs/validation/latest/api/pydantic_settings/index.md>
- Extra types API page: <https://pydantic.dev/docs/validation/latest/api/pydantic-extra-types/pydantic_extra_types_color/index.md>
- Pydantic GitHub: <https://github.com/pydantic/pydantic>
- pydantic-settings GitHub: <https://github.com/pydantic/pydantic-settings>
- pydantic-extra-types GitHub: <https://github.com/pydantic/pydantic-extra-types>

Use the exact concrete page and append `/index.md` for clean markdown. Some root
landing URLs under `examples/`, `api/pydantic/`, and `api/pydantic-extra-types/`
are not published even though their child pages are. The current docs use the
unpinned `latest` path; determine the repository's versions before copying an API
into code. When fetching from pydantic.dev, include a short `goal` query parameter
when practical; never include secrets or private project details.

## Requested concepts

| Concept | Official page |
|---|---|
| Models | `concepts/models/` |
| Fields | `concepts/fields/` |
| JSON Schema | `concepts/json_schema/` |
| JSON parsing | `concepts/json/` |
| Types and custom types | `concepts/types/` |
| Unions | `concepts/unions/` |
| Aliases | `concepts/alias/` |
| Configuration | `concepts/config/` |
| Serialization | `concepts/serialization/` |
| Validators | `concepts/validators/` |
| Dataclasses | `concepts/dataclasses/` |
| Forward annotations | `concepts/forward_annotations/` |
| Strict mode | `concepts/strict_mode/` |
| TypeAdapter | `concepts/type_adapter/` |
| Validation decorator | `concepts/validation_decorator/` |
| Conversion table | `concepts/conversion_table/` |
| Experimental APIs | `concepts/experimental/` |
| Settings management | `concepts/pydantic_settings/` |
| Performance | `concepts/performance/` |

Related error pages are `errors/errors/`, `errors/usage_errors/`,
`errors/validation_errors/`, and `errors/troubleshooting/` (Logfire-based
recurrence analysis, alerts, and scrubbing rejected `input` values). Internals
that matter for custom types are `internals/architecture/` (including the
`plugin_settings` interception layer) and `internals/resolving_annotations/`.

Useful get-started pages are `get-started/install/`, `get-started/changelog/`,
`get-started/migration/`, and `get-started/version-policy/`.

## Pydantic API coverage

The API index includes these modules. Use the exact module page rather than
guessing a signature:

- `aliases` — `AliasPath`, `AliasChoices`, `AliasGenerator`.
- `annotated_handlers` — `GetCoreSchemaHandler`, `GetJsonSchemaHandler`.
- `base_model` — `BaseModel`, `create_model`, model lifecycle/validation/dump APIs.
- `config` — `ConfigDict`, `with_config`.
- `dataclasses` — Pydantic dataclass decorator and rebuild helpers.
- `errors` — usage/schema errors; `ValidationError.error_count()`, filtered
  `errors()`/`json()`, and `from_exception_data()`.
- `experimental` — opt-in APIs: `pydantic.experimental.pipeline` (`validate_as`,
  `transform`, `predicate`, constraints, `then`/`otherwise`, `|`/`&`, v2.8+) and
  `arguments_schema.generate_arguments_schema()` (v2.11+). Both are unstable.
- `fields` — `Field`, `FieldInfo` (`get_default(validated_data=...)`,
  `default_factory_takes_validated_data`, `asdict()`), `PrivateAttr`,
  `computed_field` (`exclude_if=` on v2.13+).
- `functional_serializers` — `field_serializer`, `model_serializer`, serializer markers.
- `functional_validators` — `field_validator`, `model_validator`, validator
  markers (`InstanceOf`, `SkipValidation`, `ValidateAs` on v2.12+),
  `json_schema_input_type` (v2.9+).
- `functional_serializers` — `field_serializer`, `model_serializer`,
  `PlainSerializer`, `WrapSerializer`, `SerializeAsAny`, `when_used`.
- `json_schema` — `GenerateJsonSchema`, `models_json_schema`, `ref_template`,
  title generators, schema utilities and handlers.
- `networks` — URL, DSN, email, and IP types.
- `root_model` — `RootModel`.
- `standard_library_types` — behavior for Python standard-library annotations.
- `type_adapter` — `TypeAdapter`.
- `types` — strict, secret, JSON, temporal, encoded, discriminator, and constraints.
- `validate_call` — `validate_call` and call validation helpers.
- `version` — runtime version information.

## Core, settings, and extra-types API coverage

`pydantic-core` has two main API pages:

- `pydantic_core/` — `SchemaValidator`, `SchemaSerializer`, `ValidationError`,
  `from_json`, `to_json`, `to_jsonable_python`, URL primitives, and error types.
- `pydantic_core_schema/` — schema constructors for primitives, containers,
  unions, tagged unions, models, dataclasses, function validators, serializers,
  defaults, JSON/Python branches, and definitions/ref recursion.

`pydantic-settings` covers `BaseSettings`, `SettingsConfigDict`, source classes,
CLI helpers, config-file sources, secrets sources, and customization hooks.

`pydantic-extra-types` pages cover Color, Coordinate, Country, Currency, ISBN,
Language, MAC address, Payment, Pendulum, Phone Numbers, ABA Routing Number,
Script Code, Semantic Version, Timezone Name, and ULID. Some package modules may
be newer or not yet in the API index; verify the installed package before relying
on them.

## Compatibility facts to check

- Research snapshot of the rolling docs: Pydantic v2.14.4 (pydantic-settings
  v2.16.3). Treat this as a date-stamped observation, not a project requirement.
- v2 uses `model_validate`, `model_dump`, `model_json_schema`, `ConfigDict`,
  `field_validator`, and `model_validator`; v1 names are deprecated or removed.
- `populate_by_name` is discouraged from v2.11; use `validate_by_alias` and
  `validate_by_name` when the target version supports them.
- `serialize_by_alias` is currently opt-in in v2 and expected to default to true
  in v3; pin output behavior explicitly.
- `TypeAdapter.dump_json()` returns `bytes`; `BaseModel.model_dump_json()` returns
  `str`.
- Newer features include partial JSON and `cache_strings` (v2.7), `FailFast` and
  the experimental pipeline API (v2.8), `json_schema_extra` merging from
  `Annotated` (v2.9), validated-data default factories, `TypeAdapter.rebuild()`,
  `Unpack` call validation and experimental partial validation (v2.10), named
  type aliases, `validate_by_*`, and `generate_arguments_schema()` (v2.11),
  `extra=` validation-call overrides, `exclude_computed_fields`, `union_format`
  (v2.12), `FieldInfo.asdict()` (v2.12.3), `ascii_only` on `StringConstraints`,
  `computed_field(exclude_if=...)`, and validated-data private-attribute
  factories (v2.13), and `polymorphic_serialization` (v2.13). Confirm exact
  minimum versions in the changelog.
- v2.14.0+ adds a stable top-level `MISSING` sentinel (previously experimental
  in v2.12), `create_model(__namespace__=...)`, `TypeForm`, `frozendict` support,
  `defaultdict` factories for `dict`/`frozendict`/`frozenset`, native core schemas
  for `Fraction`, named tuples, `deque`, `OrderedDict`, and `Counter`, and
  `multiple_of` for `Fraction`/`timedelta`. v2.14.1–2.14.4 add TypedDict
  inheritance for `closed`/`extra_items`, named-tuple `Sequence` validation and
  serialization, stricter JSON extra-key handling, and rejection of non-string
  extra keys. `model_config` is no longer mutated after class creation.
- Distinguish partial JSON parsing (`pydantic_core.from_json(...,
  allow_partial=True)`, v2.7+) from experimental partial validation
  (`experimental_allow_partial` on adapter/validator APIs, v2.10+). Neither
  should be treated as proof that an incomplete payload is complete.
- Generic-model bracket syntax (`class Box[T]`) requires Python 3.12; use the
  `TypeVar`/`Generic` spelling on older Python. `TypedDict` also needs the
  `typing_extensions` backport on Python versions where the standard-library
  implementation is not supported by the runtime. Pydantic v2.14 dropped Python
  3.9 (minimum 3.10); pydantic-settings 2.16+ requires Python 3.11+.
- `pydantic-settings` has its own Python/package version floor and release cycle.
  Gate newer settings controls such as `env_prefix_target`, `dotenv_filtering`,
  CLI helpers, and cloud sources against the installed settings package rather
  than the Pydantic version alone.
- For `NestedSecretsSettingsSource` with `secrets_nested_subdir=True`, require
  pydantic-settings 2.14.2+ because versions `>=2.12.0,<2.14.2` have a symlink
  escape advisory (GHSA-4xgf-cpjx-pc3j). The plain `SecretsSettingsSource` had a
  separate symlink-escape issue fixed in 2.16.3; require 2.16.3+ wherever a
  secret file could be a symlink to a path outside `secrets_dir`. See
  `references/settings.md`.
- Low-level core schemas and experimental APIs have a smaller stability promise;
  use the high-level Pydantic API whenever possible.

## Relevant integrations

When an integration is part of the task, route to its concrete page rather than
generalizing from Pydantic alone:

- LLM output and structured responses: `integrations/llms/`.
- Static typing and tooling: `integrations/dev-tools/mypy/` (`pydantic.mypy`
  plugin), `pyrefly/` (built-in support), `linting/` (`flake8-pydantic`,
  `PYDXXX`), `hypothesis/` (the old plugin was removed in v2), `rich/`,
  `pycharm/`, and `visual_studio_code/`.
- Generated models: `integrations/dev-tools/datamodel_code_generator/`.
- Documentation: `integrations/dev-tools/documentation/` (Sphinx `intersphinx_mapping`
  and MkDocs `objects.inv`; note `latest` vs `dev`).
- AWS Lambda (native-wheel troubleshooting) and Logfire (instrumentation and
  scrubbing): `integrations/aws_lambda/` and `integrations/logfire/`.
