# pytest Best Practices Reference

> Comprehensive best practices for writing maintainable, fast, and reliable pytest test suites.
> Source: https://docs.pytest.org/en/stable/explanation/best-practices.html and community wisdom.

## Table of Contents

- [Test Organization](#test-organization)
- [Test Naming and Structure](#test-naming-and-structure)
- [Test Isolation](#test-isolation)
- [Fixture Best Practices](#fixture-best-practices)
- [Parametrization Best Practices](#parametrization-best-practices)
- [Mocking Best Practices](#mocking-best-practices)
- [Assertion Best Practices](#assertion-best-practices)
- [Speed and Performance](#speed-and-performance)
- [CI/CD Integration](#cicd-integration)
- [Coverage Best Practices](#coverage-best-practices)
- [Test Pyramid for Data Projects](#test-pyramid-for-data-projects)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Code Review Checklist for Tests](#code-review-checklist-for-tests)

---

## Test Organization

### Use the src-layout with tests outside the package

```
my_project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── pipeline.py
│       └── transforms.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── conftest.py
│   │   ├── test_pipeline.py
│   │   └── test_transforms.py
│   ├── integration/
│   │   ├── conftest.py
│   │   └── test_pipeline_integration.py
│   └── e2e/
│       ├── conftest.py
│       └── test_pipeline_e2e.py
├── pyproject.toml
└── README.md
```

**Why src-layout?**
- Prevents accidental imports of `tests` as a package
- Forces you to install your package to test it (catches packaging bugs)
- Avoids `sys.path` manipulation issues
- Works well with `--import-mode=importlib`

**Why tests outside src?**
- Tests are development-time artifacts, not runtime dependencies
- They won't be included when you `pip install` your package
- Clear separation of production code and test code

### Separate tests by tier

```
tests/
├── unit/          # Fast, no external deps, mocked everything
├── integration/   # Real Spark, Databricks Connect, local services
└── e2e/           # Real Databricks workspace resources
```

Run tiers separately in CI:
```bash
# Fast feedback on every commit
pytest tests/unit/ -m unit

# PR checks
pytest tests/unit/ tests/integration/ -m "not e2e"

# Nightly
pytest tests/ -m "not slow"
```

### One conftest.py per tier

Each tier has different fixture needs:
- **Root `conftest.py`**: Global stubs (sys.modules), markers, hooks
- **`tests/unit/conftest.py`**: Mock fixtures (mock_dbutils, mock_ws, mock_spark)
- **`tests/integration/conftest.py`**: Real Spark session fixture
- **`tests/e2e/conftest.py`**: pytester fixtures, env_or_skip, debug_env_name

---

## Test Naming and Structure

### Name tests by behavior, not by implementation

```python
# BAD — describes implementation
def test_filter_uses_where_clause():
    ...

# GOOD — describes behavior
def test_filter_returns_only_active_users():
    ...

def test_filter_excludes_users_without_status():
    ...
```

### Use descriptive test names with the pattern: `test_<unit>_<scenario>_<expectation>`

```python
def test_transform_filters_rows_by_date_range():
    ...

def test_transform_handles_empty_dataframe():
    ...

def test_transform_raises_on_missing_column():
    ...
```

### Group related tests in classes (optional, but useful for shared fixtures)

```python
class TestTransformFilters:
    """Tests for the filter transformation."""

    def test_filters_by_single_date(self, spark):
        ...

    def test_filters_by_date_range(self, spark):
        ...

    def test_returns_empty_for_no_matches(self, spark):
        ...
```

Classes in pytest:
- Must NOT have `__init__`
- Are used only for grouping — no inheritance
- Share fixtures defined at class level
- Can be marked as a whole: `@pytest.mark.unit class TestFoo:`

### Arrange-Act-Assert (AAA) pattern

```python
def test_user_creation(spark):
    # Arrange
    input_data = [("Alice", 30), ("Bob", 25)]
    df = spark.createDataFrame(input_data, ["name", "age"])

    # Act
    result = add_age_category(df)

    # Assert
    assert result.count() == 2
    categories = result.select("category").distinct().collect()
    assert len(categories) <= 3
```

Keep the three sections visually separated. If a test is hard to structure this way,
it might be testing too many things.

---

## Test Isolation

### Tests must not depend on each other

```python
# BAD — test_b depends on test_a having run
created_id = None

def test_a_create():
    global created_id
    created_id = create_resource()

def test_b_read():
    assert read_resource(created_id) is not None  # fails if test_a didn't run
```

```python
# GOOD — each test is self-contained
def test_create_and_read(make_table):
    table = make_table()
    created = create_resource(table)
    assert read_resource(created.id) is not None
```

### Use function-scoped fixtures for mutable state

```python
@pytest.fixture  # function scope by default
def clean_dataframe(spark):
    """Fresh DataFrame for each test — no shared state."""
    return spark.createDataFrame([("Alice", 30)], ["name", "age"])
```

### Avoid global state and singletons

If your code uses global state (e.g., a global SparkSession), reset it in an autouse fixture:

```python
@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test."""
    my_module._global_cache = {}
    yield
    my_module._global_cache = {}
```

### Use `tmp_path` for file-based tests

```python
def test_file_processing(tmp_path):
    # Each test gets its own clean temp directory
    input_file = tmp_path / "input.csv"
    input_file.write_text("col1,col2\n1,2\n")

    result = process_file(str(input_file))

    output_file = tmp_path / "output.csv"
    assert output_file.exists()
```

---

## Fixture Best Practices

### Choose the right scope

| Fixture type | Recommended scope | Why |
|-------------|-------------------|-----|
| Mock objects | `function` | Each test gets a fresh mock |
| Small test data | `function` | Prevents cross-test contamination |
| Config files | `module` | Loaded once per test file |
| SparkSession (local) | `session` | Expensive to create, stateless for reads |
| Database connection | `session` | Expensive to establish |
| HTTP client | `session` | Connection pooling |
| Databricks WorkspaceClient | `session` | Auth is expensive |

### Use yield for cleanup

```python
@pytest.fixture
def spark_session():
    spark = SparkSession.builder.master("local[*]").getOrCreate()
    yield spark
    spark.stop()  # Always runs, even if test fails
```

### Make fixtures composable

```python
@pytest.fixture
def catalog_name():
    return "test_catalog"

@pytest.fixture
def schema_name(catalog_name):
    return f"{catalog_name}.test_schema"

@pytest.fixture
def test_table(spark, schema_name):
    """Create a table, yield it, clean up."""
    spark.sql(f"CREATE TABLE {schema_name}.test (id INT)")
    yield spark.table(f"{schema_name}.test")
    spark.sql(f"DROP TABLE IF EXISTS {schema_name}.test")
```

### Factory fixtures for flexible test data

```python
@pytest.fixture
def make_user(spark):
    """Factory: create users with custom attributes."""
    created = []
    def _make(name="Alice", age=30, active=True):
        user = spark.createDataFrame([(name, age, active)], ["name", "age", "active"])
        created.append(user)
        return user
    yield _make
    # Cleanup if needed
```

```python
def test_active_users(make_user):
    user1 = make_user(name="Alice", active=True)
    user2 = make_user(name="Bob", active=False)

    result = filter_active(make_user(name="Alice", active=True).union(user2))
    assert result.count() == 1
```

### Don't over-use autouse

```python
# BAD — hides dependencies, runs for tests that don't need it
@pytest.fixture(autouse=True)
def spark_session():
    ...

# GOOD — explicit, only runs when requested
@pytest.fixture(scope="session")
def spark_session():
    ...
```

Use `autouse` only for:
- Resetting global state
- Stubbing `sys.modules`
- Setting up logging
- Environment variable cleanup

### Give fixtures descriptive docstrings

```python
@pytest.fixture(scope="session")
def spark():
    """A local SparkSession for testing transformations.

    Created once per session and shared across all tests.
    Uses local[*] to use all available CPU cores.
    """
    ...
```

pytest shows fixture docstrings in `pytest --fixtures` output.

---

## Parametrization Best Practices

### Parametrize instead of copy-pasting

```python
# BAD — three tests with copy-pasted logic
def test_add_positive():
    assert add(1, 2) == 3

def test_add_negative():
    assert add(-1, -2) == -3

def test_add_zero():
    assert add(0, 0) == 0

# GOOD — one parametrized test
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (-1, -2, -3),
    (0, 0, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Use descriptive IDs

```python
@pytest.mark.parametrize("input, expected", [
    pytest.param("hello", 5, id="normal_string"),
    pytest.param("", 0, id="empty_string"),
    pytest.param("a" * 100, 100, id="long_string"),
    pytest.param(None, 0, id="none_input", marks=pytest.mark.xfail),
])
def test_string_length(input, expected):
    assert safe_len(input) == expected
```

Output: `test_string_length[normal_string] PASSED`

### Test edge cases explicitly

```python
@pytest.mark.parametrize("df_data, expected_count", [
    # Normal cases
    pytest.param([("Alice", 30)], 1, id="single_row"),
    pytest.param([("Alice", 30), ("Bob", 25)], 2, id="multiple_rows"),
    # Edge cases
    pytest.param([], 0, id="empty_dataframe"),
    pytest.param([("Alice", None)], 1, id="null_value"),
    pytest.param([(None, 30)], 1, id="null_key"),
    # Error cases
    pytest.param(None, 0, id="none_input", marks=pytest.mark.xfail(raises=AttributeError)),
])
def test_count_users(spark, df_data, expected_count):
    if df_data is not None:
        df = spark.createDataFrame(df_data, ["name", "age"])
    else:
        df = None
    assert count_users(df) == expected_count
```

### Don't over-parametrize

If a test has too many parameters, it becomes hard to understand. Split into multiple
focused tests instead:

```python
# BAD — too many parameters, hard to understand
@pytest.mark.parametrize("input, format, compression, expected", [
    ...
])
def test_read_file(input, format, compression, expected):
    ...

# GOOD — separate concerns
@pytest.mark.parametrize("format", ["csv", "json", "parquet"])
def test_read_supports_formats(format):
    ...

@pytest.mark.parametrize("compression", ["none", "gzip", "snappy"])
def test_read_supports_compression(compression):
    ...
```

---

## Mocking Best Practices

### Mock at the boundary, not internally

```python
# BAD — mocking internal implementation details
def test_process(mocker):
    mocker.patch("my_module._internal_helper")

# GOOD — mocking external boundaries
def test_process(mocker):
    mocker.patch("my_module.SparkSession")  # mock the external dependency
```

### Prefer dependency injection over mocking

```python
# BAD — hard to test, requires mocking
def process_data():
    spark = SparkSession.builder.getOrCreate()  # global dependency
    df = spark.read.table("source")
    return transform(df)

# GOOD — dependency injection, easy to test
def process_data(spark):
    df = spark.read.table("source")
    return transform(df)

def test_process_data(spark_session):
    result = process_data(spark_session)
    assert result.count() > 0
```

### Use `spec` to catch mock misuse

```python
from unittest.mock import MagicMock

def test_with_spec():
    # Without spec — any attribute access returns a mock (silently wrong)
    bad_mock = MagicMock()

    # With spec — AttributeError on wrong attribute access
    good_mock = MagicMock(spec=WorkspaceClient)
    good_mock.unknown_method()  # raises AttributeError
```

### Verify important calls, not every call

```python
def test_create_catalog(mocker):
    mock_ws = mocker.patch("my_module.WorkspaceClient")

    create_catalog(mock_ws, "test_catalog")

    # GOOD — verify the important call
    mock_ws.catalogs.create.assert_called_once_with(name="test_catalog")

    # BAD — over-specifying implementation details
    # mock_ws.__init__.assert_called_once()
    # assert mock_ws.call_count == 1
```

### Use `side_effect` for different return values per call

```python
def test_retry_logic(mocker):
    mock_api = mocker.patch("my_module.api_call")
    mock_api.side_effect = [ConnectionError(), ConnectionError(), "success"]

    result = retry_api_call(max_retries=3)

    assert result == "success"
    assert mock_api.call_count == 3
```

### Reset mocks between tests

`mocker` (pytest-mock) and `monkeypatch` auto-clean up. If using raw `unittest.mock`:

```python
@pytest.fixture
def mock_client():
    mock = MagicMock(spec=WorkspaceClient)
    # Reset before each test (mocker does this automatically)
    mock.reset_mock()
    return mock
```

---

## Assertion Best Practices

### Use plain `assert` — pytest's introspection gives great error messages

```python
def test_transform(spark):
    result = transform(input_df)
    assert result.count() == 5
    # On failure: E   assert 3 == 5
```

### Add messages for complex assertions

```python
def test_schema(spark):
    result = transform(input_df)
    expected_fields = ["name", "age", "category"]
    actual_fields = result.schema.fieldNames()

    assert set(actual_fields) == set(expected_fields), \
        f"Schema mismatch. Expected: {expected_fields}, Got: {actual_fields}"
```

### Use `pytest.approx` for floats

```python
def test_average():
    result = calculate_average([1.0, 2.0, 3.0])
    assert result == pytest.approx(2.0)

    # With tolerance
    assert result == pytest.approx(2.0, rel=1e-3)  # relative tolerance
    assert result == pytest.approx(2.0, abs=0.01)  # absolute tolerance
```

### Use `pytest.raises` for expected exceptions

```python
def test_invalid_input():
    with pytest.raises(ValueError, match="column 'name' not found"):
        transform(invalid_df)

# With specific exception type
def test_missing_column():
    with pytest.raises(KeyError) as exc_info:
        df.select("nonexistent_column")
    assert "nonexistent_column" in str(exc_info.value)
```

### Use `pytest.warns` for expected warnings

```python
def test_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="will be removed"):
        deprecated_function()
```

### Assert on data, not on implementation

```python
# BAD — tests implementation details
def test_filter(mocker):
    mock_filter = mocker.patch("pyspark.sql.DataFrame.filter")
    transform(df)
    mock_filter.assert_called_once()

# GOOD — tests behavior
def test_filter(spark):
    df = spark.createDataFrame([("Alice", "active"), ("Bob", "inactive")], ["name", "status"])
    result = filter_active(df)
    rows = result.collect()
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"
```

---

## Speed and Performance

### Keep unit tests under 100ms

```python
# BAD — unit test that starts real Spark
def test_transform():
    spark = SparkSession.builder.master("local[*]").getOrCreate()  # 3+ seconds
    ...

# GOOD — unit test with mock or small local Spark
def test_transform(mock_spark):
    ...

# Or use a session-scoped Spark fixture shared across all tests
```

### Share expensive resources with session-scoped fixtures

```python
@pytest.fixture(scope="session")
def spark():
    """One SparkSession for the entire test session."""
    spark = SparkSession.builder.master("local[*]").appName("tests").getOrCreate()
    yield spark
    spark.stop()
```

### Use `--durations` to find slow tests

```bash
pytest --durations=10  # show 10 slowest tests
```

### Run tests in parallel with pytest-xdist

```bash
pytest -n auto              # use all CPU cores
pytest -n 4                 # use 4 workers
pytest -n auto --dist loadfile  # distribute by file (better for mixed durations)
pytest -n auto --dist loadscope  # distribute by class/module
```

**Caveat**: Tests must be isolated for parallel execution. No shared mutable state,
no order dependencies, no file conflicts.

### Use `--sw` (stepwise) during development

```bash
pytest --sw  # stop at first failure, resume from there next time
```

### Skip slow tests by default

```toml
[tool.pytest.ini_options]
markers = ["slow: tests that take more than 10 seconds"]
```

```bash
pytest -m "not slow"  # run fast tests only
pytest -m slow        # run only slow tests (e.g., in nightly CI)
```

### Use `pytest-timeout` to catch hanging tests

```bash
pytest --timeout=300  # fail tests that take > 300 seconds
```

```toml
[tool.pytest.ini_options]
timeout = 300
```

---

## CI/CD Integration

### Run tests in stages

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit/ -m unit --cov=src --cov-report=xml

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/integration/ -m integration

  e2e-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'  # nightly only
    steps:
      - run: pytest tests/e2e/ -m e2e
```

### Use JUnit XML for CI reporting

```bash
pytest --junitxml=test-results.xml
```

Most CI systems (GitHub Actions, GitLab CI, Jenkins) parse JUnit XML for test reporting.

### Use `--strict-markers` and `--strict-config` in CI

```bash
pytest --strict-markers --strict-config
```

This catches typos in marker names and configuration errors early.

### Cache pip dependencies

```yaml
# .github/workflows/test.yml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
```

### Use `pytest --lf` for PR checks

If a previous CI run failed, re-running only the failed tests gives faster feedback:

```bash
pytest --lf  # only run tests that failed last time
```

### Coverage thresholds

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

Fails the build if coverage drops below 80%.

---

## Coverage Best Practices

### Configure coverage in `pyproject.toml`

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "tests/*",
    "*/__init__.py",
    "*/conftest.py",
    "*/_version.py",
]
branch = true  # measure branch coverage, not just line coverage

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
fail_under = 80
show_missing = true
```

### Use branch coverage

Branch coverage catches missed `if/else` paths that line coverage misses:

```toml
[tool.coverage.run]
branch = true
```

```python
def classify(x):
    if x > 0:       # line covered
        return "pos"
    else:            # line covered
        return "neg"

# Line coverage: 100% if you test classify(1)
# Branch coverage: 50% — the else branch is not tested
```

### Don't chase 100% coverage

- 80-90% is a good target for most projects
- Focus on covering critical business logic
- Use `# pragma: no cover` for intentionally uncovered code (e.g., debug-only paths)
- Coverage measures **what was executed**, not **what was tested** — a line being covered
  doesn't mean it's correct

### Use `--cov-report=term-missing` to find gaps

```bash
pytest --cov=src --cov-report=term-missing
```

Shows which lines are not covered, making it easy to identify gaps.

---

## Test Pyramid for Data Projects

For PySpark/Databricks projects, the test pyramid looks different:

```
        /\
       /e2e\        Few — real workspace resources (minutes each)
      /------\
     /integration\  Some — real Spark, Databricks Connect (seconds each)
    /--------------\
   /     unit       \ Many — mocked, fast (milliseconds each)
  /-------------------\
```

### Unit tests (many, fast)

- Test pure transformation logic (takes DataFrame, returns DataFrame)
- Mock Spark, dbutils, SDK clients
- Use local Spark only for DataFrame creation/comparison
- Target: < 100ms per test, thousands of tests

```python
def test_filter_active(spark):
    df = spark.createDataFrame([("Alice", "active"), ("Bob", "inactive")], ["name", "status"])
    result = filter_active(df)
    assert result.count() == 1
```

### Integration tests (some, medium)

- Test with real Spark (local or Databricks Connect)
- Test I/O operations (read/write Delta tables, volumes)
- Test with real Databricks SDK (WorkspaceClient)
- Target: 1-30s per test, hundreds of tests

```python
@pytest.mark.integration
def test_write_to_delta(spark):
    df = spark.createDataFrame([("Alice", 30)], ["name", "age"])
    df.write.mode("overwrite").saveAsTable("test_schema.users")
    result = spark.read.table("test_schema.users")
    assert result.count() == 1
```

### E2E tests (few, slow)

- Test with real Databricks workspace resources
- Use pytester fixtures (make_catalog, make_schema, make_table, make_job)
- Test full pipelines end-to-end
- Target: 10-60s per test, tens of tests

```python
@pytest.mark.e2e
def test_pipeline_creates_table(make_catalog, make_schema, make_table):
    catalog = make_catalog()
    schema = make_schema(catalog_name=catalog.name)
    table = make_table(catalog_name=catalog.name, schema_name=schema.name)

    run_pipeline(catalog.name, schema.name, table.name)

    result = spark.read.table(f"{catalog.name}.{schema.name}.{table.name}")
    assert result.count() > 0
```

### Decision guide

```
Does the function use Spark?
├── NO → Unit test (mock everything)
├── YES, but only transformations → Unit test with local Spark
├── YES, reads/writes Delta/UC → Integration test with Databricks Connect
└── YES, creates/manages resources → E2E test with pytester fixtures
```

---

## Anti-Patterns to Avoid

### 1. Testing implementation, not behavior

```python
# BAD
def test_uses_filter(mocker):
    mock_filter = mocker.patch("pyspark.sql.DataFrame.filter")
    process(df)
    mock_filter.assert_called_once()

# GOOD
def test_returns_correct_rows(spark):
    df = spark.createDataFrame([("Alice", "active"), ("Bob", "inactive")], ["name", "status"])
    result = process(df)
    assert result.count() == 1
```

### 2. Over-mocking

```python
# BAD — mocking everything, testing nothing real
def test_pipeline(mocker):
    mocker.patch("module.SparkSession")
    mocker.patch("module.DataFrame")
    mocker.patch("module.transform")
    mocker.patch("module.write")
    run_pipeline()  # what are we even testing?
```

### 3. Brittle assertions

```python
# BAD — breaks if order changes
def test_results(df):
    result = process(df).collect()
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"

# GOOD — order-independent
def test_results(df):
    result = process(df).collect()
    names = {row["name"] for row in result}
    assert names == {"Alice", "Bob"}
```

### 4. Shared mutable state

```python
# BAD — tests affect each other
shared_df = None

def test_a(spark):
    global shared_df
    shared_df = spark.createDataFrame(...)

def test_b():
    assert shared_df.count() > 0  # fails if test_a didn't run
```

### 5. Catch-all exception handling

```python
# BAD — hides bugs
def test_process():
    try:
        result = process()
        assert result is not None
    except Exception:
        pass  # swallows all errors

# GOOD — let specific exceptions propagate
def test_process():
    result = process()
    assert result is not None

# Or test for expected exceptions
def test_process_raises_on_invalid():
    with pytest.raises(ValueError):
        process(invalid_input)
```

### 6. Test interdependencies

```python
# BAD — tests must run in order
def test_create():
    global resource_id
    resource_id = create()

def test_read():
    assert read(resource_id) is not None  # depends on test_create

def test_delete():
    delete(resource_id)  # depends on test_create

# GOOD — each test is independent
def test_create_and_read(make_resource):
    resource = make_resource()
    assert read(resource.id) is not None
```

### 7. Too many assertions in one test

```python
# BAD — one test tests everything, hard to diagnose failures
def test_everything(spark):
    df = process(spark)
    assert df.count() == 5
    assert df.columns == ["name", "age"]
    assert df.filter("age > 25").count() == 3
    assert df.agg({"age": "avg"}).collect()[0][0] == 28.5

# GOOD — focused tests
def test_process_returns_5_rows(spark):
    assert process(spark).count() == 5

def test_process_has_correct_schema(spark):
    assert process(spark).columns == ["name", "age"]

def test_process_filters_by_age(spark):
    assert process(spark).filter("age > 25").count() == 3
```

### 8. Ignoring test output

```python
# BAD — no assertion
def test_process(spark):
    result = process(spark)
    print(result)  # just looking at output

# GOOD — explicit assertion
def test_process(spark):
    result = process(spark)
    assert result.count() == 5
```

---

## Code Review Checklist for Tests

When reviewing test code, check:

- [ ] **Test name describes behavior** (`test_filter_returns_active_users` not `test_filter_1`)
- [ ] **One concept per test** (not testing 5 things in one function)
- [ ] **No test interdependencies** (each test can run alone)
- [ ] **Fixtures are appropriately scoped** (session for Spark, function for mocks)
- [ ] **Mocks are at boundaries** (not mocking internal implementation)
- [ ] **Assertions are specific** (not `assert result is not None` for everything)
- [ ] **Edge cases are covered** (empty input, None, boundary values)
- [ ] **Tests are fast** (unit tests < 100ms)
- [ ] **Tests are marked** (unit/integration/e2e/slow)
- [ ] **No copy-pasted setup** (use fixtures)
- [ ] **Parametrized where appropriate** (not 5 copy-pasted tests)
- [ ] **Cleanup is handled** (yield fixtures, tmp_path, pytester make_* fixtures)
- [ ] **Error messages are helpful** (assert messages for complex checks)
- [ ] **No hardcoded paths** (use tmp_path or fixtures)
- [ ] **No skipped tests without reason** (`pytest.mark.skip(reason="...")`)
