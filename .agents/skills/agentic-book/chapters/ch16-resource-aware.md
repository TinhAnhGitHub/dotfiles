# Chapter 16: Resource-Aware Optimization

## Core Idea
Resource-aware optimization is the discipline of making every operational decision an agent
makes — which model to call, how much context to send, which tools to invoke, whether to
retry or bail — a function of the task's true difficulty and the budget of money, time, and
compute actually available. It goes beyond plain planning: planning sequences actions, while
resource-aware optimization prices and throttles them. The central tension is a
three-way trade-off among output quality, cost, and latency, and the pattern builds an
agentic system that monitors and reallocates those resources dynamically rather than
hard-coding a single model or tool for the whole session.

## Frameworks Introduced
- **Complexity router (Router Agent):** a front-door classifier that scores an incoming
  request and forwards it to the least capable model that can still do the job well. Simple
  queries land on a fast, cheap path; complex or high-risk queries escalate to a powerful,
  expensive one. The router itself can be a rule (e.g., query length) or an LLM/ML model
  that reasons about nuance, and it can be improved by prompt tuning or fine-tuning on a
  labeled set of (query, best-model) pairs.
- **Hierarchical multi-agent orchestration:** Google's ADK lets specialized agents carry
  specialized roles. A common shape is a planner (strong model) that decomposes a request,
  then tool-execution steps (cheap model) that perform repetitive lookups. Different agents
  can even be bound to different models.
- **Critique Agent:** an evaluator that reviews generated text (and optionally the original
  query) for correctness, completeness, and bias. It drives self-correction, produces
  performance metrics, and — crucially for budgeting — flags bad routing decisions (simple
  questions sent to an expensive model, or hard questions sent to a weak one), feeding that
  signal back to improve the router.
- **Graceful degradation / fallback:** when a preferred model is overloaded, throttled, or
  down, the system automatically switches to a default or cheaper model so service
  continues rather than failing. OpenRouter expresses this as a sequential list of models to
  try in order.
- **Dynamic model switching and adaptive tool selection:** choosing models and tools per
  sub-task based on cost, latency, and execution time, plus contextual pruning (summarizing
  and retaining only the most relevant history) to cut token spend.

## Key Concepts
- **Router Agent:** the classifier that maps requests to the appropriate model or tool.
- **Critique Agent:** the evaluator that enforces quality and exposes routing mistakes.
- **Quality tier:** a bundle of a resource profile (model, context size, toolset) with an
  implied service level.
- **Budget:** an explicit cap on tokens, wall-clock time, API calls, or dollars.
- **Contextual pruning & summarization:** trimming history so inference costs track what is
  actually needed.
- **Adaptive tool use:** invoking only the capabilities required to resolve current
  uncertainty, weighing API cost and latency.
- **Proactive resource prediction:** forecasting workload so resources can be pre-allocated
  and bottlenecks avoided.
- **Graceful degradation:** continuing at reduced capacity under pressure instead of
  crashing.
- **Learned resource allocation:** refining allocation policy over time from feedback and
  metrics.
- **Cost-sensitive exploration:** in multi-agent systems, treating communication cost as a
  first-class optimization target alongside compute.
- **Energy-efficient / edge deployment:** minimizing power use on battery-constrained
  hardware.
- **Parallelization & distributed awareness:** spreading load across machines for throughput.

## Mental Models
- **Optimize the whole trajectory, not the price of one call.** A cheap but wrong action on a
  high-stakes task costs far more than an expensive, correct, read-only answer.
- **Right-size before you scale up.** Escalate to a stronger model only when complexity or
  risk justifies it; default to the smallest tool that fits.
- **Quality is a knob, not a setting.** Treat quality, cost, and latency as adjustable
  levers balanced against each other, with the balance point chosen per task and per user.
- **Fail downward, never dead.** When capacity vanishes, degrade gracefully to a fallback
  rather than returning an error.

## Anti-patterns / Failure Modes
- **Cheapest-always:** routing everything to the cheapest model sacrifices quality precisely
  where errors are most expensive.
- **Context accumulation:** piling on history inflates token count and attention dilution.
- **Unmeasured routing:** assuming the classifier is right without tracking its error rate or
  the downstream cost/quality it produces.
- **Over-engineering simple asks:** spending a router + critique + tools on a question that a
  single cheap call answers.
- **Silent degradation:** degrading quality without telling the user or logging it, so
  problems go unnoticed.
- **Fallback loops:** repeatedly hitting a broken primary model without a backoff or a hard
  stop, burning budget.

## Implementation Sketch
Illustrative pseudocode (not from any library):

```
function handle(query):
    tier = router.classify(query)          # simple / reasoning / live_data
    budget = make_budget(query, tier)      # tokens, time, dollars caps
    context = prune(history, query)        # keep only relevant bits

    if tier == simple:
        model = CHEAP
    elif tier == reasoning:
        model = STRONG
    else:  # live_data
        results = tool.search(query)       # adaptive tool use
        model = STRONG
        context = combine(context, results)

    answer = model.generate(context)
    ok, note = critic.evaluate(query, answer)
    if not ok and budget.remaining():
        answer = model.generate(context + note)   # self-correction loop
        budget.spend()

    router.record(query, tier, answer, cost, latency)  # learn to route better
    return answer, model, cost
```

A concrete OpenAI-flavored variant classifies each prompt into `simple`, `reasoning`, or
`internet_search`, runs a Google Custom Search for the last category, and picks
`gpt-4o-mini` for simple, `o4-mini` for reasoning, and `gpt-4o` for search-grounded answers.
An ADK-flavored variant defines a `QueryRouterAgent` (a `BaseAgent`) that can route by a
cheap metric like word count, and pairs a strong "planner" agent with a cheap "flash" agent
for the repetitive tool calls that follow the plan.

## Worked Example
A travel planner uses a hierarchical agent. The planner — a strong model — understands a
vague request, breaks it into a multi-step itinerary, and makes the judgment calls. Once the
plan exists, the individual lookups (flight prices, hotel availability, restaurant reviews)
are simple, repetitive web queries that a cheap, fast model handles fine. A Critique Agent
then reviews outputs for factual correctness and bias, and watches the router: if it keeps
sending trivial lookups to the strong model or hard reasoning to the weak one, the critique
signal retunes routing and saves money. The same logic applies to a financial analyst who
gets a quick, cheap summary for a preliminary report and a powerful, slower model only when
a high-stakes forecast justifies the cost and time.

## Key Takeaways
1. Model choice, context size, tool depth, and retry budget should all scale with task
   complexity and real cost/latency/compute constraints.
2. A Router Agent classifies incoming work; route simple queries to cheap fast paths and
   reserve power for hard or high-risk ones.
3. A Critique Agent raises quality and exposes routing mistakes, feeding a self-improving
   loop that improves allocation over time.
4. Prune context, use tools adaptively, and consider communication and energy costs in
   multi-agent and edge deployments.
5. Build graceful degradation and sequential fallbacks so failures reduce quality instead of
   breaking service.
6. Predict workload proactively and, where possible, learn allocation policies from feedback.
7. Always balance quality, cost, and latency together and measure the result.

## Connects To
- **Router / routing chapters:** the complexity router is a specialized instance of general
  request routing.
- **Concurrency / orchestration chapters:** throughput, parallelization, and cost are
  coupled — distributing work changes both latency and spend.
- **Evaluation & monitoring chapters:** the trade-offs here are only as good as the metrics
  that measure quality, cost, and latency; the Critique Agent is a living evaluation loop.
- **Multi-agent orchestration:** hierarchical planning with per-agent model binding is the
  structural backbone that makes resource-aware routing possible.
