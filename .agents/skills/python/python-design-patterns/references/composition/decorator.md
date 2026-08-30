# Decorator

## Intent

Wrap an object or callable with another object that exposes the same contract and adds one focused
behavior.

## Use when

Use a Decorator for orthogonal concerns such as tracing, retries, caching, authorization, logging,
rate limits, or output transformation that may be stacked or selected at runtime.

## Why

Each concern remains independently testable, and combinations do not require a new subclass. The
wrapper can preserve the original contract while making the added behavior explicit in wiring.

## Example

```python
from collections.abc import Callable

def with_prefix(fn: Callable[[str], str], prefix: str) -> Callable[[str], str]:
    def wrapped(value: str) -> str:
        return prefix + fn(value)
    return wrapped
```

This solves repeated output decoration without modifying the wrapped function.

## When not to use

Prefer a plain function when there is only one transformation. Avoid deep decorator stacks when
ordering, error ownership, or signature visibility matters more than reuse.

## Trade-offs and tests

Decorator order is behavior. Preserve metadata with `functools.wraps`, preserve sync/async shape,
and test ordering, exceptions, cancellation, and introspection. MLflow tracing, Transformers
callbacks, and LiteLLM callbacks are useful real-world evidence; see the [matrix](../frameworks/index.md).

## Framework examples

### MLflow — `@mlflow.trace` (adapted)

```python
import mlflow

@mlflow.trace(name="answer")
def answer(question: str) -> str:
    return model.generate(question)
```

This solves adding trace spans and captured inputs/outputs without putting telemetry into the
model's business logic. The decorator fits because it wraps the same callable contract and adds
one cross-cutting behavior that can be composed with other wrappers. See the official [MLflow
manual tracing documentation](https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/manual-tracing).

### Hugging Face Hub — `@validate_hf_hub_args` (adapted)

```python
from huggingface_hub.utils import validate_hf_hub_args

@validate_hf_hub_args
def fetch_model(repo_id: str, *, revision: str | None = None):
    return download_from_hub(repo_id, revision=revision)
```

This solves repeating repository-id and revision validation at Hub API boundaries. It fits
Decorator because validation is attached around the existing function while its main download
responsibility remains unchanged. See the official [Hugging Face Hub validator
source](https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/utils/_validators.py).
