# Trace Operations and Production Controls

## UI and programmatic inspection

The MLflow trace UI exposes the request/response, span tree, execution time, state,
tools, exceptions, token/cost information, tags, feedback, and expectations. Use the UI
for a first diagnosis, then preserve a small reproducible trace or evaluation record.

Trace search uses a SQL-like filter language. Search syntax and field names vary by MLflow
version/backend; validate a query against a small result set before scheduling it. A SQL
backend is the safe default for current search workflows; the FileStore path is deprecated
for newer trace search capabilities.

Typical query dimensions include:

- trace status, timestamps, run ID, client request ID, name;
- prompt name/version and span name/type;
- tags and metadata;
- feedback and expectation values;
- trace text on supported SQLAlchemy-backed OSS stores.

Do not expose a broad trace search tool to an assistant or reviewer when field selection is
enough. The MLflow MCP Server supports `extract_fields` for selecting only required paths.

## Sessions, users, and version context

Set stable metadata on every turn:

```python
mlflow.update_current_trace(
    metadata={
        "mlflow.trace.user": user_id,
        "mlflow.trace.session": session_id,
        "app_version": resolved_app_version,
    }
)
```

Use a non-sensitive stable user identifier and a separate opaque session identifier. For
multi-turn evaluation, missing or inconsistent session IDs prevent conversation-level judges
from seeing the full interaction. Also record prompt/model/tool versions needed to explain
behavior; do not put secrets or raw credentials in tags.

## Tokens, cost, and multimodal content

Token and cost views depend on provider metadata and model pricing coverage. Treat missing
pricing as unknown, not zero. Validate model names, usage fields, and custom pricing before
using cost in a release or budget gate.

Images/audio and other content parts can be stored in span inputs/outputs and rendered in
the UI. Apply content classification, size limits, retention, and access controls to binary
attachments as well as text.

## Feedback and expectations

- Feedback records how an execution performed; it may come from a user, reviewer, code scorer,
  or LLM judge.
- Expectations record what should have happened and are the stronger source for ground truth.
- Preserve source, rationale, reviewer, and timestamp. Override automated feedback rather than
  rewriting it when a human intentionally supersedes a judge.
- Route approved trace cases to the evaluation-monitoring dataset workflow.

## Privacy and lifecycle

Apply masking/redaction before export or reviewer access. Test nested tool arguments, exception
messages, request previews, headers, and attachments—these are common leakage paths. Use archive
for reversible retention changes; delete only with an explicit retention policy, access review,
and audit record. Deleting a trace can remove context needed to interpret assessments.

## Production reliability

Observe exporter queue depth, dropped spans, retry/timeout counts, and shutdown flushing. Test
sampling, async logging, OTel propagation, streaming, and process restarts under load. A trace
pipeline that blocks or crashes the application is an availability risk; choose fail-open or
fail-closed behavior intentionally.

## Sources

- https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/dashboard/
- https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/ui/
- https://mlflow.org/docs/latest/genai/tracing/search-traces/
- https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/archive-traces/
- https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/delete-traces/
- https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/multimodal/
- https://mlflow.org/docs/latest/genai/tracing/track-users-sessions/
- https://mlflow.org/docs/latest/genai/tracing/attach-tags/
- https://mlflow.org/docs/latest/genai/tracing/collect-user-feedback/
- https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/masking/
- https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/logging/
- https://mlflow.org/docs/latest/genai/tracing/track-environments-context/
- https://mlflow.org/docs/latest/genai/tracing/token-usage-cost/
