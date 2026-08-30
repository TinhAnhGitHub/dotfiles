# Book-derived LLMOps patterns

This file records the reusable engineering patterns synthesized from the local
Databricks LLMOps book material. It intentionally summarizes the ideas instead
of copying the book text or distributing its figures.

## Local source map

The source material is available at:

```text
C:\TinhAnh\project\development\databricks_book
```

| Chapter | Local source | Reusable pattern | Figures consulted |
|---|---|---|---|
| 7 | `7_Foundation_Models_and_Context_Engineering\content.md` | foundation-model hosting choices, context engineering, AI Search/Genie/MCP/Lakebase composition, retrieval evaluation | `figure\mlod_0701.png` through `mlod_0710.png` |
| 8 | `8_MLflow_for_GenAI\content.md` | GenAI flavors, trace anatomy, trace metadata, scorer layers, prompt optimization, logging/registering agent resources | `figure\mlod_0801.png`, `0802.png`, `0803.png`, `0805.png`, `0806.png`, `0808.png`, `0809.png` |
| 9 | `9_Deploying_in_Monitoring_LLM_Based_Systems\content.md` | Model Serving separation, agent deployment, DAB/Lakeflow workflows, code-vs-model promotion, tiered monitoring, cost attribution | `figure\mlod_0901.png`, `0902.png`, `0903.png` |
| 10 | `10_AI_Governance\content.md` | lifecycle governance, Git/IaC approvals, record-keeping, human oversight, risk and release checklist | `figure\mlod_1001.png` |

`6_ Monitoring_ML_Applications\content.md` is currently empty, so use the
existing monitoring skill and current Databricks documentation for that chapter.

## Patterns incorporated

### LLM system composition

The book’s system view is broader than a model: foundation model, context/data
processing, retrieval, structured analytics, MCP tools, memory, MLflow tracing
and evaluation, Model Serving, monitoring, and cost/governance all participate
in behavior. The skill therefore requires a component inventory and release
manifest.

### Context engineering

Prompts are only one part of context. Track tools, retrieved chunks, metadata
filters, conversation history, memory, truncation/summarization, and intermediate
steps. For retrieval, compare hybrid search, filtering, reranking, query
rewriting, and chunking with a test dataset rather than intuition.

### Trace metadata

The book examples link `git_sha`, model version, endpoint name, session ID, and
request ID to MLflow traces. The skill generalizes this to release ID, prompt,
served entity, index, tool, and deployment identities while warning against
secret/raw-payload leakage.

### Evaluation loop

Start with a small expert-agreed dataset; add expectations and negative cases;
use code-based, model-based, and human graders; align judges; evaluate before
registration; then sample production traces and feed confirmed failures back
into regression tests.

### Promotion model

The book emphasizes that most LLM applications promote code/configuration and
environment-specific resources rather than a standalone foundation-model
artifact. The skill retains this distinction while requiring immutable MLflow/
UC/endpoint evidence for custom artifacts.

### Deployment and monitoring jobs

The book separates preprocessing/index sync, agent log/register/deploy, and
monitoring workflows. It also demonstrates cheap checks over all traces and
sampled LLM judges, with a governed table/dashboard for operational review.

### Governance checklist

The book’s governance chapter maps documentation, IaC, data/model lineage,
quality gates, PR approvals, deployment approvals, rollback, record-keeping,
human oversight, security, and monitoring into a lifecycle checklist. These
controls are included in the core skill rather than treated as a separate
compliance afterthought.

## Caveat

The book is early-release material and platform APIs evolve. Treat its diagrams
and examples as architecture patterns. Re-check current Databricks and MLflow
documentation, workspace feature availability, endpoint capabilities, and SDK
schemas before executing production changes.
