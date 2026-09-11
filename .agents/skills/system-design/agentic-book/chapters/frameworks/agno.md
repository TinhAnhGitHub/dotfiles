# Agno API and Pattern Map

**Repository**: https://github.com/agno-agi/agno  
**Positioning**: Python framework and runtime for building, serving, and managing agent platforms. The repository separates the SDK from the AgentOS runtime/UI. Confirm imports against the installed release.

## Core model

Agno centers on composable `Agent` objects. Agents can use models, tools, knowledge, memory, storage, structured input/output, reasoning, and streaming. `Team` composes agents around delegation; `Workflow` composes deterministic application steps. AgentOS supplies a service/API/control-plane layer for running agents, storing data/traces, and managing access.

A useful distinction is **agent cognition** versus **platform operations**: keep mission policy, authorization, evaluation, and domain logic explicit even when AgentOS supplies persistence or HTTP serving.

## Important modules, classes, and functions

### Agents and runs

- `Agent` — declares model, instructions, tools, knowledge, memory, response format, reasoning behavior, and runtime options. Use for Ch 1, 4, 5, 8, 11, 14, 17, and 18.
- `Agent.run(...)` / async run variants — execute a task and return a response object; use streaming when the caller needs progress.
- `RunResponse`/run-event types — carry output, tool activity, reasoning, citations, and status depending on configuration. Persist only what is required.
- `Agent.print_response(...)` and stream controls — convenient CLI/demo presentation; separate presentation from production auditing.
- Pydantic response models / structured output configuration — constrain output at a boundary (Ch 1, Ch 5, Ch 19). A valid model is not proof that the content is correct.

### Teams and collaboration

- `Team` — coordinates multiple agents and exposes a team-level task interface (Ch 7).
- Team member/delegation configuration — gives specialists roles, descriptions, and permissions. Delegation should specify ownership and a handoff schema.
- Team modes and routing/selection options — choose whether a coordinator delegates, members collaborate, or results are aggregated. Use sequential delegation for dependencies and parallel work only for independent tasks.
- Team responses/events — preserve member identity and intermediate artifacts so a supervisor can resolve conflicts rather than silently merging them.

### Workflows

- `Workflow` — application-level orchestration for multi-step operations, useful for Ch 1 chaining, Ch 2 routing, Ch 3 parallelization, Ch 6 planning, Ch 11 monitoring, and Ch 12 recovery.
- Workflow step/decorator APIs — define named steps that pass typed data and can call agents or ordinary Python functions. Prefer deterministic code for validation, branching, persistence, and side effects.
- Workflow state and event/result objects — carry progress and outcomes; define explicit stop/failure states.
- Sequential, parallel, and conditional workflow examples — model fan-out/fan-in, routing, and loops without pretending every decision must be an LLM decision.

### Models, tools, and toolkits

- Model provider classes under Agno's model integrations — configure OpenAI-compatible, Gemini, DeepSeek, Anthropic, and other providers where supported. Keep model choice behind a resource policy (Ch 16).
- Callable tools — ordinary Python functions can become agent tools from their names, signatures, docstrings, and type hints. Make functions narrow and side-effect-aware.
- Toolkits — grouped capabilities for search, databases, files, shell, APIs, or domain operations. Expose only the subset needed for a role.
- Tool-call limits, tool-choice controls, confirmation/approval hooks, and error results — use them to constrain actions and implement Ch 5, Ch 12, and Ch 18.
- `ReasoningTools` or comparable reasoning tool integrations — add search/calculation/decomposition capabilities when measured need justifies them; do not equate extra reasoning with correctness.

### Knowledge, memory, and storage

- Knowledge base/knowledge configuration — connects an agent to documents and search, implementing Ch 14 RAG.
- Vector database integrations and search methods — index, retrieve, and optionally rerank evidence. Preserve source metadata and permissions.
- `Memory`/agentic memory options — retain useful user or task facts; keep memory separate from current session state and apply retention/consent rules (Ch 8).
- Storage implementations such as SQLite/Postgres-backed storage — persist sessions, runs, and application state. Scope keys by user/tenant/session.
- Session identifiers, user identifiers, session state, and history controls — maintain continuity while limiting context bloat.

### Guardrails, learning, and operations

- Input/output guardrail hooks and validation functions — reject or transform unsafe content before/after model execution (Ch 18).
- Learning/memory-machine examples — support feedback-driven improvement (Ch 9), but put updates behind regression evaluation and rollback.
- `AgentOS` — runtime/control plane for serving agents, with API endpoints, streaming/WebSockets, storage, traces, authentication/RBAC, MCP support, and UI features described by the project. Treat service configuration as part of the threat model.
- Serving/deployment functions and templates — expose agents as services; add health checks, quotas, authorization, and audit logging rather than assuming the runtime supplies domain safety.
- Evaluation/simulation/cookbook examples — useful starting points for Ch 19, but examples are not acceptance evidence for your application.

## Pattern-by-pattern use

| Book chapter | Agno surface | Purpose |
|---|---|---|
| 1, 2, 3, 6 | `Workflow`, steps, team routing | orchestration |
| 4, 17 | agent reasoning/refinement configuration | quality loops |
| 5 | callable tools/toolkits and tool limits | external actions |
| 7 | `Team`, members, delegation | specialization |
| 8 | memory, session state, storage | continuity |
| 9 | learning/memory examples | adaptation |
| 10 | MCP integrations | discoverable capabilities |
| 11, 19 | run events, traces, evals | monitoring |
| 12 | workflow errors/retries/fallback code | resilience |
| 13 | confirmation/HITL hooks | approval |
| 14 | knowledge/vector search | grounding |
| 15 | team/API/MCP boundaries | agent communication |
| 16 | model and workflow choices | resources |
| 18 | guardrails, RBAC, tool restrictions | safety |
| 20, 21 | workflow queues and teams | prioritization/discovery |

## Strengths, limits, and selection rule

Agno is attractive when you want a single platform vocabulary for agents, teams, workflows, knowledge, memory, storage, and serving. It is less attractive when you need a very small dependency surface or completely framework-neutral orchestration. Keep core contracts portable and test the exact runtime behavior of the selected AgentOS version.

Use **Agno** for an agent platform; use **LangGraph/ADK** when explicit graph control is the primary requirement; use **PydanticAI** when typed Python boundaries dominate. These can be design alternatives, not a reason to mix every abstraction.

**Sources**: official repository README, cookbook structure, and documentation links, accessed 2026-09-01.
