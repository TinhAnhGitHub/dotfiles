# Chapter 9: Performance Engineering

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 9

## Core Idea

Performance engineering reshapes computation to match hardware physics. An accelerator can have enormous arithmetic capacity yet run slowly because bytes arrive late, kernels launch inefficiently, or communication is exposed. Diagnose first, then target the dominant term with memory reuse, fusion, precision, compilation, algorithmic change, or overlap.

## Frameworks Introduced

- **Memory wall**: Off-chip HBM bandwidth and distance can limit throughput before Tensor Cores reach peak. Use it to prioritize data movement and reuse over nominal arithmetic capacity.
- **Roofline diagnosis**: Classify an operation by arithmetic intensity relative to compute and memory ceilings. Use the operating point to choose a memory, compute, or overhead intervention.
- **Iron law of ML performance**: Reason about execution as data movement, compute, and latency/overhead, with overlap exposing the slower unhidden cost. Use the decomposition to avoid optimizing a nondominant term.
- **Efficiency frontier**: Throughput, latency, cost, quality, and memory form competing objectives. Use the application’s SLO and quality contract to choose a point rather than declaring one configuration universally best.
- **Optimization playbook**: Profile, remove I/O/CPU/communication stalls, classify the kernel, then apply fusion/tiling, precision, graph compilation, or algorithmic changes and re-profile.

## Key Concepts

- **Arithmetic intensity**: Operations performed per byte moved.
- **Ridge point**: Roofline crossover where compute and memory ceilings meet.
- **HBM**: High-capacity off-chip accelerator memory whose bandwidth can still be the binding wall.
- **Operator fusion**: Combine operations so intermediates remain in fast on-chip memory.
- **Tiling**: Partition computation to maximize data reuse in registers or shared memory.
- **FlashAttention**: A fused/tilled attention family that avoids materializing unnecessary intermediates.
- **Precision engineering**: Use formats such as FP8 or INT4 when quality and kernel support permit.
- **Graph compilation**: Tools such as `torch.compile`, XLA, and TensorRT reduce launch and dispatcher overhead.
- **MFU**: Fleet-level useful model computation, including losses from system overhead.

## Mental Models

Think of performance as a tensor’s journey through registers, SRAM, L2, HBM, and the network. Think of small-batch autoregressive decode as often memory-bound, while prefill and large GEMMs may be compute-bound. Use batch size to move along a latency-throughput frontier, not as a universal “bigger is better” knob. Treat overlap as conditional: it helps only when useful computation covers communication and launch costs.

## Anti-patterns

- **Optimizing blind**: Applying fusion or quantization before profiling and risking zero gain or quality loss.
- **Peak-FLOP fixation**: Increasing clocks for a memory-bound kernel whose arithmetic units are already waiting.
- **Naive quantization**: Shrinking representations while retaining kernels or memory paths that still move the original bytes.
- **Framework overhead denial**: Ignoring Python dispatch, launch gaps, synchronization, and allocator behavior.
- **Single-point benchmarking**: Reporting throughput without latency, cost, quality, memory, batch, and scale context.

## Worked Example

For a 70B serving workload, a latency-oriented configuration may keep FP16 weights, use batch one, and apply speculative decoding; a throughput-oriented configuration may use INT4, a large batch, and no speculation. The latter can lower cost per token dramatically while increasing inter-token latency. Neither wins without an application target. The engineering sequence is to profile low utilization, rule out data-loader, CPU, and communication stalls, use a roofline plot to classify the remaining kernels, then choose fusion/tiling for memory-bound work, precision or algorithmic changes for the appropriate regime, and graph compilation for launch overhead. Re-measure the whole frontier after every change.

## Key Takeaways

1. Profile before optimizing and identify the dominant exposed term.
2. Use Roofline to distinguish compute-bound, memory-bound, and overhead-bound work.
3. Reduce bytes and round trips with fusion, tiling, precision, and suitable kernels.
4. Use compilation and overlap only where their targeted overhead is actually exposed.
5. Optimize the throughput/latency/cost/quality/memory frontier for the workload’s SLO.

## Connects To

- **Chapter 2**: Accelerator memory hierarchy and Roofline ceilings are physical inputs.
- **Chapter 3**: Communication latency and bandwidth can remain exposed at scale.
- **Chapter 5**: Parallelism changes batch, overlap, and communication behavior.
- **Chapter 8**: Placement and utilization determine whether local optimizations matter fleet-wide.
