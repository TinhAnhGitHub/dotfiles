# Application Settings

Use `BaseSettings` from `pydantic-settings`, not from `pydantic`. The default source order is:

```text
init kwargs > process environment > dotenv file > mounted secret files > field defaults
```

The code below makes the nested environment name `APP_DB__HOST` explicit. The API key uses `SecretStr`, and its aliases make both `APP_API_KEY` and the conventional mounted filename `api_key` valid without exposing the value.

## `settings.py`

```python
from pydantic import AliasChoices, BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        secrets_dir="/run/secrets",
        case_sensitive=False,
        extra="ignore",
    )

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api_key: SecretStr = Field(
        validation_alias=AliasChoices("APP_API_KEY", "api_key")
    )
```

`APP_DB__HOST` is split at `__` into `db.host`. A mounted secret directory uses one file per field; mount the credential at `/run/secrets/api_key`. The first alias also permits `/run/secrets/APP_API_KEY` if the orchestrator uses the environment spelling for secret keys.

Environment and dotenv values use Pydantic's default lax conversion, so a string such as `APP_DB__PORT=5432` becomes an integer. Strict mode is not enabled. Matching is case-insensitive, unrelated dotenv keys are ignored by `extra="ignore"`, `db` supplies typed defaults, and `api_key` is required unless one of its sources provides it. `SecretStr` redacts the credential in representations; do not serialize or log the settings object as an application diagnostic.

An ordinary `.env` can contain non-secret settings such as:

```dotenv
APP_DB__HOST=database.internal
APP_DB__PORT=5432
```

Do not commit `.env`. If an API key is put in `.env`, `APP_API_KEY` from the real process environment overrides it, and either value overrides `/run/secrets/api_key`.

The normal application entry point is simply:

```python
settings = AppSettings()
```

It reads `.env` relative to the process working directory and `/run/secrets` as configured above. For tests or another deployment layout, pass `_env_file` and `_secrets_dir` per instance as shown below.

## Precedence tests

These tests use synthetic fixture values only. They assert secret values but never print them, dump the settings model, or log source contents.

```python
from pathlib import Path
from typing import Optional, Tuple

import pytest

from settings import AppSettings


def write_sources(
    tmp_path: Path,
    *,
    dotenv_api_key: Optional[str] = None,
    secret_api_key: str = "mounted-secret",
) -> Tuple[Path, Path]:
    dotenv_file = tmp_path / ".env"
    secret_dir = tmp_path / "secrets"
    secret_dir.mkdir()

    dotenv_lines = []
    if dotenv_api_key is not None:
        dotenv_lines.append(f"APP_API_KEY={dotenv_api_key}")
    dotenv_file.write_text("\n".join(dotenv_lines) + "\n", encoding="utf-8")
    (secret_dir / "api_key").write_text(
        secret_api_key + "\n", encoding="utf-8"
    )
    return dotenv_file, secret_dir


@pytest.mark.parametrize(
    ("init_value", "env_value", "dotenv_value", "expected"),
    [
        ("init-secret", "environment-secret", "dotenv-secret", "init-secret"),
        (None, "environment-secret", "dotenv-secret", "environment-secret"),
        (None, None, "dotenv-secret", "dotenv-secret"),
        (None, None, None, "mounted-secret"),
    ],
)
def test_api_key_source_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_value: Optional[str],
    env_value: Optional[str],
    dotenv_value: Optional[str],
    expected: str,
) -> None:
    monkeypatch.delenv("APP_API_KEY", raising=False)
    monkeypatch.delenv("APP_DB__HOST", raising=False)
    if env_value is not None:
        monkeypatch.setenv("APP_API_KEY", env_value)

    dotenv_file, secret_dir = write_sources(
        tmp_path, dotenv_api_key=dotenv_value
    )
    init_kwargs = {} if init_value is None else {"api_key": init_value}
    settings = AppSettings(
        _env_file=dotenv_file,
        _secrets_dir=secret_dir,
        **init_kwargs,
    )

    assert settings.api_key.get_secret_value() == expected


def test_nested_environment_overrides_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APP_API_KEY", raising=False)
    monkeypatch.setenv("APP_DB__HOST", "environment-host")
    dotenv_file = tmp_path / ".env"
    dotenv_file.write_text("APP_DB__HOST=dotenv-host\n", encoding="utf-8")
    secret_dir = tmp_path / "secrets"
    secret_dir.mkdir()
    (secret_dir / "api_key").write_text("mounted-secret\n", encoding="utf-8")

    settings = AppSettings(_env_file=dotenv_file, _secrets_dir=secret_dir)

    assert settings.db.host == "environment-host"


def test_init_kwargs_override_nested_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APP_API_KEY", raising=False)
    monkeypatch.setenv("APP_DB__HOST", "environment-host")
    dotenv_file, secret_dir = write_sources(tmp_path)

    settings = AppSettings(
        db={"host": "init-host"},
        _env_file=dotenv_file,
        _secrets_dir=secret_dir,
    )

    assert settings.db.host == "init-host"


def test_default_is_used_when_no_source_provides_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APP_API_KEY", raising=False)
    monkeypatch.delenv("APP_DB__PORT", raising=False)
    dotenv_file, secret_dir = write_sources(tmp_path)

    settings = AppSettings(_env_file=dotenv_file, _secrets_dir=secret_dir)

    assert settings.db.port == 5432
```

Run the focused suite with `pytest -q`. For a safe health/debug signal, expose only non-sensitive metadata, such as whether the key is configured; never serialize or log the settings object, and never enable `PYDANTIC_SETTINGS_DEBUG=1`, because those paths can disclose settings source values.

The installed global `python3` in this workspace had no Pydantic packages or project lockfile. A separate `uv` verification environment resolved Pydantic `2.13.4`, `pydantic-core` `2.46.4`, and `pydantic-settings` `2.15.0`; the implementation uses stable v2 settings APIs.

Reference: [pydantic-settings settings documentation](https://github.com/pydantic/pydantic-settings/blob/main/docs/index.md) for nested environment parsing and source precedence.
