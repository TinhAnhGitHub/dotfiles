# Flavor selection and executable contract

## Separate the lifecycle layers

| Concern | Owner |
|---|---|
| Source/config identity and trace lineage | `version-tracking` |
| Executable packaging and inference schema | this skill |
| Quality evidence and regression gates | `evaluation-monitoring` |
| Immutable governed versions and aliases | `model-registry` |
| Databricks endpoint capacity, traffic, logs, ACLs | `databricks-model-serving` |

## Object serialization versus Models from Code

Choose object serialization only for simple, supported, self-contained objects whose native
serializer is reliable. Choose Models from Code when the model has:

- sockets, clients, file handles, lambdas, closures, or dynamic references;
- LangGraph or partner-package components;
- remote vector stores or resources reconstructed at load time;
- source that must be reviewable and diffable;
- serialization incompatibility across Python/framework versions.

Models from Code stores and executes source, so review the artifact like deployable code. The
model-definition file should construct clients lazily or from environment/managed identity, never
hard-code credentials, and avoid mutating remote state during import.

## Interface contract

Define before logging:

1. **Request schema** — names, nesting, optional fields, conversation context, params.
2. **Response schema** — text, citations, tool calls/results, reasoning visibility, custom output.
3. **Streaming events** — event types, IDs, aggregation, final item, errors/cancellation.
4. **Batching** — whether PyFunc receives one logical request or tabular/list batches.
5. **State** — external conversation/checkpoint store rather than process memory where serving can
   scale horizontally.

Use `input_example` for signature inference where the flavor supports it. Unity Catalog requires
a model signature. Type hints and Pydantic models can improve validation, but feature-detect the
installed MLflow behavior and avoid broad `Union` types that collapse validation.

## Dependencies

Use one explicit strategy:

```python
info = mlflow.pyfunc.log_model(
    python_model="agent.py",
    name="agent",
    input_example={"input": [{"role": "user", "content": "Hello"}]},
    pip_requirements=[
        "mlflow==<TARGET_VERSION>",
        "pydantic>=2,<3",
        "openai==<TESTED_VERSION>",
    ],
)
```

- `pip_requirements` defines the full environment; keep it complete and pinned for production.
- `extra_pip_requirements` supplements flavor-inferred core dependencies, useful for supported
  LangChain components.
- `code_paths` adds local modules but can hide import-root mistakes; validate in an isolated env.
- Never depend on packages that happened to exist in the logging notebook.

## Resources and credentials

Record remote resource identities explicitly when the flavor/API supports `resources`. On
Databricks, resource declarations are important for passthrough authentication to UC functions,
Vector Search indexes, serving endpoints, and other managed dependencies. Load
`databricks-model-serving` for exact current resource types.

Credentials belong in the serving environment's secret/identity mechanism. Confirm that DSPy and
LlamaIndex intentionally strip API keys from serialized settings; inject them at runtime.

## Acceptance checks

- source artifact contains no secrets;
- signature accepts the real client payload and rejects malformed payloads;
- native load and `mlflow.pyfunc.load_model` both behave as documented;
- dependency rebuild succeeds without notebook state;
- remote resources resolve with production identity;
- sync and streaming outputs agree semantically;
- traces contain LLM, retriever, tool, and error spans;
- fixed evaluation dataset passes explicit gates;
- registered model and endpoint refer to the tested artifact.
