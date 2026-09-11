# Chapter 4: Distributed Communication and I/O Optimizations
**Source**: AI Systems Performance Engineering — Chris Fregly, O’Reilly, 2025 early release, available Chapter 4

## Core Idea
Distributed AI succeeds when data movement is treated as a first-class pipeline. Overlap communication with compute, bypass unnecessary CPU copies, choose topology-appropriate collective algorithms, and stage storage data locally so GPUs do not wait for network, disk, or synchronization.

## Frameworks Introduced
- **Communication/computation overlap**: Use asynchronous operations and CUDA streams so transfers run while kernels compute; gradient accumulation, compression, and buckets reduce or hide synchronization cost.
- **Magnum IO**: A stack spanning network I/O, storage I/O, in-network compute, and I/O management; its components include GPUDirect RDMA, NCCL, GDS, SHARP, DPUs, NetQ, and UFM.
- **NCCL collective strategies**: Ring suits large messages with relatively uniform links; tree/recursive doubling reduce steps; CollNet and PAT use concurrent hierarchical aggregation; auto mode selects based on topology and message conditions.
- **NIXL inference transfer**: Complement NCCL with direct, asynchronous movement of KV-cache and other large buffers across GPU, CPU, NVMe, and object-storage tiers.

## Key Concepts
- **RDMA/GPUDirect RDMA**: Direct memory-to-memory transfer that bypasses per-packet CPU copying; InfiniBand and RoCE are the main examples.
- **GPUDirect Storage (GDS)**: Direct storage-to-GPU DMA, avoiding host-memory bounce buffers; the source cites a 20% read-throughput gain in some workloads.
- **All-reduce**: Collective gradient aggregation across training GPUs.
- **KV-cache**: Reused attention key/value tensors; prefill builds it and decode uses it to generate tokens.
- **Prefill/decode disaggregation**: Put compute-bound prompt processing and memory-throughput-bound token generation on different resources.
- **Data locality and sharding**: Place balanced dataset shards on nodes or fast local NVMe to avoid a storage hot spot.
- **Goodput bubble**: GPU idle time caused by a batch, transfer, or synchronization not being ready.

## Mental Models
Use bandwidth for large transfers and latency for small-message diagnosis; a low-latency but narrow link can still lose on a large all-reduce. Think of every copy as a candidate for elimination and every wait as a candidate for overlap. Treat the storage system as part of the training model: few large sequential reads, parallel workers, and local caching are generally friendlier than millions of tiny random reads. Tune from telemetry: correlate `nvidia-smi`, `iostat`, `ifstat`, profiler timelines, and NIC counters.

## Anti-patterns
- **CPU bounce buffers**: Routing GPU-to-GPU or storage data through host memory adds copies and CPU overhead.
- **One storage server or hot shard**: Even a distributed filesystem stalls when access is uneven or metadata requests from small files overload its service.
- **Unbounded parallelism/prefetch**: More workers or queued batches eventually saturate disk, network, CPU, or RAM.
- **Blind NCCL knob changes**: Force algorithms or buffer sizes only after profiling topology, message sizes, and the selected interface.

## Code Examples
```python
loader = DataLoader(dataset, batch_size=B, num_workers=8,
                    pin_memory=True, prefetch_factor=2)
for batch in loader:
    batch = batch.to(device, non_blocking=True)
    outputs = model(batch)
```
The pattern prepares up to two batches per worker and overlaps pinned-memory transfer with model work. For Ethernet, the source also identifies `NCCL_SOCKET_IFNAME`, `NCCL_IB_HCA`, `NCCL_ALGO`, `NCCL_NTHREADS`, and `NCCL_BUFFSIZE` as workload-dependent controls.

## Worked Example
With 100 TB of data and 100 nodes, stage a 1 TB shard on each node and read locally at roughly 5–6 GB/s sequentially. For network capacity, eight GPUs each sending 1 GB/s generate 8 GB/s against a 100 Gbit/s link’s 12.5 GB/s, which fits if no other traffic competes. Sixteen GPUs generating 16 GB/s exceed that link; investigate compression, accumulation, or batching while monitoring accuracy and throughput.

## Key Takeaways
1. Overlap compute with gradient, activation, KV-cache, and input transfers.
2. Prefer RDMA, zero-copy paths, GDS, and in-network SHARP where supported.
3. Choose NCCL strategy and parameters experimentally; verify interfaces and topology first.
4. Pack small files, shard evenly, prefetch bounded batches, and cache data close to GPUs.
5. Measure end-to-end goodput rather than a single disk, NIC, or GPU metric.

## Connects To
- **Chapter 1**: Overlap and locality are concrete ways to raise goodput and test mechanical sympathy.
- **Chapter 2**: NVLink/NVSwitch, HBM, NICs, and DPUs determine the fastest data paths.
- **Chapter 3**: NUMA affinity, pinned memory, containers, and schedulers must preserve those paths.
