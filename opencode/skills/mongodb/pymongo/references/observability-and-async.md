# Monitoring, logging, change streams, and PyMongo Async

## Driver telemetry and logging

- Register short, non-blocking `CommandListener`, `ServerListener`, and
  `ConnectionPoolListener` instances with `event_listeners=[...]`. Do not perform network I/O or
  log sensitive payloads in callbacks; command content can be redacted.
- Configure Python loggers such as `pymongo`, `pymongo.command`, `pymongo.connection`, and
  `pymongo.serverSelection`. `MONGODB_LOG_MAX_DOCUMENT_LENGTH` controls command-document
  truncation; raising it increases sensitive-data and cost exposure.

## Change streams

- Use `collection.watch()`, `database.watch()`, or `client.watch()` based on the required scope,
  and manage the stream with a context manager.
- Persist the complete event `_id` resume token only after successful processing. Choose exactly
  one of `resume_after`, `start_after`, and `start_at_operation_time`.
- Bound polling with `max_await_time_ms`, and choose `full_document`/pre-image options based on
  whether absence is acceptable. Pre/post-image behaviors and expanded DDL events have server
  version requirements (notably MongoDB 6.0+ for several options).

```python
with collection.watch(max_await_time_ms=1_000) as stream:
    for change in stream:
        process(change)
        save_resume_token(change["_id"])
```

## Async and Motor migration

- New asyncio code uses `AsyncMongoClient`; `await` network methods and consume cursors with
  `async for`. `find()` produces an `AsyncCursor` synchronously.
- Do not share `AsyncMongoClient` across threads or event loops. Do not use the unsupported
  `connect` keyword with it.
- Motor is deprecated after May 14, 2026. Migration generally changes import/client type, adds
  `await`, changes cursor iteration to `async for`, and removes Motor-only APIs such as `each()`.
  Verify every API against the async API reference—methods absent there may be synchronous.

## Sources

- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/monitoring-and-logging/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/monitoring-and-logging/monitoring/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/monitoring-and-logging/logging/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/monitoring-and-logging/change-streams/
- https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/
- https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/index.html
