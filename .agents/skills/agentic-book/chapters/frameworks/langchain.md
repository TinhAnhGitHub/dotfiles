# LangChain API and Pattern Map

**Repository**: https://github.com/langchain-ai/langchain  
**Positioning**: component and integration framework for LLM applications and agents. LangGraph is the associated lower-level orchestration layer; LangSmith is the related observability/evaluation/deployment ecosystem. Verify imports against the installed release.

## Core model

LangChain supplies interoperable building blocks: chat models, messages, prompts, tools, embeddings, documents, retrievers, vector stores, output parsers, and agents. The Runnable interface provides a common composition and execution surface. Use LangChain for the components and LangGraph when the application's control flow needs explicit state, cycles, checkpoints, or interrupts.

## Important modules, classes, and functions

### Models and prompts

- `init_chat_model(...)` — provider-independent model initialization; supports swapping providers during experiments. Map to Ch 16 resource-aware routing and Ch 19 evaluation.
- Chat model interfaces and message types (`HumanMessage`, `AIMessage`, `ToolMessage`, system messages) — represent conversation and tool observations. Keep system policy distinct from untrusted retrieved content (Ch 8, Ch 18).
- `ChatPromptTemplate` and message prompt templates — construct repeatable prompts from typed variables, examples, and retrieved context (Ch 1, Appendix A).
- Model methods such as `invoke`, `ainvoke`, `stream`, and `batch` — run one request, async request, stream events, or batch work. Batch/parallel execution must still respect rate limits and independence.
- `with_structured_output(...)` — ask a model for a schema-constrained result; validate it and handle refusal/parse failures as explicit states (Ch 1, Ch 5, Ch 12).

### Runnable composition and control

- `Runnable` — common protocol for components that accept input and produce output.
- `RunnableSequence` / pipe operator `|` — build linear dataflow pipelines (Ch 1).
- `RunnableParallel` — run independent branches and return keyed results (Ch 3); cap concurrency and validate merge inputs.
- `RunnableBranch` — select a branch from a predicate or router (Ch 2); retain an unknown/clarification path.
- `RunnableLambda` — insert ordinary Python logic for transformation, validation, and deterministic policy.
- `RunnableConfig` and config metadata — carry tags, run IDs, callbacks, concurrency settings, and request metadata for tracing without polluting business data.
- `with_retry`, `with_fallbacks`, and configurable alternatives where available — implement bounded resilience and model fallbacks (Ch 12/16). Never retry non-idempotent writes blindly.

### Tools and agents

- `@tool` decorator — turns a typed Python function into a callable tool with a name, description, and argument schema (Ch 5).
- `BaseTool` / `StructuredTool` — customize tool schemas, async execution, error behavior, and runtime context. Authorization and side-effect controls belong in the implementation, not the description.
- Tool-calling model bindings — let the model propose calls; the executor validates and invokes them, then adds a tool result message.
- Agent constructors/factories in current LangChain releases — provide a ready loop for model → tool call → observation. Prefer explicit graph control when you need durable state, approval, or custom recovery.
- Agent middleware/hooks and callbacks — add logging, policy checks, retries, or transformations at lifecycle points; test ordering carefully.

### Retrieval and knowledge

- `Document` — content plus metadata used throughout ingestion and retrieval (Ch 14).
- `Embeddings` interface — maps text to vectors for semantic search; use provider-specific implementations behind a stable interface.
- `VectorStore` — index and similarity-search abstraction; methods commonly include adding documents and retrieving candidates.
- `Retriever` / `as_retriever(...)` — exposes a standard retrieval interface and supports search configuration such as top-k/filtering.
- Text splitters/document loaders — prepare corpus chunks and metadata. Poor chunking or missing provenance undermines RAG.
- Retrieval chains/compositions — connect query rewriting, retrieval, reranking, augmentation, and answer generation. Add citation/entailment checks rather than treating retrieval as truth.

### Memory, observability, and integration

- Message history/session abstractions and configurable stores — support short-term context, but durable memory and retention policy need an explicit backend and scope (Ch 8).
- Callback/event interfaces — observe model calls, tool calls, retriever behavior, errors, and token usage; use for Ch 19 trajectories.
- Provider integrations — model, embedding, vector database, tool, and loader packages reduce integration work but add dependency/version surface. Pin and test integrations.
- LangSmith integration — tracing, evaluation, debugging, and deployment features around LangChain/LangGraph. Treat telemetry as potentially sensitive and configure redaction.

## Pattern-by-pattern use

| Book chapter | LangChain surface | Purpose |
|---|---|---|
| 1 | prompts, Runnables, pipe | sequential composition |
| 2 | `RunnableBranch`, routers | conditional dispatch |
| 3 | `RunnableParallel`, batch/async | independent work |
| 4 | evaluator/critic chains | reflection |
| 5 | `@tool`, `StructuredTool`, tool messages | function calling |
| 6 | structured plan chains; use LangGraph for execution | planning |
| 7 | agent delegation; use LangGraph for topology | collaboration |
| 8 | history/store integrations | memory |
| 9 | datasets/evals and prompt/model variants | adaptation |
| 10 | MCP integrations where configured | capability discovery |
| 11 | callbacks and stateful orchestration | goal monitoring |
| 12 | retries/fallbacks/callback errors | recovery |
| 13 | application approval callbacks or LangGraph interrupts | HITL |
| 14 | `Document`, embeddings, retrievers, vector stores | RAG |
| 15 | remote tools/agent integrations | communication |
| 16 | configurable models, batching, concurrency | resources |
| 17 | tool loops and agent reasoning | deliberation |
| 18 | middleware, tool policy, input/output checks | safety |
| 19 | callbacks, LangSmith traces/evals | monitoring |
| 20 | deterministic Runnable ranking logic | prioritization |
| 21 | chains plus graph/search orchestration | discovery |

## Strengths, limits, and selection rule

LangChain is a strong first choice when the problem is model/provider integration, retrieval, tool composition, and fast experimentation. It is not a substitute for explicit authorization, durable execution, or a carefully designed state machine. If the agent needs branching, loops, persistence, interruption, or replay, use LangGraph around LangChain components.

Do not let a high-level agent factory hide the book's boundaries: typed inputs/outputs, retrieval provenance, tool permissions, failure classification, approval, and trajectory evaluation must remain inspectable.

**Sources**: official repository README, core package structure, and linked documentation, accessed 2026-09-01.
