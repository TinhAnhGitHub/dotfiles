# Automatic Issue Detection and AI Issue Discovery

## Contents

1. Purpose and prerequisites
2. How automatic issue detection works: five stages
3. What is analyzed
4. CLEARS issue categories
5. Running detection
6. Working with detected issues
7. Converting issues into engineering controls
8. Best practices, cost, and privacy
9. AI Issue Discovery via MCP/CLI

## 1. Purpose and prerequisites

Automatic issue detection is for discovering unknown or recurring failure modes across a
batch of traces. It complements, but does not replace, scorers:

- **Scorers** test known criteria repeatedly.
- **Issue detection** proposes and clusters failure modes you may not have encoded yet.

Current upstream docs describe the feature in the MLflow UI. Use a recent MLflow server,
traces with meaningful inputs/outputs/spans, and a configured judge/model endpoint.
Version-check the target deployment; current research places the feature in recent
MLflow 3.x and identifies 3.11.1+ in release material.

## 2. How it works: five stages

The documented analysis pipeline is:

1. **Identify issues from traces** — inspect selected traces against requested issue
   dimensions.
2. **Analyze triage results** — combine per-trace rationales, human feedback, and agent
   execution behavior into richer analyses.
3. **Cluster issues** — group similar analyses and generate issue labels/descriptions.
4. **Annotate traces** — attach issue associations and rationales to affected traces.
5. **Generate a summary** — report dominant issues, severity, root causes, and next steps.

This is an LLM-driven discovery process. Every cluster requires human verification before
it becomes a product requirement, ground truth, alert, or regression test.

## 3. What is analyzed

Issue detection can use:

- request inputs and app outputs;
- tool calls, arguments, results, and failures;
- span sequence and execution flow;
- exceptions, timeouts, and error statuses;
- latency and performance behavior;
- retrieval/context behavior represented in spans;
- trace metadata, tags, sessions, and human feedback.

Detection quality depends on trace quality. If tools are opaque or spans are untyped, the
analysis may identify a symptom without the root cause.

## 4. CLEARS categories

| Category | Detects | Example |
|---|---|---|
| **Correctness** | Hallucination, factual error, unsupported claim | Invented refund exception |
| **Latency** | Slow path, timeout, bottleneck | Repeated retriever calls cause 12 s response |
| **Execution** | Tool/API failure, malformed args, bad control flow | Cancel tool called before lookup |
| **Adherence** | Instruction, policy, format, or role violation | Returns prose instead of required JSON |
| **Relevance** | Off-topic or unhelpful output | Explains billing history instead of duplicate charge |
| **Safety** | Harmful, sensitive, or inappropriate behavior | Requests a password or exposes PII |

Category selection should reflect the app:

- support: relevance, adherence, correctness;
- RAG: correctness, relevance, execution;
- real-time agent: latency, execution;
- content generation: safety, adherence, relevance;
- transaction agent: execution, adherence, safety, correctness.

Start broad during discovery, then use targeted runs for known high-risk dimensions.

## 5. Running detection

### UI workflow

1. Open an experiment view containing traces.
2. Select all traces or a representative subset.
3. Start **Detect Issues**.
4. Select CLEARS categories.
5. Select/configure the analysis model or AI Gateway endpoint.
6. Run the asynchronous analysis and monitor progress.
7. Review summary, severity distribution, clusters, and affected traces.

Use stratified data rather than only the latest or worst traces. For multi-turn apps,
preserve sessions so the analyzer sees conversation context.

### Selection pattern

```text
random normal sample
+ negative feedback sample
+ error/timeout sample
+ high latency/cost sample
+ new app/prompt/tool version sample
+ high-risk cohort sample
```

This reduces sampling bias and makes prevalence estimates more credible.

## 6. Working with detected issues

An issue normally includes:

- category;
- generated description;
- severity;
- affected-trace count;
- trace links and per-trace rationale;
- suggested root cause or next step.

Lifecycle statuses documented in the workflow:

- **Pending:** needs review.
- **Resolved:** validated, fixed, and ideally verified.
- **Rejected:** false positive, intentional behavior, duplicate, or out of scope.

Triage process:

1. Inspect multiple traces in the cluster.
2. Confirm the issue is coherent, not merely similar wording.
3. Estimate prevalence with an unbiased sample.
4. Correct category/severity/description.
5. Separate product failure from evaluator/tracing failure.
6. Assign owner and remediation type.
7. Create expectations and regression cases.
8. Verify the fix on historical affected traces and the broader dataset.
9. Mark resolved only after monitoring confirms recurrence is controlled.

## 7. Convert issues into engineering controls

| Validated issue | Durable control |
|---|---|
| Wrong factual answer | Expected facts + `Correctness` + source/retrieval fix |
| Unsupported RAG answer | Retriever spans + groundedness + document-recall scorer |
| Wrong tool mutation | Tool precondition code scorer + focused regression test |
| Repeated inefficient tools | Tool efficiency judge + latency/cost metric |
| Format violation | Deterministic schema scorer |
| Policy or tone violation | Guidelines/custom judge aligned to human labels |
| User frustration across turns | Session IDs + `UserFrustration` monitoring |
| Novel issue cluster | Add tagged dataset slice and periodic prevalence metric |

Issue discovery is complete only when the issue becomes observable and testable.

## 8. Best practices, cost, and privacy

### Best practices

- Analyze representative data across time, cohorts, versions, and intents.
- Verify every model-generated issue against source traces.
- Use descriptive domain-specific names after review.
- Run periodically and after major prompt/model/tool changes.
- Track issue recurrence by app version.
- Keep detected-issue severity separate from business impact until a human confirms it.

### Cost

Cost scales with number/size of traces, categories, and analysis model. Current docs
publish example ranges rather than guarantees. Use budgets, representative subsets, and
incremental analysis. Never encode old benchmark prices as a current forecast.

### Privacy

- Redact PII before trace export where required.
- Confirm what trace content is sent to the analysis model.
- Use approved Gateway/provider endpoints.
- Limit reviewer access to affected traces.
- Treat generated reports as sensitive if they quote user content.

### Known-version caution

Recent issue reports have involved custom OpenAI-compatible base URLs. Check the installed
MLflow release notes/issues if using a nonstandard OpenAI endpoint.

## 9. AI Issue Discovery via MCP/CLI

MLflow separately documents an AI-assisted experiment analysis command:

```bash
mlflow ai-commands run genai/analyze_experiment
```

and an MCP command such as `/analyze-experiment` when the MLflow MCP server is connected
to a supported coding agent.

Use this for hypothesis-driven investigation and a generated report. It is not the same
as the UI's persisted issue-management workflow. Require the same human verification and
conversion into datasets/scorers/tests.

## Sources

- https://mlflow.org/docs/latest/genai/eval-monitor/ai-insights/detect-issues/
- https://mlflow.org/docs/latest/genai/eval-monitor/ai-insights/ai-issue-discovery/
- https://github.com/mlflow/mlflow/issues/23648
