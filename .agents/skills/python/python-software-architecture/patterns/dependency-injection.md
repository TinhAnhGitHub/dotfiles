# P07 — Composition Root and Dependency Injection

## Problem

Objects become difficult to test when they construct databases, clients, models, and executors internally. P07 centralizes construction and makes ownership and lifetime visible.

## Use when

- A process has multiple environments or provider choices.
- Resources have distinct lifetimes (process, request, task).
- Tests need to replace expensive or nondeterministic collaborators.

## Book theory

Percival ch13 calls the bootstrap/composition root the place where concrete dependencies are assembled. Keen ch18 and ch20 put wiring at the framework edge. Mak ch34 supplies factories when product construction itself varies.

## Minimal standard-library implementation

~~~python
from dataclasses import dataclass
from typing import Callable


@dataclass
class App:
    fetch: Callable[[str], str]
    emit: Callable[[str], None]


def build_app(*, fetch: Callable[[str], str], emit: Callable[[str], None]) -> App:
    return App(fetch=fetch, emit=emit)


def main() -> None:
    app = build_app(fetch=load_from_http, emit=publish_event)
    app.emit(app.fetch("item-1"))


def load_from_http(key: str) -> str:
    return key


def publish_event(value: str) -> None:
    print(value)
~~~

The example uses manual DI intentionally. A container is an implementation detail, not the architecture.

## Production evidence to inspect

Find where configuration becomes concrete objects, where resources are closed, and whether tests can build a smaller graph. Distinguish dependency injection from a service locator that lets any module fetch global state.

## Production compromise

Large agent and serving systems sometimes use module-level registries or lazy singletons for model weights and GPU pools. This reduces startup cost but makes tests and teardown harder. Make the lifetime explicit and expose an override for tests.

## When not to use it

Do not introduce a container for two functions. A constructor or `build_app()` is often more readable and has better static traceability.

## Tests and practice

Build the application with fakes, assert the real composition root wires production adapters, and test shutdown of long-lived resources. Practice in the [provider-adapter exercise](../exercises/provider-adapter.md).

## Related IDs

P06 (ports), P08 (factory/registry), P16 (lifecycle), P17 (fitness tests).

