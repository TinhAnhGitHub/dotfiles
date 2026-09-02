# Chapter 6: Model Development and Offline Evaluation

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 6

## Core Idea

Model development is an experiment-driven stage, not the whole ML system. Choose an algorithm against the task, data, constraints, and assumptions; begin with a baseline and a simple model; track reproducible experiments; then evaluate robustness, fairness, calibration, and important slices before deployment. Offline scores are necessary but cannot guarantee production usefulness.

## Frameworks Introduced

Six selection lenses are avoiding the state-of-the-art trap, starting simple, controlling human comparison bias, considering present versus future performance, evaluating trade-offs, and understanding assumptions. Four adoption phases are non-ML heuristics, simple ML, optimization of simple models, and complex models. Ensembles use bagging, boosting, or stacking. Experiment tracking and versioning record code, data, hyperparameters, metrics, samples, and artifacts. Training can use data, model, and pipeline parallelism; AutoML ranges from hyperparameter search to architecture search.

## Key Concepts

Classical models remain valuable beside neural networks because they can require less labeled data, train and infer faster, and be easier to explain. Compare architectures fairly: unequal tuning effort creates human bias. Model assumptions include predictability from available inputs, independent and identically distributed examples, smoothness, tractable latent computations, boundary shape, conditional independence, or distributional assumptions. A model that violates the relevant assumption may be a poor production choice despite a strong benchmark score.

Ensembles can improve performance when base learners make less-correlated errors. Bagging trains models on bootstrap samples and aggregates votes or averages, reducing variance. Boosting reweights hard examples across sequential weak learners. Stacking trains a meta-learner over base outputs. These gains cost deployment and maintenance complexity, so the value of an improvement matters.

Track train and evaluation loss, metrics on non-test splits, predictions with labels, training speed, resource use, and changing hyperparameters. Version code, data, and artifacts; large data, privacy deletion requirements, unclear diffs, and nondeterminism make data reproducibility harder than code reproducibility. Debugging is difficult because models can fail silently, fixes require retraining, and faults can originate in data, labels, features, algorithms, code, or infrastructure.

Distributed data parallelism replicates the model and divides data; synchronous updates face stragglers, while asynchronous updates risk stale gradients. Model parallelism divides model components, and pipeline parallelism uses micro-batches to improve overlap. AutoML can tune hyperparameters or search architectures, but its compute cost and validation discipline remain real constraints. Never tune on the test split.

Offline evaluation starts with random, simple heuristic, zero-rule, human, and existing-solution baselines. A score without a baseline is hard to interpret, and a good system is not necessarily useful if users will not trust it or it does not beat the relevant process. Perturbation tests simulate noisy production inputs. Invariance tests check that sensitive changes do not change outputs. Directional tests check expected behavior. Calibration compares predicted probabilities with observed frequencies. Confidence can determine when to abstain or involve a human. Slice-based evaluation exposes subgroup failures, critical populations, and aggregation effects such as Simpson’s paradox; slices can come from domain heuristics, error analysis, or automated slice finding.

## Mental Models

Use the simplest adequate model as an instrument for learning and a baseline. Treat every offline score as conditional on data, split, metric, and test assumptions. Evaluate the model as a decision component: robustness, fairness, calibration, uncertainty, subgroup behavior, cost, and latency matter alongside accuracy.

## Anti-patterns

- Jumping to state-of-the-art architecture without a simple baseline.
- Comparing architectures after tuning one much more than another.
- Selecting by overall accuracy while hiding minority or critical-slice failures.
- Using test data to tune features, hyperparameters, or architecture.
- Tracking only a final score and losing the data, code, or artifact context.
- Assuming clean offline inputs, calibrated probabilities, or benchmark gains imply production success.

## Worked Example

For a cough classifier trained on clean hospital recordings, compare a heuristic and simple model first, then test candidates on clips with background noise, clipping, and microphone variation. Check calibration and confidence before showing predictions, inspect performance by device and user group, and compare against the human or existing workflow. Choose the model that remains useful under production conditions, not merely the clean-test winner.

## Key Takeaways

Baselines make metrics meaningful. Simplicity accelerates learning, deployment, and debugging. Track and version the full experiment context. Use ensembles or distributed and automated methods only when operational costs are justified. Before deployment, test robustness, invariance, directional behavior, calibration, confidence, and slices, while preserving a clean final test protocol.

## Connects To

Chapters 4 and 5 determine the labels, splits, and features being evaluated. Chapter 7 turns a selected model into a serving system; Chapters 8 and 9 test whether offline assumptions hold in production and support monitoring and continual updates.
