# Evaluating Prompts, Agents, Traces, and Conversations

## Contents

1. Prompt evaluation and versioning
2. Prompt optimization
3. Agent evaluation workflow
4. RAG and tool evaluation
5. Existing-trace evaluation
6. Multi-turn evaluation and simulation
7. Workflow automation patterns

## 1. Prompt evaluation and versioning

Evaluate a prompt as a versioned component of the app, not an untracked string.

### Register

```python
import mlflow

prompt = mlflow.genai.register_prompt(
    name="support-answer",
    template=[
        {
            "role": "system",
            "content": "Answer using policy context. Do not invent exceptions.",
        },
        {"role": "user", "content": "{{question}}"},
    ],
    commit_message="Initial policy-grounded prompt",
    tags={"owner": "support-ai", "task": "support_qa"},
    model_config={"temperature": 0.0, "max_tokens": 500},
)
```

### Load and format

```python
prompt = mlflow.genai.load_prompt("prompts:/support-answer/3")
messages = prompt.format(question="What is the refund window?")
```

Use immutable version URIs in evaluations and production. Aliases such as `@latest` or
`@production` are convenient for promotion but can move and may be cached.

### Systematic iteration

```python
def build_predict_fn(prompt_uri: str):
    prompt = mlflow.genai.load_prompt(prompt_uri)

    @mlflow.trace
    def predict_fn(question: str) -> str:
        return call_model(prompt.format(question=question))

    return predict_fn

for uri in ["prompts:/support-answer/3", "prompts:/support-answer/4"]:
    mlflow.genai.evaluate(
        data=held_out_dataset,
        predict_fn=build_predict_fn(uri),
        scorers=scorers,
        model_id=uri,
    )
```

Keep dataset, model, decoding parameters, tools, and scorer suite fixed when isolating the
effect of a prompt change.

### Prompt workflow

1. Create/modify prompt on a development dataset.
2. Register a new immutable prompt version with rationale.
3. Evaluate on held-out data.
4. Compare aggregate, slice, and failure-level results.
5. Run regression gates.
6. Promote an alias only after approval.
7. Monitor production traces tagged/linked with prompt version.
8. Use new failures in the next prompt iteration.

## 2. Prompt optimization

Current MLflow exposes `mlflow.genai.optimize_prompts()` with optimizer implementations
such as `GepaPromptOptimizer` and `MetaPromptOptimizer` in newer versions.

```python
from mlflow.genai.optimize import GepaPromptOptimizer

optimization = mlflow.genai.optimize_prompts(
    predict_fn=predict_fn,
    train_data=training_dataset,
    prompt_uris=["prompts:/support-answer/3"],
    optimizer=GepaPromptOptimizer(
        reflection_model="openai:/<reflection-model>",
        max_metric_calls=200,
    ),
    scorers=scorers,
)
```

Optimization workflow:

1. Split training/alignment, validation, and final held-out test records.
2. Register the starting prompt.
3. Define scorers that reflect product quality; test their agreement with humans.
4. Set budget (`max_metric_calls`, worker count, provider limits).
5. Optimize only on training data.
6. Register optimized output as a new prompt version.
7. Evaluate once on held-out data and compare to the original.
8. Require human review for consequential domains.

### Choosing an optimizer

- **Meta-prompting:** quick rewrite, very little data, lower cost.
- **GEPA:** iterative reflection/search, richer dataset and clearer metrics, higher cost.
- **Custom optimizer:** specialized constraints or search spaces.

Avoid optimizing on the release test set. An optimized prompt can overfit judge quirks,
not true product quality.

### Optimization guardrails

- Keep train/alignment, validation, and release-test records disjoint.
- Track train-versus-validation score gaps after every optimizer round.
- Pin optimizer, reflection model, judge model, random seed where supported, budget, and
  starting prompt version.
- Stop when validation quality plateaus even if training quality continues rising.
- Re-run finalists with repeated judge calls when variance is material.
- Require human review of changed instructions and representative regressions.

## 3. Agent evaluation workflow

Agent evaluation must cover outcome and process.

### Instrument

Capture a hierarchy with meaningful span types:

- root app/agent span;
- chat-model spans;
- retriever spans;
- tool spans;
- agent/sub-agent spans;
- parser/reranker/memory spans where relevant.

### Dataset

```python
agent_data = [
    {
        "inputs": {"question": "Cancel order 123 if it has not shipped."},
        "expectations": {
            "expected_behavior": {
                "check_shipping_status_first": True,
                "cancel_only_if_unshipped": True,
            },
            "expected_tool_calls": ["get_order", "cancel_order"],
        },
        "tags": {"risk": "high", "intent": "cancel_order"},
    }
]
```

Do not encode a single exact tool trajectory if several safe plans are valid. Express
invariants (check state before mutation) instead.

### Scorer stack

1. Final outcome correctness.
2. Policy/guideline adherence.
3. Tool correctness and efficiency.
4. Deterministic argument/state invariants.
5. Routing/retrieval checks.
6. Latency, token, cost, and error budgets.

```python
from mlflow.genai.scorers import (
    Correctness,
    Guidelines,
    ToolCallCorrectness,
    ToolCallEfficiency,
)

result = mlflow.genai.evaluate(
    data=agent_data,
    predict_fn=agent_predict_fn,
    scorers=[
        Correctness(),
        Guidelines(
            name="safe_order_mutation",
            guidelines="Never cancel an order before confirming it has not shipped.",
        ),
        ToolCallCorrectness(),
        ToolCallEfficiency(),
        mutation_precondition_scorer,
    ],
)
```

Async agent functions are supported; configure timeout for long-running agents.

### Multi-agent and delegation evaluation

For an orchestrator plus specialist agents, score each layer separately:

1. **Routing:** Was the correct specialist selected for the user intent/risk?
2. **Delegation contract:** Did the orchestrator pass complete, minimal, authorized input?
3. **Specialist quality:** Did the selected agent produce a correct intermediate result?
4. **Synthesis:** Did the orchestrator preserve specialist evidence and resolve conflicts?
5. **Failure handling:** Did it retry, fallback, escalate, or abstain correctly?

```python
from mlflow.entities import Feedback, SpanType
from mlflow.genai.scorers import scorer

@scorer
def expected_delegation(trace, expectations) -> Feedback:
    invoked = [
        span.name
        for span in trace.search_spans(span_type=SpanType.AGENT)
        if span.parent_id is not None
    ]
    expected = expectations["expected_agents"]
    return Feedback(
        value=set(invoked) == set(expected),
        rationale=f"expected={expected}; invoked={invoked}",
    )
```

For LangGraph or state-machine agents, record router decisions and node transitions as
span attributes/events, then verify allowed transitions and terminal state. Avoid exact
path matching when loops/retries are valid; encode invariants and maximum budgets instead.

## 4. RAG and tool evaluation

### RAG decomposition

Evaluate separately:

1. retrieval relevance;
2. retrieval recall/sufficiency;
3. answer groundedness;
4. answer correctness;
5. citation/document attribution;
6. latency and token/cost.

This decomposition tells whether a failure comes from retrieval, generation, or both.

### Retriever output contract

Use `SpanType.RETRIEVER`. Emit documents with page content and metadata such as `doc_uri`,
chunk ID, and score. Built-in RAG judges and custom recall checks depend on this structure.

### Tool invariants

Custom trace scorer example:

```python
from mlflow.entities import Feedback, SpanType
from mlflow.genai.scorers import scorer

@scorer
def no_mutation_before_read(trace) -> Feedback:
    tools = [s.name for s in trace.search_spans(span_type=SpanType.TOOL)]
    valid = "cancel_order" not in tools or (
        "get_order" in tools and tools.index("get_order") < tools.index("cancel_order")
    )
    return Feedback(
        value=valid,
        rationale=f"Observed tool order: {tools}",
    )
```

## 5. Existing-trace evaluation

Evaluate historical traces to avoid re-running the app:

```python
traces = mlflow.search_traces(
    locations=[experiment_id],
    filter_string="tag.app_version = '2026.07.31'",
    return_type="list",
)

result = mlflow.genai.evaluate(
    data=traces,
    scorers=[
        RelevanceToQuery(),
        RetrievalGroundedness(),
        production_policy_judge,
    ],
)
```

Workflow:

1. Query a representative or incident-focused sample.
2. Check trace completeness and privacy.
3. Add expectations where domain truth is available.
4. Score without `predict_fn`.
5. Inspect failures and scorer errors.
6. Tag validated issue categories.
7. Merge approved cases into an evaluation dataset.

## 6. Multi-turn evaluation and simulation

### Session identity

Every turn must carry the same session ID:

```python
with mlflow.tracing.context(session_id="session-123", user="user-456"):
    agent("First message")
    agent("Follow-up message")
```

Older versions use `mlflow.update_current_trace` with
`metadata={"mlflow.trace.session": session_id}`.

### Evaluate pre-collected sessions

Search traces/sessions and pass them to `evaluate` with multi-turn judges. Current docs
attach conversation-level assessments to the first trace in chronological order.

### Conversation simulation

The full framework is experimental and requires newer MLflow:

```python
from mlflow.genai.simulators import ConversationSimulator
from mlflow.genai.scorers import ConversationCompleteness, UserFrustration

simulator = ConversationSimulator(
    test_cases=[
        {
            "goal": "Resolve a duplicate charge",
            "persona": "Frustrated customer",
            "context": {"account_tier": "premium"},
        }
    ],
    max_turns=6,
    user_model="openai:/<simulator-model>",
)

def predict_fn(input: list[dict], **kwargs) -> str:
    # Responses-API form: `input` is the complete conversation history.
    return agent.respond(messages=input, context=kwargs)

result = mlflow.genai.evaluate(
    data=simulator,
    predict_fn=predict_fn,
    scorers=[ConversationCompleteness(), UserFrustration()],
)
```

Verify exact constructor and input signature in the installed version. Simulated users
are useful for coverage, not a replacement for real-world sessions and human review.

## 7. Workflow automation patterns

### Prompt candidate matrix

```text
for prompt_version × model_version × tool_config:
  run on development dataset
  retain Pareto candidates (quality, latency, cost)
run finalists on held-out dataset
run critical regression suite
promote one immutable configuration
```

### Agent failure routing

```text
judge/code failure
  → final-answer problem? prompt/model/context
  → retrieval problem? index/query/reranker/doc metadata
  → tool problem? schema/description/permissions/retry/idempotency
  → routing problem? agent policy/sub-agent selection
  → operational problem? timeout/rate limit/dependency
  → evaluator problem? missing span/ambiguous criterion/judge mismatch
```

### Production curation

```text
sample sessions and traces
  → detect clusters and negative feedback
  → human validate
  → add expectations
  → merge into dataset
  → add critical @mlflow.test
  → fix prompt/agent
  → compare on same dataset
```

## Sources

- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/prompts/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/agents/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/multi-turn/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/conversation-simulation/
- https://mlflow.org/docs/latest/genai/prompt-registry/
- https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/
