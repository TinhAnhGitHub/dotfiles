# Google ADK API and Pattern Map

**Repository**: https://github.com/google/adk-python  
**Positioning**: modular, code-first Python framework for agents and graph-based workflows. The repository describes ADK 2.0 as breaking from 1.x in agent APIs, events, and session schema; pin versions and verify documentation.

## Core model

ADK separates an **Agent** that reasons/uses tools from a **Workflow** that orchestrates nodes. A `Runner` executes the application and coordinates sessions/events. The system supports LLM agents, deterministic workflow nodes, routing, fan-out/fan-in, loops, retries, state, nested workflows, streaming, task-mode delegation, MCP tools, and HITL.

## Important modules, classes, and functions

### Agents and execution

- `Agent` / `LlmAgent` — configure name, model, instruction, tools, output behavior, sub-agents, and delegation. Use for Ch 5, 7, 14, 17, and 18.
- `BaseAgent` — common agent contract for custom agents and workflow composition.
- `Runner` — runs an agent/workflow with a session and event stream. It is the execution boundary for Ch 8, 11, 12, 13, and 19.
- `Runner.run(...)`/async event iteration — yields model, tool, state, and workflow events. Consume and persist only what is needed; redact sensitive payloads.
- `Event` and event actions/state deltas — represent observable transitions and state changes. Use them for progress, replay, and trajectory evaluation.

### Workflow nodes and topologies

- `Workflow` — graph-oriented orchestration with edges between agents/nodes. Use when topology must be inspectable.
- `SequentialAgent` — fixed ordered execution (Ch 1).
- `ParallelAgent` — concurrent independent branches (Ch 3); use explicit join/merge validation.
- `LoopAgent` — repeated execution under a termination condition (Ch 4, 11, 17, 21); always bound iterations and budget.
- `BaseNode` / custom function nodes — deterministic transformations, validators, policy gates, and application logic. Prefer code for authorization and schema checks.
- Conditional edges/routing nodes — select a branch from state or model classification (Ch 2).
- Dynamic nodes and nested workflows — construct or delegate subgraphs when the task requires specialization or runtime composition (Ch 6/7).

### Context, sessions, state, and memory

- `Context` — carries request/workflow-scoped state and runtime services into nodes. Treat it as a contract, not an unbounded bag.
- `ToolContext` — gives tools access to invocation context, state, and controlled actions.
- `SessionService` and `InMemorySessionService` — store session history/state for execution; use a durable implementation in production.
- Session identifiers, state keys, and state deltas — separate conversation state from application/workflow variables. Define scope and retention.
- Memory service/search integrations — support long-term retrieval distinct from the current session (Ch 8/14).
- Checkpoint/resume and workflow resumability features — support Ch 12 recovery and Ch 13 human pauses; test idempotency around resumed writes.

### Tools and protocols

- Function/custom tools — expose ordinary Python capabilities with schemas and controlled context.
- OpenAPI tools — integrate API-described operations; still enforce auth, argument validation, quotas, and side-effect approvals.
- MCP toolsets — discover/use MCP tools and resources (Ch 10). Discovery is not permission.
- Long-running function/task tools — represent work that needs progress or later completion; define lifecycle, timeout, and ownership.
- Agent transfer/delegation and task mode — pass work to another agent with explicit inputs/results (Ch 7/15).

### Resilience, human control, and evaluation

- Workflow retry policies and node error handling — implement bounded transient retries and fallback (Ch 12).
- Interrupt/HITL mechanisms — pause a run, collect human input, update state, and resume (Ch 13).
- Callbacks/plugins — observe or intercept model/tool/workflow lifecycle for guardrails, logging, metrics, and policy. Avoid hidden mutation order.
- ADK evaluation/`adk eval` workflow — run eval sets and inspect results (Ch 19). Add domain-specific correctness, safety, and trajectory checks.
- CLI/development UI commands such as `adk run`, `adk web`, and `adk eval` — useful for local iteration and demonstrations; deployment security still requires explicit configuration.

## Pattern-by-pattern use

| Book chapter | ADK surface | Purpose |
|---|---|---|
| 1 | `SequentialAgent`, workflow edges | chaining |
| 2 | conditional routing/edges | dispatch |
| 3 | `ParallelAgent`, fan-in | concurrency |
| 4 | `LoopAgent`, critic nodes | reflection |
| 5 | function/OpenAPI/MCP tools | actions |
| 6 | workflow graph and planner agent | planning |
| 7 | sub-agents, transfer, task mode | collaboration |
| 8 | sessions/state/memory service | continuity |
| 9 | eval-driven updates | adaptation |
| 10 | MCP toolsets | discovery |
| 11 | state/events and loop conditions | monitoring |
| 12 | retry, checkpoint/resume, failures | recovery |
| 13 | interrupts and human input | approval |
| 14 | retrieval/memory/RAG tools | grounding |
| 15 | A2A/task delegation support | communication |
| 16 | model/tool/routing configuration | resources |
| 17 | LLM loops and custom nodes | reasoning |
| 18 | callbacks, plugins, tool policies | safety |
| 19 | events, traces, eval CLI | monitoring |
| 20 | stateful queue/workflow nodes | prioritization |
| 21 | loops, dynamic workflows, specialist agents | discovery |

## Strengths, limits, and selection rule

Choose ADK when graph workflow control, agent delegation, sessions/events, streaming, and Google ecosystem integration are all important. It is more than an LLM wrapper, so its event/session/workflow version boundaries need integration tests. Keep framework-independent state schemas and policy checks portable, and do not assume Gemini optimization means every provider has identical capabilities.

**Sources**: official repository README, workflow descriptions, and API/documentation links, accessed 2026-09-01.
