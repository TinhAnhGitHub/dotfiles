# Running Systematic Evaluations

## Contents

1. Evaluation modes
2. Data setup patterns
3. `predict_fn` patterns
4. Sync, async, and concurrency
5. Evaluating existing outputs and traces
6. Results, comparison, and release decisions
7. Debugging and common failures
8. Automation template

## 1. Evaluation modes

Choose one mode deliberately:

| Mode | Data contains | `predict_fn` | Purpose |
|---|---|---|---|
| Direct evaluation | Inputs + optional expectations | Required | Run current app and capture fresh traces |
| Answer-sheet evaluation | Inputs + outputs + optional expectations | Omitted | Score pre-generated outputs without rerunning |
| Trace evaluation | `Trace` objects | Omitted | Score historical or production executions, including spans |
| Multi-turn trace evaluation | Session-tagged traces | Omitted | Score conversation-wide behavior |
| Conversation simulation | Goals/personas/context | Required with special signature | Generate and score synthetic sessions |

For candidate comparisons, regenerate both candidates from the same immutable inputs
unless the goal is specifically to rescore frozen outputs.

## 2. Data setup patterns

### Managed EvaluationDataset

Recommended for shared, versioned, production-oriented benchmarks:

```python
from mlflow.genai.datasets import get_dataset

dataset = get_dataset(dataset_id="d-...")
result = mlflow.genai.evaluate(
    data=dataset,
    predict_fn=predict_fn,
    scorers=scorers,
)
```

### List of dictionaries

Best for fast prototypes and focused regression reproduction:

```python
data = [
    {
        "inputs": {"question": "What is MLflow?", "locale": "en-US"},
        "expectations": {"expected_facts": ["MLflow is open source"]},
        "tags": {"slice": "product_knowledge"},
    }
]
```

### Pandas DataFrame

```python
import pandas as pd

data = pd.DataFrame(
    [
        {
            "inputs": {"question": "What is MLflow?"},
            "outputs": "MLflow is an AI and ML platform.",
            "expectations": {"expected_facts": ["MLflow is open source"]},
        }
    ]
)
result = mlflow.genai.evaluate(data=data, scorers=scorers)
```

Trace-aware scorers need actual traces, not a static answer-sheet DataFrame.

### Spark DataFrame

Spark input is documented for larger datasets. Keep nested `inputs` and `expectations`
JSON-serializable and confirm the installed MLflow/Spark compatibility before relying on
distributed behavior.

## 3. `predict_fn` patterns

### Direct app entrypoint

```python
def predict_fn(question: str, locale: str = "en-US") -> dict:
    return support_app(question=question, locale=locale)
```

MLflow calls the function with `**inputs`. A row with keys `question` and `locale` needs
matching parameters or `**kwargs` handling.

### Adapter for a mismatched app API

```python
def predict_fn(question: str, history: list[dict] | None = None) -> dict:
    app_result = support_app.invoke(
        {
            "user_message": question,
            "messages": history or [],
        }
    )
    return {
        "response": app_result["answer"],
        "escalated": app_result["escalated"],
    }
```

The adapter is part of the evaluation contract. Keep it thin and test it so mapping bugs
do not masquerade as app regressions.

### Raw LLM call

```python
from openai import OpenAI

client = OpenAI()

@mlflow.trace
def predict_fn(question: str) -> str:
    response = client.chat.completions.create(
        model="<candidate-model>",
        messages=[
            {"role": "system", "content": "Answer accurately and concisely."},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content
```

### Logged MLflow model

Load once outside the function:

```python
model = mlflow.pyfunc.load_model("models:/support-agent@candidate")

def predict_fn(question: str):
    return model.predict({"question": question})
```

Loading inside `predict_fn` repeats expensive initialization for every row.

### Databricks Model Serving

```python
predict_fn = mlflow.genai.to_predict_fn("endpoints:/support-agent-endpoint")
```

Confirm request schema and endpoint support. Load `databricks-model-serving` for endpoint
auth, readiness, and query shape.

### Prompt Registry

```python
prompt = mlflow.genai.load_prompt("prompts:/support-answer/7")

@mlflow.trace
def predict_fn(question: str) -> str:
    messages = prompt.format(question=question)
    return call_model(messages)
```

Pin a version for repeatable evaluation. Alias-based loads are useful during development
but can move or cache.

### Streaming applications

Evaluation needs one final return value even when production streams tokens/events. Wrap
the stream and accumulate the same semantic output users receive:

```python
@mlflow.trace
def predict_fn(question: str) -> str:
    chunks = []
    for event in streaming_agent(question):
        if event.type == "text_delta":
            chunks.append(event.text)
    return "".join(chunks)
```

For a traced generator itself, current MLflow supports `@mlflow.trace(output_reducer=...)`
in supported versions. Use a reducer that reconstructs the final output without storing
unbounded intermediate state. Score partial events only when partial-output quality is a
real product contract; otherwise score the completed response and use span events for
stream timing/errors.

## 4. Sync, async, and concurrency

Async functions are supported in current MLflow:

```python
async def predict_fn(question: str) -> str:
    result = await agent.run(question)
    return result.final_output
```

Useful environment controls documented across current evaluation pages include:

```bash
export MLFLOW_GENAI_EVAL_MAX_WORKERS=10
export MLFLOW_GENAI_EVAL_MAX_SCORER_WORKERS=2
export MLFLOW_GENAI_EVAL_ASYNC_TIMEOUT=600
export MLFLOW_GENAI_EVAL_ENABLE_SCORER_TRACING=true
```

The skip-trace-validation variable has changed naming in docs/source across versions.
Inspect `mlflow.environment_variables` rather than copying a stale name.

Concurrency principles:

- Respect model/provider rate limits.
- Do not use more workers than the app or judge endpoint can sustain.
- Separate prediction and scorer concurrency when possible.
- Preserve row identity and idempotency under retry.
- Expect evaluation to make an extra trace-validation call in some versions.
- Record timeout/errors as evaluation errors rather than silently dropping rows.

## 5. Existing outputs and traces

### Pre-generated outputs

```python
data = [
    {
        "inputs": {"question": "What is MLflow?"},
        "outputs": "MLflow is an open-source platform.",
        "expectations": {"expected_facts": ["MLflow is open source"]},
    }
]

result = mlflow.genai.evaluate(data=data, scorers=scorers)
```

Use this to compare judges or rescore frozen app outputs. It cannot recreate missing tool,
retrieval, routing, latency, or token details.

### Existing traces

```python
traces = mlflow.search_traces(
    locations=[experiment_id],
    filter_string="tag.environment = 'production'",
    order_by=["timestamp_ms DESC"],
    max_results=200,
    return_type="list",
)

result = mlflow.genai.evaluate(
    data=traces,
    scorers=scorers,
)
```

Do not pass `predict_fn`; trace inputs, outputs, spans, and assessments are reused.

### Re-evaluation after annotation

1. Search traces.
2. Add human expectations to selected traces.
3. Re-run `evaluate(data=traces, scorers=...)`.
4. Merge approved traces into the evaluation dataset.

This supports the production-to-dataset loop without invoking the app again.

## 6. Results and comparison

```python
result = mlflow.genai.evaluate(...)

aggregate = result.metrics
rows = result.result_df
run_id = result.run_id
```

Inspect the installed object before relying on less common attributes. Core analysis:

- aggregate mean/pass rate per scorer;
- scorer error rate;
- per-record values and rationales;
- slice metrics by tags;
- latency, tokens, cost, and tool errors;
- candidate-baseline deltas with confidence/variance;
- count and severity of critical regressions.

### Release decision pattern

```text
Pass only if:
  all critical regression cases pass
  AND no protected slice drops beyond tolerance
  AND scorer error rate is below threshold
  AND cost/latency budgets pass
  AND aggregate quality is non-inferior or improved
```

Define this policy before viewing candidate results.

## 7. Debugging and common failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `unexpected keyword argument` | Input keys do not match `predict_fn` | Rename parameters or add a wrapper |
| Trace scorer sees no spans | App is not instrumented or span types are missing | Enable autolog/manual tracing and type spans |
| RAG judge has no documents | Retriever output schema is wrong | Emit document objects with text and URI metadata |
| Results differ across CI runs | Unpinned model/judge, model nondeterminism | Pin versions and align judge; use deterministic gates |
| Many missing scores | Scorer exceptions or rate limits | Inspect assessment errors and server logs; lower concurrency |
| Extra model call | Trace validation probe | Account for it or use the version-correct skip setting |
| Static DataFrame fails trace scorer | No active Trace object | Use field-based scorer or evaluate real traces |
| Prompt result is stale | Alias cache | Pin version or set appropriate cache TTL |

## 8. Automation template

```python
def run_candidate_evaluation(dataset, predict_fn, scorers, candidate_id):
    with mlflow.start_run(run_name=f"eval-{candidate_id}") as run:
        mlflow.set_tag("candidate_id", candidate_id)
        mlflow.set_tag("dataset_id", dataset.dataset_id)
        mlflow.set_tag("dataset_digest", dataset.digest)
        result = mlflow.genai.evaluate(
            data=dataset,
            predict_fn=predict_fn,
            scorers=scorers,
        )
        return {
            "run_id": run.info.run_id,
            "metrics": result.metrics,
            "rows": result.result_df,
        }
```

Pin/record:

- dataset ID/digest;
- app/model/prompt versions;
- scorer names/versions and judge models;
- environment and git SHA;
- worker/timeouts;
- MLflow version.

## Sources

- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/eval-examples/
- https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/
- https://mlflow.org/docs/latest/genai/eval-monitor/faq/
- https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html
