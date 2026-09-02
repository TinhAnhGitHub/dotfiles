# Chapter 12: AI Systems Performance Checklist (175+ Items)
**Source**: AI Systems Performance Engineering — Chris Fregly, O’Reilly, 2025 early release, available TOC Chapter 12

## Core Idea
Use the checklist as a repeatable loop: measure the end-to-end system, fix the largest contributor, measure again, and preserve the result. It spans cost and reproducibility, architecture, OS and drivers, GPU kernels, data I/O, precision, distributed communication, inference serving, and power. The source’s 175+ reminders are conditional: apply only the items relevant to the observed bottleneck.

## Frameworks Introduced
- **Optimize the expensive first**: Apply the 80/20 rule. If data loading is 40%, GPU compute 50%, and communication 10%, fix data loading before a 1% kernel.
- **Profile before and after**: Compare iteration time, throughput, latency, utilization, memory, network, and energy; a change such as checkpointing can hurt a workload that is not memory-limited.
- **Least-intrusive sufficient fix**: Start with AMP, prefetching, libraries, and compiler improvements; reserve custom kernels for a measured need.
- **End-to-end regression loop**: Version configurations, benchmark changes in CI, document gains, and test scale before committing to a larger cluster.

## Key Concepts
- **Bottleneck classes**: Compute-bound, memory-bound, I/O-bound, and communication-bound workloads require different fixes.
- **Goodput**: Useful work per dollar or joule, not theoretical FLOPs.
- **Topology awareness**: Keep coupled ranks within NVLink/NVSwitch domains and use hierarchical collectives across nodes.
- **Overlap**: Hide input copies and all-reduce behind computation with asynchronous streams and pipelining.
- **Tail latency**: Track p99 inference latency, not only averages.
- **Reproducibility**: Git, benchmark baselines, version pinning, checkpoints, and documented configurations make gains durable.

## Mental Models
Use a resource-chain model: the slowest CPU, memory, disk, network, or synchronization stage starves every faster stage. Use a locality model: place hot weights, activations, and KV cache in GPU HBM; use CPU memory, NVMe, and remote links for colder or overflow data. Use a scale model: if an all-reduce consumes 20% of an iteration on eight GPUs, profile it before scaling because the fraction can worsen beyond a node or rack. Use a sustainability model: a memory-bound kernel may run at a lower clock with similar time but better throughput per watt.

## Anti-patterns
- **Micro-optimizing without a baseline**: Theory-driven changes can do nothing or regress throughput.
- **Oversubscribing CPU, NIC, or storage**: Eight GPUs can generate over 200 Gbps during all-reduce; a single 100 Gbps NIC can throttle them.
- **Using MIG for tightly coupled jobs**: MIG is for isolation and small workloads; distributed jobs need full GPU access.
- **Ignoring correctness, accuracy, and reliability**: Validate quantization, keep ECC enabled unless justified, and preserve fault tolerance for long jobs.

## Worked Example
A practical pass starts with Nsight Systems plus framework profilers and NVTX ranges around loading, forward, and backward phases. If GPUs idle behind input, increase `DataLoader(num_workers=N)`, use `pin_memory=True`, `non_blocking=True`, fast local NVMe, sharded/binary data, and prefetching; compare real-data overhead with synthetic data, aiming for under 10%. If communication dominates, use RDMA, topology-aware NCCL, hierarchical all-reduce, gradient accumulation or compression, and test with NCCL tests. For kernels, inspect occupancy, coalescing, shared-memory conflicts, divergence, and roofline position before trying fusion, streams, `cudaMemcpyAsync`, or `cudaMemPrefetchAsync`. For serving, benchmark dynamic batching, TensorRT/Dynamo/vLLM, quantization, NIXL KV-cache transfers, and p99 latency. Finish with a power/thermal run using `nvidia-smi dmon` and compare throughput per watt.

## Reference Tables
| Area | Verify | Source-supported actions |
|---|---|---|
| OS/driver | NUMA, pinned memory, versions | `numactl --membind`, `ulimit -l unlimited`, `nvidia-smi -pm 1`, `--ipc=host`, `--ulimit memlock=-1` |
| GPU/data | idle gaps, bandwidth, allocations | `pin_memory=True`, `non_blocking=True`, `cudaMemcpyAsync`, CUDA Graphs, binary formats |
| Network | link health and collective time | RDMA/RoCE, `NCCL_NTHREADS`, `NCCL_BUFFSIZE`, `NCCL_SHARP_CAPABLE=1`, `iperf`, NCCL tests |
| Serving/power | p99, thermals, cost | warmup, MIG/QoS, `nvidia-smi -pl`, clocks, DCGM/Prometheus dashboards |

## Key Takeaways
1. Profile on a small representative scale before buying or launching a much larger cluster.
2. Keep all nodes’ drivers, CUDA, libraries, and benchmark inputs controlled and documented.
3. Prefer coalesced, fused, asynchronous, library-backed paths, but verify every gain.
4. Tune accuracy, throughput, latency, reliability, and energy together.
5. Re-run regression benchmarks after framework, driver, firmware, kernel, or topology changes.

## Connects To
- **Chapter 10**: Case studies supply measured examples of FP8/FP4, scheduling, overlap, and unified memory.
- **Chapter 11**: Future optics, DPUs, sparsity, cooling, and heterogeneous devices extend the same checklist categories.
