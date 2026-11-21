# Integrations and anti-patterns

## pytest integration

Hypothesis runs on pytest. Load `pytest-skill` for runner, fixture, marker, and
collection fundamentals. Hypothesis-specific pytest surface:

- CLI: `--hypothesis-profile`, `--hypothesis-seed`, `--hypothesis-show-statistics`,
  `--hypothesis-verbosity`.
- Function-scoped pytest fixtures run once per `@given` test function, not once per
  generated input. This is the most common correctness trap
  (`HealthCheck.function_scoped_fixture`).
- Positional strategies fill parameters from the right, leaving leading arguments
  for pytest fixtures. Do not mix positional and keyword strategies.
- `@pytest.mark.parametrize` and `@given` can be combined, but keep the matrix small
  and understand that each parametrized case runs its own Hypothesis search.

## Django, NumPy, pandas

- Django: `hypothesis.extra.django` provides `from_model()` and a TestCase mixin;
  use `@given` with model strategies and let the mixin manage the database.
- NumPy: `st.arrays(dtype=..., shape=...)`; bound shape and dtype.
- pandas: `st.data_frames(columns=..., index=...)`; bound row counts.
- Verify installed extras before relying on these — the docs expose the strategies
  but extras are optional.

## Databricks / PySpark

There is no native PySpark DataFrame strategy. Generate bounded Python rows,
schemas, and options with Hypothesis, then create the DataFrame inside the test
using a session-scoped Spark fixture. Compare with `assertDataFrameEqual` or
chispa (see `pytest-databricks`).

```python
from hypothesis import given, settings, strategies as st


@settings(max_examples=20, deadline=None)
@given(st.lists(st.tuples(st.integers(), st.text(max_size=10)), max_size=50))
def test_transform_preserves_count(rows, spark_session):
    df = spark_session.createDataFrame(rows, ["id", "name"])
    result = transform(df)
    assert result.count() == len(rows)
```

Mark remote Databricks tests as integration tests, keep `max_examples` small, and
avoid function-scoped Spark fixtures unless each generated input truly needs a
fresh session.

## Anti-patterns

- Testing a single fixed example with `@given` — use a plain pytest test.
- Unbounded strategies producing huge values — bound sizes and ranges.
- `assume()` for domain constraints a strategy could express — use `.filter()` or
  a constrained strategy.
- Early `return` in a property test — it counts as a passing case.
- Blanket health-check suppression — fix the underlying generation problem.
- Relying on the example database for permanent regressions — use `@example`.
- `@reproduce_failure` blobs left in the suite — they are version-specific and
  temporary.
- `st.data()` when `@composite` would be clearer.
- `from_regex()` without `fullmatch=True` when the whole string must match.

## Verification checklist

1. The property and domain are stated in one sentence.
2. Strategies are bounded and terminate quickly.
3. A known bug is captured as a permanent `@example`.
4. Fixture scope is compatible with per-input generation.
5. Health checks are addressed, not blanket-suppressed.
6. The test is run with `--hypothesis-show-statistics` at least once to inspect cost.
