# Chapter 1: Prompt Chaining

## Core Idea
Prompt chaining (also called the **Pipeline pattern**) is a divide-and-conquer strategy for
complex tasks. Instead of asking one LLM to solve a multifaceted problem in a single
monolithic step, you decompose it into a sequence of smaller, focused sub-problems. Each
sub-problem gets its own purpose-built prompt, and the output of one step is fed as input to
the next. This creates a dependency chain where earlier results guide later processing, so the
model builds on validated work rather than restarting from scratch at every step.

Chaining also inserts natural seams for integrating external knowledge and tools: at any step
the model can call an API, query a database, or invoke a deterministic tool, turning an isolated
model into a component of a larger system. Because each step is modular, the whole pipeline is
easier to understand, debug, and optimize — and it forms the backbone of multi-step agentic
systems that plan, reason, and act.

## Frameworks Introduced
- **Prompt Chaining / Pipeline**: Decompose a task with clear dependencies (extract → analyze
  → draft). Define one prompt per stage, pass structured output between stages, and validate
  each handoff.
- **LangChain / LangGraph**: LangChain gives linear-sequence abstractions (and the LCEL
  expression language for composing chains); LangGraph extends this to stateful, cyclical
  graphs for richer agent behavior.
- **Crew AI** and the **Google Agent Development Kit (ADK)**: Structured environments for
  building and executing multi-step, role-based sequences.
- **Context Engineering**: The broader discipline of assembling the full informational
  environment (system prompt, retrieved data, tool outputs, implicit context) that a chain's
  steps consume.

## Key Concepts
- **Stage**: A single focused model call or deterministic processing step within the chain.
- **Handoff**: The data contract passed from one stage to the next; reliability depends on its
  integrity.
- **Structured output**: Enforcing a machine-readable format (JSON/XML) between stages so the
  next prompt can parse and insert data unambiguously.
- **Per-stage roles**: Assigning a distinct role to each prompt (e.g., "Market Analyst" →
  "Trade Analyst" → "Expert Documentation Writer") sharpens focus and accuracy.
- **Error propagation**: An early mistake amplifies downstream, poisoning later stages.
- **Instruction neglect**: A monolithic prompt causes requirements to be silently dropped.
- **Contextual drift**: The model loses track of the original context inside a huge prompt.
- **Long-context strain**: Overloading the context window starves the model of usable signal.
- **Hallucination**: Higher cognitive load raises the chance of fabricated detail.
- **Deterministic logic between calls**: Validation, conditional branching, and data
  normalization inserted by the execution framework, not the model.
- **Parallel-plus-sequential hybrid**: Independent data gathering runs concurrently; dependent
  synthesis/refinement steps chain sequentially.
- **Conversation state**: Each turn is built as a new prompt that folds in accumulated history
  and extracted entities.

## Mental Models
Think of a chain as a **typed data pipeline, not a conversation**: each function performs one
operation before passing its result on. Use a **chain** when steps are strictly ordered; reach
for a **graph** when you need branching paths or loops. Picture the context as an engineered
environment — the richer and better-structured the information handed to each step, the higher
the output quality.

## Anti-patterns / Failure Modes
- **Monolithic prompt**: One giant prompt overloads attention, causing instruction neglect,
  contextual drift, and hallucination, and makes failures hard to localize.
- **Unstructured handoff**: Free-form output drifts in format, silently breaking the next
  stage's parsing.
- **Unbounded chain**: No stop condition or validation means runaway token spend.
- **Validation skipping**: Feeding raw, unverified extraction into later stages guarantees
  error propagation.
- **Doing math in-model**: LLMs are unreliable at precise arithmetic; a step that should call an
  external calculator instead.

## Implementation Sketch
```
input
  → extract(fields/schema)
  → validate(required fields + format)   # deterministic check
  → [normalize text, e.g. "one thousand and fifty" → 1050]
  → [tool call for arithmetic if needed]
  → transform → JSON
  → synthesize/draft
  → final review/check
```
Insert deterministic gates between model calls for validation and conditional re-prompting
(e.g., if fields are missing/malformed, spawn a targeted follow-up prompt rather than
retrying blindly).

## Worked Example
**Market report pipeline.** 1) Summarize key findings from the report. 2) Using only that
summary, identify the top three trends and extract supporting data points, emitted as JSON:
```json
{
  "trends": [
    {
      "trend_name": "AI-Powered Personalization",
      "supporting_data": "73% of consumers prefer brands that use personal data to make shopping more relevant."
    }
  ]
}
```
3) Draft a concise email to marketing that lays out the trends and their data. Each stage only
sees its validated input — the email stage never re-reads the raw report.

**OCR-to-structured invoice** (hybrid variant): extract text from the document image, normalize
values, delegate any required calculation to an external calculator tool, then assemble the
validated structured record. Independent extractions across many documents can run in parallel;
collation → synthesis → review then chain sequentially.

## Key Takeaways
1. Break complex tasks into focused, ordered stages — give each stage one job.
2. Pass explicit structured output (JSON/XML) between stages as the handoff contract.
3. Insert deterministic gates: validate required fields/format, normalize data, and call
   external tools (like calculators) for exact operations.
4. Use per-stage roles and bounded prompts to reduce cognitive load and cut instruction
   neglect, drift, and hallucination.
5. Combine parallel data gathering with sequential synthesis/refinement when a task has both
   independent and dependent steps.
6. Prefer a chain over a single prompt whenever reliability, debuggability, and tool
   integration matter.
7. Treat context as an engineered artifact — build pipelines that fetch, transform, and feed
   the right information to each step, using tuning/optimization tools (e.g., Vertex Prompt
   Optimizer) to refine prompts and system instructions at scale.

## Connects To
- **Ch 2 (Routing)**: Chooses which chain or branch to run for a given input.
- **Ch 4 (Reflection)**: Wraps a chain's final output with a review/refinement loop.
- **Ch 12 (Recovery)**: Handles failed or malformed stages, retries, and error propagation.
- **Context Engineering**: The discipline that supplies each stage with rich, well-formed
  context; optimizers close the feedback loop that improves context quality over time.
