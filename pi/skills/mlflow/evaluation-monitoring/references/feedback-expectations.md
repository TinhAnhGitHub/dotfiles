# Human Feedback, Expectations, and Annotation

## Contents

1. Feedback vs expectations
2. Assessment sources and schema
3. Programmatic feedback lifecycle
4. Expectation types and APIs
5. Annotation workflows
6. Integrating expectations with evaluation
7. Judge alignment dataset
8. Best practices and automation

## 1. Feedback vs expectations

Both are assessments attached to a trace or span, but they have different semantics:

| Assessment | Question | Typical creator | Use |
|---|---|---|---|
| Feedback | How well did this execution perform? | User, reviewer, code, or LLM judge | Diagnose quality, calibrate judges, select failures |
| Expectation | What should have happened? | Domain expert/human | Ground truth, dataset labels, regression contract |

Never silently convert model feedback into human ground truth. A judge can propose a
label, but a human should approve expectations for consequential criteria.

## 2. Assessment sources and schema

```python
from mlflow.entities import AssessmentSource
from mlflow.entities.assessment_source import AssessmentSourceType

human = AssessmentSource(
    source_type=AssessmentSourceType.HUMAN,
    source_id="reviewer@example.com",
)
code = AssessmentSource(
    source_type=AssessmentSourceType.CODE,
    source_id="policy-checker-v3",
)
judge = AssessmentSource(
    source_type=AssessmentSourceType.LLM_JUDGE,
    source_id="quality-judge-v2",
)
```

Useful assessment fields include name, value, rationale, source, optional metadata,
optional error, trace ID, optional span ID, timestamps, and assessment ID.

Use stable names such as `user_satisfaction`, `response_correctness`,
`expected_response`, or `expected_documents`. A name is part of the evaluation contract.

## 3. Programmatic feedback lifecycle

### Log feedback

```python
import mlflow

feedback = mlflow.log_feedback(
    trace_id=trace_id,
    name="user_satisfaction",
    value=False,
    rationale="The response did not resolve the account issue.",
    source=human,
    metadata={"channel": "thumbs_down", "app_version": "2026.07.31"},
)
```

Values may be boolean, numeric, categorical, text, or structured JSON. Pick one stable
type per assessment name so aggregate analysis remains meaningful.

Attach feedback to a specific span when the reviewer is judging retrieval, a tool call,
or another intermediate operation and the installed API supports `span_id` for the call.

### Log an evaluation error

```python
from mlflow.entities import AssessmentError

mlflow.log_feedback(
    trace_id=trace_id,
    name="external_policy_check",
    error=AssessmentError(
        error_code="POLICY_SERVICE_TIMEOUT",
        error_message="The policy service did not respond in 10 seconds.",
    ),
    source=code,
)
```

An evaluation failure is not the same as a failing score. Preserve the error so missing
assessments do not look like passes.

### Retrieve

```python
assessment = mlflow.get_assessment(
    trace_id=trace_id,
    assessment_id=feedback.assessment_id,
)
```

### Update in place

Use update when correcting the same assessment while retaining its identity:

```python
from mlflow.entities import Feedback

mlflow.update_assessment(
    trace_id=trace_id,
    assessment_id=feedback.assessment_id,
    assessment=Feedback(
        name="user_satisfaction",
        value=True,
        rationale="Reviewer corrected the accidental thumbs-down.",
    ),
)
```

### Override automated feedback

Use override when a human intentionally supersedes a code/judge assessment. This keeps
the original for audit rather than rewriting history.

```python
corrected = mlflow.override_feedback(
    trace_id=trace_id,
    assessment_id=automated_feedback.assessment_id,
    value="pass",
    rationale="The domain policy permits this exception.",
    source=human,
    metadata={"override_reason": "approved_policy_exception"},
)
```

### Delete

```python
mlflow.delete_assessment(
    trace_id=trace_id,
    assessment_id=feedback.assessment_id,
)
```

Deletion can affect replacement/override validity. Prefer update or override when audit
history is important.

## 4. Expectation types and APIs

Expectations require MLflow 3.2+ in the current docs.

### Factual

```python
mlflow.log_expectation(
    trace_id=trace_id,
    name="expected_facts",
    value=["The refund window is 30 days"],
    source=human,
    metadata={"policy_version": "refund-policy-2026-04"},
)
```

### Structured

```python
mlflow.log_expectation(
    trace_id=trace_id,
    name="expected_extraction",
    value={
        "intent": "refund_request",
        "should_escalate": False,
        "policy_id": "refund-30-day",
    },
    source=human,
)
```

### Behavioral

```python
mlflow.log_expectation(
    trace_id=trace_id,
    name="expected_behavior",
    value={
        "must_verify_identity": True,
        "must_not_request_password": True,
        "tone": "professional_and_empathetic",
    },
    source=human,
)
```

### Span-level

```python
mlflow.log_expectation(
    trace_id=trace_id,
    span_id=retriever_span_id,
    name="expected_documents",
    value=["policy/refunds/2026", "faq/refunds"],
    source=human,
)
```

Use span-level expectations when a final answer can be correct by accident despite wrong
retrieval or tool behavior.

### Manage expectations

```python
expectation = mlflow.get_assessment(trace_id=trace_id, assessment_id=assessment_id)

from mlflow.entities import Expectation
mlflow.update_assessment(
    trace_id=trace_id,
    assessment_id=assessment_id,
    assessment=Expectation(name="expected_answer", value="Paris"),
)

mlflow.delete_assessment(trace_id=trace_id, assessment_id=assessment_id)
```

Inspect the installed `mlflow.log_expectation` signature because span and metadata
parameters have changed across minors even when the conceptual workflow remains stable.

## 5. Annotation workflows

### Developer inner loop

1. Run traced examples.
2. Annotate obvious good/bad cases.
3. Add expectations for concrete failures.
4. Tag emerging failure modes.
5. Draft deterministic checks or judge criteria.

### Domain-expert review

1. Define a labeling guide with stable names, value types, and examples.
2. Present representative traces without unnecessary sensitive data.
3. Collect independent labels on a calibration subset.
4. Measure disagreement and revise the guide.
5. Adjudicate consequential differences.
6. Promote consensus labels into expectations/datasets.

### End-user feedback

Store the MLflow trace ID or a client request correlation ID with the app response. A
feedback endpoint then resolves that ID and calls `mlflow.log_feedback`.

```python
def record_end_user_feedback(trace_id: str, user_id: str, positive: bool, comment: str | None):
    return mlflow.log_feedback(
        trace_id=trace_id,
        name="user_satisfaction",
        value=positive,
        rationale=comment,
        source=AssessmentSource(
            source_type=AssessmentSourceType.HUMAN,
            source_id=user_id,
        ),
    )
```

Do not trust a client-supplied trace ID without authorization checks. Prevent users from
annotating traces they do not own.

### Review queues

Use queues for:

- judge/human disagreement;
- low-confidence or high-risk cases;
- negative user feedback;
- novel issue clusters;
- randomly sampled normal traffic;
- expectation updates after policy changes.

Review queues prevent annotation from being dominated only by dramatic failures.

## 6. Integrating expectations with evaluation

When traces with expectations are merged into an evaluation dataset, scorers receive the
expectations dictionary.

```python
from mlflow.genai.scorers import Correctness, ExpectationsGuidelines, scorer

@scorer
def expected_escalation(outputs: dict, expectations: dict) -> bool:
    expected = expectations["expected_behavior"]["should_escalate"]
    return outputs["escalated"] is expected

result = mlflow.genai.evaluate(
    data=dataset,
    predict_fn=predict_fn,
    scorers=[Correctness(), ExpectationsGuidelines(), expected_escalation],
)
```

Ground-truth design rules:

- Prefer atomic expected facts over one overfitted prose answer.
- Put row-specific rules in `expectations["guidelines"]`.
- Use typed structured objects for tool and extraction tasks.
- Define abstention/escalation behavior explicitly.
- Keep expectation schema backward-compatible or version it.

## 7. Judge alignment dataset

Judge alignment compares a judge's assessment to human feedback on the same traces.

Requirements in the current workflow:

- both judge and human assessments on each selected trace;
- assessment name exactly matches the judge name;
- at least about 10 examples; use more and stratify for reliable validation;
- separate alignment/training traces from held-out validation traces.

```python
from mlflow.genai.judges.optimizers import MemAlignOptimizer

optimizer = MemAlignOptimizer(reflection_lm="anthropic:/<reflection-model>")
aligned = initial_judge.align(alignment_traces, optimizer)
aligned.register(experiment_id=experiment_id)
```

Other documented optimizer families include SIMBA and GEPA. Confirm current imports and
constructors against the installed version.

Measure agreement by class/slice, not only overall accuracy. A judge can look accurate
while systematically failing a rare high-risk class.

## 8. Best practices and automation

- Define one semantic meaning and value type per assessment name.
- Include rationale for human and judge labels where disagreement is actionable.
- Track reviewer, policy/guideline version, app version, and confidence.
- Use overrides rather than destructive edits when correcting automated feedback.
- Redact PII before sending traces to external reviewers or judge models.
- Separate user preference feedback from factual correctness.
- Sample positive and normal traffic as well as failures.
- Re-annotate when policies, products, or expected behavior change.
- Never let a feedback endpoint block the primary user request; log asynchronously and
  handle duplicate submissions idempotently.
- Monitor annotation coverage and inter-reviewer agreement.

## 9. Databricks labeling schemas and sessions

Databricks Review App labeling uses explicit schemas and sessions. Schemas define the
question, assessment type, reviewer input widget, instructions, validation, and comments.

Built-in expectation schema names align with judges:

- `EXPECTED_FACTS` → `Correctness` and `RetrievalSufficiency`;
- `EXPECTED_RESPONSE` → `Correctness` and `RetrievalSufficiency`;
- `GUIDELINES` → `ExpectationsGuidelines`.

```python
import mlflow.genai.label_schemas as schemas
from mlflow.genai.label_schemas import (
    InputCategorical,
    InputText,
    InputTextList,
    LabelSchemaType,
)

expected_facts = schemas.create_label_schema(
    name=schemas.EXPECTED_FACTS,
    type=LabelSchemaType.EXPECTATION,
    title="Expected facts",
    input=InputTextList(max_count=10, max_length_each=500),
    instruction="List independently verifiable facts required in a correct response.",
    overwrite=True,
)

quality = schemas.create_label_schema(
    name="response_quality",
    type="feedback",
    title="How would you rate this response?",
    input=InputCategorical(options=["Poor", "Fair", "Good", "Excellent"]),
    enable_comment=True,
)
```

Other documented inputs are `InputCategoricalList` and `InputNumeric`. Manage schemas
with `get_label_schema`, recreate with `overwrite=True`, and `delete_label_schema`.

A labeling session is an MLflow run that groups traces, schemas, and assigned reviewers.
Names need not be unique; persist `session.mlflow_run_id`.

```python
import mlflow.genai.labeling as labeling

session = labeling.create_labeling_session(
    name="support_failures_2026_07",
    assigned_users=["expert@example.com"],
    label_schemas=["response_quality", schemas.EXPECTED_FACTS],
)

session.add_traces(traces)
session.set_assigned_users(["expert@example.com", "lead@example.com"])

# After review, upsert expectations by trace inputs into an evaluation dataset.
session.sync(to_dataset="main.agent_eval.support_regression")
```

Current docs recommend focused sessions of roughly 25–100 traces to limit reviewer
fatigue. Assigning users can grant access to the containing MLflow experiment; review the
permission impact before adding external/domain reviewers.

## Sources

- https://mlflow.org/docs/latest/genai/assessments/feedback/
- https://mlflow.org/docs/latest/genai/assessments/expectations/
- https://mlflow.org/docs/latest/genai/assessments/review-queues/
- https://mlflow.org/docs/latest/genai/concepts/feedback/
- https://mlflow.org/docs/latest/genai/concepts/expectations/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/alignment/
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/concepts/labeling-schemas
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/human-feedback/concepts/labeling-sessions
