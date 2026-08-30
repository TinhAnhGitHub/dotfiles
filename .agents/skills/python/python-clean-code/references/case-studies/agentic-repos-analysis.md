# Agentic repositories — Chapters 18–24 evidence

This is a source-oriented field guide for agentic/LLM repositories. These are verified local
checkouts under `/home/tinhanhnguyen/Desktop/project/reference/`; paths are intentionally recorded
so examples can be rechecked against the repository version. A missing pattern is meaningful: do
not manufacture a descriptor or metaclass example when a project only consumes `property`.

| Chapter | Verified agentic examples |
|---|---|
| 18 | LangGraph client/stream context managers; LlamaIndex durable runtime and `match access`; AG2/AutoGen `ContextVar`/Docker cleanup; ClawGUI `AsyncExitStack`; CogAgent FastAPI lifespan; browser-use action matching and `finally` cleanup |
| 19 | Agent-S process orchestration and bounded BBoN tasks; ClawGUI locks/tasks/`to_thread`; LlamaIndex task/queue control loops; AG2 dependent chats; TuriX-CUA cancellation and `to_thread`; DeepSeek Harness reader threads/queues |
| 20 | Agent-S `ThreadPoolExecutor`/`as_completed`; DeerFlow shared thread executor; SCALE-CUA futures; Open-AgentRL process pools; MAI-UI `as_completed`; LangGraph `run_in_executor`; LlamaIndex executor bridge; AG2 `run_in_executor` |
| 21 | LangGraph async stream cancellation; LlamaIndex async workflow contexts; AG2 dependent futures; ClawGUI per-session async tasks; DeerFlow sync-to-async tools; Agent-S bounded async work; TuriX-CUA async stop coordination |
| 22 | LlamaIndex `DictLikeModel` dynamic fields; AG2/AutoGen `LLMConfig` forwarding; LangGraph/deer-flow/ClawGUI module `__getattr__`; LangGraph `cached_property`; DeerFlow cached catalog property |
| 23 | No verified custom descriptor implementation in the inspected agentic repositories. LangGraph, DeerFlow, and TuriX-CUA consume properties/cached properties; the local book examples remain the descriptor evidence. |
| 24 | LlamaIndex `WorkflowMeta`; AG2/AutoGen `MetaLLMConfig`; TuriX-CUA dynamic Pydantic `create_model`; InfiGUI-G1 and Dart-GUI dynamic enum/config metaclasses |

## Exact local source anchors

### Chapter 18

- `langgraph/libs/sdk-py/langgraph_sdk/_sync/client.py` — `SyncLangGraphClient.__enter__`/`__exit__`.
- `langgraph/libs/sdk-py/langgraph_sdk/_async/stream.py` — `AsyncThreadStream` task cancellation/close.
- `llama-agents/packages/llama-agents-server/src/llama_agents/server/runtime.py` — durable runtime lifecycle.
- `llama-agents/packages/llama-agents-control-plane/src/llama_agents/control_plane/build_api/build_app.py` — `match access`.
- `SCALE-CUA/osworld_eval/mm_agents/coact/autogen/llm_config.py` — `ContextVar` restoration.
- `ClawGUI/clawgui-agent/nanobot/nanobot/agent/loop.py` — `AsyncExitStack` shutdown.
- `CogAgent/app/vllm_openai_server.py` — FastAPI lifespan cleanup.

### Chapters 19–21

- `agent-s/osworld_setup/s3/bbon/generate_facts.py` — semaphore, `to_thread`, and `gather`.
- `ClawGUI/clawgui-agent/nanobot/nanobot/agent/loop.py` — locks, task tracking, shutdown gather.
- `ClawGUI/clawgui-agent/nanobot/nanobot/agent/tools/gui.py` and `tools/web.py` — `to_thread`.
- `agent-s/gui_agents/s1/aci/LinuxOSACI.py` — `ThreadPoolExecutor` and `as_completed`.
- `deer-flow-agent/backend/packages/harness/deerflow/tools/sync.py` — shared executor bridge.
- `SCALE-CUA/osworld_env/worker/src/task.py` and `session.py` — executor/future handling.
- `Open-AgentRL/verl/workers/reward_manager/prime.py` — process pool and executor timeout.
- `MAI-UI/MAI-UI/evaluation/grounding/eval_server.py` — `as_completed` evaluation workers.
- `TuriX-CUA/examples/main.py` and `src/controller/registry/service.py` — async lifecycle and `to_thread`.
- `deepseek-harness/python/sdk/src/deepseek_harness/client.py` — reader/stderr threads and queues.

### Chapters 22–24

- `llama-agents/packages/llama-index-workflows/src/workflows/events.py` — `DictLikeModel`.
- `langgraph/libs/langgraph/langgraph/pregel/_read.py` — `PregelNode.cached_property`.
- `deer-flow-agent/backend/packages/harness/deerflow/skills/catalog.py` — cached catalog names.
- `SCALE-CUA/osworld_eval/mm_agents/coact/autogen/llm_config.py` — forwarded dynamic attributes and `MetaLLMConfig`.
- `llama-agents/packages/llama-index-workflows/src/workflows/workflow.py` — `WorkflowMeta`.
- `TuriX-CUA/src/controller/registry/service.py` — Pydantic `create_model`.
- `InfiGUI-G1/verl/protocol.py` and `verl/utils/py_functional.py` — metaclass/config and dynamic enum behavior.
- `dart-gui/verl/protocol.py` and `verl/utils/py_functional.py` — corresponding metaclass utilities.

## External source links

- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LlamaIndex](https://github.com/run-llama/llama_index)
- [AG2](https://github.com/ag2ai/ag2)
- [Agent-S](https://github.com/simular-ai/Agent-S)
- [TuriX-CUA](https://github.com/TurixAI/TuriX-CUA)
