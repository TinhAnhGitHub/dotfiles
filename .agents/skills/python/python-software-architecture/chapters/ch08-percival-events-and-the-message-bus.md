# Chapter 8: Events and the Message Bus

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part II: Event-Driven Architecture

## Core Idea
Domain events record significant occurrences within the domain model; a lightweight message bus dispatches these events to independent handlers, enforcing the Single Responsibility Principle without coupling core logic to side effects.

## Frameworks Introduced
- **Domain Event Pattern**:
  - When to use: When a state change in the domain model requires secondary actions (e.g. sending emails, updating search indexes, notifying external systems).
  - How:
    1. Define simple immutable dataclasses for events (e.g. `OutOfStock(sku)`).
    2. The domain model records events onto an internal list (`self.events.append(...)`).
    3. The service layer or Unit of Work harvests recorded events and publishes them to the message bus.
- **Internal Message Bus**:
  - When to use: Decoupling use cases and side effects within a single process.
  - How: Maintain a dictionary mapping event types to lists of handler functions. When an event is dispatched, invoke each registered handler.

## Key Concepts
- **Domain Event**: An immutable notification representing something that happened in the domain in the past (named in the past tense, e.g. `Allocated`, `OutOfStock`).
- **Message Bus**: A routing mechanism that receives messages and executes the appropriate handler functions.
- **Side Effect Decoupling**: Keeping email dispatch, SMS alerts, or webhook calls out of domain entities and service layer orchestrations.
- **Event Harvesting**: Pulling uncommitted events from domain aggregates inside the Unit of Work before or after committing transactions.

## Mental Models
- **Domain Models Don't Send Emails; They Announce Facts**: An aggregate should never import an email client. It simply states: *"I have run out of stock."* Whoever cares is free to listen.
- **Events Are Past-Tense Facts**: Because an event happened in the past, it cannot be rejected or cancelled. Handlers react to reality.

## Anti-patterns
- **Calling Notification Services from Domain Methods**: Writing `email_client.send()` inside `Batch.allocate()`.
- **Bloating the Service Layer with Side Effects**: Chaining 10 different notification and sync calls inside a single service function.
- **Treating Events as RPC Calls**: Expecting an event handler to return a value back to the aggregate that raised it.

## Code Examples

```python
from dataclasses import dataclass
from typing import Callable, Dict, List, Type

# 1. Event Definition
@dataclass
class Event:
    pass

@dataclass
class OutOfStock(Event):
    sku: str

# 2. Domain Aggregate records events
class Product:
    def __init__(self, sku: str, batches: list):
        self.sku = sku
        self.batches = batches
        self.events: List[Event] = []

    def allocate(self, line) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            self.events.append(OutOfStock(sku=self.sku))
            raise

# 3. Lightweight In-Memory Message Bus
class MessageBus:
    def __init__(self, HANDLERS: Dict[Type[Event], List[Callable]]):
        self.HANDLERS = HANDLERS

    def handle(self, event: Event):
        for handler in self.HANDLERS.get(type(event), []):
            handler(event)
```
- **What it demonstrates**: Event definition, aggregate recording the event, and a decoupled message bus dispatching to registered handlers.

## Reference Tables

| Approach | Direct Call in Service | Domain Event + Message Bus |
|---|---|---|
| **Coupling** | Service coupled to email/SMS clients | Domain & Service know only about the Event dataclass |
| **Adding New Actions** | Must edit and re-test service layer | Simply register a new handler on the bus |
| **SRP Compliance** | Violates SRP (business rule + notification) | Enforces SRP (handlers have single focus) |
| **Testability** | Requires mocking external services in use cases | Verify `OutOfStock` event is in `product.events` |

## Worked Example
Harvesting events inside the Unit of Work and dispatching them:

```python
def send_out_of_stock_email(event: OutOfStock):
    email.send_mail(
        "stock_team@furniture.com",
        f"Item {event.sku} is out of stock!"
    )

bus = MessageBus({
    OutOfStock: [send_out_of_stock_email],
})

# In Unit of Work:
class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def commit(self):
        self.session.commit()
        self.publish_events()

    def publish_events(self):
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                bus.handle(event)
```
Notice how `allocate()` in the service layer remains completely clean of email notifications.

## Key Takeaways
1. Domain events represent facts that have already happened within the business.
2. Aggregates record events internally; infrastructure/UoW publishes them after transaction commits.
3. Message buses decouple notification and synchronization side effects from business rules.
4. New side effects can be added by registering new handlers without modifying existing domain code.

## Connects To
- **Ch 7**: Aggregates as the creators and holders of domain events.
- **Ch 9**: Expanding the message bus to drive the entire application architecture.
- **Ch 10**: Distinguishing between Events and Commands.
