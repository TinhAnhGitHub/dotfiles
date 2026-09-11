# Chapter 10: Inference at Scale

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 10

## Core Idea
Inference is a user-facing service, not merely a forward pass. Its governing constraints are usually P99 latency, memory residency, request variability, and lifetime serving cost; the right architecture follows the model class and the active bottleneck.

## Frameworks Introduced
- **Training–inference inversion**: Training favors aggregate throughput and tolerates long variance; inference favors bounded latency, continuous session state, and redirect/failover without user impact. Use this when adapting a training optimization to serving.
- **Serving hierarchy**: Reason from request-level batching and caching, through replica memory management and scheduling, to service-level routing and platform multitenancy. Use it to locate where a latency or utilization problem actually lives.
- **Prefill/decode split**: Prefill processes the prompt and is comparatively compute-intensive; autoregressive decode produces output token by token, repeatedly reading weights and maintaining private KV-cache state. Disaggregate the phases when their workload mix and SLOs justify separate pools.

## Key Concepts
- **TTFT**: Time to First Token, the initial responsiveness signal.
- **TPOT**: Time Per Output Token, the perceived streaming pace.
- **Continuous batching**: Admit and remove requests at iteration boundaries rather than waiting for a whole static batch to finish.
- **KV cache**: Per-request attention state retained across generated tokens.
- **PagedAttention**: Page-like KV allocation that reduces fragmentation and recovers usable memory.
- **Tensor, pipeline, and expert parallelism**: Sharding strategies whose communication cost must fit the network and latency budget.
- **Power of two choices**: Probe two candidate replicas and choose the less-loaded one, improving balance over naive assignment.
- **Serving tax**: Communication, serialization, coordination, queuing, and isolation overhead added by distribution.

## Mental Models
- Think of decode as a memory-bandwidth problem disguised as a compute problem; more arithmetic peak does not automatically create more token capacity.
- Use static or dynamic batching for predictable vision shapes, feature-parallel batching for sparse recommenders, and iteration-level continuous batching for variable-length LLM requests.
- Treat tail latency as an architectural input: raising utilization is only useful if P99 remains inside the downstream contract.
- Choose sharding when a model or latency floor cannot fit one device; choose replication when capacity, not model residency, is binding.

## Anti-patterns
- **Optimize only average throughput**: Averages hide tail requests that violate the service-level objective.
- **Apply one batching policy everywhere**: Model shape, output-length variance, and statefulness determine the useful batching primitive.
- **Treat KV cache as incidental memory**: Fragmentation or over-admission can destroy throughput even when weights fit.
- **Assume training cost is the main bill**: High-volume inference OpEx compounds for the life of the service.
- **Distribute without budgeting the tax**: Sharding, failover, multi-tenancy, and global routing buy capacity or isolation by consuming communication and coordination budget.

## Worked Example
A 13B model with 26 GB of weights fits on one A100. If throughput demand doubles, horizontal replication is the natural first response because residency is not the constraint. By contrast, a 175B model cannot fit on an 80 GB GPU at typical precision, so sharding is mandatory even at low request volume. For an LLM endpoint, measure TTFT and TPOT separately: a scheduler may protect active decode tokens from new prefill work so that already-streaming users retain readable output pace. If output lengths vary, continuous batching can admit a short request while a long request continues, avoiding the padding and idle time of a conventional batch. Paged KV allocation then increases the number of active sequences the same memory can hold.

## Key Takeaways
1. Design serving around P99 latency and state residency, not training-era throughput alone.
2. Prefill and decode have different physical bottlenecks and can require different pools and policies.
3. Continuous batching, KV management, caching, sharding, and routing are coupled decisions.
4. Distribution is worthwhile only when its communication, coordination, and reliability tax fits the SLO.
5. Lifetime serving economics can dominate the one-time training investment.

## Connects To
- **Chapter 6**: Network topology and collective communication determine whether sharding is viable.
- **Chapter 9**: Performance engineering supplies the measurement discipline for latency and utilization.
- **Chapter 11**: Edge serving inverts data-center assumptions about memory, power, and connectivity.
- **Chapter 12**: MLOps operates these serving fleets through rollout, monitoring, and cost controls.
