---
name: ai-gateway
description: >
  MLflow AI Gateway governance for LLM providers: encrypted LLM connections,
  unified and passthrough endpoints, model capabilities, traffic splitting,
  fallbacks, usage/cost tracking, budget limits, LLM guardrails, benchmarks,
  and coding-agent routing. Use whenever a user asks to centralize provider
  credentials, route models, add failover, control spend, enforce policies,
  or call an MLflow Gateway endpoint. Load the parent `mlflow` skill first.
compatibility: MLflow 3.x; AI Gateway requires the FastAPI tracking server and a SQL backend store
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-30"
---

# MLflow AI Gateway

Use AI Gateway as the runtime governance plane between applications and model providers. It
centralizes credentials, exposes stable endpoint names, routes traffic, applies guardrails,
and records usage. It is not the Prompt Registry, Model Registry, agent server, or a substitute
for application-level authorization and output validation.

## Mandatory preflight

1. Inspect MLflow client/server versions and confirm the FastAPI tracking server is being used.
2. Confirm a SQL backend store: SQLite, PostgreSQL, MySQL, or MSSQL; file-based tracking stores
   are not supported for Gateway.
3. Define providers, model capabilities, streaming/tool/Responses/embedding requirements, and
   the endpoint names that applications will consume.
4. Decide who may create connections/endpoints, how provider keys are encrypted/rotated, and
   how requests are authenticated to the MLflow server.
5. Define routing, fallback, guardrail, budget, logging, retention, and rollback policies before
   connecting a production agent or coding assistant.
6. Load `tracing-observability` for trace semantics and `evaluation-monitoring` before using
   Gateway judges, guardrails, or model migrations as quality gates.

## Core object model

```text
LLM connection (provider credentials/configuration)
  → Gateway endpoint (stable name + provider/model/capabilities)
      → traffic split or ordered fallback
          → unified or provider-native API
              → request/usage/cost trace and guardrail assessments
```

Keep a connection reusable but environment/team-scoped. Keep the endpoint name stable while
changing its model only under a tested rollout policy. Record the resolved provider/model,
route, prompt/app version, and Gateway configuration revision in release evidence.

## Quickstart

```bash
pip install 'mlflow[genai]'
mlflow server --port 5000
```

Create an LLM connection and endpoint in the MLflow UI or via the current Gateway API. The UI
stores provider credentials encrypted and keeps them masked. Query the endpoint through the
native invocations API:

```bash
curl -X POST http://localhost:5000/gateway/support/mlflow/invocations \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

The exact endpoint/provider configuration API evolves quickly; inspect the installed API or use
the current official endpoint guide rather than inventing a client method.

## Query styles

| Style | URL | Use |
|---|---|---|
| MLflow unified | `/gateway/{endpoint_name}/mlflow/invocations` | Stable MLflow interface for chat and embeddings; preserves Gateway routing |
| OpenAI-compatible | `/gateway/mlflow/v1` with endpoint name as `model` | Drop an existing OpenAI client in without provider-key changes |
| OpenAI passthrough | `/gateway/openai/v1/chat/completions`, `/embeddings`, `/responses` | Provider-native OpenAI features |
| Anthropic passthrough | `/gateway/anthropic/v1/messages` | Native Anthropic Messages API |
| Gemini passthrough | `/gateway/gemini/v1beta/models/{endpoint}:generateContent` | Native Gemini request shape |

Use unified APIs for portability and routing. Use passthrough only when the provider-specific
capability is required, and test that the endpoint's model supports tools, reasoning, caching,
structured output, streaming, or embeddings as requested.

## Security and credential lifecycle

- Never commit provider API keys, Gateway encryption passphrases, or bearer tokens.
- Configure a custom `MLFLOW_CRYPTO_KEK_PASSPHRASE` in production; the local default is for
  development/single-user use. File-based tracking stores are not a supported production path.
- Rotate a provider key by editing the shared connection for zero-downtime replacement, or create
  a new connection and switch endpoints when an explicit rollback boundary is needed.
- Rotate the encryption key-encryption key with `mlflow crypto rotate-kek`; update both
  `MLFLOW_CRYPTO_KEK_PASSPHRASE` and `MLFLOW_CRYPTO_KEK_VERSION` together before restarting.
- Restrict Gateway server access independently of provider-key access. A centralized key does not
  grant every caller permission to invoke every model.
- Treat prompts, responses, tool arguments, and guardrail rationales as potentially sensitive
  trace data; load `tracing-observability` for masking and retention.

## Routing, fallback, and dynamic changes

Traffic splitting supports A/B tests, gradual migrations, and load distribution. Ordered fallback
chains improve availability when a provider/model fails. They do not guarantee semantic equivalence:
the release gate must evaluate every route and record which route served each trace.

Gateway endpoint and connection updates take effect dynamically without a server restart. Use that
power carefully:

1. Create a candidate endpoint/connection.
2. Exercise it on fixed evaluation data and representative traces.
3. Start with a small traffic slice or a deliberate fallback position.
4. Compare quality, latency, error rate, token usage, and cost.
5. Promote or roll back using an auditable configuration change.

Deleting an endpoint removes it from service immediately; migrate callers first.

## Usage, cost, and budgets

Gateway requests are traced and can expose request counts, latency, errors, tokens, and cost
trends. Validate provider pricing/model metadata and distinguish unknown cost from zero. Use
p50/p90/p99 latency and per-team/provider/model slices rather than only a global average.

Budget policies can be daily, weekly, or monthly and can alert through a webhook or reject new
requests. A rejected request returns HTTP 429 after the limit is reached. Define the behavior for
critical traffic, retries, fallback requests, and streaming before enabling hard limits. Local
and Redis-backed usage trackers have different durability/coordination properties; choose the
deployment mode deliberately.

## Guardrails

Gateway guardrails can run an LLM judge before the provider call, after the response, or in a
pre/post pipeline. Use `{{inputs}}` and `{{outputs}}` in the documented judge configuration,
then choose block, sanitize, or redact behavior. Post-response guardrails do not support streaming
responses in the current guide, so do not advertise full streaming compatibility without testing.

Guardrails add latency and model cost and may false-positive. Calibrate them on human-reviewed
examples, version the policy/judge, log decisions, and keep deterministic checks in the application
for schema, authorization, and transactional invariants.

## Benchmarks and coding agents

Measure Gateway overhead in the target network/deployment. The documented response header
`X-MLflow-Gateway-Duration-Ms` can help separate Gateway time from provider time for non-streaming
requests. Do not carry example benchmark numbers into an SLO without reproducing them.

Coding agents and long-running agents benefit from stable endpoint names, centralized tracing,
budget controls, and guardrails. Apply narrower endpoint permissions and smaller tool/model
allow-lists to agents than to general internal experimentation.

## Reference router

| Need | Read |
|---|---|
| Install, server, connection, endpoint, and query patterns | [`references/governance.md`](references/governance.md) |
| Complete Gateway index, subpages, and status notes | [`references/source-ledger.md`](references/source-ledger.md) |

## Quality bar

A Gateway design must identify its SQL backend and auth boundary, keep credentials out of source
and traces, preserve endpoint/model/route identity, test streaming/tools/embeddings as applicable,
measure latency and cost, define fallback and budget behavior, calibrate guardrails, and provide a
rollback path for dynamic changes.

## Related skills

- `tracing-observability` for request/span context, masking, token/cost, and production exporters.
- `evaluation-monitoring` for judges, datasets, regression gates, and guardrail calibration.
- `prompt-registry` for versioned prompts and the Prompt Engineering UI/Playground.
- `agent-serving` for hosting a Responses API-compatible agent.
- `mcp-server` for coding-agent access to MLflow trace data.
