---
name: pytest-skill
description: >
  Production-grade pytest guidance for Python tests: authoring, fixtures,
  parametrization, assertions, mocking, markers, discovery, plugins, hooks,
  debugging, output, warnings, doctests, CI, and migration from unittest.
  Use this skill whenever a request mentions pytest, conftest.py, fixtures,
  pytest.mark, parametrization, test discovery, pytest plugins/hooks, or asks
  how to write, run, debug, organize, or improve Python tests with pytest.
  For PySpark or Databricks-specific testing, also use pytest-databricks.
license: MIT
metadata:
  author: TestMu AI
  version: "2.0"
  source: "https://docs.pytest.org/en/stable/"
---

# Pytest Skill

Use this as an implementation playbook, not as a reason to add dependencies or
over-engineer a small test. Prefer the smallest pytest feature that gives a
clear, isolated, behavior-focused test.

## Operating workflow

1. **Inspect before editing.** Read the target module, nearby tests,
   `conftest.py` files, and the active pytest configuration. Check
   `pytest --version` and installed plugins when behavior may be version- or
   plugin-dependent.
2. **Classify the test.** Choose pure unit, integration, subprocess/CLI,
   async, plugin, doctest, or compatibility testing. Do not use a real network,
   cloud resource, clock, or random source in a unit test unless that behavior
   is explicitly the subject of the test.
3. **Choose the narrowest mechanism.** Organize pytest tests in a dedicated
   `Test*` class for the production function or class under test, and use plain
   `assert` statements within its test methods; use fixtures for
   dependencies/lifecycle; `parametrize` for a known decision
   table; `subtests` only for cases discovered during execution; and mocks only
   at an external boundary.
4. **Make isolation explicit.** Prefer function-scoped fixtures and
   `tmp_path`. Split state-changing setup into small yield fixtures with
   teardown immediately after `yield`. Avoid hidden `autouse` state unless it
   is truly global test policy.
5. **Verify in layers.** Run collection first, the focused test, the relevant
   test directory/marker, and then the full suite when practical. Report
   skipped, xfailed, warnings, and deselected tests rather than hiding them.

Read the reference that matches the task:

| Need | Reference |
|---|---|
| Official how-to and examples coverage, newer pytest features | `reference/official-patterns.md` |
| Deep fixture, assertion, cache, configuration, CI, and plugin playbook | `reference/playbook.md` |
| Dynamic parametrization, plugin testing, fixture overrides, async patterns | `reference/advanced-patterns.md` |

For Spark, Databricks Connect, `dbutils`, `WorkspaceClient`, or
`databricks-labs-pytester`, load `pytest-databricks` as well; do not replace its
environment-specific guidance with generic mocks.

## Core test patterns

## Project test organization, paths, and documentation

Apply these conventions to all pytest code unless the project has an explicit,
documented exception:

- Separate test suites into `tests/unit/` and `tests/integration/`. Put shared
  fixtures, hooks, and pytest configuration in `tests/conftest.py`, and reuse
  those fixtures rather than recreating common setup in individual test files.
- Treat `pytestconfig.rootpath` as the base for test resources. Construct paths
  with `pathlib.Path`, never hard-code absolute paths, and avoid `.resolve()`
  when it would bind the test to a machine-specific layout. Define reusable
  resource-directory fixtures in `tests/conftest.py` and inject them where
  needed:

  ```python
  from pathlib import Path

  import pytest


  @pytest.fixture
  def fixtures_dir(pytestconfig) -> Path:
      return pytestconfig.rootpath / "tests" / "fixtures"
  ```

  A test should then compose its resource path from the injected fixture, for
  example `data_path = fixtures_dir / "data.json"`.
- Begin every test file with a module docstring that identifies the component,
  the covered scenarios, and whether the file contains unit or integration
  tests. Give every test method a concise docstring stating the behavior under
  test, its input or setup, its expected behavior, and the regression or
  contract it protects.
- Organize tests by production symbol. Use one dedicated `Test*` class for each
  production function or class, with only the relevant cases for that symbol in the
  class. Do not write standalone `test_*` functions. Name classes and methods
  with pytest conventions and observable behavior, such as `TestParseEmail`,
  `test_returns_expected_value`, and `test_raises_for_invalid_input`.

The expected layout is:

```text
tests/
├── conftest.py
├── unit/
└── integration/
```

Keep unit tests isolated and deterministic. Use integration tests when a case
depends on multiple components, external services, databases, filesystems, or
infrastructure.


### Plain tests and assertion introspection

```python
import pytest


class TestTotal:
    def test_includes_tax(self):
        """Checks subtotal 10 at 20 percent tax returns 12, protecting tax arithmetic."""
        assert total(subtotal=10, tax_rate=0.2) == 12


class TestParseEmail:
    def test_reports_invalid_input(self):
        """Checks invalid email input raises its validation error, preserving the input contract."""
        with pytest.raises(ValueError, match=r"invalid email") as exc_info:
            parse_email("not-an-email")
        assert exc_info.value.args[0] == "invalid email"


class TestCalculateRatio:
    def test_returns_approximate_float_result(self):
        """Checks one divided by three is accurate within tolerance, guarding float precision."""
        assert calculate_ratio(1, 3) == pytest.approx(1 / 3, rel=1e-6)
```

Use `assert left == right`, not `self.assertEqual`; pytest rewrites asserts to
show useful diffs for strings, sequences, mappings, sets, and expressions.
Add a message only when it adds domain context. Use `pytest.fail()` for a
failure discovered by control flow, not as a replacement for normal asserts.

For modern Python exception groups, use `pytest.RaisesGroup` and
`pytest.RaisesExc` when the group structure matters. Do not assert only that an
exception group contains one expected exception if additional unexpected
exceptions would make the test unsafe.

### Fixtures: dependency injection and lifecycle

```python
import pytest


@pytest.fixture
def user_factory():
    created = []

    def make_user(name="Alice"):
        user = {"name": name}
        created.append(user)
        return user

    yield make_user
    # Replace this with real cleanup when the fixture creates resources.
    created.clear()


class TestUserFactory:
    def test_creates_user_with_given_name(self, user_factory):
        """Checks the fixture factory creates Bob data, preserving fixture-provided setup."""
        assert user_factory("Bob") == {"name": "Bob"}
```

Rules that prevent most fixture bugs:

- A test requests a fixture by naming it as an argument; fixtures can request
  other fixtures and pytest caches one instance per test/scope.
- Use `function` scope by default. Use `class`, `module`, `package`, or
  `session` only when sharing is safe and materially reduces setup cost.
- A broader-scoped fixture cannot depend on a narrower-scoped fixture
  (`ScopeMismatch`). A callable `scope=` can select scope from a CLI option.
- Prefer one state-changing action per yield fixture. Teardown runs in reverse
  dependency order; `addfinalizer` is useful when cleanup must be registered
  conditionally after setup succeeds.
- Use factory fixtures when one test needs multiple independently-created
  objects. Do not call a fixture function directly; compose it or use
  `request.getfixturevalue()` only for genuinely dynamic lookup.
- Use `request.node`, `request.param`, `request.config`, and markers for
  carefully scoped dynamic behavior. Keep the normal dependency graph explicit.
- Put shared fixtures in the nearest appropriate `conftest.py`. A closer
  `conftest.py` can override an upstream fixture; `usefixtures` is for setup
  whose returned value is not needed by the test.

`autouse=True` is appropriate for narrowly-scoped global policy such as
resetting process state or installing a safety guard. It is usually a smell for
data setup because it hides why a test depends on that state.

### Parametrization and test IDs

```python
import pytest


class TestNormalizeName:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            pytest.param(" Alice ", "Alice", id="trimmed"),
            pytest.param("", "", id="empty"),
            pytest.param(None, None, marks=pytest.mark.xfail(reason="pending API decision"), id="none"),
        ],
    )
    def test_returns_normalized_value(self, raw, expected):
        """Checks named inputs normalize as expected, documenting API edge-case behavior."""
        assert normalize_name(raw) == expected
```

- Give meaningful `ids` for domain cases; IDs become part of node IDs and make
  failures/selective reruns understandable.
- Stack decorators for a Cartesian product only when every combination is
  meaningful. Prefer explicit case objects when the matrix would explode.
- Use `indirect=True` to pass a value into a fixture, and fixture
  `params=[...]` when the fixture itself is the varying dependency.
- Parameter values are passed as-is, not copied. Never mutate shared list/dict
  parameters; construct fresh values or use immutable case data.
- Apply `pytest.param(..., marks=...)` for a single-case skip/xfail.
- Use `pytest_generate_tests(metafunc)` for collection-time cases from CLI
  options or checked-in data. Decide and document the empty-case policy.

Use `subtests` (pytest 9+) when cases are discovered only during test
execution and all failures should be reported in one test. Parametrization is
better when cases should be collected, selected by node ID, rerun individually,
or handled by `--last-failed`.

### Mocking and monkeypatching

Patch the name looked up by the system under test, not necessarily the name in
the dependency's original module:

```python
class TestFetchUser:
    def test_returns_user_from_http_response(self, mocker):
        """Checks a mocked user response returns Ada, protecting the HTTP boundary contract."""
        response = mocker.Mock(status_code=200)
        response.json.return_value = {"id": 7, "name": "Ada"}
        mocker.patch("myapp.users.requests.get", return_value=response)

        assert fetch_user(7)["name"] == "Ada"


class TestLoadSettings:
    def test_reads_test_environment(self, monkeypatch):
        """Checks test environment variables configure settings, preventing process-state leakage."""
        monkeypatch.setenv("APP_ENV", "test")
        monkeypatch.delenv("OPTIONAL_FLAG", raising=False)
        assert load_settings().environment == "test"
```

- Use `pytest-mock`'s `mocker` for `patch`, `spy`, `stub`, and automatic mock
  cleanup; use `unittest.mock` when the project already standardizes on it.
- Use `monkeypatch.setattr/delattr`, `setitem/delitem`, `setenv/delenv`,
  `syspath_prepend`, `chdir`, and `monkeypatch.context()` for reversible local
  changes. `raising=False` is intentional only when absence is valid.
- Prefer dependency injection or a small fake when it makes the boundary
  clearer. Use `spec`/`autospec` where appropriate so a mock cannot invent an
  invalid API. Assert important observable calls, not every implementation
  detail.
- For async calls use `AsyncMock` and await the system under test; do not make a
  synchronous mock pretend to be awaitable.

### Markers, skips, and xfails

Register custom markers and run with `--strict-markers`:

```toml
[tool.pytest.ini_options]
markers = [
  "unit: fast isolated tests",
  "integration: uses a real service or local integration runtime",
  "slow: takes longer than the normal test budget",
]
```

```python
import pytest


class TestDatabaseRoundTrip:
    @pytest.mark.integration
    def test_persists_and_reads_data(self, database):
        """Checks the integration database round trip, protecting multi-component persistence."""
        ...


class TestGpuPath:
    @pytest.mark.skipif(not HAS_GPU, reason="requires GPU")
    def test_uses_gpu_when_available(self):
        """Checks GPU-capable setup follows the GPU path, preserving optional hardware support."""
        ...


class TestKnownBug:
    @pytest.mark.xfail(strict=True, raises=KnownBug, reason="issue #123")
    def test_exposes_known_bug(self):
        """Exercises the known failing setup, ensuring the tracked defect remains visible."""
        ...
```

Use `pytest.importorskip("optional_pkg", minversion="...")` for optional
dependencies. Use imperative `pytest.skip()`/`pytest.xfail()` only when the
condition is known during setup or execution. Make xfails strict in CI when an
unexpected pass should force removal of stale bug metadata. Never use skip or
xfail to conceal an ordinary failing test.

### Files, output, logs, and warnings

- Use `tmp_path` (`pathlib.Path`) for per-test files and `tmp_path_factory` for
  expensive session-shared artifacts. Use `--basetemp` only with a disposable
  directory because it is cleared before the run.
- Use `capsys` for Python-level text output, `capsysbinary` for bytes, `capfd`
  or `capfdbinary` for subprocess/file-descriptor output, and
  `capsys.disabled()` for a short intentionally-live block.
- Use `caplog.at_level()`/`set_level()`, `caplog.records`, `record_tuples`, and
  `caplog.clear()` to test logging behavior. Configure live/file logging only
  when it helps the workflow; do not assert on formatting unless formatting is
  the contract.
- Use `pytest.warns()` to assert an expected warning and `recwarn` to inspect
  all warnings. Treat unexpected deprecations as errors in CI, with narrow,
  documented filters for intentionally legacy behavior.

### Async, CLI, doctest, and unittest compatibility

- For async tests, use the project’s async plugin (commonly `pytest-asyncio`),
  configure its event-loop policy explicitly, and use async fixtures according
  to that plugin's current API.
- For a CLI, prefer invoking the real entry point in a subprocess when process
  boundaries, exit codes, or stdout/stderr matter; use `capsys` for a direct
  function-level CLI test.
- Run docstrings with `--doctest-modules` and text examples with
  `--doctest-glob`. Use `doctest_optionflags`, `doctest_namespace`,
  `getfixture('fixture_name')`, and `--doctest-continue-on-failure` deliberately.
- pytest runs `unittest.TestCase` suites, including their setup methods and
  skips. During migration, retain compatibility first; do not assume normal
  pytest fixture arguments or parametrization work inside `TestCase` methods.
  New pytest tests should normally use fixtures and plain asserts.

## Discovery and command cookbook

```bash
# Run and select
python -m pytest                         # current interpreter; adds cwd to sys.path
pytest tests/                            # directory
pytest tests/test_api.py::TestUsers::test_create
pytest 'tests/test_api.py::test_parse[empty]'  # quote [] in shells that expand it
pytest -k 'login and not slow'
pytest -m 'unit and not integration'
pytest --pyargs installed_package.tests
pytest @tests-to-run.txt                 # one path/node/option per line (pytest 8.2+)

# Understand collection/configuration
pytest --version
pytest --collect-only -q
pytest --fixtures
pytest --markers
pytest --trace-config                    # active plugins and conftest files
pytest --setup-show tests/test_api.py
pytest --setup-plan                       # inspect fixture plan without running

# Tight feedback loop
pytest -x --maxfail=3
pytest --lf                             # only last failures; use --lfnf=none if desired
pytest --ff                             # failures first, then all tests
pytest --nf                             # newest files first
pytest --cache-show
pytest --cache-clear
pytest --durations=10 --durations-min=1.0

# Debug/report
pytest -x --pdb
pytest --trace
pytest -l --tb=short
pytest --full-trace
pytest -ra --show-capture=all
pytest --junitxml=reports/junit.xml     # CI report
```

`-n auto`, `--cov`, `--html`, `--timeout`, `--reruns`, and stepwise options
come from plugins. Confirm the plugin is installed and active before adding
them to project defaults. Use `pytest -p no:PLUGIN` or
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` to diagnose plugin interference.

When invoking from Python, call `pytest.main([...])` with explicit arguments
and inspect its return value. Avoid calling `pytest.main()` repeatedly in one
process because imported test modules remain cached.

## Configuration baseline

Prefer the project's existing configuration format. A conservative baseline is:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra", "--strict-markers", "--strict-config", "--tb=short"]
markers = [
  "unit: fast isolated tests",
  "integration: tests using external or integration resources",
  "slow: tests outside the normal runtime budget",
]
```

Add coverage, async, timeout, logging, doctest, or warning policy only when the
corresponding dependency and project policy exist. Do not blindly combine
`-v` and `-q`, or make every local run stop at the first failure. Check the
actual configuration source with `pytest --help` and the session header; pytest
configuration files are not merged arbitrarily.

## Plugin and hook work

Use a local `conftest.py` for project-only fixtures and hooks. Use a package
plugin when behavior is reusable across projects. Register a plugin through a
`pytest11` entry point when it must be installable. Test plugins with the
built-in `pytester` fixture by creating temporary test files and asserting
outcomes.

Safe hook rules:

- Hook argument names are validated and optional arguments can be omitted.
- Most non-test-running hooks should not raise; turn user/config errors into a
  clear `pytest.UsageError` or a controlled report.
- Use `@pytest.hookimpl(tryfirst=True/trylast=True)` only when ordering is part
  of the design. Hook wrappers are generator functions that yield exactly once.
- For custom collection, use public `pytest.File`, `pytest.Item`,
  `pytest.Directory`, `pytest_collect_file`, or `pytest_collect_directory` APIs;
  implement `runtest`, `repr_failure`, and `reportinfo` for useful failures.
- Use `pytest_collection_modifyitems` for collection-time marking/deselection,
  but keep policy visible and test it. `pytest_assertrepr_compare` and
  `pytest.register_assert_rewrite()` are advanced tools for shared helpers.

## Quality gates and anti-patterns

- Name tests after behavior and keep Arrange–Act–Assert readable.
- Test public behavior and contracts, not private call order.
- Keep tests independent, deterministic, and safe to run in any order or with
  xdist. Seed or inject randomness and control time rather than sleeping.
- Separate unit/integration/e2e markers and make external-resource tests opt-in
  or skip with an explicit reason.
- Avoid mutable module globals, broad `except Exception`, test ordering,
  unconditional network calls, hard-coded temp paths, over-mocking, and tests
  with no meaningful assertion.
- Treat retries as a last-resort quarantine for diagnosed environmental
  flakiness; fix the race or isolation problem instead of masking it.

## Official coverage map

The companion reference was refreshed against the current pytest stable docs:

- **How-to:** invocation, assertions, fixtures, marks, parametrization,
  subtests, temporary paths, monkeypatch, doctests, cache, failures, output,
  logging, capture, warnings, skip/xfail, plugins, plugin writing/hooks,
  existing suites, unittest, xunit setup, and bash completion.
- **Examples:** failure reports, basic patterns, parametrization, custom marks,
  collection-aware session fixtures, custom discovery, non-Python collectors,
  and custom directory collectors.

Source index: <https://docs.pytest.org/en/stable/how-to/index.html> and
<https://docs.pytest.org/en/stable/example/index.html>.
