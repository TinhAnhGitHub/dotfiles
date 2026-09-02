# Chapter 4: Training Data

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 4

## Core Idea

Training data is the foundation of model behavior, including train, validation, and test splits rather than a finite, stationary “dataset.” Creating it is iterative: sample a useful population, obtain defensible labels, inspect bias and lineage, address imbalance or scarcity, and revise as the task and production distribution change. More data is not automatically better; low-quality labels or unrepresentative samples can make a model worse.

## Frameworks Introduced

Sampling families are nonprobability and random sampling. Convenience, snowball, judgment, and quota sampling help get started but carry selection bias. Simple random, stratified, weighted, reservoir, and importance sampling address different constraints. Label sources include hand, natural or behavioral, weak, semi-supervised, transfer-learning, and active-learning labels. Imbalance responses operate at metric, data, or algorithm level; augmentation uses label-preserving transformation, perturbation, or synthesis.

## Key Concepts

Simple random sampling gives every population member equal selection probability, but rare classes may disappear. Stratification samples within important groups; weighting encodes domain priorities or corrects a known distribution difference. Reservoir sampling maintains an equal-probability sample of an unbounded stream without knowing its eventual size. Importance sampling uses an easier proposal distribution and reweights its samples to represent a harder target distribution.

Hand labeling is expensive, slow, privacy-sensitive, and difficult to scale when expertise is required. Label multiplicity arises when annotators or sources disagree. Data lineage—where each sample and label came from—lets a team identify biased sources and explain regressions after new data is added.

Natural labels come from outcomes such as actual travel time, later stock price, clicks, purchases, ratings, disputes, or user corrections. Implicit negatives, such as no click within a chosen window, are assumptions rather than direct truth. Feedback loop length creates a speed-versus-accuracy trade-off: a short window enables rapid iteration but can label delayed positives as negative; a long fraud-dispute window gives stronger truth but delays detection.

When hand labels are scarce, weak supervision encodes expert heuristics as labeling functions, combines and denoises their conflicting outputs, and can apply them privately at scale. Semi-supervision expands a small seed set through high-confidence self-training, similarity, or perturbations. Transfer learning reuses a model trained on an abundant base task, such as language modeling, then uses it directly or fine-tunes it. Active learning asks annotators for uncertain or committee-disagreement examples rather than random ones.

Imbalance can hide rare classes, reward majority-class shortcuts, and expose asymmetric error costs. Overall accuracy can be misleading; inspect per-class metrics, precision, recall, F1, ROC or precision-recall behavior, and tune thresholds to the cost. Oversampling and undersampling alter training distributions but can overfit or discard information; cost-sensitive, class-balanced, and focal losses alter what errors the learner emphasizes. Never evaluate on resampled data.

Augmentation can crop, flip, or perturb images; make safe text substitutions; add noise; use adversarial examples; or synthesize template, mixup, or generated data. Every transformation must preserve the intended label.

## Mental Models

Sampling is a claim about the world your model will face. A label is a measurement with provenance and delay, not an unquestionable fact. Scarce labeling should be allocated where it changes the decision boundary or resolves uncertainty. Train distributions may be adjusted, but evaluation should represent deployment.

## Anti-patterns

- Treating convenient data as representative.
- Mixing annotators or sources without lineage or quality checks.
- Calling every non-click an immediate negative.
- Using accuracy on a rare-event problem.
- Oversampling before splitting or evaluating on the altered distribution.
- Applying augmentation that changes semantics while retaining the old label.

## Worked Example

For spam detection, begin with a random sample but stratify to preserve rare legitimate or spam cases. Use a small expert-labeled audit set to assess heuristic labeling functions, then combine programmatic labels and retain provenance. If positives remain rare, report precision-recall and choose a threshold for the cost of missed spam versus false alarms. Revisit the feedback window because delayed clicks or user reports can change labels.

## Key Takeaways

Design sampling, labels, splits, metrics, and feedback windows together. Invest in label quality and lineage. Use weak, semi-, transfer, and active learning strategically rather than pretending missing labels do not matter. Treat imbalance and augmentation as task-specific interventions, then validate against the real distribution.

## Connects To

Chapter 3 provides the pipelines and transports that produce data. Chapter 5 turns curated examples into features and guards against leakage; Chapter 6 uses the splits, labels, and metrics for model selection and offline evaluation.
