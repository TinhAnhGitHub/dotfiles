# Observer and publish/subscribe

## Intent

Notify independent listeners when an event or state change occurs without hard-coding every
consumer into the publisher.

## Use when

Use Observer for telemetry, callbacks, plugin hooks, training events, tracing, cache invalidation,
or UI/domain notifications with multiple optional consumers.

## Why

The publisher owns event timing while listeners can be added or removed independently. It is a
natural extension point for cross-cutting behavior.

## Example

```python
from collections.abc import Callable

Listener = Callable[[str], None]

class EventBus:
    def __init__(self) -> None:
        self._listeners: list[Listener] = []

    def subscribe(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def publish(self, event: str) -> None:
        for listener in tuple(self._listeners):
            listener(event)
```

This solves optional logging and metrics consumers without adding branches to the core operation.

## When not to use

Use a direct function call when there is one required consumer. Do not hide critical business
control flow in a global event bus.

## Trade-offs and tests

Define ordering, failure isolation, duplicate delivery, unsubscribe behavior, and backpressure.
Test listener failure and shutdown as well as successful notification.

## Framework evidence

Transformers callbacks, MLflow tracing, LangChain middleware, and LiteLLM callbacks are concrete
examples. Use the [framework matrix](../frameworks/index.md) for current source links.

## Framework examples

### Transformers — `TrainerCallback`

Transformers solves the problem of adding metrics, checkpoints, or notifications without editing
the Trainer loop. The callback is an Observer because the Trainer publishes lifecycle events and
independent listeners react to them.

```python
from transformers import TrainerCallback

class MetricsSink(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            metrics_store.write(logs)

trainer = Trainer(..., callbacks=[MetricsSink()])
```

Adapted from the [Transformers Trainer callbacks guide](https://github.com/huggingface/transformers/blob/main/docs/source/en/trainer_callbacks.md)
(main, fetched 2026-08-30; adapted).

### LiteLLM — callback telemetry

LiteLLM solves the problem of observing normalized provider calls without placing telemetry
branches in every call site. A custom callback fits Observer because the routing operation emits
events to optional listeners that can be added independently.

```python
from litellm import completion

response = completion(
    model="provider/model",
    messages=[{"role": "user", "content": "Hello"}],
    callbacks=[telemetry_callback],
)
```

Adapted from [LiteLLM custom callbacks](https://docs.litellm.ai/docs/observability/custom_callback)
(latest, fetched 2026-08-30; adapted).
