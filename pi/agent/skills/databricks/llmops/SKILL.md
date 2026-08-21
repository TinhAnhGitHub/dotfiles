---
name: databricks-llmops
description: >
  End-to-end LLMOps and AgentOps on Databricks: turn Git changes to prompts,
  orchestration, tools, retrieval, models, evaluations, and infrastructure into
  governed, versioned, observable releases. Use this skill whenever a user asks
  about production LLM applications, agent workflows, Git-to-production CI/CD,
  component lineage, prompt/version management, evaluation gates, custom
  Model Serving endpoint versioning, canary or rollback releases, tracing,
  monitoring, cost attribution, safety, or AI governance—even when they do not
  explicitly say LLMOps.
compatibility: Requires Databricks CLI/SDK and MLflow; verify workspace and library versions before using preview APIs.
metadata:
  version: "0.1.0"
  parent: databricks
---

# Databricks LLMOps

Use this skill as the orchestration layer for a production LLM application or
agent. It does not replace the narrow MLflow, Model Serving, Vector Search,
MCP, Jobs, DABs, Apps, Lakebase, or platform skills. It connects them into a
repeatable release system and makes the complete system—not just the model—the
unit of versioning, evaluation, deployment, and audit.

## Load the right companion skills

Load `databricks` first. Then select companions from this table:

| Concern | Companion skill | Use it for |
|---|---|---|
| MLflow GenAI lifecycle | `../../mlflow/SKILL.md` | MLflow 3 concepts and managed-vs-OSS boundaries |
| Trace/evaluation/monitoring | `../../mlflow/evaluation-monitoring/SKILL.md` | Traces, scorers, judges, feedback, regression, production evaluation |
| App and Git lineage | `../../mlflow/version-tracking/SKILL.md` | LoggedModel, Git identity, active model, configuration snapshots |
| Prompt Registry and optimization | `../../mlflow/prompt-registry/SKILL.md` | Prompt versions, aliases, templates, model config, automatic lineage, optimization, and model migration |
| Agent packaging | `../../mlflow/genai-flavors/SKILL.md` | ResponsesAgent, Models from Code, signatures, resources, dependencies |
| Registry promotion | `../../mlflow/model-registry/SKILL.md` | UC model versions, aliases, promotion, rollback evidence |
| MCP dependencies | `../../mlflow/mcp-registry/SKILL.md` | MCP server/tool versions, aliases, access, snapshots |
| Serving runtime | `../model-serving/SKILL.md` | Endpoint CRUD, served entities, routes, readiness, logs, metrics |
| Retrieval/context | `../vector-search/SKILL.md` | AI Search/Vector Search indexes, sync, retrieval quality |
| Workflow orchestration | `../jobs/SKILL.md` | Lakeflow Jobs, task DAGs, retries, schedules, notifications |
| Infrastructure promotion | `../dabs/SKILL.md` | Multi-target `databricks.yml`, resource IaC, CI/CD deployment |
| Agent memory | `../lakebase/SKILL.md` | Session state, branches, permissions, connection patterns |
| Applications | `../apps/SKILL.md` | Databricks Apps and app-to-endpoint permissions |
| Platform/security | `../platform/SKILL.md` | UC grants, secrets, system tables, workspace operations |

Read only the companion references relevant to the request. For exact current
CLI/SDK fields, inspect the installed tool and current documentation rather than
copying a stale JSON shape from an example.

## Core operating model

Treat an LLM system as a composed release, not as a single model artifact:

```
scope -> compose context -> instrument -> evaluate -> package/register
       -> promote -> deploy -> observe -> learn/rollback
```

The release unit includes, as applicable:

- application and orchestration code;
- system/developer/user prompt templates and prompt versions;
- provider, foundation, fine-tuned, embedding, and judge model identifiers;
- tool and MCP server definitions, permissions, and tool snapshots;
- source data, chunking/embedding configuration, index identity, and sync state;
- memory schema and session-state behavior;
- guardrails, safety policies, routing/fallback rules, and data-retention policy;
- MLflow LoggedModel/package and Unity Catalog registered model version;
- evaluation dataset digest, scorers, judge configuration, and thresholds;
- endpoint name, served entity/version, traffic routes, and endpoint config;
- bundle target, job/run IDs, dependency lockfile digest, approvers, and release ID.

If a component can change behavior, cost, access, or compliance, give it an
identity and include it in the release record.

## Golden workflow

### 1. Scope the system before building it

Document intended use, non-goals, users, risk level, latency/cost SLOs, quality
criteria, human-override requirements, data boundaries, and ownership. Convert
each important product requirement into at least one positive and one negative
evaluation case. Define what happens when the system is uncertain, unsafe,
over budget, unavailable, or unable to retrieve context.

### 2. Keep the repository as the system source of truth

Prefer one repository containing code, prompts-as-code, evaluation data/schema,
resource definitions, tests, operational documentation, and release metadata.
Use a layout like:

```
src/agent/                 # orchestration and tools
prompts/                   # templates, metadata, changelog
evals/                     # cases, expectations, slices, scorers
resources/                 # DAB job/endpoint/app/dashboard definitions
tests/                     # unit, contract, smoke, regression tests
docs/                      # architecture, model card, runbook, risk record
pyproject.toml             # pinned dependencies and build metadata
databricks.yml             # targets and bundle variables
```

Do not put secrets, raw private prompts, or full dirty diffs into MLflow tags.
Record a commit SHA and a safe status/config digest; retain sensitive evidence
only in an approved secured artifact store.

### 3. Make every change reviewable through Git

Use feature branches and pull requests. Protect the main branch with required
reviewers, CI checks, dependency/security scanning, prompt/evaluation review,
and deployment approval. Treat changes to prompts, model IDs, tool schemas,
retrieval settings, guardrails, endpoint configuration, and DAB resources as
behavioral changes—not as harmless configuration edits.

At build time capture:

```text
git_sha, repository, branch/tag, dirty_state, source_digest,
dependency_lock_digest, bundle_commit, build/run_id
```

If Databricks Git Folders do not expose reliable repository metadata, inject the
commit from CI and mark the source identity as externally supplied. Never claim
reproducibility from an untracked working tree.

### 4. Instrument before optimizing

Trace the request, agent chain, model calls, retrieval, embedding, reranking,
tool/MCP calls, memory reads/writes, guardrail decisions, errors, and final
output. Attach stable metadata such as `release_id`, `git_sha`, `prompt_version`,
`model_version`, `endpoint_name`, `served_entity`, `session_id`, and
`client_request_id`. Keep high-cardinality or sensitive values out of tags;
use governed metadata/payload storage with access controls and retention.

### 5. Evaluate the candidate before registration or promotion

Use a small, high-quality seed set first, then grow it with production failures,
human-reviewed examples, and representative slices. Hold the dataset, scorers,
judge model/configuration, sampling policy, and test environment constant when
comparing candidates. Evaluate traces—not only final text—when tool choice,
retrieval, safety, or multi-turn behavior matters.

Use a tiered evaluator:

- deterministic checks for every test/request: schema, required citations,
  policy violations, tool arguments, latency, token/cost limits;
- model-based judges on a controlled sample: relevance, correctness,
  groundedness, completeness, tone, safety, retrieval sufficiency;
- human review for acceptance criteria, difficult cases, judge calibration,
  overrides, and high-impact decisions.

Gate on absolute thresholds, baseline deltas, critical-slice regressions,
operational SLOs, and security checks. A higher aggregate score does not excuse
a critical safety, access-control, or quality regression.

### 6. Log and register the complete executable

For custom agents, package the orchestration code and declare all resources:
serving endpoints, Vector Search/AI Search indexes, UC tables/functions, Genie
spaces, SQL warehouses, MCP servers, and memory dependencies. Use a stable
configuration contract with environment-specific resource IDs injected at
release time. Record evaluation results, source identity, resource list,
dependency digest, and release metadata on the MLflow model/run before creating
the UC model version.

Resolve any approval alias to an immutable numbered model version before deploy.
Aliases are useful policy pointers; they are not deployment evidence.

### 7. Promote code and configuration, not an imaginary standalone agent model

For most LLM applications, the foundation model is a managed API and the
behavioral artifact is the combination of code, prompt, tools, context, and
configuration. Deploy the same reviewed source revision into each target with
environment-specific resource bindings. Use DAB targets such as `dev`, `acc`,
and `prd`, and make the deployment pipeline the only normal production writer.

A practical workflow is:

1. PR CI validates code, prompts, schemas, dependencies, DABs, and evals.
2. A release job runs smoke/evaluation gates and logs the candidate.
3. The candidate is registered in Unity Catalog with immutable metadata.
4. An approval promotes the release and resolves the exact model version.
5. A deployment job updates the endpoint and records the resulting config.
6. A post-deploy smoke test invokes the stable endpoint and validates traces.
7. Monitoring and rollback remain available as separate repeatable jobs.

Keep data preprocessing/index synchronization separate from agent release
deployment unless they have a deliberate dependency. This makes failures easier
to isolate and allows context data to refresh without silently changing the
agent release.

### 8. Operate with feedback and rollback

Synchronize traces to governed storage, run cheap checks broadly, sample costly
LLM judges, surface human review, and feed confirmed failures back into the
regression set. Alert on quality, safety, latency, errors, tool/retrieval
behavior, token usage, and cost. A rollback is a controlled endpoint config
update to a known-good served entity and release manifest—not merely moving a
registry alias.

## Git-to-production release contract

Every release should produce one machine-readable record, for example:

```yaml
release_id: support-agent-2026-08-01-gabc1234
source:
  git_sha: abc1234
  dirty: false
  dependency_lock_digest: sha256:...
application:
  logged_model_id: m-...
  registered_model: catalog.schema.support_agent
  registered_model_version: "17"
  prompt: prompts:/catalog.schema.support-agent/12
  provider_model: databricks-<pinned-model-id>
context:
  retriever_index: catalog.schema.support_index
  source_table_version: 481
  embedding_model: <pinned-endpoint>
tools:
  mcp_servers: [<server-version-or-alias>]
  tool_snapshot_digest: sha256:...
evaluation:
  dataset_digest: sha256:...
  scorers: [correctness, groundedness, safety, latency_budget]
  baseline_release_id: support-agent-2026-07-28-gdef5678
  gates: {correctness_min: 0.85, safety_min: 0.99}
deployment:
  target: prd
  endpoint_name: support-agent
  endpoint_config_snapshot_digest: sha256:...
  served_entity: support-agent-v17
  traffic: {support-agent-v17: 100}
evidence:
  evaluation_run_id: <run-id>
  bundle_run_id: <run-id>
  approvers: [<user-or-group>]
```

Adapt fields to the actual API and avoid inventing IDs. The important property
is that a trace can be followed backward from endpoint and served entity to
release, model, code, prompt, tools, context, evaluation, and approver.

## Custom Model Serving endpoint versioning

Keep these identities distinct:

| Identity | Meaning | Release rule |
|---|---|---|
| Prompt/app version | Behavioral source | New version for behavior/config changes |
| MLflow LoggedModel | Tracked executable candidate | Link to Git, config, traces, evals |
| UC registered model version | Immutable packaged artifact | Resolve and record the number |
| Served entity | Endpoint deployment unit | Pin `entity_version`; give it a unique name |
| Endpoint config snapshot | Observed entities and traffic routes | Record the platform response plus a caller-owned digest; do not assume a universal integer config version |
| Stable endpoint name | Client contract | Keep stable while versions change |

Moving a UC alias does not update a served entity that pins a model version.
Explicitly update endpoint configuration, wait for both readiness and config
update completion, then smoke-test the exact route. For canaries, deploy
champion and challenger as separate served entities, record their identities in
traces/inference evidence, and ensure route percentages total 100. Roll back by
restoring the prior known-good endpoint config and release manifest.

For Databricks Agent Framework or `agents.deploy`, pass release metadata through
the deployment job/configuration and, where supported, inject values such as
`GIT_SHA`, `MODEL_VERSION`, `MODEL_SERVING_ENDPOINT_NAME`, and the MLflow
experiment ID. These names are not automatically guaranteed environment
variables for every deployment path. Use request/session IDs to join client
events, endpoint telemetry, and MLflow traces. Verify current support for endpoint
features such as traffic splitting, AI Gateway controls, inference tables,
guardrails, and express deployment before promising them for a custom
`ResponsesAgent` endpoint.

## Prompt and context operations

- Store prompt templates and prompt metadata in Git; use the [MLflow Prompt
  Registry](../../mlflow/prompt-registry/SKILL.md) where immutable prompt
  versions, aliases, automatic trace/model linking, or optimization workflows
  are useful. A prompt version is a release component, not a hidden string.
- Use a fully qualified Unity Catalog prompt name for Databricks-managed MLflow
  when the workspace requires it, such as
  `prompts:/catalog.schema.support-agent/12`; verify the target MLflow backend.
- Give each prompt a version, owner, purpose, input/output contract, model
  compatibility note, examples, safety constraints, and changelog.
- Never substitute environment secrets or unreviewed user content into a
  system prompt at build time.
- Treat prompt changes like hyperparameter changes: run the same regression
  dataset, record the candidate, compare slices, and release deliberately.
- Separate prompt engineering from context engineering. Track retrieval,
  memory, tool availability, history truncation, and context assembly because
  identical prompts can behave differently with different context.
- For RAG, version source data/table snapshots, chunking, embedding endpoint,
  index, filters, query type, reranker, and retrieval evaluation. Prefer
  hybrid search, metadata filters, and reranking only when measurements justify
  their latency and cost.

## Production monitoring checklist

At minimum monitor:

- request success/error rate, timeout rate, queue time, p50/p95/p99 latency;
- input/output tokens, provider/model usage, cost per request and per tenant;
- tool/MCP call count, failure rate, retries, invalid arguments, and loops;
- retrieval hit rate, empty-context rate, Recall@K/Precision@K when labels exist;
- schema/format failures, refusal and fallback rates, guardrail violations;
- sampled groundedness, correctness, relevance, safety, and user feedback;
- release, endpoint, served entity, Git SHA, prompt, and model dimensions.

Run code-based checks on all traffic where affordable and LLM-based judges on a
representative sample (often 5–20%, tuned to risk and cost). Critical safety,
security, access-control, and schema checks should remain deterministic and
all-traffic where feasible; do not hide high-impact failures in a small sample.
Stratify sampling for low-confidence, safety-triggered, new-release, high-cost,
and high-error traffic rather than relying only on random sampling.

Use usage policies/tags consistently for serverless Jobs, serving, AI Search,
Lakebase, and other resources **where the target resource supports them**;
verify resource-specific fields and policy precedence and use direct tags as a
fallback. Join billing/system tables with trace token usage; provider invoices
and some pay-per-token costs may require a separate cost source. Protect raw
payloads and apply retention/access controls.

## Safety, security, and governance

- Use least-privilege UC permissions, endpoint ACLs, app resource grants, and
  secret scopes/OAuth; do not embed PATs, API keys, or client secrets in Git.
- Decide explicitly whether a resource uses service-principal identity or
  on-behalf-of-user access. OBO improves per-user authorization and auditability
  but requires compatible resources and permissions.
- Start new guardrails in log/observe mode when safe, measure false positives,
  then enforce. Put domain constraints and deterministic validators in agent
  logic as well as model-level controls.
- Keep technical documentation, architecture, risk decisions, model/release
  cards, limitations, runbooks, and approval records in the repository or an
  approved governed location, updated in the same pull requests as code.
- Record data provenance/licensing, representativeness/bias checks, schema and
  drift evidence, cybersecurity events, human review/override IDs and reasons,
  deployer instructions, and model limitations when the risk profile requires
  them.
- Add human approval/override and a safe stop path for high-impact use cases.
- Pin dependencies and CI actions, scan the software supply chain, validate
  prompt/tool input boundaries, and test prompt injection, data exfiltration,
  PII leakage, unsafe content, and denial-of-service behavior.

## Anti-patterns to reject

| Anti-pattern | Why it fails | Better pattern |
|---|---|---|
| “latest” is deployed directly | It is mutable and not reproducible | Resolve alias to a numbered version and record it |
| Alias moved, endpoint left untouched | Runtime still serves the pinned entity | Update endpoint config explicitly and verify readiness |
| Prompt edits bypass CI | Quality and safety regressions are invisible | Prompt PR + regression eval + release metadata |
| Only final answers are logged | Tool/retrieval failures cannot be diagnosed | Trace the full execution graph |
| Full LLM judging on every request | Cost and latency become unbounded | Tier 1 all traffic, sampled Tier 2, human calibration |
| Separate undocumented resource setup | Rebuilds drift across environments | DABs/SDK provisioning plus a release manifest |
| Manual production hotfixes | Auditability and rollback are lost | Protected, approved pipeline or documented break-glass path |

## Response contract for this skill

When designing or implementing an LLMOps workflow:

1. State the system boundary and component inventory.
2. Draw or describe the dev → evaluation → registry → serving → monitoring loop.
3. Define the Git, prompt, model, endpoint, data/index, tool, and evaluation
   identities that must be recorded.
4. Choose the companion skills and read their current references.
5. Separate immutable artifacts from mutable aliases and stable client contracts.
6. Show quality, safety, cost, and rollback gates—not only deployment commands.
7. Include environment-specific configuration and permissions without leaking
   secrets.
8. Call out preview/release-sensitive features and validate exact CLI/SDK schemas.

## References

Load these progressively:

- [Workflow patterns](references/workflow-patterns.md) — Git, CI/CD, DAB targets, jobs, handoffs, and rollback.
- [Lineage and release manifest](references/lineage-and-release-manifest.md) — component identity and audit schema.
- [Serving versioning](references/serving-versioning.md) — custom endpoint versions, canary, readiness, and rollback.
- [Evaluation and prompt operations](references/evaluation-and-prompt-ops.md) — datasets, scorers, judges, prompt releases, and gates.
- [Prompt Registry](references/prompt-registry.md) — Prompt Registry subsections, aliases, templates, model config, caching, lineage, optimization, and model migration.
- [Monitoring, cost, and safety](references/monitoring-cost-safety.md) — traces, tiered evaluation, FinOps, security, and governance.
- [Book-derived patterns](references/book-patterns.md) — synthesized notes and the local chapter/figure map.
- [Source ledger](references/source-ledger.md) — official documentation and local source provenance.

Use [scripts/inspect_llmops_capabilities.py](scripts/inspect_llmops_capabilities.py)
before relying on installed MLflow/Databricks APIs. Use
[evals/evals.json](evals/evals.json) as regression prompts for this skill.
