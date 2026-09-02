# Chapter 3: OS, Docker, and Kubernetes Tuning for GPU-based Environments
**Source**: AI Systems Performance Engineering — Chris Fregly, O’Reilly, 2025 early release, available Chapter 3

## Core Idea
A GPU is only as productive as the host stack feeding it. NUMA placement, pinned memory, page management, CPU scheduling, driver state, container I/O, and topology-aware orchestration remove the delays that otherwise appear as GPU bubbles, jitter, or low utilization.

## Frameworks Introduced
- **Locality-first CPU/GPU feeding**: Bind a process, its memory, interrupts, and the GPU-serving work to the same NUMA node.
- **Producer–consumer input pipeline**: CPU workers load and transform future batches while the GPU consumes the current batch; tune workers, prefetching, and pinned memory together.
- **MPS versus MIG**: Use MPS to overlap underutilized processes; use MIG for hardware-isolated memory and SM partitions. Neither is a universal acceleration switch.
- **Topology-aware scheduling**: Kubernetes Topology Manager, NVIDIA GPU Operator, and correctly configured SLURM should place multi-GPU work on compatible NUMA/NVLink resources.

## Key Concepts
- **Pinned memory**: Page-locked host memory that supports fast DMA and asynchronous transfers; the chapter reports 2–3× faster copies than pageable memory.
- **Transparent Huge Pages (THP)**: Larger pages that reduce TLB pressure and page-fault overhead; gains may be a few percent.
- **Persistence mode**: Keeps the driver and GPU initialized, avoiding roughly one to two seconds of cold-start overhead.
- **MPS**: Concurrently schedules multiple clients, but does not partition GPU memory or provide strong isolation.
- **MIG**: Hardware partitions memory and SMs, with strong isolation but fixed, potentially fragmented capacity.
- **Overlay filesystem**: Container copy-on-write layers add I/O metadata and write overhead; bind mounts bypass them.
- **Resource isolation**: cgroups, CPU Manager, and pod requests/limits protect CPU and memory, while Kubernetes lacks native first-class I/O isolation in the described release.

## Mental Models
Follow the data path: storage → CPU workers → pinned host memory → GPU, and inspect each boundary when utilization dips. Treat containers as near-bare-metal for compute but not automatically for I/O or topology. Use MPS when slack exists to fill, MIG when isolation matters, and neither for a large job needing the whole GPU. Prefer homogeneous nodes and dedicated resources when consistency matters.

## Anti-patterns
- **Cross-NUMA scheduling**: Letting the OS migrate GPU-serving threads or allocate remote memory adds latency and jitter; the chapter reports possible 5–10% training gains from pinning.
- **Oversubscribed host/GPU memory**: Swapping or relying on unified-memory paging is a safety net, not a performance plan; GPU OOMs and host OOM-killer actions can terminate jobs.
- **Heavy dataset I/O in the writable image layer**: Copy-on-write and overlay lookups needlessly slow reads and writes.
- **Arbitrary GPU allocation**: Giving a multi-GPU pod devices from different fast-link or NUMA domains can halve effective inter-GPU bandwidth.

## Code Examples
```bash
numactl --cpunodebind=1 --membind=1 python train
nvidia-smi -pm 1
```
Use matching NUMA CPU and memory placement, and keep GPUs initialized. For data transfer, configure PyTorch’s `DataLoader(pin_memory=True)` and use nonblocking copies; for storage, bind-mount data such as `-v /data/dataset:/mnt/dataset:ro` instead of writing through the container layer.

## Worked Example
On an eight-GPU node split across two NUMA nodes, map GPUs 0–3 and their workers to node 0 and GPUs 4–7 to node 1. Pin each training process and its memory with `numactl`, reserve worker CPUs, and enable pinned DataLoader memory. If a GPU remains idle, increase workers or prefetching until storage or CPU saturation appears, rather than blindly adding workers. For Kubernetes, request a topology-compatible GPU set, use `hostNetwork: true` when policy permits performance-sensitive RDMA, and request dedicated CPUs or the node when jitter is unacceptable.

## Key Takeaways
1. Start with hardware topology, then align CPU, memory, interrupts, GPU, and pod placement.
2. Disable swapping, use locked memory and appropriate huge pages, and keep the driver persistent.
3. Tune DataLoader workers, `prefetch_factor`, and `pin_memory` from measurements; excessive prefetch consumes RAM.
4. Match CUDA container libraries to the host driver; the source gives CUDA 12.8 with driver 570.124.06 or newer as an example.
5. Keep ECC enabled for serious workloads unless a narrowly justified research trade-off accepts corruption risk.

## Connects To
- **Chapter 2**: Hardware NUMA, HBM, and interconnect topology determine useful affinity choices.
- **Chapter 4**: RDMA/NCCL traffic and storage pipelines depend on the host networking, CPU, and I/O configuration.
