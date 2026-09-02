# Chapter 6: Network Architectures

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 6

## Core Idea
Architecture is infrastructure. MLPs, CNNs, RNNs, transformers, and sparse recommendation models encode different inductive biases, memory patterns, and parallelism constraints; choose among them by matching data structure and deployment limits.

## Frameworks Introduced
- **Architecture Selection Framework**: Map data to an initial family, then check memory, compute, inference speed, accuracy, and deployment readiness; loop back when a check fails.
- **Inductive Bias Hierarchy**: CNNs impose strong locality and sharing, RNNs impose temporal recurrence, MLPs impose little structure, and transformers learn adaptive relationships.
- **Lighthouse Models**: ResNet-50 probes compute, GPT-2/Llama probes bandwidth, DLRM probes capacity, MobileNetV2 probes edge latency, and keyword spotting probes power.

## Key Concepts
- **MLP**: Dense connectivity for tabular or weakly structured features.
- **CNN**: Local filters and weight sharing for spatial patterns and translation-related structure.
- **RNN**: Recurrent state for sequential dependencies, with an inherently sequential path.
- **Attention**: Content-dependent weighted routing between positions.
- **Transformer**: Attention, feed-forward layers, residual connections, normalization, and positional information without recurrence.
- **Sparse embedding architecture**: Recommendation design in which large categorical tables dominate capacity and access behavior.
- **Arithmetic intensity**: The relationship between useful arithmetic and data moved, indicating likely compute or bandwidth pressure.
- **KV cache**: Stored key/value state that grows with context and concurrency during autoregressive serving.

## Mental Models
Choose an architecture as a hypothesis about structure: locality suggests CNNs, temporal dependence suggests RNNs, arbitrary feature relationships suggest MLPs, complex long-range relations suggest transformers, and high-cardinality categorical inputs suggest DLRM-style embeddings. FLOPs are not speed; operation shapes, reuse, memory traffic, and hardware utilization decide throughput. For transformers, distinguish training/prefill from decoding: the former parallelizes positions but faces dense attention cost, while the latter repeatedly streams weights and cache state.

## Anti-patterns
- **Leaderboard selection**: Accuracy without resource and deployment analysis produces infeasible systems.
- **“More complex is better”**: A mismatched inductive bias can need more data and cost more while performing worse.
- **FLOP counting alone**: MobileNetV2’s lower operation count does not guarantee faster execution on every accelerator.
- **Ignoring sequence state**: Transformer capacity planning that budgets weights but not attention storage or KV cache will fail at context or concurrency.
- **Transferring training assumptions**: A GPU-friendly architecture may violate edge memory, power, or latency limits.

## Worked Example
For offline wildlife monitoring, camera images contain local, translation-invariant, hierarchical visual features, so a CNN is the natural starting point. ResNet-50 is too compute- and power-heavy; a tiny keyword-spotting network lacks visual capacity. A MobileNetV2 variant with 0.75 width and INT8 weights is selected, then checked against 512 MB RAM, a 500 ms detection target, and an approximately 2 W average power budget. The estimated 209 ms inference leaves room for system overhead, but accuracy and six-month battery life still require target-device validation.

## Key Takeaways
1. Match inductive bias to data before tuning implementation.
2. Validate memory, compute, latency, accuracy, power, and deployment hardware in sequence.
3. Treat quadratic attention and recurrent paths as structural constraints.
4. Profile the target regime; training, prefill, and decoding can bind differently.
5. Architecture choice is a deployment decision, not only a modeling decision.

## Connects To
- **Chapter 2**: Deployment paradigms define the constraints architecture must satisfy.
- **Chapter 5**: Architectures compose the neural computations and gradient paths.
- **Chapter 7**: Frameworks translate architectural graphs into hardware execution.
- **Chapter 8**: Training memory and parallelism follow architectural structure.
