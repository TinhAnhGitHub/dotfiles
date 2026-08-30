# Official pytest patterns and examples

This reference distills the current stable pytest how-to and examples indexes
into implementation-oriented advice. The source pages are the authority for
version-sensitive details:

- <https://docs.pytest.org/en/stable/how-to/index.html>
- <https://docs.pytest.org/en/stable/example/index.html>

Use this file when a task needs a less common pytest feature. Prefer public
pytest APIs and verify the installed pytest version before using newer features.

## 1. Invocation, selection, and collection

Pytest discovers `test_*.py` and `*_test.py`, then `test_*` functions/methods
and `Test*` classes without an `__init__`. The invocation forms below compose:

```bash
pytest                                  # current directory
pytest tests/test_api.py                # one module
pytest tests/unit/                       # one directory tree
pytest tests/test_api.py::TestUsers     # one class
pytest tests/test_api.py::test_create   # one test
pytest 'tests/test_api.py::test_parse[empty]'  # one parameter case
pytest -k 'user and not slow'           # name/node keyword expression
pytest -m 'integration and not slow'    # marker expression
pytest --pyargs mypackage.tests         # import package, then collect there
pytest @selected-tests.txt              # paths/node IDs/options, one per line
```

Useful collection controls include `--ignore PATH`, `--ignore-glob PATTERN`,
`--deselect NODEID`, `--keep-duplicates`, and `--collect-only`. Configure
`testpaths`, `python_files`, `python_classes`, `python_functions`, and
`norecursedirs` rather than relying on a large accidental search tree.

`python -m pytest` is almost the same as `pytest`, but adds the current working
directory to `sys.path`. `pytest --version`, `pytest -h`, `pytest --fixtures`,
`pytest --markers`, and `pytest --trace-config` are the first diagnostic
commands when a test, fixture, option, or plugin is not found.

From Python, use an explicit argument list:

```python
import pytest

exit_code = pytest.main(["-q", "tests/unit"])
assert exit_code == pytest.ExitCode.OK
```

Do not call `pytest.main()` repeatedly in one process to observe source edits:
test modules imported by the first call remain in Python's import cache.

## 2. Assertions and failure reports

Use ordinary Python `assert` statements. Assertion rewriting provides focused
comparisons for values, calls, attributes, strings, lists, dictionaries, sets,
and membership expressions. Prefer this:

```python
assert response.status_code == 201
assert response.json() == {"id": 4, "name": "Ada"}
```

Use the assertion helpers for semantic cases:

```python
assert measured == pytest.approx(expected, rel=1e-6, abs=1e-9)

with pytest.raises(ValueError, match=r"invalid.*email") as info:
    parse_email(value)
assert info.value.args == ("invalid email",)

with pytest.warns(DeprecationWarning, match="use parse_email"):
    legacy_parse(value)
```

`pytest.raises` accepts subclasses. If an exact type is part of the contract,
also assert `info.type is ExpectedError`. Use its `check=` predicate when a
small structured condition is clearer than inspecting a message. Do not put
too much code inside a `raises` block: an exception from the wrong statement
can make a test pass for the wrong reason.

For Python exception groups, `pytest.RaisesGroup` checks the group structure and
`pytest.RaisesExc` describes an individual expected exception. Use
`flatten_subgroups` or `allow_unwrapped` only when the contract allows those
shapes. `ExceptionInfo.group_contains()` is convenient for presence checks but
must not be used alone to prove that no unexpected exception is present.

For shared assertion helpers, add `pytest.register_assert_rewrite("pkg.helpers")`
from a package entry point or root `conftest.py`. A helper can implement
`pytest_assertrepr_compare` to provide domain-specific diffs. Keep these hooks
small and test them with a failing example; use `--assert=plain` only when
debugging assertion-rewrite interference.

## 3. Fixtures: the complete mental model

A fixture is a named dependency. Pytest resolves the dependency graph, runs
setup once per active scope, caches its return value for that scope, passes it
to tests, then finalizes it. A fixture can request fixtures just like a test.

```python
@pytest.fixture(scope="module")
def client(server_url):
    client = Client(server_url)
    yield client
    client.close()
```

Available scopes are `function`, `class`, `module`, `package`, and `session`.
Use a callable scope when a command-line option controls an expensive resource:

```python
def resource_scope(fixture_name, config):
    return "session" if config.getoption("--keep-resource") else "function"


@pytest.fixture(scope=resource_scope)
def resource():
    yield start_resource()
```

Keep scope dependencies valid: a session fixture cannot depend on a function
fixture. Pytest groups tests to minimize active parametrized fixture instances;
do not depend on incidental execution order.

### Safe teardown

Prefer one state-changing action per fixture and put cleanup immediately after
`yield`. If setup fails before `yield`, its teardown is not run, so only register
an `addfinalizer` after the resource was successfully created:

```python
@pytest.fixture
def temporary_user(request, api):
    user = api.create_user()
    request.addfinalizer(lambda: api.delete_user(user.id))
    return user
```

Use `yield` for the normal case. `addfinalizer` is useful for conditional or
multi-step cleanup. Split fixtures rather than putting many unrelated actions
into one fixture; pytest unwinds completed fixtures in reverse dependency order.

### `request`, markers, and factories

`request.node` gives the current test item, `request.config` gives configuration,
`request.param` carries fixture parametrization, and `request.getfixturevalue`
allows carefully controlled dynamic lookup. A factory fixture returns a creator
function when one test needs multiple values. `usefixtures` runs a fixture when
the test does not need its value. A closer `conftest.py` can override a fixture
for a subtree, which is useful for replacing a real integration dependency with
an in-memory implementation in unit tests.

Avoid direct calls to fixture functions. Avoid broad `autouse` fixtures: they
make dependencies invisible. Autouse is reasonable for narrow global safety or
cleanup policy.

## 4. Marks, parametrization, and subtests

Register custom marks in configuration and use `--strict-markers` to catch
typos. Marks can be applied to functions, classes, modules via `pytestmark`,
and individual parameter cases:

```python
pytestmark = pytest.mark.api


@pytest.mark.device(serial="123")
def test_device():
    ...


@pytest.mark.parametrize(
    "payload,expected",
    [
        pytest.param({}, 400, id="missing-fields"),
        pytest.param({"name": "Ada"}, 201, id="valid"),
        pytest.param(None, 500, marks=pytest.mark.xfail(reason="issue #44")),
    ],
)
def test_create(payload, expected):
    ...
```

Marker selection supports boolean expressions and keyword arguments whose
values are simple `int`, `str`, `bool`, or `None` values:

```bash
pytest -m 'api and not slow'
pytest -m "device(serial='123')"
```

For parametrization, prefer readable IDs via `ids=[...]`, `pytest.param(id=...)`,
or an `ids=` function. Stack decorators only for a purposeful Cartesian
product. Use `indirect=True` to route values through a fixture. Use a fixture's
`params=[...]` when the varying object is the fixture itself.

Parameter values are passed without copying. Mutable values can leak mutations
between cases, so use tuples/immutable case data or create fresh objects.

Use `pytest_generate_tests(metafunc)` in `conftest.py` or a test module for
collection-time parameters derived from CLI options or checked-in data:

```python
def pytest_addoption(parser):
    parser.addoption("--case", action="append", default=[])


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        cases = metafunc.config.getoption("--case")
        metafunc.parametrize("case", cases, ids=str)
```

Document the behavior when the generated list is empty (`skip`, `xfail`, or
collection failure according to the project's policy).

### Subtests

Core subtests are available starting in pytest 9 and are still experimental:

```python
def test_all_supported_formats(subtests):
    for fmt in discover_formats():
        with subtests.test(format=fmt):
            assert can_round_trip(fmt)
```

Subtests run during execution, so individual cases cannot be selected by node
ID or independently rerun by `--last-failed`; failures do not stop later cases.
Use parametrization for known decision tables and subtests for dynamic cases.

## 5. Temporary files and monkeypatching

`tmp_path` is a unique `pathlib.Path` per test. `tmp_path_factory` is session
scoped and is suitable for an expensive artifact shared by tests. Pytest keeps
recent temporary runs by default. `--basetemp` selects a base directory and
clears it before a run, so never point it at a directory containing user data.
Prefer these fixtures over `tempfile` paths hard-coded into tests. `tmpdir` is
legacy `py.path` behavior; use `tmp_path` for new code.

`monkeypatch` automatically restores changes at the end of the requesting test
or fixture:

```python
def test_home_and_path(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("MODE", "test")
    monkeypatch.setitem(CONFIG, "retries", 0)
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
```

The full API is `setattr`, `delattr`, `setitem`, `delitem`, `setenv`, `delenv`,
`syspath_prepend`, `chdir`, and `context`. Patch where the application looks up
the name. `monkeypatch.context()` is useful for limiting a risky patch to a
small block. Use `raising=False` only when a missing target/key is expected.

## 6. Output, logging, warnings, and outcomes

Pytest captures output and displays it for failed tests. Select the capture
implementation with `--capture=fd|sys|tee-sys|no`; `-s` means `no`.

- `capsys`: Python `sys.stdout`/`sys.stderr` text.
- `capsysbinary`: Python-level bytes.
- `capfd`/`capfdbinary`: OS file descriptors, including subprocess output.
- `capsys.disabled()`: temporarily show output live.
- `caplog`: records and text; use `at_level`, `set_level`, `records`,
  `record_tuples`, `get_records("setup"|"call"|"teardown")`, and `clear()`.

Use `--show-capture=no|stdout|stderr|log|all`, `--log-cli-level`, and
`--log-file` for workflow/reporting needs. Assert the logging contract, not
incidental formatter details.

Warnings are captured automatically. Use `pytest.warns`, `pytest.deprecated_call`,
and `recwarn` for assertions. `filterwarnings` can be configured globally or
per test with `pytest.mark.filterwarnings`; keep ignores narrow and explained.

Use `skip` when prerequisites are absent and the test cannot run. Use `xfail`
when a known defect or unsupported behavior is expected. `xfail(strict=True)`
turns an unexpected pass into a failure. `raises=` narrows which defect is
allowed. Use `pytest.importorskip` for optional modules and
`allow_module_level=True` for a conditional module skip.

## 7. Cache, failure handling, and debugging

The built-in cache provider supports the fast feedback loop:

```bash
pytest --lf                 # last failures only; defaults to all if none exist
pytest --lf --lfnf=none     # run nothing when there are no cached failures
pytest --ff                 # failed tests first, then the rest
pytest --nf                 # new/modified files first
pytest --cache-show
pytest --cache-clear
```

Plugins and `conftest.py` can store JSON-encodable values with
`pytestconfig.cache.get("namespace/key", default)` and `.set(...)`. Do not put
secrets or large artifacts in `.pytest_cache`; clear it in CI when stale state
could affect the result.

For failures, use `-x`/`--maxfail=N`, `--pdb`, `--trace`, `breakpoint()`,
`--showlocals`, `--tb=short|long|line|native|no`, `--full-trace`, and
`faulthandler_timeout` as appropriate. Pytest enables faulthandler by default;
it also reports unraisable and unhandled thread exceptions as warnings. Treat
those warnings as defects instead of allowing silent background failures.

## 8. Doctests and existing test suites

```bash
pytest --doctest-modules src/
pytest --doctest-glob='*.rst' docs/
pytest --doctest-modules --doctest-continue-on-failure
pytest --doctest-modules --doctest-report=ndiff
```

Use `doctest_optionflags` such as `NORMALIZE_WHITESPACE`,
`IGNORE_EXCEPTION_DETAIL`, `ALLOW_UNICODE`, `ALLOW_BYTES`, or `NUMBER` only
when their relaxed matching is appropriate. `doctest_namespace` can inject
shared names, and doctest examples can access a fixture with
`getfixture('tmp_path')`. Remember that pytest-specific helpers reduce
portability to the stdlib doctest runner.

Pytest can run an existing suite after installing the package in editable mode
(`pip install -e .` or the project's equivalent), which avoids fragile manual
`sys.path` changes. It collects `unittest.TestCase` classes and supports their
setup/teardown, skips, xfails, and (in current pytest) `subTest`. Ordinary
pytest fixtures, parametrization, and custom hooks do not become arguments or
features inside `TestCase` methods; migrate incrementally.

Xunit-style `setup_module`/`teardown_module`, `setup_class`/`teardown_class`,
`setup_method`/`teardown_method`, `setup_function`/`teardown_function` remain
supported, but fixtures are preferred for new code because dependencies and
cleanup are composable.

## 9. Plugins, hooks, and custom collection

Installed `pytest-*` plugins are normally auto-loaded. `pytest --trace-config`
shows what is active; `-p NAME` early-loads one and `-p no:NAME` disables one.
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` is useful for a minimal reproduction.
`pytest_plugins = (...)` can require a plugin from a test module or root
`conftest.py`; requiring plugins from nested `conftest.py` files is deprecated.

A local `conftest.py` is a plugin. Common hooks include:

```python
def pytest_addoption(parser):
    parser.addoption("--env", default="test")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--env") == "prod":
        for item in items:
            if "destructive" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="disabled in prod"))
```

Hook argument names are validated; omit arguments you do not need. Most hooks
should not raise arbitrary exceptions. `@pytest.hookimpl(tryfirst=True,
trylast=True)` controls ordering, while wrapper hooks are generator functions
that yield once around other implementations.

For reusable plugins, expose a `pytest11` entry point. Test plugin behavior with
the `pytester` fixture by creating a temporary test module/conftest, invoking
`pytester.runpytest(...)`, and checking `result.assert_outcomes(...)`.

Custom collection can support YAML, JSON, or another test language with
`pytest_collect_file`/`pytest_collect_directory`, `pytest.File`, `pytest.Item`,
and `pytest.Directory`. Implement `runtest`, `repr_failure`, and `reportinfo`
so collection, node IDs, verbose output, and failures remain understandable.
Use `--collect-only` while developing a collector.

## 10. Official examples worth reusing

The examples index demonstrates patterns that are easy to miss:

- **Basic customization:** default CLI options, custom CLI options and
  fixtures, conditional skip from a CLI flag, assertion helpers with
  `__tracebackhide__`, report headers, duration profiling, incremental test
  steps, package/directory fixtures, post-processing reports, fixture access to
  test reports, and `PYTEST_CURRENT_TEST`.
- **Parametrization:** CLI-controlled matrices, readable IDs from lists,
  functions, and `pytest.param`, plus dynamic generation.
- **Markers:** node-ID selection, `-k`, registration, module/class marks,
  per-case marks, marker arguments, platform marks, and reading marks from
  fixtures/hooks.
- **Collection:** custom naming/ignore rules, deselection, non-Python YAML
  files, and manifest-driven directory collectors.
- **Failure reporting:** use pytest's assertion introspection and verbosity
  levels (`-v`, `-vv`) to reveal the right amount of diff detail.

Do not copy an example's demo-only `assert 0`, deliberately failing tests, or
network-dependent fixture into production code. Adapt the mechanism and retain
the isolation and reporting idea.

## 11. Bash completion

When a team wants pytest option completion in bash, install `argcomplete` and
register it according to the environment:

```bash
eval "$(register-python-argcomplete pytest)"     # current shell
register-python-argcomplete pytest >> ~/.bashrc  # persistent user setup
```

Treat shell configuration as user/environment setup, not as part of a test
fixture or project test dependency.
