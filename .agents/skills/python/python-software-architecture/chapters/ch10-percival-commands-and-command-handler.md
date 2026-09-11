# Chapter 10: Commands and Command Handlers

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part II: Event-Driven Architecture

## Core Idea
Messages in an event-driven system are of two distinct types: Commands (imperative instructions intended for exactly one handler that can fail) and Events (broadcast notifications of past facts intended for zero-or-more handlers that should not fail).

## Frameworks Introduced
- **Command-Event Dichotomy**:
  - When to use: When modeling interactions in any message-driven or CQRS architecture.
  - How:
    - **Command**: Expressed as an imperative verb (`Allocate`, `CreateBatch`, `ChangeQuantity`). Sent to exactly one destination. Expected to succeed or raise an error back to the caller.
    - **Event**: Expressed as a past-tense verb (`Allocated`, `BatchCreated`, `OutOfStock`). Broadcast to zero or many subscribers. Handlers should fail independently without crashing the publisher.
- **Dual Dispatch Message Bus**:
  - When to use: When the message bus handles both user requests (commands) and follow-up actions (events).
  - How: Route commands to a `COMMAND_HANDLERS` dictionary (1:1 mapping) and events to an `EVENT_HANDLERS` dictionary (1:N mapping).

## Key Concepts
- **Command**: A message requesting an action. Has one handler. Can fail.
- **Event**: A message stating something has happened. Has 0..N handlers. Should not fail the primary action.
- **Intent vs Fact**: A command expresses intent (which might be rejected); an event expresses an indisputable fact.
- **Synchronous Error Recovery**: How the API handles command failures (returning HTTP 400/409) versus event failures (dead-letter queues, retries).

## Mental Models
- **Commands Are Orders; Events Are News**: A boss gives an employee an order (Command: "Finish this report"). The employee announces the news (Event: "The report has been submitted").
- **1:1 vs 1:Many**: If more than one handler handles a command, your architecture is ambiguous. If zero handlers listen to an event, the system remains completely valid.

## Anti-patterns
- **Using Events to Direct Action**: Raising an event named `PleaseAllocateOrder` instead of issuing a command `Allocate`.
- **Multiple Command Handlers**: Registering two different handlers for a single command, making execution order non-deterministic.
- **Failing the Main Command on Event Handler Error**: If sending an email notification fails, rolling back the database transaction that successfully created the order.

## Code Examples

```python
from dataclasses import dataclass

class Message:
    pass

# Commands: Imperative, Exactly One Handler
@dataclass
class Command(Message):
    pass

@dataclass
class Allocate(Command):
    orderid: str
    sku: str
    qty: int

@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None

# Message Bus with Separate Routing
class MessageBus:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        command_handlers: Dict[Type[Command], Callable],
        event_handlers: Dict[Type[Event], List[Callable]],
    ):
        self.uow = uow
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers
        self.queue: list[Message] = []

    def handle(self, message: Message):
        self.queue = [message]
        while self.queue:
            msg = self.queue.pop(0)
            if isinstance(msg, Command):
                self.handle_command(msg)
            elif isinstance(msg, Event):
                self.handle_event(msg)

    def handle_command(self, command: Command):
        handler = self.command_handlers[type(command)]
        try:
            handler(command, uow=self.uow)
            self.queue.extend(self.uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise  # Commands re-raise errors to notify callers
```
- **What it demonstrates**: Strict architectural separation between Commands (single handler, re-raises errors) and Events.

## Reference Tables

| Property | Command (`Allocate`) | Event (`Allocated`) |
|---|---|---|
| **Naming** | Imperative verb (`CreateBatch`) | Past-tense verb (`BatchCreated`) |
| **Destination** | Exactly one recipient | Broadcast to 0..N subscribers |
| **Sender Expectation** | Expects action to be completed or error raised | Fire and forget; doesn't care who listens |
| **Error Handling** | Re-raises exception to caller (HTTP 400/500) | Isolated per handler; retried or logged |
| **Validation** | Can be rejected as invalid | Cannot be rejected; already happened |

## Worked Example
Handling a web request via command dispatch:

```python
@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    cmd = commands.Allocate(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )
    try:
        bus.handle(cmd)
    except InvalidSku as e:
        return jsonify({"message": str(e)}), 400
    except OutOfStock as e:
        return jsonify({"message": str(e)}), 409
    return jsonify({"status": "allocated"}), 202
```
The controller is now purely a message factory: parse JSON into Command -> dispatch to Bus -> map exceptions to HTTP status codes.

## Key Takeaways
1. Commands express intent and are handled by exactly one handler.
2. Events express past facts and can be handled by zero or many handlers.
3. Commands fail loudly; event handlers fail independently.
4. Separate command routing from event routing in the message bus.

## Connects To
- **Ch 9**: Message bus implementation evolution.
- **Ch 11**: Commands and events across microservice boundaries.
- **Ch 12**: CQRS: Commands modify state; Queries read state.
