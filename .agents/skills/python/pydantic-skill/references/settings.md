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
file/cloud sources. pydantic-settings 2.16+ requires Python 3.11+.

### Version gates (pydantic-settings, verify against installed version)

| Feature | Minimum |
|---|---|
| `env_ignore_empty`, `env_parse_none_str` | 2.2.0 |
| `env_parse_enums` | 2.3.0 |
| `nested_model_default_partial_update` | 2.5.0 |
| `env_nested_max_split` | 2.8.0 |
| source-order behavior, `NestedSecretsSettingsSource` | 2.12.0 |
| nested-secrets symlink fix (GHSA-4xgf-cpjx-pc3j) | 2.14.2 |
| `env_prefix_target`, config-source deep merge, nested YAML sections, `Traversable` | 2.13.0 |
| `dotenv_filtering` | 2.14.0 |
| `cli_show_env_vars`, `PYDANTIC_SETTINGS_DEBUG`, regular-TOML `toml_table_header` | 2.15.0 |
| `env_file_depth`, `CliVariadicArg`, `settings_cached()`, AWS SSM source, Python 3.11 floor | 2.16.0 |
| plain `SecretsSettingsSource` symlink-escape fix | 2.16.3 |

## Source precedence

The usual priority is highest to lowest: CLI (when enabled), initialization
kwargs, environment variables, dotenv files, secret files, and field defaults.
Sources are merged with a **deep update**, so a lower-priority source can still
supply a missing nested key. `settings_customise_sources()` can reorder, add, or
remove sources; its returned tuple order is priority order, and enabling CLI only
makes it topmost by default. State the chosen order in application docs and tests
because changing it changes production behavior. Runtime validation arguments
(`strict`, `extra`, `context`) passed to `model_validate()` are not applied to
`BaseSettings`.

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
resolved from the current working directory; `env_file_depth` (v2.16+) searches
parent directories, which is useful when a script runs from a monorepo
subdirectory. `extra='forbid'` can make unrelated dotenv keys fail startup. For
shared files, use `dotenv_filtering='match_prefix'` or `'only_existing'` where
supported, or `extra='ignore'` when that is intentional. With `env_prefix`, an
unprefixed dotenv key that matches a field may be silently skipped while an
unrelated extra key still fails under `extra='forbid'`.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_depth=2,          # v2.16+: find .env in a parent directory
        dotenv_filtering='match_prefix',  # v2.14+: ignore unrelated keys
        env_prefix='APP_',
        extra='forbid',
    )
    api_key: str
```

Secret directories use `filename -> value` and are lower priority than env/dotenv.
Use mounted secret files or a secret manager, never commit `.env` or plaintext
credentials. `_env_file=None` and `_secrets_dir=...` are useful per-instance
overrides. Any truthy `PYDANTIC_SETTINGS_DEBUG` value enables debug output (with
DEBUG logging on the `pydantic_settings` logger); it includes source values,
merging, and file-resolution details, so never enable it in production or capture
its output in CI artifacts.

`settings_cached()` / `settings_clear_cache()` (v2.16+) provide a process-local
singleton per settings class without a hand-rolled `lru_cache`; calling the class
directly still builds a fresh instance.

```python
settings = Settings.settings_cached()   # same object on repeated calls
fresh = Settings()                       # always a new instance
Settings.settings_clear_cache()
```

### Security advisory: secret directories and symlinks

Two related symlink-escape issues affect secret sources:

- `>=2.12.0,<2.14.2`: `NestedSecretsSettingsSource` with
  `secrets_nested_subdir=True` could follow an attacker-influenced symlink
  outside `secrets_dir` and bypass the size cap (GHSA-4xgf-cpjx-pc3j). Fixed in
  2.14.2.
- `<2.16.3`: the plain `SecretsSettingsSource` could read a secret file that is a
  symlink to a path outside `secrets_dir`. Fixed in 2.16.3; links that stay
  inside the directory (for example the Kubernetes `..data/passwd` layout) still
  work.

Prefer `pydantic-settings>=2.16.3` and keep the secrets mount non-writable. If an
upgrade is impossible, avoid `secrets_nested_subdir=True` and ensure every entry
is fully application-controlled. Advisory:
<https://github.com/pydantic/pydantic-settings/security/advisories/GHSA-4xgf-cpjx-pc3j>.

`SecretsSettingsSource` reads top-level fields only. `NestedSecretsSettingsSource`
is opt-in through `settings_customise_sources()`; it supports nested models,
nested directories, `secrets_dir_missing`, size limits, and independent
case/prefix/delimiter settings. An explicit `secrets_dir` on the wrapper takes
precedence over the wrapped source and model config (v2.16.2+).

```python
from pydantic_settings import (
    BaseSettings, NestedSecretsSettingsSource, SecretsSettingsSource,
    SettingsConfigDict, PydanticBaseSettingsSource,
)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/run/secrets')

    @classmethod
    def settings_customise_sources(
        cls, settings_cls, init_settings, env_settings, dotenv_settings,
        file_secret_settings,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            NestedSecretsSettingsSource(
                SecretsSettingsSource(settings_cls, secrets_dir='/run/secrets'),
                secrets_nested_subdir=True,
            ),
        )
```

## CLI and file/cloud sources

`SettingsConfigDict(cli_parse_args=True)` enables built-in CLI parsing. It supports
JSON or repeated list/dict values, aliases, enums/literals, kebab case, positional
arguments, subcommands, and `CliApp`. CLI arguments are visible in process lists;
do not pass credentials through them. Newer helpers are release-sensitive:
`cli_show_env_vars` (v2.15+), `CliVariadicArg` for named variadic options,
`CliUnknownArgs`, `CliMutuallyExclusiveGroup`, async `CliApp` commands,
`CliApp.serialize()`/`format_help()`, and the `CliImplicitFlag`/`CliExplicitFlag`/
`CliToggleFlag`/`CliDualFlag` family (v2.16+). A repeated collection option
**replaces** earlier values by default; use `CliVariadicArg` when you need
`--param a b c`. Newer file/cloud source classes are release-sensitive; check the
settings API before using them.

```python
from pydantic_settings import BaseSettings, CliApp, CliVariadicArg, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, cli_show_env_vars=True)
    hosts: CliVariadicArg[list[str]]   # --hosts a b c, or repeated --hosts
    verbose: bool = False

# CliApp.run(Settings) parses sys.argv; CliApp.serialize(settings) round-trips.
```

JSON, YAML, TOML, and `pyproject.toml` sources are registered through source
classes and `settings_customise_sources`; optional dependencies and shallow versus
deep merge behavior vary by source. Useful keys include `yaml_config_section`
(dot-path sections), `pyproject_toml_depth`, `pyproject_toml_table_header`, and
regular-TOML `toml_table_header` (v2.15+). `deep_merge=True` is a **constructor**
argument, not a `SettingsConfigDict` key. Sources accept `Traversable` resources
(v2.13+). Cloud sources are optional and opt-in: AWS Secrets Manager, Azure Key
Vault, and Google Secret Manager can use ambient credentials (Google falls back
to `google.auth.default()`, Azure to `DefaultAzureCredential`); AWS Systems
Manager Parameter Store is available via `AWSSystemsManagerSettingsSource` with
the `aws-systems-manager` extra (v2.16+). Test all cloud sources with redacted
fixtures.

```python
from pydantic_settings import (
    BaseSettings, PyprojectTomlConfigSettingsSource, SettingsConfigDict,
    TomlConfigSettingsSource,
)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(pyproject_toml_table_header=('tool', 'myapp'))

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings,
                                   dotenv_settings, file_secret_settings):
        return (
            init_settings,
            env_settings,
            PyprojectTomlConfigSettingsSource(settings_cls),
            TomlConfigSettingsSource(settings_cls, toml_file='settings.toml',
                                     deep_merge=True),  # constructor-only
            file_secret_settings,
        )
```

## Custom sources and verification

Subclass `EnvSettingsSource` for a small parsing override (`prepare_field_value`),
or implement `PydanticBaseSettingsSource` for a real external source. Check source
priority, field aliases, complex-value decoding, nested env overrides, defaults,
dotenv unknown keys, missing secret directories, and redaction. Settings
construction is synchronous; move blocking file/network source work off an async
event loop when appropriate.
