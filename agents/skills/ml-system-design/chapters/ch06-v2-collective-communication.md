# Chapter 6: Collective Communication

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 6

## Core Idea

Distributed training’s abstract synchronization becomes a physical travel manifest: every gradient, shard, activation, or token follows a collective communication pattern. Correct design starts by choosing the narrowest primitive that preserves the algorithm, then choosing an algorithm and topology that minimize startup, bytes moved, and exposed time.

## Frameworks Introduced

- **Collective primitive ladder**: Send/Receive, Broadcast, Reduce, AllReduce, AllGather, ReduceScatter, and AllToAll express different coordination shapes. Use the smallest primitive that satisfies the parallelism strategy.
- **Alpha-beta model**: Communication combines a startup tax (latency) and a transit fee (message size over effective bandwidth). Use it for first-order sizing and algorithm crossover reasoning.
- **Ring AllReduce**: Split the buffer into chunks, perform reduce-scatter around a ring, then all-gather results. Use it for large messages and bandwidth-efficient uniform link use.
- **Tree / butterfly / double binary tree**: Tree-like algorithms reduce startup rounds, while recursive halving-doubling can combine logarithmic latency with bandwidth-efficient movement under suitable connectivity. Use message size and topology—not a universal favorite—to choose.
- **Hierarchical AllReduce**: Reduce within nodes, exchange reduced shards across nodes, then gather within nodes. Use it when NVLink and inter-node bandwidth differ sharply.

## Key Concepts

- **AllReduce decomposition**: AllReduce can be understood as ReduceScatter followed by AllGather.
- **ReduceScatter**: Reduce contributions while distributing distinct result shards.
- **AllGather**: Replicate distributed shards to every participant.
- **AllToAll**: Every rank sends unique data to every other rank; common in MoE routing.
- **Latency regime**: Small messages are dominated by startup and software overhead.
- **Bandwidth regime**: Large messages are dominated by bytes transferred over the fabric.
- **NCCL reality gap**: Measured performance can trail simplified model predictions because protocol and implementation overhead matter.
- **Communication-computation overlap**: Pipeline communication under useful computation to remove it from the critical path when computation is sufficient.

## Mental Models

Treat a collective as both an API and a traffic shape. The primitive fixes who must coordinate; the algorithm fixes how data traverses links. Think of Ring as a bandwidth schedule, Tree as a latency schedule, and hierarchical collectives as a way to respect physical locality. Separate predicted transfer time from exposed time: overlap can hide latency, but launch and synchronization overhead may remain.

## Anti-patterns

- **One algorithm for every size**: Misses the latency/bandwidth crossover and topology effects.
- **Flat-ring blindness**: Sends traffic across slow inter-node links when local reduction could shrink it first.
- **Confusing AllToAll with AllReduce**: Applies a reduction pattern to unique routing traffic and creates hot spots.
- **Trusting the model without measurement**: Ignores NCCL protocol overhead, stragglers, and real fabric behavior.
- **Compression without convergence checks**: Saves bytes while silently changing optimization behavior.

## Worked Example

A hierarchical AllReduce for a multi-node job has three phases. First, GPUs in each node perform an intra-node ReduceScatter over NVLink, producing a shard per GPU. Second, matching shards participate in inter-node AllReduce over the slower fabric, so only a fraction of the original tensor crosses the node boundary. Third, an intra-node AllGather reconstructs the complete result. This schedule spends expensive inter-node bandwidth on reduced shards and uses fast local links for fan-in and fan-out. Profile each phase separately; a theoretically ideal schedule can still lose to protocol startup or poor placement.

## Key Takeaways

1. Choose the primitive from the algorithm’s data dependency.
2. Use alpha-beta reasoning to separate startup from transit cost.
3. Match Ring, Tree, butterfly, or double-tree behavior to message size and fabric.
4. Hierarchically reduce traffic across bandwidth cliffs and measure actual NCCL behavior.
5. Overlap only when useful computation covers exposed communication.

## Connects To

- **Chapter 3**: Link bandwidth, topology, congestion, and loss behavior are the physical inputs.
- **Chapter 5**: Data, tensor, pipeline, FSDP, and expert parallelism create distinct collectives.
- **Chapter 8**: Placement and rail-aware scheduling determine collective paths.
- **Chapter 9**: Profiling identifies communication overhead and overlap effectiveness.
