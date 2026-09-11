# LangGraph API and Pattern Map

**Repository**: https://github.com/langchain-ai/langgraph  
**Positioning**: low-level, stateful orchestration for long-running agents. It can be used without LangChain. Verify imports against the installed LangGraph version; APIs evolve.

## Core model

LangGraph models an application as a stateful graph. A **state schema** is read and updated by **nodes**; **edges** determine what runs next. `START` and `END` delimit execution. A compiled graph exposes `invoke`/`ainvoke` for one result and `stream`/`astream` for incremental events or state updates.

Typical construction:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MyState)
builder.add_node("retrieve", retrieve)
builder.add_node("answer", answer)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "answer")
builder.add_edge("answer", END)
graph = builder.compile(checkpointer=checkpointer)
```

The important boundary is the state contract: nodes should consume and return narrow, serializable updates rather than hidden mutable globals.

## Important modules, classes, and functions

### Graph construction and control flow

- `StateGraph` — builder for graphs whose nodes read/write a typed state. Use it for Ch 1 chaining, Ch 2 routing, Ch 3 fan-out/fan-in, Ch 4 reflection, Ch 6 planning, and Ch 11 monitoring.
- `MessagesState` — convenience state shape for message-based agents; useful for ReAct/chat workflows (Ch 17).
- `START`, `END` — graph boundary sentinels.
- `add_node(name, fn, ...)` — registers a function, runnable, or subgraph as a node.
- `add_edge(source, target)` — expresses a fixed dependency.
- `add_conditional_edges(source, path, mapping)` — routes from a node according to state or a routing function (Ch 2).
- `compile(...)` — freezes graph topology and attaches checkpointer, store, interrupt, cache, and retry configuration. Compilation is where missing edges and invalid graph structure should fail early.
- `invoke`, `ainvoke`, `stream`, `astream` — execute synchronously/asynchronously or consume intermediate updates. Streaming is useful for progress, HITL UIs, and long-running tasks.
- `Command` — lets a node combine a state update with a control decision such as `goto`; useful when the decision and update must be atomic.
- `Send` — dynamically creates a map task with an individual input, useful for parallel work over a variable collection (Ch 3).

### Runtime control and resilience

- `interrupt(...)` — pauses graph execution and returns control to the caller for human input or approval (Ch 13). Resume using the same durable thread/run identity.
- `RetryPolicy` — attaches bounded retry behavior to a node; use only for classified transient failures (Ch 12).
- `CachePolicy` — caches node results where inputs are stable and side effects are absent (Ch 16).
- `get_stream_writer()` — lets nodes emit custom progress events while preserving the graph stream.
- Runtime/context/config parameters — pass request-scoped dependencies, metadata, and configuration without putting them into global state.

### Persistence and memory

- Checkpointers such as `InMemorySaver`, SQLite, and Postgres implementations — persist graph state between steps and resume after interruption/failure. Use a production backend for durable work and isolate `thread_id` per conversation/workflow.
- `InMemoryStore` and store interfaces — long-term namespaced storage separate from the active checkpoint. Use it for selective user/application memory (Ch 8), not for blindly storing every message.
- State inspection/update methods such as `get_state`, `get_state_history`, and `update_state` — inspect, repair, or manually adjust a running thread. Treat these as privileged operations.
- Time-travel/replay capabilities — inspect prior checkpoints and branch from a known state for debugging or what-if evaluation (Ch 19).

### Agent and subgraph patterns

The LangGraph ecosystem includes prebuilt agent helpers (for example, ReAct-style agents) and examples for tool calling, plan-and-execute, reflection, adaptive RAG, multi-agent teams, and human input. Prefer explicit `StateGraph` when a prebuilt helper hides a decision or permission boundary. Subgraphs allow a specialist workflow to be embedded as a node while retaining a local state contract (Ch 7).

## Pattern-by-pattern use

| Book chapter | LangGraph feature | Purpose |
|---|---|---|
| 1 Chaining | fixed edges, sequential nodes | typed pipeline |
| 2 Routing | conditional edges, `Command` | branch by state/intent |
| 3 Parallelization | fan-out edges, `Send`, map/join state | concurrent independent work |
| 4 Reflection | cycles and critic/producer nodes | bounded refinement |
| 5 Tools | tool nodes and message state | execute validated capabilities |
| 6 Planning | plan and execution nodes/subgraphs | visible task graph |
| 7 Collaboration | subgraphs, supervisor/team graphs | specialist ownership |
| 8 Memory | checkpointer + store | short/long-term separation |
| 9 Learning | versioned graph/policy updates | gated adaptation |
| 11 Goals | state metrics and loop edges | progress control |
| 12 Recovery | retry policy, checkpoint resume | fault handling |
| 13 HITL | `interrupt`, state inspection | pause/approve/edit |
| 14 RAG | retriever/tool nodes | grounded evidence |
| 16 Resources | cache, routing, concurrency limits | budget control |
| 17 Reasoning | ReAct, search, debate graph examples | deliberation |
| 18 Safety | permission nodes and interrupt gates | defense in depth |
| 19 Evaluation | streams, traces, replay | trajectory analysis |
| 20 Prioritization | queue state and routing | next-task selection |
| 21 Discovery | hypothesis/experiment subgraphs | bounded exploration |

## Design guidance and trade-offs

Use LangGraph when the workflow's **state transitions** are part of the product contract. Keep model calls, tools, authorization, and evaluation as ordinary functions around the graph rather than hiding them in prompts. Give every persisted state a schema, tenant/thread scope, retention rule, and redaction policy. Checkpoint before side effects and make writes idempotent.

The framework gives control, not correctness. A graph can faithfully execute a bad plan, retrieve bad evidence, or expose an unsafe tool. Add Ch 12 recovery, Ch 18 guardrails, Ch 19 evaluation, and Ch 13 approval explicitly. Graph complexity is a real cost: if a simple chain is sufficient, do not build a state machine.

## Minimal selection rule

- Choose **LangChain** for component/integration composition.
- Choose **LangGraph** when branching, cycles, checkpoints, interruption, or resumability must be explicit.
- Use both when LangChain components supply models/tools/retrievers and LangGraph supplies control flow.

**Sources**: official repository README and examples, accessed 2026-09-01.
