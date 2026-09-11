# Chapter 10: AI System Optimization Case Studies
**Source**: AI Systems Performance Engineering — Chris Fregly, O’Reilly, 2025 early release, available TOC Chapter 10

## Core Idea
Performance gains come from co-designing model algorithms, numerical formats, compilers, communication, memory, and rack-scale hardware. The case studies repeatedly show that the right software can expose “free” throughput on existing hardware, while a hardware upgrade pays off only when the workload exercises its new bandwidth, memory, or precision capabilities.

## Frameworks Introduced
- **Profile, overlap, and co-design**: First identify the dominant compute, memory, communication, or scheduling cost; then overlap independent work and align model choices with the hardware topology.
- **Goodput per dollar**: Judge an optimization by useful tokens, training throughput, latency, energy, and cost—not by peak FLOPs alone.
- **Verifier-in-the-loop kernel search**: Generate a kernel, compile and test correctness, measure it against a baseline, and feed the result into the next candidate. Human engineers set constraints and review edge cases.

## Key Concepts
- **DualPipe**: DeepSeek’s parallelism strategy for overlapping computation and communication on bandwidth-limited H800 GPUs.
- **FP8/FP4**: Lower-precision formats that increase Tensor Core throughput when accuracy remains within tolerance.
- **Disaggregated inference**: Separating KV-cache prefill from token-generating decode and routing work to suitable GPUs.
- **PagedAttention**: vLLM’s virtual-memory-like management of attention KV caches.
- **Continuous batching**: Forming batches as requests arrive rather than waiting for a fixed window.
- **Unified CPU–GPU memory**: GH200/GB200 designs use fast NVLink-C2C to make CPU memory an extension for oversized workloads.
- **3D parallelism**: Combining data, tensor, and pipeline parallelism; expert parallelism is an additional option for MoE models.

## Mental Models
Treat bandwidth as a budget: DeepSeek’s 671-billion-parameter, 64-expert DeepSeek-V3 used custom CUDA communication paths and DualPipe to compensate for the H800’s reduced bandwidth, completing at an estimated $5.6M GPU cost. Treat scheduling and cache placement as part of inference: Dynamo’s dynamic batching, load balancing, and prefill/decode disaggregation produced 2× throughput on an H100 Llama deployment; vLLM’s PagedAttention and continuous batching improve goodput without new GPUs. Treat a superchip as workload-specific: GH200 reduced CPU–GPU transfer overhead from 22% to 3% and raised GPT-J throughput 17%, while a workload fitting entirely in HBM gained only about 2%.

## Anti-patterns
- **Buying compute before finding the bottleneck**: More GPUs do not fix slow data movement, cache placement, or synchronization.
- **Assuming peak hardware numbers transfer automatically**: FP8/FP4, NVLink, and unified memory help only when software and workload shape use them.
- **Trusting generated kernels without verification**: AI-assisted code must be compiled, correctness-tested, benchmarked, and human-reviewed.
- **Ignoring collaboration and failure modes**: OpenAI’s GPT-4.5 case emphasizes de-risking, continuous monitoring, and cross-team debugging; even `sum()` on a rare custom-code path caused catastrophic failures at scale.

## Worked Example
A progression illustrates the tuning ladder. MobileEye used H100 FP8 Tensor Cores, Transformer Engine, and `torch.compile` kernel fusion; the result was a measured 47% reduction in average step time versus its bfloat16 baseline. For serving, use vLLM to reduce KV-cache fragmentation and batch arrivals continuously, then use Dynamo when cluster-level routing and prefill/decode separation are the constraint. At larger scale, GB200 NVL72 combines 72 Blackwell GPUs with fifth-generation NVLink: FP4 doubled math throughput versus FP8, and reported Llama 405 inference throughput reached up to 30× a comparable Hopper cluster. These numbers are workload and configuration results, not universal guarantees.

## Key Takeaways
1. Measure the bottleneck before selecting precision, compiler, library, or hardware.
2. Overlap communication with computation when interconnect bandwidth is scarce.
3. Prefer mature optimized systems—PyTorch compiler, vLLM, Dynamo, NCCL—before custom code.
4. AI search can improve algorithms and kernels: AlphaTensor found 10–20% faster V100 GEMM; DeepSeek-R1 generated Attention kernels 1.1–2.1× faster than FlexAttention in the cited test.
5. Validate hardware purchases on representative workloads; GH200’s advantage was largest for memory-oversized inference (4.33 versus 0.57 tokens/s in Baseten’s 70B test).

## Connects To
- **Chapter 11**: Future hardware, optical fabrics, sparsity, and autonomous optimization extend these case-study patterns.
- **Chapter 12**: The checklist turns the diagnosis, measurement, and tuning workflow into repeatable operational actions.
