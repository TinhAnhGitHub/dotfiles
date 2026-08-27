# Application Settings

This example uses `pydantic-settings` to load a nested database configuration
from four sources:

1. Constructor arguments, if supplied.
2. Process environment variables, including `APP_DB__HOST`.
3. `.env`.
4. Files in the mounted secrets directory.

The first source that supplies a value wins. Defaults are used last. The
source order is explicit in `settings_customise_sources`, so the precedence
does not depend on an implicit library default.

## Dependencies

```toml
# pyproject.toml
[project]
dependencies = [
    "pydantic>=2.7",
    "pydantic-settings>=2.12",
]

[project.optional-dependencies]
test = ["pytest>=8"]
```

## Settings Model

```python
# app/settings.py
from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    NestedSecretsSettingsSource,
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
        # The mounted files use the same delimiter as nested environment keys.
        secrets_nested_delimiter="__",
        extra="ignore",
    )

    db: DatabaseSettings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            # Secret filenames are field paths, not APP_-prefixed env names.
            NestedSecretsSettingsSource(file_secret_settings, secrets_prefix=""),
        )


def safe_summary(settings: Settings) -> dict[str, str]:
    """Return diagnostics that are safe to include in logs."""
    return {"db_host": settings.db.host}


def load_settings() -> Settings:
    """Load settings using `.env` and `/run/secrets` defaults."""
    return Settings()
```

`env_nested_delimiter="__"` maps `APP_DB__HOST` to `Settings.db.host`:

```text
APP_DB__HOST=database.internal
```

The mounted directory has one file per nested key. With the configuration
above, the production layout is:

```text
/run/secrets/
├── db__host
└── db__password
```

The secret filenames do not include the `APP_` environment prefix. The
`NestedSecretsSettingsSource` maps the field path (`db` + `host`) using
`secrets_nested_delimiter`.

A non-secret `.env` can contain the host fallback:

```dotenv
# .env -- do not commit credentials here
APP_DB__HOST=database-from-dotenv.internal
```

Keep credentials in the mounted secret file instead of putting them in `.env`
or process arguments.

## Precedence Tests

```python
# tests/test_settings.py
from pathlib import Path

from app.settings import Settings, safe_summary


MOUNTED_PASSWORD = "fixture-only-password"


def make_sources(tmp_path: Path) -> tuple[Path, Path]:
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "APP_DB__HOST=from-dotenv\n",
        encoding="utf-8",
    )

    secrets_dir = tmp_path / "run-secrets"
    secrets_dir.mkdir()
    (secrets_dir / "db__host").write_text(
        "from-mounted-secret\n",
        encoding="utf-8",
    )
    (secrets_dir / "db__password").write_text(
        f"{MOUNTED_PASSWORD}\n",
        encoding="utf-8",
    )
    return dotenv, secrets_dir


def test_environment_overrides_dotenv_and_mounted_secret(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dotenv, secrets_dir = make_sources(tmp_path)
    monkeypatch.setenv("APP_DB__HOST", "from-environment")

    settings = Settings(_env_file=dotenv, _secrets_dir=secrets_dir)

    assert settings.db.host == "from-environment"


def test_dotenv_overrides_mounted_secret_when_environment_is_absent(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dotenv, secrets_dir = make_sources(tmp_path)
    monkeypatch.delenv("APP_DB__HOST", raising=False)

    settings = Settings(_env_file=dotenv, _secrets_dir=secrets_dir)

    assert settings.db.host == "from-dotenv"


def test_mounted_secret_is_fallback_when_higher_sources_are_absent(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dotenv, secrets_dir = make_sources(tmp_path)
    dotenv.write_text("# no host in this file\n", encoding="utf-8")
    monkeypatch.delenv("APP_DB__HOST", raising=False)

    settings = Settings(_env_file=dotenv, _secrets_dir=secrets_dir)

    assert settings.db.host == "from-mounted-secret"


def test_constructor_values_have_highest_precedence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dotenv, secrets_dir = make_sources(tmp_path)
    monkeypatch.setenv("APP_DB__HOST", "from-environment")

    settings = Settings(
        db={"host": "from-constructor", "password": "constructor-password"},
        _env_file=dotenv,
        _secrets_dir=secrets_dir,
    )

    assert settings.db.host == "from-constructor"


def test_secret_values_are_masked_and_not_in_safe_diagnostics(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dotenv, secrets_dir = make_sources(tmp_path)
    monkeypatch.delenv("APP_DB__HOST", raising=False)

    settings = Settings(_env_file=dotenv, _secrets_dir=secrets_dir)

    # This verifies masking without printing or interpolating the secret.
    assert str(settings.db.password) == "**********"
    assert MOUNTED_PASSWORD not in repr(settings)
    assert safe_summary(settings) == {"db_host": "from-dotenv"}
```

The tests assert values in memory but never print them. In particular, do not
log `settings.db.password.get_secret_value()`, `settings.model_dump()`, or the
entire settings object. If startup diagnostics are needed, log only the
allowlisted result of `safe_summary(settings)`.

Run the tests with:

```bash
pytest -q
```
