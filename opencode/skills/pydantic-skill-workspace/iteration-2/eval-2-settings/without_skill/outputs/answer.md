# Application Settings

Use `pydantic-settings` to combine nested environment variables, a dotenv file,
and a mounted secrets directory. The source order below is explicit:

1. Values passed to `Settings(...)`.
2. Real process environment variables, including `APP_DB__HOST`.
3. Values from `.env`.
4. Files in `/run/secrets`.
5. Model defaults, if any.

Sources are merged by field, so a higher-priority source can provide
`db.host` while a lower-priority source still supplies `db.password`.

## Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "pydantic>=2,<3",
    "pydantic-settings>=2.14.2,<3",
]

[project.optional-dependencies]
test = ["pytest>=8,<9"]
```

## Settings Model

```python
# app/settings.py
from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    NestedSecretsSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class DatabaseSettings(BaseModel):
    host: str
    password: SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        secrets_dir="/run/secrets",
        # Secret filenames are field paths, not APP_-prefixed names.
        secrets_prefix="",
        secrets_nested_delimiter="__",
        extra="ignore",
    )

    db: DatabaseSettings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            # Wrapping the supplied source preserves the _secrets_dir override.
            NestedSecretsSettingsSource(file_secret_settings),
        )


def safe_summary(settings: Settings) -> dict[str, str]:
    """Return only explicitly allowlisted, non-secret diagnostics."""
    return {"db_host": settings.db.host}


def load_settings() -> Settings:
    return Settings()
```

`env_nested_delimiter="__"` maps this variable to `settings.db.host`:

```text
APP_DB__HOST=database.internal
```

The mounted directory uses a flat file for each nested field. With
`secrets_prefix=""` and `secrets_nested_delimiter="__"`, its layout is:

```text
/run/secrets/
├── db__host
└── db__password
```

Each file contains only its value, optionally followed by a newline. Keep the
password out of `.env`, source control, command-line arguments, and logs.

A non-secret `.env` can provide a fallback host:

```dotenv
# .env
APP_DB__HOST=database-from-dotenv.internal
```

## Precedence Tests

```python
# tests/test_settings.py
from pathlib import Path

from app.settings import Settings, safe_summary


MOUNTED_PASSWORD = "fixture-mounted-password"


def make_sources(
    tmp_path: Path,
    *,
    dotenv: str = "APP_DB__HOST=from-dotenv\n",
    mounted_host: str = "from-mounted-secret",
) -> tuple[Path, Path]:
    env_file = tmp_path / ".env"
    env_file.write_text(dotenv, encoding="utf-8")

    secrets_dir = tmp_path / "run-secrets"
    secrets_dir.mkdir()
    (secrets_dir / "db__host").write_text(
        f"{mounted_host}\n",
        encoding="utf-8",
    )
    (secrets_dir / "db__password").write_text(
        f"{MOUNTED_PASSWORD}\n",
        encoding="utf-8",
    )
    return env_file, secrets_dir


def clear_process_settings(monkeypatch) -> None:
    # Do not let a developer shell or CI runner change the test source order.
    monkeypatch.delenv("APP_DB__HOST", raising=False)
    monkeypatch.delenv("APP_DB__PASSWORD", raising=False)


def assert_password_is(settings: Settings, expected: str) -> None:
    # A failed test has a constant error and cannot disclose either value.
    if settings.db.password.get_secret_value() != expected:
        raise AssertionError("database password came from an unexpected source")


def test_environment_overrides_dotenv_and_mounted_secret(tmp_path, monkeypatch):
    clear_process_settings(monkeypatch)
    env_file, secrets_dir = make_sources(tmp_path)
    monkeypatch.setenv("APP_DB__HOST", "from-environment")

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert settings.db.host == "from-environment"
    assert_password_is(settings, MOUNTED_PASSWORD)


def test_dotenv_overrides_mounted_secret_when_environment_is_absent(
    tmp_path, monkeypatch
):
    clear_process_settings(monkeypatch)
    env_file, secrets_dir = make_sources(tmp_path)

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert settings.db.host == "from-dotenv"
    assert_password_is(settings, MOUNTED_PASSWORD)


def test_mounted_secret_is_fallback_when_higher_sources_are_absent(
    tmp_path, monkeypatch
):
    clear_process_settings(monkeypatch)
    env_file, secrets_dir = make_sources(
        tmp_path,
        dotenv="# no database host here\n",
    )

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert settings.db.host == "from-mounted-secret"
    assert_password_is(settings, MOUNTED_PASSWORD)


def test_constructor_values_override_every_external_source(tmp_path, monkeypatch):
    clear_process_settings(monkeypatch)
    env_file, secrets_dir = make_sources(
        tmp_path,
        dotenv="APP_DB__HOST=from-dotenv\nAPP_DB__PASSWORD=dotenv-password\n",
    )
    monkeypatch.setenv("APP_DB__HOST", "from-environment")
    monkeypatch.setenv("APP_DB__PASSWORD", "environment-password")

    settings = Settings(
        db={"host": "from-constructor", "password": "constructor-password"},
        _env_file=env_file,
        _secrets_dir=secrets_dir,
    )

    assert settings.db.host == "from-constructor"
    assert_password_is(settings, "constructor-password")


def test_dotenv_password_overrides_mounted_password_without_logging_it(
    tmp_path, monkeypatch
):
    clear_process_settings(monkeypatch)
    env_file, secrets_dir = make_sources(
        tmp_path,
        dotenv=(
            "APP_DB__HOST=from-dotenv\n"
            "APP_DB__PASSWORD=dotenv-password\n"
        ),
    )

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert_password_is(settings, "dotenv-password")
    assert str(settings.db.password) == "**********"
    assert safe_summary(settings) == {"db_host": "from-dotenv"}


def test_environment_password_overrides_dotenv_and_mounted_password(
    tmp_path, monkeypatch
):
    clear_process_settings(monkeypatch)
    env_file, secrets_dir = make_sources(
        tmp_path,
        dotenv=(
            "APP_DB__HOST=from-dotenv\n"
            "APP_DB__PASSWORD=dotenv-password\n"
        ),
    )
    monkeypatch.setenv("APP_DB__PASSWORD", "environment-password")

    settings = Settings(_env_file=env_file, _secrets_dir=secrets_dir)

    assert_password_is(settings, "environment-password")
    assert str(settings.db.password) == "**********"

```

The tests inspect secret values only for an in-memory source-selection check.
They do not print them, include them in failure messages, dump the settings
object, or log source dictionaries. Application diagnostics should use only an
allowlisted projection such as `safe_summary(settings)`; never log
`settings.db.password.get_secret_value()`, `settings.model_dump()`, or the
contents of `/run/secrets`.

Run the tests with:

```bash
pytest -q tests/test_settings.py
```
