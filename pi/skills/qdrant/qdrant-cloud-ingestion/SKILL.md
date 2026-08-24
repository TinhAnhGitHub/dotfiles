---
name: qdrant-cloud-ingestion
parent: qdrant
description: "Guides indexing and data ingestion into Qdrant Cloud (managed Qdrant). Use when someone says 'I have a Qdrant Cloud URL and API key', 'connect to cloud', 'ingest/upload data to Qdrant Cloud', 'bulk upload to cloud cluster', 'indexing on cloud', 'cloud is slow to ingest', 'migrate my data to Qdrant Cloud', 'which shards for cloud', or 'cloud strict mode'. Also use when creating collections, payload indexes, or running bulk/migration uploads against a cloud cluster (cluster URL ending in cloud.qdrant.io). Pair with qdrant-deployment-options for cluster selection and qdrant-indexing-performance-optimization when ingestion is slow."
---

# Ingesting and Indexing Data in Qdrant Cloud

Qdrant Cloud is managed Qdrant: you get a load-balanced cluster URL, an API key, and no raw config files. Everything here is tuned for that environment — API-key auth, cloud defaults (strict mode), managed scaling (resharding), and the ingestion patterns that actually saturate a cloud cluster.

## Connect to Your Cloud Cluster (URL + API key)

Use when: you have a cluster URL like `https://xyz-example.eu-central.aws.cloud.qdrant.io` and an API key.

- Python: `QdrantClient(url="https://<cluster-id>.<region>.<provider>.cloud.qdrant.io", api_key="<key>")` [Cloud quickstart](https://skills.qdrant.tech/md/documentation/cloud-quickstart/)
- TypeScript: `new QdrantClient({ url, apiKey })`; Go/Rust/.NET take `host`, `port: 6334`, `https: true`, `apiKey` [Authentication](https://skills.qdrant.tech/md/documentation/cloud/authentication/)
- REST API is port **6333**, gRPC is port **6334** (both HTTPS). gRPC gives the best ingestion throughput [Cluster access](https://skills.qdrant.tech/md/documentation/cloud/cluster-access/)
- The cluster endpoint load-balances across healthy nodes automatically; node-specific endpoints exist for monitoring (prepend `node-{num}-` to the URL)
- API keys are created on the Cluster Detail page and **shown only once**; use `eyJhb...` keys (v1.11+) for granular collection-level permissions
- Verify connectivity first: `client.get_collections()` or `curl https://<url>:6333 -H 'api-key: <key>'`
- Cloud Inference adds `cloud_inference=True` to embed with hosted models during ingestion [Cloud inference](https://skills.qdrant.tech/md/documentation/inference/cloud-inference/)

## Know the Cloud Defaults Before You Ingest

Use when: planning the collection schema or wondering why uploads/requests fail in cloud.

Cloud enables **strict mode** by default for new collections — uploads that filter on unindexed fields are **rejected**:

- `unindexed_filtering_retrieve: false` and `unindexed_filtering_update: false`: filtered writes/reads require a payload index on the filter field [Strict mode](https://skills.qdrant.tech/md/documentation/ops-configuration/administration/?s=strict-mode)
- `max_payload_index_count: 100` — at most 100 payload indexes per collection (v1.16+) [Configure cluster](https://skills.qdrant.tech/md/documentation/cloud/configure-cluster/)
- Max 1000 collections per cluster (more degrades performance)
- No raw `config.yaml` editing: optimizer threads, async scorer, strict mode, and replication defaults are configured via the Cloud Console "Configure" tab [Configuration](https://skills.qdrant.tech/md/documentation/cloud/configure-cluster/)
- Free clusters: 1 node, 1 GB RAM, 0.5 vCPU, 4 GB disk ≈ 1M vectors at 768 dims; auto-suspended after 1 week of inactivity [Create cluster](https://skills.qdrant.tech/md/documentation/cloud/create-cluster/)
- Watch cloud alerts (memory/disk >80%, throttling) during ingestion — they fire by email automatically [Cluster monitoring](https://skills.qdrant.tech/md/documentation/cloud/cluster-monitoring/)

## Design the Collection for Cloud Ingestion

Use when: creating a collection before the first big upload. The schema is the single biggest lever on ingestion speed.

- Create the collection with `shard_number` at **2x the node count** (e.g., 4 shards on a 2-node cluster); each shard gets an independent update worker [Distributed deployment](https://skills.qdrant.tech/md/documentation/scaling/distributed_deployment/?s=sharding)
- Set `replication_factor >= 2` for production; writes with `write_consistency_factor` 1 are cheaper during bulk load [Replication](https://skills.qdrant.tech/md/documentation/scaling/distributed_deployment/?s=replication)
- For large datasets use `on_disk=True` on the vector config (memmap) instead of relying on `memmap_threshold` — the optimizer converting segments during load becomes the bottleneck [Bulk upload](https://skills.qdrant.tech/md/documentation/manage-data/bulk-upload/)
- Consider `datatype="uint8"` or scalar/product/binary quantization at creation to shrink memory and speed up indexing [Quantization](https://skills.qdrant.tech/md/documentation/manage-data/quantization/)
- **Create payload indexes BEFORE uploading** — filter-aware HNSW edges are built during ingestion; late indexes require a costly HNSW rebuild [Indexing](https://skills.qdrant.tech/md/documentation/manage-data/indexing/?s=payload-index)
- Don't create more payload indexes than you filter on (cloud caps at 100, each extra index costs write + memory)
- Right-size `m` (16 default) and `ef_construct` (100-200) at creation — they are hard to justify increasing later [Vector index](https://skills.qdrant.tech/md/documentation/manage-data/indexing/?s=vector-index)
- Multi-tenant data: skip the global HNSW and use `payload_m` on a `tenant_id` keyword index — dramatically faster ingestion and no cross-tenant search [Multitenancy](https://skills.qdrant.tech/md/documentation/manage-data/multitenancy/)

## Bulk Ingest into the Cloud Cluster

Use when: uploading a large dataset (thousands to billions of points).

- Use `client.upload_collection()` (column-oriented) or `client.upload_points()` (record-oriented, generator-friendly) — they batch, parallelize, and retry for you [Points API](https://skills.qdrant.tech/md/documentation/manage-data/points/?s=upload-points)
- Batch size **64-256 points** per request; drop toward 64 if payloads are large (10 KB+) [Bulk upload](https://skills.qdrant.tech/md/documentation/manage-data/bulk-upload/)
- Run **2-4 parallel upload streams** (Python: `parallel=4`); one stream per shard is the sweet spot [Bulk upload](https://skills.qdrant.tech/md/documentation/manage-data/bulk-upload/)
- Use `max_retries=3` and consider `wait=False` on writes to avoid head-of-line blocking while the optimizer catches up [Points](https://skills.qdrant.tech/md/documentation/manage-data/points/)
- Prefer gRPC (port 6334) for throughput when the client supports it
- Provide deterministic IDs (your UUIDs/hashes) for idempotent re-runs; auto-generated UUIDs duplicate data on re-upload [Points](https://skills.qdrant.tech/md/documentation/manage-data/points/)
- Use `update_mode=insert_only`/`update_only` (v1.17+) for resume-safe pipelines [Points](https://skills.qdrant.tech/md/documentation/manage-data/points/)
- For very large loads, temporarily raise `optimizers_config.indexing_threshold` (default 20000 kB / 20 MB) so HNSW builds after the load, then restore it — the docs' example uses 10000; restore by setting it back [Collections](https://skills.qdrant.tech/md/documentation/manage-data/collections/?s=update-collection-parameters)
- Note: `update_collection` blocks until running optimizers finish — schedule the threshold change around the load, not mid-load
- During the unindexed window, search falls back to brute force — acceptable during load, not during serving

## Indexing on Cloud (After or During Ingestion)

Use when: watching the optimizer, worried about index build time, or tuning cloud indexing resources.

- HNSW is built lazily by the optimizer when a segment exceeds `indexing_threshold` (default 20000 kB) — `indexed_vectors_count` lower than `points_count` is expected, not a bug [Optimizer](https://skills.qdrant.tech/md/documentation/ops-optimization/optimizer/?s=indexing-optimizer)
- Check progress with `GET /collections/{name}` (optimizer_status, indexed_vectors_count) and `/collections/{name}/optimizers` (v1.17+); cluster-wide: `GET /cluster` [Optimization monitoring](https://skills.qdrant.tech/md/documentation/ops-optimization/optimizer/?s=optimization-monitoring)
- HNSW build is CPU-bound: on cloud, `optimizer_cpu_budget` (threads) is controlled from the Configure tab; AWS Standard clusters can add **GPU nodes for write-heavy/indexing workloads** [Configure cluster](https://skills.qdrant.tech/md/documentation/cloud/configure-cluster/)
- Never use HDD-class disks for indexing; cloud disk speed tiers: Balanced ≥ 32 GiB, Performance ≥ 256 GiB (AWS) [Create cluster](https://skills.qdrant.tech/md/documentation/cloud/create-cluster/)
- If a payload-index field produces too many unique values (long `text` fields), disable extra HNSW links for that index and rely on query-time strategies [Indexing](https://skills.qdrant.tech/md/documentation/manage-data/indexing/?s=disable-the-creation-of-extra-edges-for-payload-fields)
- Cloud **managed resharding** (v1.13+): change `shard_number` up or down without recreating the collection; only one resharding per collection at a time, slight performance dip during it [Resharding](https://skills.qdrant.tech/md/documentation/cloud/cluster-scaling/?s=resharding)
- Growing too big for the node? Vertical scaling (more RAM/CPU) needs headroom for existing data and a short downtime if replication factor = 1 [Cluster scaling](https://skills.qdrant.tech/md/documentation/cloud/cluster-scaling/)
- For continuous ingestion + search contention: reduce batch size, lower optimizer CPU budget (start at 50% vCPUs), cap `max_optimization_threads`, or scale out [Read-write contention](https://skills.qdrant.tech/md/documentation/ops-optimization/read-write-contention/)

## Migrate Data into Qdrant Cloud

Use when: moving existing collections (from another Qdrant or Pinecone, Weaviate, Milvus, pgvector, Elasticsearch, FAISS, etc.) into a cloud cluster.

- Use the official `qdrant-migration` tool: streams batches, auto-creates collections, **resumes interrupted migrations** (`_migration_offsets` tracking), works live [Migration tool](https://skills.qdrant.tech/md/documentation/migrate-to-qdrant/)
- Target URL must be **gRPC, port 6334**: `--qdrant.url 'https://xxx.cloud.qdrant.io:6334' --qdrant.api-key 'eyJhb...'` [Data migration tutorial](https://skills.qdrant.tech/md/documentation/tutorials-operations/migration/)
- Tune `--migration.batch-size` (default 50; 256-512 for large migrations), `--migration.restart` to ignore saved progress [Migration tool](https://skills.qdrant.tech/md/documentation/migrate-to-qdrant/)
- Verify after migration: point counts, indexed vectors, and search quality comparisons [Migration guidance](https://skills.qdrant.tech/md/documentation/migration-guidance/)
- Snapshot-based moves: collection snapshots work on cloud (single-node: cluster URL; multi-node: per-node URLs), restore to the same or a new cluster [Backups](https://skills.qdrant.tech/md/documentation/cloud/backups/)

## Embed While Ingesting (Cloud Inference)

Use when: you don't want to run embedding locally or in a separate service.

- Enable Cloud Inference (default on new clusters) and pass `cloud_inference=True`; upsert `PointStruct(id=..., vector=Document(text=..., model="sentence-transformers/all-MiniLM-L6-v2"), payload=...)` and the cluster embeds for you [Cloud inference](https://skills.qdrant.tech/md/documentation/cloud/inference/)
- Free models are available; paid models bill per 1M tokens; inference runs in-region (EU for EU clusters, US otherwise; free models US-only) [Cloud inference](https://skills.qdrant.tech/md/documentation/cloud/inference/)
- Beware: embedding in-cluster adds latency per point — batch accordingly and prefer vector pre-computation for huge loads

## Verify Ingestion Completed

Use when: the upload finished and you need proof before switching traffic.

- `client.get_collection(name)` → `points_count`, `indexed_vectors_count`, `optimizer_status` [Collections](https://skills.qdrant.tech/md/documentation/manage-data/collections/)
- Compare `points_count` with source row count; if `indexed_vectors_count < points_count`, indexing is still catching up (see Indexing section)
- Spot-check recall: run a few queries against known neighbors [Search](https://skills.qdrant.tech/md/documentation/search/search/)
- Cloud-only `/sys_metrics` for cluster-level ingress/load-balancer health [Cluster monitoring](https://skills.qdrant.tech/md/documentation/cloud/cluster-monitoring/)

## What NOT to Do

- Do not upload with `wait=True` while `prevent_unoptimized` is on — head-of-line blocking can time out writes during ingestion [Read-write contention](https://skills.qdrant.tech/md/documentation/ops-optimization/read-write-contention/)
- Do not create payload indexes AFTER HNSW is built (filterable vector index breaks; needs rebuild)
- Do not use `m=0` on an existing collection to skip indexing — it can drop the existing HNSW and force long reindexing [Bulk upload](https://skills.qdrant.tech/md/documentation/manage-data/bulk-upload/)
- Do not upload one point per request (per-request overhead dominates; batch 64-256)
- Do not filter on fields without payload indexes in cloud — strict mode rejects the write/read
- Do not assume `points_count` == indexed vectors: unindexed segments search by brute force until the optimizer catches up
- Do not store vectors in RAM on small cloud nodes — use `on_disk=True` or quantization when data outgrows memory
- Do not pick 1 shard on a multi-node cluster "to keep it simple" — you forfeit parallel ingestion and can't split a shard across nodes later (reshard up instead)
- Do not ignore cloud alerts or run past 80% memory/disk during a load — the cluster will throttle or OOM
