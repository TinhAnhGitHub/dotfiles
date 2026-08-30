# Sentinel, lazy evaluation, and shared resources

## Intent

Represent boundary states precisely and defer or reuse expensive work deliberately.

## Use when

Use a Sentinel when `None`, an empty value, and “argument omitted” have different meanings. Use
lazy evaluation when a result may not be needed. Use pooling or shared immutable state when setup
is expensive and ownership is explicit.

## Why

Identity-based sentinels prevent accidental conflation. Laziness saves work and memory, while
controlled reuse avoids repeatedly creating clients, tokenizers, connections, or model state.

## Example

```python
_MISSING = object()

def get_setting(settings: dict[str, str], key: str, default: object = _MISSING) -> str:
    if key in settings:
        return settings[key]
    if default is _MISSING:
        raise KeyError(key)
    return default  # type: ignore[return-value]
```

This solves the ambiguity between an omitted default and an explicitly supplied `None`-like value.

## When not to use

Do not add a sentinel when `None` is the only valid absence state. Do not use global caches or
pools without a clear invalidation, thread-safety, and shutdown policy.

## Trade-offs and tests

Sentinel identity does not automatically survive serialization. Lazy code complicates timing and
errors; shared resources complicate isolation. Test omission, explicit values, cache misses,
invalidation, concurrency, and cleanup.

## Framework examples

### vLLM — cached engine construction

vLLM solves the problem of repeatedly constructing an expensive inference engine when a process
serves multiple requests. A lazy, keyed factory fits this Python-specific pattern because the
engine is created only on first use and reused by identity; the application still owns cache
invalidation and shutdown.

```python
from functools import lru_cache
from vllm import LLM

@lru_cache(maxsize=2)
def engine(model_id: str) -> LLM:
    return LLM(model=model_id)

outputs = engine("model-id").generate(["hello"])
```

Adapted from the [vLLM offline inference guide](https://docs.vllm.ai/en/stable/serving/offline_inference/)
(stable, fetched 2026-08-30; adapted).
