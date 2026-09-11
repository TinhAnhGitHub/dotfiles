# Appendices A–G: Prompting, Interactions, Frameworks, and Agents

## Appendix A — Advanced Prompting Techniques

**Core idea.** A prompt is a specification you iterate against measured evidence, not a one-shot incantation. Write clear task statements, concrete action verbs, concise context, and explicit output schemas; add examples only when they disambiguate behavior. Choose the cheapest method that meets a measured quality target, and validate against a small evaluation set rather than a single lucky run.

**Frameworks/techniques introduced.** Zero-/one-/few-shot prompting, role/persona framing, step-back abstraction (ask the model to reason about principles before the case), self-consistency (sample multiple paths and take the majority answer), tree/graph search over candidate steps, structured debate between agents, program-aided reasoning (offload arithmetic/bookkeeping to code), and structured output (schema-enforced).

**Implementation sketch.**

```
best = None
for _ in range(N):                      # self-consistency
    answer = llm(task, few_shots, schema)
    best = majority(best, answer)       # aggregate votes
if not valid(best, schema): reject()    # guard the boundary
```

For program-aided reasoning, route calculations to code rather than asking the model to compute: define the formula in Python, let the model fill parameters, then execute and feed the result back. For structured output, pair the schema with a validation pass that rejects malformed rows instead of trusting free-form prose.

**Worked example.** Extracting records: give a JSON schema and one valid example, then a validation layer rejects malformed rows instead of trusting free-form prose. For a reasoning task, first prompt the model to state the governing principles (step-back), then apply them to the specific case, and run several samples to confirm the answer is stable.

## Appendix B — AI Agentic Interactions

**Core idea.** Agents are moving from text-in/text-out to agents that perceive and act in GUIs and the physical world. The Agent-Computer Interface (ACI) lets an agent use the visual "front door" of software instead of rigid API scripts.

**Concepts.** The ACI loop has four stages: (1) **visual perception** — screenshot the screen; (2) **GUI element recognition** — segment the image into interactive components (button vs. banner vs. field); (3) **contextual interpretation** — the LLM reasons about what each element means for the task; (4) **dynamic action and response** — drive mouse/keyboard and watch for feedback, loading, and errors. Projects illustrate the spectrum: ChatGPT Operator and Google Project Mariner (browser/task automation), Anthropic Computer Use (cross-app desktop orchestration), Browser Use (DOM-level control), and embodied efforts like Project Astra and low-latency multimodal chat (Gemini Live, GPT-4o). **Vibe coding** is the companion creative mode: state a high-level "vibe," iterate in natural language, focus on *what* not *how*, and use optional memory banks to keep style consistent across sessions.

## Appendix C — Framework Overview

**Core idea.** Frameworks are interchangeable *canvases* for the same agentic patterns; keep your domain logic, contracts, and evaluation framework-agnostic so the architecture can move canvases.

**Frameworks introduced.**

- **LangChain / LCEL** — composable, linear dataflow (`prompt | model | parse`); good for DAGs like simple RAG, summarization, extraction.
- **LangGraph** — stateful graph of nodes and conditional edges; cycles, retries, checkpoints, human pauses; fine-grained control.
- **CrewAI** — role/goal/backstory "agents" + tasks + a Crew running a sequential or hierarchical process; designs a team charter rather than a state machine.
- **Google ADK** — opinionated, production-oriented "team" patterns (Sequential/Parallel agents), implicit session/state management.
- Others map to niches: AutoGen (conversation-driven orchestration), LlamaIndex (data/RAG pipelines), Haystack (retrieval pipelines), MetaGPT (SOP-driven roles), Strands (lightweight MCP-enabled SDK).

**Mental model.** LangChain gives building blocks, LangGraph gives the wiring diagram, CrewAI/ADK give a factory assembly line for teams. Pick the level of abstraction your task demands.

**Worked example.** A single-agent RAG pipeline fits an LCEL chain; the same feature needing human approval before a write becomes a LangGraph node with a conditional edge and a checkpoint; a three-specialist research-and-write effort maps naturally onto a CrewAI Crew of Agents and Tasks—same pattern, three canvases.

## Appendix D — AgentSpace

**Core idea.** An enterprise platform for an "agent-driven enterprise": unified search over documents/email/databases, an enterprise knowledge graph, and a no-code **Agent Designer**. Specialized agents reason, plan, and execute multi-step actions; multiple agents collaborate over the open **A2A (Agent2Agent) Protocol**; security rests on role-based access and encryption. The trade-off is convenience and integration depth in exchange for platform lock-in and less granular control.

## Appendix E — AI Agents on the CLI

**Core idea.** The shell is becoming a collaborative workspace: agents that understand natural language, hold context over your whole codebase, and execute multi-step dev tasks.

**Tools.** **Claude Code** builds a holistic mental model of a repo for large refactors; scope is bounded by the user through **MCP**-defined tools. **Gemini CLI** is open-source with a large context window, multimodal input, and a "Reason and Act" loop. **Aider** is git-native, editing files in a read-modify-write loop with commit discipline. **GitHub Copilot CLI** leans on repo embeddings (CodeRover) for edits and scripts. **Terminal-Bench** provides the benchmark suite measuring these capabilities. The recurring theme: the human sets scope and reviews; the agent is a reasoning engine augmented by user-defined tooling.

## Appendix F — Under the Hood: Context Building

**Core idea.** Every call is a prompt assembled from system message, conversation history, tools, retrieved documents, and state. **Context is the real product**; you are a context engineer.

**Mental models.** The context window is a **limited desk**: prioritize the most relevant, recent, and authoritative material. **Recency and prominence bias** mean the top and bottom of the prompt weigh heavily, so order deliberately. **Lost in the middle** means mid-prompt details get dropped, so keep critical instructions at the ends. Manage cost/latency/quality through retrieval, compression, summarization, and selective inclusion.

## Appendix G — Coding Agents

**Core idea.** The human is orchestrator, architect, and final quality gate; agent output is a *proposal*, never authority. Code prompting spans writing, explaining, translating, and debugging-by-reviewing.

**Practice.** Stage a complete, task-specific context (brief, relevant code/docs, constraints, tests, acceptance criteria); version prompts as code; assign specialist roles (implement, test, document, optimize, review); and use iterative dialogue to correct imperfect work. Before accepting a change, inspect the diff, run tests, review security/permissions, and confirm the change satisfies the original mission. Debugging is most effective when the agent explains the failure hypothesis, proposes a minimal fix, and the human re-runs tests rather than accepting a blind edit.

## Cross-Appendix Synthesis

**Key concepts (16).** Few-shot scaffolding · role framing · step-back abstraction · self-consistency · tree search · program-aided reasoning · structured output schemas · ACI perception-action loop · multimodality · framework-as-canvas · knowledge graph grounding · A2A inter-agent protocol · MCP tool scoping · context window as limited desk · recency/prominence bias · lost-in-the-middle · vibe coding · diff-as-review-gate.

**Mental models.** (1) Prompt = spec tested against data. (2) Frameworks = canvases, patterns = painting. (3) Agent = proposal-maker, human = approver. (4) Context = finite workspace to be engineered. (5) Interface ladder: API → GUI/DOM → embodied perception.

**Anti-patterns / failure modes.** Copying prompts from a single lucky run; letting free-form prose become an implicit contract; over-interpreting framework code samples as universal APIs; over-relying on a model's internal knowledge instead of retrieved ground truth; runaway agent loops; trusting agent edits without diff, test, and security review; vague "vibe" prompts with no acceptance criteria.

**Connects to.** Appendix A's prompting techniques feed every later section; context engineering (F) is what makes retrieval (B/RAG), frameworks (C), and coding agents (G) effective; ACI and vibe coding (B) define how humans delegate to agents; the human-as-orchestrator stance (G) underpins the safety discussion elsewhere. Always verify protocols, model capabilities, and framework APIs against current documentation before implementing.
