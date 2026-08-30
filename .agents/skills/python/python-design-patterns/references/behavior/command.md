# Command

## Intent

Represent an operation and its arguments as a value that can be queued, retried, logged, replayed,
or executed later.

## Use when

Use Command for deferred work, task queues, job orchestration, undo/replay, audit logs, or a
boundary where execution policy is separate from the operation itself.

## Why

The caller can schedule and observe work without knowing how it runs. It also gives retries,
timeouts, idempotency, and serialization a place to live.

## Example

```python
from dataclasses import dataclass
from typing import Protocol

class Command(Protocol):
    def execute(self) -> str: ...

@dataclass(frozen=True)
class SendMessage:
    sender: object
    text: str

    def execute(self) -> str:
        return self.sender.send(self.text)
```

This solves a queue or executor needing a uniform unit of work rather than a growing dispatch API.

## When not to use

Do not wrap a synchronous one-line call that is never deferred or inspected. A plain function is
the better command when no state or protocol is needed.

## Trade-offs and tests

Commands raise serialization, idempotency, retry ownership, and stale-state questions. Test
replay, failure, cancellation, and whether arguments capture values or mutable references.

## Framework evidence

vLLM queue APIs, TRL trainer callbacks/reward functions, and OpenRLHF/slime rollout hooks show
command-like deferred execution. Verify exact lifecycle semantics in the [matrix](../frameworks/index.md).

## Framework examples

### vLLM — `LLM.generate()` requests

vLLM solves the problem of submitting many inference requests while keeping batching and engine
execution out of the caller. Treating prompts plus sampling parameters as command data fits
Command because requests can be queued, retried by the surrounding job system, and collected
later as a uniform batch.

```python
from vllm import LLM, SamplingParams

prompts = ["Summarize A", "Summarize B"]
params = SamplingParams(temperature=0.2, max_tokens=64)
outputs = LLM(model="model-id").generate(prompts, params)
```

Adapted from the [vLLM offline inference guide](https://docs.vllm.ai/en/stable/serving/offline_inference/)
(stable, fetched 2026-08-30; adapted).

### slime — custom rollout hook

slime solves the problem of injecting rollout behavior into a reusable training loop without
forking that loop. A configured `custom_generate_function_path` acts as a deferred command
handler, so execution policy and rollout implementation can evolve independently.

```python
rollout_config = {
    "custom_generate_function_path": "my_project.rollouts:generate"
}
```

Adapted from [slime customization](https://thudm.github.io/slime/get_started/customization.html)
(latest, fetched 2026-08-30; adapted).
