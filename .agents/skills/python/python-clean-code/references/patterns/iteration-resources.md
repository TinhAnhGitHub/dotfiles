# Iteration and resource ownership

## Use when

Use iterables and generators for lazy or streaming data, and context managers when acquisition and
cleanup must be tied to a lexical scope.

## Why

Lazy iteration controls memory and latency. Context managers make ownership visible and ensure
cleanup on success, exceptions, and early exit.

```python
from collections.abc import Iterable, Iterator

def nonempty(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        if line.strip():
            yield line
```

Accept `Iterable` when callers need not provide a collection; return `Iterator` when output is
single-pass. Use `itertools` before inventing a custom stream helper.

## Tests and pitfalls

Test laziness, single-pass behavior, early termination, cleanup, and backpressure. Never assume an
async generator is concurrent merely because it yields values.

## Framework examples

### OpenAI Python SDK — owned streaming

```python
with client.responses.stream(model="provider:model", input=prompt) as stream:
    for event in stream:
        consume(event)
```

The context manager ties stream cleanup to the lexical scope, while iteration lets the caller
process events incrementally instead of buffering the response. See the SDK’s [streaming helpers](https://github.com/openai/openai-python/blob/main/helpers.md).

### LangGraph — consume graph updates lazily

```python
for update in graph.stream({"topic": topic}, stream_mode="updates"):
    render(update)
```

`stream()` exposes workflow progress as a single-pass iterable, solving the latency and memory cost
of waiting for a complete graph result. See the [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).

### Hugging Face Hub — iterate paginated results

```python
from collections.abc import Iterator


def model_ids() -> Iterator[str]:
    for model in HfApi().list_models(filter="text-generation"):
        yield model.id
```

The API iterator hides pagination and keeps discovery lazy, so callers need not materialize every
Hub result. See the [HfApi reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api).

## When not to use

Do not use a generator when callers need random access, repeated traversal, or a small collection
whose eager construction is clearer. Do not add a context manager when no resource is acquired or
owned by the scope.

## Trade-offs

Lazy iteration reduces memory use and latency, but iterators are often single-pass and defer errors
until consumption. Context managers make cleanup reliable while requiring ownership and lifetime to
be explicit at the call site.

## ArjanCodes 2026 examples (adapted)

### Build a lazy generator pipeline

Generators are useful when each stage can produce one item at a time. Keep stages composable so
the consumer controls how far the source is read.

```python
from collections.abc import Iterable, Iterator


def parse_rows(lines: Iterable[str]) -> Iterator[tuple[str, int]]:
    for line in lines:
        name, raw_count = line.rstrip("\n").split(",", maxsplit=1)
        yield name, int(raw_count)


def positive_rows(rows: Iterable[tuple[str, int]]) -> Iterator[tuple[str, int]]:
    yield from (row for row in rows if row[1] > 0)
```

Nothing is parsed until iteration begins, and no intermediate list is required. Adapted from the
[2026 `generators` examples](https://github.com/ArjanCodes/examples/tree/main/2026/generators),
which also cover composition, `send`, async generators, and backpressure.

### Make feature choices explicit in the pipeline

When a workflow has optional behavior, pass a stage or choose a small pipeline rather than burying
feature flags inside a generator.

```python
def consume(source: Iterable[str], *, normalize: bool = False) -> list[str]:
    rows: Iterable[str] = source
    if normalize:
        rows = (row.strip().lower() for row in rows)
    return list(rows)
```

This keeps eager materialization at the boundary where it is intentional. See the [2026 `clean`
examples](https://github.com/ArjanCodes/examples/tree/main/2026/clean) and [feature examples](https://github.com/ArjanCodes/examples/tree/main/2026/features).

### Test the ownership contract

```python
def test_generator_is_lazy() -> None:
    consumed = False

    def source() -> Iterator[str]:
        nonlocal consumed
        consumed = True
        yield "a"

    rows = consume(source())
    assert consumed
    assert rows == ["a"]
```

For a resource-owning generator, add a test that closes or exhausts it and observes cleanup. For
bounded pipelines, assert that the producer cannot outrun the consumer indefinitely.


## zedr clean-code-python diagnostics (adapted)

The [zedr clean-code-python table of contents](https://github.com/zedr/clean-code-python#table-of-contents)
separates filtering from effects and asks whether a function works at one abstraction level. A lazy
filter keeps the source traversal separate from the action.

```python
from collections.abc import Iterable, Iterator


def active_clients(clients: Iterable[Client]) -> Iterator[Client]:
    return (client for client in clients if client.active)


def email_clients(clients: Iterable[Client]) -> None:
    for client in active_clients(clients):
        send_email(client)
```

The generator is reusable and lazy; the sending function owns the side effect. Test the filter
without a mail service, then test one focused delivery integration.

### The Lazy Loading Pattern: Making Python Applications Feel Instant

In ["The Lazy Loading Pattern: How to Make Python Programs Feel Instant"](https://www.youtube.com/watch?v=ENnDxEOAKKc) and its [companion repository](https://github.com/ArjanCodes/examples/tree/main/2025/lazy), Arjan demonstrates how combining lazy evaluation, generators, caching, and background preloading eliminates sluggish startup times and memory bloat.

#### The 4-step progressive refactoring from eager to responsive

1. **Eliminate Startup Latency (Eager $\to$ Lazy)**: Moving `load_sales()` from the global application startup into the specific action branches guarantees the CLI or API boots in under 10ms.
2. **Stream with Generators for Bounded Memory ($O(N) \to O(1)$)**: Replace `[row for row in reader]` with a generator that yields rows sequentially. Consumers that only require top-$N$ elements or aggregations can terminate early without loading millions of rows into RAM.
3. **Prevent Repeated I/O via Caching**:
   - For pure static computations: use stdlib `functools.cache`.
   - For volatile external services (e.g. currency rates, remote pricing, auth tokens): use a **TTL (Time-To-Live) cache** to balance instant response with bounded data freshness.
4. **Preload Proactively in Background**: Spawn a lightweight daemon thread on startup (`threading.Thread(target=..., daemon=True).start()`) to warm expensive caches during interactive user think-time.

#### Generator streaming vs. Eager materialization

```python
# ❌ EAGER: Allocates millions of dicts in RAM before caller can inspect a single row
def load_sales_eager(path: str) -> list[dict[str, str]]:
    with open(path) as f:
        return list(csv.DictReader(f))  # 💥 High memory consumption and 10s startup stall

# ✅ LAZY STREAMING: Yields row by row; memory remains bounded at O(1)
def load_sales_stream(path: str) -> Iterator[dict[str, str]]:
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# ✅ EARLY TERMINATION: Consumes only the required slice, avoiding unwanted I/O
def sample_total(path: str, limit: int = 10_000) -> float:
    total = 0.0
    for i, sale in enumerate(load_sales_stream(path), start=1):
        total += float(sale["amount"])
        if i >= limit:
            break
    return total
```

#### The Time-To-Live (TTL) cache pattern for external APIs

```python
import time
from functools import wraps
from typing import Any, Callable

def ttl_cache(seconds: int) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Cache function results for a bounded duration to avoid stale API data drift."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache_data: dict[tuple[Any, ...], Any] = {}
        cache_time: dict[tuple[Any, ...], float] = {}

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(kwargs.items()))
            now = time.time()
            if key in cache_data and (now - cache_time[key]) < seconds:
                return cache_data[key]
            result = func(*args, **kwargs)
            cache_data[key] = result
            cache_time[key] = now
            return result
        return wrapper
    return decorator

@ttl_cache(seconds=60)
def get_live_rates() -> dict[str, float]:
    """Fetched on demand, cached for 60 seconds, then refreshed automatically."""
    return fetch_currency_rates_api()
```

#### Proactive background preloading pattern

```python
import threading
from functools import cache

@cache
def compute_sales_metrics(path: str) -> dict[str, float]:
    return {"total": sum(float(r["amount"]) for r in load_sales_stream(path))}

def preload_data(path: str) -> None:
    """Preload data in a background daemon thread while user reads the menu."""
    threading.Thread(target=lambda: compute_sales_metrics(path), daemon=True).start()
```

#### The 3 golden rules of lazy resources

| Rule | Problem | Clean Remedy |
|---|---|---|
| **1. Never `@cache` a generator** | Caching stores the generator iterator itself, which exhausts on first run and returns `[]` on second run. | Cache the materialized collection (`tuple`) or the aggregate calculation result. |
| **2. Avoid I/O in properties** | `@property` implies $O(1)$ attribute access; hidden queries in properties surprise callers in logging/repr. | Make expensive calls explicit methods (`fetch_sales()`, `load_rates()`). |
| **3. Bound external cache lifetime** | Permanent caching of live APIs causes silent data staleness and drift. | Use `@ttl_cache(seconds=N)` to bound staleness to an acceptable window. |

