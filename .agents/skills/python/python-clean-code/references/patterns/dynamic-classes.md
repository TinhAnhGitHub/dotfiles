# Dynamic classes and attributes

## Use when

Use properties, descriptors, class decorators, and `__init_subclass__` when a repeated invariant
or class-registration rule must be centralized and remain visible at the declaration boundary.

## Why

These hooks eliminate repetitive boilerplate while preserving a normal Python-facing API. They
should narrow a stable rule, not create an invisible programming language.

## Order of preference

1. Plain method or property.
2. Descriptor for reusable attribute behavior.
3. Class decorator or `__init_subclass__` for declaration-time registration.
4. Metaclass only when class creation itself must be coordinated.

## Tests

Test descriptor lookup precedence, class creation, subclass registration, inheritance, error
messages, and serialization. Keep dynamic behavior typed and document the generated surface.

## Framework examples

### Transformers — declaration-time AutoClass registration

```python
AutoConfig.register("my-model", MyConfig)
AutoModel.register(MyConfig, MyModel)
```

Registration attaches a custom implementation to the framework’s normal loading surface, solving
extension without changing `AutoModel` itself. See Transformers [custom models](https://huggingface.co/docs/transformers/en/custom_models).

### qwen-agent — tool registry extension

```python
register_tool("search", SearchTool)
tool = TOOL_REGISTRY["search"](**config)
```

The registry centralizes name-to-class discovery while keeping the declaration boundary visible;
this is preferable to hidden metaclass behavior for replaceable tools. See the qwen-agent [agent guide](https://github.com/QwenLM/Qwen-Agent/blob/main/qwen-agent-docs/website/content/en/guide/core_moduls/agent.md).

### Agno — registering toolkit capabilities

```python
class SearchToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="search")
        self.register(self.search)
```

`Toolkit.register` turns a method into a discoverable capability at class setup time, solving
repeated tool metadata and registration boilerplate without requiring a metaclass. See the [Agno SDK](https://docs.agno.com/sdk/introduction).

## When not to use

Do not introduce descriptors, class hooks, or metaclasses for a one-off attribute or a small fixed
set of classes. Prefer a plain method or property when the invariant is already local and obvious.

## Trade-offs

Dynamic hooks reduce repeated registration and validation code, but they complicate introspection,
inheritance, error reporting, and serialization. Keep the generated surface narrow and documented.

## ArjanCodes 2026 examples (adapted)

### Register declarations with a typed class decorator

When every declared event needs the same dataclass behavior and registry entry, a small class
decorator keeps the rule at the declaration site.

```python
from dataclasses import dataclass
from typing import Any, dataclass_transform

EVENTS: dict[str, type[Any]] = {}


@dataclass_transform()
def event(cls: type[Any]) -> type[Any]:
    registered = dataclass(cls)
    EVENTS[registered.__name__] = registered
    return registered


@event
class UserCreated:
    user_id: int
```

Adapted from the [2026 `dctricks/2_autoregistry.py`](https://github.com/ArjanCodes/examples/blob/main/2026/dctricks/2_autoregistry.py).
The registry should have one owner and a documented duplicate-name policy; otherwise an explicit
registration call is easier to debug.

### Reuse validation with a descriptor

```python
class Positive:
    def __set_name__(self, owner: type[object], name: str) -> None:
        self.name = name

    def __get__(
        self,
        instance: object | None,
        owner: type[object] | None = None,
    ) -> int | Positive:
        return self if instance is None else instance.__dict__[self.name]

    def __set__(self, instance: object, value: int) -> None:
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")
        instance.__dict__[self.name] = value


class RetryConfig:
    attempts = Positive()
```

Descriptors pay off when the same storage and validation rule appears across several classes. The
[2026 descriptor examples](https://github.com/ArjanCodes/examples/tree/main/2026/descriptors) include
minimal, non-data, lazy, and validated variants; test class access, instance access, assignment,
and the error path before generalizing one.
