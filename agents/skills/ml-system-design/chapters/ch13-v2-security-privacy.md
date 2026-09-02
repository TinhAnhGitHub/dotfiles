# Chapter 13: Security & Privacy

**Source**: Machine Learning Systems — Vijay Janapa Reddi (Vol. 2), Chapter 13

## Core Idea
ML security protects more than an endpoint: the model, training data, artifact path, hardware, serving interface, and learned decision boundary are all part of the attack surface. Privacy is likewise a lifecycle property because models can retain and reveal shadows of sensitive data. Security and privacy must be designed into training, deployment, operations, and recovery.

## Frameworks Introduced
- **Expanded ML attack surface**: Analyze supply chain, access and isolation, model-specific attacks, hardware, service interfaces, and generative semantics. Use it before selecting controls; a firewall cannot stop poisoning or prompt injection.
- **Layered defense architecture**: Build upward from least privilege, service identity, encrypted transport, and audit logging to privacy controls, signed artifacts, adversarial evaluation, runtime monitoring, TEEs/HSMs, and semantic guardrails. Layers catch different failures and should degrade gracefully.
- **Security and Privacy Maturity Model**: Mature boundaries in dependency order: access/configuration; data/privacy; model integrity; adversarial/abuse; governance/evidence. The order follows the threat model, not a calendar.
- **Differential privacy**: Bound the influence of an individual record through a tracked privacy budget. DP-SGD clips per-example gradients, adds calibrated noise, and accounts for cumulative loss; lower budget means stronger protection but more utility and compute pressure.

## Key Concepts
- **Model extraction**: Reconstructing model behavior through queries.
- **Data poisoning**: Corrupting training data so the learned model internalizes harmful behavior.
- **Membership inference**: Inferring whether a record appeared in training.
- **Prompt injection**: Using language and context to make a model treat content as instruction.
- **Model integrity**: Confidence that validated code, data, weights, and configuration are what production serves.
- **Trusted execution environment (TEE)**: Hardware-supported isolation for sensitive computation.
- **Differential privacy budget**: The tracked cumulative privacy loss across training and releases.
- **Provenance**: Traceability from a model to its data, code, principal, and checkpoint.

## Mental Models
- The model is both asset and attack surface: learning creates utility and new leakage or manipulation paths.
- Privacy is spent, not switched on. Repeated queries, retraining, and A/B tests can consume one shared budget.
- Start with the boundary currently unprotected; do not paralyze delivery by deploying every advanced defense before basic access and integrity controls.
- Defend the semantic channel as well as the network channel: outputs, tools, prompts, and retrieved content need policy and monitoring.

## Anti-patterns
- **Treat federated learning or encrypted storage as complete privacy**: Updates, endpoints, metadata, and model outputs can still leak.
- **Rely on obscurity or perimeter controls**: Learned behavior can be extracted or poisoned without a conventional software exploit.
- **Use DP without accounting**: A library default is not a threat model or a lifecycle budget.
- **Skip signed artifacts and rollback evidence**: Operators cannot determine which data or binary caused an incident.
- **Deploy semantic guardrails outside the serving path**: Prompt injection and tool misuse pass through ordinary text channels.

## Worked Example
For a healthcare personalization service, first enforce least-privilege identities, encrypted transport, and auditable access to data, weights, deployments, and logs. Next isolate sensitive training data and track a privacy budget across fine-tuning and future releases. Sign datasets, manifests, and model artifacts so a suspect deployment can be traced and rolled back. If an adaptive attacker can query the service, add rate limiting, output monitoring, extraction tests, and red-team exercises. Select a TEE or stronger formal defense only if the threat model justifies its hardware and latency cost. Finally map retention, incident response, and reproducible control checks to governance obligations. This staged path makes security progress measurable without pretending that one control solves every layer.

## Key Takeaways
1. ML security must include learned boundaries, provenance, hardware, and generative interfaces.
2. Differential privacy provides bounded claims only when its budget is measured across the lifecycle.
3. Maturity is cumulative: access, privacy, integrity, abuse resistance, then evidence.
4. Security controls trade utility, latency, compute, and operational complexity.
5. Recovery depends on signed artifacts, registry permissions, audit trails, and rollback paths.

## Connects To
- **Chapter 10**: Sharding, batching, routing, and multi-tenancy create serving attack and isolation surfaces.
- **Chapter 11**: Federated and edge systems change where data and updates are exposed.
- **Chapter 14**: Robustness handles intentional or accidental perturbations that security controls alone cannot contain.
- **Chapter 16**: Privacy, accountability, auditability, and human impact become governance obligations.
