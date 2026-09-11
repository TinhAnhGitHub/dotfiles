# Chapter 20: Prioritization

## Core Idea
In complex, dynamic environments an agent faces many candidate actions, conflicting
goals, and finite resources. Without an explicit process for choosing the next action,
it wastes effort, misses deadlines, or fails its primary objectives. The
**Prioritization pattern** gives the agent a policy for ranking tasks, goals, and
sub-goals by significance, urgency, dependencies, and resource cost, then selecting and
sequencing the most critical work — and re-ranking as the world changes. It mirrors how a
manager coordinates a team by weighing input from every member rather than reacting to
the loudest request.

## Frameworks Introduced
- **Criteria-driven ranking**: Define evaluation criteria (urgency, importance,
  dependencies, resource availability, cost/benefit, user preferences) → evaluate each
  candidate → apply scheduling/selection logic to pick the next action or sequence →
  dynamically re-prioritize when circumstances change.
- **Layered prioritization**: Apply the same ranking at three levels — overarching
  objective selection (strategic), ordering steps within a plan (sub-tasks), and choosing
  the next immediate action (tactical action selection).
- **Dynamic re-prioritization**: Continuously update the order in response to new critical
  events, approaching deadlines, or completed work, so the agent stays responsive rather
  than executing a stale plan.

## Key Concepts
- **Criteria definition**: The rules or metrics used to judge tasks — urgency (time
  sensitivity), importance (impact on the main objective), dependencies (whether a task is
  a prerequisite for others), resource availability (are tools/information ready?),
  cost/benefit (effort vs. expected outcome), and user preferences for personalized agents.
- **Task evaluation**: Assessing each candidate against the criteria, using anything from
  simple rules to weighted scoring or LLM reasoning.
- **Scheduling / selection logic**: The algorithm that, from the evaluations, chooses the
  optimal next action or sequence — often a queue or a light planning component.
- **Urgency**: Cost of delay; how soon something must be acted on before its value decays
  or harm occurs.
- **Importance/value**: Contribution to the mission or primary objective.
- **Dependencies**: Tasks that unlock other tasks; doing prerequisite or risk-reducing work
  first even when a blocked task looks more attractive.
- **Resource constraints**: Time, compute, budget, and personnel that cap what can run at
  once and shift priorities (e.g., off-peak for cheap batch jobs).
- **Re-prioritization**: Re-scoring and re-ordering after new information arrives.

## Mental Models
Priority is a **policy under constraints**, not a permanent list. A good ranking balances
urgency, importance, dependencies, and cost, and it is revisited as observations arrive.
Preserve deadlines, fairness, and safety even when a model is tempted by a quick but
low-value shortcut. Think of the queue as a living state: every completed task, new
request, and changing deadline is a signal to re-rank.

## Anti-patterns / Failure Modes
- **Static queue**: Evaluate once and never re-score, ignoring new evidence and shifting
  deadlines.
- **Urgency-only ranking**: Chase the most time-sensitive work and starve important
  foundational or high-value tasks.
- **Unexplainable score**: Rank by an opaque number so decisions cannot be audited,
  challenged, or trusted.
- **Ignoring dependencies**: Jump to a tempting task that is blocked, wasting a turn on
  work that cannot complete.
- **Over-committing**: Scheduling more than available resources allow, causing contention
  and missed deadlines.

## Implementation Sketch
A generic loop (illustrative, not from any source):

```
def prioritize(candidates, criteria, resources):
    scored = []
    for t in candidates:
        score = (criteria.importance * t.value
                 + criteria.urgency   * t.time_pressure
                 - criteria.cost      * t.effort
                 + criteria.dep_bonus * t.unlocks_others)
        scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored

def run(queue, resources):
    while queue:
        next_task = select_next(prioritize(queue, CRITERIA, resources), resources)
        if next_task is None:          # no runnable work fits resources
            next_task = pick_least_blocking(queue)  # do a prerequisite instead
        outcome = execute(next_task)
        queue = re_evaluate(queue, outcome)   # re-prioritize on new signals
```

Selection prefers the highest score that current resources can run; when nothing fits, it
picks a prerequisite or risk-reducing task that unblocks the queue.

## Worked Example
The book's example is a **Project Manager agent built with LangChain**. It wraps an
in-memory `SuperSimpleTaskManager` (a dict-backed store of `Task` objects with `id`,
`description`, `priority` P0/P1/P2, and `assigned_to`) and exposes tools:
`create_new_task`, `assign_priority_to_task`, `assign_task_to_worker`, and `list_all_tasks`,
each validated with Pydantic argument schemas. A `ChatOpenAI` model drives a REACT agent
whose system prompt enforces a prioritization workflow: create the task first to get an ID,
then infer priority/assignee from the request (urgent/ASAP/critical → P0; else a sensible
default like P1 and a default worker), and finally list the board. It runs two scenarios —
an urgent login-system request routed to Worker B (P0) and a low-detail content-review task
(defaulted to P1) — showing how the agent interprets ambiguous input, selects tools
autonomously, sequences actions, and records final state.

A contrasting real-world illustration: a support agent handles a **security incident**
before a routine feature request even when the feature has higher business value, because
risk and time-to-harm dominate; it logs the reason and revisits the queue after containment.

## Key Takeaways
1. **Declare ranking criteria and weights up front** (urgency, importance, dependencies,
   cost, resources) so decisions are reproducible.
2. **Rank at three levels** — objective, plan sub-tasks, and immediate action — and keep
   them consistent.
3. **Account for dependencies and risk**; do work that unblocks others even if it is less
   flashy.
4. **Re-score dynamically** whenever new events, deadlines, or observations arrive.
5. **Explain the choice** — surface why a task was selected or deferred so it can be
   audited and trusted.
6. **Respect resource constraints** — schedule cheap batch work off-peak and protect
   capacity for critical paths.
7. **Match the mechanism to the stakes** — simple queues for stable settings, LLM reasoning
   or planning components for ambiguous, multi-objective ones.

## Connects To
- **Planning**: exposes the task dependencies and sub-task ordering that prioritization ranks.
- **Monitoring**: supplies the real-time signals (new events, approaching deadlines) that
  trigger re-prioritization.
- **Cost / capacity management**: provides the resource and cost inputs that constrain the
  ranking.
- **Tool use**: the PM agent shows prioritization realized through discrete, validated tools
  the model selects and sequences.
