# Chapter 11: Event-Driven Architecture: Using Events to Integrate Microservices

**Source**: *Architecture Patterns with Python* (Percival & Gregory, O'Reilly) — Part II: Event-Driven Architecture

## Core Idea
Publishing domain events over external message brokers (like Redis, RabbitMQ, or Kafka) enables asynchronous, temporally decoupled integration between microservices, preventing distributed balls of mud.

## Frameworks Introduced
- **External Event Integration Pattern**:
  - When to use: When multiple independent services need to react to changes without synchronous REST/gRPC coupling.
  - How:
    1. Distinguish between *Internal Domain Events* (private to the service) and *External Integration Events* (published to external brokers).
    2. An external publisher adapter serializes internal events to JSON and posts them to a message broker channel.
    3. An external listener process subscribes to broker channels and translates incoming messages into local Commands.
- **Temporal Decoupling**:
  - When to use: To ensure service availability even when external dependent services are offline.
  - How: Asynchronous message queuing allows Service A to complete its work and post an event without waiting for Service B to respond.

## Key Concepts
- **Distributed Ball of Mud**: A microservice architecture where services are tightly coupled via synchronous HTTP calls, cascading failures across the network.
- **Integration Event**: A publicly shared event schema designed for consumption by other services.
- **Internal vs External Events**: Internal events can change frequently with domain refactoring; external events represent public contracts and must be versioned carefully.
- **Idempotency**: The property that performing an operation multiple times produces the same result as performing it once, essential when brokers guarantee at-least-once delivery.

## Mental Models
- **Think of Microservices as Autonomous Post Offices**: Rather than calling each other on the phone and waiting on hold (synchronous HTTP), they send letters via postal carriers (message queues) and process mail when ready.
- **Internal Events Are Private Thoughts; Integration Events Are Press Releases**: Do not publish your internal domain thoughts directly; formulate a clean, intentional press release for external consumption.

## Anti-patterns
- **Synchronous Call Cascades**: Service A calls Service B over HTTP, which calls Service C, which calls Service D; any latency or failure brings down the entire chain.
- **Sharing Database Tables Across Services**: Letting multiple services query the same relational tables instead of communicating via events.
- **Publishing Internal Domain Entity State**: Dumping raw SQLAlchemy model dictionaries into message brokers, exposing internal implementation details.

## Code Examples

```python
import json
import redis
from adapters import repository
from service_layer import messagebus

r = redis.Redis(host="localhost", port=6379)

# External Publisher: Thin adapter around internal bus
def publish_external_event(event: Event):
    payload = json.dumps({
        "event_name": type(event).__name__,
        "data": event.__dict__
    })
    r.publish("allocation_events", payload)

# External Listener Process (Entrypoint)
def run_redis_subscriber():
    pubsub = r.pubsub()
    pubsub.subscribe("batch_events")
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            if data["event_name"] == "BatchCreated":
                cmd = commands.CreateBatch(
                    ref=data["data"]["ref"],
                    sku=data["data"]["sku"],
                    qty=data["data"]["qty"],
                    eta=data["data"].get("eta")
                )
                bus.handle(cmd)
```
- **What it demonstrates**: Redis publisher listening to internal domain events and external subscriber translating inbound broker messages into local commands.

## Reference Tables

| Characteristic | Synchronous RPC / REST | Asynchronous Event Broker |
|---|---|---|
| **Coupling** | Tight (network, endpoint, availability) | Loose (schema-only, temporally decoupled) |
| **Failure Mode** | Cascading failure if callee is down | Buffered in queue until consumer recovers |
| **Latency** | Sum of all downstream network calls | Immediate acknowledgement |
| **Consistency** | Strong / Immediate | Eventual Consistency |

## Worked Example
Preventing duplicate processing with idempotency keys:

```python
class IdempotentHandler:
    def __init__(self, uow, processed_repo):
        self.uow = uow
        self.processed_repo = processed_repo

    def handle(self, cmd: commands.CreateBatch):
        with self.uow:
            if self.processed_repo.has_seen(cmd.message_id):
                logger.info("Message %s already processed, skipping", cmd.message_id)
                return
            self.uow.batches.add(Batch(cmd.ref, cmd.sku, cmd.qty))
            self.processed_repo.record_seen(cmd.message_id)
            self.uow.commit()
```

## Key Takeaways
1. Temporal decoupling allows services to operate reliably even when collaborators are down.
2. Translate external messages into local commands before feeding them to your local message bus.
3. Keep integration event schemas distinct from internal domain events.
4. Design event handlers to be idempotent to safely handle duplicate message deliveries.

## Connects To
- **Ch 10**: Converting external events into internal commands.
- **Ch 12**: Using events to populate read models in CQRS.
- **Ch 24**: Strangler Fig pattern for migrating monoliths to microservices.
