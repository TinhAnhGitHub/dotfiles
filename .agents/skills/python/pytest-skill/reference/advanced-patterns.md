# Pytest — Advanced Patterns & Architecture

## 1. Strongly-Typed Fixture Factories

Avoid returning weakly-typed dictionaries or unannotated lambdas. Use
`typing.Protocol` or `collections.abc.Callable` so tests get full IDE
autocompletion, static type checking (mypy/pyright), and deterministic cleanup
registered via `request.addfinalizer`.

```python
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol
import pytest


@dataclass
class User:
    id: int
    name: str
    email: str
    role: str


class UserFactory(Protocol):
    def __call__(
        self,
        name: str = "Test User",
        email: str | None = None,
        role: str = "viewer",
    ) -> User: ...


@pytest.fixture
def make_user(request: pytest.FixtureRequest) -> UserFactory:
    created: list[User] = []
    counter = 0

    def _factory(
        name: str = "Test User",
        email: str | None = None,
        role: str = "viewer",
    ) -> User:
        nonlocal counter
        counter += 1
        user = User(
            id=counter,
            name=name,
            email=email or f"user{counter}@example.com",
            role=role,
        )
        created.append(user)
        return user

    def cleanup() -> None:
        # Perform real external teardown here (database deletions, remote calls)
        created.clear()

    request.addfinalizer(cleanup)
    return _factory


class TestUserWorkflow:
    def test_creates_distinct_users(self, make_user: UserFactory) -> None:
        admin = make_user(name="Alice", role="admin")
        viewer = make_user(name="Bob")

        assert admin.id != viewer.id
        assert admin.role == "admin"
        assert viewer.role == "viewer"
```

## 2. Database Savepoint Rollback Pattern (SQLAlchemy 2.0+)

The transactional rollback pattern provides test isolation without dropping and
recreating tables between tests. In SQLAlchemy 2.0+, `join_transaction_mode="create_savepoint"`
intercepts inner `session.commit()` calls made by application code: they commit only to
the savepoint, while the fixture's outer transaction rolls everything back at test end.

### Synchronous Pattern

```python
from collections.abc import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from myapp.models import Base


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("postgresql+psycopg://user:pass@localhost:5432/test_db")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    # Begin outer non-ORM transaction
    outer_tx = connection.begin()
    
    # Bind session to connection; any internal commit becomes a SAVEPOINT
    SessionMaker = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")
    session = SessionMaker()

    yield session

    session.close()
    outer_tx.rollback()
    connection.close()
```

### Asynchronous Pattern (`ext.asyncio`)

```python
from collections.abc import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from myapp.models import Base


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_engine():
    engine = create_async_engine("postgresql+asyncpg://user:pass@localhost:5432/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def async_db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    async with async_engine.connect() as conn:
        outer_tx = await conn.begin()
        session_factory = async_sessionmaker(
            bind=conn,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        async with session_factory() as session:
            yield session
        await outer_tx.rollback()
```

## 3. Parametrized Fixtures and Indirect Routing

```python
# Parameterized fixture
@pytest.fixture(params=["sqlite", "postgres"])
def database(request):
    db = connect(request.param)
    yield db
    db.close()

# Fixture with indirect parametrize
@pytest.fixture
def http_client(request):
    timeout = getattr(request, 'param', 30)
    return HttpClient(timeout=timeout)

@pytest.mark.parametrize("http_client", [5, 10, 30], indirect=True)
def test_with_different_timeouts(http_client):
    assert http_client.timeout in (5, 10, 30)
```

## Advanced Parametrize

```python
# Matrix parametrize
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    assert x * y > 0  # Generates 4 tests: (1,10), (1,20), (2,10), (2,20)

# Conditional skip
@pytest.mark.parametrize("browser", [
    "chrome",
    "firefox",
    pytest.param("safari", marks=pytest.mark.skipif(sys.platform != "darwin", reason="macOS only"))
])
def test_browser(browser): pass

# ID customization
@pytest.mark.parametrize("input,expected", [
    pytest.param("hello", 5, id="simple-word"),
    pytest.param("", 0, id="empty-string"),
    pytest.param("a b c", 5, id="with-spaces"),
])
def test_length(input, expected):
    assert len(input) == expected
```

## Mocking Patterns

```python
# Patch decorator
@patch("myapp.services.requests.get")
def test_fetch_user(mock_get):
    mock_get.return_value.json.return_value = {"id": 1, "name": "Alice"}
    mock_get.return_value.status_code = 200
    user = fetch_user(1)
    assert user.name == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")

# Context manager patch
def test_with_context():
    with patch("myapp.db.Session") as MockSession:
        session = MockSession.return_value.__enter__.return_value
        session.query.return_value.first.return_value = User(id=1)
        result = get_user(1)
        assert result.id == 1

# Async mocking
@pytest.mark.asyncio
async def test_async_service():
    with patch("myapp.client.fetch", new_callable=AsyncMock) as mock:
        mock.return_value = {"data": "test"}
        result = await process_data()
        assert result == "test"

# Mock property
def test_property():
    with patch.object(type(obj), 'prop', new_callable=PropertyMock, return_value=42):
        assert obj.prop == 42
```

## Plugin Ecosystem

```python
# conftest.py — production-grade
import pytest

def pytest_addoption(parser):
    parser.addoption("--env", default="test", choices=["test", "staging", "prod"])

@pytest.fixture
def env(request):
    return request.config.getoption("--env")

def pytest_collection_modifyitems(config, items):
    """Auto-mark slow tests, skip them unless --runslow."""
    if not config.getoption("--runslow", default=False):
        skip_slow = pytest.mark.skip(reason="use --runslow to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

# Custom marker
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
```

## Configuration

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-ra",                    # Show summary of all non-passing
    "--strict-markers",       # Error on unknown markers
    "--strict-config",        # Error on config issues
    "-x",                     # Stop on first failure
    "--tb=short",             # Short traceback
    "--cov=src",              # Coverage for src/
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
    "e2e: end-to-end tests",
]
filterwarnings = ["error", "ignore::DeprecationWarning"]
```

## Modern Async Testing (`pytest-asyncio` 0.24+)

Older versions of `pytest-asyncio` relied on an implicit, global `event_loop`
fixture that frequently triggered `RuntimeError: got Future attached to a different loop`.

Modern `pytest-asyncio` (0.24+) introduces explicit loop scoping. Configure
default scopes in `pyproject.toml` and align fixture and test loop scopes:

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
asyncio_default_test_loop_scope = "function"
```

### Async Fixture Lifecycle and Shared Scope

```python
import pytest
from httpx import ASGITransport, AsyncClient
from myapp.asgi import app


# Function-scoped async fixture (matches test default)
@pytest.fixture
async def api_client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


# If a fixture is session-scoped, its loop_scope MUST also be session:
@pytest.fixture(scope="session", loop_scope="session")
async def shared_redis():
    client = await init_redis()
    yield client
    await client.aclose()


class TestAsyncAPI:
    async def test_create_order(self, api_client: AsyncClient) -> None:
        response = await api_client.post("/orders", json={"item": "book", "qty": 1})
        assert response.status_code == 201
        assert response.json()["status"] == "confirmed"
```

### Testing `asyncio.TaskGroup` and Cancellation

```python
import asyncio
import pytest
from pytest import RaisesGroup, RaisesExc


async def failing_worker(task_id: int):
    await asyncio.sleep(0.01)
    if task_id == 1:
        raise ValueError("task 1 failed")
    if task_id == 2:
        raise KeyError("task 2 failed")


class TestConcurrentTaskGroups:
    async def test_handles_taskgroup_exceptions(self):
        with pytest.RaisesGroup(RaisesExc(ValueError), RaisesExc(KeyError)):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(failing_worker(1))
                tg.create_task(failing_worker(2))
```

## Deterministic Time Control (`time-machine`)

`freezegun` works by monkeypatching standard Python library imports at runtime.
This incurs $O(N)$ module-search overhead on every test and often fails when
functions cache references to `datetime.now()` (e.g. in default parameter values).

**`time-machine`** operates via C-level interception of the system clock. It
runs in constant $O(1)$ time, never leaks between tests, and intercepts
pre-cached C-level references.

```python
from datetime import datetime, timedelta, timezone
import pytest


def get_token_expiry(hours_valid: int = 24) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours_valid)


class TestTimeSensitiveToken:
    def test_expiry_generation(self, time_machine):
        # Freeze clock deterministically (tick=False prevents time from progressing)
        frozen_instant = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        time_machine.move_to(frozen_instant, tick=False)

        assert datetime.now(timezone.utc) == frozen_instant

        expiry = get_token_expiry(hours_valid=2)
        assert expiry == datetime(2026, 1, 15, 14, 0, 0, tzinfo=timezone.utc)

        # Fast-forward clock to verify expiration check
        time_machine.shift(timedelta(hours=3))
        assert datetime.now(timezone.utc) > expiry
```

## Property-Based Testing (`hypothesis`)

Example-based tests (`assert add(1, 2) == 3`) only verify scenarios the developer
anticipated. **Hypothesis** fuzzed inputs against mathematical and behavioral
invariants, automatically finding edge cases (Unicode characters, null bytes,
integer overflow, empty strings) and *shrinking* failures to the minimal reproducible case.

```python
import pytest
from hypothesis import given, assume, strategies as st
from myapp.codec import compress, decompress, parse_user_input


class TestInvariants:
    # 1. Round-trip invariant: decompress(compress(x)) == x
    @given(st.binary(min_size=0, max_size=10_000))
    def test_compression_roundtrip(self, data: bytes) -> None:
        compressed = compress(data)
        decompressed = decompress(compressed)
        assert decompressed == data

    # 2. Input filtering with assume()
    @given(st.text(min_size=1, max_size=100))
    def test_username_sanitization(self, username: str) -> None:
        assume(not username.isspace())  # Skip inputs that do not meet preconditions
        result = parse_user_input(username)
        assert len(result) > 0
        assert not result.startswith(" ")
```

## Snapshot Testing (`syrupy` and `inline-snapshot`)

Snapshot testing captures large, structured outputs (API JSON, ASTs, SQL strings,
HTML templates) and asserts against an external golden master file without
writing repetitive assertions.

### Syrupy (External Snapshot Files)

```bash
pip install syrupy
pytest --snapshot-update   # Regenerate snapshot files when changes are intentional
```

```python
import re
from uuid import UUID
import pytest


def sanitize_payload(payload: dict) -> dict:
    """Sanitize volatile fields before snapshot comparison."""
    copy = payload.copy()
    if "created_at" in copy:
        copy["created_at"] = "<TIMESTAMP>"
    if "id" in copy:
        copy["id"] = "<UUID>"
    return copy


class TestOrderSerialization:
    def test_order_schema_matches_snapshot(self, snapshot, order_service):
        result = order_service.build_order_payload(customer_id="cust-123")
        # syrupy creates and checks __snapshots__/test_order.ambr
        assert sanitize_payload(result) == snapshot
```

### Inline Snapshots (`inline-snapshot`)

`inline-snapshot` writes the expected result directly back into your test file
upon running `pytest --inline-snapshot=create`:

```python
from inline_snapshot import snapshot


def test_calculation():
    # Running pytest --inline-snapshot=create automatically fills snapshot(...) with actual output
    assert calculate_summary([10, 20, 30]) == snapshot(
        {"count": 3, "mean": 20.0, "total": 60}
    )
```

## Parallel Execution & Multi-Worker Isolation (`pytest-xdist`)

Running tests across multiple CPU cores (`pytest -n auto`) introduces worker race
conditions on databases, caches, and files.

### Dynamic Resource Isolation per Worker

Pytest-xdist provides the `worker_id` fixture (`gw0`, `gw1`, or `master` when single-threaded):

```python
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def database_url(worker_id: str) -> str:
    # Give each worker process its own isolated database schema or database
    if worker_id == "master":
        return "postgresql://user:pass@localhost:5432/test_db_master"
    return f"postgresql://user:pass@localhost:5432/test_db_{worker_id}"
```

### Shared Initialization with File Locking (`filelock`)

When an expensive operation (such as migrations or downloading a model) must run
only once across all xdist workers:

```python
from pathlib import Path
from filelock import FileLock
import pytest


@pytest.fixture(scope="session", autouse=True)
def run_migrations_once(tmp_path_factory, worker_id):
    if worker_id == "master":
        # Single-worker run: run directly
        execute_migrations()
        return

    # Multi-worker run: lock across processes
    root_tmp = tmp_path_factory.getbasetemp().parent
    lock_file = root_tmp / "migrations.lock"
    flag_file = root_tmp / "migrations.done"

    with FileLock(str(lock_file)):
        if not flag_file.exists():
            execute_migrations()
            flag_file.write_text("done")
```

### Distribution Strategies

- `--dist=load`: Default round-robin by test function.
- `--dist=loadscope`: Groups tests by module or test class on the same worker.
  Essential for tests sharing class- or module-scoped transactional setups.
- `--dist=loadfile`: Ensures all tests in a file run on the same worker process.

## Hermetic Network Isolation (`pytest-socket`)

Prevent accidental network leakage in unit test suites (e.g. third-party API
calls, analytics tracking, unintended cloud resource hits):

```bash
pip install pytest-socket
pytest --disable-socket
```

```python
import pytest
import requests


class TestHermeticity:
    def test_disallows_unmocked_http(self):
        # Fails immediately with SocketBlockedError
        with pytest.raises(Exception):
            requests.get("https://api.github.com")

    @pytest.mark.enable_socket
    def test_explicit_integration_call(self):
        # Explicitly opted-in network access for integration tests
        resp = requests.get("https://httpbin.org/status/200")
        assert resp.status_code == 200
```

## Anti-Patterns

- ❌ `assert True` or `assert result` without checking specific values
- ❌ `@pytest.fixture(autouse=True)` at module scope — hidden side effects
- ❌ Fixtures that do too much — split into focused, composable fixtures
- ❌ Hardcoded test data paths — use `tmp_path` fixture
- ❌ `time.sleep()` in tests — use `pytest-timeout` and mock time
- ❌ Catching exceptions in test code — let pytest handle assertion errors

## Dynamic Parametrization (pytest_generate_tests)

Generate parametrization at collection time — useful when the parameter space
comes from data, config, or external sources rather than literals.

```python
# conftest.py — generate cases from a data file
def pytest_generate_tests(metafunc):
    if "dataset" in metafunc.fixturenames:
        rows = load_cases_from_yaml("cases.yaml")
        metafunc.parametrize("dataset", rows, ids=[r["id"] for r in rows])

# Multiple fixtures driven from one data source
def pytest_generate_tests(metafunc):
    if {"username", "password"} <= set(metafunc.fixturenames):
        creds = load_credentials()
        metafunc.parametrize(
            "username,password",
            [(c["user"], c["pass"]) for c in creds],
            ids=[c["name"] for c in creds],
        )

# Scope the generated fixture so it is created once per session
def pytest_generate_tests(metafunc):
    if "lang" in metafunc.fixturenames:
        metafunc.parametrize("lang", ["en", "de", "fr"], scope="session")
```

## Fixture Override & Composition

Fixtures are looked up upward through conftest scopes; **the first one found
wins**. Override an upstream fixture by redefining it in a closer conftest.py,
or per-test via direct parametrization:

```python
# tests/unit/conftest.py — override the app-level db fixture for unit tests
@pytest.fixture
def db():
    return InMemoryDB()

# Per-test override: parametrizing the argument name beats the fixture
@pytest.mark.parametrize("username", ["admin", "banned_user"])
def test_login(username, db):
    ...
```

Compose fixtures by depending on other fixtures — never call them directly.
For programmatic access at runtime, use `request.getfixturevalue`:

```python
@pytest.fixture
def api_client(request):
    backend = request.getfixturevalue(f"{request.param}_backend")
    return APIClient(backend=backend)
```

## request Object Power-User Patterns

```python
@pytest.fixture
def current_user(request):
    # Marker-driven behavior
    marks = [m for m in request.node.iter_markers()]
    if any(m.name == "admin" for m in marks):
        return make_admin()
    return make_user()

def test_something(request):
    # Fixture values on demand
    session = request.getfixturevalue("db_session")
    # CLI options from conftest-registered flags
    env = request.config.getoption("--env")
    # Test metadata
    test_id = request.node.nodeid          # "tests/test_x.py::test_something"
```

## Packaging a Plugin (pip-installable)

```toml
# pyproject.toml
[project]
name = "myapp-pytest"
version = "0.1.0"

[project.entry-points.pytest11]
myapp = "myapp_pytest.plugin"
```

```python
# myapp_pytest/plugin.py
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "myapp: myapp-specific marker")

def pytest_collection_modifyitems(config, items):
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.integration)

def pytest_report_header(config):
    return "myapp plugin: loaded"
```

Verify with `pytest --trace-config`. To import fixtures defined in a
library conftest, use `pytest_plugins` in the **root** conftest:

```python
# conftest.py (root only — deprecated in nested conftests)
pytest_plugins = ["myapp_pytest.fixtures"]
```

## Testing Plugins with pytester

```python
# test_plugin.py
pytest_plugins = ["pytester"]          # or run pytest with -p pytester

def test_marker_added(pytester):
    pytester.makepyfile("""
        import pytest
        @pytest.mark.myapp
        def test_x(): assert True
    """)
    result = pytester.runpytest("--strict-markers")
    result.assert_outcomes(passed=1)

def test_plugin_option(pytester):
    pytester.makeconftest("""
        def pytest_addoption(parser):
            parser.addoption("--my-flag", action="store_true")
    """)
    result = pytester.runpytest("--my-flag")
    result.assert_outcomes(passed=1)
```
