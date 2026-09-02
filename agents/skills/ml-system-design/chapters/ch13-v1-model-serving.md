# Chapter 13: Model Serving

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 13

## Core Idea
Serving turns a trained model into a reliable request-processing system. The deployment target—cloud, mobile, edge, or TinyML—sets different limits on memory, latency, throughput, energy, connectivity, and updateability. A serving design must meet quality and service objectives under traffic, not merely execute a model once.

## Frameworks Introduced
- **Serving spectrum**: Cloud systems favor elastic throughput and centralized operations; mobile systems balance app memory, responsiveness, and device acceleration; TinyML systems operate within severe SRAM, flash, and energy budgets.
- **Serving stack**: A request passes through ingress or load balancing, validation and preprocessing, model runtime, postprocessing, and response handling. Observability and health checks span the whole path.
- **Queueing model**: Arrivals, service time, concurrency, and utilization determine waiting. As utilization approaches capacity, queueing and tail latency rise sharply; throughput alone is not a safe capacity target.
- **Batching strategies**: Static batching improves accelerator utilization when traffic is regular; dynamic batching waits briefly to form batches, trading efficiency against waiting time; continuous batching suits some autoregressive workloads.
- **Resource isolation**: CPU affinity, memory locking, controlled scheduling, and dedicated resources reduce interference and latency jitter.

## Key Concepts
- **SLO/SLA**: Service objectives and commitments such as latency percentiles, availability, and error rate.
- **Tail latency**: High-percentile request time, often the user-visible constraint for interactive systems.
- **Load balancer**: Distributes requests, monitors replica health and model readiness, and enables gradual traffic shifts.
- **Model readiness**: A replica has loaded weights, completed warm-up, and can serve correctly—not merely that its process is alive.
- **Admission control**: Reject or defer work when capacity or quality guarantees would otherwise be violated.
- **Autoscaling**: Add or remove replicas using workload and saturation signals, while accounting for startup and warm-up time.
- **Cold start**: Startup delay from loading images, weights, runtimes, or accelerators.
- **Edge deployment**: Local execution can reduce network dependence and data movement but imposes fixed resource limits.

## Mental Models
Think in request paths and queues, not model calls. A 2 ms kernel can sit inside a much slower pipeline, and a fast average can coexist with unacceptable p99 latency. Capacity is a safe operating region, not the maximum measured throughput. Batching is a control knob: it amortizes overhead and raises utilization but adds waiting and may increase memory pressure. Deployment context is part of model architecture; a model that fits cloud VRAM may be infeasible in TinyML SRAM.

## Anti-patterns
- **Average-latency fixation**: Ignoring p95/p99 behavior and overload transitions.
- **Running at saturation**: Planning capacity at peak throughput leaves no room for bursts, failures, or service-time variance.
- **Unbounded queues**: Preserving every request can create runaway latency and memory use; define admission and backpressure behavior.
- **Liveness-only health checks**: Routing traffic to replicas whose model is still loading or warming up.
- **Blind dynamic batching**: Waiting for batches can violate latency SLOs when traffic is sparse.
- **Ignoring isolation**: Noisy neighbors, paging, and shared resources create unpredictable jitter.

## Worked Example
A vision API must meet a 50 ms p99 target. The team measures the complete path at realistic request rates, compares batch-1 with short-window dynamic batching, and observes queue growth as utilization rises. They reserve headroom, cap the batching delay, configure readiness checks after warm-up, and route away from overloaded replicas. During a burst, admission control protects accepted requests instead of allowing an unbounded queue. The selected configuration is justified by p99 latency, throughput, error rate, memory, and cost—not by the fastest isolated inference call.

## Key Takeaways
1. Design for the target serving context and its resource budget.
2. Optimize the entire request path and report tail latency.
3. Keep utilization below the unstable queueing region.
4. Make batching, backpressure, readiness, and isolation explicit.
5. Capacity-plan for bursts, failures, cold starts, and model updates.

## Connects To
- **Chapter 10**: Compression can make a model fit the serving target, but runtime support determines realized benefit.
- **Chapter 11**: Accelerator utilization and memory movement shape serving throughput.
- **Chapter 12**: Serving claims require production-like load and percentile benchmarks.
- **Chapter 14**: Operations owns deployment safety, monitoring, rollback, and drift response.
