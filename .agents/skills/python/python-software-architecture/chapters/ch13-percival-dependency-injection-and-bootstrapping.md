# Chapter 13: Dependency Injection (and Bootstrapping)

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part II: Event-Driven Architecture

## Core Idea
Dependency Injection in Python does not require heavy XML frameworks or magic decorators; a simple bootstrap function acting as the Composition Root configures dependencies and wires handlers at application startup.

## Frameworks Introduced
- **Composition Root / Bootstrapper**:
  - When to use: In every production application to wire adapters, repositories, and handlers together in a single place at startup.
  - How: Write a `bootstrap()` function that instantiates real dependencies (database engines, session factories, email clients), injects them into message handlers via closures or `functools.partial`, and returns a configured `MessageBus`.
- **Manual Dependency Injection with Closures / Partials**:
  - When to use: When passing dependencies into handlers without polluting domain signatures.
  - How: Use `inspect` or `functools.partial` to bind the Unit of Work and external adapters to handlers, exposing a uniform callable interface `handler(message)`.

## Key Concepts
- **Composition Root**: The single location where the entire object graph of the application is assembled.
- **Dependency Injection (DI)**: Passing collaborators into an object rather than letting the object instantiate them internally.
- **Bootstrapping**: The startup routine that connects configuration, database sessions, and handlers into a working system.
- **Explicit Dependencies**: Requiring dependencies as arguments rather than relying on global variables or hidden imports.

## Mental Models
- **Think of the Bootstrapper as an Electrical Switchboard**: Production wires the switchboard to the city grid; tests wire it to a generator. The appliances (handlers and models) don't care where the power comes from.
- **Keep Wiring at the Outer Edge**: Domain models and service functions should never instantiate their own databases. Pass them in at the outermost layer.

## Anti-patterns
- **Global Database Singletons**: Importing `from app import db` and calling `db.session` everywhere, making testing impossible without monkeypatching.
- **Over-Engineered DI Containers**: Using heavy reflection-based enterprise frameworks in Python when a 30-line bootstrap script accomplishes the same goal cleanly.
- **Scattered Configuration**: Instantiating repositories and database connections in multiple web controller files.

## Code Examples

```python
import inspect
from functools import partial
from typing import Callable, Dict, Type
from adapters import orm, notifications
from service_layer import messagebus, unit_of_work

def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = None,
    notifications_adapter: notifications.AbstractNotifications = None,
) -> messagebus.MessageBus:
    if start_orm:
        orm.start_mappers()

    if uow is None:
        uow = unit_of_work.SqlAlchemyUnitOfWork()
    if notifications_adapter is None:
        notifications_adapter = notifications.EmailNotifications()

    # Inject dependencies using partials or inspection
    dependencies = {"uow": uow, "send_mail": notifications_adapter.send}
    injected_event_handlers = {
        event_type: [inject_dependencies(handler, dependencies) for handler in handlers]
        for event_type, handlers in messagebus.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in messagebus.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )

def inject_dependencies(handler: Callable, dependencies: dict) -> Callable:
    params = inspect.signature(handler).parameters
    handler_dependencies = {
        name: dep for name, dep in dependencies.items() if name in params
    }
    return partial(handler, **handler_dependencies)
```
- **What it demonstrates**: A pure Python bootstrap script providing dependency injection without heavy framework magic.

## Reference Tables

| Approach | Global Singletons | Heavy DI Framework | Pythonic Bootstrapper |
|---|---|---|---|
| **Explicitness** | Hidden dependencies | Obscured in container config | Explicit in function arguments |
| **Test Setup** | Requires `mock.patch()` | Container configuration overrides | Pass fakes directly: `bootstrap(uow=FakeUoW())` |
| **Python Idiom** | Bad practice | Java/Spring port | Idiomatic Python (`functools.partial`) |
| **Setup Location** | Scattered in files | Container files | Single Composition Root (`bootstrap.py`) |

## Worked Example
Bootstrapping an entire test environment in one line:

```python
def test_allocate_via_bootstrapped_bus():
    # Complete end-to-end test without database or network:
    bus = bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications_adapter=FakeNotifications(),
    )
    
    bus.handle(commands.CreateBatch("b1", "RETRO-LAMP", 50))
    bus.handle(commands.Allocate("o1", "RETRO-LAMP", 10))
    
    assert bus.uow.batches.get("b1").available_quantity == 40
```

## Key Takeaways
1. Use a single Composition Root (`bootstrap.py`) to assemble the application object graph.
2. Invert dependencies by accepting collaborators as parameters rather than importing globals.
3. Python's `functools.partial` and `inspect` module provide clean, lightweight dependency injection.
4. Testing becomes trivial: pass fake adapters into the bootstrapper to test the entire application.

## Connects To
- **Ch 4 & 6**: Service layer and UoW receive their dependencies through bootstrap.
- **Ch 10**: Handlers are wired to the message bus via the bootstrapper.
- **Ch 20**: Clean Architecture driver configuration.
