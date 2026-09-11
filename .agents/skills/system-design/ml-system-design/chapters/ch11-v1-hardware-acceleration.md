# Chapter 11: Hardware Acceleration

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 11

## Core Idea
ML performance is shaped by the interaction of algorithms, operators, memory movement, and hardware. A faster chip does not guarantee a faster model: the workload may be limited by memory bandwidth, synchronization, unsupported operators, launch overhead, or poor utilization. Hardware-aware design chooses representations and execution plans that keep the right resources busy.

## Frameworks Introduced
- **Roofline model**: Relate attainable performance to peak compute and memory bandwidth through arithmetic intensity. It helps classify a kernel as compute-bound or memory-bound and points to the next optimization.
- **Hardware–software co-design**: Shape model architecture, tensor layouts, precision, compiler graph, kernels, and accelerator selection together rather than optimizing them in isolation.
- **Memory-hierarchy analysis**: Examine movement among registers, caches, shared/local memory, device memory, and host memory; reuse can matter more than nominal FLOPs.
- **Specialization spectrum**: General-purpose CPUs offer flexibility, GPUs offer throughput, and domain-specific accelerators trade flexibility for efficient supported operations. The right choice follows workload and lifecycle needs.

## Key Concepts
- **Arithmetic intensity**: Useful operations per byte moved. Low intensity often makes bandwidth and data reuse the limiting factors.
- **Utilization**: The fraction of available compute, memory, or accelerator capacity actually used.
- **Kernel fusion**: Combine compatible operations to reduce intermediate writes, reads, and launch overhead.
- **Tiling/blocking**: Partition computation to reuse data in a faster memory level.
- **Mixed precision**: Use supported lower-precision arithmetic to raise throughput and reduce movement while preserving sensitive computations.
- **Operator coverage**: The set of model operations efficiently implemented by a target runtime; unsupported operations can trigger expensive fallbacks.
- **Data movement**: Transfers and layout conversions that frequently dominate an otherwise small operation.

## Mental Models
Treat memory as a first-class resource. An operation’s theoretical FLOPs are only useful if data can arrive in time and the hardware can execute the required kernel. Roofline analysis is a diagnosis, not a benchmark replacement: it suggests whether to improve reuse, reduce bytes, increase parallelism, or optimize arithmetic. Also distinguish peak specifications from sustained application performance; end-to-end preprocessing, transfers, synchronization, and framework overhead determine user-visible results.

## Anti-patterns
- **Peak-FLOPs comparison**: Comparing accelerator specifications without matching precision, workload, batch shape, or operator mix.
- **Ignoring transfers**: Reporting device kernel time while excluding host-device copies, layout conversion, or input preparation.
- **One-size-fits-all batching**: Large batches can improve throughput while violating latency or memory limits.
- **Assuming compiler magic**: Graph compilation cannot fuse or optimize operations that are semantically incompatible or unsupported.
- **Premature custom kernels**: Hand tuning before profiling the full path can optimize a non-binding component and increase maintenance cost.

## Worked Example
A transformer inference path has high theoretical compute but disappointing throughput. Profiling shows repeated materialization of intermediates and host-device synchronization between small operators. Roofline reasoning identifies low effective arithmetic intensity. The team changes tensor layouts, fuses compatible operators, tiles a hot matrix operation for cache reuse, and keeps transfers on device. They then remeasure end-to-end latency at production batch sizes. If a required operator still falls back to the CPU, the design must either provide an accelerator implementation, change the graph, or choose a different target; the peak number alone cannot resolve the bottleneck.

## Key Takeaways
1. Profile first and classify the limiting resource.
2. Optimize data movement, reuse, and supported kernels as well as arithmetic.
3. Use Roofline to prioritize, then validate with end-to-end measurements.
4. Co-design model, compiler, runtime, and hardware constraints.
5. Report sustained behavior under realistic shapes and precision modes.

## Connects To
- **Chapter 10**: Compression is valuable only when hardware and kernels exploit the resulting representation.
- **Chapter 12**: Hardware comparisons require controlled, reproducible benchmark conditions.
- **Chapter 13**: Serving traffic turns accelerator utilization, batching, and queueing into user-visible latency.
- **Chapter 16**: Efficient systems align technical optimization with practical constraints and goals.
