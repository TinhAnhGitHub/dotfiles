# Pytest — Advanced Patterns & Playbook

## Fixture Patterns

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Scoped fixtures with teardown
@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("postgresql://localhost/test")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Factory fixture
@pytest.fixture
def user_factory(db_session):
    created = []
    def _create(name="Alice", email=None):
        user = User(name=name, email=email or f"{name.lower()}@test.com")
        db_session.add(user)
        db_session.flush()
        created.append(user)
        return user
    yield _create
    for u in created:
        db_session.delete(u)

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

## Async Testing

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_concurrent_requests():
    results = await asyncio.gather(
        fetch("/api/users"), fetch("/api/products"), fetch("/api/orders")
    )
    assert all(r.status == 200 for r in results)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    response = await async_client.post("/users", json={"name": "Alice"})
    assert response.status_code == 201
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
