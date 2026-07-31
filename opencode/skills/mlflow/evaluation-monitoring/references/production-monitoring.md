# Automatic Evaluation and Production Monitoring

## Contents

1. Offline vs automatic evaluation
2. OSS MLflow automatic evaluation
3. Databricks managed production monitoring
4. Sampling, filtering, and sessions
5. Scorer lifecycle
6. Dashboards and operational signals
7. Outer-loop curation
8. Troubleshooting and best practices

## 1. Offline vs automatic evaluation

| Dimension | Offline | Automatic/production |
|---|---|---|
| Trigger | Explicit `mlflow.genai.evaluate()` | New traces/sessions arrive |
| Data | Curated dataset or historical traces | Live traffic |
| Goal | Compare, validate, regression-test | Detect trends and live failures |
| Coverage | Controlled cases | Sampled/filtered real traffic |
| Output | Evaluation run and assessments | Assessments attached to live traces, trend charts |

Reuse criteria across phases where supported, but do not assume every offline scorer can
run online.

## 2. OSS MLflow automatic evaluation

Current upstream MLflow docs provide server-side automatic evaluation. Prerequisites:

1. MLflow Server;
2. MLflow Tracing in the app;
3. session IDs for multi-turn judges;
4. configured AI Gateway endpoint for judge execution.

Only LLM judges are supported online in OSS. Code-based `@scorer` and `Scorer` class
implementations remain offline-only.

### Register and start a trace judge

```python
import mlflow
from mlflow.genai.scorers import ScorerSamplingConfig, ToolCallCorrectness

mlflow.set_experiment("support-agent-production")

judge = ToolCallCorrectness(model="gateway:/quality-judge")
registered = judge.register(name="tool_call_correctness")
registered = registered.start(
    sampling_config=ScorerSamplingConfig(sample_rate=0.5)
)
```

### Session judge

```python
from mlflow.genai.scorers import ConversationalGuidelines

session_judge = ConversationalGuidelines(
    name="conversation_policy",
    guidelines=(
        "The assistant should resolve the request without asking for authentication secrets."
    ),
    model="gateway:/quality-judge",
)
registered_session = session_judge.register(name="conversation_policy")
registered_session = registered_session.start(
    sampling_config=ScorerSamplingConfig(sample_rate=1.0)
)
```

### Update or stop

```python
from mlflow.genai.scorers import get_scorer

registered = get_scorer(name="tool_call_correctness")
registered = registered.update(
    sampling_config=ScorerSamplingConfig(sample_rate=0.25)
)
registered = registered.stop()
```

Current upstream docs state:

- assessments generally appear within one or two minutes;
- a newly created/enabled judge processes traces/sessions at most one hour old;
- updating a judge does not re-evaluate already assessed traces;
- failed evaluations are not retried automatically;
- session evaluation waits for a default five-minute inactivity buffer.

## 3. Databricks managed production monitoring

Databricks production monitoring is a distinct managed Beta service. It extends online
execution to supported custom `@scorer` functions in addition to LLM judges.

Prerequisites can include:

- workspace preview enabled;
- `CAN EDIT` or equivalent experiment permission;
- instrumented app and tested scorers;
- serverless budget policy when the default policy is disabled;
- SQL warehouse configuration for Unity Catalog traces;
- notebook-based scorer registration for custom code.

### Built-in judge

```python
from mlflow.genai.scorers import Safety, ScorerSamplingConfig

safety = Safety().register(name="safety")
safety = safety.start(
    sampling_config=ScorerSamplingConfig(sample_rate=1.0)
)
```

### Guidelines judge

```python
from mlflow.genai.scorers import Guidelines

policy = Guidelines(
    name="policy",
    guidelines=["The response must not expose personal information."],
).register(name="production_policy")

policy = policy.start(
    sampling_config=ScorerSamplingConfig(sample_rate=0.5)
)
```

### Custom code scorer — Databricks-only online pattern

Define and register from a Databricks notebook. Keep it self-contained, with imports
inside the function and no closure/external-variable dependencies.

```python
from mlflow.genai.scorers import scorer, ScorerSamplingConfig

@scorer
def response_has_citation(outputs):
    import re
    text = str(outputs)
    return bool(re.search(r"\[[^\]]+\]", text))

registered = response_has_citation.register(name="response_has_citation")
registered = registered.start(
    sampling_config=ScorerSamplingConfig(sample_rate=0.2)
)
```

Class-based scorers are not supported by managed production serialization. Databricks
currently documents at most 20 continuously monitored scorers per experiment.

### Budget policy

```python
mlflow.set_experiment_tag(
    experiment_id=experiment_id,
    key="mlflow.workload_creation_policy_id",
    value="<serverless-budget-policy-id>",
)
```

### Backfill historical traces

```python
from datetime import datetime
from databricks.agents.scorers import BackfillScorerConfig, backfill_scorers

job_id = backfill_scorers(
    experiment_id=experiment_id,
    scorers=[BackfillScorerConfig(scorer=safety, sample_rate=0.8)],
    start_time=datetime(2026, 7, 1),
    end_time=datetime(2026, 7, 31),
)
```

Backfill is Beta. Verify current signature/package version.

## 4. Sampling, filtering, and sessions

`ScorerSamplingConfig` currently exposes `sample_rate` from 0.0 to 1.0 and optional
`filter_string`.

```python
config = ScorerSamplingConfig(
    sample_rate=0.1,
    filter_string="metadata.environment = 'production'",
)
```

Sampling guidance:

| Criterion | Starting rate |
|---|---:|
| Critical safety/security | 1.0 when feasible |
| Expensive trace judge | 0.05–0.20 |
| Development/internal QA | 0.30–1.0 |
| Baseline representative quality | Choose statistically meaningful stratified sample |

Do not filter only to successful traces if you need execution/error monitoring.

### Session behavior

- All turns must carry `mlflow.trace.session` metadata.
- Session judges run after inactivity; default documented buffer is five minutes.
- If new traces arrive later, automatic evaluation may replace previous session results.
- Filters apply to the first trace in the session in current OSS docs.

## 5. Scorer lifecycle

```text
draft/test offline
  → register immutable/versioned definition
  → start with sampling config
  → observe errors, cost, and agreement
  → update sample/filter or register improved version
  → stop
  → delete only when retention/governance permits
```

Use assignment (`scorer = scorer.start(...)`) because Databricks explicitly documents
lifecycle operations as returning new instances; writing this way is safe across both
environments.

Common functions in current APIs include `get_scorer`, `list_scorers`, and
`delete_scorer`. Confirm imports in the target environment.

## 6. Dashboards and operational signals

Monitoring quality in isolation is dangerous. Correlate assessments with:

- request volume and cohort;
- latency distribution and timeout/error rate;
- input/output/total tokens;
- model cost where available;
- tool call count, latency, and failure rate;
- retriever hit/empty rates;
- user feedback;
- app, prompt, model, and tool version.

MLflow's Overview/trace views can expose usage and quality trends. Databricks UC traces can
also be queried with SQL and used in AI/BI dashboards. Alerting may be external to MLflow;
define the operational owner and trigger policy.

## 7. Outer-loop curation

```text
live trace
  → automatic assessment and operational metrics
  → select failed, disagreed, novel, and random cases
  → human verify and add expectations
  → merge into candidate dataset
  → add critical regression test
  → fix app/prompt/retrieval/tool/judge
  → offline re-evaluation
  → deploy and confirm live recurrence drops
```

Keep raw feedback, expected behavior, and scorer output distinct so the history remains
auditable.

### Databricks trace archival to Delta

Databricks provides a separate Beta archival flow for long-term retention and custom
analytics:

```python
from mlflow.tracing.archival import (
    disable_databricks_trace_archival,
    enable_databricks_trace_archival,
)

enable_databricks_trace_archival(
    delta_table_fullname="main.agent_observability.archived_traces",
    experiment_id=experiment_id,
)

# Later, if required:
disable_databricks_trace_archival(experiment_id=experiment_id)
```

The target UC table is created if absent and appended if present. Grant write permission,
define retention/compaction/PII policy, and treat a scorer-version change as a metric
boundary in dashboards.

### Operational dashboards and alerts

For UC-backed traces, build SQL/AI-BI views from the generated trace views or the archival
table. Track at least volume, error rate, P50/P95 latency, token/cost distribution, scorer
pass rate/error rate, negative user feedback, and app/prompt/model version. Alerting is a
platform workflow rather than a substitute for trace-level investigation; route to
`databricks-platform` for SQL/AI-BI/alert resources.

## 8. Troubleshooting and best practices

| Symptom | Check |
|---|---|
| Missing assessments | Active state, sampling > 0, filter match, trace age, Gateway/model auth |
| Session judge never runs | Session metadata and inactivity buffer |
| Custom Databricks scorer serialization fails | Notebook definition, inline imports, no closures/type imports, decorator not class |
| UC monitoring does not start | SQL warehouse ID and privileges |
| 403 when registering on Databricks | Experiment permissions and serverless budget policy |
| Scores look wrong | Trace schema, judge instructions, human alignment, model version |
| Costs spike | Sample rate, judge model, trace size, number of judges |

Best practices:

- Test every scorer offline on known good/bad examples before scheduling.
- Pin or version judge instructions/model.
- Monitor scorer error rate; missing scores are not passes.
- Start at a controlled sample rate and measure cost.
- Use filters to target risk but maintain an unbiased baseline sample.
- Redact sensitive content before export or judge execution.
- Backfill after scorer changes only when comparison semantics remain valid.

## Sources

- https://mlflow.org/docs/latest/genai/eval-monitor/automatic-evaluations/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/versioning/
- https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/production-monitoring
- https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/manage-production-scorers
- https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/backfill-scorers
- https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/serverless-budget-policy
