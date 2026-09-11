# Chapter 3: Parallelization

## Core Idea
Many agentic tasks decompose into sub-tasks that do **not** depend on one another's
outputs. When that independence holds, executing those sub-tasks concurrently — LLM
calls, tool/API invocations, or entire sub-agents — collapses wall-clock time:
instead of the total being the *sum* of each step's duration, independent branches
run at once and their results are joined at an explicit synchronization point.

Parallelism is a **latency optimization, not a reasoning shortcut**. It does not make
any single step smarter; it makes the parts that *can* overlap actually overlap. The
bottleneck it removes is most dramatic when steps wait on external I/O (APIs,
databases, search), where sequential waiting accumulates each request's latency.

## Frameworks Introduced
- **LangChain Expression Language (LCEL)** — `|` sequences steps; combining runnables
  inside a dictionary/list (via `RunnableParallel`) makes the runtime execute them
  concurrently when the collection feeds a downstream component.
- **LangGraph** — a graph's topology defines parallelism: multiple nodes can fan out
  from a single common state transition and later converge at a join node.
- **Google ADK** — native multi-agent primitives: `ParallelAgent` (runs
  `sub_agents` concurrently, storing each result in session state via `output_key`),
  `SequentialAgent` (orchestrates phases), and `LlmAgent` (the worker/coordinator).
  Also supports **LLM-Driven Delegation**, where a Coordinator agent's model identifies
  independent sub-tasks and triggers their concurrent handling.

## Key Concepts
- **Independence** — a sub-task needs no other sub-task's output to proceed. This is the
  precondition you prove before fanning out.
- **Fan-out / fan-in** — split work into concurrent branches (fan-out), then collect and
  synthesize their outputs at a convergence point (fan-in).
- **Join / synchronization point** — the step that waits for all required branches and
  merges them; typically sequential.
- **Concurrency vs. parallelism** — `asyncio` gives *concurrency* on one thread via an
  event loop that switches tasks when one is idle (e.g. awaiting I/O); it is not true
  CPU parallelism, which Python's Global Interpreter Lock (GIL) constrains.
- **Bounded concurrency** — cap the number of in-flight branches to protect cost,
  provider rate limits, and downstream capacity.
- **output_key** (ADK) — the named slot in session state where each parallel sub-agent
  stores its result for the merger to read.
- **Partial / degraded result** — a branch that timed out, failed, or returned weak
  output and must be detectable and handled.
- **Branch identity** — preserve which source/branch produced each result so synthesis
  can attribute findings and detect conflicts.

## Mental Models
- **Parallelism is scheduling, not intelligence.** Use it for *breadth* (many independent
  lookups); use Prompt Chaining for *dependency*; use Routing for *decisions*.
- **The slow path is the sum of waits.** If steps only ever wait on each other, the total
  latency is additive — overlap removes the additive part.
- **Fan-in is the truth-teller.** Concurrency buys speed; the join is where correctness
  is decided, so synthesis must inspect quality and conflicts rather than average them away.

## Anti-patterns / Failure Modes
- **Parallelizing dependent steps** — fanning out work that secretly needs another
  branch's output produces race conditions or inconsistent shared assumptions.
- **Unlimited fan-out** — unbounded concurrency causes cost spikes and provider
  throttling; always bound it.
- **Blind merge** — feeding all branch outputs into synthesis without filtering or
  labeling lets one bad/partial branch poison the final answer.
- **Confusing concurrency with parallelism** — assuming `asyncio` gives real throughput
  for CPU-bound work that the GIL serializes.
- **Ignoring the complexity tax** — concurrent architecture materially raises the cost of
  design, debugging, and logging; treat that as a first-class trade-off.

## Implementation Sketch
Pseudocode (framework-agnostic):

```
branches = [make_branch(input, spec) for spec in independent_specs]   # fan-out
results  = await run_bounded(branches, max_concurrency=N)             # concurrent run
cleaned  = [label_or_drop(r) for r in results]                        # handle partials
answer   = synthesize(cleaned, input)                                 # fan-in / join
```

**LangChain (LCEL)** — define each independent unit as its own chain (prompt | LLM |
parser), bundle them in a `RunnableParallel` (plus a `RunnablePassthrough` to forward
the original input), then pipe the bundle into a synthesis prompt → LLM → parser, and
run with `ainvoke` under `asyncio`.

**Google ADK** — create worker `LlmAgent`s (each with an `output_key`), wrap them in a
`ParallelAgent`, then place the parallel agent and a merging `LlmAgent` into a
`SequentialAgent` so research runs concurrently and synthesis runs after the join.

## Worked Example
**Research a topic, then synthesize.**
- Sequential: search A → summarize A → search B → summarize B → synthesize (each step
  waits for the last).
- Parallel: **search A** and **search B** concurrently → **summarize A** and **summarize
  B** concurrently → **synthesize** the final answer (this step waits for both summaries).
  Each parallel researcher returns a summary under its own `output_key`; the merger
  `LlmAgent` synthesizes a structured, attributed report **grounded exclusively** on the
  provided summaries (no external knowledge), and flags where sources conflict.

## Key Takeaways
1. Parallelize only what is genuinely independent — prove independence before fanning out.
2. It shines on external-I/O-bound work (multiple APIs, databases, searches), where it
   removes additive waiting latency.
3. Bound concurrency and preserve branch identity so synthesis can attribute and detect
   conflicts; make joins tolerate timeouts and partial failures.
4. Frameworks bake this in: LCEL's `RunnableParallel`, LangGraph's branching graph
   topology, and Google ADK's `ParallelAgent`/`SequentialAgent`.
5. `asyncio` provides concurrency, not true parallelism — account for the GIL on CPU-bound
   work.
6. The join/fan-in is where correctness lives: synthesis must inspect quality and conflicts,
   not silently average them away.
7. Concurrency raises complexity and cost across design, debugging, and logging — weigh it.

## Connects To
- **Prompt Chaining** — parallelization is the concurrent counterpart to sequential
  chaining; the two compose (parallel fan-in feeds the next chain step).
- **Routing** — a router can decide *when* to fan out versus run sequentially.
- **Multi-agent collaboration** — parallel specialist agents are one coordination topology,
  often orchestrated by a Coordinator (LLM-Driven Delegation).
- **Failure handling / recovery** — partial branch failures need explicit timeout and
  retry policy at the join.
- **Cost & resource management** — bounded concurrency is a resource and cost decision.
