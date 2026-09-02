# Chapter 9: Learning and Adaptation

## Core Idea
Agents get better at what they do by changing their thinking, actions, or knowledge from experience and data — moving from static instruction-followers to systems that improve over time. Adaptation is the *observable* change in behavior or knowledge that results from learning. But adaptation is not automatically good: it can produce drift, reward hacking, or unsafe behavior, so every learning loop must be measured, gated, and reversible.

## Frameworks Introduced
- **Six learning modes:** Reinforcement Learning (RL), Supervised Learning (SL), Unsupervised Learning (UL), Few-/Zero-Shot adaptation with LLMs, Online (streaming) learning, and Memory-based learning. Each suits different environments and update cadences.
- **Policy-alignment methods:** RLHF (two-step: train a reward model from human comparisons, then optimize the policy with PPO) vs. DPO (skip the reward model and optimize the policy directly on preference data).
- **Self-improvement loops:** an agent that modifies its own source code and is scored against a benchmark archive (SICA), and evolutionary agents that mutate and select whole programs or algorithms (AlphaEvolve, OpenEvolve).
- **Safe learning pipeline:** collect trajectories → evaluate → candidate update → safety + regression gating → canary → monitor → promote or rollback.

## Key Concepts
1. **Policy** — the agent's decision-making strategy mapping states to actions. Learning = improving the policy.
2. **Reward / feedback signal** — a scalar or comparison indicating outcome quality; the compass for all learning loops.
3. **Reinforcement Learning** — try actions, receive rewards and penalties, learn optimal behavior in changing environments (robots, games).
4. **Supervised / Unsupervised Learning** — map labeled inputs to outputs (classification, prediction) vs. discover hidden structure in unlabeled data (organization, mental maps).
5. **Few-/Zero-Shot adaptation** — LLMs pick up new tasks from a handful of examples or plain instructions, enabling rapid response without retraining.
6. **Online learning** — continuously update on incoming data streams for real-time adaptation.
7. **Memory-based learning** — recall past experiences to adjust current actions in similar situations.
8. **PPO (Proximal Policy Optimization)** — stable RL that makes small, careful policy updates using a *clipped* objective that creates a trust region, preventing the huge risky steps that collapse training.
9. **RLHF** — align an LLM via a learned reward model (from "A better than B" comparisons) optimized with PPO; powerful but complex and unstable.
10. **DPO (Direct Preference Optimization)** — directly optimize the policy on preference data, removing the reward model; simpler and more robust, though it trades some flexibility.
11. **Reward hacking** — the agent exploits a loophole in the reward/eval rather than solving the real task.
12. **Drift** — behavior gradually moving away from intended performance after repeated updates.

## Mental Models
- **Learning is a deployment pipeline, not a runtime reflex.** Treat it as a gated loop with regression tests and rollback, not an unconditional self-edit.
- **Prefer reversible updates first.** Shift routing, prompts, and memory before policy fine-tuning; favor DPO-style direct optimization before heavy PPO reward-model stacks.
- **The eval is the environment.** In evolutionary and self-improving agents, a faithful, hard-to-game evaluation is the entire system — a weak eval produces weak (or hostile) evolution.
- **Small steps survive.** PPO's clipping mirrors good practice: incremental, verified changes beat big autonomous rewrites.

## Anti-patterns / Failure Modes
- **Optimize a proxy metric** — invites reward hacking; the agent maximizes the score, not the goal.
- **Learn from untrusted or noisy feedback** — teaches malicious or degenerate behavior.
- **Self-modify in production without a sandbox** — removes the ability to diagnose, isolate, and recover (SICA runs fully inside a Docker container to contain this risk).
- **Unbounded iteration in self-improvement loops** — stagnation, runaway loops, or compounding errors; needs an overseer to halt.
- **Confusing one improved result (reflection) with changed future behavior (learning).**

## Implementation Sketch
A generic learning loop:

```
loop:
  1. collect trajectories + outcomes (state, action, reward / preference pairs)
  2. evaluate with a faithful, hard-to-game harness; score on multiple objectives
  3. propose a candidate update (prompt, memory, policy, or code)
  4. gate: safety review + regression suite (old AND new cases)
  5. deploy to a canary; monitor for drift and reward hacking
  6. promote to production, or rollback to the known-good version
```

For preference alignment, choose **RLHF** when you need flexible, reward-driven control and can tolerate reward-model training, or **DPO** when you want a simpler, more stable direct optimization on "A vs. B" data.

## Worked Example
**SICA (Self-Improving Coding Agent)** modifies its own code each iteration: it reviews an archive of past versions and benchmark scores (weighted by success, time, and cost), picks the best version, analyzes the archive for improvement ideas, edits its own codebase, re-runs the benchmarks, and records the result. Across iterations it autonomously invented a "Smart Editor," a "Diff-Enhanced Smart Editor," an "AST Symbol Locator," and a "Hybrid Symbol Locator." An asynchronous LLM **overseer** watches the callgraph and event stream to catch loops or stagnation and can halt execution. Result: real gains in code editing and navigation without traditional training — but the initial weakness (the LLM struggled to *propose* genuinely novel, feasible modifications) exposes the open problem of authentic creativity in self-improvement.

**AlphaEvolve / OpenEvolve** generalize this: an LLM ensemble (e.g., Gemini Flash for proposals, Pro for refinement) generates algorithm candidates, an automated evaluator scores them, and an evolutionary framework iteratively improves solutions. Reported wins include a 0.7% reduction in global data-center compute, faster Gemini kernels and FlashAttention GPU instructions, and new matrix-multiplication algorithms. OpenEvolve evolves *whole files* across languages with multi-objective and distributed evaluation.

## Key Takeaways
1. Match the learning mode to the environment: RL for action-in-environment, SL for labeled mapping, UL for structure, few/zero-shot for speed, online/memory for continuous and context-aware adaptation.
2. Alignment: DPO is usually simpler and more stable than PPO-based RLHF; pick based on how much reward-model flexibility you truly need.
3. Keep learning loops measured, gated, and reversible — regression tests, canaries, and rollback are non-negotiable.
4. Protect the eval: a faithful, hard-to-game evaluation is what makes evolution and self-improvement safe and useful.
5. Constrain self-modification: sandbox it, version it, and monitor it (an overseer prevents runaway loops).
6. Watch for drift and reward hacking after every update; evaluate against both old and new cases.
7. Self-improvement is powerful but still limited by an agent's ability to propose genuinely novel, feasible changes.

## Connects To
- **Reflection vs. learning:** reflection improves one result; learning changes future behavior across results.
- **Evaluation (Ch 19):** the eval harness determines whether adaptation actually helped or just gamed a metric.
- **Guardrails:** safety constraints must not be learned away by the optimization loop.
- **Multi-agent coordination:** tuning data must capture full interaction trajectories across all agents so the whole system improves coherently.
- **RAG / knowledge bases (Ch 14):** memory-based learning lets agents store and reuse proven solutions to new problems.
