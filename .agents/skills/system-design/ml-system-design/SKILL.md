---
name: ml-system-design
description: "Actionable ML system design knowledge synthesized from Introduction to Machine Learning Systems (Vijay Janapa Reddi), Machine Learning Systems Vol. 2, Designing Machine Learning Systems (Chip Huyen), AI Systems Performance Engineering (Chris Fregly), and the supplemental MLOps Tools guide. Use for end-to-end ML architecture, performance engineering, data, training, inference, fleet operations, safety, and tool selection."
---

<!-- argument-hint: [topic, lifecycle stage, tool category, or chapter filename] -->

# ML System Design
**Sources**: 4 books + supplemental `mlops-tools.md` | Chapters: 51 | **Generated**: 2026-09-02

## How to Use This Skill

- Without arguments: apply the core decision sequence below.
- With a topic such as `leakage`, `distributed training`, `serving`, `monitoring`, `privacy`, or `sustainability`: load the matching chapter file(s).
- With a source-qualified filename such as `ch10-v2-inference-at-scale`: load that chapter.
- For named tools: read [mlops-chapter-tool-mapping-plan.md](mlops-chapter-tool-mapping-plan.md); it is a dated, non-normative inventory and validation plan.

## Core Frameworks & Mental Models

- **Iterative Process (Chip Huyen):** start from business/user requirements, frame the prediction task, establish a baseline, then iterate through data, features, model, evaluation, deployment, monitoring, and feedback. Do not freeze the system around its first model.
- **D·A·M Taxonomy (Vol. 1):** diagnose every miss through **Data**, **Algorithm**, and **Machine** hypotheses. Inspect coverage/labels/distribution, model work, and latency/bandwidth/memory/utilization; relax the binding constraint and remeasure.
- **Five-Pillar Framework (Vol. 1):** assign ownership across data engineering, training systems, deployment infrastructure, operations/monitoring, and ethics/governance. The model is one layer in a larger system.
- **Iron Law of ML Systems (Vol. 1):** first separate data movement, arithmetic, and fixed overhead: `T ≈ Dvol/BW + O/(Rpeak·ηhw) + Llat`. Optimize the critical-path term and account for overlap.
- **Deployment Paradigm Framework (Vol. 1):** choose cloud, data-center, edge, mobile, TinyML, or hybrid from latency, privacy, connectivity, memory, energy, update, and cost constraints—not fashion.
- **Data-as-code and constraint propagation:** version, test, review, and trace datasets/features like source code; propagate downstream SLOs and policy constraints back into upstream data/model choices.
- **Fleet Stack and C3 Taxonomy (Vol. 2):** at scale, reason across infrastructure, distribution, serving/operations, and governance; localize waste to **Compute**, **Communication**, or **Coordination** and track useful work (goodput), not utilization alone.
- **Roofline and measurement discipline (Vol. 1/2):** classify a workload as movement-, compute-, memory-, communication-, or coordination-bound before choosing hardware, kernels, precision, compression, topology, or parallelism. Benchmark representative end-to-end behavior.
- **Full-stack performance engineering (Fregly):** follow the data path from hardware and NUMA topology through OS, containers, orchestration, communication, I/O, and runtime. Profile the bottleneck, improve one layer, and remeasure GPU utilization, goodput, latency, cost, and reliability.
- **Serving is an SLO-bearing pipeline:** budget network, feature retrieval, preprocessing, inference, postprocessing, and serialization; for generative systems separate prefill/decode, queueing, batching, capacity, and tail latency.
- **Closed-loop operations:** version data/code/configuration/environment/model/dependencies together; validate offline and under production-like traffic; use shadow/canary/controlled release, monitoring, rollback, and evidence-based retraining.
- **Responsible-by-design:** security, privacy, fairness, robustness, safety, sustainability, explainability, and accountability are measurable release constraints, not a final checklist.

### Decision sequence

1. Define user value, prediction target, guardrails, SLOs, label delay, and rollback ownership.
2. Characterize data distributions, leakage, feedback loops, lineage, and feature parity.
3. Choose the simplest model and deployment paradigm that satisfy hard constraints.
4. Estimate compute, memory, bandwidth, storage, communication, energy, failure, and cost budgets.
5. Build a reproducible train/evaluate/serve path and test representative slices and traffic.
6. Add observability, progressive rollout, recovery, governance, and an accountable owner.
7. Re-measure after each optimization; the binding constraint moves.

## Chapter Index

| Chapter | Title | Source |
|---|---|---|
| [ch01-chip-overview-of-machine-learning-systems](chapters/ch01-chip-overview-of-machine-learning-systems.md) | Overview of Machine Learning Systems | Chip Huyen |
| [ch01-v1-introduction](chapters/ch01-v1-introduction.md) | Introduction | Vol. 1 — Reddi |
| [ch01-v2-introduction](chapters/ch01-v2-introduction.md) | Introduction | Vol. 2 — Reddi |
| [ch02-chip-introduction-to-machine-learning-systems-design](chapters/ch02-chip-introduction-to-machine-learning-systems-design.md) | Introduction to Machine Learning Systems Design | Chip Huyen |
| [ch02-v1-ml-systems](chapters/ch02-v1-ml-systems.md) | ML Systems | Vol. 1 — Reddi |
| [ch02-v2-compute-infrastructure](chapters/ch02-v2-compute-infrastructure.md) | Compute Infrastructure | Vol. 2 — Reddi |
| [ch03-chip-data-engineering-fundamentals](chapters/ch03-chip-data-engineering-fundamentals.md) | Data Engineering Fundamentals | Chip Huyen |
| [ch03-v1-ml-workflow](chapters/ch03-v1-ml-workflow.md) | ML Workflow | Vol. 1 — Reddi |
| [ch03-v2-network-fabrics](chapters/ch03-v2-network-fabrics.md) | Network Fabrics | Vol. 2 — Reddi |
| [ch04-chip-training-data](chapters/ch04-chip-training-data.md) | Training Data | Chip Huyen |
| [ch04-v1-data-engineering](chapters/ch04-v1-data-engineering.md) | Data Engineering | Vol. 1 — Reddi |
| [ch04-v2-data-storage](chapters/ch04-v2-data-storage.md) | Data Storage | Vol. 2 — Reddi |
| [ch05-chip-feature-engineering](chapters/ch05-chip-feature-engineering.md) | Feature Engineering | Chip Huyen |
| [ch05-v1-neural-computation](chapters/ch05-v1-neural-computation.md) | Neural Computation | Vol. 1 — Reddi |
| [ch05-v2-distributed-training](chapters/ch05-v2-distributed-training.md) | Distributed Training | Vol. 2 — Reddi |
| [ch06-chip-model-development-and-offline-evaluation](chapters/ch06-chip-model-development-and-offline-evaluation.md) | Model Development and Offline Evaluation | Chip Huyen |
| [ch06-v1-network-architectures](chapters/ch06-v1-network-architectures.md) | Network Architectures | Vol. 1 — Reddi |
| [ch06-v2-collective-communication](chapters/ch06-v2-collective-communication.md) | Collective Communication | Vol. 2 — Reddi |
| [ch07-chip-model-deployment-and-prediction-service](chapters/ch07-chip-model-deployment-and-prediction-service.md) | Model Deployment and Prediction Service | Chip Huyen |
| [ch07-v1-ml-frameworks](chapters/ch07-v1-ml-frameworks.md) | ML Frameworks | Vol. 1 — Reddi |
| [ch07-v2-fault-tolerance](chapters/ch07-v2-fault-tolerance.md) | Fault Tolerance | Vol. 2 — Reddi |
| [ch08-chip-data-distribution-shifts-and-monitoring](chapters/ch08-chip-data-distribution-shifts-and-monitoring.md) | Data Distribution Shifts and Monitoring | Chip Huyen |
| [ch08-v1-model-training](chapters/ch08-v1-model-training.md) | Model Training | Vol. 1 — Reddi |
| [ch08-v2-fleet-orchestration](chapters/ch08-v2-fleet-orchestration.md) | Fleet Orchestration | Vol. 2 — Reddi |
| [ch09-chip-continual-learning-and-test-in-production](chapters/ch09-chip-continual-learning-and-test-in-production.md) | Continual Learning and Test in Production | Chip Huyen |
| [ch09-v1-data-selection](chapters/ch09-v1-data-selection.md) | Data Selection | Vol. 1 — Reddi |
| [ch09-v2-performance-engineering](chapters/ch09-v2-performance-engineering.md) | Performance Engineering | Vol. 2 — Reddi |
| [ch10-chip-infrastructure-and-tooling-for-mlops](chapters/ch10-chip-infrastructure-and-tooling-for-mlops.md) | Infrastructure and Tooling for MLOps | Chip Huyen |
| [ch10-v1-model-compression](chapters/ch10-v1-model-compression.md) | Model Compression | Vol. 1 — Reddi |
| [ch10-v2-inference-at-scale](chapters/ch10-v2-inference-at-scale.md) | Inference at Scale | Vol. 2 — Reddi |
| [ch11-chip-human-side-of-machine-learning](chapters/ch11-chip-human-side-of-machine-learning.md) | The Human Side of Machine Learning | Chip Huyen |
| [ch11-v1-hardware-acceleration](chapters/ch11-v1-hardware-acceleration.md) | Hardware Acceleration | Vol. 1 — Reddi |
| [ch11-v2-edge-intelligence](chapters/ch11-v2-edge-intelligence.md) | Edge Intelligence | Vol. 2 — Reddi |
| [ch12-v1-benchmarking](chapters/ch12-v1-benchmarking.md) | Benchmarking | Vol. 1 — Reddi |
| [ch12-v2-ml-operations-at-scale](chapters/ch12-v2-ml-operations-at-scale.md) | ML Operations at Scale | Vol. 2 — Reddi |
| [ch13-v1-model-serving](chapters/ch13-v1-model-serving.md) | Model Serving | Vol. 1 — Reddi |
| [ch13-v2-security-privacy](chapters/ch13-v2-security-privacy.md) | Security & Privacy | Vol. 2 — Reddi |
| [ch14-v1-ml-operations](chapters/ch14-v1-ml-operations.md) | ML Operations | Vol. 1 — Reddi |
| [ch14-v2-robust-ai](chapters/ch14-v2-robust-ai.md) | Robust AI | Vol. 2 — Reddi |
| [ch15-v1-responsible-engineering](chapters/ch15-v1-responsible-engineering.md) | Responsible Engineering | Vol. 1 — Reddi |
| [ch15-v2-sustainable-ai](chapters/ch15-v2-sustainable-ai.md) | Sustainable AI | Vol. 2 — Reddi |
| [ch16-v1-conclusion](chapters/ch16-v1-conclusion.md) | Conclusion | Vol. 1 — Reddi |
| [ch16-v2-responsible-ai](chapters/ch16-v2-responsible-ai.md) | Responsible AI | Vol. 2 — Reddi |
| [ch17-v2-conclusion](chapters/ch17-v2-conclusion.md) | Conclusion | Vol. 2 — Reddi |
| [ch01-fregly-introduction-and-ai-system-overview](chapters/ch01-fregly-introduction-and-ai-system-overview.md) | Introduction and AI System Overview | Chris Fregly |
| [ch02-fregly-ai-system-hardware-overview](chapters/ch02-fregly-ai-system-hardware-overview.md) | AI System Hardware Overview | Chris Fregly |
| [ch03-fregly-os-docker-kubernetes-gpu-tuning](chapters/ch03-fregly-os-docker-kubernetes-gpu-tuning.md) | OS, Docker, and Kubernetes Tuning for GPU-based Environments | Chris Fregly |
| [ch04-fregly-distributed-communication-and-io-optimizations](chapters/ch04-fregly-distributed-communication-and-io-optimizations.md) | Distributed Communication and I/O Optimizations | Chris Fregly |
| [ch10-fregly-ai-system-optimization-case-studies](chapters/ch10-fregly-ai-system-optimization-case-studies.md) | AI System Optimization Case Studies | Chris Fregly |
| [ch11-fregly-future-trends-in-ultra-scale-ai-systems-performance-engineering](chapters/ch11-fregly-future-trends-in-ultra-scale-ai-systems-performance-engineering.md) | Future Trends in Ultra-Scale AI Systems Performance Engineering | Chris Fregly |
| [ch12-fregly-ai-systems-performance-checklist-175-plus-items](chapters/ch12-fregly-ai-systems-performance-checklist-175-plus-items.md) | AI Systems Performance Checklist (175+ Items) | Chris Fregly |

## Topic Index

- **Requirements and problem framing** → Chip chapters 1–2; Vol. 1 chapters 1–3
- **Data, labels, leakage, features, feedback** → Vol. 1 chapters 3–4, 9; Chip chapters 3–5, 8–9
- **Neural computation, architectures, frameworks, training** → Vol. 1 chapters 5–8; Vol. 2 chapters 5–6; Chip chapter 6
- **Data selection, compression, acceleration, benchmarking** → Vol. 1 chapters 9–12; Vol. 2 chapters 2–4, 9
- **Serving, inference, batching, routing, edge** → Vol. 1 chapter 13; Vol. 2 chapters 10–11; Chip chapter 7
- **Monitoring, retraining, rollout, platform operations** → Vol. 1 chapter 14; Vol. 2 chapter 12; Chip chapters 8–10
- **Fault tolerance, orchestration, communication, fleet scale** → Vol. 2 chapters 1–8
- **Security, privacy, robustness, fairness, responsibility** → Vol. 1 chapter 15; Vol. 2 chapters 13–16; Chip chapter 11
- **Sustainability and cost** → Vol. 1 chapters 1–2, 11–12; Vol. 2 chapter 15; Fregly chapters 1–4, 10–12
- **Full-stack performance, NUMA, GPU, OS/container tuning, I/O** → Fregly chapters 1–4
- **Performance case studies, future systems, optimization checklist** → Fregly chapters 10–12
- **MLOps tools and discovery** → [mlops-chapter-tool-mapping-plan.md](mlops-chapter-tool-mapping-plan.md)

## Supporting Files

- [glossary.md](glossary.md) — concise terms and source chapter references
- [patterns.md](patterns.md) — reusable design patterns and trade-offs
- [cheatsheet.md](cheatsheet.md) — decision rules, diagnostic trees, and release gates
- [mlops-chapter-tool-mapping-plan.md](mlops-chapter-tool-mapping-plan.md) — historical tool inventory, 51-chapter mapping, modern Exa refresh, and validation plan

## Scope & Limits

This is synthesized guidance, not the source books. PDF extraction used `pdftotext` because Docling was unavailable; layout-heavy diagrams, typography, images, tables, and some formulas may be incomplete, so verify important technical details against the PDFs. The Fregly source is a September 2025 O’Reilly early release: its TOC marks chapters 5–9 unavailable, so this skill covers only the seven available sections (1–4 and 10–12) and does not fabricate the missing chapters. The MLOps tool list is historical and non-comprehensive; validate maintenance, license, security, compatibility, benchmark fit, and current project status before adoption. The source books are copyrighted/licensed works; this skill intentionally avoids long verbatim reproduction and should remain private unless redistribution rights are confirmed.
