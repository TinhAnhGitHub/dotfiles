# Hypothesis strategies

All examples assume `from hypothesis import given, strategies as st`.

## Built-in strategies

| Strategy | Generates | Notes |
|---|---|---|
| `st.integers(min_value=, max_value=)` | ints | Bound ranges to keep failures meaningful |
| `st.floats()` | floats | Excludes NaN/inf by default; `allow_nan=True` to include |
| `st.booleans()`, `st.none()` | bool / None | Useful in unions |
| `st.text(alphabet=, min_size=, max_size=)` | str | Bound size; use `st.characters()` for the alphabet |
| `st.binary()` | bytes | `min_size`/`max_size` |
| `st.lists(elements, min_size=, max_size=, unique=)` | list | `unique=True` needs a hashable/equatable element strategy |
| `st.sets`, `st.frozensets`, `st.dictionaries(keys, values)` | containers | Dicts need a key strategy |
| `st.tuples(*strategies)`, `st.fixed_dictionaries({...})` | fixed shapes | Good for structured records |
| `st.sampled_from(seq)` | one of seq | Does not copy mutable values; rejects empty seq; shrinks toward earlier items |
| `st.from_regex(pattern, fullmatch=True)` | matching str | Matches a substring by default — use `fullmatch=True` |
| `st.from_type(T)`, `st.builds(T, ...)` | instances | `register_type_strategy` for reusable overrides |
| `st.enums(EnumClass)`, `st.dataclasses(cls)` | enum/dataclass values | Dataclasses handled natively |
| `st.recursive(base, extend, max_leaves=100)` | nested structures | Put simpler alternatives first for shrinking |
| `st.deferred(lambda: ...)` | lazy strategy | For mutually recursive definitions |
| `st.data()` | interactive draws | Interleave generation with test logic; incompatible with `@example` |

## Adapting strategies

- `strategy.map(fn)` — transform generated values.
- `strategy.filter(pred)` — constrain; retries within generation, better than `assume()`.
- `strategy.flatmap(fn)` — dependent generation; prefer `@composite` for readability.
- `st.one_of(a, b, c)` — union; simpler branches first.
- `st.just(value)` — a single value.

```python
from hypothesis import given, strategies as st

nonempty = st.lists(st.integers(), min_size=1, max_size=20)


@given(nonempty)
def test_first_is_present(values: list[int]) -> None:
    assert values[0] in values
```

## Composite and dependent strategies

```python
from dataclasses import dataclass

from hypothesis import given, strategies as st


@st.composite
def user_payload(draw) -> dict:
    name = draw(st.text(min_size=1, max_size=32))
    age = draw(st.integers(min_value=0, max_value=120))
    tags = draw(st.lists(st.text(max_size=10), max_size=5))
    return {"name": name, "age": age, "tags": tags}


@given(user_payload())
def test_payload_shape(payload: dict) -> None:
    assert 0 <= payload["age"] <= 120
    assert len(payload["name"]) >= 1
```

`@composite` receives `draw` as its first argument. Use it instead of nested
`flatmap()` chains. Use `data()` only when generation must be interleaved with
test logic; it produces less readable failures and cannot be used with `@example`.

## Type-driven generation

```python
from dataclasses import dataclass

from hypothesis import given, strategies as st


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@given(st.builds(Point))
def test_point_fields(point: Point) -> None:
    assert isinstance(point.x, int) and isinstance(point.y, int)
```

`st.builds()` infers annotated constructor arguments. Use explicit strategies when
defaults or validators need tighter constraints. `st.from_type(T)` works for many
standard types; register custom ones with `st.register_type_strategy`.

## NumPy and pandas

Hypothesis exposes `st.arrays(...)` for NumPy and `st.data_frames(...)` for pandas
when those libraries are installed. Bound shape/dtype and row counts. There is no
native PySpark DataFrame strategy — see `references/integrations.md`.

## Common mistakes

- Unbounded `st.text()` / `st.lists()` producing huge values — bound sizes.
- `assume()` used to constrain a domain that a strategy could express directly.
- `from_regex()` without `fullmatch=True` — matches a substring, not the whole string.
- Mutable defaults in `sampled_from()` — values are not copied.
- Recursive strategies with complex branches first — poor shrinking.
