---
description: Analyze a research paper systematically
---

Analyze the research paper provided in $ARGUMENTS.

The input may be:

* A local paper file referenced with `@path/to/paper.pdf`
* A paper title
* A paper URL
* Additional questions or analysis requirements

Read the entire paper before producing the final analysis. Base every claim on the paper itself. Clearly distinguish between:

* Statements explicitly made by the authors
* Your interpretation of the results
* Limitations or implications inferred from the evidence

Use the exact names of methods, models, datasets, benchmarks, metrics, losses, training stages, and baselines.

Structure the response as follows.

# 1. Problem Statement

Explain the main problem addressed by the paper.

Include:

* The task or research area
* The limitations of existing approaches
* Why the existing methods are insufficient
* The practical or theoretical consequence of those limitations
* The specific prior papers, algorithms, models, datasets, or benchmarks associated with the problem, when explicitly mentioned

Do not describe only the general research topic. Identify the precise gap that motivates the proposed work.

# 2. Proposed Solution and Contributions

Explain how the paper addresses the identified problems.

Include:

* The central idea of the proposed solution
* The relationship between each problem and the corresponding solution
* The main contributions claimed by the authors
* Whether each contribution is primarily:

  * A new algorithm
  * A modification of an existing algorithm
  * A training paradigm
  * A model architecture or module
  * A reward design
  * A data-construction method
  * A dataset
  * A benchmark
  * An evaluation protocol
  * A system or engineering framework
  * A theoretical analysis

Separate genuinely novel contributions from implementation choices or combinations of existing techniques.

# 3. Method

Describe the complete method and its execution flow.

## 3.1 Inputs and Outputs

Specify:

* Input data
* Input observations or states
* Model inputs
* Expected outputs
* Training-time outputs
* Inference-time outputs

## 3.2 Method Pipeline

Explain the method step by step, from data input to the final output.

For every important component, explain:

* Its responsibility
* Why it is required
* What information it receives
* What it produces
* How it interacts with other components

## 3.3 Algorithm and Training Objective

When applicable, explain:

* The base algorithm being used
* What was modified compared with the original algorithm
* Policy, reference model, critic, reward model, verifier, or environment roles
* On-policy and off-policy data usage
* Sampling and trajectory construction
* Reward definition
* Advantage estimation
* Loss functions
* Optimization stages
* Data filtering or curriculum strategies
* Parameter synchronization or replay-buffer behavior

Rewrite important equations in readable form and explain:

* Every variable
* The input and output of the equation
* How the equation is computed
* How it differs from the corresponding standard algorithm
* What behavior the equation encourages

Do not classify a method as a new reinforcement-learning algorithm unless the optimization algorithm itself is materially changed. Distinguish among:

* A new RL algorithm
* A modified RL objective
* A new reward or advantage estimator
* A data or rollout strategy
* A training framework
* An engineering optimization

## 3.4 Data Construction

When applicable, explain:

* Data sources
* Collection process
* Filtering rules
* Annotation process
* Positive and negative sample construction
* Train, validation, and test splits
* Synthetic or model-generated data
* Potential data leakage or overlap
* Whether evaluation tasks are related to training data

## 3.5 Benchmark, Dataset, and Metric Contributions

When the paper introduces a benchmark or dataset, explain:

* What it measures
* Task categories
* Dataset size
* Data sources
* Splits
* Annotation procedure
* Evaluation protocol
* Metrics
* Differences from existing benchmarks
* Known biases, limitations, or contamination risks

# 4. Experiments

## 4.1 Implementation Details

Extract all available implementation details, including:

* Base models
* Model sizes
* Initialization or checkpoints
* Training datasets
* Number of samples or trajectories
* Hardware
* Number and type of GPUs
* Batch size
* Learning rate
* Optimizer
* Number of epochs or optimization steps
* Sampling temperature
* Maximum sequence or trajectory length
* Reward coefficients
* KL coefficients
* Important hyperparameters
* Inference configuration

Use `Not specified in the paper` when information is unavailable. Do not invent missing values.

## 4.2 Benchmarks and Datasets

For every experiment, explicitly state:

* Benchmark name
* Dataset name
* Dataset split
* Number of evaluated tasks or examples
* Evaluation setting
* Whether the evaluation is online, offline, simulated, or performed in a real environment
* Whether external tools, demonstrations, retrieval, or privileged information are used

Do not use vague descriptions such as “the main benchmark.” Always give its exact name.

## 4.3 Evaluation Metrics

For every metric, explain:

* Metric name
* What it measures
* Whether higher or lower is better
* Unit of evaluation, such as step, episode, task, trajectory, token, or sample
* Whether the metric is automatically computed or human-evaluated
* Important caveats in interpreting it

## 4.4 Compared Methods

List the important baselines and competing methods.

For each baseline, mention when available:

* Model name and size
* Training method
* Whether it uses the same base model
* Whether it uses additional data
* Whether it uses demonstrations, planning, retrieval, or external tools
* Whether the comparison is directly fair
* Important differences in evaluation settings

Identify comparisons that may not be strictly apples-to-apples.

# 5. Results

Analyze the primary results benchmark by benchmark.

For every important result, state:

* Benchmark and dataset
* Evaluation setting
* Metric
* Proposed method's score
* Strongest baseline score
* Absolute improvement
* Relative improvement when useful
* Whether the result is state of the art under the stated setting

Then explain:

* What the result demonstrates
* Which contribution likely caused the improvement
* Whether the gains are consistent across tasks, models, and settings
* Where the method performs poorly
* Whether the evidence supports the authors' claims

Do not say that the method achieves state of the art unless the paper provides a valid comparison under a clearly defined setting.

Use tables when they improve clarity, especially for:

* Benchmark results
* Baseline comparisons
* Different model sizes
* Different training stages
* Online versus offline results

# 6. Ablation, Analysis, and Insights

## 6.1 Contribution-Level Ablation

Map every major contribution to its ablation evidence.

For each contribution, explain:

* The full method result
* The result after removing or changing the contribution
* Absolute performance change
* What the change demonstrates
* Whether the component is essential, complementary, or marginal
* Whether interactions between components were tested

Flag claimed contributions that are not independently ablated.

## 6.2 Training and Behavioral Analysis

Discuss analyses such as:

* Training curves
* Reward progression
* Policy entropy
* KL divergence
* On-policy and off-policy behavior
* Success and failure trajectories
* Scaling behavior
* Data efficiency
* Generalization
* Robustness
* Error propagation
* Computational efficiency

Explain what each analysis reveals about why the method works or fails.

## 6.3 Dataset or Benchmark Analysis

For dataset or benchmark papers, analyze:

* Performance patterns across task categories
* Which models or method families perform well
* Common failure modes
* Difficulty distribution
* Annotation reliability
* Dataset bias
* Contamination or leakage risks
* Whether the benchmark measures the intended capability
* Insights about the current limitations of evaluated models

## 6.4 Limitations and Future Directions

Separate:

* Limitations explicitly acknowledged by the authors
* Limitations inferred from the experiment design
* Missing experiments
* Fairness concerns
* Scalability concerns
* Generalization concerns
* Reproducibility concerns
* Possible future research directions

# 7. Conclusion and Takeaways

Summarize what should be remembered from the paper.

Include:

* The problem
* The central solution
* The most important technical contribution
* The strongest empirical finding
* The main limitation
* Where the method can be reused
* What ideas are most useful for future research or engineering

End with these subsections:

## One-Sentence Summary

Provide one precise sentence describing the paper.

## What Is Actually Novel?

State the genuinely novel part without repeating the authors' marketing language.

## Practical Reuse

Explain which parts could be reused in another project and under what conditions.

## Critical Assessment

Give a balanced assessment of the paper's strengths, weaknesses, experimental reliability, and overall significance.

Additional requirements:

* Preserve mathematical and technical precision.
* Define specialized terminology before using it.
* Use exact section, table, figure, and equation references when available.
* Do not rely only on the abstract or introduction.
* Cross-check claims against experiments and ablations.
* Explicitly mention missing evidence.
* Do not assume that correlation in an ablation proves causation.
* Do not invent implementation details, results, or author claims.
* When multiple papers are provided, analyze each paper separately first, then add a final comparison covering:

  * Problem formulation
  * Main contribution
  * Method
  * Data
  * Benchmarks
  * Metrics
  * Results
  * Limitations
  * Which paper provides the stronger contribution and why
