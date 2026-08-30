# pydantic-settings

## Boundary and installation

`BaseSettings` moved out of Pydantic v2:

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Database(BaseModel):
    host: str = 'localhost'
    port: int = 5432

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP_',
        env_nested_delimiter='__',
        env_nested_max_split=2,
        env_ignore_empty=True,
        env_file='.env',
        secrets_dir='/run/secrets',
    )
    database: Database = Field(default_factory=Database)
    api_key: str
```

Inspect the installed `pydantic-settings` version separately. Its current
package requires a compatible Pydantic v2 and has optional integrations for some
file/cloud sources.

## Source precedence

The usual priority is highest to lowest: CLI (when enabled), initialization
kwargs, environment variables, dotenv files, secret files, and field defaults.
`settings_customise_sources()` can reorder, add, or remove sources; its returned
tuple order is priority order. State the chosen order in application docs and
tests because changing it changes production behavior.

## Environment names and nested values

- `env_prefix` applies to default field names; `alias`, `validation_alias`, and
  `AliasChoices` select alternate names. `env_prefix_target` controls whether a
  prefix applies to variables, aliases, or both; gate it by the installed version.
- Environment matching is case-insensitive by default; `case_sensitive=True`
  matters for dotenv and non-Windows environments but does not defeat Windows's
  normalized environment behavior.
- `list`, `set`, `dict`, and nested models are normally JSON strings in one env var.
- `env_nested_delimiter='__'` explodes variables such as
  `APP_DATABASE__HOST=localhost`; nested keys beat a top-level JSON value.
- Use `env_nested_max_split` when a delimiter could split a field such as
  `api_key` into the wrong path.
- `nested_model_default_partial_update` controls whether nested defaults are
  preserved/partially updated when only a nested environment key is supplied;
  test this explicitly when nested models have meaningful defaults.
- `env_ignore_empty`, `env_parse_none_str`, and `env_parse_enums` alter parsing;
  document them because they change defaults and user input semantics.

An alias overrides the default field-name environment variable. With the default
`env_prefix_target='variable'`, this reads `API_KEY` rather than `APP_API_KEY`:

```python
class AliasedSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='APP_')
    api_key: str = Field(validation_alias='API_KEY')
```

Use `env_prefix_target='all'` when the intended name is `APP_API_KEY`; verify this
against the installed `pydantic-settings` version before relying on it.

For comma-separated values, do not expect `NUMBERS=1,2,3` to be JSON. Use
`NoDecode` with a before validator, disable decoding and parse intentionally, or
customize the source:

```python
from typing import Annotated
from pydantic import BeforeValidator
from pydantic_settings import NoDecode

def split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(',') if part.strip()]

CsvList = Annotated[list[str], NoDecode, BeforeValidator(split_csv)]

class Settings(BaseSettings):
    origins: CsvList
```

`ForceDecode` is the field-level escape hatch when global `enable_decoding=False`.

## Dotenv and secrets

`env_file` can be one or multiple files; later files override earlier ones, but
real environment variables override dotenv values. Relative dotenv paths are
resolved from the current working directory. `extra='forbid'` can make unrelated
dotenv keys fail startup. For shared files, use `dotenv_filtering='match_prefix'`
or `'only_existing'` where supported, or `extra='ignore'` when that is intentional.

Secret directories use `filename -> value` and are lower priority than env/dotenv.
Use mounted secret files or a secret manager, never commit `.env` or plaintext
credentials. `_env_file=None` and `_secrets_dir=...` are useful per-instance
overrides. `PYDANTIC_SETTINGS_DEBUG=1` logs source values, including secrets;
never enable it in production or capture its output in CI artifacts.

### Security advisory: nested secret directories

`pydantic-settings` versions `>=2.12.0,<2.14.2` are affected when
`NestedSecretsSettingsSource` is used with `secrets_nested_subdir=True`: an
attacker-influenced symlink inside `secrets_dir` could be followed outside the
configured directory and bypass the size cap. Prefer `pydantic-settings>=2.14.2`
and keep the secrets mount non-writable. If an upgrade is impossible, avoid
`secrets_nested_subdir=True` or ensure every entry is fully application-controlled.
See the official advisory: <https://github.com/pydantic/pydantic-settings/security/advisories/GHSA-4xgf-cpjx-pc3j>.

## CLI and file/cloud sources

`SettingsConfigDict(cli_parse_args=True)` enables built-in CLI parsing. It supports
JSON or repeated list/dict values, aliases, enums/literals, kebab case, positional
arguments, subcommands, and `CliApp`. CLI arguments are visible in process lists;
do not pass credentials through them. Newer CLI helpers and file/cloud source
classes are release-sensitive; check the settings API before using them.

JSON, YAML, TOML, and `pyproject.toml` sources are registered through source
classes and `settings_customise_sources`; optional dependencies and shallow versus
deep merge behavior vary by source. Cloud sources (AWS Secrets Manager, Azure Key
Vault, Google Secret Manager) need explicit credentials and should be tested with
redacted fixtures.

## Custom sources and verification

Subclass `EnvSettingsSource` for a small parsing override (`prepare_field_value`),
or implement `PydanticBaseSettingsSource` for a real external source. Check source
priority, field aliases, complex-value decoding, nested env overrides, defaults,
dotenv unknown keys, missing secret directories, and redaction. Settings
construction is synchronous; move blocking file/network source work off an async
event loop when appropriate.
