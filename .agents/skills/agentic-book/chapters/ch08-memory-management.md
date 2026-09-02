# Chapter 8: Memory Management

## Core Idea
Intelligent agents need to retain and use information from past interactions, just as humans do. Memory is the agent's ability to remember prior conversations, observations, and learning so it can make informed decisions, keep conversational context, and improve over time. The core problem is managing two very different needs at once: the immediate, temporary information of a single conversation, and the vast, persistent knowledge gathered across many interactions. The standard solution is a **dual-component memory system** that separates short-term (contextual) memory from long-term (persistent) memory, then retrieves only what the next step needs.

## Frameworks Introduced
- **Google ADK** structures memory around three components—**Session** (a chat thread and its events), **State** (`session.state`, a key-value scratchpad), and **Memory** (a searchable long-term repository)—backed by two services: **SessionService** (session lifecycle) and **MemoryService** (long-term add/retrieve).
- **LangChain / LangGraph** manage short-term memory as thread-scoped state persisted by a *checkpointer*, and long-term memory as JSON documents saved in custom *namespaces* via a *store*, recalling them across threads.
- **Vertex Memory Bank** is a managed service that uses Gemini to asynchronously extract facts and preferences from conversation history, store them by scope (e.g. user ID), resolve contradictions, and recall them via full-data or similarity search—integrating with ADK, LangGraph, and CrewAI.

## Key Concepts
1. **Short-Term Memory (Contextual):** Working memory held in the LLM's context window—recent messages, agent replies, tool results, reflections. Limited capacity; ephemeral; lost when the session ends. Long-context windows enlarge it but don't create persistence.
2. **Long-Term Memory (Persistent):** External repository (databases, knowledge graphs, vector stores) for info needed across interactions. Stored outside the processing environment.
3. **Semantic Search:** Converting information into numerical vectors so retrieval matches by meaning, not exact keywords.
4. **Session:** A unique chat thread logging messages/actions (Events) and storing temporary State.
5. **State (`session.state`):** A mutable dictionary of key-value pairs (strings, numbers, booleans, lists, dicts) tracking user preferences, task progress, and flags for the active thread.
6. **MemoryService:** Interface with two core operations—`add_session_to_memory` (extract content from a session into long-term store) and `search_memory` (query the store for relevant data).
7. **State key prefixes:** `user:` (scoped to a user across sessions), `app:` (shared across all users), `temp:` (valid only for the current turn, not persisted). Keys without a prefix are session-specific.
8. **State update paths:** `output_key` on an `LlmAgent` (simplest, for text replies) and `EventActions.state_delta` (for complex, multi-key, prefixed, or non-text updates appended via `append_event`).
9. **Checkpointer (LangGraph):** Persists agent state so a thread can be resumed at any time.
10. **Store / Namespace (LangGraph):** Hierarchical JSON storage—namespace like a folder, key like a filename—supporting `put`, `get`, and similarity `search`.
11. **Three long-term memory types:** *Semantic* (facts/preferences), *Episodic* (past experiences, often via few-shot examples), and *Procedural* (rules/instructions, updated via self-*Reflection*).
12. **Persistence options:** In-memory services (testing only, lost on restart) vs. database (SQLite/PostgreSQL) and cloud (Vertex AI) services for production.

## Mental Models
- **Memory is a two-lane system:** the fast, tiny, disposable context lane (session/state) and the slow, durable, searchable knowledge lane (memory store). Design for each lane's capacity and lifespan separately.
- **State is working memory, not a database:** mutate it in place only for reading; persist changes through the event pipeline.
- **Scope everything:** every memory item carries a scope (who owns it), a lifespan (how long it lives), and a retrieval path.
- **Reflection is procedural learning:** an agent can rewrite its own instructions from past interactions to improve over time.

## Anti-patterns / Failure Modes
- **Directly mutating `session.state` after retrieval:** bypasses event processing, is not recorded in history, may not persist, causes concurrency issues, and skips timestamp updates. Always update via `output_key` or `state_delta` on `append_event`.
- **Confusing in-memory with persistent storage:** assuming test services survive restarts.
- **Context bloat:** letting full history overflow the context window, degrading performance and raising cost.
- **Unscoped memory:** leaking data between users, tasks, or tenants by ignoring `user:`/`app:` prefixes.
- **No consolidation:** storing every turn verbatim instead of extracting, deduplicating, and resolving contradictions (which Memory Bank automates).

## Implementation Sketch
Pseudocode for a reflection-based procedural-memory update in LangGraph (not copied source):

```python
def update_instructions(state: State, store: BaseStore):
    namespace = ("instructions",)
    current = store.search(namespace)[0]
    prompt = prompt_template.format(
        instructions=current.value["instructions"],
        conversation=state["messages"],
    )
    new_instructions = llm.invoke(prompt)["new_instructions"]
    store.put(("agent_instructions",), "agent_a",
              {"instructions": new_instructions})

def call_model(state: State, store: BaseStore):
    instructions = store.get(("agent_instructions",), key="agent_a")[0]
    prompt = prompt_template.format(instructions=instructions.value["instructions"])
    # ... continue with response generation
```

ADK state update via `state_delta` inside a tool (illustrative):

```python
def log_user_login(tool_context: ToolContext) -> dict:
    state = tool_context.state
    state["user:login_count"] = state.get("user:login_count", 0) + 1
    state["task_status"] = "active"
    state["user:last_login_ts"] = time.time()
    state["temp:validation_needed"] = True
    return {"status": "success"}  # committed when the event is appended
```

## Worked Example
A travel chatbot greets a returning user. On entry, the **Runner** retrieves the **Session** via the **SessionService**; the **State** holds `task_status` and the current booking steps. As the user shares their name and destination, the agent updates state through `output_key`/`state_delta` (never by direct dict mutation). To recall the user's past preference for aisle seats, it calls `add_session_to_memory`, which writes to the **MemoryService** (e.g. `VertexAiRagMemoryService`). On the next session, `search_memory` returns that preference, letting the bot personalize offers across conversations. One-time data like an auth token stays in `temp:` or session scope and is never stored in long-term memory.

## Key Takeaways
1. Memory is what lets agents go beyond one-shot answers—maintaining context, tracking multi-step tasks, and personalizing.
2. Short-term memory is temporary and context-window-bound; long-term memory persists externally and is retrieved by search.
3. In ADK, **Session** = chat thread, **State** = temporary dictionary, **MemoryService** = searchable long-term knowledge.
4. **SessionService** owns the session lifecycle (initiate, resume, record events, delete); update state through `append_event`, not direct mutation.
5. State key prefixes (`user:`, `app:`, `temp:`) define scope and persistence—keep state simple, typed, and clearly named.
6. LangChain's `ConversationBufferMemory` auto-injects conversation history into prompts; LangGraph's store enables semantic, episodic, and procedural long-term memory.
7. Managed options (Vertex AI RAG, Vertex Memory Bank) add scalable, persistent, semantic recall and automatic fact extraction across frameworks.
8. Choose in-memory services for testing and database/cloud services for production persistence.

## Connects To
- **Ch 14 (RAG):** Retrieval-Augmented Generation is the long-term knowledge base pattern; memory management extends it with session/state and personalized, user-scoped recall.
- **Learning and Adaptation (next pattern):** procedural memory and reflection are the bridge to agents that change how they think and act based on new experience.
- **Vertex Memory Bank:** a cross-framework managed memory layer that consolidates, de-duplicates, and recalls user knowledge.
