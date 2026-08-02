# Prefect 3 troubleshooting, limits, and safety

Use this reference before changing state, deleting data, rotating credentials,
or scaling self-hosted services. Verify the installed version with
`prefect version` and prefer the current official pages in
`references/source-ledger.md` over remembered Prefect 2.x behavior.

## First-response checklist

```bash
python --version
prefect version
prefect config view --show-defaults
prefect cloud workspace ls                 # Cloud only
prefect work-pool ls
```

Then identify the failing boundary:

1. **Client/control plane:** API URL, profile, workspace membership, API key,
   server/client compatibility, proxy/TLS.
2. **Scheduling:** deployment exists, schedule is active, parameters match,
   server scheduler/background services are running.
3. **Dispatch:** work-pool/queue name, worker heartbeat/role, pool concurrency,
   run state (`Scheduled`, `Late`, `Pending`, `AwaitingConcurrencySlot`).
4. **Infrastructure:** image/registry, pull steps, provider credentials,
   network/RBAC, job variables, architecture.
5. **Flow code:** imports/dependencies, parameter schema, retries, timeouts,
   result storage, logs, and side effects.

## Symptoms and fixes

| Symptom | Likely cause | Check/fix |
|---|---|---|
| Cloud `401 Invalid authentication credentials` | Wrong/expired key, URL, or profile | Check `PREFECT_API_URL`; use `/api/me/` with the key; log in again without printing it. |
| Cloud `404` for a workspace | Caller is not a member or account/workspace IDs are wrong | `prefect cloud workspace ls`; use the account/workspace form required by the current page. |
| Run stays `Scheduled` then `Late` | No healthy worker subscribed to the pool/queue | Start the worker, check `PREFECT_API_URL`, pool type, queue, role, and heartbeat. |
| Worker health is `503` | Flag missing, stale poll, API latency/auth, port/firewall | Start with `--with-healthcheck`; inspect `PREFECT_WORKER_QUERY_SECONDS`, logs, and `:8080/health`. |
| Health is `200` but runs do not execute | Health proves polling only | Check deployment pool/queue, concurrency slots, image pull, and provider job logs. |
| Docker run cannot import project code | Wrong image/pull step or generated build omitted `pyproject.toml` deps | Use a custom Dockerfile/pinned image or explicit pull/install step. |
| Kubernetes `403` creating jobs/pods | Role/RoleBinding/service-account mismatch | `kubectl auth can-i ...`; inspect namespace, worker values, and pod logs. |
| Cloud Run image fails immediately | Unsupported `linux/arm64` image | Build/publish `linux/amd64` for the documented serverless target. |
| Empty logs | Flow never started, logging context missing, or remote settings differ | Check worker/infrastructure logs; use `get_run_logger()` in a run and `log_prints=True`. |
| `MissingContextError` | Run logger used outside a flow/task context | Use `get_logger()` for ordinary code, `with_context`/`copy_context` for propagated run context. |
| Cache never hits | Results not persisted, unstable key, expired cache, different run ID, or inaccessible storage | Set `persist_result=True`, choose a policy/key, inspect storage/lock manager, and test one process first. |
| Cache duplicates in parallel | `READ_COMMITTED` permits concurrent same-key work | Use `SERIALIZABLE` and a shared lock manager, or make the task idempotent. |
| Local result disappears after retry | New Docker/Kubernetes infrastructure has a different filesystem | Use remote result storage or a shared persistent volume. |
| Flow parameter validation fails | Type/schema mismatch or >512 KB payload | Pass correct keyword parameters; use a Pydantic model; put large data in external storage. |
| Self-hosted basic auth returns `401` | `PREFECT_API_KEY` overrides basic-auth settings | Unset the API-key environment/profile; set matching server/client auth strings. |
| Self-hosted replicas duplicate schedules/actions | Memory Docket or in-process services | Use Postgres/Redis, a Redis Docket URL, `--no-services` API replicas, and separate service workers. |
| `prefect server start --workers N` exits | Multi-worker requirements are not configured | Use Postgres and Redis-backed messaging/cache/ordering/lease storage. |
| Helm `CreateContainerConfigError` | Missing auth Secret/config | Inspect `kubectl events` and rendered values. |
| Helm `ConnectError: Name or service not known` | Wrong internal API URL | `helm template`; use the service DNS name plus `/api`. |
| Webhook fires but no event | Invalid template/body/auth or Cloud endpoint issue | Inspect `prefect-cloud.webhook.failed` and the Event Feed; validate `body`/`headers` template access. |
| Database grows despite retention | Vacuum service disabled/not running or long transactions | Inspect vacuum settings/logs, event retention, autovacuum, bloat, and transaction age. Back up before deletion. |

## Failure semantics to explain explicitly

- A cancellation request should set `CANCELLING`; infrastructure is given a
  grace period and the backend later reaches `CANCELLED`. Do not force a
  running run directly to `CANCELLED` unless the administrative risk is
  understood. Independent cancellation needs a deployment/monitoring worker;
  nested child runs cannot be independently cancelled from an inline parent.
- State hooks execute client-side and are not durable. Use Automations for
  reliable notifications, cleanup, or cross-deployment actions.
- `on_failure` runs after retries are exhausted, while `on_running` may run for
  every retry attempt. A retry may repeat external side effects; use
  idempotency keys or transaction rollback compensation.
- A timed-out synchronous task may continue blocking until the underlying
  blocking operation returns. Use a native network timeout or process/async
  boundary.
- A tag limit of zero aborts matching tasks; a multi-tag task needs capacity in
  every tag. Tag limits are backed by global limits named `tag:<tag>` in newer
  Prefect 3 releases, while older docs show a legacy tag CLI/client API.
- A flow returning a future must resolve it or return a supported future/state;
  otherwise work can be left unfinished. A thread-pool task that waits on a
  child task can deadlock when no worker is free.
- A `rate_limit` call needs a global limit configured with slot decay. Global
  concurrency leases expire/renew; strict mode determines whether renewal
  failure stops work.

## Security, privacy, permissions, and cost

### Credentials and data

- Variables are not encrypted. Use Secret blocks, integration credential
  blocks, workload identity, or an external secret manager.
- Keep API keys out of source, generated SDKs, Docker layers, `prefect.yaml`,
  systemd unit files, logs, artifacts, event payloads, and task parameters.
- Result storage commonly uses pickle/cloudpickle. Read only from trusted
  storage and pin compatible serializer dependencies; manual file reads bypass
  expiration and lock checks.
- Direct dynamic-infrastructure bundles do not automatically exclude `.env`,
  keys, or credentials. Maintain a reviewed `.prefectignore`.
- Treat event payloads, form inputs, webhook fields, Jinja variables, and
  `ImportString` paths as untrusted. Validate and constrain them before shell,
  SQL, filesystem, import, or network use.
- Do not log PII/secrets. Logging markup can interpret square brackets and
  produce misleading output; custom handlers/settings must be installed in
  the remote execution environment, not only on the deploy machine.

### Permissions and networking

- Cloud workers need the Worker role; workspace roles govern deployments,
  blocks, automations, and workspaces. Use service accounts for CI and rotate
  expiring keys.
- Kubernetes workers need only the required job/pod/log/secret permissions.
  Provider push pools may request broad IAM permissions during provisioning;
  review and reduce them afterward.
- Self-hosted Server and Compose have no auth by default. Add basic auth,
  CSRF/CORS controls, TLS/reverse-proxy validation, firewall rules, and private
  network access before exposure.
- Cloud egress normally needs `api.prefect.cloud`, `app.prefect.cloud`, and
  `auth.workos.com` on TCP 443; use FQDN rules because service IPs change.
  Disable optional telemetry only with the documented settings.

### Cost and retention

- Managed and push pools have run-duration/compute limits; Cloud workspaces
  and automation actions can be plan-limited. Modal/Coiled/provider compute is
  billed separately according to the provider page.
- Build once and deploy multiple flows/images when possible; avoid installing
  unpinned packages at every run.
- Configure event/flow-run retention and the database vacuum service only with
  a recovery/backup plan. Deletion is permanent and direct SQL can leave
  orphaned logs/artifacts.

## Version and documentation caveats

- These references target the `/v3/` documentation and Prefect 3.x. Check
  release notes before using a feature with an explicit gate.
- Self-hosted client/server skew can produce 422 errors; upgrade the older side
  deliberately rather than guessing.
- Schedule APIs changed around Prefect 3.1.16; match the installed API.
- Assets, deployment version history, metric triggers, some notification
  actions, webhooks, and Push/Managed pools have Cloud-only or plan-specific
  scope in the current docs.
- `prefect sdk generate` and server-side default result storage are documented
  as beta/moving features. Mark them version-dependent in generated guidance.
- Integration decorators moved from `prefect_<provider>.experimental` to
  top-level package modules; old imports may warn and later disappear.
- `DeploymentEventTrigger`, interactive pause imports, lock-manager names, and
  `GitRepository` keyword spelling have inconsistent examples in official
  pages. Prefer the current page's public import and run a tiny import check:

  ```bash
  python -c "from prefect import flow, task, get_client; print('Prefect imports OK')"
  ```

If a symbol cannot be verified, say so and link the exact page rather than
inventing a compatibility shim.
