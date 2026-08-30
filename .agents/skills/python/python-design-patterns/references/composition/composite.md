# Composite

## Intent

Let callers treat one component and a group of components through the same interface.

## Use when

Use Composite for agent teams, workflow steps, middleware lists, tree-shaped configuration, or
pipelines where a group should be runnable like one unit.

## Why

The caller depends on one protocol while composition controls sequencing, parallelism, aggregation,
or failure policy.

## Example

```python
from collections.abc import Iterable
from typing import Protocol

class Check(Protocol):
    def run(self, value: str) -> bool: ...

class AllChecks:
    def __init__(self, checks: Iterable[Check]) -> None:
        self.checks = tuple(checks)

    def run(self, value: str) -> bool:
        return all(check.run(value) for check in self.checks)
```

This solves the need to add, remove, or nest checks without changing the caller.

## When not to use

Do not force a tree when children have incompatible lifecycle or result types. Use a Facade for a
fixed multi-step subsystem and a pipeline when order is the primary abstraction.

## Trade-offs and tests

Define ordering, short-circuiting, parallel failure, and child ownership. Test leaf and composite
objects independently, then test empty, one-child, and multi-child cases.

## Framework evidence

Agno's Agent/Team/Workflow composition and Google ADK's SequentialAgent, ParallelAgent, and
LoopAgent are representative composite designs. See the [framework matrix](../frameworks/index.md).

## Framework examples

### Agno — `Team` (adapted)

```python
from agno.team.team import Team

support_team = Team(
    name="support",
    members=[research_agent, writer_agent],
)
support_team.run("Answer the customer's question")
```

This solves treating several specialist agents as one runnable support unit. Agno's `Team` fits
Composite because the caller uses the team's `run()` interface while the team owns member
coordination and aggregation. See the official [Agno teams
documentation](https://docs.agno.com/teams/overview).

### Google ADK — `ParallelAgent` (adapted)

```python
from google.adk.agents import LlmAgent, ParallelAgent

research = ParallelAgent(
    name="parallel_research",
    sub_agents=[
        LlmAgent(name="web", model="model", instruction="Search the web"),
        LlmAgent(name="docs", model="model", instruction="Search internal docs"),
    ],
)
```

This solves running independent child agents behind one workflow node. It fits Composite because
the parent and each leaf share the agent contract, while the parent supplies parallel execution
policy. See the official [Google ADK workflow agents
documentation](https://adk.dev/agents/workflow-agents/).
