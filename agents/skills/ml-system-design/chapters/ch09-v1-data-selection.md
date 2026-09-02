# Chapter 9: Data Selection

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 9

## Core Idea
Data selection is data-algorithm co-design: maximize useful learning per unit of compute rather than assuming that more examples are always better. The goal is the lowest end-to-end cost of reaching target quality while preserving deployment-relevant coverage, rare cases, and underrepresented groups.

## Frameworks Introduced
- **Information-Compute Ratio (ICR)**: Learning signal gained per unit of training compute. Use it to compare subsets, curricula, or synthetic-data policies; estimate it with validation improvement, loss reduction, learning-curve area, uncertainty scores, and coverage checks.
- **Three-stage selection pipeline**: Apply static pruning before training, dynamic selection during training, and synthetic generation on demand. Each stage earns its place only when its quality gain exceeds its scoring, storage, labeling, or generation cost.
- **Selection inequality**: Selection plus subset training must cost less than full-data training. This is the end-to-end break-even test, not a promise that a smaller dataset is faster.

## Key Concepts
- **Static pruning**: Remove redundancy or harmful examples before training through coreset selection, deduplication, and quality filtering.
- **Coreset**: A smaller subset intended to preserve a dataset’s useful learning signal or coverage.
- **EL2N/GraNd**: Proxy-model training-dynamics scores that find uncertain or high-gradient examples.
- **Deduplication**: Exact or near-duplicate removal using hashes, MinHash/LSH, perceptual hashes, or embeddings.
- **Dynamic selection**: Change which examples are presented as model knowledge evolves.
- **Curriculum learning**: Present data in a deliberate progression, often easier to harder.
- **Active learning**: Select unlabeled examples for expensive human annotation.
- **Semi-supervised learning**: Use a small labeled set to learn from a larger unlabeled pool.
- **Compute-optimal frontier**: A measured balance of model size, data, and compute; it is regime-specific, not a universal ratio.

## Mental Models
Think of data as workload composition, not merely input. Selection removes work before model and hardware costs are paid, so savings can multiply with compression and throughput improvements. Treat “data becomes a tax” as a marginal-return signal: after the ICR frontier, additional examples may increase operations without proportionate learning. Use minimum coverage constraints before optimizing average information value; an unusual example may be low-frequency but high-risk.

## Anti-patterns
- **More data by default**: Diminishing returns can turn extra examples into storage, labeling, and training cost.
- **Unstratified pruning**: Average-loss selection can erase rare classes, demographic groups, or failure modes.
- **Synthetic-only validation**: Generated data can have a domain gap or reinforce model collapse; validate on real, deployment-relevant data.
- **Ignoring selection overhead**: A full-model scan or per-epoch rescoring can erase subset savings and make training slower.
- **Benchmark-only selection**: A curated set that wins on one test set may fail on independently collected data.

## Worked Example
A team wants a 100,000-image coreset from 1 million images. Random subsampling risks losing rare classes and boundary cases. They train a lightweight proxy for five epochs, compute EL2N scores, retain high-uncertainty images, then enforce class and deployment-slice coverage before full training. This is useful only if proxy rankings transfer and the selection cost is below the saved training time. In the source’s illustrative comparison, target-model scoring costs 2.8 hours while proxy scoring costs 0.6 hours, preserving much more net savings. The correct acceptance test compares subset-plus-selection time, target accuracy, calibration, and slice performance with the full-data baseline.

## Key Takeaways
1. Optimize information per FLOP, not dataset size alone.
2. Diagnose the binding constraint: labels, compute, redundancy, scarcity, or convergence.
3. Protect rare and deployment-critical coverage explicitly.
4. Measure selection overhead, I/O behavior, and amortization across repeated runs.
5. Validate curated data on independent, representative distributions.

## Connects To
- **Chapter 8**: Selection reduces the training workload before training-loop optimizations apply.
- **Chapter 10**: A selected dataset changes what the compressed model learns, but does not itself shrink the model.
- **Chapter 12**: Benchmarking verifies accuracy, coverage, calibration, and efficiency claims.
- **Chapter 14**: Selection and data lineage must remain reproducible as models and distributions evolve.
