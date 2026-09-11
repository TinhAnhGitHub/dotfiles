# Chapter 4: Our First Use Case: Flask API and Service Layer

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part I: Building an Architecture to Support Domain Modeling

## Core Idea
The Service Layer (or Use Case layer) orchestrates business workflows: it receives requests from the outside world, fetches domain objects via repositories, executes domain logic, and commits state.

## Frameworks Introduced
- **Service Layer Pattern**:
  - When to use: When web controllers or CLI handlers begin containing business workflow logic, database queries, and error handling.
  - How: Extract use cases into dedicated service functions (e.g. `services.allocate(orderid, sku, qty, repo, session)`). The web controller becomes a thin translation layer.
- **Thin Controller Pattern**:
  - When to use: In any web API (Flask, FastAPI, Django).
  - How: The controller only parses HTTP requests into primitive types, calls a service function, and formats the response status code and JSON.

## Key Concepts
- **Service Layer (Application Service)**: Coordinates domain objects and infrastructure to perform a complete business use case.
- **Domain Service vs. Application Service**: A domain service contains core business calculation logic; an application service orchestrates data retrieval, domain calls, and transaction commits.
- **Primitive Obsession in Handlers**: Passing primitive types (strings, ints) to service functions rather than web framework objects (`flask.request`).
- **Fake-Driven Service Testing**: Testing entire use cases edge-to-edge by passing a `FakeRepository` to service functions without running HTTP servers.

## Mental Models
- **Web Frameworks Are Delivery Mechanisms, Not the Application**: Flask or FastAPI is just an adapter that translates HTTP into use-case calls.
- **The Service Layer Is the Conductor of the Orchestra**: The service layer does not play the instruments (domain rules); it tells each section when to play.

## Anti-patterns
- **Fat Controllers**: Putting database queries, validation, transaction management, and business decisions directly inside HTTP endpoint handlers.
- **Domain Logic in the Service Layer**: Letting the service layer mutate internal properties of entities directly instead of calling domain methods.
- **Passing Web Framework Objects Downwards**: Passing `flask.request` or Django `HttpRequest` into service layer functions.

## Code Examples

```python
# services.py
from domain.model import OrderLine, Batch, OutOfStock
from adapters.repository import AbstractRepository

class InvalidSku(Exception):
    pass

def allocate(
    orderid: str, sku: str, qty: int, repo: AbstractRepository, session
) -> str:
    line = OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not any(b.sku == line.sku for b in batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    
    batchref = model_allocate(line, batches)
    session.commit()
    return batchref

# flask_app.py (Thin Controller)
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    try:
        batchref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            repo=SqlAlchemyRepository(db.session),
            session=db.session,
        )
    except (OutOfStock, InvalidSku) as e:
        return jsonify({"message": str(e)}), 400
    return jsonify({"batchref": batchref}), 201
```
- **What it demonstrates**: Clean separation between a thin HTTP controller and an application service orchestrating repository access and domain operations.

## Reference Tables

| Responsibility | Web Controller | Service Layer | Domain Model |
|---|---|---|---|
| **JSON Serialization** | Yes | No | No |
| **HTTP Status Codes** | Yes (201, 400, 404) | No | No |
| **Database Transaction** | No | Coordinates commit | No |
| **Repository Access** | No | Calls `repo.get()`, `repo.add()` | No |
| **Business Invariants** | No | Delegates to Model | Enforces rules directly |

## Worked Example
Testing the allocation use case completely in memory:

```python
def test_returns_allocation():
    repo = FakeRepository([
        Batch("b1", "COMPACT-DESK", 100, eta=None)
    ])
    session = FakeSession()
    
    result = services.allocate("o1", "COMPACT-DESK", 10, repo, session)
    
    assert result == "b1"
    assert session.committed is True

def test_errors_for_invalid_sku():
    repo = FakeRepository([
        Batch("b1", "AREALSKU", 100, eta=None)
    ])
    session = FakeSession()
    
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, session)
```

## Key Takeaways
1. The service layer captures user intent and orchestrates workflows.
2. Web controllers should only parse requests, invoke services, and return responses.
3. Pass primitive data or DTOs into services to decouple them from HTTP frameworks.
4. Testing use cases through the service layer with fakes tests the application end-to-end without network overhead.

## Connects To
- **Ch 5**: Testing strategies across the Domain vs Service layers.
- **Ch 6**: Replacing manual `session.commit()` with the Unit of Work pattern.
- **Ch 18**: Sam Keen's Application Layer Use Cases.
