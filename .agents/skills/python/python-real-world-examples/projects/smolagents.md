# smolagents

> Repository: [huggingface/smolagents](https://github.com/huggingface/smolagents/tree/30bb1161095dbae2271e6bc3cc4c219cc3897a57)
> Default branch: `main`
> Commit: `30bb1161095dbae2271e6bc3cc4c219cc3897a57`
> License: Apache-2.0
> Domain: Lightweight tool-using and code-generating agents
> Python: >=3.10 (`pyproject.toml`)
> Evidence level: A for agent loop, registries, model adapters, callbacks, and focused tests; B for external executor lifecycle
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/smolagents` (read-only pinned checkout)

## 1. Executive Architecture Summary

smolagents keeps the agent core deliberately small: a `MultiStepAgent` owns an explicit memory of task/planning/action/final-answer steps, asks a model for the next action, validates and executes tools, and emits callbacks/metrics. `CodeAgent` and `ToolCallingAgent` specialize the action protocol. Models, tools, MCP collections, and external executors are adapted behind small interfaces and secure allowlists.

```text
Task
 │
 ▼
MultiStepAgent ── AgentMemory + CallbackRegistry + Monitor
 │       │
 │       ├── Model interface ── Transformers/API/vLLM/LiteLLM/Bedrock
 │       └── tool name map ─── Tool / managed agent / MCP collection
 │                              │
 └── CodeAgent executor ── local/remote sandbox boundary
```

This is a clear Macro workflow example, but it is not a durable workflow engine: memory is in-process and serialization is opt-in. No authoritative P01–P04 domain/repository/unit-of-work pattern was found.

## 2. Layering & Boundary Discipline

| Layer | Responsibility | Evidence |
|---|---|---|
| Agent workflow | Step loop, planning, final-answer validation, managed-agent composition | `src/smolagents/agents.py` |
| State and observability | Typed memory steps, run result, token/timing metrics, logs | `src/smolagents/memory.py`, `monitoring.py` |
| Tool contract | Typed input/output metadata, lazy setup, execution validation, serialization | `src/smolagents/tools.py`, `tool_validation.py` |
| Model/provider adapters | Common `Model.generate` contract, message/tool-call normalization, provider clients | `src/smolagents/models.py` |
| Execution/security perimeter | Python executor, Docker/E2B/remote executors, MCP/Hub code loading | `local_python_executor.py`, `remote_executors.py`, `mcp_client.py` |

### Python/native boundary

The core agent, memory, tool validation, and model-adapter protocols are Python. Optional `TransformersModel` and `VLLMModel` delegate inference to PyTorch/vLLM; API models delegate to HTTP/provider SDKs; CodeAgent can delegate execution to local or remote sandboxes. There is no central native scheduler in this checkout. The important boundary is between trusted Python orchestration and code/provider execution that may be remote, optional, or untrusted.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | `MODEL_REGISTRY` and `AGENT_REGISTRY` in `src/smolagents/models.py`/`agents.py`; `TOOL_MAPPING`, `ToolCollection`, and `@tool` in `tools.py`/`default_tools.py` | `tests/test_agents.py` serialization/unknown-class tests; `tests/test_tools.py` decorator/collection tests; `tests/test_models.py` provider tests | Software Design ch34; Architecture ch13; Clean Architecture ch19–20 | A |
| P09 | Strategy and policy | `Model` interface with provider subclasses; `CodeAgent` versus `ToolCallingAgent`; configurable planning/final-answer checks/executors | `tests/test_models.py`, `tests/test_agents.py` fake-model and agent-class tests | Software Design ch33; Architecture ch04; Clean Architecture ch14 | A |
| P12 | Adapter/façade and provider router | `ApiModel`, `InferenceClientModel`, `LiteLLMModel`, `LiteLLMRouterModel`, `OpenAIModel`, `AmazonBedrockModel`, `VLLMModel`, and `ToolCollection.from_mcp` | `tests/test_models.py` provider/client/role-conversion/retry tests; `tests/test_tools.py` MCP collection tests | Software Design ch35; Clean Architecture ch19–20 | A |
| P13 | State machine/workflow | `MultiStepAgent.run`/`_run_stream`, planning/action/final-answer steps, managed agents, explicit `AgentMemory`, `RunResult` | `tests/test_agents.py` step numbering, max-step, reset, planning, tool-call, and multi-agent tests | Architecture ch08–11; Clean Architecture ch18 | A |
| P14 | Decorator, middleware, and observability | `CallbackRegistry`, per-step callbacks, `Monitor.update_metrics`, `AgentLogger`, and `@tool` metadata decoration | `tests/test_agents.py` callback registration/finalization tests; `tests/test_monitoring.py` metric/error/replay tests | Software Design ch37/ch39; Clean Architecture ch23 | A |
| P16 | Concurrency and resource lifecycle | Parallel tool-call execution in `ToolCallingAgent`, `max_tool_threads`, lazy `Tool.setup`, model cleanup, local/remote executor boundaries | Tool-calling, model, monitoring, and remote-executor tests | Software Design ch41; Clean Architecture ch23 | B |
| P17 | Testing seams and architecture fitness | Fake models, fake tools, executor injection, registry allowlists, serialization round trips, and callback mocks | `tests/test_agents.py`, `test_models.py`, `test_tools.py`, `test_memory.py`, `test_monitoring.py` | Clean Architecture ch21 | A |

No authoritative P01–P07, P10, or P11 evidence was found. The agent workflow is explicit and stateful, but it does not claim durable events, CQRS projections, or transactional consistency.

## 4. Source Walkthrough

### `src/smolagents/agents.py`

`MultiStepAgent` validates unique tool/managed-agent names, constructs `AgentMemory` and `Monitor`, and registers step callbacks. `run` resets or resumes in-process memory, then `_run_stream` performs optional planning, action generation, tool execution, step finalization, and final-answer validation until success or `max_steps`. `ToolCallingAgent` parses structured tool calls and can process multiple calls; `CodeAgent` routes model-produced code to an executor.

### `src/smolagents/memory.py`

Typed `MemoryStep` subclasses represent task, planning, action, system-prompt, and final-answer state. `AgentMemory` can reset, replay, or serialize succinct/full steps. `CallbackRegistry` dispatches callbacks by the step class MRO, preserving compatibility with callbacks that accept only the step or also the agent. The MRO dispatch is a compact way to support both general and step-specific observers.

### `src/smolagents/tools.py` and `default_tools.py`

`Tool` validates class metadata and the `forward` signature, lazily runs `setup`, sanitizes agent inputs/outputs, emits tool-calling schemas, and can serialize source code. The `@tool` decorator creates a Tool subclass from a typed function. `ToolCollection` adapts Hub/MCP collections into a list of tools. `TOOL_MAPPING` provides the built-in default-tool lookup.

### `src/smolagents/models.py`

`Model` standardizes message cleanup, role conversion, stop/tool parameters, and parsing of provider responses. Concrete classes adapt Transformers, vLLM, MLX, Hugging Face Inference, LiteLLM/router, OpenAI/Azure, and Bedrock. `MODEL_REGISTRY` is intentionally explicit: deserialization accepts only known model classes rather than importing arbitrary class paths.

### `src/smolagents/agents.py` serialization and execution boundaries

`MultiStepAgent.to_dict` records model/tool/agent metadata; `from_dict` resolves the model through `MODEL_REGISTRY`, reconstructs tools from source, and resolves agent classes through `AGENT_REGISTRY`. `execute_tool_call` validates names and arguments, substitutes state values, distinguishes managed agents from tools, and wraps failures as agent-specific errors. `trust_remote_code` gates Hub/MCP code paths, acknowledging that tool loading is executable behavior.

### `src/smolagents/monitoring.py`

`Monitor` accumulates token usage and timing from action steps, while `AgentLogger` exposes structured task, message, code, and error logging. These are deliberately injected/attached cross-cutting concerns rather than mixed into each provider implementation.

## 5. Theory Versus Practice

### Theoretical ideal

Software Design ch33/ch34 recommends a stable abstraction with replaceable strategies and controlled construction. Clean Architecture ch14/19–20 puts providers and execution mechanisms behind adapters. Architecture ch08–11 and ch18 favor explicit workflow state; ch21/ch23 favor fakes, seams, and observable execution.

### Production implementation

smolagents uses a small set of Python protocols/classes and explicit registries. Model responses are normalized to `ChatMessage`; tools are normalized to schema-bearing `Tool` objects; agent steps are stored as dataclasses and callbacks are dispatched by type. Serialization uses allowlisted model/agent classes but reconstructs tool code, while MCP/Hub loading requires an explicit trust flag.

### Difference and rationale

The library favors usability over a heavyweight dependency-injection container: dictionaries and constructor arguments are enough for a small agent. It also accepts source-code serialization because tools must be portable to Hub/Spaces, but that is a stronger trust boundary than ordinary object serialization. In-process memory makes replay and streaming simple, yet a process crash loses the run unless the caller persists `RunResult`/steps. Parallel tool calls improve latency, but tool side effects and ordering are the caller’s responsibility.

## 6. Testing Strategy

- `tests/test_agents.py` supplies fake code/tool-call models and verifies tool setup, max-step handling, resets, planning, callbacks, state substitution, serialization, managed agents, malformed output, and parallel tool calls.
- `tests/test_models.py` checks parameter precedence, role conversion, provider client construction, structured-output restrictions, retry behavior, streaming, and Transformers message formatting.
- `tests/test_tools.py` checks class/decorator validation, JSON schema and nullable arguments, source extraction, `to_dict`/`from_dict` round trips, and MCP `ToolCollection` behavior.
- `tests/test_memory.py` checks typed step initialization, dictionaries, messages, reset, and code replay.
- `tests/test_monitoring.py` checks token/timing metrics for success, max-step, errors, streaming, and replay.

The files were inspected at the pinned revision. Provider/network and optional-executor tests depend on installed extras and were not run in this research pass.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Explicit dictionaries for model/agent/tool registries | Easy to understand and secure to deserialize | Use a typed dependency container or versioned plugin manifest when graphs become large |
| Tool source-code serialization | Makes tools portable to Hub/Spaces | Never load unreviewed code; source reconstruction is execution, not data-only deserialization |
| In-process `AgentMemory` | Fast streaming, replay, and simple continuation | Add durable storage and idempotency before using it for long-running production workflows |
| Model subclasses per provider | Keeps provider quirks near their SDK | A growing provider list needs shared error taxonomy, capability discovery, and contract tests |
| Parallel tool calls | Reduces latency for independent calls | Do not parallelize tools with shared mutable state or non-idempotent side effects without explicit ordering |
| Lazy tool setup | Avoids loading expensive resources for unused tools | Define cleanup and health checks for tools that hold sockets, models, or subprocesses |

## 8. Practice Exercise

Build a mini tool-calling agent:

1. Define `Model.generate()` returning a normalized message and two fake providers with different response shapes.
2. Define a typed `@tool` decorator and a name registry that rejects duplicate tools.
3. Implement `MemoryStep` subclasses and a callback registry with general and step-specific callbacks.
4. Add a five-step limit, final-answer check, state-variable substitution, and a fake parallel tool executor.
5. Add secure serialization with an explicit model/agent allowlist and tests for unknown classes and untrusted tool loading.

The exercise is complete when providers can change without changing the agent loop, and every state transition is observable in a test.
