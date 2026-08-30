# Strategy

## Intent

Represent an interchangeable algorithm or policy behind one callable or protocol.

## Use when

Use Strategy when the orchestration is stable but ranking, retry, sampling, parsing, routing,
reward, or validation policy varies by configuration or runtime context.

## Why

The orchestrator stops accumulating conditionals, and each policy can be tested independently.
Python often needs only a function; use a class when the strategy owns state or dependencies.

## Example

```python
from collections.abc import Callable, Sequence

Ranker = Callable[[Sequence[str]], list[str]]

def choose(items: Sequence[str], rank: Ranker, limit: int) -> list[str]:
    return rank(items)[:limit]
```

This solves hard-coding one ranking policy into a retrieval workflow.

## When not to use

Keep a small fixed branch when the alternatives are local and unlikely to change. Avoid dozens of
strategies that share no meaningful contract.

## Trade-offs and tests

The interface must specify ordering, determinism, side effects, and error behavior. Test each
strategy against shared contract tests and test selection separately.

## Framework evidence

LangChain's provider/tool structured-output strategies, TRL reward functions, DSPy predictors and
optimizers, and LiteLLM Router policies are representative examples. See the [matrix](../frameworks/index.md).

## Framework examples

### LangChain — `ToolStrategy` as a structured-output policy

LangChain solves the problem of keeping agent orchestration stable while choosing how structured
output is enforced. Passing `ToolStrategy` as `response_format` fits Strategy because the output
policy is selected independently of the agent core loop.

```python
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class Review(BaseModel):
    sentiment: str

agent = create_agent(
    model="provider:model",
    tools=[],
    response_format=ToolStrategy(Review),
)
```

Adapted from [LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
(1.x, fetched 2026-08-30; adapted).

### LiteLLM — `Router` policy

LiteLLM `Router` solves provider selection, fallback, and load-balancing without changing the
caller completion contract. It fits Strategy because routing policy varies while the surrounding
application continues to submit the same request shape.

```python
from litellm import Router

router = Router(model_list=[{"model_name": "fast", "litellm_params": {"model": "provider/model"}}])
response = router.completion(model="fast", messages=[{"role": "user", "content": "Hi"}])
```

Adapted from the [LiteLLM documentation](https://docs.litellm.ai/)
(latest, fetched 2026-08-30; adapted).
