# Composition over inheritance

## Intent

Assemble small objects or functions at runtime instead of creating a subclass for every
combination of independent features.

## Use when

Use this principle when a class varies along two or more axes—such as provider, retry policy,
format, transport, or authorization—and combinations are beginning to create subclasses or
conditional attributes.

## Why

Composition localizes each feature, makes deletion and testing easier, and lets the caller choose
the combination at runtime. It follows the central lesson of the Python patterns guide: named
patterns are secondary to the design principle behind them.

## Example

```python
from collections.abc import Callable

Emit = Callable[[str], None]
Filter = Callable[[str], bool]

def make_logger(emit: Emit, accept: Filter) -> Callable[[str], None]:
    def log(message: str) -> None:
        if accept(message):
            emit(message)
    return log
```

This solves the need for “file logger”, “filtered logger”, and “filtered socket logger” classes
without multiplying types.

## When not to use

Keep a small cohesive class when the variants are fixed, the invariant is shared, and composition
would make the public API harder to understand. Do not split every line into an object.

## Trade-offs and tests

Composition adds wiring and can hide call order. Test each component alone and at least one
assembled configuration; document ownership, ordering, and error propagation.

## Framework examples

### LangGraph — `StateGraph` (adapted)

```python
from typing_extensions import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    question: str

builder = StateGraph(State)
builder.add_node("retrieve", retrieve)
builder.add_node("answer", answer)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "answer")
builder.add_edge("answer", END)
workflow = builder.compile()
```

This solves a workflow with independently replaceable retrieval and answer steps. `StateGraph`
fits composition over inheritance because the application assembles nodes and edges at runtime
instead of creating a subclass for every workflow variant. See the official [LangGraph graph API
documentation](https://docs.langchain.com/oss/python/langgraph/graph-api).

### Google ADK — `SequentialAgent` (adapted)

```python
from google.adk.agents import LlmAgent, SequentialAgent

workflow = SequentialAgent(
    name="support_flow",
    sub_agents=[
        LlmAgent(name="draft", model="model", instruction="Draft a reply"),
        LlmAgent(name="review", model="model", instruction="Review the draft"),
    ],
)
```

This solves a fixed sequence of specialist steps while keeping each agent independently
replaceable. It fits the principle because the workflow is assembled from collaborators rather
than encoded in an inheritance tree. See the official [Google ADK workflow agents
documentation](https://adk.dev/agents/workflow-agents/).

## ArjanCodes OOP lessons (adapted)

### Compose capabilities, not implementation inheritance

When reuse is about independent capabilities—such as filtering and emitting—inheritance creates a
subclass matrix and couples unrelated changes. Compose those capabilities so the problem is solved
by wiring, while each collaborator remains replaceable and testable.

```python
from collections.abc import Callable

class Logger:
    def __init__(self, emit: Callable[[str], None], accept: Callable[[str], bool]) -> None:
        self.emit = emit
        self.accept = accept

    def log(self, message: str) -> None:
        if self.accept(message):
            self.emit(message)
```

Adapted from [ArjanCodes' code-reuse example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/01_code_reuse_after.py).

### Use options, functions, or strategies for independent axes

When two choices vary independently, a frozen value object plus a callable often communicates the
design better than subclasses for every combination. This solves feature-axis explosion while
keeping the caller's choices explicit at the assembly point.

```python
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class RenderOptions:
    uppercase: bool = False

def render(text: str, transform: Callable[[str], str] = str,
           options: RenderOptions = RenderOptions()) -> str:
    value = transform(text)
    return value.upper() if options.uppercase else value
```

Adapted from [ArjanCodes' feature-variation example](https://github.com/ArjanCodes/examples/blob/main/2026/oop/03_feature_variation_after.py).

### Delay abstraction until shared meaning is proven

When there is only one implementation or no demonstrated change axis, a small function is the
clearest solution. This avoids premature abstraction; introduce a Protocol or collaborator only
after multiple implementations share a meaningful contract. The accompanying lesson is [ArjanCodes'
OOP video](https://www.youtube.com/watch?v=RqcEK7sWesQ), and the example is [premature-abstraction
after](https://github.com/ArjanCodes/examples/blob/main/2026/oop/06_premature_abstraction_after.py).

## Related patterns

[Adapter](../composition/adapter.md), [Decorator](../composition/decorator.md), [Strategy](../behavior/strategy.md),
and [Dependency Injection](../extensibility/registry-di.md) are common implementations of this principle.
