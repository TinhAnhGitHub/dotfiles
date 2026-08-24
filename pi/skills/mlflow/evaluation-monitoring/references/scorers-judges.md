# Scorers and LLM-as-a-Judge

## Contents

1. Selection strategy
2. Built-in judge inventory
3. Guidelines judges
4. Custom LLM judges
5. Code-based scorers
6. Trace-aware patterns
7. Aggregation and pass/fail
8. Alignment and versioning
9. Third-party scorers
10. Cost, reliability, and best practices

## 1. Selection strategy

Use the simplest reliable scorer for each criterion:

| Need | Prefer |
|---|---|
| Exact schema, regex, threshold, tool arg, latency, policy rule | Code-based scorer |
| General correctness/relevance/fluency | Built-in judge |
| Simple natural-language rule | `Guidelines` or `ExpectationsGuidelines` |
| Domain-specific categorical/numeric assessment | `make_judge` |
| Retrieval/tool/routing trajectory | Trace-aware built-in or custom scorer |
| Conversation-wide behavior | Multi-turn judge on session traces |

Combine scorers rather than asking one judge to decide every quality dimension.

## 2. Built-in judge inventory

Import built-ins from `mlflow.genai.scorers`. Availability can differ between OSS and
Databricks; `Safety` and `RetrievalRelevance` are marked Databricks-only in current OSS
docs.

### Response quality

| Judge | Criterion | Ground truth | Trace/session | Notes |
|---|---|---:|---:|---|
| `RelevanceToQuery` | Response directly addresses input | No | No | Useful baseline semantic judge |
| `Correctness` | Expected facts/response are supported | Yes | No | Prefer `expected_facts` for flexible truth |
| `Completeness` | All questions in one prompt addressed | No | No | Experimental |
| `Fluency` | Grammar and natural flow | No | No | Not a factuality measure |
| `Safety` | Avoids harmful/toxic output | No | No | Current OSS docs mark Databricks-only |
| `Equivalence` | Semantically equivalent to expected output | Yes | No | Useful for reference-answer tasks |
| `Summarization` | Faithful, complete, concise, clear summary | No | No | Use source content in inputs/trace |
| `Guidelines` | Global custom rules | Criterion supplied | No | Pass/fail LLM judge |
| `ExpectationsGuidelines` | Per-record rules | `expectations.guidelines` | No | Good for heterogeneous cases |

### RAG

| Judge | Criterion | Ground truth | Requirement |
|---|---|---:|---|
| `RetrievalRelevance` | Retrieved documents are relevant | No | Retriever spans; Databricks-only in current OSS docs |
| `RetrievalGroundedness` | Answer is supported by retrieved information | No | Retriever spans |
| `RetrievalSufficiency` | Retrieved context contains enough to answer | Yes | Retriever spans + expected facts/response |

RAG judges need correctly typed `RETRIEVER` spans and useful document outputs. A final
text answer alone cannot support these checks.

### Tool calls

| Judge | Criterion | Requirement | Status |
|---|---|---|---|
| `ToolCallCorrectness` | Tool choice and arguments are appropriate | `TOOL` spans; optional expected calls | Experimental |
| `ToolCallEfficiency` | Tool usage has no unnecessary/redundant calls | `TOOL` spans | Experimental |

Check the installed constructor for options such as exact matching or ordering before
using them; experimental signatures can change.

### Multi-turn

| Judge | Criterion |
|---|---|
| `ConversationCompleteness` | All user questions across the session are handled |
| `ConversationalGuidelines` | Conversation-wide rules are followed |
| `ConversationalRoleAdherence` | Assistant maintains its assigned role |
| `ConversationalSafety` | Conversation remains safe |
| `ConversationalToolCallEfficiency` | Tools are used efficiently across turns |
| `KnowledgeRetention` | Earlier user facts are retained correctly |
| `UserFrustration` | Frustration appears and/or is resolved |

Multi-turn judges are experimental, require session IDs, and current built-in docs say
they score pre-collected traces rather than a normal single-turn `predict_fn`. The fuller
conversation simulation framework arrived later than the first judge classes; use MLflow
3.10+ for the complete documented workflow.

### Minimal examples

```python
from mlflow.genai.scorers import (
    Correctness,
    RelevanceToQuery,
    RetrievalGroundedness,
    ToolCallEfficiency,
)

scorers = [
    Correctness(model="openai:/<judge-model>"),
    RelevanceToQuery(model="openai:/<judge-model>"),
    RetrievalGroundedness(model="openai:/<judge-model>"),
    ToolCallEfficiency(model="openai:/<judge-model>"),
]
```

Do not hard-code a default judge model. Pin one explicitly or use
`MLFLOW_GENAI_JUDGE_DEFAULT_MODEL`.

For supported built-ins, `inference_params` can tune provider parameters such as
temperature or max tokens:

```python
Correctness(
    model="openai:/<judge-model>",
    inference_params={"temperature": 0.0, "max_tokens": 500},
)
```

## 3. Guidelines judges

### Global criterion

```python
from mlflow.genai.scorers import Guidelines

no_secrets = Guidelines(
    name="no_secret_request",
    guidelines=[
        "The response must not ask for passwords, tokens, or authentication secrets.",
        "The response must use approved identity-verification steps.",
    ],
    model="openai:/<judge-model>",
)
```

Write criteria as observable requirements. Split unrelated requirements into separate
judges so a failure has one actionable meaning.

### Per-row criterion

```python
from mlflow.genai.scorers import ExpectationsGuidelines

data = [
    {
        "inputs": {"question": "..."},
        "outputs": "...",
        "expectations": {
            "guidelines": [
                "Mention the 30-day refund window",
                "Do not promise an exception",
            ]
        },
    }
]

mlflow.genai.evaluate(data=data, scorers=[ExpectationsGuidelines()])
```

## 4. Custom LLM judges

Use `make_judge` when built-ins cannot express the domain criterion.

```python
from typing import Literal
from mlflow.genai.judges import make_judge

resolution_judge = make_judge(
    name="issue_resolution",
    instructions="""
Assess whether the response resolves the request.

Request: {{ inputs }}
Response: {{ outputs }}
Expected behavior, if provided: {{ expectations }}

Return fully_resolved only when the response gives an actionable and policy-compliant
resolution. Return needs_follow_up when required information or action remains.
""",
    feedback_value_type=Literal[
        "fully_resolved",
        "partially_resolved",
        "needs_follow_up",
    ],
    model="openai:/<judge-model>",
)
```

Documented template variables include:

- `{{ inputs }}`
- `{{ outputs }}`
- `{{ expectations }}`
- `{{ trace }}` for full execution exploration
- `{{ conversation }}` for multi-turn sessions

Trace-based judges require an explicit capable model and can cost more because the judge
may inspect multiple spans. Conversation templates have combination restrictions; verify
the current docs before mixing variables.

Judge instructions should include:

1. one criterion;
2. precise label definitions;
3. required evidence;
4. how to handle missing information;
5. counterexamples/boundaries when ambiguity is high;
6. a rationale requirement.

## 5. Code-based scorers

### Decorator pattern

```python
from mlflow.entities import Feedback
from mlflow.genai.scorers import scorer

@scorer
def response_schema(outputs: dict) -> Feedback:
    required = {"answer", "citations"}
    missing = sorted(required - set(outputs))
    return Feedback(
        value=not missing,
        rationale="All fields present" if not missing else f"Missing: {missing}",
    )
```

Supported keyword-only scorer inputs are `inputs`, `outputs`, `expectations`, and
`trace`; declare only what is needed. Supported outputs include `bool`, `int`, `float`,
`str`, `Feedback`, and `list[Feedback]`.

### Multiple metrics

```python
@scorer
def operational_metrics(trace):
    latency_ms = trace.info.execution_duration
    tool_errors = sum(
        span.status.status_code == "ERROR"
        for span in trace.search_spans(span_type="TOOL")
    )
    return [
        Feedback(name="latency_ms", value=latency_ms),
        Feedback(name="tool_error_count", value=tool_errors),
    ]
```

Each returned feedback item must have a distinct name.

### Stateful class

```python
from mlflow.genai.scorers import Scorer

class MaxLength(Scorer):
    name: str = "within_length"
    max_words: int = 100

    def __call__(self, outputs: str) -> Feedback:
        count = len(outputs.split())
        return Feedback(
            value=count <= self.max_words,
            rationale=f"{count} words; limit is {self.max_words}",
        )
```

Use instance fields, not mutable class-level state. Prefer the decorator for most cases.

### Error behavior

Let exceptions propagate when a scorer cannot evaluate a record; MLflow records an error
feedback and continues. Do not convert evaluator errors into a passing score.

OSS automatic evaluation supports only LLM judges, not code-based scorers. Databricks
managed production monitoring can support self-contained `@scorer` functions under
notebook serialization constraints; class-based scorers remain unsupported there.

## 6. Trace-aware patterns

### Retrieval recall

```python
from mlflow.entities import Feedback, SpanType, Trace

@scorer
def document_recall(trace: Trace, expectations: dict) -> Feedback:
    expected = set(expectations["expected_retrieved_context"])
    spans = trace.search_spans(span_type=SpanType.RETRIEVER)
    actual = {
        doc["doc_uri"]
        for span in spans
        for doc in (span.outputs or [])
        if "doc_uri" in doc
    }
    recall = len(actual & expected) / len(expected) if expected else 1.0
    return Feedback(value=recall, rationale=f"actual={sorted(actual)}")
```

### Tool trajectory

```python
@scorer
def tool_trajectory(trace: Trace, expectations: dict) -> Feedback:
    actual = [s.name for s in trace.search_spans(span_type=SpanType.TOOL)]
    expected = expectations["tool_call_trajectory"]
    return Feedback(
        value=actual == expected,
        rationale=f"expected={expected}; actual={actual}",
    )
```

Only require an exact trajectory when the order is a true business invariant. Agents may
have multiple valid plans.

### Agent routing

```python
@scorer
def routing(trace: Trace, expectations: dict) -> Feedback:
    actual = [s.name for s in trace.search_spans(span_type=SpanType.AGENT)]
    expected = expectations["expected_agents"]
    return Feedback(value=actual == expected, rationale=f"actual={actual}")
```

Trace-aware scorers require actual trace objects; current docs warn that they cannot run
against an ordinary static pandas answer sheet.

## 7. Aggregation and pass/fail

The scorer decorator supports configuration such as aggregation and `pass_if` in newer
MLflow versions. Inspect the installed signature.

Design principles:

- Numeric metrics need an explicit direction and release threshold.
- Binary/categorical judges need a clearly defined pass set.
- Report mean plus pass rate, distribution, and critical-slice metrics.
- Never gate only on an average when one catastrophic failure matters.
- Define baseline-comparison tolerances before seeing candidate results.

## 8. Alignment and versioning

### Alignment loop

1. Draft the judge.
2. Run it on representative traces.
3. Collect human labels with the exact same assessment name.
4. Split alignment and held-out validation sets.
5. Align with a documented optimizer such as MemAlign, SIMBA, or GEPA.
6. Compare agreement, false positives/negatives, and per-slice behavior.
7. Register the aligned judge as a new version.
8. Pin that version in regression and monitoring workflows.

```python
from mlflow.genai.judges.optimizers import MemAlignOptimizer

aligned = judge.align(
    alignment_traces,
    MemAlignOptimizer(reflection_lm="anthropic:/<reflection-model>"),
)
registered = aligned.register(experiment_id=experiment_id)
```

Registration/versioning support differs by scorer type and environment. Current docs
support built-in and `make_judge` judge registration. Guidelines work in automatic
evaluation/Databricks monitoring examples. Code scorer registration is Databricks-managed
and constrained.

### Calibration metrics

On a held-out human-labeled set, report:

- confusion matrix and per-class precision/recall/F1;
- false-positive/false-negative rates for critical classes;
- simple agreement and Cohen's kappa for two raters;
- weighted kappa for ordinal labels;
- disagreement by intent, language, risk, and annotator.

```python
from sklearn.metrics import classification_report, cohen_kappa_score, confusion_matrix

print(confusion_matrix(human_labels, judge_labels))
print(classification_report(human_labels, judge_labels, zero_division=0))
print("kappa=", cohen_kappa_score(human_labels, judge_labels))
```

Use adjudicated human labels as the reference and report human-human agreement alongside
judge-human agreement; a judge cannot reliably exceed an ambiguous labeling guide.

## 9. Third-party scorers

MLflow documents adapters/integrations for:

- DeepEval
- RAGAS
- Arize Phoenix
- TruLens
- Guardrails AI
- Google ADK

Databricks documents the following notable adapters; verify imports and optional package
versions on the individual page:

| Adapter | Notable scorer families |
|---|---|
| DeepEval | Answer relevancy, faithfulness, contextual recall/precision/relevancy, task completion, tool/argument correctness, step efficiency, plan adherence/quality, conversation quality, bias/toxicity/PII leakage, exact/pattern match |
| RAGAS | Context precision/recall/utilization, answer relevance/faithfulness/accuracy, topic adherence, tool-call accuracy/F1, agent-goal accuracy, factual/semantic comparison, BLEU/ROUGE/CHRF/exact match, rubrics |
| Arize Phoenix | Hallucination, relevance, toxicity, QA, summarization |
| TruLens | Groundedness, context/answer relevance, coherence, logical consistency, execution efficiency, plan adherence/quality, tool selection/calling |
| Guardrails AI | Toxic language, NSFW, jailbreak, PII, secrets, gibberish; useful deterministic/rule-based checks without judge calls |
| Google ADK | Adapter for Google ADK evaluation workflows; verify its current scorer catalog and optional dependency on the upstream page |

Databricks pages expose wrappers under `mlflow.genai.scorers.<provider>` and commonly
support `get_scorer()`. These names evolve with optional upstream dependencies, so consult
the page/API at implementation time.

Use them when their specialized metric is mature and validated for the task. Keep the
same quality checks as native scorers: input schema, trace assumptions, provider cost,
version compatibility, deterministic behavior, and whether production execution is
supported.

## 10. Cost, reliability, and best practices

- Pin judge model and judge version in CI.
- Prefer deterministic checks for deterministic requirements.
- Calibrate judges to human labels; report disagreement.
- Sample and cache thoughtfully, but do not leak prior answers into independent tests.
- Separate criterion definition from the candidate app prompt.
- Treat rationale as evidence for review, not proof.
- Track judge token/cost and latency separately from app cost.
- Use stronger models during judge development and a validated cost-effective model at
  scale.
- Redact sensitive trace content before external judge calls.
- Revalidate after model/provider changes.

## Sources

- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/guidelines/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/custom-judges/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/alignment/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/versioning/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/third-party/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/third-party/google-adk/
