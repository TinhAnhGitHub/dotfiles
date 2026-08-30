# AI-system boundaries

## Intent

Separate model/provider access, tools, orchestration, state, evaluation, telemetry, and execution
resources behind explicit contracts.

## Use when

Use these boundaries when an agent system must swap providers, add tools, support sync and async
execution, persist state, run in parallel, or connect rollout/training code to an inference engine.

## Why

AI systems combine unstable external APIs with long-lived workflows and expensive resources. Small
protocols and adapters keep those concerns replaceable and make failures observable.

## Mapping common problems to patterns

| Problem | Pattern combination |
|---|---|
| Provider-specific request/response shapes | Adapter + Facade + typed Protocol |
| Tool discovery and safe extension | Registry + Dependency Injection + Command |
| Agent/team/workflow composition | Composite + State Machine + Observer |
| Human approval and resume | State Machine + Memento/checkpoint + Command |
| Rollout and training coupling | Adapter + Strategy + actor/worker delegation |
| Provider failure and load balancing | Strategy + Decorator/middleware + retry policy |
| Trace and evaluation integration | Observer + context propagation + immutable event record |

## Example

```python
from typing import Protocol

class Model(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...

class Agent:
    def __init__(self, model: Model, tools: tuple[object, ...]) -> None:
        self.model = model
        self.tools = tools
```

This solves an agent class importing one provider, one tool implementation, and one telemetry
system directly.

## When not to use

Do not create an abstraction for a single stable internal call. Avoid wrapping every framework
object; abstract only the behavior that the application actually owns.

## Trade-offs and tests

Boundaries can hide streaming, token accounting, retries, cancellation, and provider-specific
features. Test the protocol contract, adapter fidelity, failure mapping, trace context, and end-to-
end lifecycle with fakes before adding live framework integration tests.

## Framework evidence

The [framework matrix](../frameworks/index.md) links concrete examples from verl, LangGraph,
PydanticAI, Agno, Google ADK, vLLM, OpenRLHF, slime, DSPy, TRL, OpenAI, and LiteLLM.

## Framework examples

### LangGraph — `StateGraph.compile()` with a checkpointer

LangGraph solves the problem of mixing graph orchestration, durable state, and node
implementation in one agent class. A typed state boundary plus compilation fits this pattern
because provider calls, workflow transitions, and persistence remain separately replaceable.

```python
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    answer: str

builder = StateGraph(State)
builder.add_node("answer", answer_node)
builder.add_edge(START, "answer")
builder.add_edge("answer", END)
app = builder.compile(checkpointer=InMemorySaver())
```

Adapted from the [LangGraph graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
and [persistence guide](https://docs.langchain.com/oss/python/langgraph/persistence/)
(v1, fetched 2026-08-30; adapted).

### verl — role/worker mapping

verl solves the problem of coupling PPO control flow to a particular actor, critic, or rollout
backend. The role-to-worker mapping is an explicit adapter boundary, so the orchestration owns
coordination while workers own provider and execution details.

```python
role_worker_mapping = {
    "actor": ActorRolloutWorker,
    "critic": CriticWorker,
    "rollout": RolloutWorker,
}
```

Adapted from [verl PPO architecture](https://verl.readthedocs.io/en/latest/examples/ppo_code_architecture.html)
(latest, fetched 2026-08-30; adapted).
