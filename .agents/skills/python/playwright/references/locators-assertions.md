# Locators, actionability, and web-first assertions

## Locator priority

1. `page.get_by_role("button", name="Sign in")` — accessible role + name
2. `page.get_by_label("Email")` — form label
3. `page.get_by_text("Submit", exact=True)` — visible text
4. `page.get_by_test_id("submit-btn")` — explicit test id
5. CSS/XPath — last resort, keep short and structural

Locators are strict: an action or assertion fails if multiple elements match.
Use `.filter()` to narrow, with the inner locator relative to the outer one:

```python
from playwright.sync_api import Page, expect

row = page.get_by_role("row").filter(has=page.get_by_text("Ada"))
expect(row.get_by_role("cell")).to_have_text("Engineer")
```

Chaining: `page.get_by_role("listitem").get_by_role("link", name="Details")`.

## Actionability

Actions auto-wait for the element to be visible, stable, receive events, enabled,
and editable (and not inert from Playwright 1.65). Common actions: `.click()`,
`.fill()`, `.check()`, `.select_option()`, `.press()`, `.hover()`, `.scroll_into_view_if_needed()`.

Never use `time.sleep()` or fixed waits. If an element is not ready, diagnose why
(hydration, animation, network) rather than adding a delay. Use
`expect(locator).to_be_visible()` to wait for a condition.

## Web-first assertions

`expect()` retries until the condition holds or the timeout (default 5 s) expires.
Prefer it over `assert locator.is_visible()` for anything that may settle later.

```python
import re

from playwright.sync_api import Page, expect


def test_assertions(page: Page) -> None:
    page.goto("https://example.test")
    expect(page).to_have_title(re.compile("Example"))
    expect(page.get_by_role("heading")).to_be_visible()
    expect(page.get_by_test_id("count")).to_have_text("3")
    expect(page.get_by_role("button", name="Save")).to_be_enabled()
    expect(page.locator(".items")).to_have_count(3)
```

Common matchers: `to_be_visible`, `to_be_hidden`, `to_have_text`, `to_contain_text`,
`to_have_value`, `to_be_enabled`, `to_be_checked`, `to_have_count`, `to_have_class`,
`to_have_attribute`, `to_have_url`. Use `not_` to invert:
`expect(locator).not_to_be_visible()`.

Soft assertions (require `pytest-playwright>=0.8.0`) collect multiple failures
instead of stopping at the first: `expect.soft(locator).to_have_text(...)`.

## Frames and dialogs

- Frames: `page.frame_locator("iframe").get_by_role(...)`.
- Dialogs: register `page.on("dialog", lambda d: d.accept())` before the action
  that triggers them, otherwise the dialog blocks the test.

## Common mistakes

- Long CSS/XPath selectors that break on markup changes — use role/label/test id.
- `assert locator.is_visible()` instead of `expect(...).to_be_visible()` — no retry.
- Fixed sleeps — flaky and slow.
- Ambiguous locators — strict mode will fail; narrow with `.filter()`.
- `filter(has=...)` with an absolute locator — the inner locator must be relative.
