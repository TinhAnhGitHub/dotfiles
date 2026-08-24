---
name: mongodb-pymongo
parent: mongodb
description: >-
  Use for Python applications that use PyMongo 4.x or BSON: MongoClient or AsyncMongoClient,
  Database and Collection APIs, CRUD, cursors, aggregation, transactions, change streams,
  BSON/Extended JSON/ObjectId/UUID/datetime handling, CodecOptions and custom codecs, indexes,
  Database.command(), Atlas Search APIs, driver monitoring, or Python logging. Invoke whenever
  implementing, reviewing, debugging, or migrating PyMongo or Motor code, even when the user
  only mentions a Python MongoDB client, `bson`, or `AsyncMongoClient`. For pool sizing and
  cross-driver connection tuning, also load `mongodb/connection`; for query-plan/index performance,
  load `mongodb/query-optimizer`; for Search or Vector Search solution design, load `mongodb/search-and-ai`.
license: Apache-2.0
metadata:
  version: "1.0.0"
  pymongo_docs_version: "4.17"
---

# PyMongo 4.17 Development Guide

Use the official PyMongo 4.17 documentation bundled in `references/` before producing
implementation advice. Prefer PyMongo's public APIs over private driver internals and state any
server, Atlas, or PyMongo version prerequisite next to the code that needs it.

## Route the request

| Request | Read first |
| --- | --- |
| Client construction, URI, TLS/auth, timeouts, client reuse, pools | `references/connect-and-lifecycle.md` |
| Database/collection setup, reads, writes, cursors, bulk work, aggregation, sessions | `references/crud-and-aggregation.md` |
| `bson`, `ObjectId`, `UUID`, dates, EJSON, `CodecOptions`, custom types | `references/bson-and-codecs.md` |
| Standard/Search indexes, `explain`, database commands | `references/indexes-search-and-commands.md` |
| Logging, listeners, change streams, sync/async choice or Motor migration | `references/observability-and-async.md` |
| Exact official source or a less common API module | `references/source-map.md` |

## Workflow

1. Identify the installed PyMongo version, deployment type (Atlas/self-managed), server version,
   and whether the call path is synchronous or asyncio. Do not mix sync and async snippets.
2. Inspect the existing client construction and collection schema before changing behavior. Reuse
   one long-lived client per process/application; do not create a client per request or reuse a
   client after `fork()`.
3. Pick the highest-level public API that expresses the operation (`find`, `aggregate`,
   `create_index`, `watch`) instead of `Database.command()` where possible.
4. Make bounded, observable code: use projections/limits or cursor iteration, attach a useful
   `comment` to diagnostics, and choose timeouts based on the workload. Never silently set random
   pool or timeout values.
5. Separate read-only guidance from mutation. Before code that drops data/indexes, changes index
   definitions, alters users/roles, or runs administrative commands, clearly label the impact and
   obtain explicit approval if execution is possible.
6. Include error handling appropriate to the operation and explain retry/idempotency assumptions.
   A transaction callback can be retried, so it must not perform irreversible external side effects.

## Sync and async rules

- Use `MongoClient` and normal `for` loops in synchronous code. Use `AsyncMongoClient`, `await`,
  and `async for` in asyncio applications. `AsyncCollection.find()` returns an `AsyncCursor`; it is
  not itself awaited.
- `AsyncMongoClient` is confined to one event loop and is not thread-safe. `MongoClient` is
  thread-safe, but neither client should be inherited by child processes.
- Motor is deprecated after **May 14, 2026**. For new asyncio work and Motor migrations, target
  PyMongo Async and read `references/observability-and-async.md`.

## Defaults and correctness guardrails

- Verify connectivity with `client.admin.command("ping")`; close clients during controlled
  application shutdown or a context-manager scope. Do not call `close()` from `__del__`.
- `mongodb+srv://` enables TLS by default. Do not recommend `tlsInsecure`, invalid certificates,
  or invalid hostnames outside a clearly marked local/test exception.
- Preserve BSON types: parse request IDs with `ObjectId`, use timezone-aware UTC datetimes, and
  choose `UuidRepresentation.STANDARD` for new cross-language data. Native `uuid.UUID` cannot be
  encoded under the default `UNSPECIFIED` representation.
- Avoid `list(cursor)` for unbounded data. Use a projection and iterate, call `to_list()` with a
  deliberate bound in async code, and close long-lived cursors/change streams.
- Prefer `count_documents()` for an accurate count and `estimated_document_count()` only when an
  approximate metadata count is acceptable. Do not use removed/deprecated cursor `count()` APIs.
- Put regular index design and query-plan analysis through `mongodb/query-optimizer`. Keep normal
  collection indexes distinct from Atlas Search/Vector Search indexes.

## Response expectations

For implementation/review answers, provide:

1. The sync or async assumption and relevant compatibility requirements.
2. A minimal, typed, public-API code sample with values left configurable where environment facts
   are unknown.
3. A short rationale for safety, type handling, timeouts, retry behavior, and resource cleanup.
4. A concise validation step (`ping`, test data, a bounded query, or `explain`) and the official
   source URL when behavior is version-sensitive.
