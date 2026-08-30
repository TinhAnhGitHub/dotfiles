# Tracing Instrumentation Patterns

Use the official tracing index and the installed MLflow API signature as the source of
truth. This reference condenses the current Python, TypeScript, and OpenTelemetry paths;
it is not a substitute for checking provider/framework compatibility.

## Start with the smallest useful boundary

```python
import mlflow


@mlflow.trace(name="answer")
def answer(question: str) -> str:
    return application_answer(question)
```

Add nested spans around retrieval, tools, policy checks, and other decisions that explain
the final output. Use `SpanType` values where the downstream evaluation or UI needs semantic
classification.

## Manual API choices

| API | Use |
|---|---|
| `@mlflow.trace(...)` | Decorate an application function; captures inputs/outputs/errors and nests with active spans |
| `mlflow.trace(fn)` | Wrap a third-party or existing function without editing it |
| `mlflow.start_span(...)` | Trace an arbitrary block and set inputs/outputs manually |
| `mlflow.get_current_active_span()` | Add attributes or inputs/outputs from inside the current span |
| `mlflow.update_current_trace(...)` | Add root tags, metadata, and request/response previews |

Current documentation covers sync, async, generator, and async-generator functions, but
the support gates are MLflow-minor-specific. Inspect the target version before promising
streaming or async behavior. Keep `@mlflow.trace` outermost when combining decorators unless
the framework integration requires another order.

## Automatic tracing

Automatic integrations capture known provider/framework boundaries. Typical setup is:

```python
import mlflow

mlflow.set_tracking_uri("<tracking-uri>")
mlflow.set_experiment("<experiment-name>")
mlflow.openai.autolog()  # Substitute the installed integration.
```

Use the integration index to identify the actual import and package extra. The current index
contains Python and TypeScript agent frameworks, model providers, gateways, third-party tools,
and no-code applications. Automatic tracing does not prove that every custom tool, retriever,
queue, or business decision is represented; add manual spans at those boundaries.

Combining auto and manual tracing is the preferred pattern for multi-agent flows. Test that
manual spans are children of the expected root and that repeated provider calls do not create
duplicate or orphaned traces.

## OpenTelemetry ingestion/export

MLflow's tracking server exposes an OTLP trace endpoint:

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="<tracking-uri>/v1/traces"
export OTEL_EXPORTER_OTLP_TRACES_HEADERS="x-mlflow-experiment-id=<experiment-id>"
```

Use native GenAI semantic conventions for provider/model, token, tool, and retrieval data.
When an existing collector is authoritative, configure MLflow as one exporter or ingest
through the collector and verify trace IDs remain correlated. Test both HTTP and worker/queue
propagation in distributed applications.

OTel instrumentation can emit valid spans without producing the fields needed by MLflow's
trace UI or trace-aware judges. Inspect a real trace and supplement missing fields with manual
attributes/spans rather than relying on span names alone.

## Production instrumentation

For production:

1. Pin the full application and exporter versions.
2. Enable async/background logging where supported and test queue flush on shutdown.
3. Choose an explicit sampling policy and preserve unsampled incident identifiers elsewhere.
4. Configure exporter retry, timeout, and failure behavior so observability failures do not
   unexpectedly fail user requests.
5. Use `mlflow-tracing` when dependency footprint matters; keep full MLflow in development,
   evaluation, registry, or packaging environments.
6. Verify PII masking/redaction before traces leave the process or become visible to reviewers.

## Sources

- https://mlflow.org/docs/latest/genai/tracing/
- https://mlflow.org/docs/latest/genai/tracing/quickstart/
- https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/automatic/
- https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/manual-tracing/
- https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/opentelemetry/
- https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/distributed-tracing/
- https://mlflow.org/docs/latest/genai/tracing/integrations/
- https://mlflow.org/docs/latest/genai/tracing/opentelemetry/
- https://mlflow.org/docs/latest/genai/tracing/lightweight-sdk/
- https://mlflow.org/docs/latest/genai/tracing/prod-tracing/
