# Chapter 1: Introduction

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 1

## Core Idea
An ML system must make learned behavior trustworthy while delivering it within physical, economic, and operational limits. The model is only one part of a continuously changing system whose data, algorithm, machine, and feedback loops must be co-designed.

## Frameworks Introduced
- **D·A·M Taxonomy**: Diagnose a binding constraint on the Data, Algorithm, or Machine axis; measure again after every intervention because bottlenecks migrate.
- **Iron Law of ML Systems**: Treat execution time as the combined cost of moving data, performing computation, and fixed latency or orchestration overhead. Optimize the term that actually dominates the critical path.
- **Five-Pillar Framework**: Organize production responsibility around Data Engineering, Training Systems, Deployment Infrastructure, Operations & Monitoring, and Ethics & Governance.
- **Bitter Lesson**: General methods that exploit scalable computation tend to win over hand-crafted domain-specific systems, but only when data, algorithms, and machines can support the scale.

## Key Concepts
- **ML system**: Software whose core behavior is determined by parameters learned from data rather than explicitly programmed rules.
- **Data-centric paradigm**: Improving data quality, coverage, and relevance can be as consequential as changing the model.
- **Silent degradation**: Performance can decline as the world shifts even when code and weights remain unchanged.
- **AI engineering**: Holding statistically evaluated behavior to deterministic reliability targets across the D·A·M axes.
- **Lighthouse models**: Canonical workloads used to expose recurring system bottlenecks.
- **Conservation of Complexity**: Simplifying one D·A·M domain often moves work or constraints into another.

## Mental Models
Think of ML as “Software 2.0”: code specifies the learning procedure, while data helps specify the behavior. Use D·A·M when a symptom such as poor accuracy or missed latency could have several causes. Use the Iron Law before optimizing a component; a faster model is irrelevant if preprocessing or postprocessing dominates. Treat deployment as the beginning of a feedback cycle, not a finish line.

## Anti-patterns
- **Model-as-system thinking**: Improving architecture while ignoring data pipelines, serving, monitoring, or governance leaves the actual failure surface untouched.
- **Benchmark worship**: High test accuracy does not establish production readiness under distribution shift, subgroup differences, or device limits.
- **One-time deployment**: Fixed code and weights do not guarantee fixed behavior; live inputs can move away from training conditions.
- **Local optimization**: A component-level speedup can produce little end-to-end gain when another term binds.

## Worked Example
A pipeline has 60 ms of preprocessing, 45 ms of model inference, and 25 ms of postprocessing. Reducing inference to 15 ms lowers total latency from 130 ms to 100 ms: useful, but only a 23 percent system improvement rather than a 67 percent model improvement. The example makes the Iron Law and Amdahl-style reasoning operational: profile the complete path, then optimize the largest remaining term.

## Key Takeaways
1. Ask which D·A·M axis currently binds before choosing an intervention.
2. Treat datasets as behavior-defining artifacts requiring versioning, tests, and review.
3. Use the Iron Law to separate movement, compute, and orchestration costs.
4. Design for monitoring, iteration, reliability, and governance from the start.
5. Prefer scalable methods, but evaluate them inside real deployment budgets.

## Connects To
- **Chapter 2**: Maps physical constraints to Cloud, Edge, Mobile, and TinyML deployment paradigms.
- **Chapter 3**: Turns continuous co-design into a lifecycle and feedback workflow.
- **Chapter 4**: Develops Data as the first D·A·M axis and the source-code principle.
- **Chapters 5–8**: Build the algorithm, architecture, framework, and training layers.
