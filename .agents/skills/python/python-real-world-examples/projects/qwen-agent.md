# Qwen-Agent

> Repository: [QwenLM/Qwen-Agent@31a4d36](https://github.com/QwenLM/Qwen-Agent/tree/31a4d36d123688581a9e9744427272b33ce940e0)
> Default branch: `main`
> Commit: `31a4d36d123688581a9e9744427272b33ce940e0`
> License: [Apache-2.0](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/LICENSE)
> Domain: Tool-using agents, function calling, RAG, model providers, and multi-agent routing
> Python/native boundary: Python owns agent loops, message normalization, tool/LLM registries, retries, memory, and provider adapters. Optional model services or Transformers/OpenVINO backends are external/performance boundaries; the reviewed agent loop is Python.
> Evidence level: A for agent loop, tool/LLM registries, provider adapter, routing, retry, and tests
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/qwen-agent` (read-only pinned checkout)

## 1. Executive Architecture Summary

Qwen-Agent uses a small abstract `Agent` with a uniform `run` façade and subclass-specific `_run` workflows. An agent owns a function map of tools, an LLM object, system-message normalization, and response conversion. `FnCallAgent` adds a bounded loop: call the model, detect function calls, invoke tools, append function results, and continue until the model stops or the call budget is exhausted.

Provider variation is handled by `LLM_REGISTRY` and `get_chat_model`; tool variation is handled by `TOOL_REGISTRY` and `register_tool`. Higher-level agents such as `Assistant`, `ReActChat`, and `Router` compose these primitives for RAG, ReAct, and multi-agent delegation.

```text
User messages
     │ normalize/copy/system prompt
     ▼
Agent.run ── subclass _run workflow
     │             │
     │             ├── BaseChatModel / LLM registry ── provider adapter
     │             └── tool registry ── BaseTool / MCP / external tools
     │
     └── stream messages, function results, retry/error policy
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| Agent façade/workflows | `qwen_agent/agent.py`, `agents/` | Message normalization, workflow loops, routing, RAG, ReAct, multi-agent composition |
| Model port and adapters | `qwen_agent/llm/base.py`, `llm/__init__.py`, provider modules | Common chat contract, model registry/factory, streaming/function-call normalization |
| Tool port and registry | `qwen_agent/tools/base.py`, `tools/` | Tool schema, registration, invocation, MCP and external tool adapters |
| Memory/RAG | `qwen_agent/memory/`, `agents/assistant.py` | Query/key generation and knowledge prompt construction |
| External perimeter | DashScope/OpenAI/Azure/Transformers/OpenVINO/MCP services | Provider SDKs, model servers, files, and tool side effects |

The agent workflow is intentionally coupled to message schemas and tool-call conventions. That coupling is the product contract; a domain-independent business core is not claimed.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P08 | Factory, registry, and plugin architecture | [`qwen_agent/llm/base.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/llm/base.py) defines `register_llm`/`LLM_REGISTRY`; [`qwen_agent/llm/__init__.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/llm/__init__.py) implements `get_chat_model`; [`qwen_agent/tools/base.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/tools/base.py) defines `register_tool`/`TOOL_REGISTRY` | [`tests/llm/test_oai.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/llm/test_oai.py), [`tests/tools/test_tools.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/tools/test_tools.py), [`tests/agents/test_assistant.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/agents/test_assistant.py) | Software Design ch34; Clean Architecture ch20 | A |
| P09 | Strategy, policy, and template method | [`qwen_agent/agent.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/agent.py) fixes the public normalization loop and delegates `_run`; `agents/react_chat.py` and `agents/router.py` supply alternate workflow policies; `llm/base.py` centralizes retry policy | [`tests/agents/test_react_chat.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/agents/test_react_chat.py), [`tests/agents/test_router.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/agents/test_router.py), [`tests/llm/test_function_content.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/llm/test_function_content.py) | Software Design ch33; Clean Architecture ch15 | A |
| P12 | Adapter, façade, and provider router | [`qwen_agent/agent.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/agent.py) adapts dict/`Message` inputs and tool outputs; [`qwen_agent/llm/oai.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/llm/oai.py) normalizes OpenAI-compatible streaming/function calls; `get_chat_model` selects a provider | [`tests/llm/test_oai.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/llm/test_oai.py), [`tests/llm/test_function_content.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/llm/test_function_content.py), [`tests/agents/test_assistant.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/agents/test_assistant.py) | Clean Architecture ch19–20; Software Design ch35 | A |
| P13 | State machine, workflow, and saga | [`qwen_agent/agents/fncall_agent.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/agents/fncall_agent.py) loops through model/tool/function-result turns with `MAX_LLM_CALL_PER_RUN`; [`qwen_agent/agents/router.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/qwen_agent/agents/router.py) chooses and delegates to a named child agent | [`tests/agents/test_parallel_qa.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/agents/test_parallel_qa.py), [`tests/agents/test_router.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/agents/test_router.py), [`tests/memory/test_memory.py`](https://github.com/QwenLM/Qwen-Agent/blob/31a4d36d123688581a9e9744427272b33ce940e0/tests/memory/test_memory.py) | Clean Architecture ch18; Software Design ch38 | A |

## 4. Source Walkthrough

### `Agent.run` and `_run`

`Agent.run` deep-copies inputs, converts dictionaries to `Message`, inserts or merges a system message, and yields normalized output types from the subclass workflow. `_call_llm` and `_call_tool` are the two main runtime ports. Unknown tools return a user-visible message; unexpected tool exceptions are logged and formatted, while known service/parser errors propagate.

### Registries and adapters

`get_chat_model` resolves an explicit model type or deduces one from endpoint/model naming, then constructs the registered class. `TextChatAtOAI` adapts streamed OpenAI tool-call deltas into Qwen-Agent’s `Message`/`FunctionCall` schema. `register_tool` rejects duplicate names unless overwrite is explicitly allowed, and `Agent._init_tool` turns names/configs/objects/MCP servers into the function map.

### Workflow subclasses

`FnCallAgent` bounds the model/tool loop. `ReActChat` implements a textual Thought/Action/Observation loop. `Assistant` adds memory-backed knowledge to the prompt. `Router` asks a model to select a named child agent and falls back to the first known agent if the model emits an invalid name.

## 5. Theory Versus Practice

The stable `Agent.run` façade plus subclass `_run` is a template-method seam, while registries and provider classes implement factories and adapters. This keeps application code independent of provider-specific stream formats. The workflows are not pure domain use cases: prompts, token truncation, retries, and model conventions are intentionally in the orchestration layer because they are the framework’s core problem.

Retry policy is centralized but conservative: bad requests, unsafe-content errors, context overflow, and exhausted budgets are not retried. Tool failures are converted to text for the model in many cases, which favors agent continuity over strict transactional failure semantics.

## 6. Testing Strategy

- Agent tests exercise assistant, ReAct, router, parallel QA, and custom-tool behavior.
- LLM tests cover OpenAI-compatible construction and function-content normalization.
- Tool tests cover registry/tool schema and concrete tool behavior.
- Memory and retrieval tests isolate prompt-knowledge behavior.
- Live provider/network calls are environment-dependent and were not run in this pass.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Global LLM/tool registries | Easy extension and configuration-driven agents | Prefer an instance-local registry where tenants or plugins are untrusted |
| Text and schema conventions share the agent loop | Supports heterogeneous Qwen/OpenAI-style models | Add a typed protocol boundary when multiple teams own the provider adapters |
| Tool exceptions often become model-visible text | The agent can recover or choose another tool | Do not swallow failures for irreversible side effects; classify retryability explicitly |
| Bounded model-call loops instead of durable workflow storage | Simple streaming execution and predictable cost | Persist checkpoints for long-running agents, human approval, or resume-after-crash workflows |

## 8. Practice Exercise

Use [the registry-plugin exercise](../../python-software-architecture/exercises/registry-plugin.md) and [the workflow-state exercise](../../python-software-architecture/exercises/workflow-state.md): implement a model/tool registry, a bounded function-call loop, typed tool errors, and a pause/resume state. Test invalid registrations, malformed arguments, retryable versus terminal failures, and delegation to a child agent.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `QwenLM/Qwen-Agent`, `main` |
| Pinned revision | `31a4d36d123688581a9e9744427272b33ce940e0` |
| License | Apache-2.0, verified from repository `LICENSE` |
| Python/native boundary | Python agent/workflow/registry/adapters; external model services and optional runtime backends at the perimeter |
| Canonical pattern IDs | P08 (A), P09 (A), P12 (A), P13 (A) |
| Source evidence | Agent façade, function-call workflow, LLM/tool registries, OAI adapter, router, retry policy |
| Test evidence | Agent, router, ReAct, parallel QA, LLM, tool, and memory tests |
| Book mapping | Clean Architecture ch15 and ch18–20; Software Design ch33–35 and ch38 |
| Production compromise | Prompt/protocol coupling and text-visible tool errors favor model continuity and broad provider compatibility |
| Practice exercise | `exercises/registry-plugin.md`, `exercises/workflow-state.md` |
