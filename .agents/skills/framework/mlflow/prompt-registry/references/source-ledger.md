# MLflow Prompt Registry documentation source ledger

Reviewed: 2026-08-30

This ledger records the current MLflow GenAI Prompt Registry index and its
linked subpages used by the `mlflow-prompt-registry` skill. Recheck the links
when the installed MLflow version, backend, or preview status changes.

## Prompt Registry index and lifecycle

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/prompt-registry/ | Prompt Registry concepts, prompt model configuration, formats, caching, and navigation |
| https://mlflow.org/docs/latest/genai/prompt-registry/create-and-edit-prompts/ | Create, edit, version, tag, and commit prompts |
| https://mlflow.org/docs/latest/genai/prompt-registry/manage-prompt-lifecycles-with-aliases/ | Aliases and lifecycle promotion |
| https://mlflow.org/docs/latest/genai/prompt-registry/use-prompts-in-apps/ | Load, format, cache, and use prompts in applications |
| https://mlflow.org/docs/latest/genai/prompt-registry/log-with-model/ | Log prompt dependencies with MLflow Models |
| https://mlflow.org/docs/latest/genai/prompt-registry/evaluate-prompts/ | Evaluate registered prompt versions |

## Prompt behavior and optimization

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/prompt-registry/structured-output/ | Structured-output metadata and application-side validation |
| https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/ | `optimize_prompts`, GEPA, MetaPrompt, custom optimizers, and aggregation |
| https://mlflow.org/docs/latest/genai/prompt-registry/rewrite-prompts/ | Experimental trace-aware prompt rewriting for model migration |

## Interactive development

| Official source | Coverage |
|---|---|
| https://mlflow.org/docs/latest/genai/prompt-registry/prompt-engineering/ | Experimental Gateway-backed Prompt Engineering UI |
| https://mlflow.org/docs/latest/genai/prompt-registry/playground/ | Gateway-backed in-browser prompt/model Playground |
| https://mlflow.org/docs/latest/genai/governance/ai-gateway/ | Gateway governance, endpoints, and provider configuration used by UI/Playground |

## Currentness notes

- Prompt versions are immutable; aliases and model configuration can change,
  so release evidence must record the resolved version and configuration.
- The Prompt Engineering UI and Playground are interactive development surfaces
  and should not replace reproducible evaluation or deployment approval.
- Prompt optimization and rewriting are version-gated and can require a
  configured MLflow AI Gateway/provider endpoint.
- `response_format` documents intent; validate actual provider responses at the
  application boundary.
