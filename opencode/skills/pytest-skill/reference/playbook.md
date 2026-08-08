# pytest — Advanced Implementation Playbook

## §1 — Production Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short -q
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks integration tests
    smoke: marks smoke tests
    api: marks API tests
filterwarnings =
    error
    ignore::DeprecationWarning
```

```toml
# pyproject.toml (alternative)
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --strict-markers --tb=short"
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
    "smoke: smoke tests",
]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## §2 — Fixtures (Scoping, Factories, Teardown)

```python
# conftest.py — shared fixtures
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Session-scoped: created once per test session
@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

# Function-scoped: created per test (default), auto-cleanup
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Factory fixture — create multiple instances
@pytest.fixture
def user_factory(db_session):
    created = []
    def _create_user(name="Test User", email=None, role="viewer"):
        email = email or f"{name.lower().replace(' ', '.')}@test.com"
        user = User(name=name, email=email, role=role)
        db_session.add(user)
        db_session.commit()
        created.append(user)
        return user
    yield _create_user
    for user in created:
        db_session.delete(user)
    db_session.commit()

# Autouse fixture — runs for every test in module
@pytest.fixture(autouse=True)
def reset_cache():
    cache.clear()
    yield
    cache.clear()

# tmp_path for file operations (built-in)
def test_writes_output(tmp_path):
    output_file = tmp_path / "result.json"
    generate_report(output_file)
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert data["status"] == "complete"
```

## §3 — Parameterized Tests

```python
import pytest

# Basic parametrize
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

# Multiple parameters with IDs
@pytest.mark.parametrize("email,valid", [
    ("user@test.com", True),
    ("invalid", False),
    ("", False),
    ("user@.com", False),
], ids=["valid_email", "no_at_sign", "empty", "missing_domain"])
def test_validate_email(email, valid):
    assert validate_email(email) == valid

# Combine parametrize (cartesian product)
@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
@pytest.mark.parametrize("resolution", ["1920x1080", "1366x768", "375x667"])
def test_responsive_layout(browser, resolution):
    assert render_page(browser, resolution).is_valid()

# Indirect parametrize (pass to fixture)
@pytest.fixture
def user(request):
    return create_user(role=request.param)

@pytest.mark.parametrize("user", ["admin", "editor", "viewer"], indirect=True)
def test_permissions(user):
    assert user.can_view()
```

## §4 — Mocking with pytest-mock

```python
# pip install pytest-mock

def test_send_email(mocker):
    mock_smtp = mocker.patch("myapp.email.smtplib.SMTP")
    send_email("test@example.com", "Hello", "Body")
    mock_smtp.return_value.sendmail.assert_called_once()

def test_api_call(mocker):
    mock_get = mocker.patch("myapp.api.requests.get")
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
    mock_get.return_value.status_code = 200
    user = get_user(1)
    assert user["name"] == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")

def test_database_error(mocker):
    mocker.patch("myapp.db.session.commit", side_effect=IntegrityError("duplicate"))
    with pytest.raises(DuplicateError):
        create_user("Alice", "alice@test.com")

# Spy — track calls without replacing
def test_logging(mocker):
    spy = mocker.spy(logger, "info")
    process_order(order)
    spy.assert_called_with("Order processed: %s", order.id)

# Mock environment variables
def test_config(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-123")
    monkeypatch.setenv("DEBUG", "true")
    config = load_config()
    assert config.api_key == "test-key-123"
    assert config.debug is True
```

## §5 — Async Testing

```python
# pip install pytest-asyncio

import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.example.com/data")
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_async_exception():
    with pytest.raises(ConnectionError):
        await fetch_data("https://invalid.example.com")

# Async fixtures
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) > 0
```

## §6 — Testing Exceptions & Warnings

```python
# Exception testing
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_error_message():
    with pytest.raises(ValueError, match=r".*invalid email.*"):
        validate_email("not-an-email")

def test_raises_with_info():
    with pytest.raises(PermissionError) as exc_info:
        delete_file("/protected/file.txt")
    assert "permission denied" in str(exc_info.value).lower()
    assert exc_info.value.errno == 13

# Warning testing
def test_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="use new_func"):
        old_func()
```

## §7 — Markers & Custom Plugins

```python
# Custom marker usage
@pytest.mark.slow
def test_full_data_processing():
    result = process_large_dataset()
    assert result.row_count > 1_000_000

@pytest.mark.integration
def test_database_connection():
    assert db.is_connected()

# Run by marker: pytest -m "not slow"
# Run by marker: pytest -m "smoke and not integration"

# Custom plugin — conftest.py
def pytest_collection_modifyitems(config, items):
    """Auto-mark tests in integration/ directory"""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

# Custom report header
def pytest_report_header(config):
    return f"Environment: {os.getenv('ENV', 'local')}"
```

## §8 — Class-Based Test Organization

```python
class TestUserService:
    @pytest.fixture(autouse=True)
    def setup(self, db_session, user_factory):
        self.db = db_session
        self.create_user = user_factory
        self.service = UserService(db_session)

    def test_create_user(self):
        user = self.service.create("Alice", "alice@test.com")
        assert user.id is not None
        assert user.name == "Alice"

    def test_find_by_email(self):
        self.create_user(name="Bob", email="bob@test.com")
        user = self.service.find_by_email("bob@test.com")
        assert user.name == "Bob"

    def test_delete_nonexistent(self):
        with pytest.raises(NotFoundError):
            self.service.delete(999)

    class TestPermissions:
        """Nested class for permission-related tests"""
        def test_admin_can_delete(self, user_factory):
            admin = user_factory(role="admin")
            assert admin.can_delete()

        def test_viewer_cannot_delete(self, user_factory):
            viewer = user_factory(role="viewer")
            assert not viewer.can_delete()
```

## §9 — CI/CD Integration

```yaml
# GitHub Actions
name: Python Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '${{ matrix.python-version }}' }
      - name: Install deps
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml --junitxml=results.xml -v
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with: { files: coverage.xml }
      - name: Upload results
        uses: actions/upload-artifact@v4
        if: always()
        with: { name: test-results-${{ matrix.python-version }}, path: results.xml }
```

## §10 — Debugging Quick-Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Fixture not found | Wrong scope or missing conftest.py | Check conftest.py location, fixture name |
| `ScopeMismatch` | Function fixture depends on session fixture | Match scope: session → module → function |
| Tests interfere | Shared mutable state | Use function-scoped fixtures, `autouse` cleanup |
| Parametrize fails | Wrong number of params | Ensure tuple count matches parameter names |
| Slow collection | Too many test paths | Set `testpaths` in pytest.ini |
| Async test hangs | Missing `@pytest.mark.asyncio` | Add marker or set `asyncio_mode = "auto"` |
| Coverage wrong | Source path mismatch | Set `source` in `[tool.coverage.run]` |
| Import errors | Missing `__init__.py` or bad path | Add `__init__.py` or use `src` layout with `--import-mode=importlib` |
| Monkeypatch not reverting | Using at module scope | Only use in function-scoped fixtures |
| Marker warnings | Marker not registered | Add to `markers` in pytest.ini |

## §11 — Best Practices Checklist

- ✅ Use fixtures over setup/teardown methods
- ✅ Use `conftest.py` for shared fixtures (auto-discovered)
- ✅ Use `tmp_path` for file operations (built-in, auto-cleanup)
- ✅ Use `monkeypatch` for env vars and attribute patching
- ✅ Use `pytest-mock` (mocker fixture) over `unittest.mock`
- ✅ Use `@pytest.mark.parametrize` for data-driven tests
- ✅ Register all custom markers in `pytest.ini`
- ✅ Use `--strict-markers` to catch typos in marker names
- ✅ Use `pytest-cov` for coverage with `--cov-fail-under=80`
- ✅ Use `pytest-xdist` for parallel execution: `pytest -n auto`
- ✅ Use `--tb=short` for concise tracebacks in CI
- ✅ Structure: `tests/unit/`, `tests/integration/`, `conftest.py`
- ✅ Name files `test_*.py` and functions `test_*`
- ✅ Use factory fixtures for creating test objects
- ✅ Use `pytest.raises(match=...)` for precise error checking

## §12 — Output Capture & CLI Testing

```python
# capsys — capture stdout/stderr at Python level (sys.stdout / sys.stderr)
def test_greeting(capsys):
    greet("Alice")
    captured = capsys.readouterr()          # namedtuple (out, err) — also resets the buffer
    assert captured.out == "Hello, Alice!\n"
    assert captured.err == ""

def test_logs_to_stderr(capsys):
    log_warning("disk full")
    assert "disk full" in capsys.readouterr().err

# capsysbinary — capture as bytes instead of str
def test_binary_output(capsysbinary):
    emit_bytes(b"\x00\x01")
    assert capsysbinary.readouterr().out == b"\x00\x01\n"

# capfd / capfdbinary — capture at OS file-descriptor level (fd 1/2)
# catches output from subprocesses, os.system(), and C extensions
def test_child_process_output(capfd):
    subprocess.run(["python", "-c", "print('from child')"], check=True)
    assert "from child" in capfd.readouterr().out

# Turn capture off inside a block (output goes straight to the terminal)
def test_partial_capture(capsys):
    print("captured")
    with capsys.disabled():
        print("not captured")
    print("captured again")

# subtests — run independent checks, each reported separately on failure
def test_calculator_ops(subtests):
    calc = Calculator()
    for a, b, expected in [(1, 2, 3), (2, 2, 4), (0, 0, 1)]:
        with subtests.test(a=a, b=b):
            assert calc.add(a, b) == expected
```

CLI notes:

| Flag | Effect |
|------|--------|
| `-s` | Shorthand for `--capture=no` (capture fixtures still take precedence) |
| `--capture={fd,sys,tee-sys,no}` | `fd` default (catches subprocess output), `tee-sys` captures *and* passes through |
| `--show-capture={no,stdout,stderr,log,all}` | What captured output failed tests display (default `all`) |
| `--pastebin={failed,all}` | Upload failure output to a pastebin service |

## §13 — Monkeypatch Deep Dive

```python
# Patch attributes — dotted strings work; patch WHERE the code looks it up
def test_getcwd(monkeypatch):
    monkeypatch.setattr("os.getcwd", lambda: "/fake/dir")
    assert os.getcwd() == "/fake/dir"

# Freeze time — patch the name the module under test imports
# myapp/expiry.py uses:  datetime.datetime.now()
def test_never_expires(monkeypatch):
    class FakeDateTime(datetime.datetime):
        @classmethod
        def now(cls):
            return cls(2099, 1, 1)
    monkeypatch.setattr("myapp.expiry.datetime", FakeDateTime)
    assert token_expires_never() is True

# Environment variables
def test_config_from_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("API_KEY", "test-key", prepend="test-")  # prefix the value
    monkeypatch.delenv("SMTP_HOST", raising=False)              # don't fail if absent
    assert load_config().api_key == "test-key"

# Dicts, cwd, sys.path
def test_config_dict(monkeypatch):
    monkeypatch.setitem(CONFIG, "retries", 3)
    monkeypatch.delitem(CONFIG, "deprecated_flag", raising=False)

def test_build_paths(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)                 # change cwd for the duration of the test
    assert Path.cwd() == tmp_path

def test_import_from_src(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(tmp_path)) # prepend to sys.path (also invalidates caches)

# Standalone use outside fixtures
def test_manual_patch():
    with MonkeyPatch.context() as mp:
        mp.setattr("os.getcwd", lambda: "/fake")
        assert os.getcwd() == "/fake"
```

Rules of thumb:

- Patch the name the **code under test** uses (`myapp.service.requests.get`), not the upstream module — same rule as `unittest.mock`.
- All patches are auto-undone at test end (fixture teardown).
- Use `raising=False` when the target may not exist yet.
- Prefer function-scoped `monkeypatch`; module/session scopes keep changes for longer.

## §14 — Skips, Xfails & Conditional Tests

```python
# Unconditional and conditional skips
@pytest.mark.skip(reason="not implemented yet")
def test_future_feature(): ...

@pytest.mark.skipif(sys.version_info < (3, 11), reason="needs 3.11+")
def test_new_syntax(): ...

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
def test_unix_permissions(): ...

# Module- or class-level: applies to every test below it
pytestmark = pytest.mark.skipif(not HAS_DOCKER, reason="requires Docker")

# Imperative skip inside a test
def test_expensive_db():
    if not db_available():
        pytest.skip("database not running")

# Skip the whole module at collection time
pytest.skip("requires Windows", allow_module_level=True)

# Skip when an optional dependency is missing
docutils = pytest.importorskip("docutils", minversion="0.19")

# Xfail — expected failure, no traceback, listed as XFAIL/XPASS
@pytest.mark.xfail(reason="known bug #1234")
def test_known_bug(): ...

@pytest.mark.xfail(sys.version_info < (3, 11), reason="fixed in 3.11")
def test_legacy_behavior(): ...

@pytest.mark.xfail(raises=NotImplementedError, reason="TODO")
def test_unfinished(): ...

@pytest.mark.xfail(run=False, reason="crashes the interpreter")
def test_crashy(): ...

# strict=True: XPASS (test unexpectedly passes) FAILS the suite — use in CI
@pytest.mark.xfail(strict=True, reason="must fix before release")
def test_should_fail(): ...

# Marks inside parametrize
@pytest.mark.parametrize("value,expected", [
    (1, 1),
    pytest.param(2, 3, marks=pytest.mark.xfail(reason="known bug")),
    pytest.param(0, 0, id="zero"),
])
def test_add(value, expected): ...

# Imperative xfail — stops execution immediately
def test_platform_only():
    if sys.platform != "linux":
        pytest.xfail("only meaningful on Linux")
```

Reporting: `-rs` (skip reasons), `-rx` (xfail reasons), `-rX` (xpass reasons), `-rxXs` (all three). Global strict default via ini: `xfail_strict = true` (alias `strict_xfail`).

## §15 — Warnings & Logging

```ini
# pytest.ini — warnings policy
filterwarnings =
    error                        # promote warnings to errors
    ignore::DeprecationWarning
    ignore:.*legacy API.*:UserWarning:myapp\.legacy
    always::ResourceWarning
```

Filter format: `action:message:category:module:lineno` — `message` is a regex matched case-insensitively; **last matching filter wins**.

```python
# Per-test / per-module overrides (beat CLI and ini filters)
@pytest.mark.filterwarnings("error")
def test_no_warnings_allowed(): ...

@pytest.mark.filterwarnings("ignore:.*deprecated.*:DeprecationWarning")
def test_legacy_calls(): ...

pytestmark = pytest.mark.filterwarnings("error")

# Assert a warning is emitted
def test_deprecation():
    with pytest.warns(DeprecationWarning, match="use new_func"):
        old_func()

# Inspect all warnings with the recwarn fixture
def test_noise(recwarn):
    noisy_function()
    assert len(recwarn) == 2
    assert all(w.category is UserWarning for w in recwarn)

# CLI: fail the suite when warnings exceed a threshold
# pytest --max-warnings=20
```

```python
# caplog — capture and assert on log records
def test_logging(caplog):
    process_order(order)
    assert "Order processed" in caplog.text
    assert any(r.levelname == "INFO" for r in caplog.records)
    assert ("myapp.orders", logging.INFO, "Order processed: 42") in caplog.record_tuples

def test_log_levels(caplog):
    with caplog.at_level(logging.DEBUG):      # raise verbosity for a block
        debug_trace()
    caplog.set_level(logging.WARNING, logger="myapp.noisy")  # silence one logger
    caplog.clear()                            # reset between phases
```

```ini
# Live logging to the console and a file
log_cli = true
log_cli_level = DEBUG
log_cli_format = %(levelname)-8s %(name)s %(message)s
log_file = logs/tests.log
log_file_mode = w
log_file_level = DEBUG
```

CLI: `--log-cli-level=DEBUG`, `--log-file=tests.log`, `--log-file-mode=a`.

## §16 — Cache & Re-run Workflows

```bash
pytest --lf                 # re-run only the last run's failures (full suite if none)
pytest --ff                 # run everything, last failures first
pytest --nf                 # run files by mtime, newest first
pytest --sw                 # stepwise: stop at first failure; next run resumes after it
pytest --sw-skip            # skip the first failing test, stop at the second
pytest --lfnf=none          # with --lf: exit 0 (message) when nothing failed
pytest --cache-clear        # wipe the cache before running — recommended for CI
pytest --cache-show         # inspect cache contents (no collection)
pytest -p no:cacheprovider  # disable caching entirely
```

- Cache lives at `rootdir/.pytest_cache` (configurable via ini `cache_dir`).
- Survives across runs, so CI should start with `--cache-clear` to avoid stale state.

```python
# Programmatic cache — persist state between runs
def test_counter(pytestconfig):
    cache = pytestconfig.cache
    count = cache.get("myapp/count", 0)
    cache.set("myapp/count", count + 1)
```

## §17 — Selecting & Introspecting Tests

```bash
# Node IDs: file, class, method, parametrized instance
pytest tests/test_mod.py
pytest tests/test_mod.py::test_func
pytest tests/test_mod.py::TestClass::test_method
pytest 'tests/test_mod.py::test_func[x1,y2]'    # quote [ ] on Windows shells

# Read selection from a file (one entry per line)
pytest @tests_to_run.txt

# -k: substring expression over test names (Python operators)
pytest -k "MyClass and not method"
pytest -k "test_login or test_logout"
pytest -k "not slow"

# -m: marker expressions (and / or / not), marker args supported
pytest -m "slow"
pytest -m "smoke and not integration"
pytest -m "slow(phase=1)"
```

Introspection without running tests:

```bash
pytest --collect-only -q     # list all collected tests
pytest --fixtures            # show available fixtures (use -v for hidden ones)
pytest --markers             # show all registered markers
pytest --setup-show          # show fixture setup/teardown order per test
pytest --setup-plan          # dry-run: show the plan without executing
pytest --durations=10        # slowest 10 tests (--durations-min=0.005 default cutoff)
pytest -ra                   # summary of all non-passed results (default is 'fE')
```

`-r` chars: `f` failed · `E` error · `s` skipped · `x` xfailed · `X` xpassed · `p` passed · `P` passed with output · `a` all except passed · `A` all · `w` warnings (on by default).

## §18 — Debugging Failures

```bash
pytest -x --pdb                      # stop and drop into pdb on the first failure
pytest --maxfail=3                   # stop after 3 failures
pytest --pdb                         # pdb on every failure
pytest --trace                       # pdb at the start of every test
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb   # use ipdb
pytest -l                            # --showlocals: locals in tracebacks
pytest --tb=line                     # one line per failure
pytest --tb=short                    # concise (common CI default)
pytest --tb=native                   # stdlib formatting
pytest --full-trace                  # never cut tracebacks; also shows where Ctrl+C hit
pytest --durations=10                # find the slow tests first
pytest --no-header --no-summary      # minimal output
```

- `breakpoint()` in test code drops into pytest's PDB (capture is suspended while in the debugger).
- After a failure, `sys.last_value` / `sys.last_traceback` hold the exception for post-mortem debugging.
- `faulthandler_timeout = 60` in ini dumps all-thread tracebacks when a test hangs.

Assertion rewriting & custom failure messages:

```python
# conftest.py — better diffs for your own types
def pytest_assertrepr_compare(op, left, right):
    if op == "==" and isinstance(left, str) and isinstance(right, str):
        return ["strings differ:", f"  left:  {left!r}", f"  right: {right!r}"]

# Root conftest — rewrite asserts in non-test helper modules
pytest.register_assert_rewrite("myapp.helpers")

# Disable rewriting for one module: put PYTEST_DONT_REWRITE in its docstring
# Global opt-out: pytest --assert=plain
```

## §19 — Assertions Reference

```python
# pytest.approx — floating point and structured comparisons
assert 0.1 + 0.2 == pytest.approx(0.3)                  # rel=1e-6 default
assert 3.14159 == pytest.approx(3.14, rel=1e-2)
assert 1_000_000 == pytest.approx(1_000_100, abs=500)   # abs-only: rel ignored
assert {"price": 9.99} == pytest.approx({"price": 10.0}, abs=0.1)   # dicts (same keys)
assert [1.0, 2.0] == pytest.approx([1.0001, 2.0])       # sequences
assert np.array([1.0, 2.0]) == pytest.approx(np.array([1.0, 2.0001]))  # NumPy
assert dt == pytest.approx(dt + timedelta(milliseconds=500),
                           abs=timedelta(seconds=1))    # datetime (rel unsupported)
# nan_ok=True lets NaN compare equal to NaN

# pytest.fail — explicit failure with message
def test_state():
    if not is_valid():
        pytest.fail(f"invalid state: {state!r}")

# pytest.raises — multiple types, message regex, and exc_info
def test_parse_errors():
    with pytest.raises((ValueError, TypeError), match="invalid"):
        parse("not-a-json")

def test_exc_info():
    with pytest.raises(ValueError) as exc_info:
        parse("")
    assert exc_info.type is ValueError
    assert "invalid" in str(exc_info.value)

# check= — custom predicate on the exception (recent pytest)
def test_check():
    with pytest.raises(ValueError, check=lambda e: e.args == ("bad input",)):
        parse("")

# Exception groups
def test_exception_group():
    with pytest.RaisesGroup(ValueError, TypeError):
        raise ExceptionGroup("batch", [ValueError("a"), TypeError("b")])

# pytest.warns / deprecated_call
def test_warnings():
    with pytest.warns(DeprecationWarning, match="use new"):
        old_api()
    with pytest.deprecated_call():
        legacy()

# Anti-pattern: never assert on the broad `Exception` class
```

## §20 — Advanced Fixture Mechanics

```python
# The request object — introspection and dynamic behavior
@pytest.fixture
def user(request):
    if hasattr(request, "param"):          # set by fixture params / indirect parametrize
        return make_user(role=request.param)
    return make_user()

@pytest.fixture
def test_context(request):
    return {
        "name": request.node.name,         # current test name
        "module": request.module,          # the module under test
        "cls": request.cls,                # test class (or None)
        "env": request.config.getoption("--env"),      # CLI options
    }

# Teardown via addfinalizer (yield alternative, fires even on errors)
@pytest.fixture
def tmp_config(tmp_path, request):
    cfg = tmp_path / "app.toml"
    cfg.write_text("[app]\ndebug = true")
    request.addfinalizer(lambda: cfg.unlink(missing_ok=True))
    return cfg

# usefixtures — apply fixtures without naming them as arguments
@pytest.mark.usefixtures("reset_state")
def test_side_effects(): ...

# Module-level equivalent
pytestmark = pytest.mark.usefixtures("reset_state")

# Dynamic scope from a callable
def big_scope(fixture_name, config):
    return "session" if config.getoption("--integration") else "function"

@pytest.fixture(scope=big_scope)
def expensive_setup(): ...

# Fixture params — one run per value (with readable ids)
@pytest.fixture(params=["sqlite", "postgres"], ids=["lite", "pg"])
def database(request):
    db = connect(request.param)
    yield db
    db.close()

# Instantiation order: scope (session → module → class → function) → dependencies → autouse.
# Overriding: parametrizing a test argument OVERRIDES the fixture of that name.
@pytest.mark.parametrize("username", ["admin", "root"])   # beats the username fixture
def test_login(username): ...
```

## §21 — Exit Codes & CI Automation

| Code | Meaning |
|------|---------|
| 0 | All collected tests passed |
| 1 | Tests failed |
| 2 | Interrupted by user (Ctrl+C / KeyboardInterrupt) |
| 3 | Internal error during execution |
| 4 | Command-line usage error |
| 5 | No tests collected |
| 6 | Warnings exceeded `--max-warnings=N` (no test failures) |

```python
from pytest import ExitCode          # enum: OK, TESTS_FAILED, INTERRUPTED, ...
code = pytest.main(["-x", "tests"])  # returns the exit code (no SystemExit)
```

Environment variables:

| Var | Effect |
|-----|--------|
| `PYTEST_ADDOPTS="--tb=short -ra"` | Extra options applied to every run (respects `-o` overrides) |
| `PYTEST_PLUGINS=plugin_a,plugin_b` | Force-load plugins without `-p` |
| `CI` / `BUILD_NUMBER` | CI detection: disables output truncation |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` | Only load builtin + explicitly requested plugins |
| `PYTEST_DEBUG_TEMPROOT=/path` | Override the base temp directory |

CI recipe: `pytest --cache-clear --junitxml=results.xml --cov=src --cov-report=xml --cov-fail-under=80 -ra`.

## §22 — Configuration Reference

Config file precedence — **first match wins, files are never merged**:

1. `pytest.toml` / `.pytest.toml` (newer pytest)
2. `pytest.ini` / `.pytest.ini`
3. `pyproject.toml` — `[tool.pytest]` (native TOML) or `[tool.pytest.ini_options]`
4. `tox.ini` — `[pytest]` section
5. `setup.cfg` — `[tool:pytest]` section (discouraged)

Force a file with `-c FILE`; override any ini key with `-o key=value` (repeatable).

| ini key | Purpose |
|---------|---------|
| `testpaths` | Default dirs to scan when no args given |
| `python_files` / `python_classes` / `python_functions` | Discovery patterns |
| `norecursedirs` | Skip dirs during collection |
| `addopts` | Default CLI flags for every run |
| `markers` | Register custom markers (with descriptions) |
| `filterwarnings` | Warning policy (see §15) |
| `usefixtures` | Apply fixtures to every test |
| `minversion` | Minimum pytest version required to run |
| `required_plugins` | Comma-separated plugins that must be installed |
| `pythonpath = ["src"]` | Add dirs to `sys.path` (src layout) |
| `xfail_strict = true` | Global strict xfail (alias `strict_xfail`) |
| `log_cli` / `log_cli_level` / `log_file` | Logging (see §15) |
| `cache_dir` | Location of `.pytest_cache` |
| `tmp_path_retention_count` / `tmp_path_retention_policy` | Keep `all` / `failed` / `none` tmp dirs (count = how many runs) |
| `empty_parameter_set_mark` | `skip` (default) / `xfail` / `fail_at_collect` for empty parametrize |
| `doctest_optionflags` | Doctest behavior (see §23) |
| `consider_namespace_packages` | Collect PEP 420 namespace packages |
| `console_output_style` | `progress` (default) / `classic` / `count` |
| `faulthandler_timeout` | Dump thread stacks after N seconds |

Import modes (`--import-mode={prepend,append,importlib}`, default `prepend`):

- `prepend` — insert the test dir at the front of `sys.path`; test files must have globally unique names unless packages use `__init__.py`.
- `append` — same, but appended at the end (tests run against installed versions).
- `importlib` — never touches `sys.path`; recommended for `src` layouts and new projects.

## §23 — Doctests

```bash
pytest --doctest-modules               # run doctests inside .py docstrings
pytest --doctest-glob="*.rst"          # extra text-file patterns (test*.txt default)
pytest --doctest-continue-on-failure   # report every failing example, not just the first
pytest --doctest-report=ndiff          # diff style: none|cdiff|ndiff|udiff|only_first_failure
```

```ini
# pytest.ini
doctest_optionflags = NORMALIZE_WHITESPACE ALLOW_UNICODE ALLOW_BYTES
```

```python
def add(a, b):
    """
    >>> add(2, 3)
    5
    >>> add(-1, 1)          # doctest: +SKIP
    0
    """
    return a + b
```

- `NORMALIZE_WHITESPACE` tolerates spacing differences; `ALLOW_UNICODE` / `ALLOW_BYTES` strip the `u` / `b` prefixes.
- Use `getfixture` inside doctest examples: `>>> path = getfixture('tmp_path')`.
- Inject names into doctests via the `doctest_namespace` fixture:

```python
# conftest.py
@pytest.fixture(autouse=True)
def add_numpy_to_doctests(doctest_namespace):
    doctest_namespace["np"] = numpy
```

## §24 — Plugin Ecosystem

| Plugin | Install | Purpose |
|--------|---------|---------|
| pytest-cov | `pip install pytest-cov` | Coverage: `--cov=src --cov-report=term-missing --cov-fail-under=80` |
| pytest-xdist | `pip install pytest-xdist` | Parallel: `-n auto` (physical cores), `-n logical` (needs psutil), `--dist loadscope/loadfile/worksteal` |
| pytest-mock | `pip install pytest-mock` | `mocker` fixture (see §4) |
| pytest-asyncio | `pip install pytest-asyncio` | Async tests, `asyncio_mode = auto` (see §5) |
| pytest-timeout | `pip install pytest-timeout` | `@pytest.mark.timeout(5)` — kill hanging tests |
| pytest-randomly | `pip install pytest-randomly` | Randomize order with a reproducible seed |
| pytest-sugar | `pip install pytest-sugar` | Progress bar + nicer failure output |
| pytest-instafail | `pip install pytest-instafail` | Show failures the moment they happen |
| pytest-html | `pip install pytest-html` | `--html=report.html` self-contained report |
| pytest-rerunfailures | `pip install pytest-rerunfailures` | `@pytest.mark.flaky(reruns=2)` retry flaky tests |
| pytest-playwright | `pip install pytest-playwright` | End-to-end browser tests with Playwright |
| pytest-django | `pip install pytest-django` | Django test integration |
| pytest-benchmark | `pip install pytest-benchmark` | Performance benchmarks with statistics |
| pytest-socket | `pip install pytest-socket` | Block all network access in tests |
| pytest-check | `pip install pytest-check` | Multiple assertions per test, all reported |
| pytest-bdd | `pip install pytest-bdd` | Behavior-driven tests from Gherkin features |
| pytest-ordering | `pip install pytest-ordering` | `@pytest.mark.order(1)` explicit ordering |

Plugin loading notes:

- Disable any plugin: `-p no:NAME` (works for builtins too, e.g. `-p no:cacheprovider`, `-p no:doctest`, `-p no:legacypath`).
- `--disable-plugin-autoload` — only builtin + `-p`-requested plugins.
- `pytest --trace-config` — debug which plugins/conftests were loaded and why.
- Installable plugins expose an entry point:

```toml
# pyproject.toml of your plugin package
[project.entry-points.pytest11]
myplugin = "myplugin.plugin"
```
