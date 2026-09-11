# DeepSeek Harness API and Pattern Map

**Repository**: https://github.com/deepseek-ai/deepseek-harness  
**Package/command**: `@deepseek-ai/dsh`, command `dsh`  
**Positioning**: an interactive agent harness with an “everything-is-a-plugin” architecture powered by Cordis. The repository explicitly labels itself experimental developer-preview software, warns of compatibility-breaking changes, and publishes a safety notice. This reference therefore documents the verified product surface and architectural concepts rather than pretending there is a stable general-purpose SDK API.

## Core model

DeepSeek Harness is organized around a plugin runtime rather than a single `Agent` class. The harness composes UI, model access, sessions, tools, commands, and integrations as plugins/modules. The user-facing entry points are the CLI and Web UI; extension points and plugin packages are the important development boundary.

A practical mental model is:

`dsh command → runtime/plugin composition → model turn → tool/plugin events → session/context update → UI/CLI presentation`

The source repository contains TypeScript/Node-oriented packages, documentation, development notes, plugin topics, and a Cordis-based composition model. Exact internal class/function names should be read from the pinned version because the preview status means names and package boundaries may change.

## Verified commands and runtime surfaces

- `npx @deepseek-ai/dsh web` — install/run the published harness and start the Web UI, using a local address by default.
- `dsh web --no-open` — run the web server without opening a browser when supported by the current CLI.
- Source workflow: clone the repository, run `pnpm install`, `pnpm run build`, then `pnpm dsh web`.
- CLI and Web UI — provide interactive agent sessions and expose runtime behavior for local development.
- Plugin discovery/registration — the central extension mechanism. Treat plugin metadata and discovered capabilities as untrusted until authorized.
- Cordis composition — provides the runtime paradigm for composing plugin capabilities in space/time; use the repository's architecture docs for exact lifecycle hooks.

## Modules and capability responsibilities

### Plugin/runtime composition

- Plugin modules — package a capability, lifecycle behavior, command, UI contribution, tool, provider, or service. Use them to implement Ch 5 tools, Ch 7 specialization, Ch 10 integrations, and Ch 15 communication.
- Lifecycle hooks/activation — initialize and dispose plugins, register commands/routes/tools, and react to runtime events. Make startup order, cleanup, and failure behavior observable.
- Dependency/context injection supplied by the runtime — lets plugins consume shared services without global imports. Define narrow interfaces so a plugin cannot silently acquire unrelated authority.
- Configuration/settings modules — select providers, plugins, sessions, and UI/runtime options. Version and validate configuration before activation.

The public documentation emphasizes this architecture, but because the project is preview software, do not copy a guessed internal `Plugin` class signature into production code. Pin a commit and inspect the package's exported types before writing an extension.

### Models and conversation turns

- Model/provider plugins — connect the harness to model backends and normalize turn/stream events. Map to Ch 5 and Ch 16; provider-specific tool, streaming, and context behavior still needs testing.
- Prompt/system-instruction sources — assemble the agent's role and runtime context. Map to Appendix A and context engineering; keep policy separate from user/retrieved content.
- Turn/event lifecycle — a model turn may produce text, tool requests, progress, errors, or follow-up input. Record an auditable trajectory rather than only the final rendered message.
- Streaming/UI event channels — deliver incremental state to the terminal or Web UI. Do not commit an external side effect merely because an event was rendered.

### Sessions, state, and context

- Session services — maintain conversation history and active runtime state between turns (Ch 8).
- Context assembly — packages prompt files, user messages, tool observations, workspace information, and plugin-provided context for the next model call (Appendix A).
- Session query/history services visible in the repository's architecture notes — support resumption and inspection. Apply user/tenant scope, redaction, retention, and deletion rules.
- Compaction/summarization mechanisms where enabled — reduce context pressure for long sessions (Ch 8/16). Preserve decisions, provenance, pending actions, and unresolved uncertainty rather than summarizing blindly.

### Tools, commands, and MCP

- Tool/plugin registrations — expose capabilities to the model through structured calls. Use narrow schemas, argument validation, allowlists, and explicit read/write separation (Ch 5/18).
- CLI command modules — implement user-facing operations and developer workflows. A shell command is a side effect; sandbox and authorize it independently.
- MCP integration/server/client modules where configured — connect discoverable tools/resources (Ch 10). Discovery does not grant permission.
- File, shell, repository, and workspace capabilities — useful for coding-agent workflows in Appendix G, but potentially high impact. Restrict roots, command sets, network access, and write paths.
- Web/UI routes and WebSocket/event transport — carry interaction and streaming state; authenticate administrative routes and do not expose internal tools by default.

### Safety, resilience, and operations

- Safety notice and preview warnings — mandatory operational inputs: the repository has not been presented as security-audited production software.
- Permission/trust/integrity controls in the project surface — use them as defense layers, but verify exact defaults and threat model at the pinned revision.
- Plugin isolation and failure handling — a failing or malicious plugin must not corrupt unrelated sessions or receive unrestricted credentials. Add timeouts, cleanup, and capability-specific authorization.
- Session/runtime logs, event streams, and analytics modules — support Ch 19 trajectory and operational monitoring. Redact secrets and personal data before persistence.
- Build/package scripts — make the repository runnable, but build success is not a safety or correctness evaluation.

## Pattern-by-pattern use

| Book chapter | Harness surface | Purpose |
|---|---|---|
| 1 | prompt/context plugins and event-driven turns | sequential interaction |
| 2 | plugin/command/provider selection | routing |
| 3 | concurrent plugin/tool work where supported | bounded parallelization |
| 4 | iterative turns and critic plugins | reflection |
| 5 | tool/command/plugin registrations | function calling |
| 6 | coding/workspace task workflow | planning |
| 7 | plugin-specialist composition | collaboration |
| 8 | sessions, history, compaction | memory |
| 9 | versioned plugin/prompt/config changes | adaptation |
| 10 | MCP integrations | capability discovery |
| 11 | progress/events/session state | goal monitoring |
| 12 | plugin lifecycle/errors/restart handling | recovery |
| 13 | UI/CLI confirmation and pause flows | HITL |
| 14 | retrieval/context plugins | grounding |
| 15 | plugin/service/event boundaries | communication |
| 16 | provider selection, context compaction, caching/streaming | resources |
| 17 | iterative tool-grounded turns | reasoning |
| 18 | trust, permission, sandbox, safety notice, allowlists | safety |
| 19 | event/session logs and operational telemetry | evaluation |
| 20 | task/command queues and user-selected work | prioritization |
| 21 | extensible plugin ecosystem and research workflows | discovery |

## What is and is not a stable API

**Verified and documented**: repository identity, `dsh`/`npx` launch commands, Web UI, source build workflow, MIT license, Cordis-based all-plugin architecture, developer-preview warning, plugin discoverability topic, and safety notice.  
**Version-sensitive**: concrete TypeScript package names, plugin class signatures, lifecycle method names, internal session stores, event types, and tool registration functions. Before implementing an extension, inspect the pinned checkout's package exports and tests; do not infer an API from a UI feature or an archived architecture note.

## Strengths, limits, and selection rule

Choose DeepSeek Harness when the goal is an extensible interactive harness or plugin ecosystem, especially for developer-facing workflows. Choose a general agent SDK/framework when you need a stable embedded Python/TypeScript library with documented orchestration primitives. Treat the preview as a research/development dependency: isolate credentials and workspaces, pin revisions, review `SAFETY.md`, and maintain a rollback path.

The plugin architecture can implement nearly every book pattern, but it does not automatically provide correct planning, safe authorization, reliable retrieval, or evaluation. Those remain explicit application responsibilities.

**Sources**: official repository README, safety notice, package metadata, and architecture/documentation links, accessed 2026-09-01.
