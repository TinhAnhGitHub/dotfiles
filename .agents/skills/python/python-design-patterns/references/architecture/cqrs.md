# CQRS (Command Query Responsibility Segregation)

## Intent

Separate operations that change state (commands) from operations that read state (queries). The
read model may be a projection optimized for a screen or search shape, while the write model stays
the source of truth for invariants.

## Use when

Use CQRS when:

- writes and reads have different scaling, indexing, or consistency needs;
- a dashboard needs a denormalized shape that is expensive to assemble from the write model;
- commands need strict validation and auditability while queries need fast filtering; or
- asynchronous projections, replay, or independent read deployments are already required.

## Why

CQRS keeps a write contract from becoming a universal read DTO. Command handlers can enforce
invariants and emit a projection update; query handlers can return a purpose-built view without
leaking write-side fields. The separation also makes it explicit where eventual consistency and
projection failures live.

CQRS does not require event sourcing, two databases, or a message broker. A pair of functions and
two repositories is enough to start.

## Example

Give each side a small protocol and keep the command and query shapes distinct:

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CreateTicket:
    customer_id: str
    subject: str
    message: str


@dataclass(frozen=True)
class TicketSummary:
    ticket_id: str
    subject: str
    status: str
    preview: str


class TicketWriter(Protocol):
    def create(self, command: CreateTicket) -> str: ...


class TicketReader(Protocol):
    def list_summaries(self, *, status: str | None = None) -> list[TicketSummary]: ...


def create_ticket(command: CreateTicket, writer: TicketWriter) -> str:
    if not command.subject.strip() or not command.message.strip():
        raise ValueError("subject and message are required")
    return writer.create(command)


def list_tickets(reader: TicketReader, *, status: str | None = None) -> list[TicketSummary]:
    return reader.list_summaries(status=status)
```

The writer owns the source-of-truth mutation. A projector can derive `TicketSummary` after the
command commits; a query never has to load the full message or reconstruct the preview. Start with
one process and synchronous projection when that is enough, then move the projector behind a queue
only when the scaling or latency pressure is real.

## When not to use

Keep ordinary CRUD when reads and writes have the same shape, the dataset is small, and immediate
consistency matters more than independent scaling. Do not split repositories merely to rename
methods. Do not add a broker or event store before a concrete projection, throughput, or replay
requirement exists.

## Trade-offs

Separate models and handlers add code and create a synchronization boundary. Asynchronous
projections introduce stale reads, retries, duplicate delivery, and rebuild procedures. A read
model can drift from the source of truth if projection failures are not observable. The benefit is
independent query indexing and a write side that can protect invariants without serving every UI
shape.

## Tests

Test command validation and write-side invariants independently from query formatting. Test a
projector with the same source record twice to verify idempotency. Test that a failed projection is
retryable and observable, and document the read-after-write consistency guarantee. Contract-test
each query adapter against the `TicketReader` protocol.

## ArjanCodes 2026 example (adapted)

The [2026 `cqrs` example](https://github.com/ArjanCodes/examples/tree/main/2026/cqrs) separates
FastAPI command DTOs and handlers from a `ticket_commands` source-of-truth collection and a
`ticket_reads` projection. Its read model stores `preview` and `has_note` so list queries do not
load or interpret the full write document. The direct example above preserves that shape while
remaining standard-library-only.

## Framework examples

### MLflow — tracking writes and search reads (adapted)

MLflow Tracking exposes a write-oriented API for recording a run and a client API for querying
recorded runs. Keeping these behind separate application ports prevents training code from
depending on dashboard query details:

```python
import mlflow
from mlflow.tracking import MlflowClient


def record_training(learning_rate: float, validation_loss: float) -> str:
    with mlflow.start_run() as run:
        mlflow.log_param("learning_rate", learning_rate)
        mlflow.log_metric("validation_loss", validation_loss)
        return run.info.run_id


def best_run(experiment_id: str):
    client = MlflowClient()
    return client.search_runs(
        [experiment_id], order_by=["metrics.validation_loss ASC"], max_results=1
    )[0]
```

This is a CQRS-shaped application boundary: `record_training()` is a command, while
`best_run()` is a query with a read-optimized result. It does not imply that MLflow internally
implements CQRS. See the official [MLflow Tracking documentation](https://mlflow.org/docs/latest/ml/tracking/).
