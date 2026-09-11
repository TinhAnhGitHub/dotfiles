# Chapter 2: ML Systems

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 2

## Core Idea
Deployment is a physical design choice. Cloud, Edge, Mobile, and TinyML systems occupy different power, memory, bandwidth, latency, and connectivity envelopes, so the same model can be feasible in one paradigm and unusable in another.

## Frameworks Introduced
- **Deployment Paradigm Framework**: Choose among Cloud, Edge, Mobile, and TinyML by matching workload demands to the hardware and operational envelope.
- **Bottleneck Principle**: Identify whether compute, memory bandwidth, network transit, power, or fixed latency is limiting before optimizing.
- **Hybrid ML**: Distribute stages across tiers according to each stage’s latency, compute, data-locality, and operational constraints.
- **System Entropy**: Deployment does not freeze behavior; live data, traffic, and environments create continuing divergence that must be observed and managed.

## Key Concepts
- **Single-node stack**: A local anchor for reasoning about silicon, memory hierarchy, operating system, runtime, and model execution.
- **Cloud ML**: Elastic, centralized infrastructure suited to large-scale training and high aggregate throughput.
- **Edge ML**: Local inference near sensors or users, reducing network latency and preserving data locality.
- **Mobile ML**: On-device intelligence constrained by battery, thermal capacity, memory, and offline operation.
- **TinyML**: ML on microcontrollers and similarly constrained devices, often for always-on sensing.
- **Workload archetype**: A recurring resource profile such as Compute Beast, Bandwidth Hog, or Tiny Constraint.
- **Data locality invariant**: Moving data to computation can be more expensive than computing locally.

## Mental Models
Use the deployment paradigm as an early feasibility filter, not as a hosting preference. Read the Iron Law through the target: cloud emphasizes aggregate compute and throughput, edge emphasizes deterministic latency and locality, mobile emphasizes memory and energy, and TinyML emphasizes milliwatt operation and tiny memory. Treat a hybrid system as a placement problem: put frequent or latency-critical work close to the data and elastic work where capacity is abundant.

## Anti-patterns
- **“Cloud means unlimited compute”**: Network propagation, bandwidth, quotas, cost, and service contention remain hard constraints.
- **Latency-only analysis**: A model that meets compute latency can still fail because data transfer, preprocessing, or serialization dominates.
- **Shrinking a cloud model blindly**: A lower-power tier may require a different architecture, precision, data path, or operating policy.
- **Scaling before profiling**: Adding devices can replace compute pressure with communication and synchronization pressure.
- **Ignoring deployment entropy**: A system can drift after launch while infrastructure dashboards remain green.

## Worked Example
A voice assistant illustrates a three-tier hybrid. TinyML performs always-on wake-word detection locally, mobile hardware handles speech recognition, and cloud infrastructure performs complex language understanding. This split preserves privacy and responsiveness for the trigger, uses offline-capable device resources for the middle stage, and reserves elastic cloud compute for the most expensive stage. The train-serve split, hierarchical processing, and progressive deployment patterns generalize the same placement logic.

## Key Takeaways
1. Measure the binding resource before selecting a deployment target.
2. Physical laws constrain feasibility; architecture cannot repeal propagation, memory, or power limits.
3. Match workload archetypes to paradigms rather than applying one optimization everywhere.
4. Use fast local links for frequent communication and remote tiers for work that tolerates latency.
5. Make monitoring part of deployment because operational conditions evolve.

## Connects To
- **Chapter 1**: Applies the Iron Law and D·A·M diagnosis to physical deployment.
- **Chapter 3**: Carries deployment requirements backward through the ML lifecycle.
- **Chapter 6**: Architecture families encode different memory, compute, and latency commitments.
- **Chapter 8**: Training parallelism confronts the same communication and capacity walls.
