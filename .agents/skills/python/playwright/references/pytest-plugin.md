# pytest-playwright plugin: fixtures, config, async

## Installation

```bash
pip install pytest-playwright
playwright install          # CI: playwright install --with-deps
```

## Fixtures

| Fixture | Scope | Purpose |
|---|---|---|
| `page` | function | A fresh page in a fresh context per test |
| `context` | function | The browser context backing `page` |
| `new_context` | function | Factory for additional isolated contexts |
| `browser` | session | Shared Browser instance |
| `browser_type` | session | The selected browser engine |
| `browser_name` | session | Name of the browser (`chromium`/`firefox`/`webkit`) |
| `playwright` | session | Playwright driver instance |

CLI options apply only to plugin-created default fixtures. A context or page you
create manually with `browser.new_context()` does not inherit `--viewport`,
`--video`, `--tracing`, etc. — pass those options explicitly or close the context
so artifacts flush.

pytest's built-in `request` fixture is **not** a Playwright API fixture. For HTTP
calls use `page.request`, `context.request`, or define:

```python
import pytest
from playwright.sync_api import APIRequestContext, Playwright


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    return playwright.request.new_context(base_url="https://api.example.test")
```

## CLI options

```bash
pytest --browser chromium                 # chromium (default), firefox, webkit
pytest --browser chromium --browser firefox   # matrix
pytest --headed                           # show the browser UI
pytest --slowmo 100                       # slow actions by 100 ms (debugging)
pytest --viewport-size "1280,720"
pytest --base-url https://example.test
pytest --screenshot only-on-failure
pytest --video retain-on-failure
pytest --tracing retain-on-failure
```

## Configuration in pytest.ini / pyproject.toml

```ini
[pytest]
addopts = --browser chromium --tracing=retain-on-failure --screenshot=only-on-failure
```

```toml
[tool.pytest.ini_options]
addopts = ["--browser", "chromium", "--tracing=retain-on-failure"]
```

Override context options with the `browser_context_args` fixture:

```python
from typing import Any, Dict

import pytest


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "ignore_https_errors": True,
        "locale": "en-US",
    }
```

## Markers

```python
import pytest

@pytest.mark.skip_browser("webkit")
def test_chromium_only(page) -> None: ...

@pytest.mark.only_browser("chromium")
def test_single_browser(page) -> None: ...
```

## Async

Use `playwright.async_api` with the `pytest-playwright-asyncio` plugin. Do not mix
sync and async APIs in one test. Async fixtures must be declared with the plugin's
async fixture support; see the plugin docs for the current decorator.

## Parallelism

`pytest-xdist` can run browser tests in parallel, but stateful apps and shared
auth state can break. Start conservatively (few workers) and isolate all state
per test. Defer generic xdist guidance to `pytest-skill`.
