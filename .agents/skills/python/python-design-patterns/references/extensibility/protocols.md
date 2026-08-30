# Structural typing and interface segregation

## Intent

Describe the smallest behavior a collaborator needs with a structural `Protocol`, rather than
requiring every implementation to inherit from a broad base class.

## Use when

Use a narrow Protocol when unrelated objects should be interchangeable by behavior, or when a
consumer needs only one capability from a larger service.

## Why

Structural typing keeps contracts local, supports existing and test-double implementations, and
reduces the chance that a shared base class accumulates unrelated methods.

## Example

```python
from typing import Protocol

class Reader(Protocol):
    def read(self, size: int = -1) -> bytes: ...

def load(reader: Reader) -> bytes:
    return reader.read()
```

This solves a reader depending on a concrete file or stream hierarchy when it only needs `read()`.

## When not to use

Do not create a Protocol for a single private call with no substitution or contract boundary. A
function parameter is enough when the callable shape already says everything needed.

## Trade-offs and tests

Narrow Protocols can produce several small interfaces and do not enforce runtime behavior by
themselves. Test the behavioral contract, especially ordering, exceptions, partial reads, and
resource ownership.

## ArjanCodes OOP lessons (adapted)

### Prefer narrow structural Protocols to a god base class

When a consumer needs only one capability, a broad base class forces unrelated implementations to
inherit methods they cannot honor. Small Protocols solve that interface-segregation problem and fit
Python's structural typing because an object qualifies by having the required methods.

```python
from typing import Protocol

class Writer(Protocol):
    def write(self, data: bytes) -> int: ...

def copy(reader: Reader, writer: Writer) -> int:
    data = reader.read()
    return writer.write(data)
```

Adapted from [ArjanCodes' interfaces example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/04_god_base_class_after.py).

### Separate reader and writer contracts to avoid Liskov violations

When a subtype cannot support every operation promised by its base class—such as a read-only object
being forced to implement `write()`—the hierarchy violates substitutability. Separate reader and
writer Protocols solve the problem by making each function depend only on operations it can use.

```python
def read_all(source: Reader) -> bytes:
    return source.read()

def write_all(target: Writer, data: bytes) -> int:
    return target.write(data)
```

Adapted from [ArjanCodes' Liskov example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/05_substitutability_after.py).

Abstraction should still wait for a shared meaning and a demonstrated change axis. See the
accompanying [ArjanCodes OOP video](https://www.youtube.com/watch?v=RqcEK7sWesQ).

## Framework examples

### PydanticAI — typed dependency boundary (adapted)

When an agent tool needs an external service, directly depending on a concrete client couples the
tool to one implementation and makes tests awkward. A narrow `Protocol` defines only the capability
the tool uses; PydanticAI's typed `deps_type` and `RunContext` then make that boundary explicit.
Structural typing fits because any production client or test double with the required `search`
method can be injected without inheriting from a framework base class.

```python
from typing import Protocol
from pydantic_ai import Agent, RunContext

class SearchService(Protocol):
    async def search(self, query: str) -> list[str]: ...

agent = Agent("model", deps_type=SearchService)

@agent.tool
async def search(ctx: RunContext[SearchService], query: str) -> list[str]:
    return await ctx.deps.search(query)
```

Adapted from the official [PydanticAI dependencies documentation](https://pydantic.dev/docs/ai/core-concepts/dependencies/).
