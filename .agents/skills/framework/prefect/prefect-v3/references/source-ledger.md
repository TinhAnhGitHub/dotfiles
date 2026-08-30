# Prefect v3 source ledger

Research date: 2026-08-02. Research subagents used the exact model
`opencode/deepseek-v4-flash-free`. Sources below are official Prefect
documentation or first-party companion repositories. The ledger records the
canonical page and the material used from it; it is not a claim that every
example on a page is current. Where the docs disagree, the skill calls out the
conflict and asks the user to verify the installed version.

## Roots and navigation

| Source | Contribution |
|---|---|
| [Get started](https://docs.prefect.io/v3/get-started) | Prefect 3 overview, install/quickstart links, feature model. |
| [Introduction](https://docs.prefect.io/v3/get-started/index) | Current v3 orientation and concepts entry point. |
| [Install](https://docs.prefect.io/v3/get-started/install) | Python floor, install commands, client/server compatibility. |
| [Quickstart](https://docs.prefect.io/v3/get-started/quickstart) | Small flow, Cloud/local server, serve/deploy first run. |
| [Concepts index](https://docs.prefect.io/v3/concepts) | Canonical concepts navigation. |
| [How-to index](https://docs.prefect.io/v3/how-to-guides) | Canonical how-to navigation. |
| [Advanced index](https://docs.prefect.io/v3/advanced) | Advanced topic navigation and scope. |
| [Official sitemap](https://docs.prefect.io/llms.txt) | Page inventory and official markdown-page convention. |
| [Full official docs dump](https://docs.prefect.io/llms-full.txt) | Cross-check for child-page discovery. |
| [Versioning policy](https://docs.prefect.io/v3/release-notes/versioning) | Client/server compatibility and version caveats. |

## Concepts: workflows

| Source | Contribution |
|---|---|
| [Flows](https://docs.prefect.io/v3/concepts/flows) | Flow decorator, parameters, nested flows, lifecycle, final state. |
| [Tasks](https://docs.prefect.io/v3/concepts/tasks) | Task invocation modes, futures, background task model. |
| [Assets](https://docs.prefect.io/v3/concepts/assets) | Asset keys, materialization, dependencies, Cloud scope. |
| [Caching](https://docs.prefect.io/v3/concepts/caching) | Cache policies, keys, persistence, expiration, locks/isolation. |
| [States](https://docs.prefect.io/v3/concepts/states) | State types/transitions, terminal behavior, hooks. |
| [Runtime context](https://docs.prefect.io/v3/concepts/runtime-context) | `prefect.runtime`, run contexts, context availability. |
| [Artifacts](https://docs.prefect.io/v3/concepts/artifacts) | Human-readable persisted output types and UI/API model. |
| [Task runners](https://docs.prefect.io/v3/concepts/task-runners) | Thread/process/Dask/Ray runners, futures, pickling/deadlock caveats. |
| [Global concurrency limits](https://docs.prefect.io/v3/concepts/global-concurrency-limits) | Slot leases, rate decay, strict mode, limits comparison. |
| [Tag concurrency limits](https://docs.prefect.io/v3/concepts/tag-based-concurrency-limits) | Tag slots, multi-tag behavior, newer `tag:<tag>` backing. |
| [Rate limits and retention](https://docs.prefect.io/v3/concepts/rate-limits) | Cloud/API rate and retention context discovered during inventory. |
| [Webhooks concept](https://docs.prefect.io/v3/concepts/webhooks) | Cloud webhook scope discovered during inventory. |

## How-to: workflow implementation

| Source | Contribution |
|---|---|
| [Write and run](https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run) | `@flow`/`@task`, decorator options, timeouts, workflow navigation. |
| [Use assets](https://docs.prefect.io/v3/how-to-guides/workflows/assets) | `@materialize`, URI keys, dependencies, metadata patterns. |
| [Retry work](https://docs.prefect.io/v3/how-to-guides/workflows/retries) | Retry delays, exponential backoff, conditions, defaults. |
| [Retry a flow run](https://docs.prefect.io/v3/how-to-guides/workflows/retry-flow-runs) | CLI/API manual retry semantics and entrypoint caveat. |
| [Custom metadata](https://docs.prefect.io/v3/how-to-guides/workflows/custom-metadata) | Flow name, description, run-name templates/callables. |
| [Pass inputs](https://docs.prefect.io/v3/how-to-guides/workflows/pass-inputs) | Typed parameters, validation, Pydantic coercion. |
| [Add logging](https://docs.prefect.io/v3/how-to-guides/workflows/add-logging) | Run logger, print capture, context propagation, log CLI. |
| [Access runtime info](https://docs.prefect.io/v3/how-to-guides/workflows/access-runtime-info) | Runtime attributes and None-safe behavior. |
| [Run concurrently](https://docs.prefect.io/v3/how-to-guides/workflows/run-work-concurrently) | `.submit`, `.map`, futures, `wait`, dependencies, async patterns. |
| [Cache workflow steps](https://docs.prefect.io/v3/how-to-guides/workflows/cache-workflow-steps) | `persist_result`, policies, refresh, expiration, S3 storage. |
| [Run background tasks](https://docs.prefect.io/v3/how-to-guides/workflows/run-background-tasks) | `task.serve`, `.delay`, task worker, deferred maps. |
| [State-change hooks](https://docs.prefect.io/v3/how-to-guides/workflows/state-change-hooks) | Hook names, signatures, retry timing, best-effort boundary. |
| [Create artifacts](https://docs.prefect.io/v3/how-to-guides/workflows/artifacts) | Link/Markdown/progress/table/image APIs and CLI. |
| [Test workflows](https://docs.prefect.io/v3/how-to-guides/workflows/test-workflows) | Test harness, `.fn`, log capture, async/xdist pitfalls. |
| [Global concurrency](https://docs.prefect.io/v3/how-to-guides/workflows/global-concurrency-limits) | CLI/API/Terraform and sync/async concurrency/rate-limit use. |
| [Tag concurrency](https://docs.prefect.io/v3/how-to-guides/workflows/tag-based-concurrency-limits) | Task tags and legacy CLI/client APIs. |

## Concepts and how-to: deployments

| Source | Contribution |
|---|---|
| [Deployments concept](https://docs.prefect.io/v3/concepts/deployments) | Deployment schema, entrypoint, pool, schedules, triggers, versions. |
| [Schedules concept](https://docs.prefect.io/v3/concepts/schedules) | Cron/Interval/RRule, scheduler window and settings. |
| [Work pools concept](https://docs.prefect.io/v3/concepts/work-pools) | Hybrid/push/managed taxonomy and queue behavior. |
| [Workers concept](https://docs.prefect.io/v3/concepts/workers) | Worker types, polling, heartbeat, install policy. |
| [Create deployments](https://docs.prefect.io/v3/how-to-guides/deployments/create-deployments) | `serve` vs `deploy`, CLI/Python/Terraform/API routes. |
| [Run deployments](https://docs.prefect.io/v3/how-to-guides/deployments/run-deployments) | CLI and `run_deployment` parameters, scheduling, `as_subflow`. |
| [Create schedules](https://docs.prefect.io/v3/how-to-guides/deployments/create-schedules) | Python/CLI/YAML schedule creation and version gate. |
| [Manage schedules](https://docs.prefect.io/v3/how-to-guides/deployments/manage-schedules) | Pause/resume/clear and bulk-operation warnings. |
| [Deploy via Python](https://docs.prefect.io/v3/how-to-guides/deployments/deploy-via-python) | `flow.deploy`, images, source, job variables, multi-flow deploy. |
| [Prefect YAML](https://docs.prefect.io/v3/how-to-guides/deployments/prefect-yaml) | Build/push/pull steps, templating, fields, aliases, deletion semantics. |
| [Store flow code](https://docs.prefect.io/v3/how-to-guides/deployments/store-flow-code) | Local/Git/blob/image storage, credentials, pull steps. |
| [Version deployments](https://docs.prefect.io/v3/how-to-guides/deployments/versioning) | Cloud version history, code commit/image digest pinning. |
| [Customize job variables](https://docs.prefect.io/v3/how-to-guides/deployments/customize-job-variables) | Deployment/run/Automation/Terraform overrides. |

## Concepts and how-to: configuration

| Source | Contribution |
|---|---|
| [Variables concept](https://docs.prefect.io/v3/concepts/variables) | JSON configuration, limits, non-encryption warning. |
| [Blocks concept](https://docs.prefect.io/v3/concepts/blocks) | Block classes/documents, SecretStr, built-ins/integrations. |
| [Settings/profiles](https://docs.prefect.io/v3/concepts/settings-and-profiles) | Precedence, profiles, files, version gates. |
| [Server concept](https://docs.prefect.io/v3/concepts/server) | Server control plane, SQLite/Postgres and migrations. |
| [Telemetry concept](https://docs.prefect.io/v3/concepts/telemetry) | SDK/server telemetry and opt-out controls. |
| [Store secrets](https://docs.prefect.io/v3/how-to-guides/configuration/store-secrets) | Secret and credential block usage. |
| [Share configuration](https://docs.prefect.io/v3/how-to-guides/configuration/variables) | Variable set/get/unset and YAML use. |
| [Manage settings](https://docs.prefect.io/v3/how-to-guides/configuration/manage-settings) | Config CLI, profiles, TOML, `.env`, per-process settings. |

## Concepts and how-to: events and automations

| Source | Contribution |
|---|---|
| [Automations concept](https://docs.prefect.io/v3/concepts/automations) | Trigger/action model, targets, Jinja templates, Cloud actions. |
| [Events concept](https://docs.prefect.io/v3/concepts/events) | Event schema, resource/related-resource grammar, event automation. |
| [Event triggers](https://docs.prefect.io/v3/concepts/event-triggers) | Event/proactive/metric/compound/sequence trigger schemas. |
| [Create automations](https://docs.prefect.io/v3/how-to-guides/automations/creating-automations) | UI/CLI/Python automation creation. |
| [Deployment triggers](https://docs.prefect.io/v3/how-to-guides/automations/creating-deployment-triggers) | Deployment trigger YAML/Python/CLI/Terraform and quota. |
| [Custom notifications](https://docs.prefect.io/v3/how-to-guides/automations/custom-notifications) | Custom Webhook notification block and templates. |
| [Chain deployments](https://docs.prefect.io/v3/how-to-guides/automations/chaining-deployments-with-events) | Related-resource matching for upstream/downstream flows. |
| [Event payloads](https://docs.prefect.io/v3/how-to-guides/automations/passing-event-payloads-to-flows) | `emit_event`, JSON/Jinja parameter bridge, resource targeting. |
| [Parameters in templates](https://docs.prefect.io/v3/how-to-guides/automations/access-parameters-in-templates) | Jinja access to prior flow parameters. |

## Workflow infrastructure

| Source | Contribution |
|---|---|
| [Manage work pools](https://docs.prefect.io/v3/how-to-guides/deployment_infra/manage-work-pools) | Pool CLI, templates, concurrency, API/Terraform pointers. |
| [Local processes](https://docs.prefect.io/v3/how-to-guides/deployment_infra/run-flows-in-local-processes) | `serve`, process execution, source polling, pause-on-shutdown. |
| [Managed infrastructure](https://docs.prefect.io/v3/how-to-guides/deployment_infra/managed) | Cloud-managed pool, official image, limits, egress, quotas. |
| [Managed AWS identity](https://docs.prefect.io/v3/how-to-guides/deployment_infra/managed-aws-federated-identity) | Workload identity companion page. |
| [Serverless compute](https://docs.prefect.io/v3/how-to-guides/deployment_infra/serverless) | Push pool types, provisioning, provider permissions, architecture. |
| [Docker](https://docs.prefect.io/v3/how-to-guides/deployment_infra/docker) | Docker pool/worker, image build/push, dependency caveats. |
| [Static Docker container](https://docs.prefect.io/v3/how-to-guides/deployment_infra/serve-flows-docker) | Long-lived container, `.env`, runner health endpoint. |
| [Kubernetes](https://docs.prefect.io/v3/how-to-guides/deployment_infra/kubernetes) | Cluster/RBAC/Helm/worker/image setup and troubleshooting. |
| [Modal](https://docs.prefect.io/v3/how-to-guides/deployment_infra/modal) | Modal push pool, Git pull, `uv sync`, CI/CD. |
| [Coiled](https://docs.prefect.io/v3/how-to-guides/deployment_infra/coiled) | Coiled push pool, package sync, cost/data boundary. |

## Prefect Cloud and self-hosted

| Source | Contribution |
|---|---|
| [Connect to Cloud](https://docs.prefect.io/v3/how-to-guides/cloud/connect-to-cloud) | Interactive/CI login, workspace/API URL/key. |
| [Cloud workspaces](https://docs.prefect.io/v3/how-to-guides/cloud/workspaces) | Workspace lifecycle, roles, transfer/retention. |
| [Cloud webhook](https://docs.prefect.io/v3/how-to-guides/cloud/create-a-webhook) | UI creation, HTTP request and event output. |
| [Cloud API keys](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/api-keys) | Key lifecycle, expiry, service accounts, one-time reveal. |
| [Cloud user/account index](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/index) | Account-management navigation. |
| [Cloud roles](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/manage-roles) | Role/access scope. |
| [Cloud teams](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/manage-teams) | Team-management scope. |
| [Cloud service accounts](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/service-accounts) | Machine identities. |
| [Cloud ACLs](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/object-access-control-lists) | Object-level access control. |
| [Cloud SSO](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/configure-sso) | SSO scope. |
| [Cloud audit logs](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/audit-logs) | Auditability. |
| [Cloud IP allowlist](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/secure-access-by-ip-address) | Restricted access option. |
| [Cloud PrivateLink](https://docs.prefect.io/v3/how-to-guides/cloud/manage-users/secure-access-by-private-link) | Private network option. |
| [Troubleshoot Cloud](https://docs.prefect.io/v3/how-to-guides/cloud/troubleshoot-cloud) | 401/404, worker role, proxy, late runs, version issues. |
| [Local Server](https://docs.prefect.io/v3/how-to-guides/self-hosted/server-cli) | CLI server, SQLite/Postgres, migrations, multi-worker requirements. |
| [Server Docker](https://docs.prefect.io/v3/how-to-guides/self-hosted/server-docker) | Container startup and API/UI configuration. |
| [Server Windows](https://docs.prefect.io/v3/how-to-guides/self-hosted/server-windows) | PowerShell, paths, firewall, services, encoding. |
| [Server Compose](https://docs.prefect.io/v3/how-to-guides/self-hosted/docker-compose) | Postgres/Redis/API/services/worker topology and no-auth warning. |

## Advanced workflow and automation pages

| Source | Contribution |
|---|---|
| [Customize assets](https://docs.prefect.io/v3/advanced/assets) | `Asset`, `AssetProperties`, metadata overwrite/dependency rules. |
| [Advanced caching](https://docs.prefect.io/v3/advanced/caching) | Isolation, key storage, lock managers, custom cache keys. |
| [Logging customization](https://docs.prefect.io/v3/advanced/logging-customization) | YAML/config overrides, levels, formatters, highlighters. |
| [Transactions](https://docs.prefect.io/v3/advanced/transactions) | Commit/rollback lifecycle, idempotency, lock managers. |
| [Cancel workflows](https://docs.prefect.io/v3/advanced/cancel-workflows) | CANCELLING protocol, infrastructure PID scope, cleanup timeout. |
| [Interactive workflows](https://docs.prefect.io/v3/advanced/interactive) | Pause/suspend/resume, RunInput, send/receive input, validation. |
| [Persist results](https://docs.prefect.io/v3/advanced/results) | ResultStore, storage/serializers, persistence settings, beta defaults. |
| [Background-task web app](https://docs.prefect.io/v3/advanced/background-tasks) | API + task worker + shared results pattern. |
| [UI form building](https://docs.prefect.io/v3/advanced/form-building) | JSON-schema forms, Pydantic, `ImportString`, UI validation limits. |
| [Generate custom SDK](https://docs.prefect.io/v3/advanced/generate-custom-sdk) | Beta SDK generation and regeneration boundaries. |
| [Debounce events](https://docs.prefect.io/v3/advanced/debouncing-events) | `within`/`schedule_after`, burst windows, source re-query pattern. |
| [Zombie flows](https://docs.prefect.io/v3/advanced/detect-zombie-flows) | Heartbeats, proactive Automation, custom state wildcard. |
| [Custom event grammar](https://docs.prefect.io/v3/advanced/use-custom-event-grammar) | User-defined names, `after`/`expect`/`for_each`. |

## Advanced infrastructure, platform, and extensibility

| Source | Contribution |
|---|---|
| [Worker healthchecks](https://docs.prefect.io/v3/advanced/worker-healthchecks) | `/health`, thresholds, Docker/Kubernetes/Compose probes. |
| [Daemonize workers](https://docs.prefect.io/v3/advanced/daemonize-processes) | systemd, dedicated user, long-lived serving process. |
| [Direct dynamic submission](https://docs.prefect.io/v3/advanced/submit-flows-directly-to-dynamic-infrastructure) | Provider decorators, bundle files, launchers, three execution modes. |
| [Scale self-hosted](https://docs.prefect.io/v3/advanced/self-hosted) | Postgres/Redis/Docket, API/service split, LB, migrations, SSL. |
| [Database maintenance](https://docs.prefect.io/v3/advanced/database-maintenance) | Bloat/connection monitoring, vacuum, retention, direct-SQL cautions. |
| [CI/CD](https://docs.prefect.io/v3/advanced/deploy-ci-cd) | GitHub Actions, official action, workspaces, build caching. |
| [Infrastructure as code](https://docs.prefect.io/v3/advanced/infrastructure-as-code) | Terraform, Pulumi bridge, modules, Helm charts. |
| [Server Helm](https://docs.prefect.io/v3/advanced/server-helm) | Server/worker chart install, basic auth, probes, troubleshooting. |
| [Security settings](https://docs.prefect.io/v3/advanced/security-settings) | Basic auth, CSRF, CORS, proxy/custom headers, precedence. |
| [Network access](https://docs.prefect.io/v3/advanced/configure-network-access) | Cloud/self-host egress, proxies, TLS/OCSP, PrivateLink. |
| [API client](https://docs.prefect.io/v3/advanced/api-client) | Async/sync client, filters, pagination, state/event methods. |
| [Base job templates](https://docs.prefect.io/v3/advanced/customize-base-job-templates) | Variables/job configuration interpolation and replacement behavior. |
| [Custom blocks](https://docs.prefect.io/v3/advanced/custom-blocks) | Custom Pydantic blocks, registration, migration caveats. |
| [Custom worker](https://docs.prefect.io/v3/advanced/developing-a-custom-worker) | Base worker/config/variables/result and entry point. |
| [Plugins](https://docs.prefect.io/v3/advanced/plugins) | Opt-in plugin hooks, trust model, diagnostics, env controls. |

## First-party companion sources

These were consulted only for integration context; prefer the linked Prefect
docs for behavior and version gates.

| Source | Contribution |
|---|---|
| [Prefect SDK reference](https://reference.prefect.io/prefect/client/) | Current client/API symbol lookup linked by docs. |
| [Prefect Helm](https://github.com/PrefectHQ/prefect-helm) | First-party server/worker chart context and probe issue links. |
| [Terraform provider](https://github.com/PrefectHQ/terraform-provider-prefect) | Provider status and issue/milestone context. |
| [Prefect deploy GitHub Action](https://github.com/PrefectHQ/actions-prefect-deploy) | Official CI/CD action used by the advanced guide. |
| [CI/CD example](https://github.com/prefecthq/cicd-example) | First-party workflow examples referenced by the CI/CD guide. |
| [Multi-workspace CI/CD example](https://github.com/prefecthq/cicd-example-workspaces) | Staging/production workspace pattern. |

## Notable official-doc conflicts

- The current concepts page says tag limits are backed by global limits in
  newer 3.x, while the how-to still shows legacy tag CLI/client calls.
- `GitRepository(url=...)` is supported by the API reference and current code;
  one versioning example uses `repo_url=`.
- Schedule APIs differ around `3.1.16` (`Interval`/`schedule` versus older
  `IntervalSchedule`/`schedules`).
- `DeploymentEventTrigger`, `pause_flow_run`, and lock-manager imports vary
  between pages. Prefer the current public import and test it against the
  installed package.
- Old `/v3/develop/*` and `/v3/deploy/infrastructure-concepts/*` links redirect
  to current how-to pages; use the canonical URLs above.
- Generated SDK and server-side default result storage are beta/moving APIs.
