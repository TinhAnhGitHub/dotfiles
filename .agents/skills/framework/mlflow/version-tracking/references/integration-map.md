# Integration map

## Version tracking and evaluation

Load `evaluation-monitoring` when versions must be compared or gated. Version tracking provides
the candidate identity and lineage; evaluation supplies the stable dataset, `predict_fn`, scorers,
human feedback, regression gate, and production curation loop.

```text
LoggedModel candidate
  → traced predict_fn
  → fixed EvaluationDataset + scorer suite
  → comparison evidence
  → approval or rejection
  → monitored production traces
  → curated regression records
```

## Version tracking and Prompt Registry

Prompt versions are immutable, aliases are movable. For experiments, log both the requested URI
and resolved version. For production, decide whether an app release pins a prompt version or
intentionally resolves a deployment alias at runtime. The latter enables prompt-only rollout but
weakens reproducibility unless every trace records the resolved version.

## Version tracking and GenAI flavors

Load `genai-flavors` when the app must be packaged as an executable MLflow Model. Version tracking
answers **which source/config produced behavior**; a flavor answers **how the executable is logged,
loaded, validated, and served**.

## Version tracking and Model Registry

Load `model-registry` for governed immutable model versions, aliases, promotion, and rollback.
Typical transition:

```text
candidate LoggedModel + evaluation evidence
  → packaged MLflow Model
  → Registered Model Version
  → approval tags and alias
```

READY is a build state; an alias such as `@champion` is a promotion decision. Keep them separate.

## Version tracking and MCP Registry

Load `mcp-registry` when tools are supplied by MCP servers. Capture server name, semver, alias
resolution, access endpoint ID, and tool-schema snapshot/digest in the app version. A tool schema
change can alter agent behavior even if application code and prompts are unchanged.

## Databricks bridge

Load `databricks` then `databricks-model-serving` for endpoint operations. Unity Catalog model
versions and served entities form a separate deployment layer:

```text
UC Registered Model Version N
  → served entity(entity_name, entity_version=N)
  → endpoint config version K
  → traffic route percentage
```

Reassigning a UC model alias does not by itself update a served entity pinned to version N.
Update endpoint config, wait for `state.ready == READY` and
`state.config_update == NOT_UPDATING`, then record the resulting config version. During a
zero-downtime update, the previous config can continue serving until the new config is ready.
