# Chapter 14: ML Operations

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 14

## Core Idea
ML Operations (MLOps) keeps a deployed ML system correct, reproducible, and changeable over time. Availability and latency can remain healthy while predictions become wrong because data, user behavior, or the world changed. MLOps connects data, training, artifact management, deployment, monitoring, feedback, and rollback into a continuing production lifecycle.

## Frameworks Introduced
- **MLOps foundations**: Version code, data, features, configurations, model artifacts, and environments; automate tests and promotion while preserving lineage.
- **Technical-debt lens**: Hidden shortcuts in data dependencies, pipelines, interfaces, and monitoring accumulate interest as maintenance, incident, and change costs.
- **CI/CD for ML**: Continuous integration validates code and data contracts; continuous delivery promotes tested model artifacts through controlled environments.
- **Production operations loop**: Observe system and model behavior, investigate drift or incidents, retrain when evidence supports it, validate the candidate, and deploy or roll back safely.
- **Maturity framework**: Progress from manual, notebook-driven processes toward repeatable pipelines, automated validation, monitoring, governance, and dependable retraining.
- **Deployment strategies**: Canary, shadow, blue-green, and gradual traffic shifting reduce blast radius while comparing versions on real or replayed traffic.

## Key Concepts
- **Model registry**: Tracks candidate and production artifacts, metadata, lineage, approvals, and versions.
- **Feature store**: Helps align feature definitions and availability between training and serving, reducing training-serving skew.
- **Data drift**: Change in input distribution; it is a signal for investigation, not proof of quality failure.
- **Concept or label drift**: Change in the relationship between inputs and outcomes, often requiring delayed labels or downstream feedback to detect.
- **Observability**: Metrics, logs, traces, prediction distributions, slice quality, data quality, and operational alerts.
- **Reproducibility**: Ability to reconstruct how a model was trained and deployed from recorded inputs, code, and configuration.
- **Rollback**: Restore a known-good version when a release harms quality, reliability, or cost.
- **Human-in-the-loop**: Route uncertain, novel, or high-impact cases for review and feedback.

## Mental Models
Treat production as a feedback system, not a finish line. “Green” infrastructure dashboards do not establish semantic correctness. Drift detection is triage: distribution change should prompt diagnosis, label collection, slice analysis, and a decision—not automatic retraining on every fluctuation. Also treat models as governed artifacts with dependencies, not standalone files; a rollback may require restoring feature logic, preprocessing, runtime, and data contracts together.

## Anti-patterns
- **Notebook-to-production handoff**: Manual, undocumented steps make releases irreproducible.
- **Monitoring only uptime**: Healthy servers can produce degraded or biased predictions.
- **Automatic retraining without gates**: Feedback loops can amplify errors or train on unvalidated labels.
- **Unversioned data and features**: Teams cannot explain, reproduce, or safely roll back behavior.
- **All-at-once release**: A bad model reaches every user before evidence is available.
- **Alert overload**: Thresholds without ownership or runbooks produce ignored signals.

## Worked Example
A fraud model’s latency and availability remain normal, but a monitored input slice shifts after a new payment flow launches. The team freezes the model’s lineage and compares current predictions with delayed outcomes, finding a quality regression for that slice. A candidate retraining pipeline uses versioned data and feature definitions, passes offline and fairness checks, then runs in shadow and canary modes. Since the canary worsens a protected metric, traffic returns to the prior registry artifact. The incident produces a new data contract, alert owner, and rollback runbook rather than an unreviewed automatic retrain.

## Key Takeaways
1. Build reproducibility and lineage before automating promotion.
2. Monitor semantic quality and drift alongside system health.
3. Use staged deployment, explicit gates, and fast rollback.
4. Treat technical debt as a measurable production risk.
5. Retrain from evidence, with validation and accountable ownership.

## Connects To
- **Chapter 9**: Data selection and labeling choices must remain traceable in production pipelines.
- **Chapter 12**: Benchmark baselines become release gates and regression evidence.
- **Chapter 13**: Serving health, capacity, and model readiness feed operations.
- **Chapter 15**: Governance, privacy, fairness, and accountability extend operational quality.
