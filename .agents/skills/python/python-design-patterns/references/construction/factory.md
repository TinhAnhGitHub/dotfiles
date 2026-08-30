# Factory and provider selection

## Intent

Move the decision about which implementation to construct behind a stable function or registry.

## Use when

Use a Factory when the concrete implementation depends on configuration, environment, model name,
provider, or a serialized type tag, and callers should not know construction details.

## Why

Construction policy is centralized and testable. A callable factory is often more Pythonic than a
parallel Abstract Factory hierarchy.

## Example

```python
from collections.abc import Callable

class Store:
    def get(self, key: str) -> str: ...

def make_store(kind: str) -> Store:
    factories: dict[str, Callable[[], Store]] = {
        "memory": MemoryStore,
        "file": FileStore,
    }
    try:
        return factories[kind]()
    except KeyError as exc:
        raise ValueError(f"unsupported store: {kind}") from exc
```

This solves callers importing and branching over every concrete store implementation.

## When not to use

Use direct construction when there is one implementation or the caller genuinely owns the choice.
Do not let a factory become an untyped global switchboard.

## Trade-offs and tests

Factories can hide dependencies and become difficult to navigate. Test every supported key,
unknown configuration, constructor errors, and dependency injection of custom factories.

## Framework evidence

Transformers AutoClass registration, qwen-agent model/tool factories, MLflow model flavors, and
verl engine-worker selection are representative examples. See the [framework matrix](../frameworks/index.md).

## Framework examples

### Transformers — `AutoConfig.register()` and `AutoModel.register()` (adapted)

```python
from transformers import AutoConfig, AutoModel

AutoConfig.register("my-model", MyConfig)
AutoModel.register(MyConfig, MyModel)

model = AutoModel.from_config(MyConfig(hidden_size=768))
```

This solves selecting a concrete model implementation from a configuration type without branching
at every call site. It fits Factory because the AutoClass registry centralizes the construction
decision and lets callers request the stable `AutoModel` interface. See the official [Transformers
custom models documentation](https://huggingface.co/docs/transformers/en/custom_models).

### qwen-agent — `get_chat_model` (adapted)

```python
from qwen_agent.llm import get_chat_model

llm = get_chat_model({
    "model": "qwen-plus",
    "model_server": "dashscope",
})
```

This solves choosing a chat-model backend from deployment configuration while keeping agent code
provider-agnostic. It fits Factory because `get_chat_model` hides provider-specific construction
behind one selection point. See the official [qwen-agent LLM
documentation](https://github.com/QwenLM/Qwen-Agent/blob/main/qwen-agent-docs/website/content/en/guide/core_moduls/llm.md).

## ArjanCodes OOP lessons (adapted)

### Use a frozen config and a factory for values, not type explosion

When output differences are configuration values, creating `PrettyJsonExporter`,
`CompactJsonExporter`, and similar subclasses multiplies types without adding domain meaning. A
frozen config plus a callable factory solves that construction problem while keeping the choice
validated and explicit.

```python
import json
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class FormatOptions:
    kind: Literal["json", "text"] = "json"
    pretty: bool = False

def make_formatter(options: FormatOptions):
    if options.kind == "json":
        indent = 2 if options.pretty else None
        return lambda value: json.dumps(value, indent=indent)
    return str
```

Adapted from [ArjanCodes' configuration-subclasses example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/02_configuration_subclasses_after.py).

### Select independent behavior with functions or strategies

When the construction choice and the behavior choice vary on separate axes, pass the behavior as a
callable instead of adding another family of subclasses. This keeps the factory small and makes
each strategy straightforward to replace in tests.

```python
from collections.abc import Callable

def make_processor(normalize: Callable[[str], str] = str) -> Callable[[str], str]:
    return lambda value: normalize(value.strip())
```

Adapted from [ArjanCodes' feature-variation example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/03_feature_variation_after.py).

### Delay the factory abstraction until construction varies

When there is one concrete implementation and no proven change axis, direct construction is clearer
than a factory. Add the factory once multiple implementations share a meaningful selection
contract; see [ArjanCodes' premature-abstraction example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/06_premature_abstraction_after.py)
and the accompanying [OOP video](https://www.youtube.com/watch?v=RqcEK7sWesQ).
