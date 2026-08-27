# Version Gates and Source-of-Truth Guardrails

MLflow GenAI APIs evolve rapidly. Use this file whenever exact imports, defaults, preview
status, filter syntax, or environment capabilities matter.

## Source-of-truth order

1. Installed API signature/source in the target environment.
2. Environment-specific current docs:
   - OSS behavior: `mlflow.org/docs/latest`.
   - Databricks behavior: the workspace cloud's Databricks docs.
3. API reference for the installed version, not only `/latest/`.
4. Release notes and open issues for recently shipped features.
5. Examples/blogs only after they agree with the above.

When docs conflict, report the conflict and choose the target environment's source rather
than silently blending APIs.

## Runtime preflight

```python
import inspect
import mlflow

print("MLflow:", mlflow.__version__)
print("Tracking URI:", mlflow.get_tracking_uri())
print("evaluate:", inspect.signature(mlflow.genai.evaluate))

from mlflow.genai.scorers import scorer
print("scorer:", inspect.signature(scorer))
```

Use `scripts/inspect_capabilities.py` for a broader non-mutating check.

## Important version gates observed during research

These are documentation-era guides, not substitutes for runtime verification:

| Capability | Documented gate/status |
|---|---|
| Core MLflow 3 GenAI evaluation/scorers | MLflow 3.x; many core APIs from 3.1+ |
| Expectations API | Current guide says 3.2+ |
| Custom `make_judge` flow | Research/docs identify 3.4+ |
| Prompt optimization | Research/docs identify 3.5+ |
| First multi-turn judges | Built-in page says experimental from 3.7 |
| Judge Builder UI | 3.9+ |
| Full multi-turn evaluation/simulation | Experimental workflow documented for 3.10+ |
| Automatic issue detection | Recent release material identifies 3.11.1+ |
| Trace session/user context manager | Databricks research identifies 3.11+ |
| `@mlflow.test` regression testing | Current CI guide installs 3.14+ |
| Databricks UC trace location | Current Databricks docs require 3.14+ |
| Databricks production monitoring/backfill/archive | Beta |

## Known documentation drift

### Default judge model

Docs/source have referenced different OpenAI default model names over time, while
Databricks chooses an environment-specific hosted default. Never hard-code a claim about
the default. Pin `model=` or set `MLFLOW_GENAI_JUDGE_DEFAULT_MODEL`.

### `make_judge` import

Examples have used both `from mlflow.genai import make_judge` and
`from mlflow.genai.judges import make_judge`. Inspect the target version and use its API
reference.

### `scorer` import

Examples have used `from mlflow.genai import scorer` and
`from mlflow.genai.scorers import scorer`. Prefer the current API-reference path in the
target version; do not mass-rewrite working imports without verification.

### Skip trace-validation environment variable

Research found conflicting names (`MLFLOW_GENAI_EVAL_SKIP_TRACE_VALIDATION` and
`MLFLOW_GENAI_SKIP_EVAL_TRACE_VALIDATION`). Read
`mlflow.environment_variables` in the installed version.

### Multi-turn versions

Individual multi-turn judges appeared before the full conversation evaluation/simulation
framework. For a complete workflow, gate on the newer full-framework version rather than
only checking that one judge class imports.

### Production monitoring

Upstream OSS now documents automatic evaluation with LLM judges. Databricks separately
documents a managed Beta production-monitoring service that can also run constrained
custom `@scorer` functions. Do not claim all online features are Databricks-only or that
OSS accepts online code scorers.

### Trace filter grammar

Filter grammar changed across 3.x:

- newer generic docs prefer `trace.status`, `tag.<key>`, `metadata.<key>`;
- older docs used bare fields and `tags.`;
- current Databricks monitoring examples can use `attributes.status`;
- UC adds span/content/token/feedback/expectation filters;
- DataFrame column names differ from filter names.

Copy grammar from the target service/version and test it on a small query before
scheduling monitoring.

### `trace_id` vs `request_id` vs `client_request_id`

- `trace_id`: MLflow 3 primary trace identity.
- `request_id`: legacy MLflow 2 name/deprecated alias.
- `client_request_id`: user-provided external correlation identifier.

Never substitute one for another.

## Feature detection patterns

```python
from importlib.util import find_spec

has_simulators = find_spec("mlflow.genai.simulators") is not None
has_databricks_agents = find_spec("databricks.agents") is not None
```

```python
from mlflow.genai import scorers

if not hasattr(scorers, "ScorerSamplingConfig"):
    raise RuntimeError("This MLflow version lacks automatic-evaluation sampling APIs")
```

Feature detection is useful for diagnostics, but production code should still pin and
test dependency versions.

## Preview and experimental rules

For every preview/experimental capability:

1. Link the current source page.
2. State required MLflow/package/runtime/workspace version.
3. State cloud/region/preview-toggle requirements.
4. Isolate the feature behind a small adapter.
5. Add a smoke test that inspects signatures and runs one example.
6. Define a fallback or disable path.
7. Do not promise long-term schema compatibility.

## Sources

- https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html
- https://mlflow.org/docs/latest/api_reference/python_api/mlflow.environment_variables.html
- https://mlflow.org/docs/latest/genai/eval-monitor/faq/
- https://mlflow.org/docs/latest/genai/tracing/search-traces/
- https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/production-monitoring
- https://docs.databricks.com/aws/en/mlflow3/genai/tracing/trace-unity-catalog
