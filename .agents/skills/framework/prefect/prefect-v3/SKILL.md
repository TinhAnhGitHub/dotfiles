---
name: prefect-v3
description: Use whenever a user asks to build, debug, test, deploy, schedule, operate, or extend a Prefect 3 workflow or platform integration. Covers @flow/@task, parameters, states, retries, caching, results, assets, artifacts, task runners, concurrency limits, logging, deployments, prefect.yaml, schedules, work pools, workers, Docker/Kubernetes/serverless/Modal/Coiled, Prefect Cloud, self-hosted Prefect Server, events, automations, webhooks, blocks, variables, settings, API clients, custom workers, plugins, CI/CD, IaC, Helm, and advanced interactive or transactional workflows. Prefer this skill for any Prefect or prefect.yaml request, and distinguish Prefect 3.x from legacy 2.x APIs.
compatibility: Python 3.10 or newer and Prefect 3.x. Optional integrations such as prefect-docker, prefect-kubernetes, prefect-aws, prefect-gcp, prefect-azure, prefect-redis, Modal, or Coiled are required only for their respective patterns.
---

# Prefect 3

Use this skill to produce implementation-ready Prefect guidance rather than a
catalog of concepts. Start with the smallest working flow, then add the
orchestration boundary (deployment/work pool/worker), and finally add
reliability and operational controls. Read only the reference file needed for
the requested topic; read `source-ledger.md` when citing or checking a moving
API.

## 1. Mandatory preflight

Before changing code or recommending commands, establish:

1. **Runtime and versions:** Python `>=3.10`, the installed Prefect version,
   and any integration versions. Run:

   ```bash
   python --version
   prefect version
   prefect config view --show-defaults
   ```

   Use `python -m pip install -U prefect` or `uv add prefect` only when an
   upgrade is intended. For a self-hosted API, keep the client no newer than
   the server; Prefect Cloud supports client versions broadly. Pin the exact
   version in production and re-check integration compatibility.

2. **Control plane:** choose Prefect Cloud or self-hosted Prefect Server. Cloud
   needs a workspace and API key; local development can use
   `prefect server start` and `PREFECT_API_URL=http://127.0.0.1:4200/api`.
   Never put an API key in source, YAML committed to Git, or a code block that
   looks like a real credential.

3. **Execution boundary:** decide whether the flow runs in the current
   process, a long-lived `serve()` process, a worker-backed work pool, a
   serverless push/managed pool, or direct dynamic infrastructure submission.
   This determines where code, dependencies, credentials, result storage, and
   logs must exist.

4. **Data and security:** identify parameter size, PII/secrets, result storage,
   network egress, IAM/RBAC, retention, concurrency, and whether external
   events are trusted. Flow parameters are limited to 512 KB by default; pass
   references to large data instead of embedding payloads.

## 2. Quick start: smallest successful implementation

Install Prefect in a virtual environment, connect to Cloud or a local server,
then save this as `flow.py` and run `python flow.py`:

```python
from prefect import flow, task


@task(retries=2, retry_delay_seconds=5, log_prints=True)
def greet(name: str) -> str:
    message = f"Hello, {name}!"
    print(message)
    return message


@flow(log_prints=True)
def hello_flow(name: str = "Prefect") -> str:
    return greet(name)


if __name__ == "__main__":
    print(hello_flow("Prefect 3"))
```

Expected result: a flow run and task run reach `Completed`, the message is
printed, and logs are available in the configured backend. Use `prefect cloud
login` for Cloud or `prefect server start` for a local API before relying on
the UI/API. For a first local deployment, prefer `hello_flow.serve(name=...)`;
for reproducible worker-backed execution, create a work pool and use
`hello_flow.deploy(...)` or `prefect deploy`.

## 3. Mental model and end-to-end loop

Use this model when explaining or designing a system:

1. A **flow** composes work and is the deployment/parameter boundary.
2. A **task** is a retryable, cacheable, observable unit. Direct calls block;
   `.submit()` and `.map()` create futures through a task runner; `.delay()`
   sends a background task to a task worker.
3. A **flow run** or **task run** is the orchestrated execution instance. Runs
   move through typed states such as `Scheduled`, `Pending`, `Running`,
   `Retrying`, `Completed`, `Failed`, `Crashed`, `Cancelled`, and `Cached`.
4. The backend creates/schedules runs; a `serve()` process or worker picks them
   up; infrastructure executes code; states, logs, results, artifacts, assets,
   and events provide feedback.
5. The operational loop is **define → test locally → deploy code and
   dependencies → schedule/trigger → execute → observe state/logs/results →
   retry or compensate → retain/delete data**. Automate build, deploy,
   schedule validation, health checks, and safe retries; keep approval of
   credentials, IAM, destructive retention, and production traffic explicit.

### Execution decision table

| Need | Prefer | Important boundary |
|---|---|---|
| One command or notebook-like local run | `flow()` | No independent worker; local process owns context. |
| Laptop or one long-lived process with schedules | `flow.serve()` | The process must stay alive; code/deps are local. |
| Isolated per-run process | Process work pool + worker | Worker must poll the correct pool/queue. |
| Reproducible dependencies | Docker work pool or image | Build/push/pull and registry credentials are yours. |
| Kubernetes-native execution | Kubernetes pool/worker or Helm | Cluster/RBAC/image access are prerequisites. |
| No worker with provider-managed startup | Cloud push/Managed pool | Cloud/provider permissions, 24-hour run limits, and plan quotas apply. |
| Data stays near an existing cluster | Direct `.submit()` or `.submit_to_work_pool()` | Parameters must be cloudpickle-serializable; exclude secrets from bundles. |
| Strictly controlled control plane | Self-hosted Server | You own auth, Postgres/Redis, backups, upgrades, retention, and TLS. |

For details, read `references/infrastructure.md`.

## 4. Canonical API contract

Use these shapes as the stable conceptual contract, then verify exact keyword
names against the linked v3 source pages:

```python
from prefect import flow, task
from prefect.deployments import run_deployment


@task(
    retries=3,
    retry_delay_seconds=10.0,
    persist_result=True,
    tags=["database"],
)
def extract(customer_id: int) -> dict:
    return {"customer_id": customer_id, "status": "ok"}


@flow(name="customer-pipeline", validate_parameters=True)
def pipeline(customer_id: int = 1) -> dict:
    return extract(customer_id)


# From a control script or another flow; use as_subflow=False inside a flow
# when the deployment must be an independent run.
flow_run = run_deployment(
    name="customer-pipeline/production",
    parameters={"customer_id": 42},
    timeout=300,
    as_subflow=False,
)
```

The important data shapes are: parameters are JSON-compatible values validated
against the flow schema; a `PrefectFuture` resolves to a task result/state; a
`State` has a type/name/message and optional result; a deployment binds an
entrypoint to schedules, triggers, a work pool, parameters, and job variables;
an event has an event name, resource, related resources, timestamp, and
payload. Keep large or sensitive values in external storage/blocks and pass
references.

## 5. Topic routing

| Request | Read |
|---|---|
| Flows, tasks, parameters, states, retries, hooks, logging, runtime context, task runners, concurrency, caching, results, assets, artifacts, testing, transactions, cancellation, interactive workflows, forms, background tasks | `references/workflows.md` |
| Deployments, `serve`/`deploy`, schedules, `prefect.yaml`, code storage, versions, job variables, variables, blocks, settings, events, automations, webhooks, payload templates | `references/deployments.md` |
| Work pools/workers, local processes, Docker, static containers, Managed, serverless, Kubernetes, Modal, Coiled, Cloud, self-hosted, Windows, health checks, daemonization, CI/CD, IaC, Helm, scaling, database/network/security | `references/infrastructure.md` |
| API client, pagination, REST, base job templates, custom blocks, custom worker, plugin, generated SDK | `references/api-patterns.md` |
| Failure diagnosis, version gates, security/privacy, permissions, cost, operational limits | `references/troubleshooting.md` |
| Citation or exact page discovery | `references/source-ledger.md` |

## 6. Reliability and safety rules

- Prefer typed flow parameters and Pydantic models. Validate external event
  payloads and never interpolate untrusted values into shell commands, paths,
  SQL, or import strings.
- Treat retries as safe only for idempotent work. Use transactions and
  `on_rollback` for compensating side effects; use state hooks for local,
  best-effort reactions and Automations for durable reactions.
- Caching requires result persistence. Choose a cache policy and shared,
  trusted storage/lock manager deliberately; do not deserialize untrusted
  pickle/cloudpickle results.
- Do not assume local files survive a Docker/Kubernetes retry. Use remote result
  storage or a shared volume and pin serializers/dependencies.
- Use Secret blocks or an external secret manager for credentials. Variables
  are not encrypted. Self-hosted Server and Docker Compose have no auth by
  default, so add basic auth/TLS/network controls before exposure.
- Worker health only proves polling, not successful execution. Diagnose pool,
  queue, permissions, image, pull steps, and concurrency separately.
- Mark Cloud-only, beta, experimental, and version-dependent behavior clearly.
  The current docs flag Cloud assets, Cloud deployment version history, metric
  triggers, Push/Managed pools, generated SDKs, and server-side default result
  storage as moving or scope-limited features.

## 7. Fast troubleshooting

| Symptom | First checks |
|---|---|
| `401` or `404` from Cloud | `PREFECT_API_URL`, API key/workspace, membership, and key role; call `/api/me/`. |
| Run is `Scheduled`/`Late` | Work pool/queue name, worker process, worker role, worker heartbeat, and queue concurrency. |
| Cache never hits | `persist_result=True` or the persistence setting, stable cache policy/key, shared storage, and expiration. |
| Logs are missing | `get_run_logger()` inside a run, `log_prints=True`, remote logging settings, and whether infrastructure failed before startup. |
| Worker health is 503 | `--with-healthcheck`, port/firewall, API latency/auth, and `PREFECT_WORKER_QUERY_SECONDS`. |
| Self-hosted replicas duplicate work | Postgres >=14.9, Redis-backed messaging/leases/ordering, a Redis Docket URL, separate migrations, and a load balancer. |
| Kubernetes `403` | Service account Role/RoleBinding and `kubectl auth can-i`; verify namespace and image pull credentials. |
| Self-hosted basic auth gives `401` | Unset `PREFECT_API_KEY` when using `PREFECT_API_AUTH_STRING`. |

Read `references/troubleshooting.md` before suggesting destructive database,
retention, cancellation, or credential changes.

## Official documentation

The skill is based on the Prefect v3 documentation roots:

- <https://docs.prefect.io/v3/get-started>
- <https://docs.prefect.io/v3/concepts>
- <https://docs.prefect.io/v3/how-to-guides>
- <https://docs.prefect.io/v3/advanced>
- <https://docs.prefect.io/v3/release-notes/versioning>

Use only official `docs.prefect.io` pages or the first-party references listed
in `references/source-ledger.md` for rapidly changing Prefect APIs. Do not
invent an API when a page is unverified; provide the verification URL and a
version check instead.
