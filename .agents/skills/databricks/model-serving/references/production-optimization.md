# Production Optimization for Serving Endpoints

Source: [Databricks docs](https://docs.databricks.com/aws/en/machine-learning/model-serving/production-optimization)

## When to Optimize

Optimize when you hit any of these scenarios:
- **> 50K QPS** to a single endpoint
- **Sub-100ms** latency requirements
- **HTTP 429 errors** during traffic spikes
- **Cost targets** not being met
- **Moving from dev → production**

---

## Infrastructure Optimizations

### 1. Route Optimization (Biggest Impact)

| Metric | Standard | Route-Optimized |
|--------|----------|-----------------|
| QPS per workspace | 200 | 50,000+ |
| Client concurrency | 192–1,024 | No explicit limit |
| Overhead latency | < 50 ms | < 20 ms |

**Enable for:** Custom model endpoints only. Requires OAuth tokens.

### 2. Provisioned Concurrency

```
Required Concurrency = Target QPS × Average Latency (seconds)
```

**Best practices:**
- **Minimum**: Set high enough to handle baseline traffic without queuing
- **Maximum**: Set high enough for spikes while controlling cost
- **Autoscaling**: Always enable to dynamically adjust capacity

### 3. Instance Type Selection

| Type | Best For | Trade-off |
|------|----------|-----------|
| CPU (Small/Medium/Large) | Lightweight models, simple inference | Lower cost, slower for compute-intensive |
| GPU (Small/Medium/Large) | Large models, DL, image/video | Higher cost, optimal for deep learning |

> Start with CPU for dev/test. Switch to GPU only if you observe high inference latency.

---

## Model Optimizations

### Model Size & Complexity
- Smaller models → faster inference → higher QPS
- Consider **quantization** or **pruning** for large models

### Batching
- Send multiple requests in a single call to reduce per-prediction overhead

### Pre/Post-Processing
- Offload complex pre/post-processing from the serving endpoint
- Endpoint should only do inference

---

## Client-Side Optimizations

### Connection Pooling
- Use Databricks SDK — it auto-implements pooling
- If using custom clients, implement pooling yourself

### Error Handling & Retry
- Implement exponential backoff for 429/503 errors
- See [model-serving-limits.md](model-serving-limits.md) for retry pattern

### Payload Size
- Minimize request/response payload to reduce network transfer time

---

## Monitoring

| Metric | What It Measures | Target | Action if Exceeded |
|--------|-----------------|--------|-------------------|
| Latency (P50/P90/P99) | Response time | <100–500ms | Check queuing, optimize model/client |
| Throughput (QPS) | Requests/second | Workload-dependent | Enable route optimization, increase concurrency |
| Error rate | % failed requests | <1% | Review logs, check capacity |
| Queue depth | Requests waiting | 0 | Increase min concurrency or enable autoscaling |
| CPU/Memory usage | Resource utilization | <80% | Scale up instance type or increase concurrency |

### Cost Monitoring via System Tables

```sql
-- Aggregate model serving DBUs per day (last 30 days)
SELECT SUM(usage_quantity) AS model_serving_dbus, usage_date
FROM system.billing.usage
WHERE sku_name LIKE '%SERVERLESS_REAL_TIME_INFERENCE%'
GROUP BY usage_date
ORDER BY usage_date DESC
LIMIT 30;

-- Isolate batch inference costs
SELECT *
FROM system.billing.usage
WHERE workspace_id = <workspace_id>
  AND billing_origin_product = 'MODEL_SERVING'
  AND product_features.model_serving.offering_type = 'BATCH_INFERENCE';
```

### SKU Names

| `sku_name` Pattern | Description |
|--------------------|-------------|
| `<tier>_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_<region>` | DBUs accrued when endpoint starts after scale-to-zero |
| `<tier>_SERVERLESS_REAL_TIME_INFERENCE_<region>` | All other model serving costs |

---

## Troubleshooting Performance Issues

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| **Queuing / 429 errors** | Insufficient provisioned concurrency | Increase min concurrency, enable route optimization |
| **High latency** | Model too complex, or external API bottleneck | Quantize model, offload pre/post-processing, cache external calls |
| **Slow scale-up** | GPU autoscaling, large model container | Use express deployments, increase min concurrency |
| **Timeouts (504)** | Model execution > 597s | Optimize model, reduce input size, increase concurrency |
| **Cold start latency** | Scale-to-zero enabled | Disable scale-to-zero for production |
