# Lifecycle, Quickstart, and Evaluation Architecture

## Contents

1. Evaluation-driven development
2. Manual inner loop
3. Systematic evaluation
4. Outer-loop monitoring
5. Quickstart
6. Evaluation contract
7. Automation blueprint
8. Design and operational checklists

## 1. Evaluation-driven development

Treat evaluation as the control system for the app, not a report produced after the app
is finished.

```text
Build and trace
  → inspect examples manually
  → record feedback and ground truth
  → curate a representative dataset
  → encode quality with scorers
  → evaluate every meaningful app/prompt/model change
  → turn known failures into regression gates
  → monitor live traffic
  → mine live failures and drift for the next dataset revision
```

The loop separates two time scales:

- **Inner loop:** fast, qualitative, example-level iteration. Humans inspect traces,
  refine prompts/tools, and agree on what good behavior means.
- **Outer loop:** scalable, quantitative control. Automated scorers evaluate curated
  datasets and sampled live traffic; failures re-enter the inner loop.

Do not automate judgment before criteria are stable. Start with human review, discover
failure modes, then encode those criteria in code or judges.

## 2. Manual inner loop

1. Instrument the app so every call produces a useful root span and typed child spans.
2. Run realistic examples, not only happy-path demos.
3. Review final output and trajectory: retrieval, tools, routing, retries, latency, token
   use, and errors.
4. Log feedback about what happened and expectations about what should have happened.
5. Tag recurring failure categories.
6. Decide whether the fix belongs in prompt, context/retrieval, tool contract, routing,
   model, guardrail, or judge.

Exit the manual-only phase when reviewers agree on stable criteria and representative
examples exist for both good and bad behavior.

## 3. Systematic evaluation

Systematic evaluation repeats the same dataset and scorer suite across candidates.

Minimum useful suite:

- one deterministic schema/business-rule scorer;
- one task-quality judge;
- one safety/compliance criterion appropriate to the domain;
- one trace-aware scorer for RAG/tools/agents;
- slice tags for critical cohorts.

Aggregate metrics detect trends, but per-record failures drive fixes. Always inspect the
failure rows and judge rationales before deciding that a candidate is better.

## 4. Outer-loop monitoring

Monitoring answers different questions from offline evaluation:

- Is traffic distribution changing?
- Are new failure modes appearing?
- Are quality, cost, latency, or tool reliability drifting?
- Are users dissatisfied even when offline scores remain stable?

Use sampling and filters to balance cost and coverage. Safety/security may justify 100%
coverage; expensive semantic judges often use lower rates. Preserve enough unsampled raw
signals (errors, latency, user feedback) to detect blind spots.

## 5. Quickstart

### Local OSS setup

```bash
pip install --upgrade "mlflow[genai]"
mlflow server
```

Evaluation datasets require a SQL backend. A local SQL-backed server can use SQLite;
production deployments should use a supported managed SQL database and durable artifacts.

### Minimal evaluation

```python
import mlflow
from mlflow.entities import Feedback
from mlflow.genai.scorers import Correctness, Guidelines, scorer

mlflow.set_experiment("support-agent-evaluation")

data = [
    {
        "inputs": {"question": "How do I reset my password?"},
        "expectations": {
            "expected_facts": [
                "Use the Forgot Password flow",
                "Follow the link sent by email",
            ]
        },
        "tags": {"intent": "password_reset", "risk": "medium"},
    }
]

def predict_fn(question: str) -> str:
    return support_agent(question)

@scorer
def has_actionable_step(outputs: str) -> Feedback:
    passed = "password" in outputs.lower() and "email" in outputs.lower()
    return Feedback(
        value=passed,
        rationale="Mentions both the password flow and email follow-up.",
    )

result = mlflow.genai.evaluate(
    data=data,
    predict_fn=predict_fn,
    scorers=[
        has_actionable_step,
        Correctness(),
        Guidelines(
            name="no_secret_request",
            guidelines="Never ask the user to reveal a password or authentication secret.",
        ),
    ],
)

print(result.metrics)
print(result.result_df)
```

Pin the judge model explicitly or through `MLFLOW_GENAI_JUDGE_DEFAULT_MODEL` when
reproducibility matters. Do not assume the documentation's default model is stable.

## 6. Evaluation contract

### Data

Each record normally contains:

```python
{
    "inputs": {...},           # required; kwargs for predict_fn
    "outputs": ...,            # optional; omit when predict_fn generates it
    "expectations": {...},     # optional ground truth
    "tags": {...},             # optional slicing metadata
}
```

### `predict_fn`

- Receives `**record["inputs"]`.
- Parameter names must match input keys; use a wrapper when they do not.
- Return the app output in the same structure production uses.
- Instrument it or its dependencies so trace-based scorers can inspect execution.
- Omit it when data already contains outputs or when evaluating existing traces.

### Scorers

- Field-based scorers consume `inputs`, `outputs`, and `expectations`.
- Trace-based scorers consume the full `Trace` and typed spans.
- Primitive values are convenient; `Feedback` adds rationale and metadata.
- Use distinct metric names, especially when returning `list[Feedback]`.

### Result

Use `result.metrics` for aggregate summaries and `result.result_df` for per-record
analysis. Evaluation creates an MLflow run and trace-level assessments. In regression
tests, `result.passed` and `result.reason` support binary gating when scorers define
pass/fail semantics.

## 7. Automation blueprint

### Pull request

1. Load the frozen evaluation dataset revision.
2. Evaluate the candidate with pinned app, prompt, model, and judge identifiers.
3. Run deterministic scorers first.
4. Run selected LLM judges with bounded concurrency and budget.
5. Compare aggregate and slice metrics to baseline.
6. Fail explicit critical-case gates.
7. Persist the run ID as a build artifact or PR comment.

### Nightly

1. Run the broader and expensive scorer suite.
2. Sample recent production traces across cohorts.
3. Detect and cluster novel failures.
4. Generate an annotation queue; do not auto-promote unverified model labels to ground
   truth.
5. Merge reviewer-approved records into the next dataset version.

### Release

1. Confirm no critical regression.
2. Promote immutable prompt/model/app identifiers.
3. Deploy trace context tags (`environment`, `app_version`, `prompt_version`,
   `model_id`, `git_sha`).
4. Enable or update production scorers.
5. Observe quality and operational signals together.

## 8. Checklists

### Dataset quality

- Representative user intents and difficult slices
- Positive, negative, boundary, adversarial, and abstention cases
- Provenance and reviewer identity
- Explicit expectations where objective truth exists
- No train/test leakage into prompt optimization

### Scorer quality

- Criterion is singular and measurable
- Required fields/spans are present
- Judge rationale is reviewable
- Human agreement measured on a calibration set
- Cost and latency budget known
- Version/model/instructions pinned for gates

### Monitoring quality

- Sampling does not exclude failures by construction
- Error, latency, token, and user-feedback signals remain available
- Privacy/redaction happens before export where required
- Alert ownership and triage status are defined
- Validated failures become dataset cases and tests

## Sources

- https://mlflow.org/docs/latest/genai/eval-monitor/
- https://mlflow.org/docs/latest/genai/eval-monitor/quickstart/
- https://mlflow.org/docs/latest/genai/datasets/end-to-end-workflow/
- https://mlflow.org/docs/latest/genai/eval-monitor/faq/
