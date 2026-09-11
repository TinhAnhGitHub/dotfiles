# Chapter 5: Distributed Training

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 5

## Core Idea

Distributed training is a constrained partitioning problem: split model state, data, and work so memory fits and useful computation outweighs communication, synchronization, and pipeline bubbles. The **3D Parallelism Cube**—data, pipeline, and tensor axes—makes the choices explicit; hybrid configurations place each exchange on a bandwidth tier it can tolerate.

## Frameworks Introduced

- **3D Parallelism Cube**: Data parallelism replicates a model replica across batches; tensor parallelism splits layer computations; pipeline parallelism splits layers into stages. Use the product of the three degrees to reason about fleet size and placement.
- **Data parallelism**: Each worker computes on distinct data, then synchronizes gradients, usually with AllReduce. Use it for throughput when the model fits and communication can be amortized.
- **ZeRO/FSDP sharding**: Partition parameters, gradients, and optimizer state rather than replicating all state. Use it when memory is binding, accepting extra communication and coordination.
- **Scaling wall / Fleet Law**: More workers eventually reduce local compute time faster than communication and synchronization can shrink. Use scaling efficiency and exposed step components to decide when to stop scaling.
- **Parallelism selection decision tree**: Check memory fit first, then communication frequency, bandwidth placement, batch/convergence effects, and pipeline utilization.

## Key Concepts

- **Global batch**: The aggregate batch represented by all workers and any gradient accumulation.
- **BSP**: Bulk Synchronous Parallel execution in which all ranks meet at barriers.
- **SSP/ASP**: Bounded-staleness and asynchronous alternatives that trade consistency for less waiting.
- **Communication wall**: Scaling limit caused by gradient or activation exchange.
- **Pipeline bubble**: Idle warm-up and drain time around stage execution.
- **Tensor parallelism**: Sharding matrix operations, often with frequent AllReduce.
- **Expert parallelism**: Distributing MoE experts and routing tokens with AllToAll.
- **MFU**: Useful model computation relative to accelerator peak, a local/fleet productivity signal.

## Mental Models

Treat parallelism as loop transformation: decide which loop is replicated, partitioned, or pipelined, then account for its communication. Put high-frequency tensor traffic inside a node; use pipeline and data parallelism across slower links. Use data parallelism to buy throughput, model sharding to buy capacity, and pipeline parallelism to buy model fit at the price of bubbles. Above the critical batch size, extra workers may add little optimization benefit even if hardware remains available.

## Anti-patterns

- **Assuming linear scaling**: Ignores the communication wall and shrinking compute fraction.
- **Sharding for free**: Counts saved memory but not parameter gathers, reduce-scatter, latency, or overlap requirements.
- **Placing tensor parallelism across weak links**: Turns per-layer synchronization into a cross-node stall.
- **Blind gradient accumulation**: Reduces synchronization frequency but changes update cadence and may harm convergence.
- **Ignoring workload shape**: Treats dense LLMs, sparse embeddings, and MoE routing as one communication pattern.

## Worked Example

For a model too large for one accelerator, first use tensor parallelism within an NVLink-connected node so layer shards can exchange activations quickly. Partition layers into pipeline stages across nodes, using micro-batches to keep stages busy and reduce the bubble. Replicate the resulting model pipeline with data parallelism to process more data. The resulting 3D configuration is feasible only if each axis matches a physical link tier and if the global batch and optimizer schedule remain acceptable. If model state still does not fit, add ZeRO/FSDP sharding, then measure whether the added collectives erase the memory benefit.

## Key Takeaways

1. Select parallelism from memory, communication, topology, and convergence constraints.
2. Use the 3D Cube to map axes to hardware, not just to count GPUs.
3. Measure scaling efficiency and exposed communication before adding workers.
4. Treat batch size, staleness, bubbles, and sharding overhead as algorithmic costs.

## Connects To

- **Chapter 2**: Memory capacity and the bandwidth staircase constrain partitioning.
- **Chapter 3**: Fabric topology determines viable placement.
- **Chapter 6**: Each parallelism axis manifests as particular collectives.
- **Chapter 7**: Distributed jobs need checkpoints, elastic recovery, and fault-aware state.
- **Chapter 8**: Orchestration allocates complete, topology-compatible groups.
