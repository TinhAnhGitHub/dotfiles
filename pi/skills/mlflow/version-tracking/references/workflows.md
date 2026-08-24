# Version tracking workflows

## Manual Git workflow

Use this portable pattern when automatic Git versioning is unavailable:

```python
import hashlib
import json
import subprocess
import mlflow
from mlflow.utils.git_utils import get_git_commit

def git_state(repo: str = ".") -> dict[str, str | bool]:
    commit = get_git_commit(repo) or "local-dev"
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    ).stdout
    return {
        "commit": commit,
        "dirty": bool(status.strip()),
        "status_digest": hashlib.sha256(status.encode()).hexdigest(),
    }

state = git_state()
config = {
    "prompt_uri": "prompts:/support-system/7",
    "provider_model": "<PINNED_MODEL_ID>",
    "temperature": 0.2,
}
config_digest = hashlib.sha256(
    json.dumps(config, sort_keys=True).encode()
).hexdigest()[:12]
name = f"support-agent-{state['commit'][:12]}-{config_digest}"

with mlflow.set_active_model(name=name) as active_model:
    mlflow.log_model_params(
        {**config, **state},
        model_id=active_model.model_id,
    )
    traced_agent("test request")
```

Do not persist a raw dirty diff if it may contain credentials or private data. A digest plus a
secured CI artifact is often safer.

## Fair candidate comparison

Hold data, scorers, judge configuration, and sampling policy constant. Change only the candidate
app version under comparison:

```python
import mlflow
from mlflow.genai.scorers import Correctness, Guidelines

DATA = [
    {
        "inputs": {"question": "How do I reset my password?"},
        "expectations": {"expected_facts": ["Use the account recovery page"]},
        "tags": {"slice": "account-recovery"},
    }
]
SCORERS = [
    Correctness(),
    Guidelines(name="actionable", guidelines="Give a concrete next action."),
]

def evaluate_candidate(version_name, app):
    with mlflow.set_active_model(name=version_name):
        return mlflow.genai.evaluate(
            data=DATA,
            predict_fn=app,
            scorers=SCORERS,
        )
```

Compare:

- scorer pass rates and confidence/disagreement;
- latency and token/cost distributions, not only means;
- errors and trace structure;
- slice-level regressions;
- human-reviewed failures;
- operational compatibility and security changes.

Aggregate improvements cannot excuse a critical-slice regression.

## CI workflow

1. Build a clean immutable source revision.
2. Create/select the LoggedModel and capture lock/container digests.
3. Run smoke traces and schema validation.
4. Evaluate the candidate against the versioned regression dataset.
5. Compare against the current approved baseline with explicit thresholds.
6. On pass, package and register the executable artifact.
7. Move a registry alias only after approval; deploy/update the endpoint separately.
8. Record run ID, model ID, registered version, endpoint config version, and release ID.

## Production incident workflow

1. Start from a failing trace and read its linked LoggedModel ID.
2. Resolve prompt, tool/MCP, retriever, provider model, and policy versions.
3. Confirm the actual served entity/config at the event timestamp.
4. Reproduce against the same input in an isolated environment.
5. Compare to the previous known-good version on the same case and dataset slice.
6. Curate the trace into the evaluation dataset with an approved expectation.
7. Add a regression test, fix the responsible layer, evaluate, and redeploy.

## Automatic Git versioning guardrails

`mlflow.genai.enable_git_model_versioning()` is convenient but experimental. Pin an MLflow minor
version, test dirty-state handling, verify repository URL redaction, and use a fallback for
environments where `.git` metadata is unavailable. Databricks Git Folders have documented
limitations for this feature; use CI-provided commit metadata there.
