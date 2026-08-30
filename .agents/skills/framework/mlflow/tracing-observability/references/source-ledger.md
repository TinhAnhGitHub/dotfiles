# MLflow Tracing Source Ledger

Reviewed 2026-08-30. `/latest/` is moving documentation; verify all APIs against the
installed MLflow and integration versions.

## Indexes and instrumentation

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/tracing/ | Tracing overview, use cases, OTel, production SDK, integrations |
| https://mlflow.org/docs/latest/genai/tracing/quickstart/ | Python, TypeScript, OTel, experiment, session quickstart; `uvx mlflow@latest agent setup` |
| https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/automatic/ | Automatic integration taxonomy and combined auto/manual tracing |
| https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/manual-tracing/ | Decorator, wrapping, spans, attributes, previews, multimodal inputs/outputs |
| https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/opentelemetry/ | App instrumentation with OpenTelemetry |
| https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/distributed-tracing/ | Cross-service and multi-thread/process propagation |
| https://mlflow.org/docs/latest/genai/tracing/integrations/ | Framework, provider, gateway, tool, and no-code integration index |
| https://mlflow.org/docs/latest/genai/tracing/opentelemetry/ | OTLP ingestion/export and GenAI semantic conventions |
| https://mlflow.org/docs/latest/genai/tracing/faq/ | Version, setup, export, and troubleshooting FAQ |

## Observe, enhance, and deploy

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/dashboard/ | Trace dashboards and overview metrics |
| https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/ui/ | Trace list/detail UI, span tree, assessments, multimodal display |
| https://mlflow.org/docs/latest/genai/tracing/search-traces/ | SQL-like search, fields, backend limitations |
| https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/archive-traces/ | Archive and restore/lifecycle behavior |
| https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/delete-traces/ | Trace deletion controls |
| https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/multimodal/ | Images, audio, and attachment handling |
| https://mlflow.org/docs/latest/genai/tracing/token-usage-cost/ | Token and cost tracking |
| https://mlflow.org/docs/latest/genai/tracing/track-users-sessions/ | User/session metadata and grouping |
| https://mlflow.org/docs/latest/genai/tracing/attach-tags/ | Trace-level tags |
| https://mlflow.org/docs/latest/genai/tracing/collect-user-feedback/ | End-user feedback capture |
| https://mlflow.org/docs/latest/genai/tracing/observe-with-traces/masking/ | Sensitive-data masking/redaction |
| https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/logging/ | Trace logging levels |
| https://mlflow.org/docs/latest/genai/tracing/track-environments-context/ | Runtime/environment context |
| https://mlflow.org/docs/latest/genai/tracing/lightweight-sdk/ | Production `mlflow-tracing` package |
| https://mlflow.org/docs/latest/genai/tracing/prod-tracing/ | Production tracing and monitoring configuration |

## Status notes

- MLflow Tracing is documented as OpenTelemetry-compatible and supports GenAI semantic conventions.
- Automatic integrations are broad but version/provider-specific; do not assume one integration's
  API or span schema applies to another.
- Async logging, sampling, propagation, masking, and global disable are operational controls,
  not substitutes for a trace retention/privacy policy.
- Use `evaluation-monitoring` for scorers and evaluation lifecycle, and `version-tracking` for
  durable app/LoggedModel identity.
