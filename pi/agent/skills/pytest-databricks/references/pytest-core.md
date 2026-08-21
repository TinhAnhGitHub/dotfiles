# pytest Core Reference

> Complete reference for pytest fixtures, parametrization, mocking, configuration, and advanced features.
> Source: https://docs.pytest.org/en/stable/

## Table of Contents

- [Fixture Scopes and Instantiation Order](#fixture-scopes-and-instantiation-order)
- [Yield Fixtures (Setup/Teardown)](#yield-fixtures-setupteardown)
- [Fixture Composition and Dependency Resolution](#fixture-composition-and-dependency-resolution)
- [autouse Fixtures](#autouse-fixtures)
- [The `request` Object](#the-request-object)
- [Parametrized Fixtures](#parametrized-fixtures)
- [Indirect Parametrization](#indirect-parametrization)
- [pytest_generate_tests](#pytest_generate_tests)
- [monkeypatch (Complete API)](#monkeypatch-complete-api)
- [tmp_path and tmp_path_factory](#tmp_path-and-tmp_path_factory)
- [Output Capture: capsys, capfd, capsysbinary](#output-capture-capsys-capfd-capsysbinary)
- [Log Capture: caplog](#log-capture-caplog)
- [pytest Hooks](#pytest-hooks)
- [Markers](#markers)
- [Configuration](#configuration)
- [pytest Cache](#pytest-cache)
- [Warnings Management](#warnings-management)
- [Doctest Support](#doctest-support)
- [Good Practices](#good-practices)
- [CLI Flags Quick Reference](#cli-flags-quick-reference)

---

## Fixture Scopes and Instantiation Order

```python
@pytest.fixture(scope="function")  # default — new instance per test
@pytest.fixture(scope="class")     # one per test class
@pytest.fixture(scope="module")    # one per .py file
@pytest.fixture(scope="package")   # one per package directory
@pytest.fixture(scope="session")   # one per pytest run
```

**Scope rules:**
- Higher-scoped fixtures are instantiated **first** (session > package > module > class > function)
- A fixture can only depend on fixtures of the **same or wider** scope
  - A `function`-scoped fixture can use any scope
  - A `session`-scoped fixture can only use `session`-scoped dependencies
- If a fixture is used by multiple tests of different scopes, the **narrowest** scope wins
  - e.g., a `module`-scoped fixture used by a `function`-scoped test is created once per module

**When to use each:**
- `function`: Default. Safest — each test gets fresh state. Use when setup is cheap.
- `class`: Good for grouping related tests that share expensive setup in a class.
- `module`: Good for expensive setup shared by tests in one file (e.g., loading a config file).
- `package`: Rarely used. One instance per directory with `__init__.py`.
- `session`: Good for very expensive resources (Spark session, database connection, HTTP client pool).

**Overriding fixture scope dynamically:**

```python
@pytest.fixture(params=["function", "module"], scope="module")
def my_fixture(request):
    # The scope is fixed at "module" — params don't change scope
    return request.param
```

Scope is determined at definition time, not per-param. To change scope per-test, use separate fixtures or `pytest_generate_tests`.

---

## Yield Fixtures (Setup/Teardown)

```python
@pytest.fixture
def db_connection():
    # Setup
    conn = create_connection()
    yield conn  # Test runs here
    # Teardown — runs even if test fails
    conn.close()
```

Multiple yield fixtures compose safely — pytest handles the teardown order automatically
(reverse of setup order). If a fixture's setup raises an exception, pytest marks the test
as **error** (not failure), and dependent fixtures are not instantiated.

**Teardown with `addfinalizer` (alternative to yield):**

```python
@pytest.fixture
def db_connection(request):
    conn = create_connection()
    request.addfinalizer(conn.close)
    return conn
```

Use `yield` in almost all cases — it's cleaner. `addfinalizer` is useful when you need
conditional or multiple finalizers.

---

## Fixture Composition and Dependency Resolution

Fixtures can request other fixtures by name:

```python
@pytest.fixture
def database():
    return create_db()

@pytest.fixture
def user(database):
    return database.create_user()

@pytest.fixture
def user_posts(database, user):
    return database.get_posts(user.id)
```

pytest resolves the dependency graph and runs fixtures in the correct order. If an earlier
fixture fails, pytest stops and marks the test as having an error (not a failure).

**Fixture visibility:**
- Fixtures defined in a `conftest.py` are available to all tests in that directory and below
- Fixtures defined in a test module are only available in that module
- Fixtures defined in a class are only available to tests in that class
- Built-in fixtures (`tmp_path`, `monkeypatch`, `capsys`, `request`, etc.) are always available

**Dynamic fixture references with `request.getfixturevalue`:**

```python
@pytest.fixture
def my_fixture(request):
    # Dynamically request another fixture by name
    spark = request.getfixturevalue("spark_session")
    return spark.createDataFrame(...)
```

This is useful when the fixture name is determined at runtime (e.g., from parametrization).

---

## autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    """Runs automatically for every test in scope."""
    monkeypatch.setenv("ENV", "test")
```

`autouse` fixtures run without being requested. Use sparingly — they make test dependencies
implicit. Good use cases:
- Setting up logging
- Resetting global state between tests
- Stubbing `sys.modules` for Databricks-only imports
- Cleaning up temporary files

**autouse + scope:**
- `autouse=True, scope="function"`: runs before every test function (default)
- `autouse=True, scope="module"`: runs once per module, before any test in that module
- `autouse=True, scope="session"`: runs once per session

---

## The `request` Object

The `request` fixture gives access to test context:

```python
@pytest.fixture
def my_fixture(request):
    # Access the test function/node
    test_name = request.node.name
    test_module = request.module
    test_class = request.cls
    test_function = request.function
    test_file = request.fspath

    # Access parametrization values
    if hasattr(request, "param"):
        param_value = request.param

    # Access configuration
    config = request.config
    option_value = config.getoption("--my-option")

    # Add finalizer (alternative to yield)
    request.addfinalizer(cleanup_function)

    # Dynamically get another fixture
    other = request.getfixturevalue("other_fixture")

    return result
```

**`request.config.getoption`:**

```python
# In conftest.py
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev",
                     help="target environment: dev, staging, prod")

# In a fixture
@pytest.fixture
def target_env(request):
    return request.config.getoption("--env")
```

---

## Parametrized Fixtures

```python
@pytest.fixture(params=["csv", "json", "parquet"])
def file_format(request):
    return request.param

# Every test using file_format runs 3 times
def test_read(file_format):
    ...
```

With IDs for better test names:

```python
@pytest.fixture(params=[
    pytest.param("csv", id="csv-format"),
    pytest.param("json", id="json-format"),
    pytest.param("parquet", id="parquet-format"),
])
def file_format(request):
    return request.param
```

With marks per parameter:

```python
@pytest.fixture(params=[
    pytest.param("csv", id="csv", marks=pytest.mark.slow),
    pytest.param("json", id="json"),
])
def file_format(request):
    return request.param
```

---

## Indirect Parametrization

```python
@pytest.fixture
def db_connection(request):
    db_type = request.param  # receives the param value
    if db_type == "sqlite":
        return create_sqlite()
    return create_postgres()

@pytest.mark.parametrize("db_connection", ["sqlite", "postgres"], indirect=True)
def test_query(db_connection):
    ...
```

`indirect=True` means the param values are passed to the fixture via `request.param`
instead of being used directly as the test argument. This lets you parametrize the
**fixture setup** rather than the test logic.

**Partial indirect parametrization:**

```python
@pytest.mark.parametrize("db_connection,expected", [
    ("sqlite", 1),
    ("postgres", 1),
], indirect=["db_connection"])
def test_query(db_connection, expected):
    # db_connection comes from the fixture (indirect)
    # expected is passed directly to the test
    assert db_connection.count() == expected
```

---

## pytest_generate_tests

For dynamic parametrization based on command-line options, external data, or computed values:

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--stringinput", action="append", default=[],
                     help="list of string inputs")

def pytest_generate_tests(metafunc):
    if "stringinput" in metafunc.fixturenames:
        metafunc.parametrize("stringinput", metafunc.config.getoption("--stringinput"))
```

**Loading test data from a file:**

```python
def pytest_generate_tests(metafunc):
    if "dataset" in metafunc.fixturenames:
        # Load test cases from JSON
        import json
        with open("tests/test_cases.json") as f:
            cases = json.load(f)
        metafunc.parametrize("dataset", cases)
```

**Generating parametrized tests with custom IDs:**

```python
def pytest_generate_tests(metafunc):
    if "config" in metafunc.fixturenames:
        configs = load_configs()
        metafunc.parametrize(
            "config",
            configs,
            ids=[c["name"] for c in configs]  # custom test IDs
        )
```

---

## monkeypatch (Complete API)

The `monkeypatch` fixture safely modifies attributes, env vars, and dict items. All
changes are automatically reverted after the test — no manual cleanup needed.

```python
def test_with_monkeypatch(monkeypatch):
    # --- Environment Variables ---
    monkeypatch.setenv("DATABRICKS_HOST", "test.databricks.net")
    monkeypatch.delenv("OPTIONAL_VAR", raising=False)  # don't error if missing

    # --- Attributes ---
    monkeypatch.setattr("my_module.timeout", 5)
    monkeypatch.setattr(my_module, "timeout", 5)  # object form
    monkeypatch.delattr(my_class, "cached_value", raising=False)

    # --- Dictionary Items ---
    monkeypatch.setitem(globals(), "DEBUG", True)
    monkeypatch.setitem(os.environ, "CUSTOM_VAR", "value")
    monkeypatch.delitem(some_dict, "key", raising=False)

    # --- Chdir (change working directory) ---
    monkeypatch.chdir(tmp_path)

    # --- sys.path manipulation ---
    monkeypatch.syspath_prepend("/custom/path")

    # --- Undo all changes manually (optional) ---
    monkeypatch.undo()
```

**monkeypatch.setattr with a function (replacement):**

```python
def test_mock_function(monkeypatch):
    def mock_get_config():
        return {"key": "mocked_value"}

    monkeypatch.setattr("my_module.get_config", mock_get_config)

    # Or use a lambda
    monkeypatch.setattr("my_module.get_config", lambda: {"key": "mocked"})
```

**monkeypatch.setattr with raising:**

```python
# By default, setattr raises if the attribute doesn't exist
# Use raising=False to allow creating new attributes
monkeypatch.setattr(my_module, "new_attr", "value", raising=False)
```

**monkeypatch vs unittest.mock vs pytest-mock:**

| Feature | `monkeypatch` | `unittest.mock.patch` | `pytest-mock mocker` |
|---------|--------------|----------------------|---------------------|
| Built-in | Yes | Yes (stdlib) | No (plugin) |
| Auto-cleanup | Yes | No (use context manager) | Yes |
| Env vars | `setenv`/`delenv` | Manual | Manual |
| Dict items | `setitem`/`delitem` | Manual | Manual |
| Call assertions | No | Yes (`assert_called`) | Yes |
| Mock objects | No | Yes (`MagicMock`) | Yes |
| Return values | Replace function | `return_value`/`side_effect` | `return_value`/`side_effect` |
| Best for | Env vars, simple attrs | Complex mocking, call verification | Clean syntax + mock objects |

**When to use which:**
- `monkeypatch`: Env vars, simple attribute replacement, dict manipulation, `sys.path`
- `unittest.mock.patch`: When you need to verify calls, set return values, side effects
- `pytest-mock mocker`: Same as `unittest.mock` but with auto-cleanup and cleaner syntax

---

## tmp_path and tmp_path_factory

```python
# Per-test temporary directory (function scope, auto-cleaned)
def test_file_ops(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text("data")
    assert file.exists()

# Session-scoped temporary directory for sharing across tests
@pytest.fixture(scope="session")
def shared_data(tmp_path_factory):
    data_dir = tmp_path_factory.mktemp("data")
    return data_dir
```

**tmp_path_factory methods:**

```python
# Create a temp directory with a prefix
data_dir = tmp_path_factory.mktemp("data")

# Create a temp directory at a specific path
cache_dir = tmp_path_factory.mktemp("cache", numbered=False)

# Get the base temp directory
base = tmp_path_factory.getbasetemp()
```

**Retention configuration** (in `pyproject.toml`):

```toml
[tool.pytest.ini_options]
tmp_path_retention_policy = "all"  # "all" (default), "failed", "none"
tmp_path_retention_count = 3       # keep last 3 runs
```

- `"all"`: Keep all temp dirs (default)
- `"failed"`: Only keep temp dirs from failed tests
- `"none"`: Delete all temp dirs after run

---

## Output Capture: capsys, capfd, capsysbinary

pytest captures stdout/stderr by default. Use these fixtures to access captured output:

### `capsys` (text-level capture)

```python
def test_output(capsys):
    print("hello world")
    captured = capsys.readouterr()
    assert "hello" in captured.out
    assert captured.err == ""
```

### `capsysbinary` (binary-level capture)

```python
def test_binary_output(capsysbinary):
    sys.stdout.buffer.write(b"\x00\x01")
    captured = capsysbinary.readouterr()
    assert captured.out == b"\x00\x01"
```

### `capfd` (file-descriptor-level capture)

Captures output at the OS file descriptor level — works with C extensions and subprocesses:

```python
def test_subprocess_output(capfd):
    import subprocess
    subprocess.run(["echo", "hello"], check=True)
    captured = capfd.readouterr()
    assert "hello" in captured.out
```

**Disabling capture:**

```bash
pytest -s              # disable all capture (shortcut for --capture=no)
pytest --capture=no    # same as -s
pytest --capture=fd    # use file descriptor capture (default)
pytest --capture=tee-sys # capture but also pass through to terminal
```

---

## Log Capture: caplog

The `caplog` fixture captures log messages emitted during a test:

```python
import logging

def test_logging(caplog):
    logger = logging.getLogger("my_app")

    with caplog.at_level(logging.DEBUG, logger="my_app"):
        logger.info("Processing started")
        logger.warning("Low memory")

    # Check captured records
    assert len(caplog.records) == 2
    assert "Processing started" in caplog.text
    assert caplog.records[0].levelno == logging.INFO

    # Access individual records
    assert caplog.records[1].message == "Low memory"
    assert caplog.records[1].levelname == "WARNING"
```

**Setting log level for a test:**

```python
def test_debug_logs(caplog):
    with caplog.at_level(logging.DEBUG):
        # All DEBUG+ logs are captured
        logging.debug("debug message")
    assert "debug message" in caplog.text
```

**Log propagation:**

```python
def test_with_propagation(caplog):
    with caplog.at_level(logging.INFO):
        with caplog.at_propagation(True):
            logger = logging.getLogger("my_app")
            logger.info("propagated message")
    assert "propagated message" in caplog.text
```

**Log configuration in `pyproject.toml`:**

```toml
[tool.pytest.ini_options]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"

log_file = "logs/pytest.log"
log_file_level = "DEBUG"
log_file_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

---

## pytest Hooks

Hooks let you customize pytest's behavior at collection, execution, and reporting time.
Define them in `conftest.py` or a plugin.

### `pytest_addoption` — Add command-line options

```python
def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev",
                     help="target environment")
    parser.addoption("--run-e2e", action="store_true", default=False,
                     help="run end-to-end tests")
```

### `pytest_configure` — Register markers, configure

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "slow: slow tests")
```

### `pytest_collection_modifyitems` — Auto-mark tests, reorder

```python
def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on directory path."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

    # Skip e2e tests unless --run-e2e is passed
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="need --run-e2e to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)
```

### `pytest_sessionstart` — Setup at session start

```python
def pytest_sessionstart(session):
    """Called once at the start of the test session."""
    # Good place to stub sys.modules for Databricks-only imports
    import sys
    sys.modules["pyspark.pipelines"] = MockDLT()
```

### `pytest_sessionfinish` — Cleanup at session end

```python
def pytest_sessionfinish(session, exitstatus):
    """Called after all tests complete."""
    # Cleanup global resources
    pass
```

### `pytest_runtest_setup` — Before each test

```python
def pytest_runtest_setup(item):
    """Called before each test runs."""
    # Skip integration tests if no Spark available
    if "integration" in item.keywords and not spark_available():
        pytest.skip("Spark not available")
```

### `pytest_runtest_teardown` — After each test

```python
def pytest_runtest_teardown(item, nextitem):
    """Called after each test runs."""
    # Reset global state
    pass
```

### `pytest_runtest_call` — Wrap test execution

```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Wrap test execution — measure time, add context."""
    import time
    start = time.time()
    yield  # let the test run
    duration = time.time() - start
    if duration > 5:
        print(f"\nSlow test: {item.name} took {duration:.1f}s")
```

---

## Markers

### Built-in markers

| Marker | Purpose |
|--------|---------|
| `@pytest.mark.skip(reason="...")` | Always skip |
| `@pytest.mark.skipif(condition, reason="...")` | Skip if condition is True |
| `@pytest.mark.xfail(reason="...", strict=True)` | Expected to fail |
| `@pytest.mark.parametrize(...)` | Parametrize a test |
| `@pytest.mark.usefixtures("fixture1", "fixture2")` | Use fixtures without parameter |
| `@pytest.mark.filterwarnings("error")` | Treat warnings as errors for this test |

### Custom markers

Register in `pyproject.toml` to avoid warnings:

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

### xfail details

```python
@pytest.mark.xfail(reason="Known bug #123", strict=True)
def test_known_bug():
    ...

@pytest.mark.xfail(reason="Not implemented yet", raises=NotImplementedError)
def test_future_feature():
    ...

# strict=True (recommended): if the test unexpectedly PASSES, it's marked as failed
# strict=False (default): if the test passes, it's marked as xpass (unexpected pass)
```

### skipif details

```python
skip_if_no_spark = pytest.mark.skipif(
    not spark_available(),
    reason="Spark not available"
)

@skip_if_no_spark
def test_spark_transform(spark):
    ...
```

### Marker selection

```bash
pytest -m unit                    # only unit tests
pytest -m "not slow"              # everything except slow
pytest -m "integration or e2e"    # integration OR e2e
pytest -m "spark and not slow"    # spark tests that aren't slow
pytest -m "unit and not (slow or integration)"  # complex expressions
```

---

## Configuration

### Configuration file priority (highest to lowest)

1. `pyproject.toml` `[tool.pytest.ini_options]` — **recommended**
2. `pytest.ini` — legacy, still common
3. `tox.ini` `[pytest]` section
4. `setup.cfg` `[tool:pytest]` section — deprecated

If multiple files exist, the highest-priority one is used (they are NOT merged).

### `pyproject.toml` (recommended)

```toml
[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--durations=10",
]

markers = [
    "unit: fast unit tests",
    "integration: tests requiring Spark",
    "e2e: end-to-end tests",
]

# asyncio support
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"

# Log capture
log_cli = true
log_cli_level = "INFO"
log_file = "logs/pytest.log"
log_file_level = "DEBUG"
```

### `pytest.ini` (legacy)

```ini
[pytest]
testpaths = tests
addopts = -ra --strict-markers
markers =
    unit: fast unit tests
    integration: tests requiring Spark
```

### rootdir determination

pytest determines the `rootdir` by:
1. Starting from the common ancestor of all test file paths
2. Walking upward until it finds a configuration file (`pyproject.toml`, `pytest.ini`, `tox.ini`, `setup.cfg`)
3. If no config file is found, the common ancestor is used

The `rootdir` is used for:
- Resolving relative paths in configuration
- Storing the `.pytest_cache` directory
- Plugin data storage

### importlib mode

For projects with complex import structures or src-layout:

```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]
```

`importlib` mode (recommended for new projects):
- Uses `importlib` instead of `sys.path` manipulation
- Better support for src-layout and namespace packages
- Avoids `__init__.py` conflicts
- No `conftest.py` re-import issues

`prepend` mode (legacy default):
- Inserts test file directories into `sys.path`
- Can cause import conflicts with packages of the same name

### `addopts` common options

```toml
[tool.pytest.ini_options]
addopts = [
    "-ra",                    # show summary for all except passed
    "--strict-markers",       # error on unregistered markers
    "--strict-config",        # error on bad config
    "--durations=10",         # show 10 slowest tests
    "--tb=short",             # short traceback format
    "--cov=src",              # coverage for src/
    "--cov-report=term-missing",
    "--cov-report=html:reports/coverage.html",
    "--html=reports/report.html",
    "--self-contained-html",
    "--timeout=300",          # fail tests that take > 300s
]
```

### `conftest.py` locations

- **Root `conftest.py`**: available to all tests — global stubs, hooks, markers
- **Directory `conftest.py`**: available to tests in that directory and subdirectories
- Fixtures, hooks, and `pytest_addoption` go in `conftest.py`
- `conftest.py` files are not imported as modules — they are discovered by pytest

---

## pytest Cache

pytest caches test results between runs in `.pytest_cache/`. This enables re-running
only failed tests or tests that changed.

### Re-run failed tests

```bash
pytest --lf          # --last-failed: only run tests that failed last time
pytest --lf -v       # verbose
pytest --lfnf=none   # if no failures last time, run nothing
pytest --lfnf=all    # if no failures last time, run all (default)
```

### Run tests in order of failure (failed first)

```bash
pytest --ff          # --failed-first: run failed tests first, then the rest
```

### Show cache contents

```bash
pytest --cache-show          # show all cached data
pytest --cache-show=lastfailed  # show specific key
```

### Clear cache

```bash
pytest --cache-clear
```

### Using cache in fixtures/hooks

```python
def pytest_collection_modifyitems(config, items):
    cache = config.cache
    # Read from cache
    last_failed = cache.get("cache/lastfailed", {})
    # Write to cache
    cache.set("myplugin/data", {"key": "value"})
```

### Cache configuration

```toml
[tool.pytest.ini_options]
cache_dir = ".pytest_cache"  # default
```

Add `.pytest_cache` to `.gitignore`:
```
.pytest_cache/
```

---

## Warnings Management

pytest captures warnings by default and displays a summary. You can control how
warnings are handled.

### Filter warnings in configuration

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "error",                           # treat all warnings as errors
    "ignore::DeprecationWarning",      # ignore DeprecationWarning
    "ignore::PendingDeprecationWarning",
    "always::ResourceWarning",         # always show ResourceWarning
    "default::UserWarning",            # default behavior for UserWarning
    "module::pytest.PytestUnraisableExceptionWarning",
    "once::DeprecationWarning",        # show only once per location
]
```

### Filter warnings per test

```python
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_with_deprecated_code():
    ...

@pytest.mark.filterwarnings("error")
def test_strict_warnings():
    ...
```

### Warning filter syntax

```
action:message:category:module:lineno
```

- `action`: `error`, `ignore`, `always`, `default`, `module`, `once`
- `message`: regex to match warning message
- `category`: warning class (e.g., `DeprecationWarning`)
- `module`: regex to match module name
- `lineno`: line number

### Disable warning summary

```bash
pytest -W ignore              # ignore all warnings
pytest -W error::DeprecationWarning  # treat DeprecationWarning as error
pytest --disable-warnings     # disable warning summary in output
```

---

## Doctest Support

pytest can run doctests in your source modules and docstrings.

### Run doctests in modules

```bash
pytest --doctest-modules src/my_project/
```

### Run doctests in README files

```bash
pytest --doctest-glob="*.md"
```

### Configuration

```toml
[tool.pytest.ini_options]
addopts = ["--doctest-modules"]
doctest_optionflags = ["NORMALIZE_WHITESPACE", "ELLIPSIS"]
```

### Example doctest

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

### Doctest with fixtures (using `getfixture`)

```python
def my_function(spark):
    """Process data.

    >>> result = my_function(getfixture('spark'))
    >>> result.count()
    3
    """
    ...
```

---

## Good Practices

1. **Test files outside source**: Keep `tests/` separate from `src/` — tests are
   development-time artifacts, not runtime dependencies.

2. **Unique test names**: `test_transform_filters_by_date` not `test_transform_1`.
   Test names should describe what they test.

3. **One assertion concept per test**: Test one behavior per function. Multiple asserts
   are fine if they test the same concept.

4. **Use fixtures for shared setup**: Don't copy-paste setup code — extract it into a fixture.

5. **Parametrize for coverage**: One test function, many inputs — reduces duplication and
   increases coverage.

6. **Mark tests appropriately**: Use markers (`unit`, `integration`, `e2e`) to select
   test tiers in CI.

7. **Keep unit tests fast**: < 100ms per test. Mock external dependencies (Spark, network,
   databases).

8. **Use `--strict-markers`**: Catch typos in marker names early — prevents silently
   unmarked tests.

9. **Use `--strict-config`**: Error on bad configuration instead of silently ignoring it.

10. **Isolate tests**: Tests should not depend on each other or on shared mutable state.
    Use `function`-scoped fixtures for test-specific data.

11. **Test the behavior, not the implementation**: Tests should verify what the code does,
    not how it does it. This makes refactoring easier.

12. **Use `assert` with messages for complex checks**:

```python
assert result.count() == 5, f"Expected 5 rows, got {result.count()}"
```

13. **Prefer `pytest.approx` for floats**:

```python
assert 0.1 + 0.2 == pytest.approx(0.3)
assert large_value == pytest.approx(expected, rel=1e-3)  # relative tolerance
```

14. **Use `importlib` mode for new projects**: Avoids `sys.path` issues with src-layout.

15. **Pin pytest version in CI**: Use `minversion` and pin in your lockfile for reproducibility.

---

## CLI Flags Quick Reference

### Test selection

| Flag | Description |
|------|-------------|
| `pytest -k "expr"` | Run tests matching keyword expression |
| `pytest -m marker` | Run tests with marker |
| `pytest --lf` | Run only tests that failed last time |
| `pytest --ff` | Run failed tests first |
| `pytest tests/test_foo.py` | Run specific file |
| `pytest tests/test_foo.py::test_bar` | Run specific test |
| `pytest tests/test_foo.py::TestClass::test_method` | Run specific method |
| `pytest -x` | Stop on first failure |
| `pytest --maxfail=3` | Stop after 3 failures |
| `pytest --sw` | Stepwise: stop at first failure, start there next time |

### Output control

| Flag | Description |
|------|-------------|
| `pytest -v` | Verbose (one line per test) |
| `pytest -q` | Quiet (dots only) |
| `pytest -l` | Show local variables in tracebacks |
| `pytest -s` | Disable output capture |
| `pytest --tb=short` | Short traceback format |
| `pytest --tb=long` | Long traceback format (default) |
| `pytest --tb=line` | One line per failure |
| `pytest --tb=no` | No tracebacks |
| `pytest -rA` | Show summary for all tests |
| `pytest -ra` | Show summary for all except passed |
| `pytest -rf` | Show summary for failed |
| `pytest -rs` | Show summary for skipped |
| `pytest --durations=10` | Show 10 slowest tests |

### Debugging

| Flag | Description |
|------|-------------|
| `pytest --pdb` | Drop into debugger on failure |
| `pytest --pdbcls=IPython.terminal.debugger:Pdb` | Use IPython debugger |
| `pytest --trace` | Drop into debugger immediately at start of each test |
| `pytest --lf --pdb` | Re-run failures and debug them |

### Reporting

| Flag | Description |
|------|-------------|
| `pytest --cov=src` | Coverage for src/ |
| `pytest --cov-report=term-missing` | Coverage report with missing lines |
| `pytest --cov-report=html` | HTML coverage report |
| `pytest --html=report.html` | HTML test report |
| `pytest --self-contained-html` | Embed CSS/JS in HTML report |
| `pytest --junitxml=report.xml` | JUnit XML report (for CI) |

### Execution

| Flag | Description |
|------|-------------|
| `pytest -n auto` | Parallel execution (pytest-xdist) |
| `pytest -n 4` | Parallel with 4 workers |
| `pytest --dist loadfile` | Distribute by file (better for mixed durations) |
| `pytest --dist loadscope` | Distribute by test class/module |
| `pytest --timeout=300` | Fail tests that take > 300s |
| `pytest -p no:cacheprovider` | Disable cache |

### Information

| Flag | Description |
|------|-------------|
| `pytest --markers` | Show available markers |
| `pytest --fixtures` | Show available fixtures |
| `pytest --fixtures-per-test` | Show fixtures for each test |
| `pytest --collect-only` | Show collected tests without running |
| `pytest --version` | Show pytest version |
| `pytest -h` / `--help` | Show help |
