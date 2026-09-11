# Chapter 5: TDD in High Gear and Low Gear

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part I: Building an Architecture to Support Domain Modeling

## Core Idea
Test-Driven Development operates in two gears: High Gear (writing tests against the Service Layer for fast, refactor-proof coverage) and Low Gear (writing tests against Domain Models when exploring intricate business rules).

## Frameworks Introduced
- **The Gear-Shifting Framework in TDD**:
  - When to use: When developing features and deciding where tests should assert expectations.
  - How:
    - **Low Gear**: Start here when discovering domain design. Write focused unit tests directly against entities and value objects.
    - **High Gear**: Once domain concepts stabilize, write tests against the service layer. As you refactor domain internals, service-layer tests remain unchanged.
- **Test Pyramid Calibration**:
  - When to use: Structuring test suites for maintainability and speed.
  - How: Keep 80% of tests as fast unit/service tests using fakes, 15% as integration tests verifying database adapters, and 5% as end-to-end HTTP tests.

## Key Concepts
- **Low Gear TDD**: Writing tests directly against domain model classes; ideal for exploring intricate logic, but couples tests to class structures.
- **High Gear TDD**: Writing tests against the service layer; treats domain models as implementation details of the use case.
- **Test-Induced Design Damage**: Writing awkward code solely to accommodate mocks, or freezing domain design because thousands of unit tests couple directly to class private state.
- **Edge-to-Edge Unit Test**: A test that exercises a use case from the service boundary down to domain logic using in-memory fakes.

## Mental Models
- **Shift to High Gear to Refactor Fearlessly**: If all your tests assert domain class method names, you cannot refactor your domain without breaking all tests. Testing via the service layer frees the domain to change.
- **Low Gear for Exploration, High Gear for Preservation**: Use Low Gear like a microscope while shaping an algorithm; use High Gear like a safety net once the workflow is set.

## Anti-patterns
- **Testing Implementation Details**: Asserting that method `_calculate_discount()` was called with specific arguments instead of checking the resulting order total.
- **End-to-End Test Overload**: Relying on slow Selenium/Playwright or full HTTP tests to verify edge-case business logic.
- **Permanent Low Gear**: Maintaining hundreds of microscopic unit tests for trivial getters/setters that resist any architectural evolution.

## Code Examples

```python
# Low Gear Test (Coupled to Domain Model details)
def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)
    batch.allocate(line)
    assert batch.available_quantity == 18

# High Gear Test (Decoupled: Uses Service Layer and Primitive Types)
def test_allocations_are_persisted():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "SMALL-TABLE", 20, None, repo, session)
    
    result = services.allocate("o1", "SMALL-TABLE", 2, repo, session)
    
    assert result == "b1"
    batch = repo.get("b1")
    assert batch.available_quantity == 18
```
- **What it demonstrates**: The difference between testing domain entity mechanics (low gear) versus testing the complete use-case contract (high gear).

## Reference Tables

| Attribute | Low Gear (Domain Tests) | High Gear (Service Tests) | E2E Tests (HTTP) |
|---|---|---|---|
| **Target** | `domain/model.py` | `service_layer/services.py` | HTTP Endpoints |
| **Speed** | Sub-millisecond | Millisecond | Seconds |
| **Refactoring Tolerance** | Low (breaks if classes change) | High (domain can be reorganized) | Highest |
| **Feedback Value** | Clarifies domain edge cases | Validates business use case | Validates deployment wiring |

## Worked Example
Decoupling service-layer tests completely from domain models:
Instead of creating `Batch` and `OrderLine` domain objects inside the test, provide helper fixtures:

```python
def test_allocate_returns_allocation():
    repo = FakeRepository([])
    session = FakeSession()
    # High-gear: Use service layer to setup initial state!
    services.add_batch("batch1", "COMPACT-DESK", 100, None, repo, session)
    
    result = services.allocate("order1", "COMPACT-DESK", 10, repo, session)
    
    assert result == "batch1"
```
If you later decide to rename `Batch` to `StockLot` or split it into two classes, this test requires zero edits!

## Key Takeaways
1. Shift to High Gear when refactoring to keep tests decoupled from internal class layouts.
2. Low Gear is indispensable when initially designing complex business algorithms.
3. Express service-layer tests using primitives (strings, ints) to maintain pure decoupling.
4. Keep the majority of your test suite running against the service layer with fakes.

## Connects To
- **Ch 4**: Service layer as the target for High Gear tests.
- **Ch 6**: Unit of Work simplifies service tests by handling sessions cleanly.
- **Ch 21**: Sam Keen's Clean Testing Patterns.
