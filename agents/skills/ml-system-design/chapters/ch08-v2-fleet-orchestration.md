# Chapter 8: Fleet Orchestration

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 8

## Core Idea

Fleet orchestration converts scarce, heterogeneous accelerators into useful progress. Scheduling must reconcile throughput, fairness, latency, cost, multi-dimensional packing, gang semantics, failures, and topology. The scheduler is not merely assigning GPU counts: it is selecting a connected, healthy, time-bounded placement that the distributed job can actually use.

## Frameworks Introduced

- **Scheduling objective trade-off**: Throughput, fairness, latency, and cost cannot all be maximized simultaneously. Use explicit QoS classes and policy rather than hiding the trade-off in defaults.
- **Multi-dimensional bin packing**: A job consumes GPUs plus CPU, memory, local storage, bandwidth, and topology. Use first-fit/best-fit heuristics, backfill, and defragmentation while watching for stranded capacity.
- **Gang scheduling**: Allocate all mutually dependent workers together. Use it for BSP training to prevent hold-and-wait deadlock and GPUs doing no useful work.
- **Slurm/Kubernetes paradigms**: Slurm provides HPC-oriented allocation and fair share; Kubernetes provides declarative reconciliation, containers, and an extensible operator ecosystem. Use a hybrid when training and serving have different control-plane needs.
- **Topology-aware scheduling**: Model GPUs as a hierarchical graph—node, rack, rail, and pod—and score placements by communication cost. Use it when collectives or tensor parallelism are locality-sensitive.
- **Elastic scheduling**: Admit a job at a feasible minimum and resize it when marginal throughput justifies transition cost. Use framework support such as TorchElastic rather than assuming elasticity is automatic.

## Key Concepts

- **Fragmentation**: Free resources exist but not in a shape any pending job can use.
- **Backfill**: Run smaller jobs in gaps while preserving a larger job’s reserved start opportunity.
- **Priority inversion**: Low-priority allocations block higher-priority work or prevent useful progress.
- **Dominant Resource Fairness**: Equalize each user’s largest normalized share across resource types.
- **Failure-aware placement**: Avoid unhealthy or correlated failure domains.
- **Rail-optimized placement**: Align communication groups with corresponding network rails.
- **Utilization wall**: Queue wait rises sharply as a heavily tailed ML cluster approaches high utilization.
- **Over-subscription**: Admit work based on statistically nonpeak demand, with risk of contention and thrashing.

## Mental Models

Think of a job request as a shape, not a number. A request for four GPUs with NVLink connectivity is not satisfied by any four free GPUs. Think of gang scheduling as deadlock prevention. Treat topology as a weighted placement cost and failures as changing graph state. For elasticity, compare marginal useful work with resize and re-sharding cost; vacancy alone is not a reason to scale up.

## Anti-patterns

- **GPU-count-only allocation**: Ignores CPU, memory, local cache, bandwidth, and connectivity.
- **Partial synchronous allocation**: Lets jobs hold resources while waiting for the rest, producing distributed deadlock and zero progress.
- **Strict priority without progress policy**: Causes priority inversion, starvation, or idle fragmentation.
- **Topology-unaware placement**: Scatters tensor or collective groups across expensive bandwidth cliffs.
- **Aggressive over-subscription**: Treats average utilization as a guarantee and triggers simultaneous peak contention.
- **Elasticity by vacancy**: Resizes too often or without amortizing transition overhead.

## Worked Example

Suppose a large BSP job needs a contiguous, topology-compatible group while small jobs occupy partial nodes. A scheduler can reserve the large job’s start time, backfill only work that will finish before it, and periodically defragment by preempting lower-priority jobs with checkpoint support. When placement candidates exist, score them by node/rack/rail distance so high-frequency traffic stays local. If a smaller allocation can start immediately, compare its completed work with the expected work from waiting for the full group. This policy makes throughput, latency, fairness, and preemption cost visible rather than accidental.

## Key Takeaways

1. Schedule complete resource shapes with connectivity and failure domains.
2. Make objective trade-offs explicit through QoS and fair-share policy.
3. Use gang semantics for tightly coupled training and backfill safely.
4. Preserve topology locality for collectives; treat elasticity as an economic decision.
5. Measure stranded capacity and queue behavior, not aggregate allocation alone.

## Connects To

- **Chapter 3**: Network topology and rails define placement cost.
- **Chapter 5**: Parallelism determines gang shape and elastic constraints.
- **Chapter 7**: Recovery drains failed nodes and depends on checkpoint state.
- **Chapter 9**: Scheduler placement and utilization are part of measured performance.
