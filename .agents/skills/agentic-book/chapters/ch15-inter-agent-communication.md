# Chapter 15: Inter-Agent Communication (A2A)

## Core Idea
Individual agents struggle with complex, multi-faceted problems even when individually capable. The blocker is not intelligence but the lack of a common language: agents built on different frameworks cannot easily coordinate, delegate, or share information. Inter-Agent Communication (A2A) is an open, HTTP-based protocol that solves this by letting diverse agents—built with Google ADK, LangGraph, CrewAI, Azure AI Foundry, AG2, and others—discover one another, delegate tasks, and exchange results interoperably. Its identity artifact is the **Agent Card**, and its unit of work is the **asynchronous task**. A2A is backed by a broad coalition (Atlassian, Box, LangChain, MongoDB, Salesforce, SAP, ServiceNow, and Microsoft's planned Azure AI Foundry/Copilot Studio integration) and is open source.

## Frameworks Introduced
- **Google A2A protocol**: an open, JSON-RPC 2.0-over-HTTP(S) standard for agent-to-agent collaboration.
- **Agent Card**: a JSON identity/capability document enabling discovery and interaction.
- **Google ADK integration**: `AgentCard`, `AgentSkill`, `ADKAgentExecutor`, `DefaultRequestHandler`, and `A2AStarletteApplication` let an ADK agent be exposed as an A2A server.
- **Interaction mechanisms**: synchronous request/response, asynchronous polling, Server-Sent Events (SSE) streaming, and push notifications (webhooks).

## Key Concepts
1. **Core Actors** — three entities: the **User** (initiates requests), the **A2A Client** (agent/app acting on the user's behalf), and the **A2A Server** (a remote agent exposing an HTTP endpoint). The server is *opaque*: the client need not understand its internals.
2. **Agent Card** — the agent's digital identity: name, description, endpoint URL, version, capabilities (streaming, push notifications, state transition history), authentication schemes, default input/output modes, and a list of **skills** (each with an id, description, input/output modes, example prompts, and tags).
3. **Agent Discovery** — finding Agent Cards via **Well-Known URI** (`/.well-known/agent.json`), **Curated Registries** (centralized enterprise catalogs), or **Direct Configuration** (embedded/private sharing). Endpoints should be secured with access control, mTLS, or network restrictions.
4. **Tasks** — the fundamental unit of work for long-running processes. Each task has a unique id and moves through states (submitted, working, completed, etc.), enabling parallel processing.
5. **Messages** — communication payloads with **attributes** (key-value metadata like priority or creation time) and one or more **parts** (text, files, or structured JSON).
6. **Artifacts** — the tangible outputs of a task, composed of parts and streamable incrementally.
7. **Context** — a server-generated `contextId` groups related tasks and preserves continuity across turns.
8. **Interaction mechanisms** — **Synchronous** (sendTask, single complete reply), **Asynchronous polling** (server acks with "working" + task id; client polls), **SSE streaming** (sendTaskSubscribe, persistent one-way server-to-client updates), and **Push notifications/webhooks** (server pings a registered URL on major status changes).
9. **Modality-agnostic transport** — these patterns work for text as well as audio and video.
10. **Security** — mutual TLS (mTLS), comprehensive audit logs, Agent Card authentication declarations, and credential handling via OAuth 2.0 tokens or API keys passed in HTTP headers (never in URLs or bodies).
11. **`input-required` state** — lets a server ask the client for more information mid-task, preserving context for multi-turn work.
12. **JSON-RPC 2.0** — the payload protocol for all A2A communication over HTTP(S).

## Mental Models
- **Another agent is an external service, not a trusted subroutine.** It is opaque, potentially untrusted, and may fail or return poor results—so validate its outputs like tool outputs.
- **Tasks are stateful, not fire-and-forget.** A task is a lifecycle you own accountability for; track its state, timeouts, and ownership.
- **A2A coordinates agents; MCP coordinates model access to tools and data.** A2A is the inter-agent (agent-to-agent) layer; MCP is the intra-agent (client-to-tool/resource) layer. They complement each other.
- **Discovery before delegation.** Never delegate until you have the peer's Agent Card and understand its skills, capabilities, and auth requirements.

## Anti-patterns / Failure Modes
- **Opaque delegation** — hiding which agent acted and with what authority, breaking accountability and audit trails.
- **Free-form handoff** — passing unstructured requests that lose requirements, provenance, or failure state, making outcomes unverifiable.
- **No timeout or ownership** — leaving tasks orphaned in a "working" state with nothing polling or notifying.
- **Skipping discovery/auth** — calling a peer without reading its Agent Card or handling its declared auth scheme.
- **Polling when streaming fits** — using polling for real-time needs (wasteful) or webhooks for quick calls (overkill).
- **Exposing credentials in URLs/bodies** — undermining the header-based credential model.

## Implementation Sketch
```
1. Discover peer: fetch Agent Card (.well-known/agent.json or registry)
2. Validate: check skills, input/output modes, capabilities, auth scheme
3. Authenticate: obtain OAuth/API-key credential, pass via HTTP header
4. Send task: call sendTask (sync) or sendTaskSubscribe (stream)
   with a message { attributes, parts[] } and acceptedOutputModes
5. Drive lifecycle: observe submitted -> working -> completed/failed,
   or handle input-required by supplying missing info
6. Collect artifacts: read streamed/partial then final parts
7. Validate result: verify claims/provenance before using them
8. Decide: accept, retry, or escalate (log for audit)
```

Small illustrative pseudocode for a streaming client:
```
card = fetch("https://peer.example.com/.well-known/agent.json")
assert "text" in card.defaultOutputModes
headers = {"Authorization": f"Bearer {get_token(card.authentication)"}
task = sendTaskSubscribe(headers, id="task-002",
    message={role:"user", parts:[{type:"text", text:"JPY to GBP today?"}]},
    acceptedOutputModes=["text/plain"])
for event in task.stream:            # SSE updates
    print(event.status, event.artifact?.parts)
assert task.status == "completed"
```

## Worked Example
**Birthday planner across frameworks.** A coordinator agent orchestrates a birthday plan by delegating to specialized peers. For the scheduling piece it contacts a **Calendar Agent** built with Google ADK. The server defines an `AgentSkill` (`check_availability`) and an `AgentCard` advertising `streaming=True`, a text input/output mode, and its URL. The ADK backend wraps an `LlmAgent` (Gemini model) with a `CalendarToolset`, running on in-memory artifact/session/memory services, exposed through a `DefaultRequestHandler` and `A2AStarletteApplication` on Starlette/Uvicorn, with an `/authenticate` callback. The client reads the card, authenticates, sends a `check_availability` request, streams availability updates, and returns the result to the planner—demonstrating a LangGraph/CrewAI-style coordinator talking to an ADK server with no shared codebase.

## Key Takeaways
1. A2A is an open, HTTP/JSON-RPC standard enabling cross-framework agent collaboration (ADK, LangGraph, CrewAI, and more).
2. The **Agent Card** is the agent's digital identity—advertise skills, capabilities, and auth before delegating.
3. Prefer **asynchronous tasks** with explicit lifecycle states; use `input-required` for multi-turn refinement.
4. Choose the right interaction mechanism: sync for quick calls, polling for long jobs, SSE for real-time, webhooks for very long tasks.
5. Secure the whole path: mTLS, header-based credentials, Agent Card auth declarations, and audit logs.
6. Treat remote agents as opaque, potentially untrusted services—validate their artifacts before trusting them.
7. A2A coordinates agents; **MCP** (see Ch 10) is the complementary protocol for model-to-tool/resource access.
8. Tooling like Trickle AI helps visualize and track A2A traffic for debugging and optimization.

## Connects To
- **Ch 7**: A2A forms the protocol boundary for cross-agent collaboration and orchestration.
- **Ch 10**: MCP is the complementary tool/resource protocol—A2A for agents-to-agents, MCP for clients-to-tools.
- **Ch 18**: Cross-agent calls expand the safety and authorization boundary that must be enforced.
- **Ch 12 (Task lifecycle / state machines)**: A2A tasks embody typed, observable state transitions.
