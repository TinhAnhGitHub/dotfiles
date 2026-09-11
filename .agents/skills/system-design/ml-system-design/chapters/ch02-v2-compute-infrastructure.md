# Chapter 2: Compute Infrastructure

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 2

## Core Idea

Machine learning infrastructure is a physical constraint cascade. Accelerator arithmetic, memory bandwidth, power delivery, cooling, topology, and reliability interact as a system from die to node, rack, pod, and facility. The right infrastructure is workload-dependent: peak specifications matter less than sustained useful throughput at the relevant memory and communication boundary.

## Frameworks Introduced

- **Four Infrastructure Walls**: Power, memory, communication, and reliability become dominant at different fleet scales. Use the wall that is currently binding to choose the next intervention.
- **Generality Tax**: General-purpose control logic spends silicon and energy on flexibility a regular matrix workload may not need. Use the accelerator spectrum—CPU, GPU, TPU, custom ASIC—as a flexibility-versus-efficiency decision, not a universal ranking.
- **Roofline Model**: Position a workload by arithmetic intensity against compute and memory-bandwidth ceilings. Use it to decide whether more FLOP/s or more effective data reuse can improve performance.
- **Bandwidth Staircase**: HBM, intra-node links, host memory/PCIe, and inter-node fabrics form progressively slower zones. Use the staircase to map tensor, pipeline, and data parallelism to the boundary they can tolerate.

## Key Concepts

- **Accelerator spectrum**: A continuum trading programmability for specialized arithmetic efficiency.
- **SIMT**: GPU execution in which threads share an instruction stream, making regular matrix work efficient but divergence costly.
- **Systolic array**: A fixed grid that streams operands through neighboring multiply-accumulate units.
- **HBM**: High Bandwidth Memory placed close to the accelerator for high bandwidth and finite capacity.
- **Memory wall**: Compute grows faster than off-chip bandwidth, leaving arithmetic units starved for data.
- **MFU**: Model FLOPs Utilization, a measure of useful model computation relative to peak capability.
- **NUMA**: Non-uniform memory access; host placement changes the path and bandwidth to a GPU.
- **Warehouse-Scale Computer**: A pod operated as one computer, with failures and networking treated as system properties.

## Mental Models

Think of a GPU as a data-movement machine with arithmetic attached: keep operands near compute and reuse them. Think of node design as assembling a local memory pool, but remember that each physical boundary introduces a bandwidth cliff. Use sustained throughput and workload roofline position for procurement. Treat power and cooling as capacity planning inputs, not facilities afterthoughts.

## Anti-patterns

- **Peak-TFLOP procurement**: Buying the largest arithmetic number for a memory-bound or low-batch workload.
- **Weight-only memory planning**: Ignoring gradients, optimizer state, activations, and framework overhead.
- **Uniform-fleet assumption**: Forcing one accelerator type onto training, serving, and exploratory workloads with different bottlenecks.
- **Air-cooling by default**: Scaling dense racks past the thermal envelope and discovering throttling after installation.

## Worked Example

A 175B-parameter training model cannot be planned from weight storage alone: gradients and Adam state expand the working set beyond one accelerator’s HBM. A node can bridge the capacity gap by combining HBM with host DDR5 and moving selected state across the hierarchy, but that saves capacity at a bandwidth cost. The placement decision then follows the staircase: keep high-frequency tensor exchanges inside an NVLink-connected node, use pipeline communication across a more tolerant boundary, and reserve inter-node links for traffic whose volume and cadence the fabric can sustain. The same model therefore drives memory budgeting, node topology, and pod design.

## Key Takeaways

1. Identify the active infrastructure wall before selecting a chip or adding nodes.
2. Use Roofline and sustained MFU, not peak FLOP/s, for performance and procurement.
3. Budget all training state and map each exchange to a bandwidth tier.
4. Design power, cooling, cabling, and reliability with the accelerator fleet as one system.

## Connects To

- **Chapter 3**: The inter-node bandwidth cliff becomes a network-fabric design problem.
- **Chapter 5**: Parallelism is constrained by node memory and the bandwidth staircase.
- **Chapter 8**: Schedulers must preserve NUMA and topology locality.
- **Chapter 9**: Roofline, memory walls, and kernel efficiency provide the local diagnosis.
