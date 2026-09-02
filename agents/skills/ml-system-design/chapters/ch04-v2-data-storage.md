# Chapter 4: Data Storage

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 4

## Core Idea

Storage is the training fuel line: a tiered path must deliver data, transformations, and checkpoints at the rate demanded by accelerators. Capacity alone is not enough. Format, locality, prefetching, metadata behavior, CPU decode, network variance, durability, and cost determine whether GPUs compute or wait.

## Frameworks Introduced

- **Storage hierarchy**: Host DRAM, local NVMe, parallel file systems, object storage, and archive form tiers with different bandwidth, latency, capacity, and cost. Use hot tiers for active data and colder tiers for durable, infrequent access.
- **Data pipeline equation**: Required I/O grows with GPU count, target utilization, data volume per batch, and iteration cadence. Use it before scaling compute to test whether the fuel line can keep up.
- **Data stall ratio**: Measure time or capacity lost when input preparation cannot feed the accelerator. Use it to distinguish a storage bottleneck from a compute bottleneck.
- **Storage cost iceberg**: Raw $/GB hides egress, operations, duplication, metadata, data movement, and the opportunity cost of idle accelerators.
- **Checkpoint Storm**: Synchronous writes from many workers create periodic bursts unlike ordinary stochastic I/O. Use tiered staging and asynchronous durable copy to reduce critical-path pause.

## Key Concepts

- **Warm cache**: Local NVMe copy of frequently reread distributed data.
- **Parallel file system (PFS)**: Distributed storage separating metadata and object/data paths for aggregate bandwidth.
- **Small-file problem**: Per-file metadata and random I/O dominate when samples are not packed into large sequential containers.
- **Data loader pipeline**: Read, decode, augment, and collate stages feeding batches.
- **Prefetching**: Preparing future batches while the GPU processes the current batch.
- **GPUDirect Storage (GDS)**: A path that bypasses host-memory copies between storage and GPU memory.
- **Data locality**: Placement of shards near the workers that consume them.
- **Synthetic fuel line**: Storage and lineage requirements created by generated training data.

## Mental Models

Think in exposed latency, not nominal device bandwidth: a fast tier matters only if its wait is on the critical path. Pack many samples into sequential shards when metadata overhead dominates. Use buffers as shock absorbers for variance, but remember deep prefetch consumes DRAM. Treat checkpoint writes as a distributed coordination event. Optimize the total movement path, not the cheapest storage quote.

## Anti-patterns

- **Millions of individual files**: Turns capable storage into metadata- and seek-bound input.
- **Remote-only reads**: Leaves accelerators exposed to network latency and variance across epochs.
- **Benchmarking a tiny local dataset**: Hides scale-dependent contention, cache misses, and multi-worker behavior.
- **Synchronous durable checkpointing by default**: Converts a periodic burst into a full training pause.
- **Capacity-only sizing**: Confuses enough terabytes with enough throughput, IOPS, or endurance.

## Worked Example

A practical pipeline stages shards on local NVMe, uses host workers to read, decode, augment, and collate, and asynchronously transfers batches to the GPU. Prefetching overlaps preparation of batch *i+1* with computation of batch *i*. For checkpointing, each worker writes its shard locally first; a background process copies the completed checkpoint to the parallel file system. The critical pause is then the local write rather than the entire durable fan-in. This design trades local capacity and lifecycle management for far less exposed I/O and a smaller failure-recovery window.

## Key Takeaways

1. Compute the required fuel-line bandwidth before buying more accelerators.
2. Pack data, use locality, and pipeline the full read-to-GPU path.
3. Monitor stalls, queue depth, metadata, decode, and endurance—not just capacity.
4. Stage checkpoints locally and make durable copies asynchronous when safe.
5. Include provenance and verification overhead for synthetic data.

## Connects To

- **Chapter 2**: Host DRAM, NVMe, PCIe, and HBM form the node’s bandwidth hierarchy.
- **Chapter 5**: Dataset splitting and training parallelism determine read demand.
- **Chapter 7**: Checkpoint design controls recovery work and failure cost.
- **Chapter 8**: Locality-aware orchestration places jobs near cached shards.
