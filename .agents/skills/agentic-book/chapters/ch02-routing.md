# Chapter 2: Routing

## Core Idea
Sequential (prompt-chaining) workflows execute a fixed, linear sequence of steps. Routing breaks that rigidity by inserting **conditional logic** into the agent's operational cycle: before acting, the agent inspects the input, the environment, or the outcome of a prior step, decides which of several possible subsequent actions is most appropriate, and directs control there. Routing is the mechanism that lets an agent *arbitrate between multiple potential actions* rather than defaulting to a single predetermined path.

Routing can sit at multiple junctures: at the outset to classify a primary task, at intermediate points within a processing chain to pick the next action, or inside a subroutine to choose the best tool from a set. The core component is a **router** — a mechanism that evaluates and directs the flow.

## Frameworks Introduced
- **LangChain / LangGraph** — LangGraph's state-based graph architecture is especially suited to complex routing where decisions depend on the accumulated state of the whole system. LangChain offers composable runnables (`RunnableBranch`, `StrOutputParser`, `ChatPromptTemplate`) for building lightweight router chains.
- **Google Agent Developer Kit (ADK)** — Provides foundational components for structuring an agent's capabilities. In ADK, routing is typically expressed as a discrete set of **tools** (via `FunctionTool`), and a coordinator `Agent` with `sub_agents` enabled triggers framework-managed **Auto-Flow** to delegate to the right specialist.
- **Google Generative AI (`gemini-2.5-flash` / `gemini-2.0-flash`)** — Used as the classifier / coordinator model, typically at `temperature=0` for deterministic decisions.

The two frameworks illustrate divergent architectural approaches: LangGraph defines explicit nodes, edges, and transitions in a computational graph; ADK defines discrete capabilities/tools and leans on the framework's internal model to match intent to handler.

## Key Concepts
1. **Router / Coordinator** — The component that evaluates input and selects the next destination. In LangChain it is a router chain; in ADK it is a coordinator `Agent`.
2. **Route** — A named downstream branch (e.g., "booker", "info", "unclear").
3. **LLM-based Routing** — The LLM is prompted to output a category identifier ("output only the category: 'Order Status', 'Product Info', ..."), which the system reads and acts on. Flexible, but a generative model executing a prompt at inference time.
4. **Embedding-based (semantic) Routing** — The query is vectorized and matched to the most similar route/capability embedding. Decides on *meaning* rather than keywords; useful when phrasing varies widely.
5. **Rule-based Routing** — Predefined if-else / switch logic on keywords, patterns, or structured extraction. Faster and more deterministic, but less flexible on novel or nuanced inputs.
6. **ML-Model-Based Routing** — A supervised, fine-tuned discriminative classifier trained on a small labeled corpus. The routing logic lives in learned weights, not in a prompt; LLMs may help generate synthetic training data but are not part of the real-time decision.
7. **Classifier output / decision token** — The router emits a label that downstream logic matches against.
8. **Delegation** — Passing the request (and minimal context) to the selected handler/sub-agent.
9. **Clarification / fallback branch** — The safe destination when intent is unclear or confidence is insufficient.
10. **Auto-Flow (ADK)** — Framework-managed delegation driven by the presence of `sub_agents`.
11. **State-graph transitions (LangGraph)** — Edges whose selection depends on accumulated node state.
12. **Dispatch** — The act of routing the request to the chosen branch and extracting its final output.

## Mental Models
- **Router as a classifier, not a solver.** The router should decide *where* to send a request, not *do* the work. Keep it small, fast, and focused on intent/capability, not on the whole task.
- **Route on intent and capability, not wording.** Match on meaning and needed function; surface wording varies. Prefer a deterministic rule or classifier for the decisions they reliably cover.
- **Always reserve a "nowhere" destination.** Every router needs a safe fallback (clarify / escalate / refuse) so an uncertain input never forces the system to invent an action.
- **Cost/latency tradeoff.** LLM routers are flexible but expensive per call; rules and embeddings are cheaper and faster; fine-tuned classifiers are cheap at scale after training cost. Choose by volume and variance.

## Anti-patterns / Failure Modes
- **No fallback branch** — an unexpected classifier output falls through and the system invents a route or silently fails.
- **Overloaded router** — one classifier is asked to reason about the entire task, degrading accuracy; split routing into stages.
- **Hidden routing** — the decision and its rationale are not exposed to traces, making behavior non-auditable.
- **Routing on superficial keywords** — brittle against paraphrase; use semantic/embedding methods when phrasing varies.
- **LLM in the hot path when unnecessary** — paying generative-model cost for decisions a rule or classifier handles reliably.
- **Single linear path assumed** — forcing all inputs through one workflow ignores real variability and keeps the system rigid.

## Implementation Sketch
General dataflow:

```
request ──▶ router(classify intent / semantics / rules) ──┬──▶ branch: booker / tool A
                                                          ├──▶ branch: info / tool B
                                                          ├──▶ branch: escalate / human
                                                          └──▶ fallback: clarify / refuse
each branch ──▶ execute ──▶ return final output
```

LangChain-style pseudocode (illustrative, not from the source):

```
router_chain = prompt | llm(temperature=0) | StrOutputParser()   # emits 'booker'|'info'|'unclear'

delegation = RunnableBranch(
    (lambda x: x['decision'] == 'booker', booking_handler),
    (lambda x: x['decision'] == 'info',   info_handler),
    unclear_handler,   # default / fallback
)

coordinator = {"decision": router_chain, "request": RunnablePassthrough()} \
            | delegation \
            | (lambda x: x['output'])   # extract final result
```

ADK-style pseudocode (illustrative):

```
booking_agent = Agent(name="Booker", model=..., tools=[FunctionTool(booking_handler)])
info_agent    = Agent(name="Info",   model=..., tools=[FunctionTool(info_handler)])
coordinator   = Agent(name="Coordinator", model=...,
                      instruction="delegate bookings to Booker, all else to Info",
                      sub_agents=[booking_agent, info_agent])  # enables Auto-Flow
runner.run(coordinator, user_message)   # framework picks the handler
```

## Worked Example
A customer-support coordinator classifies incoming queries and routes by intent:
- **"Check order status"** → order database sub-agent/tool chain.
- **"Product information"** → product-catalog search chain.
- **"Technical support"** → troubleshooting-guide chain or human escalation.
- **Unclear** → clarification sub-agent.

Concrete runs: *"Book me a flight to London."* → `booker`; *"What is the capital of Italy?"* → `info`; *"Tell me about quantum physics."* → `unclear` (clarification). In ADK, *"Book me a hotel in Paris."* → Booker, *"What is the highest mountain in the world?"* → Info, *"Find flights to Tokyo next month."* → Booker. The coordinator never answers directly; it only classifies and delegates, then returns the handler's output.

## Key Takeaways
1. Routing injects conditional logic that lets an agent select the right tool, workflow, or sub-agent based on input and state — moving beyond linear execution.
2. Four router implementations exist with a flexibility/cost tradeoff: LLM-based, embedding-based, rule-based, and fine-tuned-ML. Prefer deterministic methods where they cover the space.
3. Define routes and their contracts (inputs, outputs, fallback) before writing the classifier.
4. Always keep a clarification / escalation / refuse branch for uncertain inputs.
5. Expose the decision and its rationale to traces for auditability.
6. LangGraph suits stateful, multi-step routing via explicit graphs; ADK suits discrete tool delegation via Auto-Flow — choose per architecture.
7. Routing can be applied at the start, mid-chain, or inside subroutines to pick the best tool from a set.

## Connects To
- **Chapter 1 (Prompt Chaining)** — Routing extends sequential chains with conditional branching.
- **Chapter 14 (RAG / Embeddings)** — Embedding-based routing reuses vector similarity to match queries to routes or capabilities.
- **Chapter on Multi-Agent / Delegation** — The coordinator + specialist sub-agent structure is a foundational delegation pattern.
- **Ch 16** — Complexity/Resource routing controls resource use.
- **Ch 13** — Risk routing determines when human approval is required.
- **Ch 18** — Safety policy can override any route chosen by the router.
