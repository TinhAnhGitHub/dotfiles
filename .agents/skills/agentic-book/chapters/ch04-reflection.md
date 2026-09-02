# Chapter 4: Reflection

## Core Idea
The Reflection pattern lets an agent evaluate its own output, process, or internal state and use that evaluation to improve the result. Unlike a simple sequential chain (where output flows straight to the next step) or routing (which selects a path), reflection inserts a **feedback loop**: the agent produces an output, examines it against desired criteria, and generates a better version or adjusts its future actions. The initial response is never treated as the final one.

Reflection can be performed by the same agent (self-reflection) or, more robustly, by a **separate logical agent** whose sole role is to analyze the output. The process has four stages:

1. **Execution** — the agent performs the task or produces an initial output.
2. **Evaluation/Critique** — an LLM call or rule set analyzes the result for factual accuracy, coherence, style, completeness, and adherence to instructions.
3. **Reflection/Refinement** — based on the critique, the agent produces a refined output, tunes parameters for a later step, or revises the overall plan.
4. **Iteration** (optional but common) — the cycle repeats until a satisfactory result or stopping condition is met.

## Frameworks Introduced
- **Producer–Critic (Generator–Critic / Producer–Reviewer) model** — the canonical implementation. Separate creation from evaluation: one role generates, another (or a second LLM call with a distinct system prompt) critiques against explicit criteria, the critique is fed back, and the loop stops after a fixed budget.
- **Self-reflection** — a single agent reviews its own work; useful for quick passes but prone to confirmation bias.
- **LangChain / LCEL** — compositional syntax for a single generate-critique-refine cycle.
- **LangGraph** — native state management and conditional transitions for full iterative loops.
- **Google ADK** — `SequentialAgent` and `LlmAgent` for ordered generate-then-review pipelines; `LoopAgent` offered as an alternative for repeated cycles. Outputs are stored in named **state keys** (`output_key`).
- **Rule-based / test-based critics** — deterministic validators (tests, static analysis) used alongside or instead of LLM critique.

## Key Concepts
- **Producer Agent** — responsible only for the initial execution (writing code, drafting text, making a plan). Fuses entirely on generation.
- **Critic Agent** — sole purpose is evaluation. Given a distinct persona (e.g., "senior software engineer," "meticulous fact-checker") and criteria; designed to find flaws and return structured feedback.
- **Persona / role separation** — the critic uses a different system prompt or agent identity to approach the output fresh, reducing the "cognitive bias" of reviewing one's own work.
- **Critique** — specific findings tied to acceptance criteria, often a bulleted list, or a sentinel phrase such as `CODE_IS_PERFECT` when no issues remain.
- **Refinement** — a revision that addresses the findings without introducing regressions; the new version is fed back into history.
- **Stopping condition** — ends the loop, e.g., critic declares the output perfect, a quality threshold is met, or a maximum iteration count is reached.
- **Iteration budget** — a hard cap on critique/refine cycles to bound cost and latency.
- **Evaluator independence** — separation of producer and critic enhances objectivity and enables specialized, structured feedback.
- **Conversation history / memory** — the running context (task, prior code, critiques, refinements) passed into each step so generation and evaluation stay grounded.
- **State keys / state management** — named slots (e.g., `draft_text`, `review_output`) that carry artifacts between agents across iterations.
- **Structured critic output** — the critic may emit a fixed schema (e.g., a dictionary with `status` ∈ {"ACCURATE","INACCURATE"} and `reasoning`) so the producer can parse feedback deterministically.
- **Meta-cognition** — reflection adds a layer of the agent observing and adjusting its own process.

## Mental Models
Reflection is **quality control, not endless deliberation** — a bounded loop, not an excuse to keep revising. The best critic is often a *different* role, model, rule set, or test suite. A key mental model is separation of concerns: creation and evaluation are deliberately split so the producer isn't its own most lenient reviewer. Another is that reflection is a *corrective engine* — it compares current output against a benchmark and closes the gap.

## Anti-patterns / Failure Modes
- **Unbounded loop** — no iteration budget inflates cost/latency and can oscillate between versions.
- **Vague self-critique** — without explicit criteria, the model produces generic praise or unfocused edits ("try harder").
- **Critique without criteria** — cannot distinguish preference from defect.
- **Critic replacing execution** — the critic should not be the judge of correctness for deterministic properties; tests and external evidence decide.
- **Context bloat** — each iteration expands history (output + critique + refinement), risking context-window overflow and API throttling.
- **Single-pass fallacy** — assuming one generate-critique cycle is enough for high-stakes or nuanced tasks.
- **Bias carryover** — self-reflection alone can repeat the same blind spots because the same model evaluates and generates.

## Implementation Sketch
```
input task + criteria
current = generate(task)
for i in 1..max_iterations:
    critique = critic(current, task, criteria)     # distinct persona/schema
    if critique == "CODE_IS_PERFECT" (or passes threshold):
        break
    current = refine(task, current, critique)      # apply feedback
    append (current, critique) to history          # preserve versions
return current
```
Framework shape (LangChain/LCEL): keep a `message_history`; iteration 0 generates from the task prompt, later iterations append "refine using the critiques" plus prior code and critique, then a `reflector_prompt` (system persona) issues the critique. Framework shape (ADK): build `LlmAgent` producers/reviewers with `output_key`s, wire them via `SequentialAgent` (generator runs first, saves to `draft_text`; reviewer reads it, saves a `status`/`reasoning` dict to `review_output`), or use `LoopAgent` for repeated cycles.

## Worked Example
**Goal:** generate a Python function `calculate_factorial(n)` that computes `n!`, includes a docstring, handles the edge case `0! == 1`, and raises `ValueError` on negative input.

- **Setup:** `ChatOpenAI(model="gpt-4o", temperature=0.1)` for deterministic output; `max_iterations = 3`; maintain a `message_history` seeded with the task.
- **Iteration 1 (Generate):** model produces initial code from the task prompt; the code is appended to history.
- **Reflect:** a `reflector_prompt` casts the model as a senior Python engineer to review against the task, returning bulleted critiques or the phrase `CODE_IS_PERFECT`.
- **Iteration 2+ (Refine):** history now holds task + last code + last critique; the model refines. The loop repeats.
- **Stop:** when critique contains `CODE_IS_PERFECT` or `max_iterations` is hit, the final refined code is returned.
- **ADK variant:** a `DraftWriter` LlmAgent produces a paragraph saved to `draft_text`; a `FactChecker` LlmAgent reads it and emits a `{status, reasoning}` dict to `review_output`, ordered by a `SequentialAgent`.

The code example demonstrates that the loop's success is judged by whether the final code actually meets requirements — ideally confirmed by running tests, not by the critic's word alone.

## Key Takeaways
1. Reflection inserts a generate → evaluate → refine feedback loop so the first output is never final.
2. The Producer–Critic model is the strongest variant: separate creation from evaluation to reduce bias and enable specialized critique.
3. Evaluation must be criterion-driven — explicit acceptance criteria, structured/sentinel critic output, and deterministic validators where possible.
4. Bound the loop with an iteration budget and a clear stopping condition to control cost, latency, and context growth.
5. Maintain conversation history so each cycle builds on the last; pair this with memory for cumulative, context-aware refinement.
6. Full iteration needs stateful orchestration (LangGraph, ADK loops); a single cycle fits simple compositional frameworks (LCEL, sequential ADK agents).
7. Benefits — higher accuracy, completeness, and adherence to complex instructions — come at the cost of extra LLM calls, latency, and context usage.
8. Use reflection when quality matters more than speed: polished long-form content, code generation/debugging, and detailed planning.

## Connects To
- **Goal setting & monitoring (Ch 11):** a goal is the benchmark for self-evaluation; reflection acts as the corrective engine using monitored feedback to detect deviations and adjust strategy.
- **Memory (Ch 8):** conversational history grounds evaluation and makes reflection cumulative rather than isolated, letting the agent avoid repeating past critiques.
- **Evaluation (Ch 19):** supplies the criteria and regression evidence that make a critic's verdict trustworthy.
- **Chaining / Routing / Parallelization:** reflection layers on top of these as a control structure, combining with them to build more robust, complex agentic systems.

*References:* "Training Language Models to Self-Correct via Reinforcement Learning" (arXiv:2409.12917); LangChain Expression Language (LCEL) docs; LangGraph docs; Google ADK multi-agent docs.
