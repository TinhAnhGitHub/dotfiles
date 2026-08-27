# Databricks MLflow 3 GenAI Tracing

## Contents

1. Trace and span model
2. Setup and authentication
3. Automatic instrumentation
4. Manual tracing APIs
5. Span types and schemas
6. Production tracing
7. Tags, metadata, users, sessions, and request correlation
8. Unity Catalog trace storage
9. Migration to Unity Catalog
10. PII redaction
11. Search, SQL, and operational analysis
12. Feedback collection
13. Troubleshooting and design rules
14. TypeScript and Node.js tracing

## 1. Trace and span model

A trace represents one app/agent execution. Its span tree records nested operations.

`TraceInfo` carries identifiers, location, request time, state, duration, previews, tags,
metadata, token/cost summaries, and assessments depending on version/backend.
`TraceData` carries the spans.

Core span fields include:

- `trace_id`, `span_id`, `parent_id`;
- name and `span_type`;
- start/end nanoseconds and status;
- inputs and outputs;
- attributes;
- events/exceptions.

MLflow 3 renamed the primary trace identifier from `request_id` to `trace_id`. Deprecated
aliases can appear in old code. `client_request_id` is different: it is an application
correlation ID for linking an external request to a trace.

## 2. Setup and authentication

In Databricks notebooks:

```python
%pip install --upgrade "mlflow[databricks]"
dbutils.library.restartPython()
```

```python
import mlflow

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/support-agent")
```

Outside the workspace, use Databricks unified authentication. Common environment-based
configuration includes `DATABRICKS_HOST` with an approved OAuth/PAT mechanism and
`MLFLOW_TRACKING_URI=databricks`. Load `databricks` and `databricks-core`; do not invent
credentials or expose secrets.

For production-only tracing, Databricks/MLflow document a lightweight `mlflow-tracing`
package. Do not install it alongside the full `mlflow` package in the same environment.

## 3. Automatic instrumentation

Start with the integration's `autolog()` and add manual spans for application logic:

```python
import mlflow

mlflow.openai.autolog()
mlflow.langchain.autolog()
```

Common documented integrations include OpenAI/Databricks Foundation Model APIs,
LangChain/LangGraph, Anthropic, DSPy, Bedrock, AutoGen, and other GenAI frameworks.
Use only the calls for libraries actually present.

Disable an integration when necessary:

```python
mlflow.openai.autolog(disable=True)
```

On serverless compute, explicitly call GenAI autologging; do not assume it is enabled.

## 4. Manual tracing APIs

### Function decorator

```python
import mlflow
from mlflow.entities import SpanType

@mlflow.trace(
    name="support_agent",
    span_type=SpanType.AGENT,
    attributes={"component": "orchestrator"},
)
def support_agent(question: str) -> dict:
    return route_and_answer(question)
```

`@mlflow.trace` supports sync and, in modern versions, async/generator/async-generator
functions. Use `output_reducer` for streamed generator output where documented.

The decorator should generally be the outermost decorator so MLflow sees the call.

### Span context manager

```python
with mlflow.start_span(name="lookup_order", span_type=SpanType.TOOL) as span:
    span.set_inputs({"order_id": order_id})
    result = lookup_order(order_id)
    span.set_outputs(result)
    span.set_attribute("tool.version", "2")
```

Use `LiveSpan` methods for inputs, outputs, attributes, status, and events.

### Events and exceptions

```python
from mlflow.entities import SpanEvent

span.add_event(
    SpanEvent(
        name="retry",
        attributes={"attempt": 2, "reason": "rate_limit"},
    )
)
```

Context managers/decorators capture exceptions. Add structured events when intermediate
retries or recoverable failures matter.

### Low-level client API

Use `MlflowClient.start_trace/start_span/end_span/end_trace` only when explicit lifecycle,
custom IDs, or integration with an existing observability system requires it. It does not
automatically manage parent-child context and may not interoperate with high-level active
span APIs.

```python
from mlflow import MlflowClient

client = MlflowClient(tracking_uri="databricks")
root = client.start_trace(name="request", inputs={"question": question})

try:
    child = client.start_span(
        name="retrieve",
        trace_id=root.trace_id,
        parent_id=root.span_id,
        inputs={"query": question},
    )
    docs = retrieve(question)
    client.end_span(
        trace_id=root.trace_id,
        span_id=child.span_id,
        outputs=docs,
        status="OK",
    )
    client.end_trace(trace_id=root.trace_id, outputs={"docs": docs}, status="OK")
except Exception:
    client.end_trace(trace_id=root.trace_id, status="ERROR")
    raise
```

Exact low-level parameter names changed from request IDs in MLflow 2 to trace IDs in
MLflow 3. Inspect the installed signature before implementing this path.

### Threads and async

Async tasks normally propagate context variables. Thread pools may require
`contextvars.copy_context()` per submitted task so child spans remain attached to the
correct trace.

## 5. Span types and schemas

Common `SpanType` members:

- `CHAT_MODEL`
- `CHAIN`
- `AGENT`
- `TOOL`
- `EMBEDDING`
- `RETRIEVER`
- `PARSER`
- `RERANKER`
- `MEMORY`
- `UNKNOWN`

Use the most specific type; scorers search these types.

Retriever spans should output documents with content and metadata such as `doc_uri`,
chunk ID, and relevance score:

```python
from mlflow.entities import Document

documents = [
    Document(
        page_content=text,
        metadata={"doc_uri": uri, "chunk_id": chunk_id, "score": score},
    )
    for text, uri, chunk_id, score in rows
]
span.set_outputs(documents)
```

Without a stable retriever schema, groundedness/relevance and recall scorers lose the
evidence they need.

## 6. Production tracing

### Async export

```python
mlflow.config.enable_async_logging()
```

Or environment configuration:

```bash
export MLFLOW_ENABLE_ASYNC_TRACE_LOGGING=true
export MLFLOW_ASYNC_TRACE_LOGGING_MAX_WORKERS=10
export MLFLOW_ASYNC_TRACE_LOGGING_MAX_QUEUE_SIZE=1000
export MLFLOW_TRACE_SAMPLING_RATIO=0.1
```

Flush on short-lived processes where the SDK does not guarantee completion:

```python
mlflow.flush_trace_async_logging()
```

### Sampling override

```python
@mlflow.trace(sampling_ratio_override=1.0)
def payment_or_account_mutation(...):
    ...
```

Use lower global sampling for volume and 100% sampling for explicitly approved critical
paths. Sampling must not create blind spots for errors; preserve operational error metrics.

### Model Serving/custom agents

Production tracing setup differs for Databricks custom agents, CPU serving, and external
apps. It can require experiment ID, tracing-enable variables, and a service principal with
experiment write permission. Load `databricks-model-serving` and verify the deployment's
current environment-variable contract.

## 7. Tags, metadata, context, and request correlation

Current docs distinguish:

- **tags:** mutable after logging; good for review status, issue category, quality labels;
- **metadata:** immutable context; good for user/session/model/app identity.

```python
@mlflow.trace
def handle_request(message: str, user_id: str, session_id: str, request_id: str):
    mlflow.update_current_trace(
        client_request_id=request_id,
        session_id=session_id,
        user=user_id,
        metadata={
            "app_version": "2026.07.31",
            "prompt_version": "support-answer/7",
        },
        tags={"environment": "production"},
    )
    return support_agent(message)
```

For versions before convenience parameters:

```python
mlflow.update_current_trace(
    metadata={
        "mlflow.trace.session": session_id,
        "mlflow.trace.user": user_id,
    }
)
```

Context manager in newer versions:

```python
with mlflow.tracing.context(session_id=session_id, user=user_id):
    support_agent(message)
```

Finished-trace tags:

```python
mlflow.set_trace_tag(trace_id=trace_id, key="review_status", value="approved")
mlflow.delete_trace_tag(trace_id=trace_id, key="review_status")
```

Never put raw secrets in tags/metadata. Hash or pseudonymize user IDs as policy requires.

## 8. Unity Catalog trace storage

Current Databricks docs require `mlflow[databricks]>=3.14.0`, a supported region, preview
features such as Variant Shredding where documented, and a SQL warehouse for querying.

```python
import os
import mlflow
from mlflow.entities.trace_location import UnityCatalog

mlflow.set_tracking_uri("databricks")
os.environ["MLFLOW_TRACING_SQL_WAREHOUSE_ID"] = "<warehouse-id>"

experiment = mlflow.set_experiment(
    experiment_name="/Shared/support-agent-uc-traces",
    trace_location=UnityCatalog(
        catalog_name="main",
        schema_name="mlflow_traces",
        table_prefix="support_agent",
    ),
)
```

The binding creates OpenTelemetry-oriented tables such as:

- `<prefix>_otel_spans`
- `<prefix>_otel_annotations`
- `<prefix>_otel_logs`
- `<prefix>_otel_metrics`

Privileges include `USE_CATALOG`, `USE_SCHEMA`, and explicit `SELECT` plus `MODIFY` on
the tables. Current docs warn that `ALL PRIVILEGES` alone is insufficient for this path.

UC benefits:

- governed table permissions;
- SQL/Spark/Genie/AI-BI access;
- OpenTelemetry compatibility;
- removal of the classic per-experiment trace count ceiling.

Limitations include regional/preview requirements, ingestion limits, and inability to
rebind an existing experiment to another UC trace location. Verify current docs before
creation because the location is a durable architecture choice.

## 9. Migration to Unity Catalog

Create a new UC-backed target experiment, stop/redirect writes to the old source, then run
the documented idempotent migration utility:

```python
from databricks.migrations.migrate_traces_to_uc import run

run(
    source_experiment_id="<source>",
    target_experiment_id="<target>",
    # start_time_ms=<optional epoch milliseconds>,
)
```

The migration copies traces, spans, assessments, tags, and metadata. It does not migrate
all experiment entities (for example runs/datasets/labeling sessions) and does not mutate
the source. Validate counts, assessments, and query results before retiring source writes.

Legacy UC schemas may require the separate `V1ToV2SqlMigration` table-prefix migration.

## 10. PII redaction

### Before export — preferred for strict controls

```python
import re
import mlflow
from mlflow.entities.span import Span

EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")

def redact_email(span: Span) -> None:
    def scrub(value):
        return EMAIL.sub("[REDACTED_EMAIL]", value) if isinstance(value, str) else value

    if isinstance(span.inputs, dict):
        span.set_inputs({k: scrub(v) for k, v in span.inputs.items()})
    if isinstance(span.outputs, str):
        span.set_outputs(scrub(span.outputs))

mlflow.tracing.configure(span_processors=[redact_email])
```

Processors mutate what is recorded/exported. They do not redact the actual input sent to
the model/tool. Use Gateway/tool controls when model-side PII handling is also required.

Databricks additionally documents post-export batch or view-based redaction for OTel
tables using AI functions. Pre-export prevents raw PII from leaving the app; post-export
can support governed analytics but temporarily retains raw data. Choose based on threat
model and compliance, not convenience.

## 11. Search, SQL, and operational analysis

### SDK

```python
traces = mlflow.search_traces(
    locations=["main.mlflow_traces"],
    filter_string=(
        "trace.status = 'ERROR' AND tag.environment = 'production'"
    ),
    order_by=["timestamp_ms DESC"],
    max_results=100,
    return_type="list",
)
```

UC adds filters for request/response content, token count, span fields/attributes,
feedback, expectations, and client request IDs in current docs. Grammar changed across
MLflow minors and some Databricks production-monitor pages still show `attributes.status`
while current search docs show `trace.status`. Use the page for the target service and
test the filter before scheduling it.

Important distinctions:

- filter `trace.status` can map to DataFrame column `state`;
- filter `trace.execution_time_ms` can map to `execution_duration`;
- `trace.client_request_id` is not the primary trace ID;
- `span.attributes.<key>` is a UC-specific filter family;
- `AND` is supported; do not assume `OR`.

### SQL

Query generated unified/metadata views rather than hand-joining raw OTel tables unless
the use case requires it. The annotations table is append-oriented with soft deletion;
deduplicate to the latest annotation version and exclude deleted rows when querying raw
tables.

Analyze:

- count/error rate and P50/P95/P99 latency;
- token/cost distribution;
- tool success/latency;
- assessment trends;
- version/cohort/session slices;
- trace volume and ingestion health.

## 12. Feedback collection

Return/store `trace_id` or `client_request_id` with the app response. A secure feedback
endpoint maps it back to the trace and logs an assessment.

```python
from mlflow.entities import AssessmentSource

mlflow.log_feedback(
    trace_id=trace_id,
    name="user_feedback",
    value=True,
    source=AssessmentSource(source_type="HUMAN", source_id=user_id),
    rationale="Resolved my issue",
)
```

For `client_request_id`, current UC search supports:

```python
matches = mlflow.search_traces(
    filter_string=f"trace.client_request_id = '{safe_request_id}'",
    max_results=1,
    return_type="list",
)
```

Validate/escape IDs and authorize ownership before attaching feedback.

## 13. Troubleshooting and design rules

- If RAG/tool judges see nothing, check span type and output schema.
- If trace export is slow, verify async logging and trace size; avoid huge attachments.
- If short-lived workers lose traces, flush before exit.
- If UC queries fail, verify SQL warehouse, preview flags, region, and explicit grants.
- If session judges do not run, verify session metadata on every turn.
- If correlation lookup fails, distinguish trace ID from client request ID.
- If tags disappear under an OTel export path, check release notes for known exporter bugs.
- Use high-level tracing APIs unless low-level lifecycle control is necessary.
- Preserve app/prompt/model/git identifiers for every production trace.

## 14. TypeScript and Node.js tracing

Databricks documents the `mlflow-tracing` npm package and `mlflow-openai` wrapper:

```typescript
import * as mlflow from "mlflow-tracing";
import { tracedOpenAI } from "mlflow-openai";

mlflow.init({
  trackingUri: "databricks",
  experimentId: process.env.MLFLOW_EXPERIMENT_ID,
});
const client = tracedOpenAI(new OpenAI());
```

Manual APIs include `mlflow.trace(...)`, `mlflow.withSpan(...)`, and
`mlflow.startSpan(...)` with explicit `span.end(...)`. Verify package/API versions and
Databricks authentication in the TypeScript-specific page before implementation.

## Sources

- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/tracing-101
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/span-concepts
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/automatic
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/function-decorator
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/span-tracing
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/manual-tracing/low-level-api
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/app-instrumentation/typescript-sdk
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/trace-unity-catalog
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/migrate-traces-to-uc
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/redact-pii-before-export
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/prod-tracing
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/attach-tags/
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/collect-user-feedback/
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/add-context-to-traces
- https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/observe-with-traces/
