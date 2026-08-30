# Singleton and inheritance overuse

## Intent

Recognize when a familiar design pattern is adding coupling, hidden state, or combinatorial
complexity instead of solving a real design pressure.

## Use when

Use this review pattern when code introduces a Singleton, deep inheritance, multiple inheritance,
or a class hierarchy solely to combine unrelated features.

## Why

An explicit Singleton often hides dependencies and makes tests share mutable state; Python modules
already provide one import-level namespace. Deep or multiple inheritance creates fragile method-
resolution and initialization contracts.

## Prefer instead

- Pass dependencies explicitly.
- Use a module-level immutable constant when shared identity is genuinely required.
- Use a Factory or Registry for construction and extension.
- Use composition, delegation, Adapter, Decorator, or Strategy for independent behavior axes.

```python
class Logger:
    def __init__(self, emit, accept) -> None:
        self.emit = emit
        self.accept = accept

    def log(self, message: str) -> None:
        if self.accept(message):
            self.emit(message)
```

This replaces a `FilteredSocketLogger`-style subclass matrix with two independently replaceable
collaborators.

## When not to use

Do not reject every class hierarchy or shared object automatically. Keep inheritance when there is
a genuine substitutable “is-a” relationship and the base contract is stable. Keep process-wide
identity only when it is a documented invariant with explicit lifecycle and test isolation.

## Trade-offs and tests

Composition adds wiring, while explicit dependencies can make constructors longer. Look for
hidden global state, subclass combinations, `super()` ordering assumptions, constructor argument
collisions, and tests requiring global reset. Confirm behavior before deleting hierarchy code.

## Related patterns

See [composition over inheritance](../principles/composition.md), [Dependency Injection and Registry](../extensibility/registry-di.md),
and [Decorator](../composition/decorator.md).

## Framework examples

### PydanticAI — `Agent` dependencies

PydanticAI `deps_type` and `RunContext` solve the problem of tools reaching for singleton
clients or other hidden process-wide state. Dependency injection fits this review pattern because
the agent receives an explicit service bundle that production and tests can replace independently.

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Services:
    weather: "WeatherClient"

agent = Agent("provider:model", deps_type=Services)

@agent.tool
def weather(ctx: RunContext[Services], city: str) -> str:
    return ctx.deps.weather.lookup(city)
```

Adapted from the [PydanticAI dependencies guide](https://pydantic.dev/docs/ai/core-concepts/dependencies/)
(latest, fetched 2026-08-30; adapted).

## ArjanCodes OOP lessons (adapted)

### Prefer frozen configuration and explicit dependencies to a Singleton

When shared settings are values rather than identity-bearing resources, a frozen dataclass and an
ordinary factory solve the problem without hidden mutable state or global reset logic. This fits
Python because callers can construct independent services for production and tests.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    endpoint: str
    timeout_seconds: float = 5.0

def make_service(config: AppConfig, transport: Transport) -> Service:
    return Service(endpoint=config.endpoint, timeout=config.timeout_seconds,
                   transport=transport)
```

Adapted from [ArjanCodes' configuration-subclasses example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/02_configuration_subclasses_after.py).

### Keep independent behavior as options or callables

When logging, retry, and formatting vary independently, a Singleton or multiple-inheritance class
combines unrelated axes and makes tests order-dependent. Explicit options and strategies solve the
problem by putting variation at the call site.

```python
from collections.abc import Callable

def send(message: str, *, retry: Callable[[Callable[[], None]], None],
         format_message: Callable[[str], str]) -> None:
    retry(lambda: deliver(format_message(message)))
```

Adapted from [ArjanCodes' feature-variation example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/03_feature_variation_after.py).

### Do not build a base class before a change axis exists

When implementations do not yet share meaning, a hierarchy only predicts future requirements and
creates coupling. Keep the local function or concrete class until a second implementation proves
the contract; see [ArjanCodes' premature-abstraction example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/06_premature_abstraction_after.py)
and the accompanying [OOP video](https://www.youtube.com/watch?v=RqcEK7sWesQ).
