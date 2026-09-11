# Chapter 9: Going to Town on the Message Bus

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part II: Event-Driven Architecture

## Core Idea
When the message bus becomes the central architectural spine of the application, every use case is triggered as a message handler, creating a uniform, highly extensible system where workflows are composed of event chains.

## Frameworks Introduced
- **Event-Driven Service Architecture**:
  - When to use: When complex business workflows trigger cascades of secondary workflows (e.g., reallocating orders when batch quantities change).
  - How:
    1. Turn service functions into message handlers that accept an event and a Unit of Work.
    2. As handlers execute, domain aggregates produce new events.
    3. The message bus collects these child events and queues them for execution within the same or subsequent transactions.
- **The Event Loop Queue**:
  - When to use: Managing event cascades without infinite recursion or stack overflows.
  - How: Maintain a FIFO queue of events inside the message bus. While the queue is non-empty, pop the front event and invoke all matching handlers.

## Key Concepts
- **Event Cascading**: A handler processing Event A causes an aggregate to raise Event B, which the message bus enqueues and handles in turn.
- **Message Loop**: A `while queue:` loop inside the message bus ensuring sequential, predictable dispatch of events.
- **Uniform Handler Interface**: Designing all use case entry points with identical signatures: `handler(event: T, uow: AbstractUnitOfWork) -> None`.

## Mental Models
- **Think of the Message Bus as an Airport Baggage Sorter**: Luggage (events) enters on conveyor belts. The sorter reads tags and routes each piece to the correct destination carousels (handlers).
- **Workflows as Domino Chains**: Instead of a monolithic function orchestrating 5 steps, Step 1 raises an event that triggers Step 2, which raises an event triggering Step 3.

## Anti-patterns
- **Infinite Event Loops**: Handler A raises Event B, which triggers Handler B raising Event A. Always ensure terminal states in event cascades.
- **Returning Values from Event Handlers**: Designing events with the expectation of getting data back; events are notifications, not synchronous function calls.
- **Coupling Handlers Directly**: Having Handler 1 invoke Handler 2 directly instead of publishing an event to the bus.

## Code Examples

```python
class MessageBus:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        event_handlers: Dict[Type[Event], List[Callable]],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.queue: list[Event] = []

    def handle(self, message: Event):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            self.handle_event(message)

    def handle_event(self, event: Event):
        for handler in self.event_handlers.get(type(event), []):
            try:
                handler(event, uow=self.uow)
                self.queue.extend(self.uow.collect_new_events())
            except Exception:
                logger.exception("Exception handling event %s", event)
                raise
```
- **What it demonstrates**: A FIFO message bus queue that collects new events emitted by the Unit of Work and processes them sequentially.

## Reference Tables

| Architecture Pattern | Monolithic Service Layer | Full Event-Driven Bus |
|---|---|---|
| **Entry Point** | Distinct function per use case | Message Bus `handle(message)` |
| **Extensibility** | Modify existing service function | Add new handler to event map |
| **Coupling** | Direct caller-callee coupling | Decoupled publish-subscribe |
| **Failure Isolation** | Exception fails entire script | Handlers can have independent retry policies |

## Worked Example
Implementing a batch reallocation requirement:
Requirement: *"When batch quantity is reduced, existing allocations may become invalid. Automatically reallocate deallocated order lines to remaining batches."*

1. Event: `BatchQuantityChanged(ref, qty)`
2. Handler: `change_batch_quantity(event, uow)`:
   - Product aggregate updates batch, deallocates excess lines, and raises `AllocationRequired(line)`.
3. Bus collects `AllocationRequired` and puts it on the queue.
4. Handler: `allocate(event, uow)` executes automatically, finding a new batch for the displaced line!
Neither handler knows about the other; they communicate strictly through events.

## Key Takeaways
1. A message queue prevents deep recursive call stacks during event cascades.
2. Converting service functions into message handlers standardizes system architecture.
3. Complex multi-step business processes can be broken down into clean, decoupled event chains.
4. Handlers interact with the database solely through the Unit of Work.

## Connects To
- **Ch 8**: Foundational concepts of events and handlers.
- **Ch 10**: Refining messages into Commands and Events.
- **Ch 11**: Extending the internal message bus to external microservices.
