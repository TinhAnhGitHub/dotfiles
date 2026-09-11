# Chapter 2: AI System Hardware Overview
**Source**: AI Systems Performance Engineering — Chris Fregly, O’Reilly, 2025 early release, available Chapter 2

## Core Idea
Modern AI hardware is a balanced system: compute, memory capacity and bandwidth, interconnect topology, power delivery, and cooling must be designed together. The GB200 NVL72 illustrates this by coupling Grace CPUs and Blackwell GPUs into coherent superchips and joining 72 GPUs with an NVLink/NVSwitch fabric.

## Frameworks Introduced
- **Integrated superchip architecture**: Use NVLink-C2C to couple one Grace CPU with two Blackwell GPUs, reducing explicit CPU/GPU copies and exposing a unified address space.
- **Memory hierarchy and locality**: Keep reusable data in registers, shared memory/L1, or L2 before relying on HBM; use CPU memory as larger but slower overflow.
- **Rack-scale acceleration domain**: Keep communication inside an NVL72 rack when possible; treat inter-rack InfiniBand or Ethernet as a slower boundary.
- **Precision as a throughput lever**: Tensor Cores and Transformer Engine use mixed FP16/BF16, FP8, and FP4 where accuracy permits, trading representation width for compute and memory efficiency.

## Key Concepts
- **Grace-Blackwell superchip**: One 72-core Grace CPU plus two Blackwell GPUs with 864 GB combined addressable memory in the GB200 figures: 480 GB LPDDR5X and 384 GB HBM3e.
- **NVLink-C2C**: Cache-coherent CPU/GPU link with about 900 GB/s between Grace and each GPU.
- **Blackwell B200**: Two-die GPU module with 192 GB HBM3e, about 8 TB/s HBM bandwidth, and 100 MB L2 cache.
- **Latency hiding**: Keep many warps in flight so another warp runs while one waits for memory.
- **NVLink 5/NVSwitch**: Fabric providing up to 1.8 TB/s of bidirectional peer bandwidth per GPU and about 130 TB/s rack bisection bandwidth in the described NVL72.
- **SHARP**: In-network aggregation that moves collective reductions into supported switch hardware.
- **Goodput and power density**: A 120 kW rack must be monitored and cooled so theoretical capacity becomes productive work.

## Mental Models
Think of CPU memory as an extension, not an equal substitute, for GPU HBM: capacity helps model fit, but latency and bandwidth still favor HBM. Think of topology as part of the programming model; the same GPU count can scale differently depending on whether communication stays in NVLink or crosses racks. Think of power and cooling as performance resources: thermal throttling and facility limits can reduce sustained clocks and throughput.

## Anti-patterns
- **Treating all memory as equivalent**: Unified addressing removes copy complexity but does not remove the HBM-versus-CPU-memory performance gap.
- **Ignoring topology**: Placing synchronization-heavy work across a slower rack boundary can turn communication into the iteration bottleneck.
- **Buying peak hardware without utilization planning**: An idle, multi-million-dollar, 120 kW appliance wastes both capital and operating power.

## Worked Example
For the described ROI scenario, a workload using 100 H100 GPUs might be handled by 50 Blackwell GPUs if each delivers more than twice the relevant throughput, especially with FP8/FP4. The example compares roughly 70 kW for the H100 fleet with 50 kW for the Blackwell fleet and notes that an upgrade can pay back in 1–2 years when kept busy. The calculation is workload- and price-dependent; its point is to compare performance per dollar and watt, not device price alone.

## Reference Tables
| Layer | Source-supported implication |
|---|---|
| HBM | Fast local working set; Blackwell B200 is described at ~8 TB/s and 192 GB. |
| Grace memory | 480 GB LPDDR5X extends capacity, but is roughly 10× lower bandwidth/higher latency than HBM. |
| Intra-rack fabric | NVLink/NVSwitch: 1–2 μs small-message latency and 2–3% all-reduce iteration share in the comparison. |
| Inter-rack fabric | InfiniBand: typically 5–10 μs or more and potentially 20–30% of iteration time for all-reduce. |

## Key Takeaways
1. Size the working set for HBM, while using coherent CPU memory deliberately for overflow.
2. Preserve locality and keep collective traffic within the fastest interconnect domain.
3. Evaluate precision, sustained throughput, power, cooling, and utilization together.
4. Monitor GPU, NVLink, NIC, temperature, and power telemetry rather than assuming peak specifications are realized.

## Connects To
- **Chapter 1**: Mechanical sympathy and goodput turn the hardware specification into an optimization method.
- **Chapter 3**: NUMA, affinity, drivers, and orchestration must expose this topology to software.
- **Chapter 4**: NCCL, RDMA, SHARP, GDS, and NIXL exploit the memory and interconnect paths described here.
