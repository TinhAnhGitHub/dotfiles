# Agentic Design Cheatsheet

## Select the smallest sufficient pattern

| If the task... | Start with... | Add when needed |
|---|---|---|
| Has dependent stages | Chaining | schemas, checkpoints |
| Has conditional paths | Routing | clarification fallback |
| Has independent work | Parallelization | bounded concurrency, merge validation |
| Needs current/private facts | Tool Use or RAG | MCP when integrations proliferate |
| Needs multiple turns | Memory | selective retrieval and retention |
| Has a long objective | Planning + Goal Monitoring | replanning and escalation |
| Needs better quality | Reflection | deterministic tests first |
| Exceeds one role/context | Multi-Agent Collaboration | explicit handoff contracts |
| Crosses agent products | A2A | auth, streaming, task states |
| Is cost/latency constrained | Resource-Aware | measured quality tiers |
| Is high-impact | Guardrails + HITL | rollback and audit |
| Is open-ended | Exploration | budgets, experiments, stop rules |

## Default design sequence

1. Define **mission, success metric, authority boundary, and stop condition**.
2. Gather authoritative context; mark missing, stale, sensitive, and untrusted inputs.
3. Choose topology: chain for dependency, route for choice, fan-out for independence, loop for refinement.
4. Define typed contracts for prompts, tools, state, handoffs, and final output.
5. Start read-only; add write access only with least privilege and approval.
6. Add bounded retries, checkpoints, observability, and a human escalation path.
7. Test normal, ambiguous, adversarial, stale-data, timeout, and partial-failure cases.

## Fast decision rules

- **Ambiguous request?** Ask a clarifying question; do not route by guess.
- **Irreversible side effect?** Preview or stage it and obtain explicit approval.
- **Tool result conflicts with memory?** Prefer the current authoritative source and record the conflict.
- **Independent subtask?** Parallelize only if it has no hidden dependency or shared mutable state.
- **Repeated failure?** Stop retrying, classify the cause, then fall back or escalate.
- **Context too large?** Retrieve, summarize, or prune; never blindly append everything.
- **Pattern adds more coordination than value?** Remove it.
- **Adaptation changes behavior?** Gate it with evaluation, versioning, and rollback.

## Risk-to-control matrix

| Risk | Minimum control |
|---|---|
| Wrong facts | RAG/tool grounding, citations, uncertainty |
| Wrong action | typed args, authorization, preview, HITL |
| Tool/network failure | timeout, bounded backoff, idempotency, fallback |
| Prompt injection | input isolation, tool allowlist, output checks |
| Memory leakage | scoped storage, retention, redaction, provenance |
| Goal drift | milestones, monitoring, stop/escalation rules |
| Cost runaway | budgets, quotas, complexity routing |
| Quality drift | trajectory traces, regression set, alerts |

## Composition recipe

`Mission → Route/Plan → Retrieve → Chain or Parallelize → Tool action → Reflect → Approve → Commit → Evaluate → Persist useful state`

Skip any stage that has no requirement behind it. Safety, observability, and failure handling are cross-cutting, not optional final polish.
