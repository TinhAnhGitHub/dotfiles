## Constraint-first end-to-end design
**When to use**: Project start or when offline success cannot ship.
**How**: Define outcome, metric, guardrails, target, traffic, label delay, rollback owner. Apply D·A·M; estimate `Dvol/BW + O/(Rpeak·ηhw) + Llat`; revisit the binding term.
**Trade-offs**: Slower demo, less rework; simpler models may win over the project horizon. (Vol1 Ch 1–3; Chip Ch 2)

## Closed-loop lifecycle with stage contracts
**When to use**: Any system beyond one analysis.
**How**: Loop problem → data → model → validation → deployment → monitoring. Specify schema, freshness, ownership, lineage, tests, and acceptance at boundaries; route evidence upstream.
**Trade-offs**: Automation reduces coupling, debugging, and debt; model tests alone do not prove readiness. (Vol1 Ch 3, Ch 14; Chip Ch 2)

## Decouple objectives before combining decisions
**When to use**: Objectives conflict or change at different rates.
**How**: Estimate separate components; combine calibrated scores or a configurable policy layer with distinct owners/cadences. Document cost and Pareto trade-offs.
**Trade-offs**: More monitoring buys independent tuning; one score can hide harm. (Chip Ch 2; Vol1 Ch 15)

## Data-centric iteration and label loop
**When to use**: Errors cluster by label, cohort, condition, or feedback source.
**How**: Profile coverage/quality; inspect disagreements; fix labels/sampling before complexity. Use stratified sampling, active learning, or measured weak supervision; record provenance/delay.
**Trade-offs**: Targeted data can beat architecture tuning but costs annotation; pseudo-labels add bias. (Vol1 Ch 4; Chip Ch 4–5)

## Point-in-time feature pipeline
**When to use**: Time/event features or differing offline/online computation.
**How**: Record event/availability time, window, entity, version, and freshness SLA. Join only available values; reuse transforms and replay-test parity.
**Trade-offs**: Metadata prevents leakage/skew; a feature store does not replace validation/access control. (Vol1 Ch 4, Ch 14; Chip Ch 5, Ch 10)

## Batch/stream dual pipeline
**When to use**: Historical recomputation and fresh response both matter.
**How**: Batch backfills, joins, training; streams fresh features, labels, alerts, or updates. Use one contract; reconcile late events and compare outputs.
**Trade-offs**: Freshness costs duplicate logic, complexity, and consistency risk; quantify value first. (Vol1 Ch 4; Chip Ch 3, Ch 9)

## Distributed parallelism by bottleneck
**When to use**: Data/model exceeds one device or scaling stalls.
**How**: Data parallelism when replicas fit; tensor when layers do not and links are fast; pipeline when stages reduce memory and microbatches hide bubbles. Profile C3; map topology before combining.
**Trade-offs**: Data pays AllReduce; tensor needs fast links; pipeline adds bubbles/imbalance; more workers can reduce throughput. (Vol2 Ch 1, Ch 5–6)

## Overlap communication, I/O, and compute
**When to use**: Accelerators idle on loading, collectives, or sync.
**How**: Prefetch/cache, locality-friendly reads, overlap copies with kernels, and schedule collectives against backpropagation. Improve the slowest stage.
**Trade-offs**: Memory, contention, and profiling complexity rise; compression adds codec cost and possible quality effects. (Vol1 Ch 2, Ch 4, Ch 11; Vol2 Ch 4, Ch 6; Fregly Ch 1–4)

## Failure-as-steady-state training
**When to use**: Long or multi-node jobs.
**How**: Classify hardware, software, straggler, and silent-corruption faults. Add validation, fault injection, checkpoints, detection, restart, elastic recovery; balance cadence with Young–Daly.
**Trade-offs**: Checkpoints consume I/O/stall; redundancy costs capacity, but recovery preserves progress. (Vol2 Ch 7; Vol1 Ch 8)

## Serving as a latency-budgeted pipeline
**When to use**: Online prediction where isolated inference looks fast.
**How**: Budget p95/p99 across network, retrieval, parsing, preprocessing, inference, postprocessing, serialization; test peak/cold/warm load. Batch/cache predictable work.
**Trade-offs**: Faster forward pass may not improve E2E latency; caching stales, edge constrains resources/updates. (Vol1 Ch 13; Vol2 Ch 9–10; Chip Ch 7)

## Headroom plus bounded dynamic batching
**When to use**: Bursty accelerator-backed traffic.
**How**: Queue compatible requests for a bounded window; benchmark batch/latency curves; scale before the queueing knee; track tails and route around unhealthy replicas.
**Trade-offs**: Batching improves utilization/cost but adds wait and p99; saturation makes queues explode. (Vol1 Ch 13; Vol2 Ch 9–10)

## Hybrid inference and graceful fallback
**When to use**: Predictable inputs, failing dependencies, or strict latency/safety.
**How**: Precompute common cases; infer novel ones. On timeout, overload, missing features, low confidence, or unsafe output, use tested cache, heuristic, smaller model, or human review; measure the path.
**Trade-offs**: Availability rises but answers may stale/degrade; fallback must not conceal errors. (Vol1 Ch 2, Ch 13–14; Chip Ch 7, Ch 11)

## Reproducible artifact and environment boundary
**When to use**: Multiple teams, frequent releases, regulation, or incident reconstruction.
**How**: Version code, data/features/labels, config, seeds, dependencies, runtime, hardware assumptions, metrics, and weights. Register ownership/use/limits/evidence; promote the exact validated artifact.
**Trade-offs**: Metadata/storage buy rollback and reproducibility; containers miss some host/driver behavior. (Vol1 Ch 3, Ch 14; Chip Ch 6, Ch 10)

## Observable degradation with multi-speed feedback
**When to use**: Delayed labels, silent failures, or evolving populations.
**How**: Monitor service, data, predictions, outcomes, and slices; tag versions. Alert fast on operations, review proxies/outcomes slower, and assign owner/runbook.
**Trade-offs**: Telemetry costs storage/privacy budget; dashboards fatigue. Drift triggers investigation, not automatic retraining. (Vol1 Ch 3, Ch 14; Chip Ch 8)

## Safe model update and rollback
**When to use**: Any decision-changing update.
**How**: Gate offline/slice/replay tests, shadow, canary, then A/B for causal evidence. Predeclare sample, duration, window, primary metric, guardrails; keep/test rollback state.
**Trade-offs**: Staging lowers blast radius but slows learning; A/B needs traffic/delayed labels, shadow cannot prove outcomes. (Vol1 Ch 3, Ch 14; Chip Ch 9)

## Threat-model and privacy-by-design
**When to use**: Sensitive data, distributed clients, public endpoints, high-impact use, or adversaries.
**How**: Map assets/actors/paths; minimize retention; use least privilege, encryption, secure updates, audit, defense in depth. Consider local/federated processing and differential privacy with explicit utility budget.
**Trade-offs**: Controls cost utility, latency, effort, and sometimes subgroup accuracy; federated/local updates are not anonymous by default. (Vol2 Ch 13; Vol1 Ch 15; Chip Ch 11)

## Fairness, safety, and human-control gates
**When to use**: High-impact, safety-critical, or user-facing decisions.
**How**: Define harm/prohibited use; test slices/intersections, calibration, robustness, and edge cases. Add rejection, escalation, filters, model card; repeat after updates.
**Trade-offs**: Coverage, accuracy, latency, privacy, fairness, transparency conflict; some uses remain inappropriate to automate. (Vol1 Ch 3, Ch 15; Vol2 Ch 14, Ch 16; Chip Ch 11)

## Cost-aware automation and build/buy
**When to use**: Repeated retraining, many models, costly serving, or platform decisions.
**How**: Compare quality value, compute/storage/labor, rollout risk, and staleness. Automate when benefit exceeds intervention cost; buy commodity, build differentiation/control, start small.
**Trade-offs**: Managed tools add lock-in/integration/residency risk; in-house adds maintenance. (Vol1 Ch 14; Chip Ch 10)
