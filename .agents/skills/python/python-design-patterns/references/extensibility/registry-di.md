# Registry and dependency injection

## Intent

Make implementations discoverable and dependencies replaceable without editing a central
dispatcher or reaching into global state.

## Use when

Use a Registry when independent modules or plugins add named implementations. Use Dependency
Injection when a component needs a service, policy, client, or clock that tests or deployments may
replace.

## Why

Registration separates extension from core code; injection makes ownership and test seams explicit.
Together they support provider selection, tool systems, callbacks, and model backends.

## Example

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")
FACTORIES: dict[str, Callable[[], T]] = {}

def register(name: str):
    def decorator(factory: Callable[[], T]) -> Callable[[], T]:
        if name in FACTORIES:
            raise ValueError(f"duplicate registration: {name}")
        FACTORIES[name] = factory
        return factory
    return decorator
```

This solves a growing import-and-branch list while keeping registration testable.

## When not to use

Use a constructor parameter for one or two dependencies. Avoid import-time global registries when
registration order, isolation, or test parallelism is difficult to control.

## Trade-offs and tests

Registries introduce string keys, import-order coupling, duplicate-name failures, and hidden global
state. Define discovery, override, lifecycle, and thread-safety rules. Test isolated registries,
duplicate names, missing names, and injected fakes.

## Framework evidence

Transformers AutoClass, qwen-agent tool registries, PydanticAI capabilities/dependencies, verl
worker selection, and slime import-path hooks illustrate this family. See the [framework matrix](../frameworks/index.md).

## Framework examples

### Transformers — `AutoConfig.register()` and `AutoModel.register()`

Transformers solves the problem of making a custom model discoverable by configuration without
editing the loader central dispatcher. These registration calls fit Registry, while the model
class receives collaborators through normal construction rather than global lookups.

```python
from transformers import AutoConfig, AutoModel

AutoConfig.register("my_model", MyConfig)
AutoModel.register(MyConfig, MyModel)
model = AutoModel.from_config(MyConfig())
```

Adapted from the [Transformers custom models guide](https://huggingface.co/docs/transformers/en/custom_models)
(latest, fetched 2026-08-30; adapted).

### PydanticAI — `deps_type` and tool capabilities

PydanticAI solves the problem of adding tools that need runtime services without importing a
process-wide client. Typed dependencies fit Dependency Injection because ownership and test
substitution are explicit at the agent boundary.

```python
from pydantic_ai import Agent, RunContext

agent = Agent("provider:model", deps_type=SearchClient)

@agent.tool
def search(ctx: RunContext[SearchClient], query: str) -> str:
    return ctx.deps.search(query)
```

Adapted from [PydanticAI dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/)
(latest, fetched 2026-08-30; adapted).
