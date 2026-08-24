---
name: qdrant
description: >
  Unified Qdrant skill suite for vector search, clients, deployment, Qdrant Cloud
  ingestion, Edge, multitenancy, monitoring, performance tuning, scaling, search
  quality, hybrid retrieval, model migration, and version upgrades. Use this parent
  skill for every Qdrant task, then load the narrowest sub-skill from the routing
  tables. Trigger whenever the user mentions Qdrant, vector collections, Qdrant Cloud,
  Qdrant Edge, HNSW, payload indexes, hybrid search, or Qdrant operations.
---

# Qdrant — Unified Skill Suite

Use this as the entry point for Qdrant work. Identify whether the request concerns
deployment, ingestion, retrieval quality, runtime performance, capacity, tenancy, or
operations before loading a narrow sub-skill.

## Primary routing

| Topic | Sub-skill | Load when |
|---|---|---|
| Client SDKs | [`qdrant-clients-sdk`](qdrant-clients-sdk/SKILL.md) | Python, JavaScript/TypeScript, Rust, Java, .NET, Go, upload/search APIs, or client integration |
| Deployment choice | [`qdrant-deployment-options`](qdrant-deployment-options/SKILL.md) | Qdrant Cloud vs self-hosted vs local/embedded vs Edge, Docker, or architecture selection |
| Qdrant Cloud ingestion | [`qdrant-cloud-ingestion`](qdrant-cloud-ingestion/SKILL.md) | Cloud URL/API key, collections, payload indexes, bulk upload, migration, strict mode, or slow cloud ingestion |
| Qdrant Edge | [`qdrant-edge`](qdrant-edge/SKILL.md) | Embedded Edge shards, snapshots/sync, on-device embeddings, BM25, or app-side fusion |
| Embedding model migration | [`qdrant-model-migration`](qdrant-model-migration/SKILL.md) | Re-embedding, changing vector dimensions/providers, dual models, A/B testing, or zero-downtime model migration |
| Multitenancy architecture | [`qdrant-multitenancy`](qdrant-multitenancy/SKILL.md) | Tenant isolation, collection strategy, payload partitioning, dedicated shards, noisy neighbors, or residency |
| Monitoring and incidents | [`qdrant-monitoring`](qdrant-monitoring/SKILL.md) | Health, metrics, Prometheus/Grafana, optimizer state, production slowdown, memory growth, or debugging |
| Proactive performance tuning | [`qdrant-performance-optimization`](qdrant-performance-optimization/SKILL.md) | Planning search, indexing, or memory configuration improvements before/without an active incident |
| Capacity and throughput scaling | [`qdrant-scaling`](qdrant-scaling/SKILL.md) | Nodes, shards, replicas, QPS, result volume, latency, data growth, or vertical/horizontal scaling |
| Search relevance | [`qdrant-search-quality`](qdrant-search-quality/SKILL.md) | Bad results, low recall/precision, missing matches, embeddings, hybrid search, reranking, or retrieval evaluation |
| Qdrant upgrades | [`qdrant-version-upgrade`](qdrant-version-upgrade/SKILL.md) | Rolling upgrades, compatibility, availability, backups, or upgrade sequencing |

## Monitoring routing

| Need | Sub-skill |
|---|---|
| Set up metrics, health probes, dashboards, alerts, and logs | [`qdrant-monitoring-setup`](qdrant-monitoring/setup/SKILL.md) |
| Diagnose an active production issue from metrics | [`qdrant-monitoring-debugging`](qdrant-monitoring/debugging/SKILL.md) |

## Performance routing

| Need | Sub-skill |
|---|---|
| Slow searches, filtered query latency, or low QPS | [`qdrant-search-speed-optimization`](qdrant-performance-optimization/search-speed-optimization/SKILL.md) |
| Slow uploads, optimizer/index build, or segment merge issues | [`qdrant-indexing-performance-optimization`](qdrant-performance-optimization/indexing-performance-optimization/SKILL.md) |
| High RAM, OOM, recovery memory, or quantization memory questions | [`qdrant-memory-usage-optimization`](qdrant-performance-optimization/memory-usage-optimization/SKILL.md) |

## Scaling routing

| Need | Sub-skill |
|---|---|
| Tail latency and p99 reduction | [`qdrant-minimize-latency`](qdrant-scaling/minimize-latency/SKILL.md) |
| Increase concurrent query throughput/QPS | [`qdrant-scaling-qps`](qdrant-scaling/scaling-qps/SKILL.md) |
| Large limits, scrolling, pagination, or fetching many vectors | [`qdrant-scaling-query-volume`](qdrant-scaling/scaling-query-volume/SKILL.md) |
| Data no longer fits or growth planning | [`qdrant-scaling-data-volume`](qdrant-scaling/scaling-data-volume/SKILL.md) |
| Add nodes, shards, or reshard | [`qdrant-horizontal-scaling`](qdrant-scaling/scaling-data-volume/horizontal-scaling/SKILL.md) |
| Increase node CPU/RAM/disk | [`qdrant-vertical-scaling`](qdrant-scaling/scaling-data-volume/vertical-scaling/SKILL.md) |
| Scale many tenants/dedicated shards | [`qdrant-tenant-scaling`](qdrant-scaling/scaling-data-volume/tenant-scaling/SKILL.md) |
| Retain only recent time-window data | [`qdrant-sliding-time-window`](qdrant-scaling/scaling-data-volume/sliding-time-window/SKILL.md) |

## Search-quality routing

| Need | Sub-skill |
|---|---|
| Diagnose relevance and measure recall/precision | [`qdrant-search-quality-diagnosis`](qdrant-search-quality/diagnosis/SKILL.md) |
| Select hybrid, reranking, diversity, discovery, or feedback strategy | [`qdrant-search-strategies`](qdrant-search-quality/search-strategies/SKILL.md) |
| Dense + sparse hybrid retrieval | [`qdrant-hybrid-search`](qdrant-search-quality/search-strategies/hybrid-search/SKILL.md) |
| Build sparse/dense/multi-field prefetch queries | [`qdrant-hybrid-search-prefetches`](qdrant-search-quality/search-strategies/hybrid-search/search-types/SKILL.md) |
| Combine rankings with RRF, DBSF, or custom fusion | [`qdrant-hybrid-search-combining`](qdrant-search-quality/search-strategies/hybrid-search/combining-searches/SKILL.md) |
| Expand candidates with relevance feedback | [`qdrant-relevance-feedback`](qdrant-search-quality/search-strategies/relevance-feedback/SKILL.md) |

## Shared operating rules

1. Establish deployment type, Qdrant version, client version, collection vector schema,
   shard/replica configuration, data volume, workload, and SLO before changing settings.
2. Distinguish **diagnosis** from **proactive tuning**. For a live incident, observe first
   with monitoring; do not blindly alter HNSW, optimizer, quantization, or shard settings.
3. Treat relevance, latency, indexing throughput, memory, durability, and cost as separate
   axes. An optimization for one can regress another.
4. Reproduce changes on representative data and filters, establish a baseline, change one
   variable at a time, and retain rollback steps.
5. Never expose Qdrant API keys. Use environment/secret management and redact diagnostics.
6. For Qdrant Cloud, account for strict mode, provider/region, node topology, and managed
   limits instead of assuming self-hosted controls are available.
7. Keep collection aliases and migration checkpoints when changing embedding models,
   schemas, sharding, or deployment topology.

## Documentation

- Qdrant documentation: https://qdrant.tech/documentation/
- Qdrant Cloud: https://qdrant.tech/documentation/cloud/
- API reference: https://api.qdrant.tech/
- Client libraries: https://qdrant.tech/documentation/interfaces/
