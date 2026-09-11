# Chapter 7: ML Frameworks

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 7

## Core Idea
An ML framework is a compiler for the silicon contract: it translates mathematical model definitions into graphs, gradients, kernels, memory allocations, and device execution. Framework choice determines which costs are visible, optimized, and portable.

## Frameworks Introduced
- **Three Framework Problems**: Solve execution (when computation runs), differentiation (how gradients are computed), and abstraction (how one interface reaches diverse hardware).
- **Ladder of Abstraction**: BLAS/LAPACK, NumPy, and ML frameworks successively hide lower-level work while introducing new contracts and trade-offs.
- **Compilation Continuum**: Choose among eager execution, static graphs, and hybrid graph-capture/JIT paths based on graph stability, debugging needs, and amortization.
- **nn.Module Abstraction**: Manage parameters, mode-dependent behavior, hierarchical composition, serialization, freezing, and inspection.

## Key Concepts
- **Eager execution**: Operations run immediately, supporting direct debugging and flexible control flow.
- **Computational graph**: A dependency representation enabling global scheduling, fusion, and memory planning.
- **Autograd tape**: A recorded operation history traversed in reverse for gradient computation.
- **Kernel fusion**: Combining operations to reduce launches and intermediate memory traffic.
- **Tensor abstraction**: Data plus shape, dtype, strides, device, and framework-managed state.
- **Graph break**: A region not captured or compiled, limiting global optimization.
- **Automatic differentiation**: Software application of derivative rules through supported compositions.
- **Deployment target**: A runtime whose operator coverage, memory model, and acceleration path must be validated.

## Mental Models
Ask what the framework can see. Eager mode maximizes immediate visibility and debugging; graph capture increases optimization visibility and can reduce dispatch and memory costs. Choose TensorFlow when its eager-to-graph and broad export ecosystem fit the target, PyTorch when rapid imperative iteration and capture/export paths matter, and JAX when pure functions and composable differentiation, vectorization, and compilation fit the work. Treat every tensor’s shape, dtype, layout, and device as an explicit contract.

## Anti-patterns
- **Assuming equivalent performance**: Same mathematics can produce different traffic, fusion, utilization, and latency.
- **Popularity-driven selection**: The final mobile or microcontroller runtime may have incompatible operators or memory assumptions.
- **Framework-as-magic**: High-level APIs do not remove the memory wall or the need to profile.
- **Unsafe tracing**: Capturing one data-dependent branch can silently produce wrong behavior for other inputs.
- **Compiling everything**: Setup and recompilation can dominate short, rapidly changing experiments.
- **Ignoring state contracts**: In-place mutation, mode flags, layout, or dtype mismatches can break gradients or deployment correctness.

## Worked Example
A simple `y = x * 2` followed by `z = y + 1` illustrates the execution choice. In eager execution, values appear immediately and an autograd tape records operations as they run. In a static graph, construction records symbolic nodes first and a later run executes an optimized graph. A hybrid compiler can preserve eager development while capturing stable regions for fusion and lower dispatch overhead. The right choice depends on how often the graph changes and how long it runs.

## Key Takeaways
1. Select frameworks by execution, differentiation, abstraction, and deployment requirements.
2. Profile graph coverage, dispatch overhead, memory traffic, and hardware utilization.
3. Use compilation when its setup cost is amortized by stable repeated work.
4. Preserve shape, dtype, layout, device, and mode contracts across boundaries.
5. Test the actual target runtime rather than assuming training behavior transfers.

## Connects To
- **Chapter 5**: Automates the computation graphs and derivatives introduced by neural computation.
- **Chapter 6**: Converts architecture-specific patterns into kernels and memory plans.
- **Chapter 8**: Exposes data loading, precision, checkpointing, and distributed controls.
- **Chapter 2**: Deployment hardware determines useful framework abstraction and export paths.
