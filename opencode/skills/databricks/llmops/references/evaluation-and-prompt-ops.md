# Evaluation and prompt operations

Evaluation is the quality control plane for LLMOps. Prompt, model, tool,
retrieval, memory, and guardrail changes are all candidate changes until data
shows that they are safe and useful.

## Build the evaluation set

Start with 10–20 high-quality examples that domain experts can agree on, then
expand from production. Each case should identify:

```yaml
id: case-001
inputs: {question: "..."}
expectations:
  expected_facts: ["..."]
  required_tools: ["..." ]
  forbidden_behaviors: ["..." ]
  reference_answer: "..."
  slice: account-recovery
  risk: high
  source: human|production|synthetic
```

Include positive and negative cases. Test when a tool/retrieval step should be
used and when it should not, expected refusal behavior, incomplete context,
prompt injection, malformed inputs, long conversations, and service failures.
Keep a dataset digest and snapshot/version with every evaluation.

## Choose scorers by failure mode

| Layer | Example checks | Scope |
|---|---|---|
| Contract | JSON/schema, citations, required fields, Pydantic validation | every case/request |
| Safety | PII/secrets, unsafe content, jailbreak/prompt injection | every case/request where possible |
| Tooling | tool name/arguments, call order, redundant calls, permission boundaries | trace-aware |
| Retrieval | Recall@K, Precision@K, F1@K, relevance, sufficiency, groundedness | retriever and trace |
| Response | correctness, completeness, relevance, tone, role adherence | LLM judge + human calibration |
| Operations | latency, tokens, retries, errors, cost, output length | every request |

Use deterministic code-based scorers first because they are cheap, reproducible,
and good at gates. Use model-based judges for nuanced behavior and calibrate
them with human assessments. Use human review for requirements that experts
must define, high-risk cases, judge alignment, and sampled production traces.

## Candidate comparison

Keep these constant when comparing candidates:

- evaluation dataset and slice definitions;
- scorer implementation and judge model/version/config;
- sampling policy and tool/resource permissions;
- timeout/retry/traffic conditions;
- baseline release and measurement window.

Change one primary factor at a time where practical. Report distributions and
slice-level results, not only averages. A candidate is not promotable if it
improves the aggregate while regressing a critical slice or safety gate.

## Pre-deploy and production evaluation

Use two tiers in production:

1. Tier 1: deterministic format, policy, latency, token, tool, and error checks
   on all eligible traces.
2. Tier 2: sampled LLM-based correctness, groundedness, relevance, tone, and
   conversation checks. Tune the sample rate to risk, traffic, cost, and judge
   latency; 5–20% is a starting range, not a universal rule.

Stratify sampling for new releases, low-confidence outputs, safety violations,
high-cost requests, empty retrieval, and user complaints. Log feedback back to
the trace, and curate confirmed failures into the regression set.

## Judge alignment

Do not treat an LLM judge as ground truth. Collect human pass/fail or graded
feedback on representative traces, inspect disagreement, refine the rubric, and
align the judge when supported. Track the judge model, instructions, rubric,
examples, and alignment dataset as versioned release components.

## Prompt lifecycle

Store prompts as typed, reviewable artifacts. Recommended metadata:

```yaml
name: support-agent-system
version: 12
owner: support-ai
purpose: answer account recovery questions
model_compatibility: <provider/model families>
input_schema: <schema/version>
output_schema: <schema/version>
template_digest: sha256:<digest>
changelog: "Added explicit escalation when prior steps failed"
eval_dataset_digest: sha256:<digest>
```

Prompt Registry can provide immutable prompt versions and optimization
workflows, while Git remains the right place for surrounding application logic,
review, and reproducible environment configuration. See
[`prompt-registry.md`](prompt-registry.md) for the subsection map and current API
details. Use both only when their ownership boundaries are explicit.

Every prompt version change should:

1. show a human-readable diff and reason;
2. validate template variables and output contract;
3. run the relevant regression/safety/slice suite;
4. record model/provider and generation settings;
5. create a new app/release identity even if the packaged code is unchanged;
6. preserve the previous prompt and rollback target.

Prompt optimization is analogous to hyperparameter tuning. Optimize against a
fixed dataset and scorer, avoid optimizing on the same examples used for the
final claim, and record the optimizer, candidate prompts, and selected result.

## RAG/context evaluation

Version and evaluate context assembly separately from response generation:

- source table/document snapshot and data-quality result;
- parser and chunking configuration;
- embedding model/endpoint and dimension;
- index name/type/sync commit;
- query type, filters, number of results, score threshold, reranker;
- query rewrite/adaptive retrieval policy;
- context window/truncation and memory summarization policy.

Test retrieval Recall@K and Precision@K where labels exist, then test answer
groundedness, citation correctness, and sufficiency using the actual trace.
