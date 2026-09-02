# Chapter 12: Benchmarking

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 12

## Core Idea
Benchmarking turns optimization claims into evidence. An ML system is not defined by one kernel or one accuracy number; it combines data, model, hardware, runtime, pipeline, and operating conditions. Fair comparison therefore fixes the question, measures the relevant granularity, reports uncertainty, and uses workloads that resemble deployment.

## Frameworks Introduced
- **ML benchmarking framework**: Define the objective, workload, metrics, system boundary, and experimental conditions before collecting numbers.
- **Granularity ladder**: Measure kernels, operators, model execution, pipeline stages, and end-to-end service separately; use each level for diagnosis without confusing it with user-visible performance.
- **Training versus inference benchmarks**: Training emphasizes time to quality, throughput, scaling, and resource use; inference emphasizes latency, throughput, tail behavior, availability, and cost per request.
- **Benchmark components**: Specify model, data, software versions, hardware, precision, batch size, warm-up, concurrency, and measurement protocol.
- **Production-aware evaluation**: Include realistic input distributions, request mix, contention, thermal state, power behavior, and service constraints.

## Key Concepts
- **Latency**: Time to complete a request; report average and distributional measures such as percentile tail latency.
- **Throughput**: Work completed per unit time, often requests, samples, or tokens per second.
- **Time to quality**: Training duration or resource needed to reach a defined quality target, rather than raw step speed alone.
- **Warm-up**: Initial execution used to remove compilation, allocation, cache, or startup effects before steady-state measurement.
- **Repetition and variance**: Repeated trials reveal noise and support confidence intervals or other uncertainty reporting.
- **Energy and power**: Power is an instantaneous or averaged rate; energy accounts for work over time. Both need clear measurement boundaries.
- **Scalability**: How performance changes with devices, workers, batch size, or concurrency; scaling efficiency can fall because of communication and synchronization.

## Mental Models
A benchmark is an instrument with a scope, not a universal truth. Kernel speed explains a local bottleneck; end-to-end latency answers a user question. Throughput and latency are coupled by batching and queueing, so neither should be reported in isolation. Reproducibility is part of the result: an impressive number without software versions, data, precision, thermal state, and measurement boundaries cannot support a sound decision.

## Anti-patterns
- **Cherry-picked runs**: Selecting the fastest trial hides variance and makes results irreproducible.
- **Peak-specification benchmarking**: Treating advertised FLOPs or throughput as sustained application performance.
- **Unfair baselines**: Comparing different batch sizes, precision, preprocessing, or optimization levels without disclosure.
- **Kernel-only conclusions**: Inferring service improvement while excluding data movement, orchestration, postprocessing, or queueing.
- **Cold-start confusion**: Mixing startup and steady-state behavior without stating which matters for the product.
- **Accuracy–efficiency separation**: Reporting speed for a model whose quality or calibration is no longer equivalent.

## Worked Example
To compare two inference runtimes, a team defines a production model, representative inputs, supported precision, concurrency levels, and a fixed hardware/software environment. Each run includes a documented warm-up, then enough repetitions to report median and tail latency, throughput, and energy per request. They measure both model execution and the complete request path, and repeat at several batch sizes. A runtime that wins isolated throughput but violates the latency target under concurrent load is not the winner; the decision uses the stated service objective and quality checks.

## Key Takeaways
1. Define the question and system boundary before benchmarking.
2. Report latency, throughput, quality, and energy together when they trade off.
3. Measure realistic shapes, distributions, concurrency, and sustained conditions.
4. Repeat trials and expose variance, warm-up, and environmental details.
5. Connect microbenchmarks to end-to-end and production evidence.

## Connects To
- **Chapters 9–11**: Benchmarking validates the gains claimed by data selection, compression, and acceleration.
- **Chapter 13**: Serving benchmarks must include queueing, batching, and tail-latency behavior.
- **Chapter 14**: Production monitoring extends benchmark assumptions into ongoing operations.
- **Chapter 16**: Evidence-based comparison supports disciplined system design.
