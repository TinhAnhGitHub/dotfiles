# Prefect 3 workflow patterns

Use this reference for flow/task implementation. Source pages: [Flows](https://docs.prefect.io/v3/concepts/flows), [Tasks](https://docs.prefect.io/v3/concepts/tasks), [States](https://docs.prefect.io/v3/concepts/states), [Task runners](https://docs.prefect.io/v3/concepts/task-runners), [Caching](https://docs.prefect.io/v3/concepts/caching), and the workflow how-to pages listed in the [source ledger](source-ledger.md).

## Flows, tasks, and inputs

`@flow` defines a composition and run boundary. `@task` adds task-level
retries, caching, concurrency, logging, and state. A flow can call a task
directly, submit it to the task runner, or delay it to a task worker.

```python
from pydantic import BaseModel
from prefect import flow, task


class Customer(BaseModel):
    customer_id: int
    email: str


@task
def normalize(customer: Customer) -> str:
    return customer.email.strip().lower()


@flow(name="normalize-customer")
def normalize_customer(customer: Customer) -> str:
    return normalize(customer)


if __name__ == "__main__":
    # Pydantic validation/coercion happens at the flow boundary.
    assert normalize_customer({"customer_id": "7", "email": " A@EXAMPLE.COM "}) == "a@example.com"
```

Use `validate_parameters=False` only when the caller performs equivalent
validation. Flow-run parameters are 512 KB by default; pass an object-store
URI or database key for large data. API-created runs require keyword
parameters. Avoid returning unbounded generators: Prefect may consume a
returned generator to serialize it.

### Task invocation modes

| Call | Use | Result |
|---|---|---|
| `task(x)` | Simple sequential work | The task result; blocks. |
| `task.submit(x)` | Concurrent work in this flow | `PrefectFuture`; call `.result()`/`.wait()` or return it. |
| `task.delay(x)` | Fire-and-forget background task | A future tracked by a task worker; start `task.serve()` first. |
| `task.map(values)` | One task run per value | Collection of futures/states; use `wait` or `.result()`. |

Future arguments are automatically resolved and create data dependencies. Use
`wait_for=[future]` for ordering without passing a value; use `unmapped(value)`
for a map argument that should remain constant. `quote`/`opaque` annotations
opt out of normal future resolution; only use them with already-resolved,
deliberately opaque values.

## Concurrency and task runners

```python
import time
from prefect import flow, task
from prefect.futures import wait


@task
def fetch(item: int) -> int:
    time.sleep(0.1)
    return item * 2


@flow
def concurrent_flow() -> list[int]:
    futures = [fetch.submit(item) for item in range(4)]
    done, not_done = wait(futures)
    assert not not_done
    return [future.result() for future in done]


if __name__ == "__main__":
    assert sorted(concurrent_flow()) == [0, 2, 4, 6]
```

`ThreadPoolTaskRunner` is the default. Use `ProcessPoolTaskRunner` for
CPU-bound or interruptible isolation, and install the relevant extras for
`DaskTaskRunner` or `RayTaskRunner`. Threads require thread-safe code; process,
Dask, and Ray runners require picklable inputs/functions. Do not submit child
tasks from a bounded worker task and immediately call `.result()` unless the
pool has capacity; this can deadlock. Configure an adequate `max_workers` or
restructure the graph.

For async work, use `async def` tasks and `asyncio.gather` where appropriate.
Synchronous timeouts cannot interrupt blocking I/O in a thread; use a native
client timeout, async cancellation points, or a process boundary.

## States, retries, and manual recovery

States are typed orchestration records, not just strings. Common states are
`Scheduled`, `Pending`, `Running`, `AwaitingRetry`, `Retrying`, `Completed`,
`Cached`, `Failed`, `Crashed`, `Cancelled`, and `TimedOut`. Use state helpers
such as `state.is_completed()` rather than comparing display names. A flow may
return a custom named terminal state when a run is intentionally skipped:

```python
from prefect import flow
from prefect.states import Completed


@flow
def maybe_work(do_work: bool):
    if not do_work:
        return Completed(name="Skipped", message="No work was requested")
    return "work completed"
```

Configure automatic retries on the smallest safe unit:

```python
import httpx
from prefect import task
from prefect.tasks import exponential_backoff


def retry_http(task, task_run, state) -> bool:
    try:
        state.result()
    except httpx.HTTPStatusError as exc:
        return exc.response.status_code not in {401, 404}
    except httpx.ConnectError:
        return True
    except Exception:
        return True


@task(
    retries=4,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    retry_condition_fn=retry_http,
)
def call_api(url: str) -> dict:
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

Use `retry_jitter_factor` for thundering-herd control and global defaults only
when they are safe for every task. Retries must be idempotent or guarded by an
idempotency key. To retry an existing run, use:

```bash
prefect flow-run retry <flow-run-name-or-id>
```

The original run ID and parameters are retained and `run_count` increases.
Deployment runs return to `Scheduled`; local runs need an `--entrypoint`.

## Logging, runtime context, metadata, and hooks

```python
from prefect import flow, task, runtime
from prefect.logging import get_run_logger


@task(log_prints=True)
def report() -> str:
    logger = get_run_logger()
    logger.info("task=%s", runtime.task_run.name)
    return "ok"


@flow(log_prints=True, flow_run_name="customer-{customer_id}")
def observable_flow(customer_id: int = 1) -> str:
    logger = get_run_logger()
    logger.info("flow=%s deployment=%s", runtime.flow_run.name, runtime.deployment.name)
    return report()
```

`prefect.runtime` attributes are `None` outside a run and do not raise. Use
`get_run_logger()` inside a run; `get_logger()` is a normal logger and is not
sent to the Prefect API. In manually created subprocesses/threads, propagate
Prefect context (`with_context` for subprocesses or `copy_context()` for
threads) or use a plain logger. Inspect persisted logs with:

```bash
prefect flow-run logs <flow-run-id>
```

State hooks are client-side and best-effort. `on_completion` and `on_failure`
apply to flows/tasks; `on_cancellation` and `on_crashed` are flow hooks;
`on_running` applies to both. `on_failure` runs after retries are exhausted and
`on_running` runs for each attempt. Hooks are synchronous, so do not put slow
or durable notification work in them; use an Automation for a durable
reaction. In a hook, use `flow_run_logger` or `task_run_logger`, not
`get_run_logger()`, because the run context is not installed there.

Advanced logging can be configured without changing flow code. For example,
set `PREFECT_LOGGING_LOGGERS_PREFECT_FLOW_RUNS_LEVEL=ERROR`,
`PREFECT_LOGGING_EXTRA_LOGGERS=dask,scipy`, or point
`PREFECT_LOGGING_CONFIG_PATH` at a complete logging YAML in the execution
environment. Settings load where the flow runs; terminal colors/highlighters do
not change the persisted UI log. Avoid markup when untrusted strings can
contain square brackets.

## Global and tag-based concurrency limits

Use global limits for a shared external resource and tags for a simple task
category. A global limit can be created with the CLI and occupied in code:

```bash
prefect gcl create database --limit 5
prefect gcl inspect database
```

```python
from prefect import flow, task
from prefect.concurrency.sync import concurrency, rate_limit


@task(tags=["database", "analytics"])
def query(value: int) -> int:
    with concurrency("database", occupy=1, strict=True):
        return value * 2


@task
def call_rate_limited_service() -> None:
    # The global limit must have slot_decay_per_second configured.
    rate_limit("external-api")


@flow
def limited_flow() -> list[int]:
    return [query(i) for i in range(3)]
```

Create a legacy tag limit with `prefect concurrency-limit create database 10`
only when the installed version still exposes that API. Newer Prefect 3
versions back tags with global limits named `tag:database`; a task with two
tags needs a slot in both, and a zero limit aborts it. Async code should import
the asyncio concurrency context instead of the sync context. Leases renew in
the background; use strict mode when continuing without enforcement is unsafe.

## Caching, results, and transactions

Caching is disabled in practice unless the result is persisted. Start with a
simple input cache:

```python
from datetime import timedelta
from prefect import flow, task
from prefect.cache_policies import INPUTS


@task(
    persist_result=True,
    cache_policy=INPUTS,
    cache_expiration=timedelta(minutes=10),
)
def expensive_lookup(key: str) -> str:
    print("executing lookup")
    return key.upper()


@flow
def cached_flow() -> list[str]:
    return [expensive_lookup("a"), expensive_lookup("a")]


if __name__ == "__main__":
    assert cached_flow() == ["A", "A"]
```

The default policy combines inputs, task source, and the prevailing run ID.
Use `INPUTS`, `TASK_SOURCE`, `FLOW_PARAMETERS`, `RUN_ID`, `NO_CACHE`, policy
composition (`+`/`-`), `cache_key_fn`, `refresh_cache=True`, and an expiration
only after deciding the invalidation contract. For non-serializable inputs,
write a custom cache key function; for multiple machines use shared storage
and a distributed lock manager such as the `prefect-redis` integration.
`READ_COMMITTED` permits duplicate concurrent execution; `SERIALIZABLE` needs
a lock manager.

To customize cache behavior across machines, configure key storage and locking
explicitly (the lock manager/storage must be trusted and reachable by every
worker):

```python
from prefect import task
from prefect.cache_policies import INPUTS, TASK_SOURCE
from prefect.transactions import IsolationLevel
from prefect.locking.memory import MemoryLockManager


policy = (INPUTS + TASK_SOURCE).configure(
    isolation_level=IsolationLevel.SERIALIZABLE,
    lock_manager=MemoryLockManager(),  # one process only; use Redis for distributed work
)


@task(cache_policy=policy, persist_result=True)
def deterministic_step(value: str) -> str:
    return value.upper()
```

For a distributed lock use the documented `prefect-redis` integration and
shared result/key storage; `MemoryLockManager` is only for threads in one
process.

For durable results, set `persist_result=True` or configure result storage and
serializer explicitly. Local result storage does not survive a new Docker or
Kubernetes retry; use S3/GCS/Azure/another shared block or a shared volume.
Pickle/cloudpickle result deserialization must be restricted to trusted storage.

Transactions use `BEGIN → STAGE → ROLLBACK → COMMIT`. Use `transaction(key=...)`
for idempotency and `@task.on_rollback`/`@task.on_commit` to compensate external
side effects. `on_rollback` can fire because a different task in the same
transaction failed, so it is not a replacement for `on_failure`.

```python
import os
from prefect import flow, task
from prefect.transactions import transaction


@task
def write_file(path: str, contents: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(contents)


@write_file.on_rollback
def remove_file(transaction_state) -> None:
    path = transaction_state.get("path")
    if path and os.path.exists(path):
        os.remove(path)


@flow
def transactional_flow(path: str, contents: str) -> None:
    with transaction(key=path) as txn:
        txn.set("path", path)
        write_file(path, contents)
        # Add validation/other participating tasks here.
```

Use a real external idempotency key and test rollback after failures in a
different participating task. `SERIALIZABLE` transactions require a lock
manager; a filesystem lock is not a distributed lock.

## Assets and artifacts

Assets identify external data by a URI-like key. Assets are marked with
`@materialize`, can declare `asset_deps`, and may carry `AssetProperties` or
runtime metadata. Asset tracking is marked Cloud-only in the current docs.
Make one workflow authoritative for metadata because property updates are
complete overwrites.

```python
from prefect import flow
from prefect.assets import Asset, AssetProperties, materialize


report = Asset(
    key="s3://example-bucket/report.csv",
    properties=AssetProperties(name="Daily report", owners=["data-team"]),
)


@materialize(report)
def build_report() -> dict:
    rows = [{"id": 1}]
    report.add_metadata({"row_count": len(rows)})
    return {"rows": rows}


@flow
def report_flow():
    return build_report()
```

Artifacts are human-readable persisted outputs in the UI/API. Use Markdown,
table, link, image, or progress artifacts for reports—not as a secret store.
Image artifacts need a publicly accessible image URL; use a link artifact for a
private image.

```python
from prefect import flow
from prefect.artifacts import create_markdown_artifact, create_table_artifact


@flow
def publish_report() -> None:
    create_markdown_artifact(
        key="daily-report",
        markdown="# Daily report\n\nThe pipeline completed.",
        description="Human-readable status",
    )
    create_table_artifact(
        key="daily-rows",
        table=[{"customer_id": "42", "status": "ok"}],
    )


if __name__ == "__main__":
    publish_report()
```

Use a stable `key` to version an artifact and `update_progress_artifact` for
in-place progress. Inspect with `prefect artifact inspect <key>`; do not put
credentials or private image URLs into artifacts.

## Background and interactive workflows

For a fire-and-forget task worker:

```python
from prefect import task


@task(log_prints=True)
def add(a: int, b: int) -> int:
    print(a + b)
    return a + b


if __name__ == "__main__":
    add.serve()
```

From another process call `add.delay(1, 2)`. A task worker must be running;
`.delay()` is not a replacement for a durable deployment when the task needs a
full flow lifecycle. For web apps, the documented pattern is an API process
that calls `.delay()` and a worker that reads task state/results; use a shared
result volume locally or remote result storage in production.

Interactive flows use `pause_flow_run`, `suspend_flow_run`, `resume_flow_run`,
and `RunInput`. Treat user input as untrusted, validate it, and re-pause on
validation failure. Pausing/suspending keeps a run non-terminal, so set an
explicit timeout and recovery policy.

```python
from prefect import flow
from prefect.flow_runs import pause_flow_run
from prefect.input import RunInput


class Approval(RunInput):
    approved: bool
    comment: str = ""


@flow
async def approval_flow() -> str:
    answer = await pause_flow_run(
        wait_for_input=Approval.with_initial_data(
            approved=False,
            comment="Please review the run",
        )
    )
    if not answer.approved:
        return "not approved"
    return f"approved: {answer.comment}"
```

Custom validators run after resume, so catch `ValidationError` and re-pause if
the input needs correction. `receive_input`/`send_input` support interactive
messages without pausing, but sender and receiver types must match exactly.

### UI forms for deployment parameters

The UI can validate JSON-schema constraints before run submission, but it does
not execute Python validators. Express cross-field constraints in
`json_schema_extra` and keep importable paths stable when using `ImportString`:

```python
from typing import Literal
from pydantic import BaseModel, Field
from prefect import flow


class EmailContent(BaseModel):
    subject: str = Field(max_length=30, json_schema_extra={"position": 0})
    body: str
    attachments: list[str] = Field(default_factory=list, max_length=5)


@flow
def send_email(
    mailing_list: list[Literal["newsletter", "customers"]],
    content: EmailContent,
    test_mode: bool = False,
) -> str:
    return f"{len(mailing_list)} lists; test={test_mode}; subject={content.subject}"
```

Do not let users control arbitrary import paths or shell commands. Inspect the
generated `model_json_schema()` when a form renders incorrectly.

To cancel a deployment run, request a graceful transition rather than writing
the terminal state directly:

```bash
prefect flow-run cancel <flow-run-id>
```

Cancellation needs a deployment and monitoring worker. Infrastructure receives
a grace period; runs that remain `CANCELLING` are cleaned up by a server safety
net. Test cancellation for each worker/provider because unsupported
infrastructure may only mark the run cancelled without stopping the process.

## Testing

Use `.fn()` for fast task unit tests and `prefect_test_harness()` when testing
orchestration/state/API behavior:

```python
from prefect import flow
from prefect.testing.utilities import prefect_test_harness


@flow
def answer() -> int:
    return 42


def test_answer() -> None:
    with prefect_test_harness():
        assert answer() == 42
```

The harness uses a temporary SQLite API. Do not nest harnesses; use a
function-scoped harness for clean state, a sync session-scoped fixture for
async tests, and one isolated harness per xdist worker. Use `disable_run_logger`
when a direct `.fn()` test calls `get_run_logger()`. Increase
`server_startup_timeout` for slow CI and check ports 8000–9000 when startup
fails.
