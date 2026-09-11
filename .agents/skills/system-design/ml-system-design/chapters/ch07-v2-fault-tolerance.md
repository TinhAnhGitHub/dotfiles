# Chapter 7: Fault Tolerance

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 7

## Core Idea

At fleet scale, failures are continuous rather than exceptional. Reliability engineering must classify faults, detect both crashes and silent corruption, preserve distributed state, and resume useful work without making recovery more expensive than the failure. The system should convert failure from a total restart into bounded lost work or graceful degradation.

## Frameworks Introduced

- **Failure taxonomy**: Transient, intermittent, permanent, fail-stop, Byzantine/silent, and correlated failures differ in duration, observability, and blast radius. Use the type and failure domain to select detection and recovery.
- **Failure domains**: GPU, node, rack, power, network, and facility boundaries determine whether redundancy is genuinely independent. Place replicas and spares across domains, not merely on different devices.
- **Young-Daly checkpoint trade-off**: Checkpoint interval balances write overhead against expected rework after a failure. Use system MTBF and actual checkpoint write time; do not treat cadence as arbitrary.
- **Check-and-verify**: Layer checksums, invariants, validation, and canary work to catch silent data corruption that does not produce a crash.
- **Elastic recovery**: Replace failed capacity and resume with fewer or different workers when the training framework supports repartitioning. Use it to turn hard failure into a throughput reduction.

## Key Concepts

- **MTBF/MTTF**: Mean time between failures or mean time to failure for a component or system.
- **Fail-stop**: A worker ceases participation and is detectable.
- **Silent Data Corruption (SDC)**: Incorrect state that continues through the system without an obvious error.
- **Checkpoint**: A serialized, consistent snapshot of model, optimizer, and execution state.
- **Checkpoint storm**: Synchronized fleet-wide checkpoint I/O burst.
- **Hot spare**: Reserved capacity used to replace a failing component quickly.
- **Straggler**: A slow participant that remains alive but holds back synchronous peers.
- **Graceful degradation**: A service continues with reduced capability instead of failing completely.

## Mental Models

Think in failure rate multiplied by component count: “rare” per-device events become routine fleet events. Treat a checkpoint as a distributed protocol, not a file write: workers reach a consistent point, write shards, confirm, and publish metadata. Use redundancy only across independent failure domains. Separate training recovery—which protects progress—from serving resilience—which protects availability and quality.

## Anti-patterns

- **Assuming independent, fail-free components**: Underestimates correlated rack, power, network, and software failures.
- **Checkpointing by wall-clock habit**: Ignores write duration, system MTBF, model state, and lost-work cost.
- **Crash-only recovery**: Restarts without state validation, communicator re-formation, or data-loader position recovery.
- **No SDC defense**: Equates absence of an error signal with correctness.
- **Unlimited retries**: Converts a bad node or software fault into repeated wasted work and fleet-wide instability.

## Worked Example

A recovery coordinator broadcasts a checkpoint ID, waits for workers to reach a consistent barrier, and has each rank write its state shard. After all confirmations, it publishes checkpoint metadata and announces completion. If a node later fails, surviving workers are terminated or paused coherently, the failed node is drained, replacement containers launch, shards reload, ranks establish a new communicator, and the loader fast-forwards to the saved batch. A canary batch then checks that loss and invariants are plausible before full training resumes. This sequence bounds both corruption risk and duplicated work.

## Key Takeaways

1. Model failure frequency at system scale and map correlated domains explicitly.
2. Detect silent corruption with independent checks and validation.
3. Choose checkpoint cadence from write cost, MTBF, and rework economics.
4. Make recovery stateful, coordinated, validated, and capable of elastic continuation.
5. Treat stragglers and graceful degradation as reliability problems, not only performance problems.

## Connects To

- **Chapter 4**: Storage hierarchy and staged writes determine checkpoint cost.
- **Chapter 5**: Distributed state, barriers, and data position must be restored consistently.
- **Chapter 6**: A failed rank can break collectives and require communicator recovery.
- **Chapter 8**: Orchestrators drain unhealthy nodes and reschedule jobs.
