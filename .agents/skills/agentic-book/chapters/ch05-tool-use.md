# Chapter 5: Tool Use (Function Calling)

## Core Idea
LLMs are powerful text generators but are fundamentally cut off from the outside world: their knowledge is static (frozen at training time) and they cannot act, compute precisely, or reach live systems. Tool Use — most often implemented as **function calling** — bridges that gap. The model is shown a catalog of external capabilities, each described by name, purpose, parameters, and types. When the user's request calls for something beyond what the model can produce from memory, the model emits a **structured call** (typically a JSON object naming a tool and its arguments). An orchestration layer intercepts that call, executes the real function, and feeds the result — an **observation** — back into the conversation so the model can produce a grounded final answer or decide the next step.

The broader term **tool calling** generalizes the idea: a tool may be a plain function, an API endpoint, a database query, or even a delegation to another specialized agent (e.g., an "analyst agent"). This framing turns the model into an orchestrator across a diverse ecosystem of resources.

## Frameworks Introduced
- **LangChain** — `@tool`/`langchain_tool` decorators to wrap functions; `create_tool_calling_agent` + `AgentExecutor` to bind model, tools, and prompt; requires an `agent_scratchpad` prompt placeholder for intermediate steps.
- **CrewAI** — `@tool` decorator, role/task/crew abstractions, explicit success/failure handling in task descriptions.
- **Google Agent Developer Kit (ADK)** — natively pre-built tools (`google_search`, `built_in_code_execution`, Vertex AI Search `VSearchAgent`), `Runner` + `InMemorySessionService` for session lifecycle, and **Vertex Extensions** (auto-executed by Google, unlike manual function calls).
- Underlying all three: the **native function-calling capabilities** of modern LLMs (Gemini, OpenAI series).

## Key Concepts
1. **Tool definition / schema** — The contract exposed to the model: function name, purpose, parameters with types and descriptions, and (implicitly) the return shape. Rich, unambiguous descriptions are what let the model choose correctly.
2. **LLM decision** — The model judges whether a tool is needed and which one, based on the request and current state.
3. **Structured call generation** — The model produces a JSON object naming the tool and extracted arguments.
4. **Interception & execution** — The framework identifies the tool and runs the real function with the arguments.
5. **Observation** — The authoritative result (or error) returned to the model as context; the ground truth the model reasons from.
6. **Follow-on processing** — The model uses the observation to answer, call another tool, or reflect.
7. **Function calling vs. tool calling** — Function calling is the specific mechanism; tool calling is the expansive pattern that also covers APIs, DB queries, and agent-to-agent delegation.
8. **Side effects** — External changes a tool causes (sending an email, booking, writing). These demand the most caution.
9. **Idempotency** — The property that lets a tool be retried safely without duplicating an effect.
10. **Delegation** — Routing a complex subtask to a dedicated agent/tool rather than handling it inline.
11. **Auto-executed vs. manual execution** — Vertex *Extensions* run automatically under Google's controls, whereas standard function calls require client-side execution.
12. **Pre-built vs. custom tools** — Frameworks ship ready tools (Search, Code Interpreter, enterprise search) and let you wrap your own.

## Mental Models
- **The model proposes; the orchestrator disposes.** The LLM never touches the outside world directly — it only requests. Validation, authorization, and execution all happen in the trusted orchestration layer.
- **Treat model-generated arguments as untrusted input.** A hallucinated parameter is a real-world hazard.
- **A tool is a capability boundary, not a prompt extension.** Each tool is a permissioned action with its own contract.
- **Read vs. write vs. commit.** Retrieving data is low-risk; changing state is high-risk and often needs a preview/approval gate.

## Anti-patterns / Failure Modes
- **Unvalidated arguments** — passing model output straight into a function turns hallucination into an operational incident (bad API calls, wrong targets).
- **Implicit execution / overpowered tools** — letting prose trigger side effects, or giving a tool broad permissions, makes mistakes dangerous.
- **Vague tool descriptions** — if the schema/purpose is unclear, the model picks the wrong tool or refuses to call needed ones.
- **String results instead of structured outcomes** — returning plain strings (or swallowing errors as text) prevents the agent from distinguishing success from failure and recovering.
- **No follow-on loop** — returning the observation without giving the model a chance to react or call another tool wastes the pattern's compositional power.

## Implementation Sketch
```
Define tools (name + purpose + typed params + return/errors)
        │
User request + tool catalog ──▶ LLM decides: call or answer?
        │ (structured call: {tool, arguments})
        ▼
Validate args (schema) + check permissions/policy
        │
        ▼
Execute real function  ──(on failure)──▶ raise structured error
        │
        ▼
Observation (result or structured error) fed back to LLM
        │
        ▼
LLM → final answer, or call another tool, or reflect
```
Illustrative pseudocode (framework-agnostic):
```
tools = catalog_of_schemas()
call = llm.choose_tool(messages, tools)        # structured JSON or None
if call is None:
    return llm.respond(messages)
args = validate(call.arguments, tools[call.name].schema)   # may raise
authorize(call.name, user, args)               # policy / least privilege
try:
    observation = dispatch(call.name, args)    # run real function
except ToolError as e:
    observation = e.to_structured()            # agent can recover
messages.append(tool_result(observation))
return llm.respond(messages)                   # or loop to another call
```
The chapter's concrete examples follow this shape: LangChain's `create_tool_calling_agent` + `AgentExecutor` (with an `agent_scratchpad` placeholder), CrewAI's tool returning a clean typed value or raising `ValueError`, and ADK's `Runner` streaming events and extracting the final response (or code-execution output).

## Worked Example
**Financial analyst (CrewAI).** A `get_stock_price(ticker)` tool returns a `float` for known tickers (e.g., AAPL → 178.15) and **raises a `ValueError`** for unknown ones — deliberately structured output, not a string, so the agent can tell failure from success. The task instructs the agent explicitly: report the price on success, or state clearly that it could not be retrieved on failure. This separates a **read** (lookup) from any hypothetical **write**, keeps the tool least-privileged, and gives the model a clean recovery path. A LangChain analog is a `search_information(query)` tool with a lookup dictionary and a default fallback; an ADK analog is a `calculator` agent using `BuiltInCodeExecutor` to write and run Python for exact math like `(5 + 7) * 3` or 10! — offloading deterministic computation the model shouldn't guess.

## Key Takeaways
1. **Tools extend the model beyond frozen knowledge** — for live data, private data, precise computation, code execution, and real-world actions.
2. **Describe tools well** — clear name, purpose, typed parameters, and return/error shape are what make correct tool selection reliable.
3. **The orchestration layer owns trust** — validate arguments against the schema and enforce authorization outside the model; never trust model output directly.
4. **Return structured results and structured errors** so the agent can distinguish outcomes and recover rather than misreading a string.
5. **Separate read/write/commit** — gate side-effecting operations behind validation, budget limits, and approval.
6. **Prefer built-in tools where possible** (Search, Code Interpreter, enterprise search) and delegate complex subtasks.
7. **Frameworks abstract the loop** — LangChain (`@tool`, `AgentExecutor`), CrewAI (`@tool`, task-level error handling), ADK (pre-built tools, `Runner`, Vertex Extensions).

## Connects To
- **Ch 10**: MCP standardizes discoverable, interoperable tools.
- **Ch 8**: Session services (`InMemorySessionService`) manage the conversation state that tool loops build on.
- **Ch 12**: Tool errors need bounded, structured recovery.
- **Ch 18**: Guardrails govern tool permissions, least privilege, and side-effect safety.
- **Ch 3/4**: Tool use composes with chaining (multi-tool flows), routing, and reflection.
