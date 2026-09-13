# P14 — Decorator, Middleware, and Observability

## Problem

Retries, tracing, metrics, authentication, and logging are cross-cutting concerns. Adding them inside every use case creates duplication and contaminates domain policy.

## Use when

- Behavior applies at a stable call, request, transport, or worker boundary.
- The wrapped contract can remain unchanged.
- Instrumentation must be consistently applied and tested.

## Book theory

Mak ch39 describes Decorator as runtime composition. Keen ch23 places telemetry at boundaries. Percival ch08 connects event handlers and side effects to a separable application concern.

## Minimal standard-library implementation

~~~python
from collections.abc import Callable
from functools import wraps
from time import monotonic
from typing import ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def timed(record: Callable[[float], None]):
    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
            started = monotonic()
            try:
                return fn(*args, **kwargs)
            finally:
                record(monotonic() - started)

        return wrapped

    return decorate
~~~

Middleware is the same idea at a request/stream pipeline boundary; ordering and exception semantics become part of the contract.

## Production evidence to inspect

Record where middleware is composed, ordering, context propagation, redaction, and whether failures are recorded without being swallowed. Tests should verify the wrapped return value and exception identity.

## Production compromise

Framework middleware often sees transport-specific context and therefore cannot be completely domain-pure. Keep it at the perimeter, standardize correlation IDs, and avoid logging prompts, credentials, or payloads by default.

## When not to use it

Use an explicit function call when behavior is business policy or its order is important enough to be visible in the use case. Hidden decorators can make flow and performance difficult to understand.

## Tests and practice

Test success, failure, cancellation, ordering, timing cleanup, and context propagation. Add a metrics decorator in the [provider-adapter exercise](../exercises/provider-adapter.md).

## Related IDs

P10 (events), P12 (adapter), P16 (resource lifecycle).

