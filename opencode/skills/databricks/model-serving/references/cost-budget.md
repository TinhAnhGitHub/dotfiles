# Cost Controls & Budget Policies for Model Serving

---

## Cost Model

Model Serving uses **DBUs (Databricks Units)** as the billing currency. Costs are incurred for:
- **Inference compute** — per-request processing on CPU/GPU
- **Cold starts** — endpoint startup after scale-to-zero
- **Container builds** — when deploying new model versions
- **Zero-downtime updates** — billed for both old + new config during transition

---

## Viewing Costs via System Tables

Enable the billing usage system table in Unity Catalog:

```sql
-- Aggregate model serving costs per day
SELECT SUM(usage_quantity) AS model_serving_dbus, usage_date
FROM system.billing.usage
WHERE sku_name LIKE '%SERVERLESS_REAL_TIME_INFERENCE%'
GROUP BY usage_date
ORDER BY usage_date DESC
LIMIT 30;

-- Filter by endpoint name
SELECT usage_date, usage_quantity, usage_metadata.endpoint_name
FROM system.billing.usage
WHERE sku_name LIKE '%SERVERLESS_REAL_TIME_INFERENCE%'
  AND usage_metadata.endpoint_name = 'my-endpoint'
ORDER BY usage_date DESC;

-- Isolate batch inference costs
SELECT *
FROM system.billing.usage
WHERE workspace_id = <workspace_id>
  AND billing_origin_product = 'MODEL_SERVING'
  AND product_features.model_serving.offering_type = 'BATCH_INFERENCE';
```

### SKU Names

| SKU Pattern | When It Appears |
|-------------|-----------------|
| `<tier>_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_<region>` | Cold start after scale-to-zero |
| `<tier>_SERVERLESS_REAL_TIME_INFERENCE_<region>` | All ongoing inference compute |

---

## Cost Optimization Strategies

| Strategy | How | Impact |
|----------|-----|--------|
| **Scale to zero** | Enable for dev/demo endpoints | Zero cost when idle; cold-start latency on first request |
| **Disable scale to zero** | Production workloads | Predictable latency, no cold-start cost |
| **Right-size concurrency** | Set min to handle baseline, max for spikes | Avoid over-provisioning |
| **Choose CPU over GPU** | Start with CPU, switch only if needed | Significantly lower cost |
| **Route optimization** | Enable for high-QPS endpoints | More QPS per DBU |
| **Use smaller models** | Prefer Llama 3.1 8B over 405B when possible | Lower cost per token |
| **Tag endpoints** | Use `patch --add-tags` for cost attribution | Enables cost tracking by project/team |
| **Monitor via system tables** | Query `system.billing.usage` regularly | Catch cost anomalies early |

---

## Budget Policies

Databricks supports **serverless budget policies** at the account level:

- **API**: `POST /api/2.0/accounts/<account_id>/budget-policies`
- **Python SDK**: `account_client.budget_policies.create(...)`
- **Terraform**: `databricks_budget_policy` resource

Budget policies let you:
- Set spending limits on serverless compute (including Model Serving)
- Assign policies to users/groups
- Receive alerts when approaching limits

### Example Terraform

```hcl
resource "databricks_budget_policy" "ml_dev" {
  name        = "ml-dev-budget"
  daily_limit = 100   # DBUs
  monthly_limit = 2000

  alert_configurations {
    trigger_type      = "PERCENTAGE"
    trigger_value     = 80
    action_configurations {
      action_type = "EMAIL_NOTIFICATION"
      target      = "team@example.com"
    }
  }
}
```

---

## Cost Attribution Dashboard

Download the [Model Serving cost attribution dashboard](https://github.com/databricks/databricks-dashboard-samples) from GitHub to get started with pre-built cost visualizations.

---

## Pricing Calculator

Use the [GenAI Pricing Calculator](https://www.databricks.com/product/pricing/genai-pricing-calculator) to estimate:
- Provisioned throughput costs
- Pay-per-token costs
- Total cost of ownership for different model sizes/QPS targets
