# Scaling, Provisioning & GPU Types

## Provisioned Concurrency

Provisioned concurrency controls how many simultaneous requests your endpoint can process.

**Formula:**

```
Required Concurrency = Target QPS × Average Latency (seconds)
```

Example: 100 QPS × 0.2s = 20 concurrent slots.

**Configuration fields** (in create/update JSON):

```json
{
  "served_entities": [{
    "entity_name": "catalog.schema.model",
    "entity_version": "1",
    "min_provisioned_throughput": 0,   // baseline concurrency
    "max_provisioned_throughput": 100, // ceiling for autoscaling
    "workload_size": "Small",          // Small | Medium | Large | Custom
    "scale_to_zero_enabled": false     // true for dev/demo
  }]
}
```

| Field | Purpose |
|-------|---------|
| `min_provisioned_throughput` | Baseline capacity — endpoint always keeps this many slots warm |
| `max_provisioned_throughput` | Ceiling — endpoint autoscales up to this during traffic spikes |
| `workload_size` | `Small`, `Medium`, `Large` — predefined CPU/memory bundles |
| `scale_to_zero_enabled` | Scale down to 0 after 30 min of inactivity |

---

## Scaling Behavior

| Event | Behavior |
|-------|----------|
| **Scale up** | Almost immediate when traffic increases |
| **Scale down** | Every **5 minutes** — reduces capacity to match reduced traffic |
| **Scale to zero** | After **30 minutes** of inactivity (if enabled) |
| **Scale from zero** | 10–20 seconds typical; can take minutes. **No SLA.** |
| **GPU autoscaling** | Takes longer than CPU autoscaling |
| **Node readiness** | After model download + health checks; depends on model size/load time |
| **Cold start** | First request after scale-to-zero: high latency expected |

> ⚠️ **Scale to zero** should NOT be used for production workloads requiring consistent uptime or guaranteed response times.

---

## Workload Types (CPU)

| Workload Type | Memory per Concurrency | When to Use |
|--------------|----------------------|-------------|
| `CPU` (Small) | 4 GB | Lightweight models, simple inference |
| `CPU_MEDIUM` | 8 GB | Models needing more memory per worker |
| `CPU_LARGE` | 16 GB | Memory-intensive models |

Trade more memory for less concurrent capacity on the same CPU hardware.

---

## GPU Instance Types

| Workload Type | GPU | GPU Memory | When to Use |
|--------------|-----|-----------|-------------|
| `GPU_SMALL` | 1× T4 | 16 GB | Lightweight GPU inference |
| `GPU_MEDIUM` | 1× A10G | 24 GB | Standard deep learning |
| `MULTIGPU_MEDIUM` | 4× A10G | 96 GB | Large models, multi-GPU |
| `GPU_MEDIUM_8` | 8× A10G | 192 GB | Very large models |

**GPU Limitations:**
- Container image creation takes **longer** than CPU (model size + deps).
- Deployments may **timeout after 60 minutes** for very large models.
- May fail with "No space left on device" for huge models.
- GPU capacity **not guaranteed** when scaling to zero — extra cold-start latency expected.
- For large LLMs, prefer Foundation Model APIs instead.

---

## Route Optimization

For high-throughput, low-latency production workloads.

| Feature | Standard | Route-Optimized |
|---------|----------|-----------------|
| QPS per workspace | 200 | 50,000+ |
| Client concurrency | 192–1024 | No explicit limit |
| Provisioned concurrency per entity | 1,024 | 1,024 (higher on request) |
| Overhead latency | < 50 ms | < 20 ms |

**Requirements:**
- Custom model endpoints only (not FM APIs or external models)
- OAuth tokens required (PATs not supported)

---

## Express Deployments

For faster endpoint creation, use express deployments. Instead of a full container build (which can take ~10 min), express deployments use pre-built containers for standard MLflow model flavors.

**Availability:** Check `databricks serving-endpoints create -h` for `--express` flag.

---

## Load Testing

Use load testing to validate concurrency configuration:

```bash
# Validate your endpoint can handle the target QPS
databricks serving-endpoints get <ENDPOINT_NAME> --output json | jq '.config'
```

See Databricks [Load testing for serving endpoints](https://docs.databricks.com/aws/en/machine-learning/model-serving/what-is-load-test).

---

## Queuing & Autoscaling

- Endpoints allow **temporary queuing** for traffic bursts.
- Beyond queuing threshold → **HTTP 429 (Too Many Requests)**.
- To minimize queuing:
  1. Set `min_provisioned_throughput` high enough for baseline + typical bursts.
  2. Enable route optimization for higher capacity.
  3. Implement client-side retry with exponential backoff.
