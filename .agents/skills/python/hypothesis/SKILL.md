---
name: hypothesis
description: >
  Property-based and stateful testing in Python with Hypothesis: `@given`, strategies,
  shrinking, `@composite`/`builds`/`from_type`, state machines with rules and bundles,
  settings/profiles, health checks, failure replay, and pytest integration. Use whenever
  a user asks for property-based tests, generative/fuzz tests, invariant or round-trip
  checks, Hypothesis strategies, shrinking a failing example, stateful testing, or
  reproducible random test inputs. Load the parent `pytest-skill` for runner and fixture
  fundamentals; Hypothesis generates inputs, pytest runs them.
compatibility: Python 3.11+; Hypothesis 6.170.x; pytest integration; optional NumPy, pandas, Django, Lark, dateutil, pytz extras
metadata:
  version: "1.0.0"
  docs-reviewed: "2026-11-21"
---

# Hypothesis — Property-Based Testing

Hypothesis generates inputs for a test that should hold for a whole domain, then
shrinks any failure to a minimal counterexample. Use it for invariants, round
trips, differential comparisons, and state machines — not for a single fixed
example (use a plain pytest test for that).

Treat a property as a claim about a domain, not a search for a passing input. A
property test that passes 100 generated cases is evidence, not proof; keep
explicit regression examples for bugs you have already found.

## Mandatory preflight

1. Confirm `hypothesis.__version__` and the pytest version; check installed extras
   before using NumPy/pandas/Django strategies.
2. State the property in one sentence: "for all inputs in domain D, invariant I
   holds." If you cannot state it, a property test is the wrong tool.
3. Bound the domain so generation terminates and failures are meaningful: constrain
   sizes, ranges, and alphabets in the strategy rather than rejecting in the test.
4. Decide how generated inputs interact with pytest fixtures. Function-scoped
   fixtures run once per Hypothesis test function, not once per generated input —
   this is a common correctness trap (`HealthCheck.function_scoped_fixture`).
5. Decide replay policy: the example database is a cache, not a guarantee. Keep
   permanent `@example` regressions for known bugs.

## Choose the right abstraction

| Need | Use |
|---|---|
| One fixed input/output pair | Plain pytest test (see `pytest-skill`) |
| Invariant over a domain | `@given` with a strategy |
| Inputs with internal structure | `@st.composite` or `st.builds` |
| Dependent values (b depends on a) | `@st.composite` with `draw` |
| Interleave generation with test logic | `st.data()` (sparingly) |
| Sequence of operations / protocol | `RuleBasedStateMachine` + `Bundle` |
| Find one minimal satisfying value | `find()` |
| Reproduce a CI failure | `@example` or `@reproduce_failure` |

## Core pattern

```python
from hypothesis import given, strategies as st


@given(st.lists(st.integers()), st.integers())
def test_append_increases_length(values: list[int], value: int) -> None:
    result = values + [value]
    assert len(result) == len(values) + 1
```

Positional strategies fill parameters from the right, which lets pytest fixtures
remain as leading arguments. Do not mix positional and keyword strategies, and do
not give the test function default argument values — Hypothesis rejects both.

Prefer strategy constraints and `.filter()` over broad `assume()`. `assume()`
rejects the whole example and can trigger `filter_too_much`; `.filter()` can retry
within generation. An early `return` incorrectly counts as a passing case.

## Custom and dependent strategies

```python
from dataclasses import dataclass

from hypothesis import given, strategies as st


@st.composite
def ordered_pairs(draw) -> tuple[int, int]:
    left = draw(st.integers())
    right = draw(st.integers(min_value=left))
    return left, right


@dataclass(frozen=True)
class Point:
    x: int
    y: int


points = st.builds(Point, x=st.integers(), y=st.integers())


@given(ordered_pairs(), points)
def test_generated_values(pair: tuple[int, int], point: Point) -> None:
    assert pair[0] <= pair[1]
    assert isinstance(point.x, int)
```

Use `@composite` (receives `draw` first) rather than complicated `flatmap()`
chains. `st.builds()` infers annotated constructor arguments; dataclasses are
handled natively. `st.from_regex()` matches a substring by default — pass
`fullmatch=True` when you need the whole string to match. Put simpler alternatives
first in `st.recursive()` so shrinking works well.

## Stateful testing

```python
from hypothesis import strategies as st
from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    initialize,
    invariant,
    rule,
)


class DictMachine(RuleBasedStateMachine):
    keys = Bundle("keys")

    def __init__(self) -> None:
        super().__init__()
        self.actual: dict[str, int] = {}
        self.expected: dict[str, int] = {}

    @initialize(target=keys)
    def seed_key(self) -> str:
        return "seed"

    @rule(target=keys, key=st.text(min_size=1, max_size=5))
    def add_key(self, key: str) -> str:
        return key

    @rule(key=keys, value=st.integers())
    def put(self, key: str, value: int) -> None:
        self.actual[key] = value
        self.expected[key] = value

    @rule(key=keys)
    def delete(self, key: str) -> None:
        self.actual.pop(key, None)
        self.expected.pop(key, None)

    @invariant()
    def agrees_with_model(self) -> None:
        assert self.actual == self.expected


TestDictMachine = DictMachine.TestCase
```

Compare the system under test against a simple model via `@invariant()`. Use
`preconditions=` to constrain rules and `Bundle`s to pass generated values between
steps.

## Settings, health checks, and replay

```python
from hypothesis import HealthCheck, example, given, settings, strategies as st
from hypothesis.database import DirectoryBasedExampleDatabase

settings.register_profile(
    "local",
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
    database=DirectoryBasedExampleDatabase(".hypothesis/examples"),
)
settings.load_profile("local")


@example("known regression input")
@given(st.text())
def test_utf8_round_trip(value: str) -> None:
    assert value.encode().decode() == value
```

Default `max_examples` is 100; the actual number of calls can differ because of
exhaustion, rejection, shrinking, and replay. Default deadline is 200 ms locally
and disabled in CI. Health checks are proactive warnings — do not blanket-suppress
them. `@reproduce_failure` blobs are temporary and version-specific; prefer a
permanent `@example` for a regression. Use `--hypothesis-profile`,
`--hypothesis-seed`, and `--hypothesis-show-statistics` from pytest.

## Reference router

| Need | Read |
|---|---|
| Built-in strategies, composite/builds/recursive, NumPy/pandas | `references/strategies.md` |
| Settings, profiles, health checks, database, replay, flaky tests | `references/settings-and-replay.md` |
| State machines, rules, bundles, invariants, preconditions | `references/stateful.md` |
| pytest/Django/Databricks integration and anti-patterns | `references/integrations.md` |

## Quality bar

Produce: the stated property and domain; bounded strategies; a runnable test with
imports; a note on fixture scope and `max_examples`; and a permanent regression
example for any bug found. Do not claim exhaustive coverage, and do not suppress a
health check without explaining why it is safe.
