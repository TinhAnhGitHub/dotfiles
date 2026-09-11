# Closures and decorators

## Use when

Use a closure or decorator when behavior must be configured once and applied consistently at a
callable boundary: retries, tracing, validation, authorization, metrics, or adaptation.

## Why

The closure captures private configuration without exposing mutable state. A decorator keeps the
cross-cutting concern at the boundary and leaves the core operation focused.

## Safe shape

Use `functools.wraps`, preserve sync/async behavior, document wrapper ordering, and avoid hiding
important exceptions. Use a class instead when state needs inspection, reset, serialization, or a
public lifecycle.

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def counted(fn: Callable[P, R]) -> Callable[P, R]:
    calls = 0

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        nonlocal calls
        calls += 1
        return fn(*args, **kwargs)

    return wrapper


def register_handler(registry: dict[str, Callable[P, R]], key: str):
    """Register a callable in a dispatch table at module import time."""
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        if key in registry:
            raise ValueError(f"duplicate registration: {key}")
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return fn(*args, **kwargs)

        registry[key] = wrapper
        return wrapper
    return decorator
```

Self-registering decorators execute at import time, co-locating registration metadata directly with
the function definition. This satisfies the Open-Closed Principle (OCP) by making extensions purely
additive without editing a central registration function. Always preserve callable metadata with
`@wraps` and validate key collisions explicitly.

## When not to use

Do not stack decorators when the resulting order is unclear, or use a closure for state that must
be observed by callers. Prefer an explicit object or middleware pipeline in those cases.

## Tests

Test metadata, wrapper order, exception propagation, configuration capture, reentrancy, and async
variants separately.

## Framework examples

### Hugging Face Hub — reusable argument validation

```python
from huggingface_hub.utils import validate_hf_hub_args

@validate_hf_hub_args
def publish(repo_id: str, *, token: str | None = None) -> None:
    ...
```

The validator decorator centralizes boundary checks across Hub operations; a closure/decorator fits
because the policy is configured once and applied consistently. See the [Hub validator source](https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/utils/_validators.py).

### MLflow — tracing a callable boundary

```python
@mlflow.trace
def retrieve_and_rank(query: str) -> list[str]:
    return rank(retrieve(query))
```

`@mlflow.trace` adds observability without mixing tracing code into retrieval logic, which is the
classic cross-cutting concern for a decorator. See [MLflow manual tracing](https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/manual-tracing).

### LangChain — middleware around an agent

```python
agent = create_agent(
    model="provider:model",
    tools=[search],
    middleware=[TimingMiddleware()],
)
```

Middleware captures policy such as timing or authorization at the agent boundary while preserving
the core tool and model functions. See the [LangChain agents documentation](https://docs.langchain.com/oss/python/langchain/agents).

### LiteLLM — callback configuration

```python
response = completion(
    model="provider/model",
    messages=messages,
    callbacks=[UsageCallback()],
)
```

The callback receives provider-normalized events without coupling application code to one provider;
the wrapper boundary keeps telemetry separate from the request. See [LiteLLM custom callbacks](https://docs.litellm.ai/docs/observability/custom_callback).

## Trade-offs

Decorators centralize cross-cutting behavior, but stacking wrappers can obscure call order, metadata,
signatures, and exceptions. Use an explicit object or middleware pipeline when state or lifecycle must
be inspected by callers.

## ArjanCodes 2026 examples (adapted)

### Capture a feature policy in a closure

Use a closure when a feature is configured once and the resulting callable has one clear operation.
Keep the fallback visible and avoid capturing mutable request state.

```python
from collections.abc import Callable


def make_title_renderer(*, uppercase: bool) -> Callable[[str], str]:
    def render(title: str) -> str:
        value = title.strip()
        return value.upper() if uppercase else value

    return render


render_title = make_title_renderer(uppercase=True)
```

This fits a feature choice that is stable for the lifetime of a component. If the choice changes
per request, pass it as data instead. Adapted from the [2026 `features` examples](https://github.com/ArjanCodes/examples/tree/main/2026/features).

### Decorate a stable boundary, preserve metadata

```python
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def audit(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        record_call(fn.__qualname__)
        return fn(*args, **kwargs)

    return wrapper
```

The `wraps` call keeps the function discoverable to tools and callers. The [2026 `dctricks`
examples](https://github.com/ArjanCodes/examples/tree/main/2026/dctricks) demonstrate the same
principle across declaration-time helpers; use a class decorator or registry only when the class
boundary is the actual extension point.


## zedr clean-code-python diagnostics (adapted)

The [zedr clean-code-python table of contents](https://github.com/zedr/clean-code-python#table-of-contents)
warns against spreading side effects or hidden mutable state through helpers. A decorator can mark
one explicit boundary, but it should not silently mutate global application state.

```python
def split_name(full_name: str) -> tuple[str, str]:
    first, last = full_name.split(maxsplit=1)
    return first, last


def log_split(full_name: str) -> tuple[str, str]:
    result = split_name(full_name)
    record_name_split(full_name)
    return result
```

Keep the pure operation independently testable and put the deliberate effect in the orchestration
layer; use a decorator only when that cross-cutting boundary is stable.
