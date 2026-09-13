# Project Case Study: PydanticAI

> **Repository**: [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai/tree/86b250f3d5e26f4cb25617a82904c720f690193d)
> **Default branch**: `main`
> **Commit**: `86b250f3d5e26f4cb25617a82904c720f690193d`
> **License**: MIT (`LICENSE`)
> **Domain**: Typed LLM agents, tools, streaming, provider integrations, and durable execution
> **Python version**: `>=3.10` (`pydantic_ai_slim/pyproject.toml`)
> **Evidence level**: A for the agent graph, dependency injection, model seam, and test double; B for the plugin-like capability/provider selection and durable-execution integration

APwP means *Architecture Patterns with Python*, CAP means *Clean Architecture with Python*, and SDP means *Software Design for Python Programmers*. The chapter references below use the book-to-pattern mapping maintained by the architecture skill.

## 1. Architecture Summary

PydanticAI gives an application a typed `Agent[DepsT, OutputT]`. The agent declaration holds instructions, tools, output schema, retry policy, model settings, capabilities, and concurrency limits. A run is then executed as an internal graph: user prompt, model request, tool/output processing, validation, retries, and eventual completion. `RunContext[DepsT]` is the typed boundary through which application dependencies reach tools and dynamic instructions.

The implementation is best understood as a **typed agent graph plus capability middleware**. Provider-specific model classes sit behind a common model interface, while capabilities contribute instructions, tools, model settings, request/response hooks, or event hooks. The public API is deliberately ergonomic: constructing an `Agent` also performs much of the composition and validation work that a textbook application would place in a separate composition root.

```mermaid
graph TD
    App[Application code] --> Agent[Agent[Deps, Output]]
    Agent --> Cap[Combined capabilities and toolsets]
    Agent --> Graph[UserPrompt -> ModelRequest -> CallTools]
    Graph --> Model[Model interface]
    Model --> Providers[Provider adapters / HTTP SDKs]
    Graph --> Tools[Typed tools and output validators]
    Graph --> Events[Run event stream and hooks]
    Graph --> Durable[Optional Temporal / Prefect / DBOS backends]
```

The central design question is not “which classic class hierarchy should represent an agent?” It is “which typed pieces should be assembled around one run, and which state must remain stable while the run moves through model and tool steps?” That is why the most useful patterns here are P05, P06, P07, P09, P12, P13, P14, P16, and P17.

## 2. Python Boundary

The assigned revision is Python orchestration code. There is no C++/CUDA/Rust hot path in the package slice studied here. Python owns agent configuration, graph execution, tool validation, event streams, retries, concurrency limits, and provider lifecycle. The external boundary is instead:

- provider HTTP clients and SDKs such as OpenAI-compatible clients;
- third-party model APIs and MCP toolsets;
- optional durable runtimes such as Temporal, Prefect, and DBOS.

`pydantic_ai_slim/pydantic_ai/models/_abstract.py` defines the model-facing port, while `pydantic_ai_slim/pydantic_ai/providers/_openai_compatible.py` centralizes one family of client construction and ownership rules. This keeps the core run graph independent of provider wire formats, but it does not make provider failures disappear: authentication, model capabilities, timeouts, and error translation remain adapter responsibilities.

## 3. Pattern Map

| ID | Pattern observed | Exact source | Exact test | Book mapping | Evidence | Production trade-off |
|---|---|---|---|---|---|---|
| P05 | Agent run as application service/use case | [`agent/abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/agent/abstract.py), [`agent/__init__.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/agent/__init__.py) | [`tests/test_agent.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_agent.py) | APwP ch04; CAP ch18 | A | The public agent combines use-case execution with framework configuration for a smaller user-facing API. |
| P06 | Model/provider ports and dependency inversion | [`models/_abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/models/_abstract.py), [`providers/_openai_compatible.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/providers/_openai_compatible.py) | [`tests/providers/test_openai_compatible_http_clients.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/providers/test_openai_compatible_http_clients.py) | CAP ch14–16, ch19–20 | A | One abstract model API still has to represent provider-specific features and errors. |
| P07 | Typed dependency injection and composition | [`agent/__init__.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/agent/__init__.py), [`tools.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/tools.py) | [`tests/test_deps.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_deps.py) | APwP ch13; CAP ch16 | A | `RunContext` is explicit at tool boundaries, while the `Agent` constructor performs broad wiring. |
| P08 | Capability/spec/provider discovery (plugin-like, not a global registry) | [`agent/spec.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/agent/spec.py), [`capabilities/_deferred_capabilities.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/capabilities/_deferred_capabilities.py) | [`tests/test_fallback_native_factory.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_fallback_native_factory.py) | SDP ch34; CAP ch19–20 | B | Deferred IDs and optional provider modules improve extensibility but make import and serialization compatibility part of runtime behavior. |
| P09 | Strategy/policy for model selection, retries, and end behavior | [`_agent_graph.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/_agent_graph.py), [`capabilities/abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/capabilities/abstract.py) | [`tests/test_capability_hooks.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_capability_hooks.py) | SDP ch33; APwP ch04 | A | Dynamic policy is powerful, but ordered capability hooks and per-tool retry budgets can be difficult to reason about. |
| P10 | Run events, hooks, and deferred tool results | [`capabilities/hooks.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/capabilities/hooks.py), [`agent/abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/agent/abstract.py) | [`tests/test_capability_events.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_capability_events.py), [`tests/test_streaming.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_streaming.py) | APwP ch08–11; SDP ch37 | A | The event stream is run-local and ordered; it is not a durable distributed message bus. |
| P12 | Provider adapter and OpenAI-compatible façade | [`providers/_openai_compatible.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/providers/_openai_compatible.py), [`models/openai.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/models/openai.py) | [`tests/providers/test_gateway.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/providers/test_gateway.py) | SDP ch35; CAP ch19–20 | A | A shared SDK façade reduces duplication, but provider capability matrices still leak into model profiles. |
| P13 | Explicit agent state machine and optional durable workflow | [`_agent_graph.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/_agent_graph.py), [`durable_exec/_base.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/durable_exec/_base.py) | [`tests/graph/builder/test_graph_execution.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/graph/builder/test_graph_execution.py), [`tests/durable_exec/test_durable_operation.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/durable_exec/test_durable_operation.py) | SDP ch38; CAP ch18, ch24 | A | Core runs are replayable, but durable storage and replay semantics are delegated to optional integrations. |
| P14 | Capability middleware, instrumentation, and stream processing | [`capabilities/abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/capabilities/abstract.py), [`capabilities/instrumentation.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/capabilities/instrumentation.py) | [`tests/test_capability_hooks.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_capability_hooks.py) | CAP ch23; SDP ch39 | A | Topological ordering makes middleware composable, but ordering constraints become part of the public architecture. |
| P15 | Composite toolsets and graph nodes | [`toolsets/combined.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/toolsets/combined.py), [`_agent_graph.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/_agent_graph.py) | [`tests/graph/builder/test_graph_iteration.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/graph/builder/test_graph_iteration.py) | SDP ch36, ch39 | B | Tool composition hides many implementation details, so tool identity and duplicate IDs need validation. |
| P16 | Async streams, cancellation, concurrency limits, and resource lifecycle | [`agent/abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/agent/abstract.py), [`models/concurrency.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/models/concurrency.py) | [`tests/test_streaming.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_streaming.py), [`tests/test_agent.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_agent.py) | SDP ch41 | A | AnyIO backpressure and provider close semantics are correctness features, not merely performance optimizations. |
| P17 | Deterministic test model, overrides, and boundary tests | [`models/test.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/models/test.py) | [`tests/models/test_model.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/models/test_model.py), [`tests/test_deps.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/tests/test_deps.py) | CAP ch21; APwP ch13 | A | The fake avoids network nondeterminism, while provider contract tests remain necessary. |

P01, P02, P03, P04, and P11 are not authoritative claims for this dossier: the assigned source does not show a DDD domain model, aggregate/repository/UoW transaction, or CQRS read model. P06’s model/provider port should not be mistaken for a domain repository.

## 4. Source Walkthrough

### 4.1 `Agent` is a typed composition root

[`pydantic_ai_slim/pydantic_ai/agent/__init__.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/agent/__init__.py) defines `Agent[AgentDepsT, OutputDataT]` and accepts the model, `deps_type`, output type, tools, toolsets, retries, end strategy, metadata, concurrency limits, and capabilities. The constructor combines capabilities, validates IDs, extracts capability-contributed toolsets and instructions, creates function/output toolsets, and installs scoped `ContextVar` overrides for model, dependencies, tools, and instructions.

This is DI at the point where the framework can still validate the whole run. A tool receives `RunContext[DepsT]`, rather than importing a database client or reading process globals. The nested `agent.override(...)` API is also an intentional testing seam: a test can replace dependencies or the model for one context without mutating the agent definition.

### 4.2 The run graph makes transitions inspectable

[`pydantic_ai_slim/pydantic_ai/_agent_graph.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/_agent_graph.py) contains `GraphAgentState`, `GraphAgentDeps`, `UserPromptNode`, `ModelRequestNode`, and `CallToolsNode`. State includes message history, usage, retry counters, run/conversation IDs, pending messages, event buffers, and discovered tools. Dependencies hold the resolved model, selectors, output schema/validators, tool manager, capabilities, instrumentation, and cancellation controller.

The nodes encode the workflow policy: model responses may lead to tool calls, retry prompts, output validation, or final output. `end_strategy` controls whether output and function tools are skipped, sequenced, or run exhaustively. This is a state machine in implementation terms, not a separate domain workflow object.

### 4.3 Capabilities are ordered middleware

[`pydantic_ai_slim/pydantic_ai/capabilities/abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/capabilities/abstract.py) describes a composable capability that can provide static configuration, per-run instances, wrapper toolsets, model-request hooks, response hooks, and event handling. `CapabilityOrdering` expresses `requires`, `wraps`, and `wrapped_by` relationships and turns them into a topological order.

This gives an application a stable extension point for instrumentation, content filtering, model selection, history processing, or web tools. It also means adding a capability can alter ordering and the effective model/tool surface, so the capability graph is part of the system’s architecture.

### 4.4 Models and providers are separate seams

[`models/_abstract.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/models/_abstract.py) supplies the common model identity/request lifecycle. [`providers/_openai_compatible.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/providers/_openai_compatible.py) centralizes `AsyncOpenAI` construction, supplied-versus-owned HTTP clients, and client replacement. Concrete providers can therefore share client lifecycle without forcing the graph to know their SDK details.

### 4.5 `TestModel` is the canonical fast seam

[`models/test.py`](https://github.com/pydantic/pydantic-ai/blob/86b250f3d5e26f4cb25617a82904c720f690193d/pydantic_ai_slim/pydantic_ai/models/test.py) implements a deterministic `Model` test double. It can call selected/all tools, synthesize tool arguments from JSON schema, return custom text or output-tool arguments, and record the last request parameters. It has no network wire. The result is a useful architecture test: the agent graph, dependency injection, tool validation, retries, and output handling can be tested without pretending that an HTTP mock is a model.

## 5. Theory Versus Practice

### Theoretical ideal

The books separate domain policy, application use cases, ports, adapters, and a composition root. A message bus or workflow engine should make state transitions explicit, and infrastructure should be replaceable through narrow interfaces. Tests should exercise the application against fakes and reserve a small number of contract tests for adapters.

### Production implementation

PydanticAI puts a large amount of wiring in `Agent`: capabilities are flattened into toolsets and instructions, output schemas become tools/validators, model names can be resolved lazily, and run-level overrides use context-local state. The graph is explicit internally but intentionally hidden behind `Agent.run`, `run_stream`, and `iter`. Providers are split into many optional modules, and durable execution is an optional family of adapters rather than a mandatory database/checkpoint layer.

### Difference and rationale

- **Rich agent object versus pure composition root:** a single declaration is easier for application authors and gives the framework enough information to validate tool IDs, output schemas, retries, and capabilities together. The cost is a large configuration object with runtime state nearby.
- **Context-local overrides versus constructor-only DI:** `ContextVar` overrides make tests and nested runs practical, but implicit context can surprise code that moves work across task boundaries.
- **Capability ordering versus simple decorators:** topological ordering prevents incompatible middleware orderings, but every capability can add another hidden edge to the execution graph.
- **Optional durable backends versus mandatory durability:** Temporal/Prefect/DBOS integrations keep the core lightweight. The application must choose a backend and follow its replay/serialization rules when it needs durable pause/resume.
- **Test model versus wire mocks:** `TestModel` validates graph semantics quickly; provider tests still need to cover request conversion, HTTP client ownership, and provider error behavior.

## 6. Testing Strategy

The strongest seam is the model interface. `tests/test_deps.py` proves that a dataclass dependency reaches a typed tool and that nested `agent.override(deps=...)` scopes restore correctly. `tests/models/test_model.py` exercises the deterministic model, while `tests/test_agent.py` covers run, output, tool, and model variations.

The graph builder tests (`tests/graph/builder/test_graph_execution.py` and `test_graph_iteration.py`) validate node transitions and iteration. Capability tests (`tests/test_capability_events.py` and `test_capability_hooks.py`) test extension ordering and lifecycle behavior. Provider tests (`tests/providers/test_gateway.py` and `test_openai_compatible_http_clients.py`) are the adapter/contract layer.

For durability, `tests/durable_exec/test_durable_operation.py`, `tests/durable_exec/test_prefect.py`, `tests/durable_exec/test_dbos.py`, and `tests/durable_exec/temporal/test_agent.py` verify integration-specific replay and tool/HITL paths. These tests should not be read as proof that the base agent persists state by itself; they prove that selected durable adapters can host the graph.

## 7. Lessons

- Use this shape when an agent has typed dependencies, structured output, multiple tools, retries, and provider substitution requirements.
- Prefer `RunContext` and a model test double at application boundaries; do not let tools reach into provider clients through globals.
- Treat capability ordering and tool IDs as architecture, not convenience metadata.
- Do not introduce the full capability/durable-execution model for a one-shot model call with no workflow state.
- Do not call the provider interface a transaction boundary. PydanticAI does not provide a domain repository or Unit of Work in this slice.
- A durable resume is only safe when tool side effects and custom dependencies obey the selected runtime’s serialization/replay contract.

## 8. Practice Exercise

Build a small `Agent[Deps, Output]` clone using only the standard library and Pydantic:

1. Define a `Model` protocol, a `RunContext[Deps]`, and a provider registry with one fake provider.
2. Add a tool decorator that records a typed tool definition and an output validator.
3. Implement `UserPrompt -> ModelRequest -> CallTools -> ModelRequest` transitions with separate tool/output retry budgets.
4. Add an ordered middleware/capability hook for tracing and a scoped dependency override.
5. Write tests using a scripted fake model: assert dependency injection, duplicate tool rejection, cancellation, and that a resumed/approved tool call cannot execute its side effect twice.

The design is complete when the application-facing agent never imports the fake provider directly and the test suite can exercise the graph without network access.
