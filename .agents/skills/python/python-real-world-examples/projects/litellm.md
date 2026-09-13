# LiteLLM

> Repository: [BerriAI/litellm@9071ca5](https://github.com/BerriAI/litellm/tree/9071ca503e4d7e2dbda542ac3b68b15df015c762)
> Default branch: `litellm_internal_staging`
> Commit: `9071ca503e4d7e2dbda542ac3b68b15df015c762`
> License: [MIT](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/LICENSE)
> Domain: Multi-provider LLM gateway, routing, fallback, and observability
> Python/native boundary: Python owns the SDK, router, provider transformations, and proxy orchestration; provider SDKs and HTTP transports are perimeter dependencies. No native hot path is required by the reviewed architecture.
> Evidence level: A for provider dispatch, routing/fallback, and logging seams
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/litellm` (read-only pinned checkout)

## 1. Executive Architecture Summary

LiteLLM is a modular Python gateway with two closely related surfaces. The SDK normalizes calls from application code, selects a provider implementation, translates provider-specific request/response formats, and exposes common completion semantics. The proxy adds authentication, policy, routing, persistence, and operational hooks around that SDK.

The central architectural pressure is variation at the perimeter: model providers differ in names, capabilities, errors, streaming behavior, and metadata. LiteLLM concentrates that variation in provider handlers and a `Router`, while the public completion façade remains comparatively stable. Fallbacks and cooldowns are policy state owned by the router rather than scattered through callers.

```text
Application / Proxy route
        │
        ▼
completion() / Router.completion()
        │
        ├── routing strategy + deployment health/cooldown
        ├── bounded fallback runner
        └── provider selection and request normalization
                    │
                    ▼
       BaseLLMHTTPHandler / provider transformations
                    │
                    ▼
          OpenAI, Azure, Bedrock, and other APIs
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Public façade | `litellm/main.py` | Validate common arguments and expose sync/async completion APIs |
| Routing/application policy | `litellm/router.py`, `litellm/router_strategy/`, `litellm/router_utils/` | Select deployments, apply strategy, cooldown, fallback, and retry policy |
| Provider adapter layer | `litellm/llms/`, `litellm/llms/custom_httpx/` | Translate common requests to provider APIs and normalize responses/errors |
| Proxy and operational perimeter | `litellm/proxy/`, `litellm/integrations/` | HTTP endpoints, auth, callbacks, metrics, database/cache integrations |

The dependency direction is practical rather than textbook-clean: the shared `main.py` and router know internal provider utilities because dispatch is the product. The important seam is that callers depend on common completion/response contracts while provider-specific mechanisms stay below the router.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | `litellm/main.py` resolves a provider through `get_llm_provider`; provider packages under `litellm/llms/` supply transformations and handlers; routing strategies are selected in `litellm/router.py` | [`tests/test_litellm/llms/soniox/test_soniox_provider_registration.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/llms/soniox/test_soniox_provider_registration.py), [`tests/test_litellm/router_strategy/test_router_routing_plugins.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/router_strategy/test_router_routing_plugins.py) | Software Design ch34; Clean Architecture ch20 | A |
| P12 | Adapter, façade, and provider router | [`litellm/router.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/litellm/router.py) selects deployments and calls `function_with_fallbacks`; [`litellm/llms/custom_httpx/llm_http_handler.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/litellm/llms/custom_httpx/llm_http_handler.py) provides a common HTTP handler seam | [`tests/test_litellm/router_strategy/test_router_routing_groups.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/router_strategy/test_router_routing_groups.py), [`tests/test_litellm/litellm_core_utils/test_fallback_utils.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/litellm_core_utils/test_fallback_utils.py), [`tests/test_litellm/router_utils/test_cooldown_handlers.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/router_utils/test_cooldown_handlers.py) | Architecture with Python ch02; Clean Architecture ch19–20; Software Design ch35 | A |
| P14 | Decorator, middleware, and observability | [`litellm/litellm_core_utils/litellm_logging.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/litellm/litellm_core_utils/litellm_logging.py) centralizes call lifecycle logging; proxy/integration hooks observe success and failure around the façade | [`tests/test_litellm/proxy/utils/proxy_logging/test_pre_call_hook.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/proxy/utils/proxy_logging/test_pre_call_hook.py), [`tests/test_litellm/proxy/utils/proxy_logging/test_post_call_failure_hook.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/proxy/utils/proxy_logging/test_post_call_failure_hook.py), [`tests/test_litellm/proxy/utils/proxy_logging/test_lifecycle.py`](https://github.com/BerriAI/litellm/blob/9071ca503e4d7e2dbda542ac3b68b15df015c762/tests/test_litellm/proxy/utils/proxy_logging/test_lifecycle.py) | Clean Architecture ch23; Software Design ch39 | A |

No authoritative P01–P07, P10, P11, or P15 claim is made here. LiteLLM has caches, persistence, and many hooks, but those facts alone do not establish a domain aggregate, CQRS read model, message bus, or pipeline architecture.

## 4. Source Walkthrough

### `litellm/router.py`

`Router` is the composition point for model deployments, cache/cooldown state, routing groups, fallback configuration, and strategy selection. Its constructor validates fallback configuration and initializes the selected strategy. `completion` delegates to a fallback-aware function, which selects a deployment and calls the common completion path. Routing strategies such as simple shuffle and lowest latency remain replaceable policy modules.

### `litellm/main.py` and `litellm/litellm_core_utils/fallback_utils.py`

The sync and async public façades validate the common request shape, resolve provider information, and hand fallback cases to a dedicated runner. The fallback runner iterates through the original model and configured alternatives, preserving common response behavior while allowing provider-specific failures to be translated at the boundary.

### Provider handlers and logging

`litellm/llms/custom_httpx/llm_http_handler.py` is a concrete transport/handler seam; provider-specific directories implement transformations around it. `litellm_core_utils/litellm_logging.py` and proxy logging hooks provide lifecycle callbacks without requiring every provider adapter to implement telemetry independently.

## 5. Theory Versus Practice

Clean Architecture places external APIs behind adapters and keeps policy inward. LiteLLM follows that intent at the provider boundary, but the SDK is a large modular monolith: common policy, provider lookup, response helpers, and compatibility code share internal utilities. This reduces the cost of supporting many providers and preserves a single public API, at the cost of a broad dependency surface and more difficult local reasoning.

The router also combines strategy, health state, fallback policy, and operational counters. That is justified because routing decisions need deployment health and request failure information. A small application should not copy this amount of global policy state; a local strategy function plus one adapter is usually enough.

## 6. Testing Strategy

- Router strategy tests cover routing groups and plugin registration without requiring every provider to be live.
- Fallback tests exercise both general fallback behavior and the failure paths that trigger it.
- Cooldown and fallback-event tests verify that deployment health changes are visible to subsequent routing decisions.
- Proxy logging tests exercise pre-call, post-success, post-failure, and lifecycle seams.
- Provider registration and transformation tests isolate provider-specific behavior from the common façade.

The evidence pass inspected source and test files at the pinned commit. Live third-party provider calls and full proxy integration were not executed.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Shared SDK utilities and a broad router | One API can support many provider contracts and fallback modes | Avoid a central router for one provider or one stable transport; it becomes unnecessary coupling |
| String/config-driven provider and strategy selection | Providers remain optional and can be added without editing every caller | Add startup validation when delayed import or capability errors would be costly |
| Cooldown, retry, and fallback policy share request state | Fast failover and better availability under provider outages | Make retry budgets and idempotency explicit for non-LLM side effects |
| Cross-cutting logging is callback-oriented | Integrations can observe calls without changing each adapter | Define callback ordering and failure isolation before adding many third-party hooks |

## 8. Practice Exercise

Use [the provider-adapter exercise](../../python-software-architecture/exercises/provider-adapter.md): build a two-provider completion façade with a registry, capability validation, normalized errors, bounded retries, and lifecycle telemetry. Add a fake provider and prove that routing and logging tests do not import a real SDK.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `BerriAI/litellm`, `litellm_internal_staging` |
| Pinned revision | `9071ca503e4d7e2dbda542ac3b68b15df015c762` |
| License | MIT, verified from repository `LICENSE` |
| Python/native boundary | Python SDK/router/proxy; external provider SDKs and HTTP transports at the perimeter |
| Canonical pattern IDs | P08 (A), P12 (A), P14 (A) |
| Source evidence | `router.py`, `main.py`, fallback runner, provider HTTP handler, logging hooks |
| Test evidence | Router strategy, fallback, cooldown, provider registration, and proxy logging tests listed above |
| Book mapping | Architecture with Python ch02; Clean Architecture ch19–20 and ch23; Software Design ch34–35 and ch39 |
| Production compromise | Modular-monolith coupling is accepted to support a very broad provider matrix and operational policy surface |
| Practice exercise | `exercises/provider-adapter.md` |
