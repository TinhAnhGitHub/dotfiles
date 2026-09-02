# Chapter 17: Reasoning Techniques

## Core Idea
Many problems cannot be solved in a single forward pass. Reasoning techniques make an
agent's internal deliberation explicit so it can decompose problems, consider
intermediate steps, explore alternatives, and verify results. The unifying principle
across this chapter is **inference-time computation**: deliberately spending more
processing budget—more steps, more branches, more verification—to buy accuracy,
coherence, and robustness. The engineering tension is always the same: expose enough
structure to solve the task well, while bounding cost and resisting the temptation to
produce confident-but-false reasoning.

## Frameworks Introduced
- **Chain-of-Thought (CoT):** Guide the model to emit a sequence of intermediate
  steps instead of a single answer. Turns one hard problem into many easy ones and
  makes reasoning auditable. Trigger phrases like "think step by step" or few-shot
  step-by-step examples both work.
- **Tree-of-Thought (ToT):** Extend CoT into a search tree. Generate several candidate
  next steps, evaluate each branch, and backtrack when a path looks wrong. Use when
  strategic planning, trial-and-error, or exploration is worth the cost.
- **Self-Correction / Self-Refinement:** An internal critic reviews drafts and
  intermediate thoughts against the original requirements, flags discrepancies
  (accuracy, completeness, clarity, tone, engagement), proposes concrete fixes, and
  rewrites. A quality-control loop folded into generation.
- **ReAct (Reasoning + Acting):** Interleave reasoning with tool use in a
  Thought → Action → Observation loop. The agent reasons about which action to take,
  acts (search, API, calculation), observes the result, and updates its plan. Essential
  whenever external feedback should change the next step.
- **Program-Aided Language Models (PAL):** Offload arithmetic, logic, and data
  manipulation to executable code (e.g., Python). The model writes code, runs it, and
  turns the deterministic result into a natural-language answer. Use computation where
  LLMs are unreliable.
- **Reinforcement Learning with Verifiable Rewards (RLVR):** A training strategy behind
  modern "reasoning models." The model learns long, adaptive reasoning trajectories
  (thousands of tokens) through trial-and-error on problems with known correct answers
  (math, code), dedicating more effort to harder problems—no per-step human label.
- **Chain of Debates (CoD) / Graph of Debates (GoD):** Multi-agent collaboration. CoD
  runs diverse models that present, critique, and counter-argue like peer review. GoD
  generalizes this to a non-linear graph where arguments are nodes linked by
  "supports"/"refutes" edges; a conclusion is the best-supported cluster (ground truth,
  search-grounded evidence, or model consensus).
- **MASS (Multi-Agent System Search):** Automate MAS design by interleaving
  block-level prompt optimization, influence-weighted topology search, and
  workflow-level prompt tuning. Principle: optimize individual agents before composing
  them, compose influential topologies, then jointly tune interdependencies.
- **Inference-time scaling / Deep Research:** The Scaling Inference Law holds that a
  smaller model given a larger "thinking budget" can beat a larger model on a simpler
  generation path. Deep Research is the archetype: a time-budgeted agent that
  explores, reasons, identifies gaps, re-searches, and synthesizes a cited report.

## Key Concepts
1. **Deliberation** — extra inference spent to improve a decision.
2. **Inference-time compute** — the "thinking budget" traded for quality.
3. **Branch** — one candidate reasoning path (ToT/graph).
4. **Observation** — an external result (tool output, test, search) that updates state.
5. **Reasoning trajectory** — the full sequence of thoughts an agent produces.
6. **Backtracking** — abandoning a branch after evaluation.
7. **Verifiable reward** — a reward from an objective check (test, proof, answer key).
8. **Topology** — the interaction structure between agents in a MAS.
9. **Search grounding** — validating claims against external sources.
10. **Consensus** — agreement across models or candidates as evidence.
11. **Thinking budget** — the cap on steps, branches, or latency you allow.
12. **Thought-action-observation loop** — the core ReAct cycle.

## Mental Models
- **CoT** = internal monologue that makes a plan explicit.
- **ToT** = deliberate search with evaluation and backtracking.
- **ReAct** = reasoning under feedback; act when the world should steer you.
- **PAL/RLVR** = verify with computation, not intuition.
- **Debate/GoD** = truth via adversarial multi-agent scrutiny.
- **MASS** = design teams like an optimization problem, not a handcraft.
- **Scaling Inference Law** = often spend more compute on a smaller model rather than
  upgrade the model itself.

## Anti-patterns / Failure Modes
- **Reasoning theater** — long, confident explanations that add no evidence or better
  decisions.
- **Unbounded search/debate** — branching or arguing without a stopping criterion,
  multiplying cost linearly or worse.
- **Model-only arithmetic and facts** — trusting the LLM to compute or recall what a
  tool or authoritative source can verify.
- **Consensus hallucination** — assuming multiple agreeing paths are correct when they
  may share the same error.
- **Over-deliberation** — spending far more budget than the task's difficulty warrants.
- **Handcrafted MAS** — composing agents without optimizing prompts or topology, leaving
  compounding misconfiguration.

## Implementation Sketch
```
if task needs external feedback:   # ReAct / Deep Research
    loop: thought -> tool action -> observation -> thought ... until "finish"
elif task has many viable paths:   # ToT / debate / self-consistency
    generate branches, evaluate, backtrack, aggregate within budget
else:                              # CoT for single-pass multi-step
    emit step-by-step rationale

if task is computational/verifiable: # PAL / RLVR-style checks
    generate code, execute, assert, then answer
always: bound branches, iterations, and thinking budget; verify before trusting
```

## Worked Example
**Explain classical vs. quantum computers and one application.**
- *CoT:* a five-step process (analyze query → formulate search queries → simulate
  retrieval → synthesize → review) produces an auditable chain ending in a clean answer
  covering bits vs. qubits, superposition/entanglement, and a drug-discovery application.
- *Self-correction pass:* the same reviewer pattern applied to a weak draft tweet
  ("We have new products...") identifies low engagement and a vague call to action, then
  rewrites it into a polished, within-limit post.
- *PAL:* for a math subproblem the agent emits Python, executes it, and reports the
  computed result rather than guessing.
- *Deep Research:* a time-budgeted agent runs initial searches, detects a contradiction
  in the sources, re-searches to resolve it, and compiles a cited report.

## Key Takeaways
1. Reasoning techniques spend inference-time compute to decompose, explore, and verify.
2. CoT is the default starting point; layer ToT, ReAct, PAL, or debate as the task
   demands exploration, feedback, or computation.
3. Bound every deliberation loop—branches, iterations, and thinking budget.
4. Verify with verifiable rewards: executable code, tests, sources, or answer keys.
5. Show the "work" when auditability matters, but keep internal deliberation distinct
   from the user-facing summary.
6. Prefer a well-instructed smaller model with a large thinking budget over a bigger
   model that generates on a single path (Scaling Inference Law).
7. Build multi-agent teams by optimizing prompts and topology, not by hand arrangement.

## Connects To
- **Ch 4:** Self-correction and reflection evaluate and refine outputs.
- **Ch 5:** Tool observations supply the feedback ReAct relies on.
- **Ch 19:** Compare reasoning trajectories empirically to pick the best technique.
- **Chapter on MAS (MASS):** automates multi-agent design and topology.
- References: Wei et al. 2022 (CoT); Yao et al. 2023 (ToT, ReAct); Gao et al. 2023
  (PAL); Inference Scaling Laws 2024; Multi-Agent Design / MASS (arXiv 2502.02533).
