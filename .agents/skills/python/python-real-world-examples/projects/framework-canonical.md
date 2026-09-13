# Canonical Open-Source AI Framework Patterns

> **Catalog**: 17 Production Frameworks from [`python-clean-code`](../../python-clean-code/SKILL.md) & [`python-design-patterns`](../../python-design-patterns/SKILL.md)
> **Domain**: Deep Learning, Reinforcement Learning, Agent Orchestration & LLM Serving  
> **Sources**: Verified production codebases across Hugging Face, OpenAI, vLLM, LangChain, and Ray ecosystems  

---

## 1. Overview & Architectural Role

While standalone applications like OpenViking or CowAgent illustrate whole-system architecture, foundational open-source AI frameworks demonstrate **tactical API design, extensible plugin seams, and high-performance Python idioms** operating under heavy load.

This reference crosswalk synthesizes the **17 canonical open-source framework patterns** into a unified architectural taxonomy, demonstrating how world-class libraries solve:
- **Zero-coupling provider abstraction** (LiteLLM, OpenAI SDK)
- **Typed dependency injection & validation** (PydanticAI, DSPy)
- **Extensible lifecycle hooks & callbacks** (Transformers, MLflow, TRL)
- **Stateful agent workflow composition** (LangGraph, Agno, Google ADK, qwen-agent)
- **High-throughput asynchronous serving & worker pools** (vLLM, verl, OpenRLHF, slime)

---

## 2. Canonical Framework Architecture Matrix

| Framework | Core Pattern | Key Architectural Seam / API | Problem Solved |
| :--- | :--- | :--- | :--- |
| **Transformers** | **Observer / Registry** | `TrainerCallback`, `AutoModel.register()` | Non-invasive training telemetry and community model plugin extension. |
| **Hugging Face Hub** | **Façade / Decorator** | `HfApi`, `@validate_hf_hub_args` | Centralized network transport with perimeter input validation. |
| **PydanticAI** | **Typed DI / Port** | `Agent[DepsT, OutputT]`, `RunContext` | Type-safe runtime dependency injection and structured outputs. |
| **LangGraph** | **State Machine / Reducer**| `StateGraph`, reducers, `interrupt()`, `Command` | Persistent cyclical agent workflows with human-in-the-loop pause/resume. |
| **LiteLLM** | **Adapter / Router** | Provider-normalized `completion()`, `Router` | Unified API over 100+ LLM providers with automatic fallback and load balancing. |
| **vLLM** | **Producer-Consumer / Queue**| `LLM`, `SamplingParams`, background engine | High-throughput batching decoupling token generation from client requests. |
| **OpenAI SDK** | **Context Manager / Builder**| `OpenAI.with_options()`, streaming context | Deterministic HTTP connection cleanup and immutable client cloning. |
| **DSPy** | **Declarative Module / Strategy**| `Signature`, `Module`, `Predict`, `compile()` | Separating prompt engineering strategy from task contracts. |
| **Agno** | **Composite / Mediator** | `Agent`, `Team`, `Workflow`, `Step` | Hierarchical multi-agent team delegation and sequential execution pipelines. |
| **Google ADK** | **Composite / Workflow** | `SequentialAgent`, `ParallelAgent`, `LoopAgent` | Tree-structured agent workflows with scoped session state. |
| **MLflow** | **Decorator / Adapter** | `@mlflow.trace`, `PythonModel` | Zero-overhead tracing decorators and portable model serving wrappers. |
| **qwen-agent** | **Command Registry** | `TOOL_REGISTRY`, `register_tool`, `BaseTool` | Dynamic tool registration and discovery without modifying core agent logic. |
| **verl** | **Engine-Worker Pool** | `Role`, `ResourcePoolManager`, `role_worker_mapping`| Decoupling PPO reinforcement learning from Ray worker placement. |
| **OpenRLHF** | **Actor Adapter** | `AgentExecutorBase`, `MultiTurnAgentExecutor` | Adapting interactive multi-turn agent execution into Ray distributed training. |
| **slime** | **Strategy Hook** | `custom_generate_function_path`, postprocess hooks | Injecting custom tool rollouts and reward verifiers into training loops. |
| **TRL** | **Template Method** | `SFTTrainer`, `GRPOTrainer`, `reward_funcs` | Extensible RL fine-tuning loops with pluggable loss and reward hooks. |
| **LangChain** | **Strategy / Middleware**| `create_agent`, middleware, `ToolStrategy` | Separating provider-specific function calling from agent orchestration. |

---

## 3. Deep-Dive Pattern Implementations

### A. Factory & Registry: Hugging Face `AutoModel.register()`
Allows third-party libraries to register custom model architectures without modifying the core `transformers` codebase:

```python
# Demonstrates dynamic open-source registry pattern
from transformers import AutoConfig, AutoModel
from transformers.models.auto.auto_factory import _BaseAutoModelClass

class CustomModelConfig(AutoConfig):
    model_type = "my_custom_llm"

class CustomModelForCausalLM:
    config_class = CustomModelConfig
    def __init__(self, config):
        self.config = config

# Extends AutoModel via runtime registry without modifying transformers source
AutoConfig.register("my_custom_llm", CustomModelConfig)
AutoModel.register(CustomModelConfig, CustomModelForCausalLM)
```

### B. Typed Dependency Injection: PydanticAI `Agent[DepsT, OutputT]`
Eliminates implicit global state by making agent dependencies strictly typed and explicitly injected:

```python
# Demonstrates typed dependency injection port
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class DatabaseConnection:
    connection_url: str

    def query(self, sql: str) -> list[dict]:
        return [{"result": "sample_data"}]

# The Agent specifies its exact runtime dependency requirements via generic types
agent: Agent[DatabaseConnection, str] = Agent(
    "openai:gpt-4o",
    deps_type=DatabaseConnection,
    system_prompt="You are a data analyst assistant."
)

@agent.tool
def execute_query(ctx: RunContext[DatabaseConnection], sql_query: str) -> str:
    # ctx.deps is statically typed as DatabaseConnection by mypy/pyright
    data = ctx.deps.query(sql_query)
    return str(data)
```

### C. The Universal Adapter & Fallback Router: LiteLLM
Normalizes wildly divergent provider APIs (Anthropic, Bedrock, Vertex, OpenAI) into a single canonical signature:

```python
# Demonstrates universal adapter with fallback policies
from litellm import Router

model_list = [
    {
        "model_name": "primary-fast",
        "litellm_params": {"model": "groq/llama-3.3-70b-versatile", "api_key": "..."},
    },
    {
        "model_name": "primary-fast",
        "litellm_params": {"model": "openai/gpt-4o-mini", "api_key": "..."},
    }
]

# Router automatically falls back from Groq to OpenAI on rate limits or 500 errors
router = Router(model_list=model_list, fallbacks=[{"primary-fast": ["openai/gpt-4o-mini"]}])
```

---

## 4. Architectural Lessons for System Designers

1. **Keep Frameworks at the Perimeter**: As shown in Hugging Face Hub and LiteLLM, isolate network calls and third-party SDK dependencies behind a thin, stable façade or adapter.
2. **Prefer Composition Over Inheritance in Workflows**: Follow LangGraph and Google ADK by modeling complex workflows as composed directed graphs rather than deeply nested subclass hierarchies.
3. **Make State Explicit**: LangGraph and PydanticAI demonstrate that explicit state objects and typed context parameters prevent the elusive bugs caused by hidden instance attributes.
