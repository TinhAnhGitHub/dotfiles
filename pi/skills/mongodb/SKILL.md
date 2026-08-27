---
name: mongodb
description: >
  Unified MongoDB skill suite for Atlas, PyMongo, schema design, query optimization,
  Atlas Search / Vector Search / Hybrid Search, connection pooling, Stream Processing,
  MCP server, and natural-language querying. Use this parent skill whenever the user
  mentions MongoDB, Atlas, Atlas Search, Vector Search, PyMongo, Motor, BSON,
  ObjectId, mongosh, connection strings, schema design, indexing, query performance,
  or the MongoDB MCP server. Load this first, then load the narrowest sub-skill
  from the routing table below.
---

# MongoDB — Unified Skill Suite

Use this as the entry point for ALL MongoDB work. Identify which MongoDB concern
the request touches (driver code, schema, indexes, search, connections, streams,
or MCP tooling) and load the narrowest sub-skill alongside this one.

## Sub-skill routing

| Topic | Sub-skill | Load when |
|---|---|---|
| **MCP server setup & auth** | [`mcp-setup`](mcp-setup/SKILL.md) | User hasn't configured `MDB_MCP_*` env vars, needs connection string vs Atlas API service-account vs Atlas Local, or `mongodb-mcp-server` troubleshooting |
| **Natural-language querying (find/aggregate)** | [`natural-language-querying`](natural-language-querying/SKILL.md) | User asks "how do I query...", wants read-only `find` or aggregation pipelines generated from natural language, or SQL→MQL translation |
| **Atlas Search, Vector Search & Hybrid Search** | [`search-and-ai`](search-and-ai/SKILL.md) | Full-text `$search`, semantic `$vectorSearch`, hybrid search, autocomplete, fuzzy matching, RAG embeddings, or Atlas Search index / query design |
| **Query & index performance** | [`query-optimizer`](query-optimizer/SKILL.md) | "Why is this slow?", slow-query logs, `explain()` analysis, Performance Advisor, or index design for an existing query/workload |
| **Schema & data modeling** | [`schema-design`](schema-design/SKILL.md) | New schema, SQL→document migration, embed vs reference, 16MB limit, time series, schema validation, pattern selection, or Atlas Schema Suggestions |
| **Driver connection & pooling** | [`connection`](connection/SKILL.md) | `MongoClient`/`connect()` tuning, pool sizing, timeouts, serverless (Lambda) reuse, `maxPoolSize`/`minPoolSize`/`maxIdleTimeMS`, or connection errors (`ECONNREFUSED`, pool exhaustion, churn) |
| **PyMongo 4.x / BSON / Motor** | [`pymongo`](pymongo/SKILL.md) | Python `pymongo`/`AsyncMongoClient`/`Motor`, CRUD, cursors, bulk, aggregation, transactions, change streams, `bson`/`ObjectId`/`CodecOptions`, index helpers, or logging |
| **Atlas Stream Processing (ASP)** | [`atlas-stream-processing`](atlas-stream-processing/SKILL.md) | Atlas Streams workspaces, connections (Kafka/Cluster/S3/HTTPS/Lambda), processors/pipelines (`$source`→`$emit`/`$merge`), DLQ, PrivateLink, or processor diagnostics |

> Each sub-skill previously lived as a top-level `mongodb-*` skill. The content is
> unchanged — only the path moved under `mongodb/`. Old cross-references like
> `mongodb-connection` now mean `mongodb/connection`.

## How to choose

1. **MCP not configured?** → `mcp-setup` first. Most read/write & search/optimizer
   skills require the MongoDB MCP Server; without it they can only give shape-based advice.
2. **Writing a query from description?** → `natural-language-querying` (read-only).
   For search-flavored queries (`contains`, fuzzy, semantic, RAG) → `search-and-ai` instead.
3. **Query exists but is slow?** → `query-optimizer` (needs `explain()`/Performance Advisor).
4. **Designing the shape of documents?** → `schema-design`. Never fix performance
   with indexes alone if the schema is wrong.
5. **Touching connection code?** → `connection` (and `pymongo` if Python). Always
   gather deployment context before changing pool/timeout values.
6. **Python code?** → `pymongo` for API correctness; combine with `connection` for
   pool tuning and `query-optimizer` for index plans.
7. **Streaming / Kafka / S3 ingestion?** → `atlas-stream-processing` (requires Atlas API credentials).

## Shared operating rules

1. **Prefer MCP-verified advice** — when the MongoDB MCP Server is available, fetch
   `collection-schema`, `collection-indexes`, `find` samples, and `explain` before
   recommending queries, indexes, or schema changes. State assumptions when MCP is absent.
2. **Separate read vs write guidance** — label mutating/index-dropping/schema-changing
   operations and require explicit user approval before execution.
3. **Never fabricate credentials** — instruct the user to set `MDB_MCP_*` themselves
   (shell profile or `~/.codex/config.toml`); do not ask for or handle secrets.
4. **Context before configuration** — connection pools, timeouts, and index choices
   depend on deployment type, workload (OLTP vs OLAP), concurrency, and server tier.
   Ask one targeted question at a time when context is missing.
5. **Data accessed together, stored together** — prefer embedding for co-accessed data;
   reference only when arrays are unbounded, entities are independently accessed, or
   many-to-many.

## Documentation

- MongoDB Docs: https://www.mongodb.com/docs/
- PyMongo 4.x: https://pymongo.readthedocs.io/
- Atlas Search: https://www.mongodb.com/docs/atlas/atlas-search/
- Atlas Vector Search: https://www.mongodb.com/docs/atlas/atlas-vector-search/
- MCP Server: https://github.com/mongodb-js/mongodb-mcp-server

