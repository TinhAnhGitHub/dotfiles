# Chapter 10: Infrastructure and Tooling for MLOps

**Source**: Designing Machine Learning Systems — Chip Huyen, Chapter 10

## Core Idea
Bringing ML to production is an infrastructure problem as much as a modeling problem. The right platform reduces repeated engineering work, makes experiments reproducible, connects development to production, and lets teams operate models without requiring every data scientist to become an infrastructure specialist.

## Frameworks Introduced
- **Four layers**: storage and compute; resource management; ML platform; and development environment. The appropriate investment depends on application count, specialization, scale, security, and organizational maturity.
- **Scheduler–orchestrator distinction**: A scheduler decides when jobs run and handles dependencies, queues, retries, and priorities. An orchestrator provisions and manages the machines, instances, clusters, replicas, and long-running services.
- **ML platform components**: Model deployment, model store, and feature store are shared capabilities that can serve many applications.
- **Build versus buy**: Decide using company stage, competitive focus, tool maturity, compliance, and integration burden.

## Key Concepts
- **Compute unit**: The resource abstraction that executes work, such as a core, job, pod, or instance; memory and operation speed constrain capacity.
- **Container image**: A reproducible environment built from instructions such as a Dockerfile.
- **Container**: A running instance of an image.
- **DAG**: A directed acyclic graph representing workflow steps and dependencies.
- **Model store**: A system for storing a model together with the artifacts needed to reproduce, debug, discover, and operate it.
- **Feature store**: A system that may manage feature definitions, compute and cache features, and keep training and inference features consistent.
- **Development environment**: The standardized place for coding, experiments, versioning, and CI/CD.

## Mental Models
- Invest first where practitioners spend time. A reliable, standardized development environment can improve productivity more directly than an impressive production stack.
- Treat reproducibility as an artifact graph, not a model binary: connect code, data, parameters, dependencies, features, experiments, ownership, and deployment.
- Abstract infrastructure for users while retaining operational ownership. “End-to-end” data science is feasible when tools hide containerization, distributed processing, failover, and resource details.
- Prefer elasticity for bursty workloads, but remember cloud compute is not infinite and can become expensive or hard to repatriate.

## Anti-patterns
- **Unversioned dependencies or data**: Identical code can behave differently across package, language, hardware, or data versions.
- **Notebook-only production provenance**: Stateful notebooks enable fast exploration but permit out-of-order execution and weak reproducibility.
- **A model store that stores only blobs**: Without generation code, features, dependencies, lineage, owner, and experiment artifacts, debugging becomes guesswork.
- **Forcing every data scientist to operate Kubernetes**: This substitutes infrastructure boilerplate for modeling unless the platform supplies useful abstractions.
- **Building by default**: Custom infrastructure creates maintenance, hiring, integration, and future innovation costs; buying is not automatically inferior.

## Worked Example
Represent a weekly model workflow as a DAG: pull data, extract features, train candidates A and B, compare them on a test set, then deploy A if it wins or B otherwise. A scheduler can express the dependencies, retries, and conditional promotion; an orchestrator can provision the required compute. Package steps in containers so featurization can use memory-heavy CPUs while training uses GPUs. Store each resulting model with its serialized parameters, definition, feature and prediction functions, environment, data version, generation code, experiment artifacts, and owner. A feature store can then share expensive features and unify batch and streaming definitions.

## Reference Table

| Layer | Primary responsibility | Representative concerns |
|---|---|---|
| Storage/compute | Hold data and execute workloads | Memory, throughput, cost, elasticity |
| Resource management | Schedule and provision work | DAGs, queues, retries, scaling |
| ML platform | Reuse ML-specific capabilities | Deployment, model store, feature store |
| Development | Help people build reproducibly | IDEs, notebooks, versioning, CI/CD |

## Key Takeaways
1. Size infrastructure to real scale and requirements; do not copy a hyperscaler by reflex.
2. Standardize tools, versions, and environments while allowing reasonable IDE choice.
3. Make model artifacts discoverable, versioned, and connected by lineage.
4. Use workflow abstractions that fit ML’s data, experiment, and deployment dependencies.
5. Revisit build-versus-buy decisions as the company and tool ecosystem mature.

## Connects To
- **Chapter 7**: Containers, deployment services, and feature consistency support prediction serving.
- **Chapter 8**: Observability and monitoring are platform capabilities that expose production health.
- **Chapter 9**: Automated retraining and test-in-production depend on scheduling, lineage, and promotion infrastructure.
- **Chapter 11**: Infrastructure choices shape team boundaries and whether specialists can empower end-to-end practitioners.
