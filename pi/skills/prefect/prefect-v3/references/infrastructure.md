# Prefect 3 infrastructure and operations

Use this reference when execution, networking, Cloud, self-hosting, or
operations are part of the request. Canonical sources include [work pools](https://docs.prefect.io/v3/concepts/work-pools), [workers](https://docs.prefect.io/v3/concepts/workers), [manage work pools](https://docs.prefect.io/v3/how-to-guides/deployment_infra/manage-work-pools), [deployment infrastructure](https://docs.prefect.io/v3/how-to-guides/deployment_infra), [Prefect Cloud](https://docs.prefect.io/v3/how-to-guides/cloud), [self-hosted](https://docs.prefect.io/v3/how-to-guides/self-hosted), and the [advanced infrastructure/platform pages](source-ledger.md).

## Work-pool taxonomy

| Type | Worker required | Typical use | Scope/caveat |
|---|---:|---|---|
| Process | Yes | Local subprocess isolation | Self-hosted/Cloud hybrid; worker host owns code/deps. |
| Docker | Yes | Reproducible per-run containers | Docker daemon and registry access required. |
| Kubernetes | Yes | Cluster-native jobs | Cluster, RBAC, image registry, and integration package required. |
| ECS/ACI/Cloud Run/Vertex | Usually yes for hybrid | Provider-native jobs | Provider credentials and integration package required. |
| Push pools (`ecs:push`, `cloud-run:push`, `modal:push`, etc.) | No | Cloud asks provider to provision each run | Prefect Cloud and provider/IAM setup; 24-hour run limit. |
| Prefect Managed | No | Prefect-hosted compute | Cloud-only; official image; 4 vCPU/16 GB/128 GB and 24-hour limit. |
| `serve()` | No worker | Long-lived static process | The serving process itself must stay available. |

Queues have priority and concurrency. Workers poll queues and heartbeat; three
missed heartbeats mark a worker offline. A run stuck `Scheduled → Late` usually
means that no subscribed worker is healthy or the pool/queue does not match.

Create and inspect pools with:

```bash
prefect work-pool create local-process --type process
prefect work-pool create local-docker --type docker
prefect work-pool ls
prefect work-pool inspect local-process
prefect work-pool set-concurrency-limit local-process 10
prefect worker start --pool local-process
```

Use the Cloud/Server API address and the worker's credentials in the worker
environment. Do not rely on runtime package installation for production
reproducibility; prebuild a pinned image instead.

## Local processes and static containers

For a local process pool, the worker creates a subprocess for each flow run.
For a static container, run a long-lived `serve()` process in a container:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY flow.py .
CMD ["python", "flow.py"]
```

```bash
docker build -t example-prefect-flow:latest .
docker run --rm --env-file .env example-prefect-flow:latest
```

`.env` should contain `PREFECT_API_URL` and a secret-injected
`PREFECT_API_KEY`. Enable the runner health server with `webserver=True` in
`serve()` or `PREFECT_RUNNER_SERVER_ENABLE=true`; the health endpoint is
normally `:8080/health`. Do not publish the health endpoint publicly without a
network policy.

## Docker work pools

```bash
prefect work-pool create image-pool --type docker
prefect worker start --pool image-pool --with-healthcheck
```

```python
from prefect import flow
from prefect.docker import DockerImage


@flow
def container_flow():
    print("runs in an isolated container")


if __name__ == "__main__":
    container_flow.deploy(
        name="container-production",
        work_pool_name="image-pool",
        image=DockerImage(name="registry.example/prefect-flow:1.0.0"),
        push=True,
        build=True,
    )
```

The generated Docker path installs `requirements.txt`; it does not reliably
install a project `pyproject.toml` without the documented auto-install
conditions. Use a custom Dockerfile or a pinned image for project dependencies.
`image_pull_policy` controls whether each run fetches a new image. Keep image
digests immutable in production.

## Kubernetes

Kubernetes execution needs a cluster, a registry, service-account RBAC, and
`prefect-kubernetes`/`prefect-docker` versions compatible with the installed
Prefect. A minimal worker installation is:

```bash
helm repo add prefect https://prefecthq.github.io/prefect-helm
helm repo update
kubectl create namespace prefect
kubectl create secret generic prefect-api-key -n prefect \
  --from-literal=key="$PREFECT_API_KEY"
helm install prefect-worker prefect/prefect-worker -n prefect \
  --set worker.config.workPool=my-kubernetes-pool
```

The worker needs permissions to create/watch/delete jobs and read pod logs.
Diagnose RBAC with:

```bash
kubectl auth can-i create jobs \
  --as=system:serviceaccount:prefect:prefect-worker -n prefect
```

The base job template must reference every custom variable using
`{{ variable_name }}`. Replacing the template replaces the full default
template, so preserve required fields and validate the JSON before saving.

## Managed and serverless infrastructure

Managed pools require Prefect Cloud, an accessible source/image, and the
official Prefect image. They have documented vCPU/memory/storage/run-duration
and workspace compute limits. Push pools require provider credentials/roles;
`--provision-infra` can create provider resources but requests broad IAM
permissions. Review the generated plan and use least privilege.

```bash
prefect work-pool create managed --type prefect:managed
prefect work-pool create cloud-run --type cloud-run:push --provision-infra
```

Serverless images may need `platform="linux/amd64"`; Cloud Run fails on an
incompatible architecture. Modal is a Cloud push pool and Coiled provisions
VMs in the user's cloud account; provider billing, spin-up time, and data
residency differ. Read the provider page before promising cost or privacy.

## Direct submission to dynamic infrastructure

The current decorator paths are top-level integration modules; old
`prefect_<provider>.experimental` imports are deprecated:

```python
from prefect import flow
from prefect_kubernetes.decorators import kubernetes


@kubernetes(work_pool="k8s-pool", namespace="analytics")
@flow
def train(dataset: str) -> str:
    return f"trained on {dataset}"


if __name__ == "__main__":
    future = train.submit_to_work_pool("daily")
    print(future.result())
```

Direct call blocks and needs local infrastructure access; `.submit()` is
non-blocking but still needs local access; `.submit_to_work_pool()` needs a
running worker and does not need local cluster access. Configure work-pool
object storage for bundles. Parameters must be cloudpickle-serializable. Add a
`.prefectignore` for `.env*`, `*.pem`, `*.key`, and `credentials.*`; sensitive
files are not automatically excluded.

## Health checks and daemonization

```bash
prefect worker start --pool image-pool --with-healthcheck
curl http://localhost:8080/health
```

`200` means the worker recently polled successfully; `503` means it is stale.
The threshold is `PREFECT_WORKER_QUERY_SECONDS * 30` (default query interval
10 seconds, approximately 5 minutes). This does not prove that a flow ran.
Tune the query interval for API latency and restrict the health server's
network exposure.

On Linux, run workers or serving processes as a dedicated systemd user with
`Restart=always`, an explicit virtual-environment `ExecStart`, and credentials
configured for that user. On Windows, use the documented PowerShell/NSSM
pattern, firewall port 4200, and UTF-8 settings when necessary. Store no API
keys in unit files; use environment files or the host secret manager.

## Prefect Cloud

```bash
prefect cloud login --key "$PREFECT_API_KEY" \
  --workspace "account-id/workspace-id"
prefect cloud workspace set --workspace "account-name/workspace-name"
prefect config view
```

Cloud account/workspace roles govern access. CI should use a service-account
key with the smallest required scope, not a developer's browser key. Browser
login keys may expire; Cloud key material is shown only once. Webhooks are
Cloud endpoints that turn HTTP requests into events; validate Jinja templates,
rate-limit callers, and avoid putting secrets into event payloads.

For restricted egress, allow FQDNs (not fixed IPs) for `api.prefect.cloud`,
`app.prefect.cloud`, and `auth.workos.com` over TCP 443. Proxy variables
`HTTPS_PROXY`, `SSL_CERT_FILE`, and `NO_PROXY` apply to client networking.

## Local server, Docker, Compose, and Windows

Start local Server:

```bash
prefect server start
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

Docker:

```bash
docker run --rm -p 4200:4200 prefecthq/prefect:3-latest \
  prefect server start --host 0.0.0.0
```

The documented Docker Compose topology separates Prefect API, background
services, Postgres, Redis, and a worker. It has no authentication by default.
For Windows, the default shell is PowerShell and SQLite lives below
`%USERPROFILE%\.prefect`; configure `PREFECT_HOME`, firewall, PATH, and a
service manager deliberately.

For a single local server SQLite is convenient. Multi-server/high-availability
self-hosting requires Postgres `>=14.9`, Redis-backed messaging/ordering/lease
storage, a Redis Docket URL, a load balancer, and separate migrations. Redis
Cluster URLs are unsupported. Run API servers with `--no-services` and run
background services separately so scheduled/automation work is not duplicated.

## Helm and self-hosted security

```bash
helm repo add prefect https://prefecthq.github.io/prefect-helm
helm repo update
helm install prefect-server prefect/prefect-server -n prefect --create-namespace
```

The Helm server and worker charts have separate configuration. Enable basic
auth with a Kubernetes Secret and set the worker's self-hosted API URL. Use
`/api/health` for process liveness and `/api/ready` for database readiness.
Chart probe paths/timing vary by chart version; inspect rendered manifests.

Self-hosted basic auth uses `PREFECT_SERVER_API_AUTH_STRING` on the server and
`PREFECT_API_AUTH_STRING` on clients. If `PREFECT_API_KEY` is also set, the API
key wins and causes a confusing `401`; unset it. Enable CSRF for production,
configure CORS/reverse-proxy headers, TLS, and a private network. Do not use
the test-only `PREFECT_API_TLS_INSECURE_SKIP_VERIFY` in production.

## CI/CD, IaC, database maintenance

The deployment loop for CI/CD is:

1. checkout a commit;
2. install/pin Prefect and integrations;
3. authenticate with `PREFECT_API_URL`/`PREFECT_API_KEY` from CI secrets;
4. build/push an immutable image or update pull steps;
5. run `prefect deploy`/the official `PrefectHQ/actions-prefect-deploy@v4`;
6. verify deployment, schedule, work pool, and a canary run.

Use separate workspaces and storage prefixes for staging/production. The
Terraform provider is active development toward API parity; Pulumi can bridge
the provider (documented Pulumi `>=3.147.0`). Helm charts include server,
worker, and Prometheus exporter patterns. Treat provider/IAM state as code and
review plans before applying.

For Postgres, monitor table size/bloat/connections, keep autovacuum healthy,
and configure the Prefect vacuum service. Flow-run/event deletion is permanent;
back up first. `VACUUM FULL` takes an exclusive lock; prefer ordinary
`VACUUM ANALYZE` or `pg_repack` under a maintenance plan. Keep event retention
long enough for automations and debugging.
