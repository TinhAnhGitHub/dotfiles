# Chapter 3: Network Fabrics

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 3

## Core Idea

The network is the synchronization backbone—or “gradient bus”—that turns accelerator nodes into one training machine. ML networking inverts conventional data-center assumptions: traffic is synchronous, periodic, elephant-sized, loss-intolerant, and judged by tail latency and global step time. A fabric must therefore be designed from wire physics through transport, topology, congestion behavior, and cluster integration.

## Frameworks Introduced

- **Five-Level Network Model**: Level 1 Wire and Link; Level 2 Transport; Level 3 Switch and Topology; Level 4 Fabric Behavior; Level 5 Cluster Design. Use it as a causal debugging path from signal integrity to stalled training.
- **ML networking inversion**: Replace many asynchronous short flows with a few synchronized collective flows. Use this to prioritize bisection bandwidth, lossless behavior, and P99 completion time over average per-flow fairness.
- **Alpha-beta performance model**: Separate fixed message startup latency from size-dependent transfer time. Use it to distinguish latency-dominated small messages from bandwidth-dominated large transfers; do not assume bandwidth alone predicts collectives.
- **Bandwidth hierarchy**: Intra-node NVLink is much faster than inter-node InfiniBand, so parallelism and placement should follow physical locality.

## Key Concepts

- **AllReduce**: Sum data across ranks and return the result to every rank.
- **AllGather**: Collect distinct shards so every rank reconstructs the full state.
- **AllToAll**: Send a distinct payload from each rank to every other rank, central to expert routing.
- **RDMA**: Remote direct memory access that avoids much host involvement.
- **GPUDirect**: Direct movement between network and GPU memory, reducing copies.
- **PAM4**: Four-level signaling that raises bits per symbol while tightening signal margins.
- **Bisection bandwidth**: Throughput ceiling across a cut dividing the cluster.
- **PFC**: Priority Flow Control, which pauses traffic classes but can propagate congestion.
- **DCQCN/HPCC**: Congestion-control approaches using feedback, with HPCC using in-network telemetry.
- **Incast**: Many senders converging on a receiver or link at once.

## Mental Models

Treat the fabric as a bus for gradients: one slow link can make every peer wait. Treat topology as a performance contract; a “non-blocking” claim does not mean a workload has no congestion. Use the alpha-beta split to choose link upgrades versus message aggregation. Think of PFC as containment, not congestion elimination, and inspect tail latency because BSP exposes the slowest path.

## Anti-patterns

- **Web-service network assumptions**: Oversubscribing a fabric designed for asynchronous traffic and expecting statistical multiplexing to hide synchronized bursts.
- **PFC as a cure**: Enabling pause propagation without observing storm risk, queue depth, and tail latency.
- **Flat topology thinking**: Treating NVLink and inter-rack paths as interchangeable when parallelism depends on locality.
- **Average-throughput monitoring**: Missing one degraded transceiver or hot path that stalls a global collective.

## Worked Example

For a large synchronous model, a gradient exchange may involve hundreds of gigabytes. Within a node, NVLink keeps the exchange close to the accelerators; across nodes, an NDR InfiniBand port has far less per-direction bandwidth, so the same collective becomes a visible step block unless overlap hides it. Start diagnosis at the application symptom, inspect RDMA and switch counters, run point-to-point bandwidth tests such as `ib_write_bw`, then check PFC/ECN and physical-layer errors. The layer model prevents an engineer from “fixing” a topology or optical problem in the training code.

## Key Takeaways

1. Design for synchronized collective completion and tail latency, not average web traffic.
2. Use the five levels to connect a training stall to the responsible layer.
3. Match collective traffic and parallelism to the bandwidth hierarchy.
4. Validate congestion control and physical health with link-level telemetry.

## Connects To

- **Chapter 2**: Node topology and the intra-/inter-node bandwidth cliff set fabric requirements.
- **Chapter 6**: Collective algorithms decide how the fabric’s physical capacity is consumed.
- **Chapter 8**: Topology-aware scheduling places jobs on favorable paths.
- **Chapter 9**: Communication overhead can be overlapped or exposed in performance timelines.
