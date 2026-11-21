# Authentication, network mocking, and API testing

## Authentication via storage state

Log in once, save state, reuse it. Auth files contain credentials — store under
`playwright/.auth` and gitignore that directory.

```python
from pathlib import Path
from typing import Any, Dict

import pytest
from playwright.sync_api import Browser, Page


AUTH_FILE = Path("playwright/.auth/user.json")


@pytest.fixture(scope="session")
def storage_state(browser: Browser) -> str:
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://example.test/login")
    page.get_by_label("Username").fill("test-user")
    page.get_by_label("Password").fill("test-password")
    page.get_by_role("button", name="Sign in").click()
    context.storage_state(path=AUTH_FILE)
    context.close()  # required so state is fully written
    return str(AUTH_FILE)


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: Dict[str, Any],
    storage_state: str,
) -> Dict[str, Any]:
    return {**browser_context_args, "storage_state": storage_state}


def test_authenticated_area(page: Page) -> None:
    page.goto("https://example.test/dashboard")
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()
```

Use `context.storage_state(indexed_db=True)` for IndexedDB-backed auth (v1.51+).
Credentials in storage state are supported from v1.62.

## Network mocking with page.route

```python
from playwright.sync_api import Page, Route, expect


def test_mocked_api(page: Page) -> None:
    def handle(route: Route) -> None:
        route.fulfill(
            status=200,
            json=[{"id": 1, "name": "Strawberry"}],
        )

    page.route("**/api/v1/fruits", handle)
    page.goto("https://demo.playwright.dev/api-mocking")
    expect(page.get_by_text("Strawberry", exact=True)).to_be_visible()
```

Rules:
- Every matching handler must call `continue_()`, `fulfill()`, or `abort()`.
- URL globs match the entire URL; use `**` to cross path segments.
- `route.fulfill()` can return `status`, `headers`, `body`, `json`, `content_type`.
- Service-worker requests are not intercepted unless service workers are blocked.
- Use `page.unroute()` to remove a handler; `page.unroute_all()` to clear all.

## API testing with APIRequestContext

```python
import pytest
from playwright.sync_api import APIRequestContext, Playwright


@pytest.fixture(scope="session")
def api(playwright: Playwright) -> APIRequestContext:
    return playwright.request.new_context(
        base_url="https://api.example.test",
        extra_http_headers={"Authorization": "Bearer test-token"},
    )


def test_create_item(api: APIRequestContext) -> None:
    response = api.post("/items", data={"name": "Ada"})
    assert response.ok
    assert response.json()["name"] == "Ada"
```

`page.request` and `context.request` share the browser context's cookies and
headers, which is useful for testing authenticated API calls from a logged-in page.

## HAR capture

`browser_context_args` can set `record_har_path` to record network traffic for a
test. Close the context explicitly so the HAR is flushed. Treat HAR files as
sensitive — they may contain tokens and personal data.
