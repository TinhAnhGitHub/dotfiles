# Chapter 9: Continual Learning and Test in Production

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 9

## Core Idea
Continual learning is the infrastructure and process that lets a model update when needed, often in micro-batches, while preserving a safe champion model. The update loop is incomplete without evaluation: offline tests, recent-data backtests, and controlled production experiments must work together.

## Frameworks Introduced
- **Champion–challenger updating**: Keep the deployed champion unchanged, train an updated challenger on fresh data, evaluate it, and promote it only when it is better and safe enough.
- **Stateless versus stateful training**: Stateless retraining starts from scratch; stateful training continues from a checkpoint using fresh data. Stateful training can reduce data and compute needs, but occasional from-scratch calibration remains useful.
- **Four stages of continual learning**: (1) manual, stateless retraining; (2) automated, stateless retraining; (3) automated, stateful training; (4) continual learning triggered by time, performance, volume, or detected drift.
- **Test in production**: Use shadow deployment, A/B testing, canary release, interleaving, or bandits to learn how a candidate behaves with live traffic.

## Key Concepts
- **Catastrophic forgetting**: A model, especially a neural network, abruptly loses previously learned information when learning new information.
- **Data iteration**: Refresh an unchanged architecture and feature set with new data.
- **Model iteration**: Add features or change the architecture; generally requires training from scratch.
- **Label computation**: Derive training labels from behavioral events and logs.
- **Backtest**: Evaluate on a recent historical period that was not used for the update.
- **Shadow deployment**: Run candidate and champion on the same requests but serve only the champion.
- **Canary release**: Gradually route traffic to a candidate and abort if key metrics degrade.
- **Bandit**: Route traffic adaptively to balance exploration with using the currently better model.

## Mental Models
- Faster updating is valuable only when fresher data improves performance enough to justify collection, labeling, compute, and evaluation costs.
- Continual learning is not necessarily per-example learning. Micro-batches match hardware better and reduce some risks.
- Evaluation is a product pipeline, not an individual’s ad hoc judgment: define tests, order, thresholds, promotion gates, ownership, and review.
- Production is the final distribution test, but exposure should be graduated according to risk and evidence.

## Anti-patterns
- **Updating the live model in place**: A bad update can remove the last known-good fallback.
- **Assuming a fixed daily schedule is optimal**: Different models and environments decay at different rates; measure the value of data freshness.
- **Using only an old static split**: It cannot represent a new distribution. Using only a recent backtest is also unsafe if that data is corrupted, so retain a trusted static sanity check.
- **Blindly choosing A/B testing**: It needs random assignment, adequate samples, and awareness of interference between variants.
- **Letting the model learn unfiltered from users**: Coordinated manipulation can rapidly teach a system harmful behavior, as the Tay incident illustrates.

## Worked Example
For a fraud detector, fresh data may arrive quickly, but fraud labels are rare and imbalanced. A payment company therefore needed roughly two weeks of live outcomes before an A/B comparison was trustworthy; evaluation, rather than training, set the update cadence. A safer pipeline would train a challenger, run static checks and a recent backtest, shadow it to compare outputs, then expose it through a randomized experiment or canary with explicit rollback thresholds. If feedback is short and online, a bandit can move traffic toward stronger variants while still exploring, but it requires stateful payoff tracking and is harder to operate.

## Key Takeaways
1. Build lineage for checkpoints, data, features, code, and evaluation results.
2. Separate data iteration from model iteration when allocating engineering effort.
3. Make fresh-data access and label computation streaming-capable where the use case demands it.
4. Automate evaluation and promotion gates before increasing update frequency.
5. Preserve a trusted champion and a rollback path at every stage.

## Connects To
- **Chapter 8**: Drift and monitoring supply triggers and signals for model updates.
- **Chapter 7**: Online prediction and streaming features enable fast feedback and production experiments.
- **Chapter 10**: Schedulers, orchestration, model stores, and feature stores make the update loop reproducible.
- **Chapter 11**: Human review, domain expertise, and responsible evaluation constrain what should be automated.
