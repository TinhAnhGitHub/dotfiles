# MLflow AI Gateway Source Ledger

Reviewed 2026-08-30. Verify endpoint/provider support and security behavior against the
installed MLflow server and deployment mode.

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/ | Gateway purpose, unified interface, routing, security, usage, dynamic updates |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/quickstart/ | Install, SQL backend, first connection/endpoint, query paths |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/api-keys/create-and-manage/ | Reusable LLM connections and credential management |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/api-keys/key-rotation/ | API-key encryption, provider-key rotation, KEK rotation |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/create-and-manage/ | Endpoint creation, capabilities, dynamic updates, deletion |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/query-endpoints/ | Unified, OpenAI-compatible, and provider passthrough APIs |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/model-providers/ | Provider catalog and provider-specific behavior |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/traffic-routing-fallbacks/ | Traffic splitting and fallback chains |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/usage-tracking/ | Request, latency, token, error, and cost telemetry |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/budget-alerts-limits/ | Spending alerts and rejection limits |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/guardrails/ | Pre/post LLM guardrails, block/sanitize/redact behavior |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/benchmarks/ | Gateway-overhead measurement and response headers |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/coding-agents/ | Coding-agent and long-running-agent usage |
| https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/ | MLflow server HTTP authentication referenced by Gateway docs |
| https://mlflow.org/docs/latest/genai/prompt-registry/playground/ | Gateway-backed LLM Playground integration |

## Status notes

- Gateway is built into the FastAPI MLflow Tracking Server and requires a SQL-backed store.
- LLM connections are reusable credential records; endpoint edits can take effect without restart.
- Budget rejection and guardrail behavior changes application reliability and latency; test them as
  part of the application contract.
- Provider catalog/capabilities and exact APIs are moving; use installed signatures and current
  provider pages before production rollout.
