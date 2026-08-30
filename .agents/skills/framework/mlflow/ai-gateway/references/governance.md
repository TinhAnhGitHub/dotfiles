# AI Gateway Governance Patterns

## Stable endpoint contract

Give applications an endpoint name, not a provider API key. Keep the name stable across a
controlled model migration and record the configuration revision in the app release manifest.
Use the endpoint's capability metadata to reject unsupported tools, reasoning, caching,
structured-output, or embedding requests before they reach production.

### Native MLflow invocations

```python
import requests

response = requests.post(
    "<tracking-uri>/gateway/support/mlflow/invocations",
    json={"messages": [{"role": "user", "content": "Hello"}]},
    timeout=30,
)
response.raise_for_status()
```

### OpenAI-compatible client

```python
from openai import OpenAI

client = OpenAI(
    base_url="<tracking-uri>/gateway/mlflow/v1",
    api_key="",  # Provider credentials remain server-side.
)
response = client.chat.completions.create(
    model="support",
    messages=[{"role": "user", "content": "Hello"}],
)
```

Use the provider-native passthrough routes only when the unified request contract cannot express
the required capability. Test route identity, response shape, streaming, retries, and errors.

## Credentials and KEK rotation

Provider credentials are stored as reusable masked connections and encrypted in the backend.
For production, configure `MLFLOW_CRYPTO_KEK_PASSPHRASE` from a secret manager. To rotate the
encryption key-encryption key, stop the server for atomicity, set the current passphrase/version,
run `mlflow crypto rotate-kek --new-passphrase ...`, then deploy both the new passphrase and
incremented `MLFLOW_CRYPTO_KEK_VERSION`. A mismatch causes decryption failures.

Provider-key rotation can be:

- in-place edit for a simple zero-downtime replacement; or
- new connection → endpoint switch → observe → retire old connection for a rollback boundary.

## Routing rollout

```text
fixed eval + representative traces
  → candidate endpoint
  → low traffic split or last-resort fallback
  → compare quality/error/latency/token/cost slices
  → promote with config revision
  → retain rollback target
```

Do not assume a fallback preserves policy or tool behavior. Evaluate each provider/model and
capture the selected route in traces or gateway logs.

## Budgets and guardrails

Budget controls are operational limits, not quality tests. Set alert-only policies while
calibrating spend, then use rejection limits for well-understood workloads. Define what happens
to retries and fallback calls near the limit.

Guardrails should be tested as a pipeline:

```text
request → pre-LLM policy → provider → post-LLM policy → caller
```

Use LLM judges for semantic safety/PII/custom policy, but keep deterministic authorization,
schema, and transaction checks in application code. Post-LLM guardrails cannot preserve a
streaming response in the current documented workflow; buffer or choose another design.

## Sources

- https://mlflow.org/docs/latest/genai/governance/ai-gateway/quickstart/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/api-keys/create-and-manage/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/api-keys/key-rotation/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/create-and-manage/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/query-endpoints/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/model-providers/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/traffic-routing-fallbacks/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/usage-tracking/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/budget-alerts-limits/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/guardrails/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/benchmarks/
- https://mlflow.org/docs/latest/genai/governance/ai-gateway/coding-agents/
