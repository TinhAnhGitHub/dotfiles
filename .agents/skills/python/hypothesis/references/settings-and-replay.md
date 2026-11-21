# Settings, health checks, and replay

## Settings and profiles

```python
from hypothesis import HealthCheck, settings

settings.register_profile(
    "ci",
    max_examples=200,
    deadline=None,          # CI is slow; deadlines are local-only by default
    suppress_health_check=[HealthCheck.too_slow],
)
settings.register_profile("dev", max_examples=25)
settings.load_profile("dev")
```

Select a profile from pytest with `--hypothesis-profile=ci`. Default `max_examples`
is 100; the actual number of calls can be lower (exhaustion, rejection) or higher
(shrinking, replay). Default deadline is 200 ms locally and disabled in CI.

Common settings: `max_examples`, `deadline`, `derandomize`, `seed`, `verbosity`,
`database`, `suppress_health_check`, `print_blob`, `stateful_step_count`.

## Health checks

Health checks are proactive warnings about tests that are likely slow, flaky, or
ineffective. Do not blanket-suppress them. Notable ones:

- `HealthCheck.too_slow` — generation dominates runtime; bound strategies.
- `HealthCheck.filter_too_much` — too many rejected examples; use `.filter()` or
  tighten the strategy instead of `assume()`.
- `HealthCheck.function_scoped_fixture` — a function-scoped pytest fixture is used
  by a `@given` test; it runs once per test function, not once per generated input.
  This is correctness-sensitive: either make the fixture session/module scoped and
  reset state inside the test, or confirm per-input reuse is actually intended.
- `HealthCheck.data_too_large` — generated values are very large; bound sizes.

## Replaying failures

The example database is a replay cache, not a correctness guarantee. Entries can
disappear after source or Hypothesis-version changes. Keep permanent `@example`
regressions for bugs you have found.

```python
from hypothesis import example, given, strategies as st


@example("")            # permanent regression for a known edge case
@example("known bug input")
@given(st.text())
def test_round_trip(value: str) -> None:
    assert value.encode().decode() == value
```

`@reproduce_failure(version, blob)` is temporary and version-specific — paste the
exact decorator printed by CI, reproduce, then replace it with a permanent
`@example`. Use `--hypothesis-seed` to reproduce a run deterministically and
`--hypothesis-show-statistics` to inspect generation cost.

## Flaky tests and deadlines

- A flaky failure often means hidden state, time dependence, or a function-scoped
  fixture. Fix the cause rather than raising `deadline` or suppressing checks.
- `deadline=None` disables the deadline for a test/profile; prefer fixing slow
  generation over disabling it globally.
- `reject()` unconditionally discards a case and is mainly for generated
  exception-suppression harnesses; outside test contexts it has been deprecated
  since 6.87.0. Prefer `.filter()` or `assume(False)`.

## `find()`

```python
from hypothesis import find, strategies as st

value = find(st.integers(), lambda x: x > 1000)
assert value > 1000
```

`find(strategy, predicate, *, settings=None, random=None, database_key=None)`
returns a minimal satisfying value and raises `NoSuchExample` if none is found.
Its default example budget is larger than a normal test (around 2,000).
