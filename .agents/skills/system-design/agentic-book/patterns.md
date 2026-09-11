# Agentic Pattern Cards

## Prompt Chaining (Pipeline)
**When to use**: A task has distinct dependent stages or exceeds one prompt's reliable capacity.
**How**: Decompose → give each stage one job → pass bounded structured output → validate at every boundary.
**Trade-offs**: More latency and token cost; early errors propagate. Add schemas, checkpoints, and stage-level tests.

## Routing
**When to use**: Intent, risk, capability, or complexity determines the next path.
**How**: Classify → dispatch to a tool, prompt, model, or specialist → retain an unclear/clarification branch.
**Trade-offs**: Misclassification sends work down the wrong path. Rules are fast and rigid; LLM routers are flexible but less deterministic.

## Parallelization
**When to use**: Subtasks are independent and can be merged later.
**How**: Prove independence → fan out with isolated inputs → join → synthesize.
**Trade-offs**: Lower latency but higher concurrency cost and harder tracing. Never parallelize steps with hidden shared state or dependencies.

## Reflection
**When to use**: Quality, correctness, or completeness matters more than minimum latency.
**How**: Producer drafts → critic checks explicit criteria → producer refines → stop at a bounded iteration count.
**Trade-offs**: Extra calls can amplify cost or introduce needless edits. A separate critic improves role separation; use tests or rules where possible.

## Tool Use / Function Calling
**When to use**: The agent needs current/private information or must affect an external system.
**How**: Define narrow typed tools → model proposes a call → validate authorization and arguments → execute → return an observation → continue or stop.
**Trade-offs**: Tool errors, stale results, malformed arguments, and side effects. Separate read from write tools and require approval for irreversible actions.

## Planning
**When to use**: The goal has multiple dependent steps, resources, or constraints.
**How**: Define outcome and stop condition → generate ordered/dependent tasks → execute → monitor observations → replan when assumptions change.
**Trade-offs**: Plans become stale; simple work can be over-planned. Keep plans inspectable and executable.

## Multi-Agent Collaboration
**When to use**: Distinct specialties, contexts, or tools justify role separation.
**How**: Assign ownership → specify handoff contracts → choose sequential, parallel, supervisor, hierarchical, or debate topology → aggregate and resolve conflicts.
**Trade-offs**: Coordination and context-transfer overhead. A single agent is preferable when roles do not have genuinely different responsibilities.

## Memory Management
**When to use**: Work spans turns, sessions, or recurring users/tasks.
**How**: Separate session history, working state, and durable memory → store only useful, consented facts → retrieve selectively → summarize/prune stale state.
**Trade-offs**: Bloat, leakage, stale personalization, and privacy risk. Give every memory item provenance and retention rules.

## Learning and Adaptation
**When to use**: Feedback and repeated experience can improve decisions over time.
**How**: Collect trajectories and outcomes → evaluate → update prompts/policies/memory/model → regression-test → deploy behind rollback.
**Trade-offs**: Drift, reward hacking, and unsafe self-modification. Never let adaptation bypass evaluation or safety controls.

## MCP
**When to use**: A growing, interoperable ecosystem must expose tools, resources, or prompts through discovery.
**How**: MCP server publishes bounded capabilities; client discovers, authorizes, invokes, and records them.
**Trade-offs**: Infrastructure and auth complexity. Plain function calling is simpler for a small fixed tool set.

## Goal Setting and Monitoring
**When to use**: A long-running agent must know whether it is progressing.
**How**: Make goals measurable → define milestones and stop conditions → observe state and outcomes → detect drift → adjust or escalate.
**Trade-offs**: Monitoring costs resources and bad metrics create false confidence. Measure outcomes, not activity alone.

## Exception Handling and Recovery
**When to use**: Always in production or when tools/network/state can fail.
**How**: Detect and classify → retry only transient failures with bounded backoff → fall back/degrade → checkpoint/rollback → notify or escalate.
**Trade-offs**: Recovery logic adds complexity; careless retries create storms and duplicate side effects.

## Human-in-the-Loop
**When to use**: Actions are high-impact, ambiguous, irreversible, regulated, or ethically sensitive.
**How**: Define escalation policy → present concise evidence and proposed action → obtain explicit decision → record the decision and resume safely.
**Trade-offs**: Human latency and bottlenecks. Use risk-based approval, not approval for every harmless step.

## Knowledge Retrieval (RAG)
**When to use**: Answers need current, private, factual, or attributable knowledge.
**How**: Ingest and index → retrieve relevant evidence → augment context → answer with citations/uncertainty → evaluate retrieval and grounding.
**Trade-offs**: Poor chunking, stale indexes, and irrelevant retrieval produce grounded-sounding errors. Agentic or graph retrieval adds flexibility and complexity.

## Inter-Agent Communication (A2A)
**When to use**: Independent agents across systems/frameworks must discover and exchange work.
**How**: Advertise identity/capabilities with an AgentCard → send typed tasks/results → support streaming or input-required states → authenticate and audit.
**Trade-offs**: Protocol and security overhead. Distinguish A2A agent-to-agent work from MCP model/client-to-tool access.

## Resource-Aware Optimization
**When to use**: Cost, latency, throughput, context, or compute are constrained.
**How**: Estimate task complexity → select model/tool depth → prune or summarize context → degrade gracefully → compare quality against budget.
**Trade-offs**: A resource router adds latency and can choose badly. Optimize from measured trajectories, not intuition.

## Reasoning Techniques
**When to use**: A problem needs decomposition, alternatives, deliberation, or tool-grounded action.
**How**: Choose the least expensive sufficient method: structured decomposition, ReAct, self-consistency, tree search, debate, or program-aided reasoning.
**Trade-offs**: More thinking increases cost and can make wrong reasoning more elaborate. Require evidence and final checks.

## Guardrails / Safety
**When to use**: Any system that handles sensitive data, communicates externally, or changes state.
**How**: Layer input validation, output filtering, behavioral constraints, least-privilege tools, moderation, audit logs, and HITL.
**Trade-offs**: False positives and latency. Test both harmful bypasses and legitimate-use breakage.

## Evaluation and Monitoring
**When to use**: Before release and continuously after deployment.
**How**: Test representative tasks and failures → trace trajectories → measure quality, safety, cost, and latency → detect drift → feed fixes into regression tests.
**Trade-offs**: Evaluation has cost and judge bias. Combine deterministic checks, human review, and model judges.

## Prioritization
**When to use**: Several goals compete for limited time, tools, or attention.
**How**: Score urgency, value, dependency, risk, and cost → select → execute → re-score when observations change.
**Trade-offs**: Heuristics can starve low-frequency important work. Preserve fairness, deadlines, and escalation rules.

## Exploration and Discovery
**When to use**: The solution space is unknown and useful novelty matters.
**How**: Generate hypotheses → critique and rank → design experiments → observe → evolve promising directions → stop on budget or evidence.
**Trade-offs**: Expensive, slow, and difficult to evaluate. Bound search and require provenance, safety, and human review before real-world action.
