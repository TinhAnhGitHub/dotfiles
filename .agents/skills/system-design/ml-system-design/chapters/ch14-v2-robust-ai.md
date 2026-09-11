# Chapter 14: Robust AI

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 14

## Core Idea
ML systems often fail silently: uptime and latency remain healthy while predictions become confidently wrong. Robust AI makes competence loss visible and bounded across environmental shifts, input-level attacks, and system-level faults, then connects each signal to a response such as monitoring, sanitization, retraining, abstention, or recovery.

## Frameworks Introduced
- **Unified Framework for Robust AI**: Treat robustness as a cross-layer property spanning model, data pipeline, runtime, hardware, and deployment. Use it when a model’s benchmark accuracy is not enough to establish recoverable production behavior.
- **Three Pillars Framework**: (1) environmental shifts—data drift, concept drift, domain/context change; (2) input-level attacks—adversarial inputs, poisoning, prompt injection; (3) system-level faults—bit flips, memory/power faults, numerical bugs, schema errors, dependency failures, and leaks. Software faults may masquerade as either of the first two.
- **Masquerade diagnosis**: Compare change boundaries, replay fixed golden inputs, and correlate with cross-layer signals. A continuous population shift differs from a step change at deployment; a hardware or numerical fault can change the answer for the same saved input.
- **Robustness response loop**: Define a detection threshold, degradation path, and adaptation mechanism, each with an explicit accuracy, compute, latency, and energy budget.

## Key Concepts
- **Distribution shift**: Production inputs differ from the reference distribution.
- **Concept drift**: The relationship between inputs and outcomes changes over time.
- **Adversarial attack**: A crafted perturbation intended to change model behavior.
- **Data poisoning**: Training samples are manipulated to alter the learned boundary.
- **Uncertainty quantification**: Signals that help the system distinguish confidence from competence.
- **Certified robustness**: A formal guarantee within a specified perturbation bound.
- **Semantic reliability**: Generative-system reliability against hallucination, ungrounded claims, or unsafe context handling.
- **Drift metrics**: Statistical measures such as PSI, KL divergence, MMD, or K-S used as evidence, not as automatic decisions.

## Mental Models
- Robustness is an immune system: it must protect the complete fleet, not only the weights.
- Diagnose before defending. The same falling-accuracy symptom can require a pipeline rollback, an attack response, or retraining.
- A clean held-out test set proves little about shifted, adversarial, or corrupted execution conditions.
- Treat uncertainty and abstention as capacity and product decisions: refusing to assert can be safer than confidently extrapolating.

## Anti-patterns
- **Equate robustness with adversarial training**: Environmental drift and system faults remain uncovered.
- **Trust a drift alert without diagnosis**: A preprocessing bug can look like covariate shift and trigger the wrong intervention.
- **Optimize clean accuracy only**: Robustness mechanisms can trade accuracy and compute for resilience; the failure consequence determines the budget.
- **Test only the model**: Schema validation, preprocessing parity, feature freshness, hardware behavior, and rollback must be tested with it.
- **Treat LLM fluency as reliability**: Hallucinations are semantic failures even when syntax, latency, and confidence appear normal.

## Worked Example
A production fraud detector’s accuracy falls while latency and uptime remain stable. First compare the production feature distribution with its reference using a calibrated distance metric and inspect whether the change is gradual. Replay a saved golden input set through the current pipeline; identical inputs producing different outputs point toward computation, numerical, hardware, or dependency faults rather than real drift. Correlate the event with a release, schema change, ECC/SDC signal, memory alarm, or unusual query pattern. If the evidence supports environmental shift, route through investigation, recalibration, or retraining thresholds; if it supports an attack, apply input defenses and adversarial evaluation; if it supports a pipeline fault, roll back and repair parity. The detector becomes robust because evidence is attached to a recovery path.

## Key Takeaways
1. Silent competence loss is the defining robustness problem.
2. The three pillars organize evidence and defenses, while software faults can masquerade across them.
3. Drift metrics matter only when calibrated to investigation, retraining, rollback, or routing.
4. Adversarial defenses, certification, uncertainty, and monitoring consume real system budgets.
5. Robustness spans the model lifecycle and the system that delivers its inputs.

## Connects To
- **Chapter 7**: Fault models and recovery provide the system-level mechanics behind masquerading failures.
- **Chapter 10**: Sharded serving and RAG create additional reliability and semantic failure modes.
- **Chapter 12**: Monitoring and rollout pipelines turn robustness signals into production action.
- **Chapter 13**: Security frames intentional threats; robustness also covers accidental and environmental stress.
