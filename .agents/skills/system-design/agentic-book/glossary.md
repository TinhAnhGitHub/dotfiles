# Glossary

**A2A (Agent-to-Agent)** — A protocol boundary for discovering and exchanging tasks/results between independent agents (Ch 15).

**ADK (Agent Development Kit)** — Google's modular agent and graph-workflow framework with agents, runners, tools, sessions, memory, delegation, and workflow nodes (Ch 23).

**Agno** — An agent framework and AgentOS runtime organized around agents, teams, workflows, tools, knowledge, memory, storage, and serving (Ch 23).

**AgentCard** — A discoverable description of an agent's identity, capabilities, and interaction surface (Ch 15).

**Agentic system** — A goal-oriented system that perceives an environment, reasons over context, and takes actions with some autonomy (Introduction).

**Chain of Thought (CoT)** — A reasoning prompt or method that decomposes a problem into intermediate steps; use cautiously and prefer concise structured reasoning when possible (Ch 17).

**Context engineering** — Selecting, packaging, and refreshing the most relevant information for the next model decision (Introduction, Appendix A).

**Context window** — The bounded token capacity available to model input and output at one time (Glossary).

**DeepSeek Harness (`dsh`)** — A plugin-oriented agent harness from DeepSeek AI; the repository currently labels itself developer preview (Ch 23).

**Exception recovery** — Detecting, classifying, handling, and recovering from failures through retry, fallback, rollback, or escalation (Ch 12).

**Function calling / tool use** — A structured model-to-function interaction in which an orchestration layer validates and executes an external capability (Ch 5).

**Goal monitoring** — Comparing observed progress with explicit success metrics and adjusting or escalating when drift appears (Ch 11).

**Guardrail** — A control that constrains inputs, outputs, behavior, tools, or approvals to reduce unsafe or misaligned outcomes (Ch 18).

**Grounding** — Connecting output to verifiable external information to reduce unsupported claims (Introduction, Ch 14).

**Human-in-the-loop (HITL)** — Human review, approval, intervention, or feedback embedded at defined decision points (Ch 13).

**MCP (Model Context Protocol)** — A client-server protocol for discovering and invoking tools, resources, and prompts (Ch 10).

**OpenAI Agents SDK** — A compact Python agent framework centered on agents, runners, tools, handoffs, guardrails, sessions, and tracing (Ch 23).

**Memory** — Retained context, divided operationally into session history, working state, and durable searchable knowledge (Ch 8).

**LangChain** — A component and integration framework for models, tools, retrievers, vector stores, and agents (Ch 23).

**LangGraph** — A low-level graph orchestration framework for stateful, durable agent workflows (Ch 23).

**llmlite** — A Zig-based LLM SDK, OpenAI-compatible edge router, CLI, and MCP server; complementary infrastructure rather than a full agent orchestrator (Ch 23).

**Parallelization** — Concurrent execution of independent subtasks followed by a merge (Ch 3).

**Planning** — Turning a high-level goal into an executable sequence or dependency graph that can be revised from observations (Ch 6).

**Prompt chaining / Pipeline** — Sequential prompts or processing stages where each output informs the next (Ch 1).

**PydanticAI** — A typed Python agent SDK with validated structured output, typed dependencies, function tools, and provider flexibility (Ch 23).

**RAG (Retrieval-Augmented Generation)** — Retrieving relevant external evidence and adding it to model context before generation (Ch 14).

**ReAct** — A reason–act–observe loop that uses tool observations to inform the next reasoning step (Ch 17).

**Reflection** — Generate–critique–refine iteration against explicit quality criteria (Ch 4).

**Resource-aware optimization** — Choosing model, context, tools, and concurrency according to quality, cost, latency, or compute budgets (Ch 16).

**Routing** — Conditional selection of a downstream path, model, tool, or specialist (Ch 2).

**Self-consistency** — Sampling or comparing multiple reasoning paths and selecting a consistent result (Ch 17).

**Structured output** — A bounded schema such as JSON used to make model-to-model or model-to-tool handoffs verifiable (Ch 1, Appendix A).

**Trajectory** — The recorded sequence of prompts, decisions, tool calls, observations, and outcomes that produced an answer (Ch 19).

**Tree of Thoughts (ToT)** — Search over multiple reasoning branches with evaluation and possible backtracking (Ch 17).
