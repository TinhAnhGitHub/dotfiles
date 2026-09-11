# Chapter 12: Command-Query Responsibility Segregation (CQRS)

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part II: Event-Driven Architecture

## Core Idea
Domain models are optimized for write operations and enforcing business invariants, not for read queries; CQRS separates the read and write models into dedicated paths, maximizing query performance and design clarity.

## Frameworks Introduced
- **Command-Query Responsibility Segregation (CQRS)**:
  - When to use: When read operations require complex joins, pagination, or high throughput that strain the domain model and ORM.
  - How:
    - **Write Path**: Direct commands through Service Layer -> Domain Model -> Unit of Work -> Repository. Enforce invariants strictly.
    - **Read Path**: Bypass the domain model and ORM completely. Execute fast, raw SQL queries directly against the database or a read-optimized view table.
- **Read Projections / Denormalized Views**:
  - When to use: When query performance demands zero-join reads.
  - How: Event handlers listen to write-side domain events (`Allocated`, `Deallocated`) and update a flattened read-only table or document store (e.g. SQLite, Redis, Elasticsearch).

## Key Concepts
- **CQS (Command-Query Separation)**: Principle stating that a method should either change state (command) or return data (query), but never both.
- **CQRS**: Applying CQS at the architectural tier level: having separate models and pathways for reads and writes.
- **Read Model**: A data structure or table optimized solely for fast retrieval and UI display.
- **Write Model**: A rich domain model with aggregates and repositories enforcing transactional integrity.
- **Eventual Consistency in Views**: The brief time window between a write transaction committing and the asynchronous read view updating.

## Mental Models
- **Writes Are Contracts; Reads Are Snapshots**: Writing is a complex negotiation where rules must be verified; reading is simply snapping a picture of the current state.
- **Don't Use a Bulldozer to Pick Up a Leaf**: Loading a full aggregate with child entities and version numbers just to display a list of SKU names on a webpage is massive overkill. Use raw SQL.

## Anti-patterns
- **Using Domain Aggregates for Reporting Queries**: Loading hundreds of aggregate roots through the repository just to compute an average or render a summary report.
- **Premature Full-Database CQRS**: Splitting into physically separate read and write databases with Kafka synchronization when a single PostgreSQL database with a simple SQL read function would suffice.
- **Writing Business Logic in Read Queries**: Embedding business calculations into SQL views that diverge from domain model rules.

## Code Examples

```python
# WRITE PATH: Through Service Layer, Domain Model, and UoW
def allocate(cmd: commands.Allocate, uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get(cmd.sku)
        batchref = product.allocate(OrderLine(cmd.orderid, cmd.sku, cmd.qty))
        uow.commit()

# READ PATH: Fast Raw SQL Bypassing Domain and ORM
def get_allocations(orderid: str, db_session) -> list[dict]:
    query = """
        SELECT ol.sku, b.reference 
        FROM allocations a
        JOIN order_lines ol ON a.orderline_id = ol.id
        JOIN batches b ON a.batch_id = b.id
        WHERE ol.orderid = :orderid
    """
    results = db_session.execute(query, {"orderid": orderid}).fetchall()
    return [{"sku": r[0], "batchref": r[1]} for r in results]
```
- **What it demonstrates**: Clean CQRS separation: write path enforces domain rules; read path uses direct SQL returning plain dictionaries.

## Reference Tables

| Dimension | Write Model | Read Model |
|---|---|---|
| **Goal** | Consistency, invariant enforcement | High throughput, low latency |
| **Tooling** | Rich Domain Model, Repository, UoW | Raw SQL, Views, Redis, Elasticsearch |
| **Data Structure** | Normalized, Aggregate boundaries | Denormalized, flattened DTOs |
| **Concurrency** | Optimistic locking, version numbers | None required (read-only) |
| **Complexity** | High business logic | Zero business logic |

## Worked Example
Updating a materialized read-view using an event handler:

```python
# Event handler updating a read-only table:
def update_read_model(event: events.Allocated, db_session):
    db_session.execute(
        """
        INSERT INTO allocations_view (orderid, sku, batchref)
        VALUES (:orderid, :sku, :batchref)
        """,
        {"orderid": event.orderid, "sku": event.sku, "batchref": event.batchref}
    )
    db_session.commit()

# Read endpoint is now a single-table primary-key lookup:
def get_order_allocations(orderid: str, db_session):
    return db_session.execute(
        "SELECT sku, batchref FROM allocations_view WHERE orderid = :orderid",
        {"orderid": orderid}
    ).fetchall()
```

## Key Takeaways
1. Domain models are for writing, not for reading.
2. Read operations should bypass the domain model and repositories completely.
3. Raw SQL or lightweight query builders provide superior query performance.
4. Denormalized views populated by domain events eliminate complex database joins.

## Connects To
- **Ch 10**: Commands drive the write path; queries power the read path.
- **Ch 11**: Events from the write model synchronize remote read models.
- **Ch 19**: Presenters and View Models in Clean Architecture.
