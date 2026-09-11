# Chapter 11: Goal Setting and Monitoring

## Core Idea
Autonomy requires explicit goals, measurable progress, and a feedback loop. Rather than reacting to each step in isolation, a goal-driven agent holds a target state, compares its current state against that target, and uses the gap to decide what to do next. Monitoring supplies the evidence—progress, drift, blocked work, or unsafe conditions—so the agent can continue, replan, degrade, or escalate instead of blindly running to completion.

## Frameworks Introduced
- **SMART goal**: Make the objective specific, measurable, achievable, relevant, and time-bound. This is the canonical model for turning a vague ambition ("be helpful") into an objective an agent can chase and a monitor can verify.
- **Goal–monitor–adjust loop**: Define metrics and milestones, observe the agent's own actions, the environment's state, and tool outputs, then react by continuing, revising the plan, degrading gracefully, or escalating to a human.
- **Role-separated judging**: In robust systems, the entity that generates work is distinct from the entity that evaluates it. A single LLM writing and grading its own output is a known weakness; a crew of specialized agents (programmer, reviewer, test writer, documenter) produces more objective assessment.

## Key Concepts
- **Goal state**: The desired end condition the agent works toward, defined in concrete, verifiable terms.
- **Initial state**: Where the agent starts; planning is the bridge between here and the goal state.
- **Success metric**: Observable evidence that the objective is met. It must be specific enough that an agent (or a judge) can answer whether it is satisfied.
- **Milestone**: An intermediate condition that signals meaningful progress toward the goal.
- **Feedback**: Information about how current output compares to goals, fed back into the next iteration.
- **Monitoring signal**: Any observation—agent action, environmental state, or tool output—that informs whether progress is being made.
- **Drift**: Divergence from the intended goal or its constraints, often discovered only through active monitoring.
- **Stop condition**: A rule that ends execution safely, either on success or when a limit is reached.
- **Replan**: Adjusting the plan when observations invalidate its assumptions.
- **Escalation**: Handing an unresolved, ambiguous, or risky situation to a human rather than guessing.
- **Iteration budget**: A predefined cap on attempts, standing in for a deadline so a loop cannot run forever.
- **Self-judgment**: The agent judging its own progress against goals; convenient but prone to optimism and hallucination.

## Mental Models
A goal is a control signal, not just a sentence. Monitor outcomes and constraints, not merely how many steps the agent completed. The trip metaphor captures it: you decide the destination (goal), note where you are (initial state), weigh options and constraints, then execute a sequence of dependent steps—rechecking your position against the destination throughout. A goal without a monitor is a wish; a monitor without a goal is noise.

## Anti-patterns / Failure Modes
- **Vague goal**: Permits endless or misaligned activity because there is nothing to declare success.
- **Activity metric**: Rewards tool calls, tokens, or steps rather than actual outcomes—agent "busyness" mistaken for progress.
- **No stop condition**: Enables runaway loops, runaway spend, and infinite refinement.
- **Self-grading collapse**: When the same LLM writes and judges, it tends to confirm its own success and miss that it is going the wrong direction.
- **Hallucinated verification**: The model may misread a goal as met without real evidence; generated code still must be run and tested, not merely declared correct.
- **Single-judge bias**: One evaluator lacks the perspective of separate reviewers, test authors, and documenters.

## Implementation Sketch
```
goals   = parse SMART goals               # specific, measurable, time-bound
metrics = define success metric + milestones
budget  = max_iterations                  # stand-in for a deadline
prev, feedback = "", ""

for i in range(budget):
    code      = generate(use_case, goals, prev, feedback)   # act
    feedback  = review(code, goals)                          # monitor
    if goals_met(feedback, goals):                           # judge vs. goal
        break                                              # success stop
    prev = code                                            # feed back
# beyond budget: surface the unresolved gap, do not silently ship
report(incomplete=True, last_feedback=feedback)
```
Key mechanics from the illustrative example: goals are a comma-separated checklist the LLM must satisfy; each cycle generates code, reviews it against the goals, and asks a single-word verdict (True/False) to make the stop decision cheap and unambiguous; on "False," the previous code and critique are fed back for the next revision. The final artifact is a clean, commented file. Production hardening separates the reviewer from the generator and adds real tests.

## Worked Example
An autonomous coding agent is handed a problem ("find the BinaryGap of a positive integer") and a quality checklist: simple to understand, functionally correct, handles comprehensive edge cases, accepts positive integers only, prints results with examples. It drafts code, then reviews that draft against every checklist item and renders a True/False verdict. On False it revises using the critique, repeating up to a fixed iteration cap. When the verdict is True it packages the solution with a header comment and saves it. If the cap is reached first, the honest outcome is an incomplete result surfaced for a human—not a confident but unverified file. A robust variant routes this to a crew: a Peer Programmer writes, a Code Reviewer grades objectively, a Test Writer adds unit tests, a Documenter writes docs, and a Prompt Refiner tunes interactions.

## Key Takeaways
1. Define success before acting: state the goal state, success metric, and stop condition up front.
2. Make goals SMART and monitoring concrete—observe actions, environment, and tool outputs, not step counts.
3. Close the loop: generate, review against goals, feed feedback back, and react by continuing, replanning, degrading, or escalating.
4. Separate the judge from the generator to avoid self-grading collapse and hallucinated verification.
5. Always set an iteration (or time/cost) budget so monitoring cannot run forever.
6. Never trust self-declared success alone: run and test produced artifacts.
7. Make failure and incomplete completion visible; escalate ambiguity instead of guessing.

## Connects To
- **Ch 6 (Planning)**: Supplies the milestones, dependencies, and sub-goals that monitoring tracks; planning and monitoring form a loop (plan → act → monitor → replan).
- **Ch 12 (Monitoring / Recovery)**: The monitoring step here triggers recovery, replanning, and escalation when drift or blockage is detected.
- **Ch 20 (Priority / orchestration)**: Monitoring signals can reprioritize tasks and redirect agent effort as conditions change.
