# Reproducibility, evaluation, registry, and serving

## Validate before registry

Use a clean environment, not the development notebook's imports. At minimum:

```python
import mlflow

loaded = mlflow.pyfunc.load_model(info.model_uri)
result = loaded.predict(REALISTIC_REQUEST)
```

When supported in the target release, `mlflow.models.predict(..., env_manager="uv")` is useful for
dependency-isolated pre-deployment validation. Confirm the installed signature first.

Validation suite:

- valid, boundary, malformed, and oversized requests;
- sync output and streaming event/final-output equivalence;
- missing credentials and unavailable remote dependencies;
- tool timeout, malformed arguments, denial, and duplicate request;
- retriever empty/error paths and citations;
- process restart and horizontal concurrency;
- trace completeness and PII redaction;
- dependency/security scan and source-artifact review.

## Evaluation gate

Load `evaluation-monitoring` and test the exact logged artifact or an equivalent `predict_fn`:

```python
import mlflow
from mlflow.genai.scorers import Correctness, Guidelines

model = mlflow.pyfunc.load_model(info.model_uri)

def predict_fn(question: str):
    response = model.predict({"input": [{"role": "user", "content": question}]})
    return extract_final_text(response)

results = mlflow.genai.evaluate(
    data=eval_dataset,
    predict_fn=predict_fn,
    scorers=[Correctness(), Guidelines(name="safe", guidelines="Do not expose secrets." )],
)
```

The extraction adapter is part of the contract and needs tests; do not silently score the wrong
field or only the last stream chunk.

## Register approved artifact

Load `model-registry`. Register the `info.model_uri`, not a reconstructed model:

```python
registered = mlflow.register_model(
    model_uri=info.model_uri,
    name="catalog.schema.support_agent",  # three levels for Databricks UC
)
```

Unity Catalog requires a signature. Record evaluation run/dataset/scorer versions as model-version
tags or governed release metadata, then move an alias only after policy checks pass.

## OSS serving

```bash
mlflow models serve -m 'models:/support-agent@candidate' --env-manager virtualenv
```

Inspect the generated scoring contract and test streaming support for the chosen serving stack;
not every generic server/client path exposes provider-style streaming identically.

## Databricks serving

Load `databricks` and `databricks-model-serving`. A serving endpoint references a concrete UC model
version through a served entity. Declare Databricks resources required for passthrough auth when
logging the model. Validate with the endpoint's OpenAPI schema when available, update endpoint
config for a new version, and wait for both readiness fields.

Canary sequence:

1. Add new served entity at 0–10% traffic.
2. Query the entity directly for smoke tests (this bypasses traffic routing).
3. Observe errors, latency, traces/inference tables, and quality signals by served entity.
4. Increase traffic in controlled steps.
5. Roll back by restoring routes/previous entity version, not merely by moving a registry alias.

During zero-downtime update, the old config can serve while the new one builds and both configs can
incur cost. Record endpoint config and served entity IDs in release evidence.
