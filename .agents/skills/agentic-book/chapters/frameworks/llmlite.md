# llmlite API and Pattern Map

**Repository**: https://github.com/zouyee/llmlite  
**Positioning**: Zig-based LLM SDK, OpenAI-compatible edge router, developer CLI, MCP server, and dashboard. It is complementary infrastructure—not a general-purpose agent orchestration framework.

## Core model

The repository describes five cooperating components:

1. **llmlite SDK** — unified provider client through a `LanguageModel`-style interface.
2. **llmlite-proxy** — gateway/router exposing OpenAI-compatible HTTP endpoints.
3. **llmlite-cmd** — CLI companion for filtered command output, direct LLM calls, memory, hooks, and savings tracking.
4. **llmlite-mcp** — MCP server exposing capabilities to compatible clients.
5. **Web dashboard** — management and analytics surface.

The design addresses the book's resource and integration patterns at the infrastructure layer. It does not replace a planner, router, reflection loop, or multi-agent supervisor.

## Important modules, components, and functions

### SDK and provider boundary

- `LanguageModel` interface/type — presents a common client abstraction across providers such as OpenAI, Anthropic, Gemini, Kimi, Minimax, and DeepSeek where supported. Use it to isolate provider selection (Ch 5/16).
- Chat/completion methods — send messages, receive responses, and support streaming. Keep provider-specific capability differences visible in tests.
- Embeddings API — supports vector generation for retrieval pipelines (Ch 14); corpus permissions, chunking, and reranking remain application responsibilities.
- Vision/multimodal, audio, image, and provider-specific APIs — extend capability coverage but should be exposed through narrow tools with explicit cost and permission policies.
- Function calling and structured output support — provide the transport boundary for Ch 5; the agent/orchestrator still validates schemas and authorizes side effects.
- Batch and streaming support — enable throughput or interactive progress. Bound concurrency and avoid treating partial streams as completed work.

### llmlite-proxy edge router

- OpenAI-compatible `/v1/chat/completions` and `/v1/embeddings` endpoints — let existing agent clients use the gateway without code changes (Ch 5/16).
- Provider routing — selects among configured providers/models based on configuration, availability, latency, or policy.
- Automatic failover — switches providers after eligible failures; classify errors and avoid duplicating non-idempotent effects.
- Circuit breaker — temporarily removes unhealthy providers to prevent retry storms (Ch 12).
- Active health checks and latency tracking — expose readiness/health and P50/P95/P99-style measurements for routing and monitoring (Ch 11/19).
- Connection pooling and rate limiting — protect upstreams and control concurrency (Ch 3/16).
- Virtual keys, team/project tenancy, and spend/cost tracking — establish quota and attribution boundaries; ensure secrets and tenant data are isolated.
- Simple/semantic caching — reduce repeated model calls where request identity and freshness allow it (Ch 16). Never cache private or side-effecting responses without a clear policy.
- Hot configuration reload — change routes/providers without rebuild; treat configuration as controlled, versioned policy.
- Metrics endpoints and analytics — support operational evaluation, but gateway metrics alone do not measure answer correctness or complete trajectories.

### llmlite-cmd CLI

- Command execution and output filtering — reduce context sent to agents and make shell results more relevant (Appendix, context engineering).
- Direct LLM access and proxy-management commands — inspect providers, health, usage, and analytics.
- Cross-session memory/search — supports developer continuity; apply retention, redaction, and user scope (Ch 8).
- Shell hooks and token-savings tracking — measure the effect of filtering and routing (Ch 16/19).
- Trust/integrity/permission-oriented commands described by the source tree — review the implementation and local policy before granting shell access.

### llmlite-mcp and operations

- MCP server component — exposes selected llmlite capabilities to MCP clients (Ch 10). Use an allowlist, authentication, rate limits, and least privilege.
- Health/readiness/Prometheus-style metrics endpoints — integrate with deployment monitoring.
- Configuration, provider, and dashboard modules — manage runtime state; do not expose administrative endpoints to an untrusted agent.

## Pattern-by-pattern use

| Book chapter | llmlite surface | Purpose |
|---|---|---|
| 1 | CLI filtering and SDK pipelines | context/data reduction |
| 2 | provider/model routing | conditional dispatch |
| 3 | pooling, rate limits, batch/streaming | bounded concurrency |
| 4 | external agent's critique loop | llmlite only transports calls |
| 5 | function calling/OpenAI-compatible API | capability boundary |
| 6 | external planner | no native planner implied |
| 7 | compatible backend for multiple agents | transport, not supervisor |
| 8 | CLI cross-session memory | operational continuity |
| 9 | analytics-informed configuration | adaptation only with gates |
| 10 | `llmlite-mcp` | MCP server |
| 11 | health/latency/usage metrics | progress/operations |
| 12 | failover/circuit breaker/rate limits | resilience |
| 13 | external approval layer | no implied HITL authority |
| 14 | embeddings/provider access | retrieval infrastructure |
| 15 | OpenAI-compatible service boundary | agent communication support |
| 16 | routing, caching, cost/latency tracking | resource optimization |
| 17 | model transport for reasoning | no reasoning guarantee |
| 18 | keys, tenancy, trust, permissions, MCP policy | security boundary |
| 19 | metrics/analytics | operational evaluation |
| 20 | gateway quotas and priorities | capacity policy |
| 21 | model/provider breadth | exploration infrastructure |

## Strengths, limits, and selection rule

Choose llmlite when you need a small native edge gateway, provider failover, OpenAI-compatible integration, cost/latency measurement, or a local MCP/CLI companion. Choose an agent framework separately for stateful orchestration, planning, tool policies, memory semantics, HITL, and evaluation. The README describes Zig 0.16+, a small edge binary, and AGPL-3.0 licensing; verify the current license and deployment obligations before embedding it in a product.

**Sources**: official repository README, source-tree structure, and MCP/architecture documentation links, accessed 2026-09-01.
