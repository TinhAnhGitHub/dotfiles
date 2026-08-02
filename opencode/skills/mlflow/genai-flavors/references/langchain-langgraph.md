# LangChain and LangGraph

## Status and selection

The MLflow LangChain flavor is experimental and fast-moving. Use a tested MLflow/LangChain pair.
Current docs support agents, retrievers, runnables, and LangGraph compiled graphs; deprecated
LangChain constructs have version-specific support. Prefer Models from Code for LangGraph and
partner packages such as `langchain-openai` to avoid legacy deserialization substitutions.

## Trace first

```python
import mlflow

mlflow.set_experiment("support-agent")
mlflow.langchain.autolog()
```

Autologging traces normal invocations. Model logging behavior is separate; do not assume autolog
packaged a LangGraph model.

## LangChain Models from Code

`chain.py`:

```python
import os
import mlflow
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

prompt = PromptTemplate.from_template("Answer concisely: {question}")
chain = prompt | ChatOpenAI(model=os.environ["PROVIDER_MODEL_ID"]) | StrOutputParser()
mlflow.models.set_model(chain)
```

Log, load, and test:

```python
import mlflow

info = mlflow.langchain.log_model(
    lc_model="chain.py",
    name="support-chain",
    input_example={"question": "What is MLflow?"},
    extra_pip_requirements=["langchain-openai==<TESTED_VERSION>"],
)

native = mlflow.langchain.load_model(info.model_uri)
print(native.invoke({"question": "What is MLflow?"}))

pyfunc = mlflow.pyfunc.load_model(info.model_uri)
print(pyfunc.predict({"question": "What is MLflow?"}))
```

The model source runs during logging/loading; credentials must be injected through environment or
managed identity. `mlflow.models.set_model()` is not a concurrency primitive—avoid concurrent
model logging in one process.

## LangGraph model

`langgraph_agent.py`:

```python
import mlflow
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@tool
def lookup_policy(topic: str) -> str:
    """Return an approved support-policy summary for a topic."""
    policies = {"refund": "Refunds require an order ID and policy eligibility check."}
    return policies.get(topic, "No approved policy found.")

graph = create_react_agent(ChatOpenAI(model="<PINNED_MODEL_ID>"), [lookup_policy])
mlflow.models.set_model(graph)
```

```python
info = mlflow.langchain.log_model(
    lc_model="langgraph_agent.py",
    name="support-langgraph",
    input_example={"messages": [{"role": "user", "content": "Explain refunds"}]},
)
```

For a stable OpenAI Responses-compatible serving contract, consider wrapping the graph in
`ResponsesAgent`; see `custom-responses-agent.md`.

## Streaming

With a streamable LangChain model logged by a compatible MLflow release:

```python
model = mlflow.pyfunc.load_model(info.model_uri)
for chunk in model.predict_stream({"question": "Explain model aliases"}):
    handle(chunk)
```

Streaming support is version/model dependent (documented from MLflow 2.12.2). Test chunk schema,
final aggregation, cancellation, provider errors, and trace completeness.

## Input conversion

MLflow may convert chat dictionaries to LangChain message objects for certain model types. If the
application requires raw dictionaries, the documented
`MLFLOW_CONVERT_MESSAGES_DICT_FOR_LANGCHAIN=false` behavior can disable conversion. Set it in the
target environment and add contract tests rather than relying on an implicit default.

## Dangerous deserialization

Some legacy retriever/vector-store loaders require `allow_dangerous_deserialization=True` for
pickle-based artifacts. Never enable this for untrusted artifacts. Prefer Models from Code plus a
trusted external vector store, immutable dependencies, and signed/reviewed artifacts.

## Common failures

- partner package object reloads from a different package under legacy serialization;
- required tool/retriever packages omitted from the environment;
- model relies on notebook globals or an in-memory vector store;
- LangGraph traced successfully but was never packaged;
- source file contains a key or performs remote mutation at import;
- request dictionary is unexpectedly converted to message objects;
- loaded streaming model returns a generator the caller forgets to consume.
