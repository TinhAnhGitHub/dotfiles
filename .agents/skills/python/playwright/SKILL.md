---
name: playwright
description: >
  Playwright Python browser and API testing with pytest-playwright: locators, web-first
  assertions, auto-waiting, fixtures, browser configuration, authentication/storage state,
  network mocking, APIRequestContext, trace viewer, screenshots/videos, and CI. Use whenever
  a user asks for browser E2E tests, UI automation, Playwright locators or expect assertions,
  pytest-playwright fixtures/config, flaky UI tests, or debugging a failed browser test.
  Load the parent `pytest-skill` for generic pytest runner and fixture fundamentals.
compatibility: Python >=3.8; Playwright Python 1.65.x; pytest-playwright; optional pytest-playwright-asyncio
metadata:
  version: "1.0.0"
  docs-reviewed: "2026-11-21"
---

# Playwright Python E2E Testing

Playwright drives Chromium, Firefox, and WebKit from one API. For Python, the
recommended path is the `pytest-playwright` plugin, which gives each test a fresh
browser context (isolation) and supports a browser matrix out of the box.

Use Playwright for browser-level E2E and UI flows. Keep fast logic in pytest unit
tests (`pytest-skill`) and property tests (`hypothesis`); browser tests are slower
and should be a thin layer over well-tested logic.

## Mandatory preflight

1. Confirm `playwright --version`, `pytest --version`, and whether
   `pytest-playwright` is installed. Browsers must be installed with
   `playwright install` (CI: `playwright install --with-deps`).
2. Decide sync (`playwright.sync_api`) vs async (`playwright.async_api` + the
   `pytest-playwright-asyncio` plugin). Do not mix them in one test.
3. Identify the base URL, auth requirements, and which browser(s) to run.
4. Decide artifact policy: trace/screenshot/video on failure for CI, off locally
   unless debugging.
5. Treat auth state files as credentials — store under `playwright/.auth`, gitignored.

## Installation and first test

```bash
pip install pytest-playwright
playwright install
```

```python
import re

from playwright.sync_api import Page, expect


def test_playwright_homepage(page: Page) -> None:
    page.goto("https://playwright.dev/")
    expect(page).to_have_title(re.compile("Playwright"))
    page.get_by_role("link", name="Get started").click()
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()
```

Run with `pytest` (headless Chromium by default). Use `--headed`, `--browser`,
`--slowmo`, `--video`, `--screenshot`, and `--tracing` to change behavior.

## Locators and assertions

Prefer user-facing locators in this order: `get_by_role()`, `get_by_label()`,
`get_by_text()`, `get_by_test_id()`, then CSS/XPath as a last resort. Locators are
strict — an action fails if more than one element matches. Use `.filter(has=...)`
to narrow, with the inner locator relative to the outer one.

```python
from playwright.sync_api import Page, expect


def test_login_form(page: Page) -> None:
    page.goto("https://example.test/login")
    email = page.get_by_label("Email")
    email.fill("user@example.test")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
```

Use `expect(...)` web-first assertions, which retry until the condition holds or
the timeout (default 5 s) expires. Do not use `assert locator.is_visible()` for
conditions that may settle later. Actions auto-wait for visibility, stability,
event reception, and enabled/editable state (and inertness from 1.65).

Never use `time.sleep()` or fixed waits. Diagnose hydration/timing issues instead.

## Fixtures and configuration

Plugin fixtures: function-scoped `page`, `context`, `new_context`; session-scoped
`playwright`, `browser_type`, `browser`, and browser metadata. CLI options apply
only to plugin-created default fixtures — manually created contexts/pages do not
inherit them.

```python
# conftest.py
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
    }
```

```ini
# pytest.ini
[pytest]
addopts = --browser chromium --tracing=retain-on-failure --screenshot=only-on-failure
```

Note: pytest's built-in `request` fixture is not a Playwright API fixture. Use
`page.request`, `context.request`, or define an `api_request_context` fixture with
`playwright.request.new_context()`.

## Auth, network, and API

```python
from playwright.sync_api import Page, Route, expect


def test_mocked_api(page: Page) -> None:
    def handle(route: Route) -> None:
        route.fulfill(json=[{"id": 1, "name": "Strawberry"}])

    page.route("**/api/v1/fruits", handle)
    page.goto("https://demo.playwright.dev/api-mocking")
    expect(page.get_by_text("Strawberry", exact=True)).to_be_visible()
```

Every matching `page.route()` handler must call `continue_()`, `fulfill()`, or
`abort()`. URL globs match the whole URL. For auth, log in once, save
`context.storage_state(path=...)`, and feed it into `browser_context_args` for
later tests. Use `indexed_db=True` for IndexedDB-backed auth (v1.51+).

## Debugging and artifacts

- `PWDEBUG=1 pytest` opens the Playwright Inspector.
- `--tracing=retain-on-failure` plus `playwright show-trace <file>` opens the trace
  viewer — the primary tool for diagnosing a failed browser test.
- `--screenshot=only-on-failure`, `--video=retain-on-failure` for CI artifacts.
- Manually created contexts must be closed explicitly so videos/HARs flush.

## Reference router

| Need | Read |
|---|---|
| Plugin fixtures, CLI/config, browser matrix, async plugin | `references/pytest-plugin.md` |
| Locator strategy, strictness, actionability, `expect` | `references/locators-assertions.md` |
| Storage state, `page.route`, APIRequestContext | `references/auth-network-api.md` |
| Inspector, trace viewer, screenshots/videos, CI, anti-patterns | `references/debug-artifacts-ci.md` |

## Quality bar

Produce: a runnable test with imports; user-facing locators; web-first assertions;
an explicit browser/config choice; and a failure-artifact policy. Do not use fixed
sleeps, brittle CSS/XPath, or `assert` on a locator that should be retried. Keep
browser tests thin and defer generic pytest guidance to `pytest-skill`.
