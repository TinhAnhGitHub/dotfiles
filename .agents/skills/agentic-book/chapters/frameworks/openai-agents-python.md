# OpenAI Agents SDK API and Pattern Map

**Repository**: https://github.com/openai/openai-agents-python  
**Positioning**: lightweight Python framework for multi-agent workflows with a small core: agents, a runner, tools, handoffs, guardrails, sessions, and tracing. It also provides sandbox, realtime, and voice surfaces. Verify names against the installed release.

## Core model

An `Agent` packages instructions, model configuration, tools, guardrails, handoffs, and optional output schema. `Runner` drives the loop: model response → tool/handoff → observation/result → next step. The SDK distinguishes **handoffs** (the next agent owns the conversation) from **agents as tools** (the caller retains ownership and asks a specialist for a bounded result).

## Important modules, classes, and functions

### Agents and runner

- `Agent` — declares name, instructions, model, tools, `output_type`, input/output guardrails, and handoffs. Use for Ch 1, 5, 7, 13, 17, and 18.
- `Runner.run(...)` / `Runner.run_sync(...)` — execute asynchronously or synchronously and return a result with final output, usage, messages, and run metadata.
- `Runner.run_streamed(...)` — expose incremental events for UI/progress while the run continues. Do not treat an unfinished stream as a committed side effect.
- Run configuration/result types — pass model provider, tracing, max turns, session, and workflow options. Bound turns and usage explicitly.
- `RunContextWrapper`/context objects — carry application dependencies and request-scoped data to tools and guardrails; do not use them as an authorization substitute.

### Tools and delegation

- `@function_tool` — turns a Python function into a typed function tool, generally deriving schema from annotations/docstrings (Ch 5).
- Function, hosted, and MCP tools — expose local functions, provider-hosted capabilities, or MCP servers. Validate permissions and arguments outside model text.
- `Agent.as_tool(...)` — wraps a specialist as a callable tool while the parent remains the owner (Ch 7).
- `handoffs=[...]` — lets a parent transfer control to a specialist. Configure handoff descriptions, input filters, and ownership deliberately.
- Tool error/result handling — return structured observations and classify failures for Ch 12 recovery; use idempotency for writes.

### Guardrails and human control

- `InputGuardrail` and `OutputGuardrail` (and corresponding decorator/helpers) — run validation before or after agent output. Use multiple layers and deterministic checks where possible (Ch 18).
- Human-in-the-loop patterns — pause in application code or use approval tools/gates before consequential actions (Ch 13). The SDK does not make a model's proposed action authoritative.
- Tool allowlists, context filters, and approval functions — constrain the capability surface and redact data crossing agent boundaries.

### Sessions, tracing, and observability

- Session interfaces and implementations such as `SQLiteSession`, SQLAlchemy-backed sessions, encrypted/session variants, and conversation stores where supported — persist history across runs (Ch 8). Set user/tenant scope and retention explicitly.
- `trace(...)`, `custom_span(...)`, and tracing processors — record agent runs, model calls, tool calls, handoffs, guardrails, and timing for Ch 19. Configure redaction because traces may contain secrets or personal data.
- Result/message/history APIs — inspect the trajectory and preserve the minimum replay/debug data needed for compliance.
- Usage limits and model/provider configuration — enforce budgets and swap providers/models for Ch 16; test provider-specific tool/schema behavior.

### MCP, sandbox, realtime, and voice

- MCP server clients such as stdio and streamable-HTTP server adapters — connect discoverable tools/resources (Ch 10). Pin server identity, auth, and tool allowlists.
- `SandboxAgent`, sandbox run configuration, manifests, and sandbox clients — give an agent an isolated workspace for long-running coding tasks. Treat filesystem, shell, network, and repository access as separate permissions.
- `RealtimeAgent`/`RealtimeRunner` — support low-latency voice/multimodal sessions; preserve the same guardrail and tool boundaries.
- Voice pipeline agents/runners — compose speech-to-text, agent execution, and text-to-speech; latency does not justify skipping approval or audit.

## Pattern-by-pattern use

| Book chapter | SDK surface | Purpose |
|---|---|---|
| 1 | agent turns, typed output, tools | sequential loop |
| 2 | handoff/tool routing | conditional dispatch |
| 3 | parallel application tasks/agents | independent work |
| 4 | critic agent or guardrail/refinement loop | reflection |
| 5 | `@function_tool`, MCP, hosted tools | external action |
| 6 | structured planner agent + runner | planning |
| 7 | `Agent.as_tool`, handoffs | collaboration |
| 8 | sessions/history | continuity |
| 9 | traces/evals and versioned instructions | adaptation |
| 10 | MCP server adapters | discovery |
| 11 | max turns, results, usage, application monitors | goals |
| 12 | tool errors, bounded turns, application retries | recovery |
| 13 | approval gates and human input | HITL |
| 14 | retrieval as tool/hosted capability | RAG |
| 15 | remote agent/tool boundary | communication |
| 16 | model/provider/usage settings | resources |
| 17 | tool loop and specialist debate | reasoning |
| 18 | input/output guardrails, sandbox, allowlists | safety |
| 19 | tracing and result history | evaluation |
| 20 | application task queue/priority tool | prioritization |
| 21 | bounded specialist exploration | discovery |

## Strengths, limits, and selection rule

Choose the OpenAI Agents SDK for a compact, readable agent loop with first-class delegation, guardrails, sessions, tracing, MCP, and optional workspace/voice capabilities. It is a good fit when application code can own topology and persistence. For complex graph-native branching, durable state transitions, or elaborate checkpoint/replay semantics, add an explicit orchestration layer or choose a graph framework.

The SDK is provider-agnostic at the interface level, but provider capabilities and tool semantics still differ. Test the actual model/provider combination, cap turns and tool calls, and keep side-effect authorization outside the agent's instructions.

**Sources**: official repository README, documentation index, and examples references, accessed 2026-09-01.
