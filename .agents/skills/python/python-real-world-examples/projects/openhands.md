# OpenHands

> Repository: [All-Hands-AI/OpenHands@6087719](https://github.com/All-Hands-AI/OpenHands/tree/60877198aa4b0075a47eef9a24043f21f5bf6f97)
> Default branch: `main`
> Commit: `60877198aa4b0075a47eef9a24043f21f5bf6f97`
> License: [MIT](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/LICENSE)
> Domain: Agent Canvas frontend, agent-server API adapters, conversations, and backend selection
> Python/native boundary: This pinned checkout is primarily TypeScript/React. It contains no central Python agent runtime; the Python files are test/helper surfaces. The evidence below is therefore TypeScript architecture evidence at the frontend-to-agent-server boundary, not a claim about a Python implementation.
> Evidence level: A for the TypeScript backend/event/conversation adapters and tests; C for any Python pattern transfer
> Research source: `/media/tinhanhnguyen/sub/oss-architecture/tmp/python-oss-architecture.LEjXfG/openhands` (read-only pinned checkout)

## 1. Executive Architecture Summary

At this revision OpenHands is a client-heavy Agent Canvas monorepo. The frontend models local and cloud agent-server backends, adapts their HTTP/WebSocket contracts, keeps backend health and active selection in stores, and represents conversation actions/observations as typed events. Runtime and conversation services route operations through the active backend and handle cloud/local differences.

This repository snapshot is not the older Python agent core sometimes associated with the OpenHands name. Its architectural value for this corpus is the external boundary: typed protocol adapters, event-driven UI state, pause/resume commands, child-conversation workflows, and explicit backend health/lifecycle policy.

```text
React UI / hooks
       │
       ├── typed event store + WebSocket context
       └── conversation/runtime service
                │
                ▼
      active backend registry + health store
                │
        local agent-server or cloud proxy
                │
                ▼
       typed conversation/event protocol
```

## 2. Layering and Boundary Discipline

| Layer | Repository location | Responsibility |
|---|---|---|
| UI/application hooks | `src/hooks/`, `src/contexts/` | User actions, WebSocket event handling, pause/resume presentation |
| Service adapters | `src/api/agent-server-adapter.ts`, `conversation-service/`, `runtime-service/`, `event-service/` | Translate typed UI calls to local/cloud server APIs |
| Backend selection state | `src/api/backend-registry/` | Active backend, health, persistence, URL selection, auth, fallback |
| Event/protocol model | `src/types/agent-server/core/events/`, `conversation-service.types.ts` | Typed actions, observations, state, pause, message, and conversation DTOs |
| External drivers | Local agent server, OpenHands Cloud, browser storage, WebSocket/HTTP | Actual runtime and persistence mechanisms, outside this checkout’s Python surface |

The boundary is explicit in TypeScript types and services, but it is not a Python clean architecture. The missing Python runtime is itself a required limitation for downstream users of this case study.

## 3. Pattern Map

| Pattern ID | Pattern | Source evidence | Test evidence | Book mapping | Level |
|---|---|---|---|---|---|
| P10 | Commands, events, and message bus | [`src/types/agent-server/core/events/action-event.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/types/agent-server/core/events/action-event.ts), observation/state/pause event types, and [`src/hooks/use-handle-ws-events.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/hooks/use-handle-ws-events.ts) separate incoming facts from UI reactions; `event-service.api.ts` retrieves event pages | [`src/api/event-service/event-service.api.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/event-service/event-service.api.test.ts), [`__tests__/api/agent-server-conversation-service.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/agent-server-conversation-service.test.ts) | Architecture with Python ch08–10; Clean Architecture ch18/ch23; Software Design ch37 | A |
| P12 | Adapter, façade, and provider router | [`src/api/agent-server-adapter.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/agent-server-adapter.ts), [`src/api/agent-server-compatibility.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/agent-server-compatibility.ts), and [`src/api/backend-registry/active-store.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/backend-registry/active-store.ts) select local/cloud backends and normalize server operations | [`src/api/agent-server-adapter.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/agent-server-adapter.test.ts), [`src/api/agent-server-compatibility.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/agent-server-compatibility.test.ts), [`__tests__/api/backend-registry/active-store.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/backend-registry/active-store.test.ts) | Clean Architecture ch19–20; Software Design ch35 | A |
| P13 | State machine, workflow, and saga | [`src/hooks/mutation/use-pause-conversation.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/hooks/mutation/use-pause-conversation.ts), [`src/hooks/mutation/use-resume-conversation.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/hooks/mutation/use-resume-conversation.ts), and [`src/services/child-conversation-launch.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/services/child-conversation-launch.ts) encode pause/resume and local/cloud child-launch transitions | [`__tests__/api/cloud/conversation-pause.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/cloud/conversation-pause.test.ts), [`__tests__/api/cloud/conversation-create.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/cloud/conversation-create.test.ts), [`__tests__/api/agent-server-conversation-service-condense.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/agent-server-conversation-service-condense.test.ts) | Clean Architecture ch18/ch24; Software Design ch38 | A |
| P16 | Concurrency, scheduling, and resource lifecycle | [`src/api/backend-registry/health-store.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/backend-registry/health-store.ts) tracks consecutive backend failures; [`src/api/runtime-service/agent-server-runtime-service.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/src/api/runtime-service/agent-server-runtime-service.ts) routes runtime calls; WebSocket context manages event-stream ownership | [`__tests__/api/backend-registry/health-store.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/backend-registry/health-store.test.ts), [`__tests__/api/cloud/conversation-runtime-info.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/cloud/conversation-runtime-info.test.ts), [`__tests__/api/backend-registry/url-selection.test.ts`](https://github.com/All-Hands-AI/OpenHands/blob/60877198aa4b0075a47eef9a24043f21f5bf6f97/__tests__/api/backend-registry/url-selection.test.ts) | Software Design ch41; Clean Architecture ch23 | A |

These are TypeScript patterns at a client/server contract boundary. They must not be used as authoritative evidence for a Python agent implementation that is absent from this pinned checkout.

## 4. Source Walkthrough

### Backend registry

`active-store.ts` chooses an active backend, honors URL selection, prefers a healthy local backend when appropriate, and falls back to a sentinel when none is usable. `health-store.ts` records consecutive failures and disables polling after the configured threshold. Storage and URL modules keep browser persistence and selection policy separate.

### Agent-server and runtime adapters

The adapter/compatibility modules translate server capabilities and API shapes into frontend operations. The runtime service chooses a cloud proxy or local remote workspace client from the active backend, so UI hooks do not know which transport is in use.

### Events and workflows

Typed event modules distinguish actions, observations, conversation state, messages, and pause events. `child-conversation-launch.ts` validates target/isolation choices, creates local worktrees or cloud tasks, polls boundedly for cloud readiness, and returns a link/status result. This is workflow coordination, not a durable Python saga engine.

## 5. Theory Versus Practice

The event/message-bus mapping is at the protocol/UI boundary: events are typed facts consumed by stores and hooks, while mutations issue commands. The backend registry is a client-side provider router with persistence and health policy. The design accepts duplicated local/cloud branches because the two backends have different authentication, URL, and lifecycle semantics.

The repository’s service layer is intentionally frontend-oriented. A server-side application should keep domain state and authorization out of browser stores; this case study is useful for API anti-corruption and state transition design, not as a complete agent-server architecture.

## 6. Testing Strategy

- Adapter tests mock HTTP/client responses and verify capability/compatibility translation.
- Backend-store tests cover selection, persistence, failure thresholds, and URL resolution.
- Event-service and conversation-service tests verify paginated event/conversation contracts.
- Cloud conversation tests cover create/pause flows; runtime tests cover cloud/local routing.
- End-to-end mock-LLM tests exist elsewhere in the repository, but were not executed in this pass.

## 7. Production Compromises and When Not to Copy

| Compromise | Benefit | Risk / when not to copy |
|---|---|---|
| Browser-side backend registry | Users can switch between local and cloud servers without rebuilding the app | Do not place secrets, authorization, or authoritative workflow state only in browser storage |
| Separate local/cloud adapter branches | Encapsulates genuinely different transport/auth/lifecycle behavior | Keep shared DTOs and compatibility tests or the branches will drift |
| Event store plus WebSocket/UI state | Supports streaming conversation updates and replay-like views | Define ordering, deduplication, and reconnect semantics before treating events as durable facts |
| Bounded child-launch polling | Handles asynchronous cloud task readiness | Use server-side jobs or durable callbacks when polling cost or reliability becomes significant |

## 8. Practice Exercise

Use [the event-driven-training exercise](../../python-software-architecture/exercises/event-driven-training.md) and [the workflow-state exercise](../../python-software-architecture/exercises/workflow-state.md): build a Python local/cloud backend adapter, emit typed action/observation events, and model pause/resume/child-launch transitions. Keep browser-like selection state separate from authoritative server state.

## 9. Canonical Research Record

| Field | Evidence |
|---|---|
| Repository / default branch | `All-Hands-AI/OpenHands`, `main` |
| Pinned revision | `60877198aa4b0075a47eef9a24043f21f5bf6f97` |
| License | MIT, verified from repository `LICENSE` |
| Python/native boundary | No central Python agent runtime in this checkout; TypeScript/React owns reviewed adapters and UI state |
| Canonical pattern IDs | P10 (A), P12 (A), P13 (A), P16 (A); Python transfer is C |
| Source evidence | Backend registry, service adapters, event types, workflow hooks, and runtime service |
| Test evidence | Adapter, registry, event, conversation, cloud pause/create, and runtime tests |
| Book mapping | Clean Architecture ch18–20 and ch23–24; Software Design ch35, ch38, and ch41 |
| Production compromise | Local/cloud divergence is retained at the client boundary; this snapshot does not evidence Python server internals |
| Practice exercise | `exercises/event-driven-training.md`, `exercises/workflow-state.md` |
