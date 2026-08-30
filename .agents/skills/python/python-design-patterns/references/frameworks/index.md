# Framework pattern matrix

This matrix is a framework-facing crosswalk, not the example catalog. Concrete, adapted framework
snippets are persisted in the `## Framework examples` section of the relevant pattern pages. Each
row helps you find an API, pattern family, and source; framework APIs change quickly, so check the
recorded revision in `../sources.json` before using a snippet as current.

The canonical set has 17 entries: Hugging Face Hub and Transformers are distinct; duplicate Agno
and OpenRLHF requests are represented once.

| Framework | Verified pattern evidence | When / why it helps | Source |
|---|---|---|---|
| **verl** | `Role`, `ResourcePoolManager`, `role_worker_mapping`; engine-worker composition and registry | Separates PPO control flow from worker implementation, placement, and backend selection. | [PPO architecture](https://verl.readthedocs.io/en/latest/examples/ppo_code_architecture.html), [HybridFlow](https://verl.readthedocs.io/en/latest/hybrid_flow.html) |
| **Hugging Face Hub** | `HfApi` client facade; validator decorators and typed request boundaries | Centralizes Hub transport and validates reusable API arguments without duplicating checks. | [Hub API reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api), [validator source](https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/utils/_validators.py) |
| **Transformers** | `TrainerCallback`; `AutoConfig.register()` and `AutoModel.register()` | Adds training hooks and custom model implementations without modifying the main Trainer or loader. | [Callbacks](https://github.com/huggingface/transformers/blob/main/docs/source/en/trainer_callbacks.md), [custom models](https://huggingface.co/docs/transformers/en/custom_models) |
| **PydanticAI** | `Agent[DepsT, OutputT]`, `RunContext`, `deps_type`, `@agent.tool`, capabilities | Makes runtime dependencies and structured outputs typed, injectable, and testable. | [Dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/), [capabilities](https://pydantic.dev/docs/ai/core-concepts/capabilities) |
| **LangChain** | `create_agent`, middleware, `ToolStrategy`, `ProviderStrategy`, `response_format` | Separates agent orchestration from provider-specific structured-output and middleware policies. | [Agents](https://docs.langchain.com/oss/python/langchain/agents), [structured output](https://docs.langchain.com/oss/python/langchain/structured-output) |
| **LangGraph** | `StateGraph`, typed state/reducers, `.compile()`, checkpointer, `interrupt()`, `Command` | Makes branching, persistence, approval, retry, and resume behavior explicit. | [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) |
| **Agno** | `Agent`, `Team`, `Workflow`, `Step`, `Toolkit.register` | Composes autonomous agents, delegated teams, deterministic workflows, and reusable tools. | [SDK](https://docs.agno.com/sdk/introduction), [teams](https://docs.agno.com/teams/overview), [knowledge](https://docs.agno.com/knowledge/quickstart) |
| **Google ADK** | `SequentialAgent`, `ParallelAgent`, `LoopAgent`, `CallbackContext`, session state | Encodes workflow composition and scoped runtime state as reusable agent objects. | [Workflow agents](https://adk.dev/agents/workflow-agents/), [state](https://adk.dev/sessions/state/), [callbacks](https://adk.dev/callbacks/) |
| **vLLM** | `LLM`, `SamplingParams`, `generate()`/`chat()`, `enqueue()` and completion waiting | Separates request submission from collection and makes batch/queue execution efficient. | [Offline inference](https://docs.vllm.ai/en/stable/serving/offline_inference/), [architecture](https://docs.vllm.ai/en/stable/design/arch_overview/) |
| **OpenAI Python SDK** | `OpenAI`, `AsyncOpenAI`, `with_options`, context-managed streams, retries | Keeps sync/async clients, request policy, streaming ownership, and transient-failure behavior explicit. | [Official SDK](https://github.com/openai/openai-python), [streaming helpers](https://github.com/openai/openai-python/blob/main/helpers.md) |
| **MLflow** | `@mlflow.trace`, manual tracing, `PythonModel`, model flavors | Adds observability at callable boundaries and exposes diverse models through a portable interface. | [Manual tracing](https://mlflow.org/docs/latest/genai/tracing/app-instrumentation/manual-tracing), [PyFunc API](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.pyfunc.html) |
| **qwen-agent** | `Agent._run`, `BaseTool`, `register_tool`, `TOOL_REGISTRY`, `get_chat_model` | Provides subclassable workflows and replaceable model/tool providers through common registries. | [Agent guide](https://github.com/QwenLM/Qwen-Agent/blob/main/qwen-agent-docs/website/content/en/guide/core_moduls/agent.md), [LLM guide](https://github.com/QwenLM/Qwen-Agent/blob/main/qwen-agent-docs/website/content/en/guide/core_moduls/llm.md) |
| **OpenRLHF** | Ray actor roles; `AgentExecutorBase`, `MultiTurnAgentExecutor`, `agent_func_path` | Decouples model-role placement from PPO orchestration and adapts multi-turn agents to training. | [Agent training](https://openrlhf.readthedocs.io/en/latest/agent_training.html), [Ray PPO launcher](https://github.com/OpenRLHF/OpenRLHF/blob/main/openrlhf/cli/train_ppo_ray.py) |
| **slime** | `custom_generate_function_path`, reward/data postprocess hooks, `Sample.metadata`, `loss_mask` | Keeps rollout/training loops reusable while injecting tools, verifiers, rewards, and token ownership. | [Customization](https://thudm.github.io/slime/get_started/customization.html), [quick start](https://thudm.github.io/slime/get_started/quick_start.html) |
| **DSPy** | `Signature`, `InputField`, `OutputField`, `Module`, `Predict`, `GEPA.compile` | Separates typed task contracts from prompting strategy and metric-driven optimization. | [DSPy](https://dspy.ai/), [modules](https://dspy.ai/api/modules/), [signatures](https://dspy.ai/api/signatures/) |
| **TRL** | `SFTTrainer`, `GRPOTrainer`, configs, callbacks, `reward_funcs`, environment factories | Injects preprocessing, loss, reward, and environment policies into reusable trainer lifecycles. | [SFTTrainer](https://huggingface.co/docs/trl/sft_trainer), [GRPOTrainer](https://huggingface.co/docs/trl/grpo_trainer) |
| **LiteLLM** | Provider-normalized `completion`/`responses`, `Router`, fallbacks, callbacks | Provides an Adapter over providers and centralizes routing, retry, load-balancing, and telemetry policy. | [Documentation](https://docs.litellm.ai/), [custom callbacks](https://docs.litellm.ai/docs/observability/custom_callback) |

## Reading a framework example

For each evidence item, extract the reusable shape rather than copying the framework:

1. Name the stable contract the application depends on.
2. Identify the framework extension point and who owns its lifecycle.
3. Record what is configurable, what is provider-specific, and what is hidden.
4. Translate it into a standard-library example before recommending the framework abstraction.
5. Verify retries, streaming, cancellation, ordering, state persistence, and error semantics.

## Version policy

Prefer a tagged release or versioned documentation. If only `main`, `latest`, or `stable` is
available, mark the row as rolling and record the fetch date. Do not imply that a framework API is
stable merely because the pattern is general.
