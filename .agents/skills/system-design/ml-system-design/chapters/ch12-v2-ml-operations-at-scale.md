# Chapter 12: ML Operations at Scale

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 12

## Core Idea
Operating one model with scripts and manual judgment is different from operating a portfolio. As model count grows, shared data, feature, infrastructure, and ownership dependencies create combinatorial complexity. Platform engineering turns per-model toil into shared control-plane capabilities: registries, lineage, CI/CD, monitoring, capacity management, and recovery.

## Frameworks Introduced
- **The N-Models problem**: The operational object becomes a dependency graph of models, features, pipelines, alerts, and owners. Use it when local changes can cascade across consumers or dashboards and on-call work no longer compose.
- **Fleet economics and TCO**: Treat training, inference, data, and iteration as distinct cost centers. Early-stage cost may be iteration-dominated; mature, high-traffic services often become inference-dominated. Use lifecycle cost to justify platform investment and choose optimization targets.
- **Layered ML operations**: Combine model registries and lineage, ensemble-aware CI/CD, staged rollout, hierarchical monitoring, feature-store correctness, platform resource management, and incident response. No single pipeline abstraction is enough.
- **Risk-matched operations**: Release cadence, validation gates, rollout duration, rollback speed, and human review should follow model risk and traffic consequences rather than one organization-wide default.

## Key Concepts
- **Platform thinking**: Shared services amortize infrastructure and operational effort across models.
- **Feature store**: Central management of feature computation, storage, serving, freshness, and lineage; it targets training-serving skew.
- **Training-serving skew**: A mismatch between feature construction during training and production serving.
- **Statistical multiplexing**: Shared capacity works because independent workloads’ peaks rarely coincide.
- **Validation gates**: Performance, latency, fairness, and data-quality checks that can block release.
- **Hierarchical monitoring**: Aggregate fleet signals while retaining model- and service-level drill-down.
- **ML productivity goodput**: Productivity measured by useful progress rather than raw resource consumption.
- **Point-in-time correctness**: Features must reflect only information available at prediction time.

## Mental Models
- At small scale, optimize a model; at portfolio scale, optimize interactions and marginal operational cost.
- A deployment is a graph change, not a file upload: trace upstream data, downstream models, owners, traffic, and rollback state.
- Alerting is a scarce capacity budget. Suppress noise, aggregate intelligently, and preserve actionable paths to ownership.
- A platform is successful when the hundredth model adds a small amount of work rather than another bespoke operating surface.

## Anti-patterns
- **Replicate artisanal pipelines**: Hundreds of bespoke jobs multiply configuration drift, testing debt, and incident surfaces.
- **Monitor every model independently**: Per-model dashboards miss cross-model failures and exhaust on-call attention.
- **Use one rollout policy**: LLMs, fraud systems, recommenders, and edge fleets have different blast radii and recovery needs.
- **Ignore feature lineage and freshness**: A healthy endpoint can serve stale or temporally invalid features.
- **Treat toil and deployment delay as inevitable**: They are measurable leading indicators of failed platform boundaries.

## Worked Example
A team manages 100 GPUs with dedicated quotas and 70% average idle time. A shared multi-tenant platform lowers idle time to 30% by statistically multiplexing workloads and reusing capacity. For the same useful work, work per GPU rises by roughly 0.70/0.30, and the chapter’s example estimates a 57.1% hardware reduction, about $1M annually on a $1.75M budget. The saving is not a license to remove controls: quotas, isolation, cost attribution, validation gates, and hierarchical alerts are what make sharing safe. The same platform can run staged canaries, collect fleet telemetry, and roll back a model or dependency change before a shared feature update damages downstream consumers.

## Key Takeaways
1. The N-Models transition is a qualitative complexity change, not linear scaling.
2. Registries, lineage, feature correctness, and shared CI/CD prevent local changes from becoming hidden fleet failures.
3. Monitoring must combine fleet aggregates with model-specific diagnostics and cost visibility.
4. TCO makes inference, iteration, data, and platform investments comparable.
5. Edge version skew and hardware-in-the-loop testing belong in normal operations.

## Connects To
- **Chapter 10**: Serving SLOs, batching, routing, and inference cost become operational objectives.
- **Chapter 11**: Device churn and heterogeneous clients extend the fleet beyond data centers.
- **Chapter 13**: Provenance, access control, privacy-aware telemetry, and audit evidence are platform functions.
- **Chapter 16**: Fairness and accountability checks must be release and monitoring controls, not later review.
