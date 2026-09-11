# Chapter 6: Planning

## Core Idea
Planning is the ability of an agent (or a system of agents) to formulate a sequence
of actions that moves a system from an initial state toward a goal state. When you
delegate a complex goal such as "organize a team offsite," you define the *what* — the
objective and its constraints — but not the *how*. The planner's job is to autonomously
chart the course: understand the current state (budget, headcount, dates), define the
goal state (a booked offsite), and discover the ordered actions that connect them. The
plan is not known in advance; it is generated in response to the request, and it is a
hypothesis rather than a rigid script. A hallmark of planning is adaptability — when a
venue cancels or a caterer is booked, a capable planner registers the new constraint,
re-evaluates options, and formulates an alternative rather than simply failing. The
foundational design decision reduces to one question: **does the "how" need to be
discovered, or is it already known?** If it is already known and the task is repeatable,
a fixed, constrained workflow is more effective because it limits autonomy to reduce
uncertainty and guarantee a consistent outcome.

## Frameworks Introduced
- **Plan-and-execute**: An agent first formulates a multi-step plan, then executes it
  sequentially. The plan is an explicit, inspectable artifact produced before action.
- **Plan-execute-replan (dynamic planning)**: An initial plan is a starting point. The
  agent executes, observes new information, and revises the plan when assumptions fail
  or constraints change. This loop is the engine of adaptability.
- **Hierarchical goal decomposition**: A single high-level objective is recursively
  broken into discrete, executable sub-goals organized into phases (e.g., gather,
  summarize, structure, refine).
- **Collaborative / human-in-the-loop planning**: The draft plan is surfaced to the user
  for review and modification *before* execution, shaping the trajectory cheaply.
- **Asynchronous long-running execution**: Complex plans (analyzing hundreds of
  sources) run off the critical path, resilient to single-point failures, with the user
  notified on completion.

## Key Concepts
- **Initial state vs. goal state**: Planning is state-space traversal — defining where
  the system starts and the concrete conditions that define success.
- **Goal decomposition**: Splitting a high-level objective into a sequence of smaller,
  actionable sub-goals or steps.
- **Sub-task / step**: A discrete, executable unit of work within the plan.
- **Dependency**: The ordering constraint that some steps must occur before others (e.g.,
  create system accounts before assigning training modules during onboarding).
- **Plan validity**: Whether the proposed steps are feasible given available tools,
  data, and context.
- **Replanning**: Re-evaluating and reformulating the plan in light of new information,
  failed steps, or newly discovered constraints.
- **Knowledge gaps**: Missing information the plan identifies and then targets with
  follow-up searches or actions — the driver of iterative research loops.
- **Synthesis**: The final phase where collected, vetted information is organized into a
  coherent narrative rather than a concatenated list of findings.
- **Sequential vs. dynamic process**: Sequential plans execute steps in a fixed order;
  dynamic plans loop, refining based on results as they appear.
- **Flexibility vs. predictability trade-off**: More planner autonomy yields flexibility
  but introduces unpredictability; fixed workflows do the opposite.

## Mental Models
- **A plan is a hypothesis, not a promise.** It encodes assumptions about the world that
  must be tested against observations; when they break, you replan.
- **Plan enough to expose dependencies, not so much that trivial work becomes
  bureaucracy.** The right granularity makes interdependencies visible without locking in
  premature detail.
- **Planning is state-space traversal.** Think of it as finding a path through a graph of
  states, optimizing for metrics (time, energy, cost) while respecting constraints
  (obstacles, rules).
- **The "how" question is the gate.** Choose a planner only when the path to the goal is
  genuinely unknown; otherwise encode it as a deterministic workflow.

## Anti-patterns / Failure Modes
- **Confusing planning with universal solution.** Dynamic planning is a specific tool,
  not a default. Applying it to well-understood, repeatable problems wastes autonomy and
  introduces unpredictable behavior where a fixed workflow would be more reliable.
- **Failing around obstacles.** A planner that cannot incorporate new constraints and
  simply errors out has not actually planned — it has scripted.
- **No synthesis.** Producing a flat list of gathered facts or searches without
  organizing them into a coherent narrative misses the point of complex-output planning.
- **Opaque process.** When intermediate steps, queries, and reasoning are hidden, the
  plan cannot be debugged, audited, or trusted — especially for high-stakes research.
- **Unbounded execution.** A research loop with no stop condition or resource guard can
  spin consuming time and tools indefinitely.

## Implementation Sketch
Illustrative pseudocode (not source from any framework):

```
function plan_and_execute(goal, state, tools, stop_condition):
    plan = decompose(goal, state)            # high-level -> ordered sub-goals
    surface_for_review(plan)                 # optional human-in-the-loop
    while not stop_condition(state):
        step = plan.next_available(state)     # respect dependencies
        if step is None:
            plan = replan(plan, state)        # new constraint or gap discovered
            continue
        try:
            result = execute(step, tools, state)
            state = update(state, result)     # record outcome, detect gaps
        except Failure as e:
            plan = replan(plan, state, e)     # substitute path or source
    report = synthesize(state)                # structured, coherent output
    return report, trace(plan)                # include citations / provenance
```

The Crew AI sketch follows the plan-and-execute shape literally: a single agent is
prompted to (1) produce a bullet-point plan for a summary, then (2) write the summary
from that plan, with an `expected_output` that enforces two distinct sections. The crew
runs `Process.sequential`, so the plan precedes and constrains the writing.

## Worked Example: Deep Research Pipeline
Consider building a system that produces a cited competitive-analysis report. Planning
decomposes the request into phases: (1) deconstruct the prompt into multi-point research
questions, (2) iteratively query a search tool, (3) evaluate sources for relevance and
detect knowledge gaps, (4) run follow-up searches to fill those gaps, (5) corroborate and
resolve discrepancies, and (6) synthesize a structured, multi-page report with inline
citations and provenance.

Two real systems illustrate this. **Google DeepResearch** deconstructs a prompt into a
research plan, presents it to the user for review before execution, then runs an
iterative search-and-analysis loop that refines queries as it gathers data. It runs
asynchronously (resilient to single-point failures, notifies on completion), can blend
user-provided private documents with web sources, and returns the full list of sources
consulted. **OpenAI's Deep Research API** similarly breaks a high-level query into
sub-questions, uses built-in tools (`web_search_preview`, optional `code_interpreter`, and
MCP tools for internal data), and exposes transparency: the final report with inline
citations plus intermediate steps — reasoning summaries, exact search queries executed,
and any code run. Models such as `o3-deep-research-2025-06-26` favor synthesis quality
while `o4-mini-deep-research` favors latency. Both show planning transforms a single query
into a comprehensive, synthesized body of knowledge while reducing manual research cost
and selection bias through broader source coverage.

## Key Takeaways
1. **Define the goal and stop conditions up front.** Planning begins by specifying the
   initial state, the goal state, and what "done" looks like before decomposing work.
2. **Decompose into interdependent, executable steps.** Break high-level objectives into
   discrete sub-goals whose ordering (dependencies) is explicit.
3. **Treat the plan as revisable.** Use plan-execute-replan so new constraints, failures,
   and knowledge gaps trigger replanning rather than hard failure.
4. **Match autonomy to the problem.** Reserve planner autonomy for tasks whose "how" is
   genuinely unknown; use fixed workflows when it is already known and repeatable.
5. **Surface the plan for review.** Let users shape the trajectory before execution to
   correct course cheaply.
6. **Synthesize, don't just collect.** The final value is a coherent, structured output
   with provenance, not a pile of gathered facts.
7. **Run heavy plans asynchronously and observably.** Guard resources, resist
   single-point failures, and expose intermediate steps for trust and debugging.

## Connects To
- **Planning depends on goal definition** and, in turn, feeds execution: a plan is only
  useful if something can carry out its steps.
- **Execution and monitoring** close the loop by running steps, observing results, and
  supplying the facts that trigger replanning.
- **Tool access** determines plan validity — a plan is only as good as the actions and
  data sources the agent can actually invoke (search, code interpreters, MCP-connected
  internal systems).
- **Transparency / provenance** concerns carry into planning's outputs: citations,
  queries, and reasoning traces make the plan auditable and trustworthy.
- **Human-in-the-loop review** connects planning to collaborative design patterns, letting
  users correct the trajectory before costly execution begins.
