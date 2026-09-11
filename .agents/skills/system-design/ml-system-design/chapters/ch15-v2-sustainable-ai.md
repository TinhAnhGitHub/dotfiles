# Chapter 15: Sustainable AI

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 15

## Core Idea
Sustainable AI treats energy, water, carbon, materials, and hardware lifetime as first-order system constraints alongside accuracy, latency, and reliability. The relevant boundary is the whole lifecycle: manufacturing and construction, training, inference, cooling and power delivery, regional grid mix, reuse, and end-of-life—not a single accelerator metric or one training run.

## Frameworks Introduced
- **Lifecycle assessment**: Account for operational energy, embodied manufacturing carbon, grid intensity, hardware lifetime, water, and e-waste across training and serving. Use it before declaring a local optimization sustainable.
- **Measurement stack**: Measure workload energy at hardware and system boundaries; track energy per operation, energy per byte, utilization, PUE, carbon intensity, and workload-level carbon. Use the metric that exposes the active bottleneck.
- **Training-versus-inference analysis**: Training may dominate research workloads, while recurring inference can dominate a deployed service. The prefill/decode split matters environmentally because decode is structurally memory-bandwidth-bound and can draw power while arithmetic units wait.
- **Multi-layer mitigation**: Choose among algorithmic design, hardware/software co-design, infrastructure and cooling, carbon-aware scheduling, hardware longevity, and usage governance according to the measured lifecycle term.
- **Jevons Paradox of AI**: Efficiency lowers unit cost, which can increase demand enough to erase or exceed savings. Pair efficiency with absolute carbon or energy budgets.

## Key Concepts
- **Sustainable AI**: Engineering the full environmental cost into architecture decisions.
- **PUE**: Power Usage Effectiveness, a facility-level measure of overhead beyond IT equipment.
- **Operational carbon**: Emissions associated with electricity consumed during use.
- **Embodied carbon**: Manufacturing and infrastructure emissions incurred before or independent of runtime.
- **Energy per byte**: A memory-movement metric that exposes data-transfer cost.
- **Arithmetic intensity**: The computation-to-data-movement relationship used to reason about energy roofs.
- **Carbon-aware scheduling**: Moving flexible work across time or regions with lower grid carbon intensity.
- **Demand rebound**: Extra usage that consumes efficiency savings.

## Mental Models
- Power is an existence constraint: a fleet that cannot be powered or cooled cannot be deployed, regardless of model quality.
- Count joules where work happens, then follow the resource upstream and downstream through manufacturing, grid, cooling, and disposal.
- When the bottleneck is unused structure, use pruning; when it is bit width or memory movement, use quantization; when repeated serving dominates, consider distillation or a smaller model.
- Efficiency is necessary but not sufficient. Ask whether usage governance keeps absolute consumption beneath the budget.

## Anti-patterns
- **Report only training emissions**: Long-lived, high-volume inference may dominate total energy.
- **Treat renewable sourcing as the whole answer**: Embodied carbon and hardware lifetime remain material.
- **Use PUE or FLOP/s per watt as a complete sustainability metric**: These omit grid intensity, memory movement, demand growth, and lifecycle impacts.
- **Optimize one component boundary**: A smaller model can shift work into inference, communication, or retraining.
- **Assume cheaper computation is automatically greener**: Jevons rebound can turn efficiency into greater absolute demand.

## Worked Example
The chapter’s GPT-3-sized illustration uses 1,287 MWh of training energy and a representative US grid intensity of 0.429 kg CO2/kWh, yielding roughly 552,123 kg of operational emissions. Moving the same flexible workload to a much lower-carbon hydro-powered region reduces the illustrative emissions by about 21.4×. That is not a claim that location solves sustainability: the lifecycle boundary still includes embodied hardware, cooling, water, hardware replacement, and future serving demand. For a high-volume service, profile decode memory movement and compare quantization, batching, distillation, placement, and demand limits against the recurring inference term.

## Key Takeaways
1. Sustainability is a physical viability constraint, not a reporting add-on.
2. Measure training, inference, embodied carbon, grid mix, cooling, water, and lifetime together.
3. Decode’s bandwidth-bound behavior makes memory efficiency important for cloud and edge sustainability.
4. Match pruning, quantization, distillation, placement, and scheduling to the measured bottleneck.
5. Pair efficiency with absolute budgets to prevent demand rebound.

## Connects To
- **Chapter 2**: Power delivery, cooling, and memory hierarchy establish the physical ceiling.
- **Chapter 10**: Serving volume, decode, batching, and quantization drive recurring energy.
- **Chapter 11**: Edge and federated workloads trade data transfer for battery and device-lifetime constraints.
- **Chapter 16**: Environmental justice and governance determine who bears system costs and how limits are enforced.
