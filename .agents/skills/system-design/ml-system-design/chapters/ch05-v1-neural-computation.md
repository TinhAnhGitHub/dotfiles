# Chapter 5: Neural Computation

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 5

## Core Idea
Neural networks turn patterns into learned behavior through composable arithmetic. Understanding forward computation, loss, backpropagation, and state explains both why networks learn and why training requires careful memory, numerical, and hardware accounting.

## Frameworks Introduced
- **D·A·M Taxonomy**: Neural computation is the Algorithm axis, but its data volume and machine placement determine system behavior.
- **Learning Process**: A forward pass produces predictions, a loss measures error, backpropagation computes gradients, and an optimizer updates parameters.
- **Inference Pipeline**: Preprocess inputs, execute learned layers, and postprocess outputs; the complete path matters more than the model alone.
- **D·A·M Taxonomy for neural computation**: Use Data to supply evidence, Algorithm to transform it, and Machine to execute the transformations within budget.

## Key Concepts
- **Neuron**: A weighted combination of inputs followed by a nonlinear activation.
- **Layer**: A composable transformation that maps one representation to another.
- **Activation function**: Nonlinearity that lets stacked layers represent more than a linear mapping.
- **Loss function**: An objective measuring disagreement between predictions and targets.
- **Backpropagation**: Reverse-mode application of the chain rule through the computation graph.
- **Gradient descent**: Iterative parameter adjustment guided by loss gradients.
- **Overfitting**: Fitting training examples more closely than the underlying task generalizes.
- **Activation retention**: Saving forward intermediates needed during the backward pass.

## Mental Models
Think of a network as a pipeline of representations, not a collection of isolated neurons. Think of backpropagation as a dependency ledger: each gradient requires particular activations, weights, or nonlinear-operation state. Use the training-memory model—weights, gradients, optimizer states, and activations—to explain out-of-memory failures. Use D·A·M to diagnose whether a poor result reflects missing evidence, inadequate computation, or insufficient execution resources.

## Anti-patterns
- **Black-box gradients**: Treating `backward` as magic hides the saved-state and memory costs that determine feasibility.
- **Weights-only memory estimates**: Activations and optimizer state can dominate training memory.
- **Inference-only profiling**: Preprocessing and postprocessing can determine end-to-end latency.
- **Blind capacity growth**: A larger network can increase compute, data requirements, and overfitting without fixing the binding issue.
- **Ignoring numerical behavior**: Low precision, stochastic layers, and batch-dependent operations can change gradient results.

## Worked Example
For a handwritten digit classifier, an image is transformed through layers into class probabilities. If the network assigns probabilities such as 0.1, 0.2, 0.5, and so on to an image labeled “seven,” the loss exposes the error. Backpropagation first measures output error, then determines how final-layer weights affect it, and finally propagates responsibility toward earlier layers. The optimizer applies the accumulated gradients, repeating the cycle over batches. The example makes the forward/backward/update dependency concrete without treating the model as detached from its training state.

## Key Takeaways
1. Learning is a coupled forward, loss, backward, and update process.
2. Nonlinearity and depth create expressive representations, but also create state and compute costs.
3. Plan memory for all training state, not merely parameters.
4. Separate inference pipeline costs from model arithmetic.
5. Use measured error slices and resource profiles to choose the next intervention.

## Connects To
- **Chapter 4**: Data quality and representation determine the evidence available to learning.
- **Chapter 6**: Architecture chooses how neural computation encodes structure.
- **Chapter 7**: Frameworks automate graphs, differentiation, and hardware execution.
- **Chapter 8**: Training systems scale these computations under memory and throughput limits.
