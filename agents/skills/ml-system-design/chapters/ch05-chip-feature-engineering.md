# Chapter 5: Feature Engineering

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 5

## Core Idea

The right features often improve a workable model more than clever algorithmic changes. Feature engineering selects information and converts it into a representation usable at training and inference. Deep learning learns many representations from raw text and images, but production systems still need domain knowledge for behavioral, categorical, temporal, and operational signals. Features carry costs in leakage risk, coverage, latency, memory, and maintenance.

## Frameworks Introduced

The chapter contrasts learned and handcrafted features, then surveys missing-value handling, scaling, discretization, categorical encoding, feature crossing, embeddings, and positional/Fourier features. Its safety framework is data leakage: information related to the label enters features even though it will not be available at inference. Good features are evaluated by model importance and generalization to unseen data.

## Key Concepts

Classical text pipelines normalize text, create n-grams, build a vocabulary, and encode counts; deep models reduce some manual work through tokenization and learned representations. Yet a spam model may also need comment votes, account age and activity, and thread views. Embeddings represent words, products, images, users, or positions as vectors. Transformers process tokens in parallel, so positional information must be supplied; positions can be learned embeddings or fixed sine/cosine-style features.

Missingness is informative. Missing not at random relates to the unobserved value, missing at random relates to another observed variable, and missing completely at random has no discernible pattern. Deleting rows or columns can lose signal and create bias. Imputation with defaults or mean, median, or mode can inject bias, confuse missing with a legitimate value, and create leakage. Feature scaling puts numeric variables on comparable ranges; standardization and log transformation address different distribution assumptions. Fit statistics on the training split and reuse them for validation, test, and inference.

Discretization bins continuous values, which can help limited-data models but introduces discontinuities. Production categories evolve: an unseen brand, user, domain, or IP can break a fixed encoder. An `UNKNOWN` bucket can conflate unlike new categories. Feature hashing fixes representation size and handles unseen categories, trading collisions for bounded infrastructure.

Feature crossing combines variables to expose nonlinear interactions, useful for models that cannot learn them easily, but it can explode the feature space and overfit. Leakage commonly comes from random splits of time-correlated data, scaling before splitting, imputing from all data, duplicates across splits, correlated groups such as multiple scans from one patient, and quirks of data generation. Split by time when predicting the future, remove duplicates before splitting, fit transformations on train only, understand collection procedures, and involve subject-matter experts. Measure suspicious feature-target power, run ablations, investigate dramatic gains, and reserve the test split for final reporting.

Feature importance asks how performance changes when a feature is removed; model-specific tools and SHAP can also explain individual predictions. Generalization asks whether a feature has coverage and value distributions that overlap future data. More features can cause leakage, overfitting, serving cost, latency, and technical debt.

## Mental Models

A feature is a contract between training and inference. Ask: could this value be known at prediction time, how was it generated, and will its coverage and distribution survive? Prefer information that generalizes over identifiers. Treat missingness and lineage as signals to investigate.

## Anti-patterns

- Scaling or imputing with statistics from validation or test data.
- Randomly splitting temporally or group-correlated examples.
- Trusting a spectacular feature gain without tracing its provenance.
- Encoding production categories as fixed, ever-complete lists.
- Adding features indefinitely without measuring importance and serving cost.
- Assuming deep learning eliminates domain-specific feature work.

## Worked Example

For taxi ETA, a model trained on the previous six days might use day of week and hour. If Sunday appears only in today’s test data, a naïve categorical encoding cannot generalize; hour values overlap and are safer. A more general `IS_RUSH_HOUR` feature may help, but it can lose useful hour-specific information. Fit preprocessing using only the six training days, then test coverage and behavior on Sunday.

## Key Takeaways

Engineer features with domain experts and production availability in mind. Split before preprocessing, track lineage, and test leakage throughout the lifecycle. Favor features with useful coverage and stable distributions; remove features that no longer pay for their operational cost. Definitions should be reusable, but computation must remain consistent between training and serving.

## Connects To

Chapter 4 supplies labeled examples and valid splits. Chapter 6 trains models on these representations, uses ablations and slice checks to validate them, and carries feature latency and generalization into deployment and monitoring.
