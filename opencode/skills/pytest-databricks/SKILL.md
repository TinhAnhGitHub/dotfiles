---
name: pytest-databricks
description: >-
  Comprehensive pytest testing skill for Python, PySpark, and Databricks. Covers the
  pytest philosophy (fixtures, parametrize, markers, conftest hierarchy, monkeypatch,
  tmp_path), unit vs integration test design, mocking strategies (unittest.mock, pytest-mock
  mocker, monkeypatch, sys.modules stubbing), PySpark DataFrame testing (assertDataFrameEqual,
  assertSchemaEqual, chispa), Databricks Connect testing (DatabricksSession, serverless,
  profile configuration), databricks-labs-pytester integration fixtures (ws, acc, spark,
  make_schema, make_table, make_catalog, make_volume, make_job, make_cluster, make_run_as,
  env_or_skip, and 70+ more), refactoring notebooks for testability, running pytest inside
  Databricks notebooks, CI/CD test automation, and coverage configuration. Use this skill
  whenever writing, reviewing, or debugging tests for Python or PySpark/Databricks code,
  setting up conftest.py, creating test fixtures, mocking Spark sessions or Databricks SDK
  clients, parametrizing tests, configuring pytest (pyproject.toml, markers, addopts),
  or planning a testing strategy (unit vs integration vs end-to-end). Also use when the user
  mentions pytest, conftest, fixture, mock, parametrize, test coverage, SparkSession in tests,
  dbutils mocking, Databricks Connect, pytester, chispa, assertDataFrameEqual, or any
  testing-related task for Databricks/PySpark projects.
---

# pytest + Databricks Testing Skill

## Why This Skill Exists

Testing PySpark/Databricks code is harder than testing ordinary Python. Spark is distributed,
`dbutils` only exists inside the Databricks runtime, `SparkSession` is a global singleton,
and notebooks resist modular testing. Many teams skip unit tests entirely — and bugs in
data transformations slip into production, causing pipeline failures and data quality issues.

This skill gives you a complete, opinionated testing philosophy that works across three tiers:

1. **Unit tests** — fast, no Spark, no cluster, mocked dependencies (milliseconds)
2. **Integration tests** — real Spark via Databricks Connect or local Spark (seconds)
3. **End-to-end tests** — real Databricks workspace resources via pytester fixtures (minutes)

Each tier has a different cost/speed/fidelity tradeoff. Knowing which tier to use for each
test is the single most important testing decision you'll make.

---

## Table of Contents

- [The pytest Philosophy](#the-pytest-philosophy)
- [Test Layout and Discovery](#test-layout-and-discovery)
- [Fixtures: The Heart of pytest](#fixtures-the-heart-of-pytest)
- [Parametrization](#parametrization)
- [Markers and Test Selection](#markers-and-test-selection)
- [Mocking Strategies](#mocking-strategies)
- [Temporary Directories](#temporary-directories)
- [conftest.py Hierarchy](#conftestpy-hierarchy)
- [Output Capture and Logging](#output-capture-and-logging)
- [pytest Cache and Re-running Failures](#pytest-cache-and-re-running-failures)
- [Warnings Management](#warnings-management)
- [Doctest Support](#doctest-support)
- [PySpark DataFrame Testing](#pyspark-dataframe-testing)
- [Databricks Connect Testing](#databricks-connect-testing)
- [databricks-labs-pytester Integration Fixtures](#databricks-labs-pytester-integration-fixtures)
- [Refactoring Notebooks for Testability](#refactoring-notebooks-for-testability)
- [Running pytest Inside Databricks Notebooks](#running-pytest-inside-databricks-notebooks)
- [pytest Configuration](#pytest-configuration)
- [Key pytest Plugins](#key-pytest-plugins)
- [Testing Strategy Decision Guide](#testing-strategy-decision-guide)
- [Best Practices Summary](#best-practices-summary)
- [Common pytest Commands](#common-pytest-commands)

For deep-dive reference material, see:
- `references/pytest-core.md` — Complete pytest fixture, parametrize, mocking, hooks, cache, warnings, and CLI reference
- `references/pytest-best-practices.md` — Comprehensive best practices: test organization, isolation, naming, speed, CI/CD, coverage, anti-patterns, and code review checklist
- `references/databricks-pytester.md` — Full 83+ fixture catalog from databricks-labs-pytester (v0.7.4)
- `references/databricks-connect-testing.md` — Databricks Connect setup, serverless, profiles, troubleshooting
- `references/pyspark-testing.md` — DataFrame equality, chispa, mocking Spark, refactoring patterns

---

## The pytest Philosophy

pytest's design rests on a few principles that make it different from `unittest` and other
frameworks. Understanding these principles helps you write tests that are maintainable,
composable, and fast.

### 1. Plain `assert` Statements

pytest uses Python's built-in `assert` keyword. No `self.assertEqual()`, `self.assertTrue()`,
or other boilerplate. pytest's assertion introspection rewrites `assert` statements at import
time to show exactly which values differed on failure:

```python
def test_simple():
    result = my_function(3)
    assert result == 5
    # If this fails, pytest shows:
    # E   assert 4 == 5
    # E    +  where 4 = my_function(3)
```

This means you write less code and get better error messages. Use plain `assert` everywhere.
For floating point comparisons, use `pytest.approx`:

```python
def test_float():
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

### 2. Auto-Discovery

pytest automatically discovers test files and functions by naming convention:
- **Files**: `test_*.py` or `*_test.py`
- **Classes**: `Test*` (no `__init__` method)
- **Functions**: `test_*`

This means you don't need to register tests anywhere — just name them correctly and pytest
finds them. This convention-over-configuration approach reduces friction.

### 3. Fixtures Over setUp/tearDown

pytest fixtures replace the xUnit `setUp`/`tearDown` pattern with something far more powerful:
explicit, modular, composable dependency injection. Instead of a monolithic setup method that
runs for every test, you define named fixtures that tests request by parameter name. This
means a test only pays the setup cost for the fixtures it actually uses.

### 4. Function-Based, Not Class-Based

pytest works with plain functions. You don't need to inherit from `TestCase`. Classes are
used only for grouping — they must not have `__init__`. This keeps tests simple and
encourages composition over inheritance.

### 5. Plugin Architecture

pytest has a rich plugin system with 1300+ plugins. Plugins can add fixtures, markers,
command-line options, and hooks. This extensibility means pytest grows with your needs.

---

## Test Layout and Discovery

### Recommended Layout

For Databricks projects, use the **tests outside the source package** layout:

```
my_project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── pipeline.py
├── tests/
│   ├── conftest.py          # Shared fixtures for all tests
│   ├── unit/                # Fast, no external dependencies
│   │   ├── conftest.py      # Unit-test-specific fixtures
│   │   └── test_pipeline.py
│   ├── integration/         # Need Spark or Databricks Connect
│   │   ├── conftest.py      # Spark session fixture
│   │   └── test_pipeline_integration.py
│   └── e2e/                 # Real Databricks workspace resources
│       ├── conftest.py      # pytester fixtures
│       └── test_pipeline_e2e.py
├── pyproject.toml
└── pytest.ini (or config in pyproject.toml)
```

### Why This Layout

- **`tests/` outside `src/`**: Prevents tests from being installed with your package.
  Tests are development-time artifacts, not runtime dependencies.
- **`unit/`, `integration/`, `e2e/` separation**: Makes it easy to run only fast tests
  in CI (`pytest tests/unit/`) and slower tests separately.
- **`conftest.py` at each level**: Fixtures defined in a `conftest.py` are available to
  all tests in that directory and below. This lets you scope fixtures appropriately.

### Discovery Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

---

## Fixtures: The Heart of pytest

Fixtures are pytest's dependency injection system. They provide defined, reliable, and
consistent contexts for tests. Understanding fixtures deeply is the key to writing
maintainable test suites.

### Basic Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    """Provide a small dataset for testing."""
    return [("Alice", 30), ("Bob", 25)]
```

### Fixture Scopes

Scope controls how often a fixture is created. Choosing the right scope is a performance
decision:

| Scope | Created | Use When |
|-------|---------|----------|
| `function` (default) | Once per test function | Default — safest, most isolated |
| `class` | Once per test class | Multiple methods share expensive setup |
| `module` | Once per `.py` file | Multiple tests in a file share expensive setup |
| `package` | Once per `__init__.py` directory | Rarely used |
| `session` | Once per pytest run | Very expensive resources (Spark session, DB connection) |

```python
@pytest.fixture(scope="session")
def spark_session():
    """Session-scoped Spark — created once, shared across all tests."""
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.master("local[*]").appName("tests").getOrCreate()
    yield spark
    spark.stop()
```

### Yield Fixtures (Setup + Teardown)

Use `yield` instead of `return` when you need cleanup:

```python
@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file, clean up after test."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text("key: value")
    yield config_path
    config_path.unlink()  # teardown
```

The code before `yield` is the setup; the code after is teardown. Teardown runs even if
the test fails. This is safer than try/finally because pytest handles exceptions in
dependent fixtures gracefully.

### Fixture Composition

Fixtures can use other fixtures — this is where pytest's fixture system truly shines:

```python
@pytest.fixture
def catalog_name():
    return "test_catalog"

@pytest.fixture
def schema_name():
    return "test_schema"

@pytest.fixture
def table_name(catalog_name, schema_name):
    return f"{catalog_name}.{schema_name}.documents"

@pytest.fixture
def spark_table(spark_session, table_name):
    """Create a test table, clean up after."""
    spark_session.sql(f"CREATE TABLE {table_name} (id INT, name STRING)")
    yield spark_session.table(table_name)
    spark_session.sql(f"DROP TABLE IF EXISTS {table_name}")
```

### `autouse` Fixtures

`autouse=True` makes a fixture run automatically for every test in scope, without being
requested as a parameter:

```python
@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Automatically set env vars for every test in this module."""
    monkeypatch.setenv("DATABRICKS_HOST", "test.databricks.net")
    monkeypatch.setenv("DATABRICKS_TOKEN", "test-token")
```

Use `autouse` sparingly — it makes tests less explicit about their dependencies. Good use
cases: mocking `sys.modules` for Databricks-only imports, setting up logging, resetting
global state.

### Parametrized Fixtures

```python
@pytest.fixture(params=["csv", "json", "parquet"])
def file_format(request):
    return request.param

def test_read_file(file_format, tmp_path):
    # Runs 3 times: once for each format
    ...
```

For the full fixture reference (fixture errors, dependency resolution order, context
manager fixtures, `request` object, `pytest_generate_tests`), see
`references/pytest-core.md`.

---

## Parametrization

### `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", 5),
    ("world", 5),
    ("", 0),
    ("a" * 100, 100),
])
def test_string_length(input, expected):
    assert len(input) == expected
```

### Stacking Decorators (Cartesian Product)

```python
@pytest.mark.parametrize("format", ["csv", "json"])
@pytest.mark.parametrize("compression", ["none", "gzip"])
def test_write(format, compression):
    # Runs 4 times: csv/none, csv/gzip, json/none, json/gzip
    ...
```

### `pytest.param` for Per-Case Marks

```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    pytest.param("edge_case", None, marks=pytest.mark.xfail),
    pytest.param("not_implemented", None, marks=pytest.mark.skip(reason="TODO")),
])
def test_parse(input, expected):
    ...
```

### Indirect Parametrization

```python
@pytest.fixture
def db_connection(request):
    db_type = request.param
    if db_type == "sqlite":
        return create_sqlite()
    elif db_type == "postgres":
        return create_postgres()

@pytest.mark.parametrize("db_connection", ["sqlite", "postgres"], indirect=True)
def test_query(db_connection):
    ...
```

---

## Markers and Test Selection

### Custom Markers

Register markers in `pyproject.toml` to avoid warnings:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: fast unit tests with no external dependencies",
    "integration: tests requiring Spark or Databricks Connect",
    "e2e: end-to-end tests against a real Databricks workspace",
    "slow: tests that take more than 10 seconds",
    "spark: tests that require a Spark session",
]
```

### Using Markers

```python
@pytest.mark.integration
class TestPipelineIntegration:
    """All methods in this class are marked as integration tests."""
    
    def test_full_pipeline(self, spark_session):
        ...

@pytest.mark.unit
def test_transform_logic():
    ...

@pytest.mark.slow
@pytest.mark.spark
def test_large_dataset(spark_session):
    ...
```

### Selecting Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run everything except slow tests
pytest -m "not slow"

# Run integration and e2e tests
pytest -m "integration or e2e"

# Run spark tests that aren't slow
pytest -m "spark and not slow"
```

### `pytest.ini` / `pyproject.toml` addopts

```toml
[tool.pytest.ini_options]
addopts = [
    "-ra",                    # Show summary for all except passed
    "--strict-markers",       # Error on unregistered markers
    "--strict-config",        # Error on bad config
    "--durations=10",         # Show 10 slowest tests
]
```

---

## Mocking Strategies

Mocking is critical for Databricks testing because `dbutils`, `SparkSession`, and the
Databricks SDK are only available in specific environments. There are several mocking
approaches, each with different tradeoffs.

### Strategy 1: `unittest.mock.patch` (Targeted Replacement)

Best for replacing specific functions or classes during a test:

```python
from unittest.mock import patch, MagicMock

def test_invoke_with_mock_llm():
    with patch("my_module.ChatDatabricks") as mock_chat:
        mock_chat.return_value.invoke.return_value = AIMessage(content="mocked")
        
        result = my_function()
        
        mock_chat.assert_called_once()
        assert result == "mocked"
```

### Strategy 2: `pytest-mock` `mocker` Fixture (Cleaner Syntax)

The `mocker` fixture from `pytest-mock` provides the same functionality with cleaner
assertions and automatic cleanup:

```python
def test_with_mocker(mocker):
    mock_chat = mocker.patch("my_module.ChatDatabricks")
    mock_chat.return_value.invoke.return_value = AIMessage(content="mocked")
    
    result = my_function()
    
    mock_chat.assert_called_once()
    mocker.stopall()  # Optional — cleanup is automatic
```

### Strategy 3: `monkeypatch` (Environment and Attribute Patching)

`monkeypatch` is a built-in pytest fixture for safely patching attributes, environment
variables, and dictionary items. All patches are automatically reverted after the test:

```python
def test_with_env(monkeypatch):
    monkeypatch.setenv("DATABRICKS_HOST", "test.databricks.net")
    monkeypatch.setattr("my_module.timeout_seconds", 5)
    monkeypatch.delenv("OPTIONAL_VAR", raising=False)
    
    # Test code here
    # All patches automatically undone after test
```

### Strategy 4: `sys.modules` Stubbing (Databricks-Only Imports)

This is the most important pattern for Databricks unit testing. Many Databricks libraries
(`databricks.sdk.runtime`, `pyspark.pipelines`, `delta.tables`) cannot be imported outside
the Databricks runtime. Stub them in `conftest.py` so test collection doesn't crash:

```python
# conftest.py
import sys
from unittest.mock import MagicMock

# Stub pyspark if not installed (e.g., in lightweight CI)
if "pyspark" not in sys.modules:
    pyspark = MagicMock()
    sys.modules["pyspark"] = pyspark
    sys.modules["pyspark.sql"] = pyspark.sql
    sys.modules["pyspark.sql.functions"] = pyspark.sql.functions
    sys.modules["pyspark.sql.types"] = pyspark.sql.types

# Stub Databricks-only modules
for _mod in (
    "databricks.sdk.runtime",
    "databricks.sdk",
    "databricks",
    "delta",
    "delta.tables",
):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()
```

This pattern is used in this codebase's `tests/noti/layout_matching/conftest.py` and
`projects/ecf_heatmap/tests/conftest.py`. It allows test collection to succeed even when
Databricks-only packages aren't installed.

### Strategy 5: Mocking `dbutils`

`dbutils` is only available inside Databricks notebooks. Mock it for local testing:

```python
from unittest.mock import MagicMock

def test_dbutils_interaction():
    mock_dbutils = MagicMock()
    mock_dbutils.fs.mkdirs.return_value = None
    
    # Simulate function call
    mock_dbutils.fs.mkdirs("/path/to/dir")
    
    mock_dbutils.fs.mkdirs.assert_called_once_with("/path/to/dir")
```

For a more reusable approach, create a `dbutils` fixture in `conftest.py`:

```python
@pytest.fixture
def mock_dbutils():
    """Provide a mock dbutils for tests that need it."""
    dbutils = MagicMock()
    dbutils.fs.mkdirs.return_value = None
    dbutils.fs.cp.return_value = None
    dbutils.fs.rm.return_value = True
    dbutils.widgets.get.return_value = "default_value"
    return dbutils
```

### Strategy 6: Mocking Databricks SDK `WorkspaceClient`

For unit testing code that uses the Databricks SDK:

```python
from unittest.mock import MagicMock

def test_create_catalog(ws_mock):
    ws_mock = MagicMock()
    ws_mock.catalogs.create.return_value = MagicMock(name="test_catalog")
    
    result = create_catalog(ws_mock, "test_catalog")
    
    ws_mock.catalogs.create.assert_called_once()
```

For integration testing, use the real `ws` fixture from `databricks-labs-pytester`.

### When to Mock vs When to Use Real Spark

| Situation | Strategy |
|-----------|----------|
| Testing pure Python logic (no Spark) | No mock needed — just call the function |
| Testing transformation logic that takes/returns DataFrames | Use local Spark session fixture |
| Testing code that calls `dbutils` | Mock `dbutils` |
| Testing code that calls Databricks SDK | Mock `WorkspaceClient` for unit, real `ws` for integration |
| Testing DLT pipelines (`pyspark.pipelines`) | Stub `sys.modules["pyspark.pipelines"]` |
| Testing SQL execution | Mock `sql_backend` for unit, real warehouse for integration |

---

## Temporary Directories

### `tmp_path` (Per-Test)

```python
def test_write_file(tmp_path):
    file_path = tmp_path / "data.csv"
    file_path.write_text("col1,col2\n1,2\n")
    
    result = read_csv(str(file_path))
    assert len(result) == 1
```

### `tmp_path_factory` (Session-Scoped)

```python
@pytest.fixture(scope="session")
def shared_test_data(tmp_path_factory):
    """Create a large dataset once, share across all tests."""
    data_dir = tmp_path_factory.mktemp("data")
    # ... create test data files ...
    return data_dir
```

---

## conftest.py Hierarchy

`conftest.py` files form a hierarchy. Fixtures defined in a `conftest.py` are available to
all tests in that directory and all subdirectories:

```
project/
├── conftest.py              # Available to ALL tests
├── tests/
│   ├── conftest.py          # Available to all tests under tests/
│   ├── unit/
│   │   ├── conftest.py      # Available to unit/ tests only
│   │   └── test_a.py
│   └── integration/
│       ├── conftest.py      # Available to integration/ tests only
│       └── test_b.py
```

### Key conftest.py Patterns for Databricks

**Root `conftest.py`** — global stubs and markers:

```python
import sys
from unittest.mock import MagicMock

# Stub Databricks-only modules for test collection
for _mod in ("databricks.sdk.runtime", "databricks.sdk", "databricks", "delta", "delta.tables"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on directory."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
```

**Integration `conftest.py`** — Spark session:

```python
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("integration-tests") \
        .getOrCreate()
    yield spark
    spark.stop()
```

---

## Output Capture and Logging

pytest captures stdout/stderr by default. Use these fixtures to access or test captured output.

### `capsys` — Capture stdout/stderr (text)

```python
def test_output(capsys):
    print("processing started")
    captured = capsys.readouterr()
    assert "processing" in captured.out
    assert captured.err == ""
```

### `capfd` — Capture at file descriptor level (works with subprocesses)

```python
def test_subprocess(capfd):
    import subprocess
    subprocess.run(["echo", "hello"], check=True)
    captured = capfd.readouterr()
    assert "hello" in captured.out
```

### `caplog` — Capture log messages

```python
import logging

def test_logging(caplog):
    with caplog.at_level(logging.DEBUG):
        logging.getLogger("my_app").warning("low memory")
    assert "low memory" in caplog.text
    assert caplog.records[0].levelname == "WARNING"
```

### Disabling capture

```bash
pytest -s              # show all output (disable capture)
pytest --capture=fd    # file descriptor capture (default)
```

For the full capture reference (capsysbinary, log configuration, propagation), see
`references/pytest-core.md`.

---

## pytest Cache and Re-running Failures

pytest caches test results between runs in `.pytest_cache/`. This is invaluable during
development — re-run only what failed.

```bash
# Run only tests that failed last time
pytest --lf

# Run failed tests first, then the rest
pytest --ff

# If no failures last time, run nothing (vs. all by default)
pytest --lf --lfnf=none

# Show cache contents
pytest --cache-show

# Clear cache
pytest --cache-clear
```

**During development workflow:**
1. Run full suite: `pytest`
2. Fix failures
3. Re-run only failures: `pytest --lf`
4. Once all pass, run full suite again to confirm

**In CI**: Use `pytest --lf` for faster PR feedback when a previous run failed.

---

## Warnings Management

pytest captures warnings and shows a summary. Control how warnings are handled:

### Global configuration

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "error",                           # treat all warnings as errors
    "ignore::DeprecationWarning",      # ignore deprecation warnings
    "always::ResourceWarning",         # always show resource warnings
]
```

### Per-test warnings

```python
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_with_deprecated_api():
    ...

@pytest.mark.filterwarnings("error")
def test_strict_no_warnings():
    ...
```

### Command-line

```bash
pytest -W ignore::DeprecationWarning    # ignore specific warning
pytest -W error                         # treat all warnings as errors
pytest --disable-warnings               # hide warning summary
```

For the full warnings reference (filter syntax, action types), see `references/pytest-core.md`.

---

## Doctest Support

pytest can run doctests embedded in your source code docstrings and markdown files.

```bash
# Run doctests in all Python modules
pytest --doctest-modules src/

# Run doctests in markdown files
pytest --doctest-glob="*.md"
```

### Configuration

```toml
[tool.pytest.ini_options]
addopts = ["--doctest-modules"]
doctest_optionflags = ["NORMALIZE_WHITESPACE", "ELLIPSIS"]
```

### Example

```python
# my_module.py
def add(a, b):
    """Add two numbers.

    >>> add(1, 2)
    3
    >>> add(-1, 1)
    0
    """
    return a + b
```

Doctests are great for:
- Documenting API usage with verified examples
- Keeping documentation in sync with code
- Simple unit tests that double as documentation

---

## PySpark DataFrame Testing

### `assertDataFrameEqual` (Spark 3.5+ / DBR 14.2+)

```python
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual

def test_transformation(spark):
    input_df = spark.createDataFrame([("Alice", 30)], ["name", "age"])
    expected = spark.createDataFrame([("Alice", 30)], ["name", "age"])
    
    result = transform(input_df)
    
    assertSchemaEqual(result.schema, expected.schema)
    assertDataFrameEqual(result, expected)
```

### Manual DataFrame Comparison

For older Spark versions or more control:

```python
def assert_df_equal(actual, expected, check_order=False):
    """Compare two DataFrames for equality."""
    if not check_order:
        actual = actual.orderBy(actual.columns)
        expected = expected.orderBy(expected.columns)
    
    assert actual.schema == expected.schema, f"Schema mismatch:\n{actual.schema}\nvs\n{expected.schema}"
    assert actual.collect() == expected.collect(), "Data mismatch"
```

### Chispa (Third-Party Library)

[Chispa](https://github.com/chispa-dev/chispa) provides richer DataFrame comparison with
better error messages:

```python
from chispa.dataframe_compression import assert_column_equality, assert_df_equality

def test_with_chispa(spark):
    df1 = spark.createDataFrame([("Alice", 30)], ["name", "age"])
    df2 = spark.createDataFrame([("Alice", 30)], ["name", "age"])
    
    assert_df_equality(df1, df2)  # Checks schema and data
    
    # For approximate equality (useful for floating point)
    assert_df_equality(df1, df2, ignore_row_order=True)
```

For the full PySpark testing reference, see `references/pyspark-testing.md`.

---

## Databricks Connect Testing

Databricks Connect lets you run Spark code locally that executes on a remote Databricks
cluster or serverless compute. This is the bridge between unit tests (no Spark) and
end-to-end tests (real workspace resources).

### Setup

```bash
pip install databricks-connect
```

**Critical**: Databricks Connect and PySpark are mutually exclusive. Use separate virtual
environments if you need both.

### Profile Configuration

The user's Databricks profile is `TA`. Configure it:

```bash
# Generate a token for the TA profile
databricks auth token --profile TA

# Or set environment variables
export DATABRICKS_HOST=<your-workspace-url>
export DATABRICKS_TOKEN=<your-token>
```

### Getting a SparkSession with Databricks Connect

```python
from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession

def get_spark() -> SparkSession:
    spark = DatabricksSession.builder.getOrCreate()
    return spark
```

### Using a Specific Profile

```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.profile("TA").getOrCreate()
```

Or via environment variable:

```bash
export DATABRICKS_CONFIG_PROFILE=TA
```

### Serverless Compute

```bash
export DATABRICKS_SERVERLESS_COMPUTE_ID=auto
```

When set to `auto`, Databricks Connect ignores `cluster_id` and uses serverless compute.

### Testing with Databricks Connect

```python
# nyctaxi_functions.py
from databricks.connect import DatabricksSession
from pyspark.sql import DataFrame, SparkSession

def get_spark() -> SparkSession:
    return DatabricksSession.builder.getOrCreate()

def get_nyctaxi_trips() -> DataFrame:
    spark = get_spark()
    return spark.read.table("samples.nyctaxi.trips")
```

```python
# test_nyctaxi_functions.py
import pyspark.sql.connect.session
from nyctaxi_functions import get_spark, get_nyctaxi_trips

def test_get_spark():
    spark = get_spark()
    assert isinstance(spark, pyspark.sql.connect.session.SparkSession)

def test_get_nyctaxi_trips():
    df = get_nyctaxi_trips()
    assert df.count() > 0
```

**Important**: When running from the terminal, pytest only works with the DEFAULT
configuration profile. Use `DATABRICKS_CONFIG_PROFILE=TA` to override, or use the
`.profile("TA")` builder method.

For the full Databricks Connect reference, see `references/databricks-connect-testing.md`.

---

## databricks-labs-pytester Integration Fixtures

`databricks-labs-pytester` is a pytest plugin providing 70+ fixtures for integration testing
against real Databricks workspaces. Every fixture auto-cleans up resources after the test.

### Installation

```toml
# pyproject.toml
[dependency-groups]
test = [
    "databricks-labs-pytester~=0.7",
    "pytest-cov~=7.0.0",
    "pytest-mock~=3.15.1",
    "pytest-timeout~=2.4.0",
    "pytest-xdist~=3.8.0",
]
```

### Key Fixtures Quick Reference

| Fixture | What It Provides | Scope | Required Env |
|---------|-----------------|-------|--------------|
| `spark` | Databricks Connect SparkSession | function | `DATABRICKS_CLUSTER_ID` or `DATABRICKS_SERVERLESS_COMPUTE_ID=auto` |
| `ws` | Databricks `WorkspaceClient` | session | `DATABRICKS_HOST` + auth |
| `acc` | Databricks `AccountClient` | session | `DATABRICKS_ACCOUNT_ID` |
| `sql_backend` | SQL execution backend | function | `DATABRICKS_WAREHOUSE_ID` |
| `sql_exec` | Execute SQL (no results) | function | via `sql_backend` |
| `sql_fetch_all` | Fetch all SQL rows | function | via `sql_backend` |
| `env_or_skip` | Get env var or skip test | function | — |
| `make_random` | Random string generator | function | — |
| `make_schema` | Create+cleanup a schema | function | via `sql_backend` |
| `make_table` | Create+cleanup a table | function | via `sql_backend` |
| `make_catalog` | Create+cleanup a catalog | function | via `ws` |
| `make_volume` | Create+cleanup a volume | function | via `ws` |
| `make_udf` | Create+cleanup a UDF | function | via `sql_backend` |
| `make_cluster` | Create+cleanup a cluster | function | via `ws` |
| `make_job` | Create+cleanup a job | function | via `ws` |
| `make_pipeline` | Create+cleanup a DLT pipeline | function | via `ws` |
| `make_warehouse` | Create+cleanup a SQL warehouse | function | via `ws` |
| `make_notebook` | Create+cleanup a notebook | function | via `ws` |
| `make_user` | Create+cleanup a workspace user | function | via `ws` |
| `make_group` | Create+cleanup a workspace group | function | via `ws` |
| `make_run_as` | Ephemeral service principal | function | via `acc` |
| `make_secret_scope` | Create+cleanup a secret scope | function | via `ws` |
| `make_model` | Create+cleanup a registered model | function | via `ws` |
| `make_experiment` | Create+cleanup an MLflow experiment | function | via `ws` |
| `make_serving_endpoint` | Create+cleanup a serving endpoint | function | via `ws` |

### Usage Examples

```python
# Test with a real Spark session via Databricks Connect
def test_spark_query(spark):
    rows = spark.sql("SELECT 1").collect()
    assert rows[0][0] == 1

# Test with a real workspace client
def test_list_clusters(ws):
    clusters = ws.clusters.list_clusters()
    assert len(clusters) >= 0

# Test with ephemeral catalog/schema/table (auto-cleaned)
def test_table_operations(make_catalog, make_schema, make_table):
    catalog = make_catalog()
    schema = make_schema(catalog_name=catalog.name)
    table = make_table(catalog_name=catalog.name, schema_name=schema.name)
    
    # Table exists during test, auto-deleted after

# Test as a lower-privilege user
def test_run_as_lower_privilege(make_run_as):
    run_as = make_run_as(account_groups=['account.group.name'])
    result = run_as.sql_fetch_all("SELECT CURRENT_USER() AS my_name")
    assert result is not None

# Skip test if env var not set
def test_external_service(env_or_skip):
    token = env_or_skip("SOME_EXTERNAL_SERVICE_TOKEN")
    assert token is not None
```

### Debug Environment Setup

For local debugging, create `~/.databricks/debug-env.json`:

```json
{
   "ws": {
     "DATABRICKS_HOST": "....azuredatabricks.net",
     "DATABRICKS_CLUSTER_ID": "0708-200540-...",
     "DATABRICKS_WAREHOUSE_ID": "33aef..."
   }
}
```

Then in `conftest.py`:

```python
@pytest.fixture
def debug_env_name():
    return "ws"
```

### Logging with Clickable Workspace Links

```python
# conftest.py
import logging
from databricks.labs.blueprint.logger import install_logger

install_logger()
logging.getLogger('databricks.labs.pytester').setLevel(logging.DEBUG)
```

For the complete 70+ fixture catalog, see `references/databricks-pytester.md`.

---

## Refactoring Notebooks for Testability

Databricks notebooks are hard to test because they mix code execution with runtime-specific
utilities. Here's how to make them testable:

### 1. Extract Transformation Logic

Move data processing into standalone Python functions:

```python
# databricks_notebook.py
from pyspark.sql import functions as F
from pyspark.sql import DataFrame

def process_data(df: DataFrame) -> DataFrame:
    """Pure transformation — no I/O, no dbutils."""
    return df.select("name", "birthDate").filter(F.col("dob") >= F.lit("2000-01-01"))

if __name__ == "__main__":
    # Main notebook logic — only runs in notebook context
    uc_volume_path = "volume://my_catalog.my_schema.my_volume/my_data"
    dbutils.fs.mkdirs(uc_volume_path)
    df = spark.read.table("my_table")
    result = process_data(df)
    result.write.mode("overwrite").saveAsTable("processed_table")
```

### 2. Minimize Direct `dbutils` Dependencies

Use dependency injection — pass `dbutils` as a parameter instead of using it globally:

```python
# Bad — hard to test
def get_config():
    return dbutils.widgets.get("config_path")

# Good — testable
def get_config(dbutils=None):
    if dbutils is None:
        from databricks.sdk.runtime import dbutils as real_dbutils
        dbutils = real_dbutils
    return dbutils.widgets.get("config_path")
```

### 3. Wrap Main Execution

```python
def main(spark, dbutils):
    """Entry point — accepts dependencies for testing."""
    config = get_config(dbutils)
    df = spark.read.table("source")
    result = process_data(df)
    result.write.mode("overwrite").saveAsTable("target")

if __name__ == "__main__":
    main(spark, dbutils)
```

---

## Running pytest Inside Databricks Notebooks

You can run pytest directly inside a Databricks notebook for quick validation:

```python
# Cell 1: Install pytest
%pip install pytest

# Cell 2: Run tests
import pytest

retcode = pytest.main([".", "-v", "-p", "no:cacheprovider"])
assert retcode == 0, "Some tests failed!"
```

This is useful for:
- Quick validation during development
- Running tests in the same environment as your production code
- CI/CD pipelines that use Databricks jobs for testing

---

## pytest Configuration

### `pyproject.toml` Configuration

```toml
[tool.pytest.ini_options]
# Test discovery
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Default options
addopts = [
    "-ra",                    # Show summary for all except passed
    "--strict-markers",       # Error on unregistered markers
    "--strict-config",        # Error on bad config
    "--durations=10",         # Show 10 slowest tests
    "--cov=src",              # Coverage for source
    "--cov-report=term-missing",
    "--cov-report=html:reports/coverage.html",
    "--html=reports/report.html",
    "--self-contained-html",
]

# Custom markers
markers = [
    "unit: fast unit tests with no external dependencies",
    "integration: tests requiring Spark or Databricks Connect",
    "e2e: end-to-end tests against a real Databricks workspace",
    "slow: tests that take more than 10 seconds",
    "spark: tests that require a Spark session",
]

# asyncio support (if using async code)
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

# Timeout for preventing hanging integration tests
# (or use pytest-timeout plugin: --timeout=300)
```

### Coverage Configuration

```toml
[tool.coverage.run]
omit = [
    "tests/*",
    "*/__init__.py",
    "*/conftest.py",
]
source = ["src", "components"]
```

---

## Key pytest Plugins

| Plugin | Purpose | Install |
|--------|---------|---------|
| `pytest-mock` | `mocker` fixture — cleaner mocking | `pip install pytest-mock` |
| `pytest-asyncio` | Async test support | `pip install pytest-asyncio` |
| `pytest-cov` | Coverage reporting | `pip install pytest-cov` |
| `pytest-xdist` | Parallel test execution | `pip install pytest-xdist` |
| `pytest-html` | HTML test reports | `pip install pytest-html` |
| `pytest-timeout` | Test timeouts | `pip install pytest-timeout` |
| `databricks-labs-pytester` | Databricks integration fixtures | `pip install databricks-labs-pytester` |
| `chispa` | PySpark DataFrame testing | `pip install chispa` |

### Parallel Testing with pytest-xdist

```bash
# Run tests in parallel using all CPU cores
pytest -n auto

# Use file-based distribution (better for tests with varying durations)
pytest -n auto --dist loadfile
```

### Timeouts with pytest-timeout

```bash
# Fail tests that take longer than 300 seconds
pytest --timeout=300

# Or in pyproject.toml
# [tool.pytest.ini_options]
# timeout = 300
```

---

## Testing Strategy Decision Guide

Use this guide to decide which testing tier to use:

```
Does the function use Spark (DataFrame, SparkSession)?
├── NO → Unit test (no Spark needed)
│   ├── Uses dbutils? → Mock dbutils
│   ├── Uses Databricks SDK? → Mock WorkspaceClient
│   └── Pure Python? → Just test directly
│
├── YES, but only transformations (takes DataFrame, returns DataFrame)
│   → Unit test with local Spark session fixture
│   → Use assertDataFrameEqual or chispa for assertions
│
├── YES, and reads/writes to Delta tables or UC volumes
│   → Integration test with Databricks Connect
│   → Use DATABRICKS_CONFIG_PROFILE=TA or .profile("TA")
│
└── YES, and creates/manages workspace resources (jobs, clusters, catalogs)
    → E2E test with databricks-labs-pytester fixtures
    → Use make_schema, make_table, make_catalog for ephemeral resources
    → Use env_or_skip for required environment variables
```

### Speed Expectations

| Tier | Typical Duration | When to Run |
|------|-----------------|-------------|
| Unit | < 100ms per test | Every commit, pre-commit hook |
| Integration (local Spark) | 1-10s per test | PR checks, local development |
| Integration (Databricks Connect) | 5-30s per test | PR checks, nightly CI |
| E2E (pytester) | 10-60s per test | Nightly CI, manual runs |

---

## Best Practices Summary

These are the most impactful practices for maintainable test suites. For the full
best-practices reference with detailed examples, see `references/pytest-best-practices.md`.

### Test Organization
- Keep `tests/` outside `src/` — tests are dev-time artifacts, not runtime dependencies
- Separate by tier: `unit/`, `integration/`, `e2e/` — run fast tests on every commit
- One `conftest.py` per tier with tier-appropriate fixtures

### Test Design
- Name tests by behavior: `test_filter_returns_active_users` not `test_filter_1`
- One concept per test — if a test is hard to name, it's testing too much
- Arrange-Act-Assert pattern — keep sections visually separated
- Tests must be independent — no shared mutable state, no order dependencies

### Fixtures
- Choose the right scope: `function` for mocks/test data, `session` for Spark/connections
- Use `yield` for cleanup — teardown runs even if the test fails
- Make fixtures composable — one fixture can depend on another
- Use factory fixtures for flexible test data creation
- Don't over-use `autouse` — it hides dependencies

### Mocking
- Mock at boundaries (external services), not internal implementation
- Prefer dependency injection over mocking — pass dependencies as parameters
- Use `spec=` on mocks to catch wrong attribute access
- Verify important calls, not every call — over-specifying makes tests brittle

### Assertions
- Use plain `assert` — pytest's introspection gives great error messages
- Add messages for complex assertions: `assert x == 5, f"got {x}"`
- Use `pytest.approx` for floats, `pytest.raises` for exceptions, `pytest.warns` for warnings
- Assert on data/behavior, not on implementation details

### Speed
- Keep unit tests under 100ms — mock external dependencies
- Share expensive resources with session-scoped fixtures
- Use `pytest -n auto` for parallel execution (tests must be isolated)
- Use `--durations=10` to find slow tests
- Use `pytest-timeout` to catch hanging tests

### CI/CD
- Run tests in stages: unit on every commit, integration on PRs, e2e nightly
- Use `--strict-markers` and `--strict-config` to catch config errors
- Use JUnit XML (`--junitxml`) for CI reporting
- Set coverage thresholds with `--cov-fail-under=80`

### Test Pyramid for Data Projects
- **Many unit tests** (mocked, < 100ms) — test pure transformation logic
- **Some integration tests** (real Spark, seconds) — test I/O and Databricks Connect
- **Few e2e tests** (real workspace, minutes) — test full pipelines with pytester fixtures

### Anti-Patterns to Avoid
- Testing implementation instead of behavior
- Over-mocking (mocking everything, testing nothing real)
- Brittle assertions (order-dependent, over-specified)
- Shared mutable state between tests
- Catch-all exception handling (`except Exception: pass`)
- Test interdependencies (tests that must run in order)
- Too many assertions in one test
- No assertion (just printing output)

For the complete best practices reference with code examples, anti-patterns, and a
code review checklist, see `references/pytest-best-practices.md`.

---

## Common pytest Commands

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Show local variables in tracebacks
pytest -l

# Run a specific test
pytest tests/unit/test_pipeline.py::TestPipeline::test_transform

# Run by marker
pytest -m unit
pytest -m "not slow"

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show slowest tests
pytest --durations=10

# Run in parallel
pytest -n auto

# With coverage
pytest --cov=src --cov-report=term-missing

# Only run tests that failed last time
pytest --lf

# Run tests matching a pattern
pytest -k "test_transform"

# Show available markers
pytest --markers

# Show available fixtures
pytest --fixtures

# Clear cache
pytest --cache-clear
```