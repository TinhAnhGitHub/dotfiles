# Chapter 3: ML Workflow

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 3

## Core Idea
The ML lifecycle is a feedback loop, not a checklist. Problem definition, data collection and preparation, model development, evaluation, deployment, and monitoring are coupled stages whose contracts and evidence must flow in both directions.

## Frameworks Introduced
- **ML Lifecycle**: Move from problem definition through data, model, evaluation, deployment, and monitoring, with feedback returning to earlier stages.
- **Constraint Propagation Principle**: A late-discovered constraint can force rework across dependent stages; discover latency, memory, safety, and validation limits early.
- **Stage Contracts**: Define each stage’s inputs, outputs, quality invariants, and acceptance conditions so local work composes into a system.
- **Systems Thinking**: Reason about data, algorithm, machine, people, and production context together rather than optimizing a single stage.

## Key Concepts
- **Problem definition**: A measurable task specification including target behavior, users, risks, constraints, and success thresholds.
- **Data collection**: Gathering evidence that covers the operating population and relevant field conditions.
- **Reproducibility**: The ability to reconstruct a model from versioned data, code, configuration, and environment.
- **Offline evaluation**: Testing against held-out data before exposing a model to users.
- **Online evaluation**: Measuring behavior under real traffic and production conditions.
- **Training-serving skew**: A mismatch between transformations or assumptions used in training and serving.
- **Production feedback**: Operational evidence that triggers investigation, retraining, or requirement revision.

## Mental Models
Treat a workflow as D·A·M coupling unfolding through time. Use requirements as backward constraints: deployment latency and safety obligations should influence data collection and model choices before implementation hardens. Separate clocks for feedback: real-time monitoring catches immediate failures, batch reviews evaluate outcomes, and slower architectural reviews address durable changes. Regard iteration velocity as search capacity, but never confuse faster experiments with guaranteed quality.

## Anti-patterns
- **Linear-pipeline thinking**: A deployment failure often originates in data, evaluation, or an unstated requirement and must travel backward.
- **Late constraint discovery**: Waiting until integration to test memory, latency, or regulatory requirements multiplies rework.
- **Accuracy-only evaluation**: A single aggregate metric can hide calibration, subgroup, robustness, or production-condition failures.
- **Unversioned experiments**: Without data, configuration, and environment lineage, a successful result cannot be reliably reproduced.
- **One feedback clock**: Reacting to every signal at the same cadence either misses drift or creates needless churn.

## Worked Example
Consider a diabetic-retinopathy screening system. The team first defines a clinically meaningful decision and acceptable error trade-offs, then collects representative images across devices and populations. Model development produces reproducible artifacts; evaluation checks held-out and production-like images, not just a convenient benchmark. Deployment begins as a bounded pilot with explicit latency and safety requirements. Monitoring watches input quality, outcome proxies, and subgroup behavior. A degradation signal sends the team back to collection or labeling rather than prompting an automatic model-only patch.

## Key Takeaways
1. Write the problem and operating constraints before choosing a model.
2. Establish stage contracts and lineage so feedback is actionable.
3. Validate under production conditions and use pilots to bound exposure.
4. Monitor behavior, inputs, and outcomes on appropriate timescales.
5. Expect iteration across data, model, infrastructure, and requirements.

## Connects To
- **Chapter 2**: Deployment paradigms supply the physical requirements that propagate backward.
- **Chapter 4**: Data acquisition, labeling, and health checks implement the data pipeline.
- **Chapter 7**: Framework choices affect reproducibility, execution, and deployment artifacts.
- **Chapter 14**: Later operational practices extend monitoring and maintenance.
