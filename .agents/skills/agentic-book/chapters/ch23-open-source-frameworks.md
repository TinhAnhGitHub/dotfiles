# Chapter 23: Open-Source Framework and Repository Map

## Core Idea
The book's patterns are framework-independent. These repositories provide different canvases for implementing them: graph orchestration, component/integration libraries, agent platforms, typed SDKs, agent harnesses, or model gateways. Choose by the control boundary your system needs—not by the number of features in a README.

For concrete API-level details, read the dedicated deep dives:

- [LangGraph](frameworks/langgraph.md)
- [Agno](frameworks/agno.md)
- [PydanticAI](frameworks/pydantic-ai.md)
- [LangChain](frameworks/langchain.md)
- [Google ADK](frameworks/google-adk.md)
- [OpenAI Agents SDK](frameworks/openai-agents-python.md)
- [DeepSeek Harness](frameworks/deepseek-harness.md)
- [llmlite](frameworks/llmlite.md)

**Research basis**: official repositories and READMEs fetched on 2026-09-01. APIs and repository status change; verify current documentation before implementation.

## Frameworks Introduced

### LangGraph — `langchain-ai/langgraph`
**Repository**: https://github.com/langchain-ai/langgraph  
**Role**: Low-level stateful orchestration for long-running agents and workflows. Its central vocabulary is graph execution: state, nodes, edges, persistence/checkpointing, interrupts, and subgraphs. It can be used independently of LangChain and is a natural fit for explicit control flow, durable execution, human pauses, memory, reflection loops, and multi-agent graphs.

**Book mapping**: Ch 1 chaining, Ch 2 routing, Ch 3 parallelization, Ch 4 reflection, Ch 6 planning, Ch 8 memory, Ch 11 monitoring, Ch 12 recovery, Ch 13 HITL, Ch 14 RAG, Ch 19 evaluation.

**Use it when**: the workflow needs explicit state transitions, cycles, resumability, checkpoints, or human inspection/modification of state.  
**Trade-off**: more orchestration control means more state-machine design and operational responsibility. It is not automatically a complete product platform.

### LangChain — `langchain-ai/langchain`
**Repository**: https://github.com/langchain-ai/langchain  
**Role**: Component and integration framework for models, messages, tools/toolkits, embeddings, retrievers, vector stores, and agents. It emphasizes interoperable abstractions and rapid composition; LangGraph is the lower-level choice for more controllable workflows. LangSmith is the associated ecosystem for tracing/evaluation/deployment, not the same library.

**Book mapping**: Ch 1 chains, Ch 5 tools, Ch 14 RAG, Ch 17 reasoning, Ch 19 evaluation; use LangGraph for the book's durable graph patterns.

**Use it when**: the main challenge is connecting providers and reusable LLM application components, especially during prototyping or when many integrations are required.  
**Trade-off**: abstraction and integration breadth can obscure runtime control. Drop to explicit graph/orchestration primitives when reliability, state, or side effects matter.

### Agno — `agno-agi/agno`
**Repository**: https://github.com/agno-agi/agno  
**Role**: Agent framework and runtime for agent platforms. The repository foregrounds `Agent`, `Team`, `Workflow`, tools, models, knowledge, memory, storage, and AgentOS. AgentOS adds a service/runtime and UI layer with APIs, traces, authentication/RBAC, and deployment-oriented capabilities.

**Book mapping**: Ch 5 tools, Ch 7 teams, Ch 8 memory, Ch 9 learning, Ch 14 knowledge/RAG, Ch 18 guardrails, Ch 19 monitoring.

**Use it when**: you want a batteries-included platform surface for serving agents, teams, workflows, storage, knowledge, memory, and operational management.  
**Trade-off**: a platform runtime introduces deployment and persistence choices. Keep business policy and evaluation separate from AgentOS so the design remains portable.

### PydanticAI — `pydantic/pydantic-ai`
**Repository**: https://github.com/pydantic/pydantic-ai  
**Role**: Python-first, type-centric agent SDK. Its core concepts include `Agent`, model/provider selection, typed dependencies, function tools/toolsets, instructions, validated structured output, and `RunContext`. The project also contains graph-oriented capabilities and points to the separate Pydantic AI Harness for long-running coding-agent capabilities such as planning, sub-agents, context management, filesystem, and shell access.

**Book mapping**: Ch 1 structured handoffs, Ch 5 typed tools, Ch 6 planning, Ch 8 state, Ch 9 adaptation, Ch 12 validation/recovery, Ch 13 HITL, Ch 17 reasoning, Ch 19 evaluation.

**Use it when**: Python typing, dependency injection, schema validation, and predictable output contracts are primary requirements.  
**Trade-off**: typing validates boundaries but does not make an agent correct or safe. Policies, authorization, retrieval quality, and trajectory evaluation still need explicit design.

### Google ADK — `google/adk-python`
**Repository**: https://github.com/google/adk-python  
**Role**: Modular, code-first agent and workflow framework. Its current README describes `Agent`, `Runner`, `Tool`, `Session`, `Memory`, and a graph-based `Workflow`; ADK 2.0 highlights routing, fan-out/fan-in, loops, retries, state, dynamic nodes, nested workflows, task-mode agent delegation, streaming, and HITL. It is optimized for Gemini but describes itself as model- and deployment-agnostic.

**Book mapping**: all core patterns, especially Ch 2 routing, Ch 3 parallelization, Ch 6 planning, Ch 7 collaboration, Ch 8 memory, Ch 10 MCP, Ch 11 monitoring, Ch 12 recovery, Ch 13 HITL, and Ch 15 A2A.

**Use it when**: you want a framework with explicit workflow nodes plus agent delegation, sessions, events, tools, and Google ecosystem integration.  
**Trade-off**: ADK 2.0 includes breaking changes from 1.x in agent APIs, events, and session schema. Pin versions and test upgrade paths.

### OpenAI Agents SDK — `openai/openai-agents-python`
**Repository**: https://github.com/openai/openai-agents-python  
**Role**: Compact Python SDK centered on `Agent` and `Runner`, with instructions, tools, guardrails, handoffs, sessions, tracing, MCP tools, and optional sandbox, realtime, and voice agents. It supports OpenAI APIs and other model providers through provider boundaries.

**Book mapping**: Ch 5 tools, Ch 7 delegation/handoffs, Ch 8 sessions, Ch 10 MCP, Ch 13 HITL, Ch 18 guardrails, Ch 19 tracing/evaluation, plus Ch 15 when an agent boundary is exposed remotely.

**Use it when**: you want a small, opinionated agent loop with first-class handoffs, guardrails, sessions, tracing, and optional workspace/voice capabilities.  
**Trade-off**: the compact loop is easy to start but complex bespoke topologies may need explicit application orchestration or another graph layer.

### DeepSeek Harness — `deepseek-ai/deepseek-harness`
**Repository**: https://github.com/deepseek-ai/deepseek-harness  
**Role**: An open-source agent harness (`dsh`) built around an “everything-is-a-plugin” architecture and Cordis. It is a product-like runtime and user-facing harness rather than a generic Python orchestration library; the repository describes a Web UI, CLI/source workflows, plugins, documentation, and a developer-preview status.

**Book mapping**: Ch 5 tools, Ch 7 collaboration through plugins, Ch 8 sessions/memory, Ch 10 MCP, Ch 12 recovery, Ch 16 resource-aware runtime concerns, Ch 18 safety, Ch 19 observability.

**Use it when**: you want to study or extend a plugin-oriented agent harness, especially for interactive developer workflows and extensible runtime capabilities.  
**Trade-off**: the repository explicitly warns of compatibility-breaking changes during developer preview. Treat it as unstable; review its safety notice before running it and isolate credentials/workspaces.

### llmlite — `zouyee/llmlite`
**Repository**: https://github.com/zouyee/llmlite  
**Role**: A Zig-based, zero-dependency LLM SDK, edge router, and CLI toolkit—not a full agent orchestration framework. The repository describes a unified multi-provider SDK, `llmlite-proxy` with OpenAI-compatible endpoints, routing/failover/circuit breaking/latency tracking/cost tracking/caching, `llmlite-cmd`, an MCP server, and a dashboard.

**Book mapping**: Ch 5 tool/API boundary, Ch 10 MCP, Ch 12 failure handling, Ch 16 resource-aware optimization, Ch 19 operational metrics. It supports an agent framework rather than replacing Ch 1–7 orchestration.

**Use it when**: the bottleneck is provider abstraction, edge deployment, failover, rate limiting, cost/latency routing, or giving existing OpenAI-compatible agents a local gateway.  
**Trade-off**: it moves infrastructure into a native Zig gateway and is licensed AGPL-3.0 according to the fetched README; confirm licensing and deployment obligations for your use.

## Selection Matrix

| Need | Best first candidates | Why |
|---|---|---|
| Explicit durable graphs and state | LangGraph, Google ADK | Nodes/edges, loops, checkpoints, pauses, workflow control |
| Broad model/tool/retriever integrations | LangChain | Interoperable components and ecosystem |
| Platform/runtime/UI for agents | Agno, Google ADK | Agents, teams/workflows, storage, serving, operations |
| Typed Python contracts | PydanticAI | Validated tools, dependencies, structured output |
| Compact handoff-oriented loop | OpenAI Agents SDK | Runner, handoffs, guardrails, sessions, tracing |
| Plugin-first interactive harness | DeepSeek Harness | Extensible runtime and developer workflow surface |
| Provider gateway and edge economics | llmlite | OpenAI-compatible proxy, failover, budgets, metrics |

## Design Guidance

1. Keep the book's domain model—mission, state, contracts, policy, evidence, evaluation—above framework APIs.
2. Prototype with the simplest fitting canvas: LangChain/PydanticAI/OpenAI Agents for focused loops; LangGraph/ADK for explicit graphs; Agno for a served platform.
3. Put authorization, approval, retries, idempotency, and audit outside model-generated instructions.
4. Treat MCP as a capability protocol and A2A as an agent boundary; a framework supporting either does not remove security design.
5. Measure framework choice by trajectory quality, recovery behavior, latency, cost, portability, and operational burden.
6. Pin versions and read release notes: ADK 2.0 and DeepSeek Harness preview status demonstrate that framework behavior can change underneath a pattern.

## Key Takeaways
1. LangGraph and ADK are strongest when workflow control and resumability are central.
2. LangChain is an integration/component layer; it is not interchangeable with LangGraph.
3. PydanticAI is valuable when contracts and typed boundaries are the main reliability lever.
4. Agno and DeepSeek Harness are more runtime/platform-oriented than minimal SDKs.
5. OpenAI Agents SDK provides a compact loop with strong handoffs, guardrails, sessions, and tracing.
6. llmlite is complementary infrastructure, especially for resource-aware multi-provider operation.
7. No repository substitutes for the book's safety, recovery, and evaluation patterns.

## Connects To
- **Ch 5**: Every framework eventually turns model proposals into validated tool calls.
- **Ch 7**: Handoffs, teams, plugins, and task APIs implement different collaboration boundaries.
- **Ch 10 / Ch 15**: MCP and A2A are protocols that can cross framework boundaries.
- **Ch 16 / Ch 19**: Gateways and observability make cost and trajectory behavior measurable.
