# Chapter 19: Evaluation and Monitoring

## Core Idea
Agents are probabilistic, so a single correct final answer is not evidence of reliability. Evaluation must score the whole system—outputs, the trajectory that produced them, resource use, and safety behavior—before release, and monitoring must keep scoring them in production where data, models, and environments drift. The goal is a continuous feedback loop: define metrics, test against representative cases, ship behind comparisons and canaries, alert on anomalies, diagnose root cause, and turn every confirmed failure into a regression case.

## Frameworks Introduced
- **Trajectory evaluation**: Judge both the outcome and the sequence of decisions, tool calls, and observations. Traditional software tests give binary pass/fail; agents need qualitative assessment of how a goal was reached.
- **Two-layer test artifacts**: `test` files for single, fast, unit-level sessions, and `evalset` files for longer, multi-turn integration sessions that simulate realistic conversations.
- **LLM-as-a-Judge**: A rubric-driven model scores subjective qualities (helpfulness, clarity, neutrality) as one signal alongside deterministic tests and human review.
- **A/B and drift monitoring**: Compare agent versions in parallel and alert when live behavior or data distribution moves beyond a baseline.
- **Trajectory match metrics**: exact, in-order, any-order, precision, recall, and single-tool checks that compare actual actions against a ground-truth path.
- **Contractor model**: A shift from underspecified prompt-following agents to formalized, verifiable "contracts" with negotiation, self-validation, and subcontract decomposition for high-stakes work.

## Key Concepts
- **Quality metrics**: factual correctness, relevance, completeness, fluency, and task success.
- **Operational metrics**: latency, token and call usage, cost, availability, and resource consumption.
- **Safety and compliance metrics**: policy violations, unsafe tool actions, escalation quality, data leakage, and audit-documented adherence to rules.
- **Trajectory**: the ordered steps an agent takes; a lossy projection of reasoning that must be inspected to explain behavior.
- **Test file vs evalset**: unit-session speed versus multi-turn integration realism.
- **Drift**: degradation from concept drift (changing input distribution) or environmental shift.
- **Anomaly detection**: flagging unusual agent actions that may signal errors, attacks, or emergent behavior.
- **LLM-as-a-Judge**: consistent, scalable, human-like scoring bounded by the judge's own biases and blind spots.
- **Contract / subcontract**: formal specifications of deliverables, scope, cost, and timing that make outcomes objectively verifiable.
- **Feedback loop**: the closed cycle from measurement to correction that drives continuous improvement.

## Mental Models
- **The answer is a trace, not the truth.** A final response collapses the reasoning that produced it; inspect enough trajectory to explain why the agent acted and whether a safer path existed.
- **Baseline is a moving target.** In production the reference for "normal" constantly shifts, so monitoring must re-establish baselines and detect relative change, not just absolute thresholds.
- **More agents is not more capable.** Adding a specialist should improve the system end-to-end; if it adds handoff friction or conflicts, it is a liability, not an asset.
- **Prompt is a proposal, contract is a promise.** Brief instructions are fine for demos; production high-stakes work needs explicit, verifiable terms the agent can negotiate and self-check against.

## Anti-patterns / Failure Modes
- **Demo evaluation**: testing only easy happy paths that the prototype was built around.
- **Judge-only evaluation**: trusting a model to grade itself without anchors, rubrics, or disagreement review.
- **Metric tunnel vision**: optimizing latency or cost while silently degrading safety or correctness.
- **Exact-match tyranny**: demanding perfect trajectory matches where flexible in-order or any-order matching is appropriate.
- **Silent drift**: letting performance degrade in production because nothing alerts on the change.
- **Contract theater**: writing verbose specs the agent never re-reads or self-validates against.

## Implementation Sketch
```
define rubric + baseline metrics
  -> build representative + adversarial test/evalset files
  -> run trajectory evaluation, score quality/safety/cost
  -> compare against previous version
  -> A/B or canary in production
  -> stream latency/tokens/cost + trajectory to time-series/observability store
  -> detect anomalies and drift vs baseline
  -> alert + generate audit report
  -> diagnose root cause, fix, add regression case
  -> close the loop
```

Small illustrative metric helper (not source code):
```
def trajectory_score(actual_actions, ground_truth, match="in-order"):
    # compare the agent's tool-call sequence to the expected path
    # using exact / in-order / any-order / precision / recall semantics
    ...
    return precision, recall, match_ok
```

## Worked Example
A smart-home agent receives "Turn off device_2 in the Bedroom." A test file captures the expected trajectory: call `set_device_info` with `location: Bedroom`, `device_id: device_2`, `status: OFF`, then respond "I have set the device_2 status to off." The evaluator compares the agent's actual tool calls using in-order matching, allowing minor extra steps, and scores precision and recall of essential actions. Separately, an evalset simulates a longer session ("What can you do?" then "Roll a die twice and check if 9 is prime") to exercise multi-step integration. In production, latency, token usage, and any deviation from expected trajectories stream to a time-series store; a drift detector alerts when response quality or tool-selection patterns move beyond the baseline, and a compliance report surfaces for human review.

## Key Takeaways
1. Evaluate outputs, trajectories, resources, and safety together—never a single metric in isolation.
2. Use representative and adversarial test files for unit speed and evalsets for integration realism.
3. Combine deterministic metrics, LLM-as-a-Judge, and human review, and record judge disagreements.
4. Match trajectories with the strictness the stakes demand: exact for high-risk, flexible for tolerant tasks.
5. Ship behind A/B tests and canaries, and stream metrics and trajectories to an observability store.
6. Detect anomalies and drift against a living baseline, and alert before users notice degradation.
7. Turn every confirmed failure into a regression case, and close the feedback loop.
8. For high-stakes work, formalize deliverables as contracts the agent can negotiate and self-validate.

## Connects To
- **Ch 11 (Goal Setting & Monitoring)**: evaluation operationalizes goals into measurable, auditable criteria.
- **Ch 17 (Reasoning)**: trajectory evaluation inspects the reasoning process behind a decision, not just its result.
- **Ch 4 (Reflection)**: reflection applies evaluation criteria at runtime to self-correct.
- **Ch 9 (Adaptation)**: adaptation requires evaluation gates before changes are accepted.
- **Ch 16 (Metrics & Trade-offs)**: the quality versus cost/latency tensions this chapter monitors are the same trade-offs.
- **Production governance**: the contractor and AI-contract ideas extend here, codifying objectives, rules, and controls for delegated agentic tasks.
