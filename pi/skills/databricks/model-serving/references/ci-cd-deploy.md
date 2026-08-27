# CI/CD for Model Versions

Automate model training, registration, and deployment using DABs, GitHub Actions, and the Databricks SDK.

---

## Pattern 1: DABs-based Model Deploy (Bundle)

Define a serving endpoint as a DABs resource:

```yaml
# databricks.yml
resources:
  serving_endpoints:
    turbine-risk-endpoint:
      name: turbine-risk-endpoint
      config:
        served_entities:
          - entity_name: "${var.model_full_name}"
            entity_version: "${var.model_version}"
            workload_size: "Small"
            scale_to_zero_enabled: true
        traffic_config:
          routes:
            - served_model_name: "${var.model_name}-${var.model_version}"
              traffic_percentage: 100
      tags:
        - key: "project"
          value: "turbine"
```

Deploy via CLI:

```bash
databricks bundle deploy -t prod --var="model_full_name=catalog.schema.model" --var="model_version=3" --var="model_name=model"
```

---

## Pattern 2: GitHub Actions CI/CD Pipeline

```yaml
# .github/workflows/model-deploy.yml
name: Train & Deploy Model

on:
  push:
    branches: [main]
    paths:
      - 'training/**'
      - 'models/**'

jobs:
  train-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Databricks CLI
        uses: databricks/setup-cli@v0.9.0

      - name: Train and register model
        run: |
          # Submit training as a serverless job
          RUN_ID=$(databricks jobs submit --no-wait --output json --json '
          {
            "run_name": "train-and-deploy-${{ github.sha }}",
            "tasks": [{
              "task_key": "train",
              "notebook_task": {
                "notebook_path": "/Users/me@example.com/train_model",
                "base_parameters": {
                  "git_sha": "${{ github.sha }}"
                }
              },
              "environment_key": "ml_env"
            }],
            "environments": [{
              "environment_key": "ml_env",
              "spec": {
                "client": "4",
                "dependencies": ["mlflow>=3.0", "xgboost==2.1.3"]
              }
            }]
          }' | jq -r .run_id)

          # Poll for completion
          for i in $(seq 60); do
            STATE=$(databricks jobs get-run "$RUN_ID" --output json | jq -r '.state.life_cycle_state')
            echo "$STATE"
            [[ "$STATE" =~ ^(TERMINATED|SKIPPED|INTERNAL_ERROR)$ ]] && break
            sleep 30
          done

          # Get model version from output
          TASK_RUN_ID=$(databricks jobs get-run "$RUN_ID" --output json | jq -r '.tasks[0].run_id')
          MODEL_VERSION=$(databricks jobs get-run-output "$TASK_RUN_ID" --output json | jq -r '.notebook_output.result | fromjson | .model_version')
          echo "model_version=$MODEL_VERSION" >> $GITHUB_ENV

      - name: Deploy to staging
        run: |
          databricks serving-endpoints update-config turbine-risk-endpoint-staging --json '{
            "served_entities": [{
              "entity_name": "catalog.schema.model",
              "entity_version": "'${{ env.model_version }}'",
              "workload_size": "Small",
              "scale_to_zero_enabled": true
            }]
          }'

      - name: Run validation tests
        run: |
          # Query staging endpoint and validate results
          RESULT=$(databricks serving-endpoints query turbine-risk-endpoint-staging \
            --json '{"dataframe_records": [{"feature1": 0.5, "feature2": 0.3}]}')
          echo "Validation result: $RESULT"

      - name: Promote alias
        run: |
          databricks api post /api/2.0/mlflow/registered-models/alias \
            --json '{
              "name": "catalog.schema.model",
              "alias": "prod",
              "version": "'${{ env.model_version }}'"
            }'

      - name: Deploy to production
        run: |
          databricks serving-endpoints update-config turbine-risk-endpoint --json '{
            "served_entities": [{
              "entity_name": "catalog.schema.model",
              "entity_version": "'${{ env.model_version }}'",
              "workload_size": "Small",
              "scale_to_zero_enabled": false
            }]
          }'
```

---

## Pattern 3: Automated Canary Deployment

Deploy a new version alongside the current one with traffic splitting:

```python
from mlflow.deployments import get_deploy_client

client = get_deploy_client("databricks")

# Step 1: Register new version and promote to @challenger alias
client.set_registered_model_alias(FULL_NAME, "challenger", new_version)

# Step 2: Update endpoint with canary traffic split
client.update_endpoint(endpoint="turbine-risk-endpoint", config={
    "served_entities": [
        {
            "entity_name": FULL_NAME,
            "entity_version": current_version,  # current prod
            "workload_size": "Small",
            "scale_to_zero_enabled": False,
        },
        {
            "entity_name": FULL_NAME,
            "entity_version": new_version,  # challenger
            "workload_size": "Small",
            "scale_to_zero_enabled": False,
        },
    ],
    "traffic_config": {"routes": [
        {"served_model_name": f"model-{current_version}", "traffic_percentage": 95},
        {"served_model_name": f"model-{new_version}", "traffic_percentage": 5},
    ]},
})
```

**Canary promotion workflow:**
1. Deploy new version with 5% traffic
2. Monitor latency, error rate, and prediction drift for N minutes
3. If healthy, increase challenger to 50% → 100%
4. Remove old version once 100% traffic on new version

---

## Pattern 4: Terraform Infrastructure-as-Code

```hcl
resource "databricks_model_serving_endpoint" "this" {
  name = "turbine-risk-endpoint"
  config {
    served_entities {
      entity_name          = var.model_full_name
      entity_version       = var.model_version
      workload_size        = "Small"
      scale_to_zero_enabled = false
    }
    traffic_config {
      routes {
        served_model_name  = "model-${var.model_version}"
        traffic_percentage = 100
      }
    }
  }
  tags {
    project = "turbine"
  }
}
```

---

## Best Practices for CI/CD

| Practice | Detail |
|----------|--------|
| **Immutable versions** | Every model version is a new artifact in UC — never overwrite |
| **Aliases, not stages** | Use `@prod` / `@challenger` / `@staging` aliases, not deprecated stages |
| **Pre-deploy validation** | Run `mlflow.models.predict(env_manager="uv")` before deploying |
| **Check for existing deploy** | Query `jobs list-runs --active-only` before submitting a new training job |
| **Check existing endpoint** | Query `serving-endpoints get` before attempting create/update |
| **Tag all resources** | Add `project`, `team`, `environment` tags for cost attribution |
| **Separate staging/prod** | Use different endpoint names or DABs targets |
