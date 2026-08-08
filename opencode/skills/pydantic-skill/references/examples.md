# Official examples and integrations

Start at the exact published example pages below. The examples are small,
runnable patterns; follow their linked concept/API page when adapting them to a
version-pinned project. The bare `/examples/` landing URL is not guaranteed to be
published, so use a concrete child page or the `llms.txt` index.

| Example | Pattern |
|---|---|
| [custom_validators](https://pydantic.dev/docs/validation/latest/examples/custom_validators/index.md) | Annotated metadata, timezone validation, core-schema wrap hooks, nested invariants |
| [dynamic_models](https://pydantic.dev/docs/validation/latest/examples/dynamic_models/index.md) | `create_model`, optionalizing fields, `FieldInfo.asdict`, inherited validators |
| [files](https://pydantic.dev/docs/validation/latest/examples/files/index.md) | JSON, JSONL, CSV, TOML, YAML, XML, and INI boundary validation |
| [orms](https://pydantic.dev/docs/validation/latest/examples/orms/index.md) | `from_attributes=True`, aliases for reserved ORM attributes, SQLAlchemy boundary |
| [queues](https://pydantic.dev/docs/validation/latest/examples/queues/index.md) | `model_dump_json`/`model_validate_json` with Redis/RabbitMQ/ARQ |
| [requests](https://pydantic.dev/docs/validation/latest/examples/requests/index.md) | HTTP response validation and `TypeAdapter(list[User])` |
| [pydantic_ai](https://pydantic.dev/docs/validation/latest/examples/pydantic_ai/index.md) | Integration with a Pydantic-based agent library |

## Patterns worth reusing

- Validate at I/O boundaries, then pass typed values inward.
- Use a `TypeAdapter` for response collections and `TypedDict` payloads instead
  of manufacturing a wrapper model solely for validation.
- Use `from_attributes=True` for ORM objects, but test lazy attributes and avoid
  accidental database I/O during serialization.
- Use a discriminated union for event/message envelopes.
- Use `model_validate_json` for queue payloads and test malformed/truncated data.
- Use `Annotated` custom types for behavior that should be shared across models.

## Anti-patterns called out by the docs

- Overriding `__init__` instead of using validators or `model_post_init`.
- Using `model_construct` or `model_copy(update=...)` with untrusted input.
- Relying on `assert` inside validators (optimized Python removes assertions).
- Copying/mutating `FieldInfo` objects as a reusable field definition.
- Applying a container constraint when the intended constraint belongs to items.
- Using an untagged union where a discriminator is available.
- Logging full settings, payment cards, phone numbers, or secret values.
- Enabling duck-typed subclass serialization without checking data exposure.

## External integrations

Pydantic is commonly used at FastAPI request/response, SQLAlchemy/ORM, queue,
HTTP client, and agent boundaries. Do not let the integration hide the Pydantic
version: inspect the actual model and package imports. If a framework has its own
schema lifecycle, preserve its contract and add focused Pydantic tests rather than
assuming the framework validates exactly like direct model construction.

For tooling and integrations, use the exact pages in the official index:
`integrations/llms/`, `integrations/dev-tools/mypy/`, `pyrefly/`, `linting/`,
`hypothesis/`, `datamodel_code_generator/`, `rich/`, `pycharm/`,
`visual_studio_code/`, `integrations/aws_lambda/`, and `integrations/logfire/`.
