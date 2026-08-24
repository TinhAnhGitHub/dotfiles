# LLMOps workflow patterns

This reference turns the LLMOps lifecycle into deployable workflow shapes. Load
it when designing a repository, Lakeflow Jobs DAG, DAB target, GitHub pipeline,
or release/rollback process.

## Recommended repository boundary

Keep application code, prompt templates, evaluation contracts, resource
definitions, tests, and operational documentation in one version-controlled
repository unless governance requires a deliberate split. A split repository
must still publish a release manifest that records the exact revision of every
repository involved.

```text
llm-app/
├── src/agent/                   # deterministic orchestration + tools
├── prompts/                     # templates, schemas, owners, changelog
├── evals/                       # cases, expectations, slices, scorers
├── resources/                   # DAB jobs/endpoints/apps/dashboards
├── tests/                       # unit, contract, smoke, regression
├── docs/                        # architecture, risk, model/release card, runbook
├── pyproject.toml               # pinned package/build metadata
├── uv.lock                      # or the project’s approved lockfile
└── databricks.yml               # dev/acc/prd targets and variables
```

## Three workflow lanes

Do not make every change run every pipeline. Separate the workflows so each has
an explicit owner and trigger:

| Lane | Trigger | Responsibilities | Typical cadence |
|---|---|---|---|
| Context/data | new data or schedule | ingest, parse, chunk, embed, sync index, data quality | scheduled/event-driven |
| Agent release | approved Git change | test, evaluate, log/register, deploy, smoke test | on demand/after merge |
| Production monitoring | schedule/stream | read traces, score, alert, dashboard, curate failures | frequent cheap checks + sampled judges |

Context refresh should not silently create a new agent release. If a retrieval
index or prompt changes behavior materially, create a new release record and
run the appropriate evaluation suite.

## CI gate sequence

Run these checks on every pull request that changes behavior:

1. Format, lint, type-check, unit tests, and dependency/license/security scans.
2. Validate prompt templates, tool schemas, response schemas, and config.
3. Build a clean artifact from the commit; record commit and dependency digests.
4. Run deterministic smoke traces with mocked or approved test resources.
5. Run the regression dataset with fixed scorers/judge settings.
6. Compare with the approved baseline, including critical slices and latency/cost.
7. Validate DABs and render/inspect endpoint configuration without mutating prod.
8. Publish evidence and require review for high-impact, safety, or infra changes.

Do not merge solely because the mean score improved. Require no critical-slice,
safety, schema, access-control, or operational SLO regression.

## CD promotion sequence

Use separate deployment targets and approvals:

```text
feature branch
  -> PR checks
  -> merge to protected main
  -> deploy/evaluate in dev
  -> approval + deploy to acceptance
  -> acceptance smoke/quality checks
  -> production approval
  -> deploy endpoint config
  -> post-deploy smoke + watch window
```

The CD job should pass `git_sha`, `release_id`, target, and deployment run ID
into the release job. Use DAB variables for catalog/schema/endpoint names and
secrets references, not copied environment files with credentials.

## Lakeflow job decomposition

A useful decomposition is:

```text
context_pipeline (scheduled)
  -> data_quality / index_sync

release_job (on demand)
  -> evaluate_candidate
  -> log_and_register
  -> approval/condition
  -> deploy_or_update_endpoint
  -> smoke_test

monitoring_job (scheduled)
  -> read_unscored_traces
  -> deterministic_scores_all
  -> sample_expensive_scores
  -> log_feedback
  -> update_metrics_view / alert
```

Keep log/register and deploy as separate tasks/jobs when independent reruns are
valuable. If the platform cannot pass task values across jobs, use an explicit
immutable model/release record as the handoff. Avoid using a mutable `latest`
pointer as the only handoff in concurrent development runs.

## Environment rules

- Keep the same source revision and workflow shape across environments.
- Bind environment-specific UC objects, endpoints, warehouses, MCP URLs, and
  memory projects through target variables.
- Use separate experiments, catalogs/schemas, usage policies, and secrets where
  isolation is required.
- Keep production write access with the deployment identity; use break-glass
  access only with an incident record.
- Store the release manifest and evaluation evidence where the approver and
  operator can retrieve them later.

## Rollback workflow

1. Identify the failing release from a trace, alert, or user report.
2. Resolve the release manifest and exact served entity/config.
3. Restore the previous endpoint configuration or deploy the known-good version.
4. Verify readiness, direct/entity smoke behavior, stable endpoint behavior, and
   trace metadata.
5. Keep the bad release available for diagnosis; do not delete evidence first.
6. Turn the failure into an evaluation case, expectation, and regression test.
7. Record incident impact, approvers, rollback time, and corrective release.

## DAB design notes

Use `databricks bundle validate --strict --target <target>` before deployment.
Prefer resources-as-code for jobs, apps, dashboards, permissions, and target
variables. If SDK-created resources are necessary, make their IDs and lifecycle
explicit in the release manifest and avoid duplicating policy/config values in
multiple files without a consistency check.
