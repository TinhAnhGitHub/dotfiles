# State, workflow, and recovery

## Intent

Represent legal lifecycle transitions, durable progress, pause/resume, retries, and recovery
explicitly instead of scattering flags and exception branches.

## Use when

Use a State Machine when behavior depends on current lifecycle state. Use a workflow/graph when
nodes, branching, persistence, human approval, or replay must be visible. Add checkpoint/memento
semantics when work must resume after process failure.

## Why

Explicit state makes invalid transitions, retry ownership, and recovery contracts testable. It
also prevents “running” from being confused with “scheduled”, “cancelled”, or “awaiting approval”.

## Example

```python
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

ALLOWED: dict[Status, set[Status]] = {
    Status.PENDING: {Status.RUNNING},
    Status.RUNNING: {Status.DONE, Status.FAILED},
    Status.DONE: set(),
    Status.FAILED: {Status.PENDING},
}
```

This solves invalid transitions hidden across unrelated methods.

## When not to use

Do not build a state machine for a single boolean with no transition rules. Use a small enum or
dataclass until persistence, branching, or recovery makes transitions a real contract.

## Trade-offs and tests

State models can grow rapidly. Test every allowed and rejected transition, restart behavior,
idempotency, timeout, retry, cancellation, and persisted-state compatibility.

## Framework evidence

LangGraph `StateGraph` plus checkpointing/interrupts, Google ADK workflow agents and session state,
Agno workflows, and OpenRLHF/slime rollout lifecycle boundaries are representative examples. Use
the [framework matrix](../frameworks/index.md).

## Framework examples

### LangGraph — checkpointed `StateGraph`

LangGraph solves the problem of pausing a graph for approval or failure and resuming it with the
same durable state. A compiled graph plus a thread-specific checkpointer fits State/Workflow
because transitions and recovery become explicit rather than hidden in exception branches.

```python
from langgraph.checkpoint.memory import InMemorySaver

app = workflow_builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "job-42"}}
app.invoke({"status": "pending"}, config=config)
```

Adapted from [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence/)
and [graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
(v1, fetched 2026-08-30; adapted).

### Google ADK — `SequentialAgent` and session state

Google ADK solves the problem of expressing ordered agent steps while keeping progress in scoped
session state. Workflow-agent composition fits this pattern because the lifecycle is visible as
named transitions and state can be inspected or resumed by the session owner.

```python
from google.adk.agents import LlmAgent, SequentialAgent

workflow = SequentialAgent(
    name="review_flow",
    sub_agents=[LlmAgent(name="draft"), LlmAgent(name="review")],
)
```

Adapted from [Google ADK workflow agents](https://adk.dev/agents/workflow-agents/)
and [session state](https://adk.dev/sessions/state/)
(2.x, fetched 2026-08-30; adapted).
