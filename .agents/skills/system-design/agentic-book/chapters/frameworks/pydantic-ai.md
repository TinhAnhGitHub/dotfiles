# PydanticAI API and Pattern Map

**Repository**: https://github.com/pydantic/pydantic-ai  
**Positioning**: typed Python AI SDK for model/provider portability, validated tools, dependencies, and structured output. The repository also points to the separate `pydantic-ai-harness` for long-running coding-agent capabilities. Verify the installed version and provider names.

## Core model

A PydanticAI `Agent` owns an agent loop. It receives instructions and a user prompt, may call tools, and returns a typed result. Python annotations and Pydantic models become contracts for model output and tool arguments. `RunContext` carries request-scoped dependencies into tools without global state.

The central design principle is **typed boundaries**: make a model produce a `BaseModel`, validate tool arguments before execution, and keep application dependencies explicit. Validation improves failure handling; it does not prove factual truth, authorization, or policy compliance.

## Important modules, classes, and functions

### Agent definition and execution

- `Agent` — configure model/provider, instructions, dependencies, tools, output type, retries, and optional capabilities. It is the main surface for Ch 1, 4, 5, 8, 14, 17, and 18.
- `agent.run(...)` / `agent.run_sync(...)` — execute async or sync runs and return a typed result object.
- `agent.run_stream(...)` — stream model/tool/output events for interactive UIs and long-running work.
- `agent.iter(...)` or equivalent iteration APIs — inspect a run's structured steps when trajectory-level control/evaluation is needed; verify the exact versioned API.
- `instructions=` and dynamic instruction functions — provide stable policy and request-dependent context. Keep authorization outside prose.
- `output_type=` — declare a Pydantic model, dataclass, primitive, or union-like result contract. Use it for typed handoffs and final-output validation.
- `retries=` and validation retry behavior — allow bounded correction when output/tool arguments fail schema validation (Ch 12), but distinguish malformed output from a transient external error.

### Types, dependencies, and tools

- `BaseModel`, `Field`, `Literal`, and validators — define constrained outputs such as enums, ranges, required evidence, or status fields (Ch 1, Ch 5).
- `RunContext[DepsType]` — carries typed dependencies, usage/context, and request-scoped state to tools and dynamic instructions.
- `@agent.tool` — registers a tool whose signature, annotations, and docstring describe the callable; the context-aware form receives `RunContext`.
- `@agent.tool_plain` — registers a tool without a context parameter for simple pure functions.
- Toolset abstractions — group or dynamically expose related tools, enforce role-specific capability sets, and implement Ch 5/18 least privilege.
- Function-tool execution — the model proposes a structured call, PydanticAI validates arguments, application code executes, and the result returns to the loop. The tool remains responsible for auth, idempotency, and side-effect policy.

### Models and providers

- Model/provider configuration — select a provider through a model string or model object; the same agent definition can be tested with different providers where compatible.
- Model settings and provider-specific settings — tune temperature, token limits, retries, and behavior without embedding provider details in domain logic.
- `UsageLimits`/usage tracking surfaces — constrain requests, tokens, or tool calls and measure resource consumption (Ch 16, Ch 19).
- Provider/model interfaces — use them to implement or swap integrations, but keep provider failure, timeout, and capability differences visible in tests.

### Structured output, messages, and streaming

- Result objects such as `AgentRunResult` (exact names are version-sensitive) — expose typed `.output`, usage, messages, and run metadata.
- Message/history types — carry model/tool exchanges for short-term continuity, debugging, and replay. Store selectively and redact sensitive values.
- Streaming result/event APIs — expose partial text or structured events; do not treat a partial stream as a committed business result.
- Output validators — enforce semantic constraints after schema parsing and request a bounded retry/refinement when appropriate (Ch 4).

### Graphs, capabilities, MCP, and long-running work

- `pydantic-graph` — typed graph/state-machine support for nodes, dependencies, and transitions where a single Agent loop is insufficient (Ch 1, 2, 3, 6, 12, 13).
- Capabilities such as web search, embeddings, image generation, and MCP — add reusable external capabilities while keeping their data and permission boundaries explicit.
- MCP capability/tool integrations — connect an agent to discoverable tools/resources; validate server trust and tool permissions outside the model (Ch 10).
- Durable execution integrations — support background/long-running operation when configured; persist state, define resume semantics, and test duplicate side effects (Ch 8, 11, 12).
- `pydantic-ai-harness` — separate companion project described by the repository as packaging memory, sub-agents, context compaction, filesystem, shell, planning, and coding-agent capabilities. Do not assume these are in the core SDK or safe by default.

### Evaluation and operations

- Evaluation/experiment integrations and Logfire/OpenTelemetry-oriented observability — trace model calls, tools, validation failures, latency, and usage for Ch 19.
- Test models and dependency injection — make tool behavior deterministic in unit tests and swap model providers in evals.
- CLI, web, voice, and realtime interfaces — run the same agent in different surfaces; presentation transport should not change authorization or core acceptance criteria.

## Pattern-by-pattern use

| Book chapter | PydanticAI surface | Purpose |
|---|---|---|
| 1 Chaining | typed output and result handoffs | reliable sequential stages |
| 2 Routing | unions/enums, dynamic instructions, graph transitions | typed dispatch |
| 3 Parallelization | async runs/tasks, graph fan-out | independent work |
| 4 Reflection | output validators, retry loop, separate evaluator agent | refinement |
| 5 Tools | `@agent.tool`, `@agent.tool_plain`, typed signatures | validated capabilities |
| 6 Planning | graph nodes or structured plan output | executable tasks |
| 7 Collaboration | sub-agents/harness or explicit handoff tools | specialization |
| 8 Memory | message history, dependencies, durable integrations | scoped continuity |
| 9 Learning | eval-driven prompt/model updates | adaptation |
| 10 MCP | MCP capability/toolset | discovery |
| 11 Goals | typed status/progress output | monitoring |
| 12 Recovery | validation retries, exceptions, durable resume | resilience |
| 13 HITL | application pause/approval around typed proposals | human authority |
| 14 RAG | retrieval capability/tool + source fields | grounding |
| 15 A2A | explicit remote tool/handoff boundary | agent communication |
| 16 Resources | usage limits/settings/model swaps | budget control |
| 17 Reasoning | structured intermediate results and graph control | deliberate inference |
| 18 Safety | typed policy fields, toolsets, validators | defense in depth |
| 19 Evaluation | usage, messages, traces, deterministic test models | trajectory metrics |
| 20 Prioritization | typed priority/task models | explainable scheduling |
| 21 Discovery | graph/agent loops with bounded outputs | experiment workflows |

## Strengths, limits, and selection rule

Choose PydanticAI when Python type checking, validated structured output, dependency injection, and provider portability are the dominant reliability needs. Choose a graph framework when topology, checkpointing, and human pauses must be first-class; use `pydantic-graph` or an external graph runtime only after comparing operational needs. Choose the companion harness for coding-agent features only after reviewing its separate security and lifecycle boundaries.

A valid Pydantic result can still be wrong, unsafe, stale, or unauthorized. Pair typed contracts with RAG/tool grounding, guardrails, HITL, exception recovery, and trajectory evaluation.

**Sources**: official repository README and linked documentation, accessed 2026-09-01.
