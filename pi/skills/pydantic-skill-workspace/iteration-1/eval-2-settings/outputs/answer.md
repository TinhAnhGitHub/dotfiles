# Application settings from environment, dotenv, and mounted secrets

Use `BaseSettings` from `pydantic-settings`, not from `pydantic`. The settings
model below has a nested `db` object, so `APP_DB__HOST` is interpreted as
`settings.db.host`.

This example targets the current Pydantic v2 and `pydantic-settings` v2 APIs.
The evaluation Python environment did not have either package importable, so
the code was not executed here. Pin and verify the versions in the application
environment before using it.

```text
pydantic>=2,<3
pydantic-settings>=2,<3
pytest>=8,<9
```

## Settings model

`app/settings.py`:

```python
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        secrets_dir="/run/secrets",
        # A shared dotenv file may contain keys for other local tools.
        extra="ignore",
    )

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api_key: SecretStr
```

With this configuration:

```text
APP_DB__HOST=prod-db.example.internal
```

loads into `settings.db.host`. The nested delimiter is `__`, and the `APP_`
prefix is applied to the top-level environment name.

The mounted secret directory should contain a file whose name is the settings
source key. With the `APP_` prefix in this current `pydantic-settings`
configuration, mount the API key as:

```text
/run/secrets/APP_API_KEY
```

The file should contain only the credential, optionally followed by a newline.
The secrets source strips surrounding whitespace. Do not put the credential in
the repository or in a committed `.env` file.

An application `.env` can contain non-secret configuration:

```dotenv
APP_DB__HOST=localhost-from-dotenv
APP_DB__PORT=5432
```

Startup then remains simple and does not print the settings:

```python
from app.settings import Settings


settings = Settings()

# Use settings.db.host and settings.db.port to configure the database client.
# Keep settings.api_key as SecretStr. If a client requires a plain string,
# call settings.api_key.get_secret_value() only at that client boundary.
```

`SecretStr` masks the value in its normal string representation and in
Pydantic serialization. That is defense in depth, not permission to log the
model. Never log `settings`, `settings.model_dump()`, environment values, or
the contents of `/run/secrets`. In particular, do not enable
`PYDANTIC_SETTINGS_DEBUG=1`, because settings debug logging includes source
values.

## Precedence

No CLI source is enabled in this model. The built-in priority, from highest to
lowest, is:

1. Values passed to `Settings(...)`.
2. Real process environment variables such as `APP_DB__HOST`.
3. Values in `.env` (or the file supplied through `_env_file`).
4. Files in `secrets_dir` (or the directory supplied through `_secrets_dir`).
5. Field defaults such as `localhost` and `5432`.

The sources are merged by field. A secret file does not replace an environment
or dotenv value for the same field; it fills the field only when higher-priority
sources did not provide it. If CLI parsing is later enabled, CLI values become
the highest-priority source.

For tests, `_env_file` and `_secrets_dir` are useful per-instance overrides.
They avoid changing the process working directory or the production mount.

## Precedence tests

`tests/test_settings.py`:

```python
from pathlib import Path

from app.settings import Settings


def _prepare_sources(tmp_path: Path, dotenv: str) -> tuple[Path, Path]:
    env_file = tmp_path / ".env"
    env_file.write_text(dotenv, encoding="utf-8")

    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    # This is a synthetic test fixture. The test never prints it.
    (secrets_dir / "APP_API_KEY").write_text("mounted-key\n", encoding="utf-8")
    return env_file, secrets_dir


def _clear_setting_environment(monkeypatch) -> None:
    # Avoid values inherited from a developer shell or CI runner.
    monkeypatch.delenv("APP_DB__HOST", raising=False)
    monkeypatch.delenv("APP_API_KEY", raising=False)


def _assert_api_key(settings: Settings, expected: str) -> None:
    # Do not include either value in the exception. A failed test therefore
    # cannot disclose the credential through its assertion message.
    if settings.api_key.get_secret_value() != expected:
        raise AssertionError("api_key did not come from the expected source")


def test_dotenv_is_used_and_secret_file_fills_missing_key(tmp_path, monkeypatch):
    _clear_setting_environment(monkeypatch)
    env_file, secrets_dir = _prepare_sources(
        tmp_path,
        "APP_DB__HOST=dotenv-host\n",
    )

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert settings.db.host == "dotenv-host"
    _assert_api_key(settings, "mounted-key")


def test_environment_overrides_dotenv_for_nested_host(tmp_path, monkeypatch):
    _clear_setting_environment(monkeypatch)
    env_file, secrets_dir = _prepare_sources(
        tmp_path,
        "APP_DB__HOST=dotenv-host\n",
    )
    monkeypatch.setenv("APP_DB__HOST", "environment-host")

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert settings.db.host == "environment-host"


def test_dotenv_overrides_secret_file_for_api_key(tmp_path, monkeypatch):
    _clear_setting_environment(monkeypatch)
    env_file, secrets_dir = _prepare_sources(
        tmp_path,
        "APP_DB__HOST=dotenv-host\nAPP_API_KEY=dotenv-key\n",
    )

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    _assert_api_key(settings, "dotenv-key")


def test_environment_overrides_dotenv_and_secret_file(tmp_path, monkeypatch):
    _clear_setting_environment(monkeypatch)
    env_file, secrets_dir = _prepare_sources(
        tmp_path,
        "APP_DB__HOST=dotenv-host\nAPP_API_KEY=dotenv-key\n",
    )
    monkeypatch.setenv("APP_DB__HOST", "environment-host")
    monkeypatch.setenv("APP_API_KEY", "environment-key")

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert settings.db.host == "environment-host"
    _assert_api_key(settings, "environment-key")


def test_initialization_kwargs_override_environment(tmp_path, monkeypatch):
    _clear_setting_environment(monkeypatch)
    env_file, secrets_dir = _prepare_sources(
        tmp_path,
        "APP_DB__HOST=dotenv-host\nAPP_API_KEY=dotenv-key\n",
    )
    monkeypatch.setenv("APP_DB__HOST", "environment-host")
    monkeypatch.setenv("APP_API_KEY", "environment-key")

    settings = Settings(
        db={"host": "init-host"},
        api_key="init-key",
        _env_file=env_file,
        _secrets_dir=secrets_dir,
    )

    assert settings.db.host == "init-host"
    _assert_api_key(settings, "init-key")
```

These tests inspect the secret only for an in-memory comparison. They do not
print it, include it in an assertion message, dump the settings model, or log
the source dictionaries. Run them with:

```bash
pytest -q tests/test_settings.py
```

If the mounted directory is absent, `pydantic-settings` warns and the required
`api_key` field then fails validation. Treat that as a deployment/configuration
error rather than making the credential optional.

If the application is pinned to an older `pydantic-settings` release, verify
the exact secret filename behavior against that release. The filename must
match the key that its `SecretsSettingsSource` resolves; keep that filename in
the test fixture so a dependency upgrade cannot silently change the contract.

References:

- Pydantic settings concepts: https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/
- Pydantic settings API: https://pydantic.dev/docs/validation/latest/api/pydantic_settings/
