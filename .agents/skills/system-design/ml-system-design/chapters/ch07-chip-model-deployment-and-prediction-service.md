# Chapter 7: Model Deployment and Prediction Service

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 7

## Core Idea
Deployment is not “put the model behind an endpoint.” It makes model logic reliable, scalable, observable, updateable, and appropriate for its users. Serving mode, feature pipeline, hardware, and optimization jointly determine behavior.

## Frameworks Introduced
- **Machine learning deployment myths**: Plan for many models, performance decay from changing data, frequent updates, and scale; deployment is a continuing operating problem rather than a one-time handoff.
- **Three prediction modes**: batch prediction uses batch features; online prediction can use precomputed batch features; streaming prediction is online prediction augmented with streaming features.
- **Cloud-versus-edge placement**: Put computation where the cost, latency, connectivity, privacy, and device-resource constraints make the system viable.
- **Model compression and inference optimization**: Make inference faster, make the model smaller, or use faster hardware. Common compression families are low-rank factorization, knowledge distillation, pruning, and quantization.

## Key Concepts
- **Deployment**: Moving a model out of development so it runs in staging or production and is accessible to users.
- **Inference**: Generating predictions from a deployed model.
- **Online prediction**: Generate and return a prediction when a request arrives; useful when results must reflect current context.
- **Batch prediction**: Generate predictions periodically or on trigger, store them, and retrieve them later; optimized for throughput.
- **Streaming feature**: A feature computed from real-time transport data. An online feature may instead be a precomputed batch feature held for online serving.
- **Train-serving skew**: Training and inference pipelines compute different features or apply different transformations.
- **Intermediate representation (IR)**: A compiler-layer representation between framework code and hardware-native code.
- **Quantization**: Represent parameters with fewer bits, reducing memory and often improving speed, with possible rounding and range errors.

## Mental Models
- Treat deployment as a second system: a correct model can still fail through dependency, data, permissions, capacity, or pipeline errors.
- Choose serving mode from product consequences: freshness and unpredictable queries favor online serving; known workloads and latency pressure favor batch; a hybrid can precompute popular requests and serve the rest online.
- Treat every performance win as a trade-off to measure: compression can alter quality, and edge placement shifts burdens to device memory, battery, and update logistics.

## Anti-patterns
- **Deploying one or two models as if they were the whole application**: Products may need many models, making lifecycle tooling essential.
- **Assuming a deployed model stays good**: Data shifts and software rot mean performance must be monitored and models must be updateable.
- **Duplicating batch and streaming feature logic**: Divergent implementations create silent production bugs; unify the pipelines or use a feature store.
- **Benchmarking only a popular model or FLOPS**: Hardware utilization and end-to-end workload behavior matter more than headline capability.

## Worked Example
A DoorDash-like delivery-time model can combine a batch feature—the restaurant’s historical mean preparation time—with streaming features such as recent order volume and available couriers. Batch prediction can serve recommendations generated every few hours, but cannot react to changed preferences or unexpected requests. For a latency-sensitive model, a real-time pipeline must transport events, compute streaming features, invoke a fast model, and return the result. If the model is too slow, compression or hardware optimization can help. In the Roblox BERT case, replacing BERT with DistilBERT and quantizing to 8-bit integers produced a large serving improvement; quality still required measurement.

## Reference Table

| Choice | Strength | Cost or limitation |
|---|---|---|
| Batch | High throughput; can precompute complex predictions | Stale and limited to known requests |
| Online | Fresh response; handles unpredictable requests | Latency and serving-cost pressure |
| Cloud | Easy to start and elastic | Network latency, recurring cost, centralized data exposure |
| Edge | Low network dependence and local processing | Device compute, memory, battery, and update constraints |

## Key Takeaways
1. Define operational and user requirements before selecting a serving architecture.
2. Keep training and inference features consistent, especially when mixing batch and streaming data.
3. Optimize end-to-end latency, not just model execution time.
4. Treat export, dependencies, hardware, monitoring, and rollback as part of deployment.

## Connects To
- **Chapter 8**: Deployment creates the production environment where shifts, silent failures, and monitoring matter.
- **Chapter 9**: Safe updates require continual learning and test-in-production techniques.
- **Chapter 10**: Containers, model stores, feature stores, and ML platforms operationalize deployment.
- **Chapter 11**: Serving choices affect user experience, team boundaries, privacy, and responsible-AI trade-offs.
