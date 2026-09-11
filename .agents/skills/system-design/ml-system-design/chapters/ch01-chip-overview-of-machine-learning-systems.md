# Chapter 1: Overview of Machine Learning Systems

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 1

## Core Idea

A production ML system is much larger than its algorithm. It joins business requirements, users and stakeholders, data collection and processing, model development, serving infrastructure, monitoring, and updating logic. ML is a good fit when a problem requires predictions learned from existing data: the patterns are complex enough that hand-written rules are unattractive, the future inputs share patterns with historical inputs, and predictions can be made repeatedly at useful scale. It is not magic, and a lookup table, ordinary software, or a human process may be cheaper and better.

## Frameworks Introduced

Huyen’s practical test for using ML is: can the system learn complex patterns from existing data to predict outcomes for unseen data? The useful-case checklist adds repetition, relatively tolerable error costs, scale, and changing patterns. The production-versus-research comparison highlights different stakeholders, inference latency, shifting data, fairness, and interpretability. The ML system is also framed as code plus data plus artifacts, rather than code alone.

## Key Concepts

Consumer examples include search, recommendation, predictive typing, translation, assistants, authentication, and health monitoring. Enterprise applications include fraud detection, price and demand optimization, acquisition and churn prediction, ticket routing, brand monitoring, and clinical support. Enterprise use often tolerates more latency but demands precise improvements because small efficiency gains can have large financial effects.

Research commonly optimizes benchmark performance and training throughput. Production must reconcile conflicting objectives: a recommendation can maximize clicks, revenue, or quality, while product teams may require a strict latency target and platform teams may prioritize reliability. Inference is usually the production bottleneck. Latency is a distribution, so p50, p90, p95, and p99 reveal behavior that an average can hide. Production data is noisy, biased, privacy-sensitive, sparse or incorrect in labels, and continuously generated.

Fairness and interpretability cannot be postponed until deployment. Historical data can encode and scale discrimination, while explanations help users trust decisions and developers debug them. Unlike traditional software, ML requires testing and versioning data and artifacts as well as code; large models and silent failures add operational difficulty.

## Mental Models

Think “system, not model.” Think of an ML project as a feedback loop: data, training, deployment, observations, and new data continually influence one another. Think of production constraints as first-class model inputs. A model that wins a static leaderboard but is too slow, opaque, costly, stale, or unfair is not a successful system.

## Anti-patterns

- Starting ML because it is fashionable when a simpler solution works.
- Treating benchmark or state-of-the-art performance as production fitness.
- Optimizing average latency while ignoring tail latency.
- Treating data as clean, stationary, representative, or automatically private.
- Assuming a correct `predict` call means correct predictions.
- Deferring fairness, interpretability, monitoring, or artifact management.

## Worked Example

For restaurant recommendations, an ML engineer may favor a complex model for click likelihood, sales may favor expensive restaurants, product may require under 100 ms, and the platform team may need fewer updates while it fixes scaling. The design must identify which constraints are mandatory, compare model complexity with latency and explanation needs, and evaluate business impact rather than selecting an algorithm in isolation.

## Key Takeaways

Use ML when learned prediction is genuinely needed and economically justified. Design the entire socio-technical system, not merely a model. Expect changing data, silent failure, and ongoing maintenance. Include fairness, interpretability, latency distributions, reliability, and reproducibility in the definition of quality.

## Connects To

Chapter 2 turns this overview into objectives, requirements, problem framing, and an iterative design process. Chapters 3–6 develop the data, training-data, feature, and model foundations; later chapters address serving, monitoring, continual learning, and responsible AI.
