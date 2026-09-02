# Chapter 8: Data Distribution Shifts and Monitoring

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 8

## Core Idea
A model can be correct in development and still fail in production because software breaks, the data changes, edge cases appear, or the system’s outputs alter future inputs. Monitoring must therefore cover both operational health and ML behavior, and must make failures diagnosable rather than merely visible.

## Frameworks Introduced
- **Two classes of failure**: Software failures include dependency, deployment, hardware, downtime, and crashes; ML-specific failures include train-serving skew, data shifts, edge cases, and degenerate feedback loops.
- **Data distribution shift taxonomy**: Covariate shift changes the input distribution; label shift changes the output prevalence while input-given-label behavior remains stable; concept drift changes the relationship between input and output. Production may contain several shifts at once.
- **Monitoring versus observability**: Monitoring tracks metrics and logs to detect problems. Observability instruments the system so its internal behavior can be inferred and investigated from runtime outputs.
- **Four monitoring artifacts**: Track accuracy-related metrics when labels arrive, predictions, features, and raw inputs. Deeper artifacts are more structured but can also reflect more processing errors.

## Key Concepts
- **Silent failure**: An ML performance expectation is violated without an obvious operational error.
- **Source distribution**: The data distribution used for training.
- **Target distribution**: The distribution encountered during inference.
- **Train-serving skew**: A mismatch between training-time and production-time data processing.
- **Edge case**: An input on which model performance is catastrophically worse, not merely an unusual input.
- **Degenerate feedback loop**: Outputs influence user behavior, which becomes future training input and reinforces the original output.
- **Two-sample test**: A statistical test for whether two populations differ beyond expected sampling variation.
- **Alert fatigue**: Reduced attention caused by too many low-value alerts.

## Mental Models
- “The model is up” is not the same as “the ML system is healthy.” Check uptime, latency, throughput, resource use, prediction distributions, features, and eventual labels.
- Prefer a ladder of evidence: validate schemas and summary statistics first, use distribution tests carefully, then inspect slices and logs to find causes.
- A drift signal is not a diagnosis. First distinguish real environmental change from pipeline bugs, missing values, wrong versions, or schema changes.
- Choose time windows deliberately. Sliding statistics reveal local incidents; cumulative statistics can hide a short, damaging dip. Seasonal cycles require windows that expose the cycle.

## Anti-patterns
- **Monitoring only accuracy**: Labels may be delayed or unavailable, so serious prediction failures can remain invisible.
- **Treating every feature shift as harmful**: Most feature changes are benign; indiscriminate alerts create fatigue.
- **Relying on mean, median, and variance alone**: Similar summaries do not prove distributions are identical, while statistical significance does not prove practical importance.
- **Ignoring feedback effects**: Ranking only popular items or candidates with a favored resume attribute can amplify exposure and selection bias.

## Worked Example
A grocery demand model initially performed well, then overestimated some items and underestimated others, causing waste and lost sales. The failure was not discovered by a deployment crash; the business noticed a persistent performance problem after the environment had changed. A useful investigation would compare recent predictions with delayed labels, validate feature schemas and ranges, inspect input and prediction distributions over suitable windows, and trace transformations through logs. For a recommender, also measure output diversity and performance across popularity buckets: increasingly homogeneous recommendations can indicate a degenerate feedback loop. Small randomized exposure can provide less biased feedback, though it may reduce immediate user relevance.

## Key Takeaways
1. Define explicit operational and ML performance expectations before choosing monitors.
2. Instrument inputs, transformations, predictions, feedback, model versions, and request context for diagnosis.
3. Use both fast proxy signals and delayed ground-truth metrics.
4. Investigate alerts for root cause before retraining; human errors often masquerade as drift.
5. Monitor slices and edge cases, not only aggregate metrics.

## Connects To
- **Chapter 7**: Separate batch and streaming paths are a major source of train-serving skew.
- **Chapter 9**: Monitoring detects when an update may be needed; continual learning performs and evaluates it.
- **Chapter 10**: Logs, workflows, model stores, and feature stores supply the instrumentation and lineage monitoring needs.
- **Chapter 11**: Monitoring must expose subgroup harms, privacy risks, and user-facing failures.
