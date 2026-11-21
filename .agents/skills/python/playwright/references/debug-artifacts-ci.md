# Debugging, artifacts, and CI

## Debugging a failed browser test

1. Re-run with `--headed` to watch the browser.
2. Use `PWDEBUG=1 pytest` to open the Playwright Inspector and step through.
3. Prefer the trace viewer: `--tracing=retain-on-failure`, then
   `playwright show-trace <path-to-trace.zip>`. The trace shows DOM snapshots,
   actions, network, and console — the primary tool for diagnosing flaky UI tests.
4. Add `--screenshot=only-on-failure` and `--video=retain-on-failure` for CI.
5. Use `page.pause()` in a headed local run to stop at a point of interest.

## Artifact flags

| Flag | Effect |
|---|---|
| `--tracing=on\|retain-on-failure\|off` | Record execution trace |
| `--screenshot=on\|only-on-failure\|off` | Capture screenshots |
| `--video=on\|retain-on-failure\|off` | Record video |
| `--output=PATH` | Directory for artifacts |

Manually created contexts must be closed explicitly so videos/HARs flush. Artifacts
may contain sensitive data — restrict access and purge after triage.

## CI

```yaml
# GitHub Actions example
- run: pip install pytest-playwright
- run: playwright install --with-deps
- run: pytest --browser chromium --tracing=retain-on-failure
- uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: playwright-report
    path: test-results/
```

- Install browser OS dependencies with `playwright install --with-deps` on Linux.
- Pin the Playwright version so browser binaries and the Python package match.
- Keep browser tests in a separate CI stage from fast unit tests.
- Start conservatively with parallelism; stateful apps and shared auth break under
  aggressive xdist. Defer generic xdist guidance to `pytest-skill`.

## Anti-patterns

- `time.sleep()` or fixed waits — use web-first assertions and auto-waiting.
- Brittle CSS/XPath selectors — use role/label/test id.
- `assert locator.is_visible()` instead of `expect(...).to_be_visible()`.
- Sharing a page/context across tests — the plugin isolates per test by default.
- Committing auth state files — gitignore `playwright/.auth`.
- Leaving tracing/video on for every local run — enable on failure for CI.
- Testing business logic through the browser — keep logic in unit tests.

## Version notes (Playwright 1.65.x)

- Actionability now includes inertness checks (1.65).
- `record_video_fps` added in 1.64; storage-state `credentials` in 1.62;
  `locator.visible` in 1.63; IndexedDB storage state in 1.51.
- Soft assertions require `pytest-playwright>=0.8.0`.
