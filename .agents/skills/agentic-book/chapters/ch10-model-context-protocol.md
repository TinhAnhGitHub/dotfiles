# Chapter 10: Model Context Protocol

## Core Idea
The Model Context Protocol (MCP) is an open, standardized protocol that lets any
compliant LLM host (client) discover, connect to, and use external capabilities
exposed by any compliant server. It turns "LLM-to-world" integration from a
custom, per-partnership glue project into a reusable, federated ecosystem. The
boundary it defines is between a client—an application or wrapper around a model
that translates the model's intent into formal MCP requests—and a server, which
owns a domain (a database, an email service, a filesystem) and exposes a bounded
set of tools, resources, and prompts to authorized clients.

MCP matters because without a shared contract, every LLM-to-tool connection is a
one-off integration that does not transfer across providers or host applications.
With MCP, a single server implementation can be consumed by many clients, and a
single client can reach many servers, simply by speaking the same language.

## Frameworks Introduced
- **MCP host/client/server**: The client discovers and invokes capabilities on
  behalf of the model under authorization; the server owns external systems and
  exposes tools (actions), resources (static data), and prompts (interaction
  templates). An optional third-party (3P) service is the actual external system
  the server wraps.
- **FastMCP**: A high-level Python framework that abstracts protocol boilerplate
  and auto-generates tool schemas from function signatures, type hints, and
  docstrings; supports server composition and proxying.
- **Google ADK (Agent Development Kit)**: A host-side toolkit whose `MCPToolset`
  lets an `LlmAgent` consume MCP servers over STDIO or HTTP, with optional
  per-tool filtering.

## Key Concepts
1. **Tool**: An executable action the model can invoke with named, typed
   parameters (e.g., `send_email`, `read_file`). It performs work and returns a
   result.
2. **Resource**: Discoverable, static data exposed as a URI-addressable asset
   (e.g., a database record, a document). The client reads it rather than
   executing it.
3. **Prompt**: A reusable template that structures how the model should interact
   with a resource or tool, ensuring consistent, effective interactions.
4. **Capability discovery**: A client queries the server (the "manifest" step) to
   learn what tools, resources, and prompts exist—just-in-time, without
   redeployment.
5. **Host/client**: The LLM-powered application that connects to servers,
   translates model intent into MCP requests, and returns results to the model.
6. **Server**: The gateway to one domain; it authenticates clients, validates
   requests, executes actions against the underlying 3P service, and returns
   standardized responses.
7. **Transport**: STDIO (JSON-RPC) for local processes; Streamable HTTP and SSE
   for remote, persistent connections.
8. **Authorization & authentication**: Controls which clients reach which servers
   and which actions they may perform—distinct from mere discovery.
9. **Error handling**: Defined failure signals (tool failure, unavailable server,
   invalid request) so the model can diagnose and retry via alternatives.
10. **Deployment modes**: Local servers (speed, sensitive-data isolation) vs.
    remote servers (shared, scalable access); on-demand interactive sessions vs.
    batch processing.

## Mental Models
- **MCP is a universal power-outlet system, not a toolbox.** Function calling
  hands the model a few custom-built, tightly coupled tools; MCP provides a
  standard socket so any compliant tool from any vendor plugs in and works. It
  exposes the connection and discovery, not the capabilities themselves.
- **Discovery is not permission.** Learning that a tool exists does not authorize
  its use. Authentication, authorization, schema validation, and approval gates
  remain the host's responsibility, outside the model.
- **MCP is an integration protocol, not an autonomy policy.** It standardizes how
  capabilities are found and called; it does not decide what the agent is allowed
  to do.
- **Agents strengthen, not replace, deterministic design.** MCP wraps existing
  APIs; the underlying API must still be agent-friendly (filtering, sorting,
  textual data formats) for the non-deterministic model to work efficiently.

## Anti-patterns / Failure Modes
- **MCP for every tool.** Wrapping trivial, fixed functions adds transport and
  infra overhead where direct function calling is sufficient. Reserve MCP for
  discoverable, reusable, cross-system capabilities.
- **Blind trust in discovery metadata.** Treating tool/resource descriptions as
  permission leads to over-broad access. Validate and allowlist before exposing.
- **Lazy legacy API wrapping.** Exposing an API as-is (e.g., one-ticket-at-a-time
  retrieval, or PDF-only document returns) makes the agent slow and inaccurate.
  Improve the underlying interface—add filtering, return Markdown instead of
  PDFs—before wrapping it.
- **Unbounded server exposure.** Publishing every capability widens the attack
  surface; keep servers narrow and filtered.
- **Assuming data-format compatibility.** MCP does not guarantee the consumer can
  parse what it returns; ensure outputs are agent-readable.

## Implementation Sketch
A small illustrative pseudocode (not copied from any source):

```
# Server side (conceptual, FastMCP-style)
@mcp.tool
def read_file(path: str) -> str:
    """Read a text file and return its contents."""
    return load_text(path)

@mcp.resource("file://*")
def doc(uri: str) -> str:
    return load_text(uri)

# Client side (conceptual, ADK-style)
server = StdioServerParameters(command="npx",
                               args=["-y", "@modelcontextprotocol/server-filesystem", ROOT])
tools = MCPToolset(connection_params=server,
                   tool_filter=["list_directory", "read_file"])  # narrow exposure
agent = LlmAgent(model="gemini-2.0-flash", tools=[tools])

# Runtime flow
manifest   = client.list()                 # discovery: tools, resources, prompts
allowed    = allowlist(manifest) & authorize(client)   # discovery != permission
call       = model.select_tool("read_file", {"path": ROOT + "/notes.md"})
observation = client.invoke(call)          # auth + validate + execute + respond
model.observe(observation)                   # context update, continue
```

## Worked Example
An ADK agent needs to manage local files. You instantiate `MCPToolset` with
`StdioServerParameters` pointing `npx` at the community `@modelcontextprotocol/server-filesystem`,
rooted at an absolute managed directory. The client discovers the server's tools,
an optional `tool_filter` restricts it to read/list actions, and the model uses
`read_file`/`list_directory` on prompts like "Show the contents of this folder."
For a remote server, the same client instead uses `HttpServerParameters(url=...)`
and `tool_filter=["greet"]` to consume a FastMCP server exposing an HTTP `greet`
tool on `localhost:8000`. In both cases, discovery happens once, authorization
and filtering bound the surface, and the model composes the result into its next
step.

## Key Takeaways
1. MCP is an open standard that makes LLM-to-tool/data integration reusable and
   interoperable across providers and hosts.
2. It uses a client-server model exposing three primitives: tools (actions),
   resources (data), and prompts (templates), with dynamic capability discovery.
3. Discovery grants knowledge, not permission—authentication, authorization,
   schema validation, and approval remain the host's job.
4. The wrapped API must be agent-friendly (filtering, textual formats); MCP does
   not fix a poorly designed underlying interface.
5. Transports matter: STDIO for local, Streamable HTTP/SSE for remote; choose by
   speed, security, and sharing needs.
6. Frameworks like FastMCP (server authoring, auto-schemas, composition) and
   Google ADK's `MCPToolset` (host consumption with tool filtering) lower the
   cost of both sides.
7. Use MCP for complex, scalable, evolving integrations; use direct function
   calling for simple, fixed tool sets.

## Connects To
- **Function calling**: MCP is the broader, standardized discovery-and-transport
  framework; function calling is a narrow, proprietary, one-to-one tool invocation.
  MCP federates; function calling embeds.
- **Agent-to-Agent (A2A)**: MCP connects a client to external capabilities
  (tools/data); A2A coordinates whole agents talking to other agents. They operate
  at different granularities and compose rather than compete.
- **Least privilege / security (later chapters)**: The narrow-server, allowlisted
  tool, authenticated-client principles here are the concrete form of least
  privilege applied to the MCP boundary.
