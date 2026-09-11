---
name: book
description: "Agentic design patterns from Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems. Use when decomposing, orchestrating, grounding, safeguarding, evaluating, or optimizing LLM-based agents and multi-agent systems."
---

<!-- argument-hint: [pattern, topic, architecture question, or chapter number] -->

# Agentic Design Patterns

**Source**: *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems*  
**Source size**: ~458 pages, 21 pattern chapters  
**Note**: The extracted PDF does not expose a reliable author name or publication metadata. This skill contains synthesized notes, not reproduced book text.

## How to use this skill

Use this as a design protocol, not as a list of buzzwords:

1. State the mission, success criteria, constraints, risk level, and authority boundary.
2. Classify the system level: reasoning-only, tool-connected, strategic, or collaborative.
3. Choose the smallest pattern composition that solves the problem.
4. Make state, context, tool contracts, failure recovery, safety gates, and evaluation explicit.
5. Prototype the happy path, then test failures, ambiguity, drift, cost, and unauthorized actions.
6. Keep humans as the final authority for consequential decisions unless explicit approval says otherwise.

When asked about a topic, read the matching chapter and `cheatsheet.md`. Read `patterns.md` for a cross-pattern design decision; read `glossary.md` for vocabulary.

## Core agent model

An agent is a goal-oriented system that **perceives**, **reasons**, and **acts** in an environment. Its practical loop is:

**Mission → Scan → Think → Act → Learn**

- **Mission**: define an outcome and boundaries, not merely a vague request.
- **Scan**: gather only relevant user context, state, retrieved knowledge, and observations.
- **Think**: plan, route, prioritize, or reason over the available evidence.
- **Act**: call validated tools or hand work to a defined specialist.
- **Learn**: inspect outcomes, record useful feedback, and adapt only under evaluation and safety controls.

Treat **context engineering** as a first-class discipline: select, package, and refresh the smallest complete context needed for the next decision. A capable model with incomplete or polluted context is still an unreliable system.

## Design ladder

| Level | System | Add when |
|---|---|---|
| 0 | LLM reasoning core | The task needs no current/private data or action. |
| 1 | Connected problem solver | Add tools and/or RAG for external facts and actions. |
| 2 | Strategic problem solver | Add planning, memory, monitoring, reflection, and adaptive context. |
| 3 | Collaborative system | Add specialized agents and explicit communication when one agent is overloaded or has conflicting roles. |

Increase the level only when a lower-level design cannot meet the requirement. Extra autonomy multiplies failure modes.

## Pattern selection and composition

- **Linear dependency** → Prompt Chaining.
- **Conditional choice** → Routing, with an unclear/clarification branch.
- **Independent work** → Parallelization; join only at a declared merge point.
- **Multi-step objective** → Planning, then execute and revise against observations.
- **External data or action** → Tool Use; use MCP when tools/resources must be discoverable and interoperable.
- **Private, changing, or attributable knowledge** → RAG; cite or expose evidence.
- **Cross-turn continuity** → Memory Management; separate session, working state, and durable memory.
- **Quality-sensitive output** → Reflection/Self-Correction.
- **Multiple specialists** → Multi-Agent Collaboration; define ownership and handoff schemas.
- **Cross-system agent calls** → A2A/Inter-Agent Communication; use MCP for agent-to-tool integration.
- **Long-running outcome** → Goal Setting and Monitoring plus Exception Recovery.
- **Cost or latency pressure** → Resource-Aware Optimization and selective model/tool use.
- **High consequence** → Guardrails, HITL, least privilege, auditability, and evaluation are mandatory.
- **Open-ended inquiry** → Exploration and Discovery with explicit budgets and stop conditions.

A robust default composition is:

`Goal + constraints → Plan/Route → Retrieve/Tool-use → Execute (chain or parallel) → Reflect → Safety/approval → Observe/evaluate → update state`

Use only the branches needed. Do not add multi-agent collaboration, long-term memory, or autonomous learning merely because they are available.

## Non-negotiable engineering principles

1. **Structured boundaries**: pass typed, bounded data between steps; reject malformed outputs.
2. **Ground actions**: tools return observations; the model never gets implicit authority from a plausible sentence.
3. **Least privilege**: expose only the tools, data, and write permissions needed for the current task.
4. **Reversible execution**: preview, stage, checkpoint, or request approval before irreversible effects.
5. **Failure is a state**: classify timeout, invalid data, authorization, model, and business failures; retry only transient failures with bounded backoff.
6. **Explicit uncertainty**: route ambiguity to clarification, evidence gathering, fallback, or a human—not confident guessing.
7. **Evaluate trajectories**: measure the sequence of decisions and actions, not only the final prose.
8. **Adapt behind a gate**: learning, prompt changes, routing changes, and self-modification require regression evaluation and rollback.

## Architecture checklist

Before implementation, answer:

- What is the mission, measurable success condition, and stop condition?
- What context is authoritative, stale, sensitive, or missing?
- Which steps are sequential, conditional, independent, or iterative?
- Which tools can read, write, spend, communicate, or change state?
- What schema crosses every boundary?
- What happens on bad retrieval, tool failure, conflicting evidence, or model uncertainty?
- Which actions require confirmation or human ownership?
- What metrics, traces, test cases, and rollback path prove this works?

## Chapter index

| # | Chapter | Design focus |
|---|---|---|
| [ch01](chapters/ch01-prompt-chaining.md) | Prompt Chaining | Linear decomposition and typed handoffs |
| [ch02](chapters/ch02-routing.md) | Routing | Conditional dispatch and fallback |
| [ch03](chapters/ch03-parallelization.md) | Parallelization | Independent work and merge points |
| [ch04](chapters/ch04-reflection.md) | Reflection | Critique, refinement, and quality loops |
| [ch05](chapters/ch05-tool-use.md) | Tool Use (Function Calling) | Validated external actions |
| [ch06](chapters/ch06-planning.md) | Planning | Executable plans and replanning |
| [ch07](chapters/ch07-multi-agent-collaboration.md) | Multi-Agent Collaboration | Specialist roles and coordination |
| [ch08](chapters/ch08-memory-management.md) | Memory Management | Session, state, and durable memory |
| [ch09](chapters/ch09-learning-and-adaptation.md) | Learning and Adaptation | Feedback-driven improvement |
| [ch10](chapters/ch10-model-context-protocol.md) | Model Context Protocol | Discoverable tools, resources, prompts |
| [ch11](chapters/ch11-goal-setting-and-monitoring.md) | Goal Setting and Monitoring | Metrics, progress, and drift |
| [ch12](chapters/ch12-exception-handling-and-recovery.md) | Exception Handling and Recovery | Resilience and rollback |
| [ch13](chapters/ch13-human-in-the-loop.md) | Human-in-the-Loop | Approval and escalation |
| [ch14](chapters/ch14-knowledge-retrieval-rag.md) | Knowledge Retrieval (RAG) | Grounded answers and evidence |
| [ch15](chapters/ch15-inter-agent-communication.md) | Inter-Agent Communication | A2A discovery and task exchange |
| [ch16](chapters/ch16-resource-aware.md) | Resource-Aware Optimization | Quality, cost, and latency |
| [ch17](chapters/ch17-reasoning-techniques.md) | Reasoning Techniques | Deliberation and action loops |
| [ch18](chapters/ch18-guardrails-safety.md) | Guardrails/Safety Patterns | Defense in depth |
| [ch19](chapters/ch19-evaluation-and-monitoring.md) | Evaluation and Monitoring | Quality, trajectory, and drift |
| [ch20](chapters/ch20-prioritization.md) | Prioritization | Value-aware scheduling |
| [ch21](chapters/ch21-exploration-and-discovery.md) | Exploration and Discovery | Hypotheses and unknowns |
| [ch22](chapters/ch22-appendices.md) | Appendices | Prompting, frameworks, coding-agent practice |
| [ch23](chapters/ch23-open-source-frameworks.md) | Open-Source Frameworks | Repository map and selection guidance |

## Supporting files

- [patterns.md](patterns.md) — pattern cards and trade-offs
- [cheatsheet.md](cheatsheet.md) — selection tree and design defaults
- [glossary.md](glossary.md) — vocabulary
- [ch22](chapters/ch22-appendices.md) — prompting, frameworks, and coding-agent practices
- [ch23](chapters/ch23-open-source-frameworks.md) — open-source framework and repository comparison
- [frameworks/](chapters/frameworks/) — detailed API, feature, class/function, and pattern mappings for each repository

## Scope and limits

These are synthesized design notes from the supplied PDF. Framework APIs, protocol details, model capabilities, and safety guidance change quickly; verify current documentation before implementation. Examples are conceptual unless independently tested. Never use this skill as a substitute for security review, domain compliance, or human approval in high-stakes workflows.
