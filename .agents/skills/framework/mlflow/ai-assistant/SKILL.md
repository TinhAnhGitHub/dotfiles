---
name: ai-assistant
description: >
  MLflow AI Assistant, the beta local MLflow UI experience backed by a coding
  agent. Use whenever a user asks about the Assistant panel, setup wizard,
  trace/evaluation analysis, prompt improvement, permissions, supported coding
  agents, or local project changes made through MLflow Assistant. Load the parent
  `mlflow` skill first.
compatibility: Beta; current docs describe local MLflow tracking servers and full Claude Code support, with other coding agents emerging
metadata:
  version: "0.1.0"
  docs-reviewed: "2026-08-30"
---

# MLflow AI Assistant

MLflow AI Assistant is a coding-agent experience embedded in the MLflow UI. It can use the local
codebase and MLflow data to help set up tracing/evaluation/versioning, debug traces, analyze
experiment data, and improve prompts. It is not a hosted model endpoint or an authorization
replacement. Current documentation describes it as beta and available for a local MLflow tracking
server; remote tracking-server support is still evolving.

## Mandatory preflight

1. Confirm a local MLflow Tracking Server and an experiment page; the Assistant currently expects
   the local UI flow and an active experiment.
2. Identify the coding-agent backend and its own account/subscription. MLflow provides the
   integration/knowledge; the coding agent supplies model execution.
3. Decide whether the assistant may execute MLflow CLI commands, read MLflow docs, edit project
   code, or receive full access. Start with the least privilege needed.
4. Classify local code, trace data, prompts, tool arguments, and provider credentials before
   granting access or sending content to the coding agent.
5. Load `mcp-server` for programmatic MLflow data access and `tracing-observability` or
   `evaluation-monitoring` for the actual technical workflow.

## Setup

```bash
mlflow server --port 5000
```

Then:

1. Open the MLflow UI and an experiment page.
2. Open the Assistant tab/panel and run the setup wizard.
3. Authenticate/configure the selected coding-agent backend.
4. Set permissions in the Assistant settings and the coding agent's own project settings.
5. Ask it to inspect the project first; review proposed file changes, tracking destinations,
   dependencies, and data access before accepting them.

The tracing quickstart also documents:

```bash
uvx mlflow@latest agent setup
```

Run it from the project's Git repository and review the generated tracing/skill changes before
committing. Pin the resulting MLflow/dependencies for reproducible development and CI.

## Permission policy

| Permission | Use | Default posture |
|---|---|---|
| Execute MLflow CLI | Fetch traces, runs, and experiment data | Grant only in a safe workspace; required for useful MLflow analysis |
| Read MLflow docs | Keep recommendations current | Grant when current API guidance is needed |
| Edit project code | Add tracing/evaluation/versioning or apply fixes | Require reviewable Git changes and a clean branch |
| Full access/bypass permissions | Unrestricted agent operations | Avoid by default; use only in an isolated, disposable environment |

The Assistant's permission controls do not remove provider, filesystem, tracking-server, or Git
risks. Keep secrets outside source/traces, use a separate development experiment, and review all
commands and diffs that can mutate data or code.

## Useful workflows

- **Instrument:** identify the application boundary, add auto/manual tracing, set experiment and
  session/user context, then run one local trace.
- **Debug:** search a narrow trace slice, inspect spans/errors/latency/tool calls, form a hypothesis,
  and validate it against the code and version metadata.
- **Evaluate:** curate expectations from verified failures, add a dataset/scorer, and run an
  explicit `mlflow.genai.evaluate()` workflow.
- **Improve prompts:** compare prompt versions or use optimization after creating a holdout and
  pinning the judge/model; review generated prompt changes as code/release artifacts.
- **Version:** record Git/app/prompt/model/tool identity before comparing or deploying.

Treat assistant output as a proposal. Human-review generated expectations, issue diagnoses,
prompt rewrites, code changes, and any destructive trace/assessment action.

## Reference router

| Need | Read |
|---|---|
| Current Assistant behavior, beta limits, setup, and permission settings | [`references/source-ledger.md`](references/source-ledger.md) |
| Trace data access through an MCP client | [`../mcp-server/SKILL.md`](../mcp-server/SKILL.md) |
| Automatic setup and app instrumentation | [`../tracing-observability/SKILL.md`](../tracing-observability/SKILL.md) |

## Quality bar

Assistant guidance must state the beta/local limitation, backend identity, permission scope, data
privacy assumptions, review boundary, and the MLflow skill that performs the resulting technical
change. Never imply that enabling Assistant grants remote-server access or that generated analysis
is ground truth.

## Related skills

- `mcp-server` for the MLflow trace-management MCP server.
- `tracing-observability` for instrumentation and trace operations.
- `evaluation-monitoring` for evaluation-driven development.
- `prompt-registry` for prompt versions, optimization, and Playground.
- `version-tracking` for Git/LoggedModel app identity.
