# Chapter 8: Model Training

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 8

## Core Idea
Training is a systems workload that spends arithmetic, memory, data movement, and communication to update parameters. The practical discipline is profile, diagnose, apply the least costly intervention, and re-profile before scaling out.

## Frameworks Introduced
- **Iron Law of Training Performance**: Training time is governed by useful work and realized throughput; improve it by reducing work, increasing effective throughput, or raising utilization.
- **Profile–Select–Compose**: Profile the pipeline, select techniques for the measured bottleneck, compose compatible fixes, and measure again.
- **Parallelism Strategies**: Data parallelism splits examples; model parallelism splits model state or computation; pipeline parallelism fills layer stages with micro-batches; tensor parallelism splits operations.
- **Training principles**: Keep the accelerator fed, fit complete training state, use precision deliberately, and scale only after single-device constraints are addressed.

## Key Concepts
- **Training state**: Weights, gradients, optimizer state, master weights where used, activations, workspaces, and allocator overhead.
- **Data-bound training**: The input path cannot supply batches fast enough.
- **Memory-bound training**: State or traffic exceeds practical capacity or bandwidth.
- **Mixed precision**: Uses lower precision for eligible work while retaining higher precision where numerical stability requires it.
- **Gradient accumulation**: Serializes micro-batches to achieve a larger effective batch within memory limits.
- **Activation checkpointing**: Stores fewer intermediates and recomputes them during backpropagation.
- **FlashAttention**: IO-aware tiled attention that avoids materializing the full score matrix in high-bandwidth memory.
- **Communication tax**: Time and energy spent synchronizing devices, reducing scaling efficiency.

## Mental Models
Treat the slowest stage as the current ceiling. A data-starved GPU needs prefetching and overlap, not a faster kernel; an out-of-memory run needs less state or traffic, not simply more batch; a compute-bound run may benefit from precision or kernel improvements. Think of scaling as trading one bottleneck for another: data parallelism buys throughput, model parallelism buys capacity, pipeline parallelism buys utilization, and tensor parallelism makes large layers feasible.

## Anti-patterns
- **Weights-only budgeting**: Optimizer states and activations can exceed parameter memory many times over.
- **Blind batch maximization**: Larger batches improve amortization but increase activation memory and may require learning-rate retuning.
- **Precision as a toggle**: FP16 may need loss scaling; BF16 has different range and precision; both require convergence validation.
- **Adding GPUs first**: Communication, input limits, imbalance, and synchronization can erase the expected speedup.
- **Kernel tuning before input profiling**: An idle accelerator may be waiting on storage, preprocessing, or host-to-device transfer.

## Worked Example
A GPT-2-scale walkthrough starts with a roughly 95.7 GB FP32 training budget for batch four. Mixed precision reduces lower-precision weights, gradients, and activations, while selective checkpointing reduces activation storage; the modeled total falls to about 33 GB before temporary workspace overhead. The techniques move the workload near a 32 GB device boundary, demonstrating why memory-saving techniques should be exhausted and re-profiled before accepting distributed complexity.

## Key Takeaways
1. Profile end-to-end training before choosing an optimization.
2. Match remedies to data, compute, memory, attention-bandwidth, or communication bottlenecks.
3. Use prefetching, mixed precision, accumulation, checkpointing, and IO-aware kernels deliberately.
4. Scale when memory, schedule, or input-service limits persist after local optimization.
5. Validate numerical behavior, convergence, utilization, and energy—not just nominal throughput.

## Connects To
- **Chapter 4**: Data storage, transformation, and feeding determine input throughput.
- **Chapter 6**: Architecture controls activation, attention, and parallelism costs.
- **Chapter 7**: Frameworks expose the runtime, precision, loader, and distributed mechanisms.
- **Chapter 2**: Training clusters and interconnects are deployment paradigms with physical limits.
