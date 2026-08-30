---
name: tracing-observability
description: >
  MLflow Tracing and GenAI observability: automatic and manual instrumentation,
  OpenTelemetry ingestion/export, distributed traces, spans, sessions and users,
  trace search and UI, feedback and tags, token/cost tracking, masking, sampling,
  and the production tracing SDK. Use whenever a user asks how to trace, inspect,
  debug, search, redact, sample, or monitor an LLM application or agent with MLflow.
  Load the parent `mlflow` skill first.
compatibility: MLflow 3.x; integrations, OpenTelemetry, and the lightweight production SDK are version-gated
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-30"
---

# MLflow Tracing and Agent Observability

Treat a trace as the evidence of one application execution: the root request, nested
LLM/retriever/tool/agent spans, inputs and outputs, errors, latency, tokens, cost, tags,
session/user context, and assessments. Tracing makes evaluation and incident analysis
possible; it does not replace a curated evaluation dataset or release gate.

## Mandatory preflight

1. Inspect `mlflow.__version__`, the tracking URI, experiment, backend, and client/server
   compatibility.
2. Identify Python versus TypeScript/Java/other OpenTelemetry instrumentation and the
   framework/provider integrations involved.
3. Decide whether the target is local debugging, cross-service tracing, or production
   tracing with a latency, dependency, and failure budget.
4. Classify prompts, inputs, outputs, tool arguments, attachments, and credentials before
   exporting or displaying them.
5. Choose sampling, async logging, retention, archive/delete, and trace correlation policies.
6. For a Databricks workspace, load `databricks` and the relevant Databricks tracing skill
   before proposing UC storage, permissions, or workspace operations.

## Choose an instrumentation path

| Need | Path | Guardrail |
|---|---|---|
| Fast local setup | `uvx mlflow@latest agent setup` inside the Git project | Review the generated diff and pin the environment before CI/deployment |
| Supported Python/TS library | Automatic tracing/autologging | Verify the integration and SDK version; auto-tracing only sees supported boundaries |
| Business logic, custom tools, or missing integration | `@mlflow.trace`, `mlflow.trace(fn)`, or `start_span()` | Type important spans and set inputs/outputs explicitly |
| Existing OTel application or another language | MLflow OTLP endpoint `/v1/traces` | Use GenAI semantic conventions and preserve trace context across services |
| Small production container | `mlflow-tracing` | Keep full `mlflow` in build/evaluation environments if those APIs are needed |

The quick setup command is a convenience, not a security boundary: inspect files, dependencies,
tracking destinations, and instrumentation before accepting changes.

## Minimal Python pattern

```python
import mlflow
from mlflow.entities import SpanType

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("support-agent")
mlflow.openai.autolog()


@mlflow.trace(name="support-request", span_type=SpanType.AGENT)
def answer(question: str, *, user_id: str, session_id: str) -> str:
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,
            "mlflow.trace.session": session_id,
        },
        tags={"environment": "development"},
    )
    with mlflow.start_span(name="retrieve-context", span_type=SpanType.RETRIEVER) as span:
        span.set_inputs({"question": question})
        context = retrieve(question)
        span.set_outputs(context)
    return call_model(question, context)
```

Replace `retrieve` and `call_model` with the application implementation. Do not log secrets,
raw authorization headers, or unbounded private content. Use a typed retriever/tool span when
RAG or tool judges will inspect the trace.

## Manual tracing contract

- `@mlflow.trace` creates a span for a function and captures inputs, outputs, duration, and
  exceptions. Current docs cover sync, async, generator, and async-generator functions; check
  the installed version for the exact minor-version gates.
- `mlflow.trace(existing_function)` wraps a third-party function without changing its source.
- `mlflow.start_span()` is the context-manager path for arbitrary blocks; call `set_inputs()`
  and `set_outputs()` yourself.
- `mlflow.get_current_active_span()` updates the active span; `mlflow.update_current_trace()`
  updates root-level tags, metadata, and request/response previews.
- Put MLflow tracing outermost when stacking decorators unless a framework-specific integration
  documents a different order. Preserve parent-child relationships and record failures as spans.
- Use `SpanType.LLM`, `SpanType.RETRIEVER`, `SpanType.TOOL`, and `SpanType.AGENT` where possible.
  Trace-aware RAG and tool scorers depend on meaningful span types and structured outputs.

## OpenTelemetry and distributed tracing

MLflow accepts OTLP traces at the MLflow server's `/v1/traces` endpoint and can export MLflow
traces/metrics to an OTel collector. Use GenAI semantic conventions for portable LLM attributes,
and configure trace propagation across web requests, queues, and worker processes. Decide whether
to dual-export to MLflow and an existing OTel backend; test sampling and correlation in both.

Do not assume an OTel span is automatically a fully useful GenAI trace. Verify provider/model,
token, tool, retriever, session, and error attributes and add manual spans where the instrumentation
does not expose the application decision or intermediate result.

## Automatic integrations

The current integration index covers Python and TypeScript agent frameworks, model providers,
gateways, tracing tools, and no-code applications. The list changes quickly and includes such
families as LangChain/LangGraph, OpenAI and Anthropic, DSPy, LlamaIndex, PydanticAI, Vercel AI,
Google ADK, CrewAI, AutoGen, Bedrock AgentCore, and others. Load the official integration page
and verify the installed integration before writing `mlflow.<name>.autolog()` code.

Combine automatic tracing with manual spans for multi-agent workflows, custom retrieval, policy
checks, and tool execution. Disable tracing deliberately with the documented global API during
privacy-sensitive or health-check paths, and re-enable it in a scoped, tested way.

## Observe and operate traces

| Operation | Practice |
|---|---|
| UI/debugging | Inspect the span tree, inputs/outputs, tools, exceptions, latency, tokens/cost, feedback, and expectations |
| Search | Prefer a SQL-backed server for trace search; validate the version-specific SQL-like filter grammar before automation |
| Sessions/users | Set `mlflow.trace.session` and `mlflow.trace.user` consistently on every turn; do not use an email as a session ID by accident |
| Cost | Check provider metadata and model pricing coverage; missing or stale pricing is not zero cost |
| Privacy | Mask/redact before export where required; limit UI/MCP/reviewer access; avoid storing secrets in tags or metadata |
| Lifecycle | Archive for reversible retention changes; delete only under an explicit retention policy and audit requirement |
| Feedback | Attach user/reviewer feedback and expectations to the trace, then route approved cases to evaluation datasets |

Multimodal inputs/outputs can be displayed as content parts or attachments. Apply the same
classification and retention policy to image/audio data as to text.

## Production rules

- Use async/background trace logging where supported and monitor queue loss, shutdown flushing,
  retries, and exporter health. Do not let trace failures break the user request unless that is
  an explicit reliability decision.
- Sample high-volume traffic, but keep full coverage for safety/security or incident slices when
  feasible. Record sampling policy and app version so quality rates remain interpretable.
- Use the lightweight `mlflow-tracing` package for a small production footprint; it preserves
  tracing capability but is not a replacement for full MLflow evaluation, registry, or deployment
  packages.
- Track app version, prompt version, provider/model, environment, and endpoint in trace metadata.
  Load `version-tracking` for Git/LoggedModel identity and `evaluation-monitoring` for assessments.
- Validate masking, cross-service propagation, session grouping, streaming completion, and graceful
  process shutdown in a staging environment before enabling production capture.

## Reference router

| Need | Read |
|---|---|
| Manual/automatic instrumentation, OTel, distributed context, framework integrations | [`references/instrumentation.md`](references/instrumentation.md) |
| UI, search, sessions, tags, feedback, multimodal data, token/cost, masking, production | [`references/operations.md`](references/operations.md) |
| Exhaustive current docs index and feature gates | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

A tracing implementation must identify its destination and version, capture the execution path
needed for debugging/evaluation, protect sensitive fields, preserve correlation across services,
measure exporter overhead/loss, and document sampling/retention. A trace with only a final answer
is insufficient for diagnosing an agent, RAG, or tool failure.

## Related skills

- `evaluation-monitoring` for datasets, scorers, automatic evaluation, issue detection, and review.
- `version-tracking` for app/LoggedModel/Git identity on traces.
- `genai-flavors` for packaging traced applications and ResponsesAgent models.
- `ai-gateway` for provider routing, budgets, guardrails, and gateway request traces.
- `mcp-server` for coding-agent access to MLflow trace data.
