# MLflow Prompt Registry reference

This reference is a practical map of the current MLflow Prompt Registry
documentation. Load the narrow official subsection when an API detail matters.

## Documentation subsections

| Topic | URL |
|---|---|
| Landing/concepts/caching | https://mlflow.org/docs/latest/genai/prompt-registry/ |
| Create and edit | https://mlflow.org/docs/latest/genai/prompt-registry/create-and-edit-prompts/ |
| Lifecycle aliases | https://mlflow.org/docs/latest/genai/prompt-registry/manage-prompt-lifecycles-with-aliases/ |
| Use in apps | https://mlflow.org/docs/latest/genai/prompt-registry/use-prompts-in-apps/ |
| Log with models | https://mlflow.org/docs/latest/genai/prompt-registry/log-with-model/ |
| Structured output | https://mlflow.org/docs/latest/genai/prompt-registry/structured-output/ |
| Evaluate | https://mlflow.org/docs/latest/genai/prompt-registry/evaluate-prompts/ |
| Optimize | https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/ |
| Rewrite for models | https://mlflow.org/docs/latest/genai/prompt-registry/rewrite-prompts/ |
| Playground | https://mlflow.org/docs/latest/genai/prompt-registry/playground/ |

## Lifecycle API

```python
import mlflow

prompt = mlflow.genai.register_prompt(
    name="catalog.schema.support-agent",
    template="Answer {{question}} using the approved support policy.",
    commit_message="Initial support policy prompt",
    tags={"owner": "support-ai"},
    model_config={"temperature": 0.2, "max_tokens": 800},
)

exact = mlflow.genai.load_prompt(
    "prompts:/catalog.schema.support-agent/1"
)
candidate = mlflow.genai.load_prompt(
    "prompts:/catalog.schema.support-agent@candidate"
)
```

Key semantics:

- New template content creates a new sequential version; existing versions are
  immutable.
- `commit_message` is the prompt-level reason for the change; link it to the
  Git PR/release ID in surrounding metadata.
- `prompts:/<name>/<version>` is deterministic; `prompts:/<name>@<alias>` is a
  mutable policy pointer.
- `@latest` is convenience resolution, not a release approval.
- Prompt-level tags and version-level tags have different scopes.
- `model_config` stores inference configuration but can be mutable; include a
  digest in release evidence and evaluate changes even if the template version
  is unchanged.

## Templates and response formats

The docs cover text and chat templates, `{{variable}}` formatting, Jinja
control-flow detection/sandboxing, and framework interop. Validate variables and
escaping before provider calls. `response_format` documents the intended
structured output shape; it does not replace runtime validation.

For a Databricks release, record:

```text
prompt URI, template digest, format type, required variables,
response schema/version, model_config digest, provider/model compatibility
```

## Aliases and caching

Aliases such as `candidate`, `staging`, and `production` can be repointed to
numbered versions. Use exact versions in offline evaluation and release
manifests. If a live process intentionally loads aliases, document cache TTL,
alias propagation, and rollback behavior. Test the version-based and alias-based
cache paths independently; immutable and mutable references have different
reproducibility properties.

## Lineage connections

The Prompt Registry documentation describes automatic linking when registry
prompts are loaded inside traced/running application code and prompt dependency
capture for supported model logging. Use this with the broader Databricks
manifest:

```text
prompt version -> trace/run -> LoggedModel -> UC registered version
             -> endpoint/served entity -> evaluation/deployment evidence
```

Do not rely only on automatic linkage when a release crosses jobs, endpoints,
or environments. Persist explicit prompt URI/version and alias-resolution
metadata in the release manifest and trace tags.

## Optimization and rewriting

The latest docs describe `optimize_prompts()` with `predict_fn`, `train_data`,
`prompt_uris`, an optimizer, and scorers. GEPA and MetaPromptOptimizer have
different cost/data trade-offs. The optimization result registers new prompt
versions; it is not permission to promote them automatically.

For model migration, use the documented trace → dataset → target model → prompt
rewrite/optimization → independent evaluation workflow. Test output quality,
safety, tool calls, retrieval, latency, and cost—not just textual equivalence.

## Currentness and Databricks caveats

- Check MLflow version before using `optimize_prompts()`; the latest docs identify
  MLflow 3.5.0+.
- The Playground requires the relevant AI Gateway/chat endpoint capability.
- OSS MLflow and Databricks-managed MLflow can differ in Unity Catalog naming,
  permissions, trace storage, managed monitoring, and feature status.
- Re-open the official page and inspect the installed API for exact signatures;
  this reference is a workflow aid, not a replacement for versioned docs.
