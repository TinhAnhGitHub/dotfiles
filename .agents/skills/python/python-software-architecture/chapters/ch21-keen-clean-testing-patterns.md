# Chapter 21: Implementing Test Patterns with Clean Architecture

**Source**: *Clean Architecture with Python* (Sam Keen, Packt 2025) — Part 3: Advanced Practices and Real-World Application (Chapter 8)

## Core Idea
Clean Architecture enables an ultra-fast, highly deterministic testing strategy where the vast majority of tests execute directly against Use Cases using in-memory fakes, minimizing slow, brittle integration and UI tests.

## Frameworks Introduced
- **The Clean Testing Pyramid**:
  - **Unit Tests (Entities)**: Test pure business logic and invariants in microseconds. Zero mocking required.
  - **Use Case Tests (Application)**: Test full application workflows edge-to-edge using in-memory fake repositories and mock gateways. Runs in milliseconds.
  - **Integration Tests (Adapters/Drivers)**: Verify real database queries, ORM mappings, and third-party APIs against real or containerized infrastructure.
  - **End-to-End / System Tests (Perimeter)**: A handful of smoke tests verifying complete HTTP request-to-database pipelines.
- **Fake-First Port Testing Strategy**:
  - When to use: Testing use cases without depending on database setups or fragile mock patches.
  - How: For every Output Port (e.g. `UserRepository`), build a corresponding `FakeUserRepository` using an internal Python dictionary.

## Key Concepts
- **Test Double Taxonomy**:
  - **Dummy**: Passed around but never actually used (e.g. parameter filler).
  - **Stub**: Provides canned answers to calls made during the test.
  - **Spy**: Records information about how it was called.
  - **Mock**: Programmed with expectations which form a specification of the calls they are expected to receive.
  - **Fake**: Has a working implementation, but takes shortcuts (e.g. in-memory storage).
- **Fast Feedback Loop**: Test suites that complete in seconds, encouraging constant execution during development.

## Mental Models
- **Test Against Use Cases, Not Implementation Details**: If you test private methods or internal database columns, refactoring breaks tests. Testing Use Case DTOs guarantees business correctness while freeing internals to change.
- **Fakes Provide Realistic State, Mocks Provide Rehearsed Lines**: A Fake repository behaves like a real database; a mock only says what you explicitly scripted it to say.

## Anti-patterns
- **Mocking the World**: Using `unittest.mock.patch` across 15 internal function calls, producing tests that pass even when the system is fundamentally broken.
- **Integration-Only Test Suites**: Running all business logic tests against a live PostgreSQL database in Docker, resulting in 20-minute test runs.
- **Testing Framework Features**: Testing that FastAPI returns 422 on bad JSON or SQLAlchemy saves a string; test your business rules, not third-party libraries.

## Code Examples

```python
import pytest
from application.use_cases import RegisterUserUseCase, RegisterUserRequest
from domain.model import User

# In-Memory Test Double (Fake)
class FakeUserRepository:
    def __init__(self):
        self._users: dict[str, User] = {}

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)

    def save(self, user: User) -> None:
        self._users[user.id] = user

class FakeEmailSender:
    def __init__(self):
        self.sent_emails = []

    def send_welcome(self, email: str) -> None:
        self.sent_emails.append(email)

# Clean, blazing-fast Use Case test
def test_register_user_successfully():
    repo = FakeUserRepository()
    sender = FakeEmailSender()
    use_case = RegisterUserUseCase(repo=repo, email_sender=sender)

    request = RegisterUserRequest(username="alice", email="alice@example.com")
    response = use_case.execute(request)

    assert response.success is True
    assert repo.get_by_email("alice@example.com") is not None
    assert "alice@example.com" in sender.sent_emails
```
- **What it demonstrates**: Full application use case verified in 2 milliseconds with zero database, network, or framework dependencies.

## Reference Tables

| Test Level | Target | Tooling | Execution Speed | Typical Share |
|---|---|---|---|---|
| **Domain Unit** | Entities, Value Objects | Pytest | < 1 ms | 40% |
| **Use Case Unit** | Interactors, Ports | Pytest + Fakes | 1–5 ms | 45% |
| **Adapter Integration** | Repositories, Drivers | Testcontainers, Postgres | 100–500 ms | 12% |
| **End-to-End** | Full Application / HTTP | TestClient, Playwright | 1–5 s | 3% |

## Worked Example
Contract testing a repository port against both Fake and Real database implementations:

```python
# Shared test contract
class UserRepositoryContractTests:
    def test_can_save_and_retrieve_user(self, repo):
        user = User(id="u-1", name="Alice", email="alice@test.com")
        repo.save(user)
        assert repo.get_by_id("u-1") == user

# Test against Fake (runs in 1 ms)
class TestFakeUserRepository(UserRepositoryContractTests):
    @pytest.fixture
    def repo(self):
        return FakeUserRepository()

# Test against Real PostgreSQL (runs in CI)
class TestPostgresUserRepository(UserRepositoryContractTests):
    @pytest.fixture
    def repo(self, db_session):
        return SqlAlchemyUserRepository(db_session)
```

## Key Takeaways
1. Design systems so that 80%+ of tests run without databases, networks, or browsers.
2. Build in-memory Fakes for each Output Port; reuse them across use-case test suites.
3. Test against Use Case Request and Response DTOs to make tests refactor-proof.
4. Use contract tests to ensure Fakes and production database adapters behave identically.

## Connects To
- **Ch 5**: Percival's High Gear vs Low Gear TDD comparison.
- **Ch 18**: Use Case Interactors as the primary testing surface.
- **Ch 20**: Testing Frameworks and Drivers separately with integration tests.
