# Chapter 10: Model Compression

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 10

## Core Idea
Model compression trades model redundancy for lower memory, latency, energy, or serving cost while retaining the behavior that matters. Compression is a systems decision, not a single accuracy trick: the best method depends on the target hardware, operator support, batch shape, quality budget, and whether the model is bandwidth- or compute-bound.

## Frameworks Introduced
- **Pruning**: Remove weights, channels, heads, or other structures. Unstructured sparsity may reduce parameter count without improving hardware speed; structured pruning is more likely to map to dense kernels and predictable latency.
- **Quantization**: Represent weights and/or activations with fewer bits. Post-training quantization is cheap; quantization-aware training can recover quality when calibration alone is insufficient.
- **Knowledge distillation**: Train a smaller student to imitate a stronger teacher through softened outputs, intermediate representations, or task targets.
- **Low-rank factorization**: Approximate large weight matrices by products of smaller matrices, exchanging parameter and operation savings for approximation error and possibly extra kernel launches.
- **Compression workflow**: Establish a quality baseline, define a deployment target, choose a method, compress, fine-tune or distill, validate, and benchmark on the actual stack.

## Key Concepts
- **Unstructured versus structured sparsity**: Zeroing individual values can save storage but often leaves dense computation and irregular memory access; removing whole structures is more hardware-friendly.
- **Calibration**: Use representative activation data to choose quantization scales and identify sensitive layers.
- **Mixed precision**: Keep sensitive operations at higher precision while lowering precision elsewhere.
- **Accuracy–efficiency Pareto frontier**: Compare configurations that cannot improve one objective without worsening another rather than chasing one headline score.
- **Sensitivity analysis**: Test which layers, tensors, or blocks tolerate aggressive compression.
- **Loss-aware compression**: Allocate precision or pruning budget according to measured quality impact, not uniform rules.

## Mental Models
Separate *mathematical compression* from *realized acceleration*. Fewer parameters can reduce memory traffic and model footprint, yet latency may remain unchanged if kernels do not exploit the new representation. Treat compression as a constrained optimization over quality, latency, memory, energy, and implementation risk. A compression point is credible only when it is evaluated end to end: model artifact, runtime, operators, preprocessing, postprocessing, and service behavior.

## Anti-patterns
- **Parameter-count worship**: A smaller checkpoint is not automatically a faster or cheaper model.
- **Blind global thresholds**: Uniform pruning or quantization can damage sensitive layers and rare behaviors.
- **Unsupported formats**: Exporting a sparse or low-bit representation without runtime and kernel support creates conversion overhead or silently falls back to dense execution.
- **Single-metric validation**: Top-line accuracy can hide calibration, robustness, fairness, or long-tail regressions.
- **Compressing before defining the target**: Without a latency, memory, or energy budget, teams cannot choose among trade-offs.

## Worked Example
Suppose a vision model misses a memory limit on an edge accelerator. The team first measures layer memory and latency, then applies sensitivity analysis. Most layers move to lower precision, while a sensitive output block stays at higher precision. Structured channel pruning removes low-contribution channels, followed by fine-tuning with a representative data mixture. The resulting checkpoint is accepted only after the accelerator runtime executes the intended kernels and a device benchmark confirms memory, tail latency, energy, and task quality. If the pruned model merely produces a sparse file that the runtime densifies, the apparent compression is not a systems win.

## Key Takeaways
1. Choose compression against a concrete deployment constraint.
2. Measure actual runtime behavior, not only parameter or file size.
3. Use sensitivity, calibration, and fine-tuning to spend quality budget deliberately.
4. Prefer representations supported by target hardware and software.
5. Report the full Pareto trade-off and guard deployment-relevant quality.

## Connects To
- **Chapter 9**: Data selection changes the training signal available to a compressed model.
- **Chapter 11**: Hardware and kernels determine whether sparsity, precision, or factorization becomes speed.
- **Chapter 12**: Benchmark design distinguishes nominal compression from realized improvement.
- **Chapter 13**: Serving constraints expose memory, batching, and tail-latency consequences.
