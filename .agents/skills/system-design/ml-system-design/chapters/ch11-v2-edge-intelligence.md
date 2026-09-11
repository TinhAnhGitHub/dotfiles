# Chapter 11: Edge Intelligence

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 11

## Core Idea
Edge intelligence moves inference, adaptation, or coordination toward the devices that observe the world. It exists where cloud round trips are too slow, raw data cannot leave, connectivity is intermittent, or personalization must follow local context. The data-center fleet’s abundance becomes the edge’s scarcity: milliwatts, megabytes, thermal headroom, and heterogeneous hardware.

## Frameworks Introduced
- **Edge learning paradigm**: Place computation where data and adaptation matter, then exchange selective updates rather than raw observations. Use it for local autonomy, privacy-sensitive inputs, and disconnected operation.
- **Three adaptation levers**: Freeze most weights or use small adapters; exploit few-shot/streaming data and experience replay; coordinate population learning through federated learning. Select the combination that fits memory, energy, privacy, and convergence limits.
- **Federated learning lifecycle**: Clients train locally, send privacy-preserving updates, and receive an aggregated model. At scale, client scheduling, non-IID data, dropout, stragglers, asynchronous synchronization, rollback, and observability are protocol concerns, not cleanup.

## Key Concepts
- **On-device learning**: Local training or adaptation without requiring server connectivity.
- **Hyper-personalization**: Adaptation to a user’s vocabulary, habits, sensors, or environment.
- **Weight freezing**: Keep most parameters fixed and update a small trainable subset.
- **Adapters/LoRA**: Compact structured or low-rank parameter updates.
- **Sparse updates**: Transmit or modify only selected parameters or gradients.
- **Experience replay**: Reuse representative prior examples to reduce catastrophic forgetting.
- **Non-IID data**: Client data distributions differ across users or devices.
- **Hardware-in-the-loop validation**: Test models and update paths on the device classes that will run them.

## Mental Models
- “The CPU coordinates; the NPU enables survival”: specialized inference silicon is a feasibility margin, not merely a speedup.
- Learning multiplies the deployment footprint: activations, gradients, optimizer state, and bidirectional traffic make local training far more expensive than inference-only execution.
- Bandwidth beats advertised TOPS for on-device generation; memory movement and locality can bind before peak compute.
- Federated learning is population learning under partial participation, not centralized training with a different transport.

## Anti-patterns
- **Treat a phone as a small data center**: Battery, thermal throttling, memory bandwidth, and intermittent links change the design regime.
- **Train every parameter locally**: The update footprint and optimizer state can exceed device budgets.
- **Centralize raw telemetry by default**: It spends privacy and communication budgets that local processing could preserve.
- **Ignore non-IID data and dropout**: A nominally convergent algorithm can produce biased or stale global models under real participation.
- **Deploy one binary to a heterogeneous fleet**: Device capability, version skew, and rollback paths must be explicit.

## Worked Example
Consider a voice assistant that works in a cloud-trained generic model but misses a user’s accent and household vocabulary. A local adapter can learn from a small stream without moving raw audio. Experience replay preserves representative older examples so personalization does not erase general language ability. The device uploads only a sparse or adapter update when connectivity and battery policy permit; a federated coordinator aggregates updates from many users while handling clients that are offline or slow. The production pipeline validates the resulting model on representative phone, gateway, and microcontroller classes, monitors privacy-preserving aggregate signals, and retains a rollback version. This architecture spends local compute and coordination to avoid latency, raw-data transfer, and permanent staleness.

## Key Takeaways
1. Edge learning is a C³ problem in which scarcity, not cluster scale, binds first.
2. Quantization, locality, small updates, and specialized hardware are survival requirements.
3. Few-shot data reuse and replay are as important as parameter-efficient adaptation.
4. Federated systems must design for non-IID data, stragglers, churn, privacy, and rollback.
5. Edge MLOps needs device-aware validation, monitoring, version management, and safe recovery.

## Connects To
- **Chapter 10**: Data-center prefill/decode and memory principles reappear under mobile bandwidth and power limits.
- **Chapter 12**: Fleet operations extends MLOps to millions of heterogeneous devices.
- **Chapter 13**: Federated updates and local data reduce exposure but do not eliminate privacy or security threats.
- **Chapter 15**: Battery, energy, hardware lifetime, and carbon accounting determine sustainable edge design.
