# DSPy and LlamaIndex

## DSPy workflow

The DSPy flavor is experimental. Use MLflow tracing during development and log the optimized
program selected by a held-out evaluation, not whichever optimizer trial ran last.

```python
import dspy
import mlflow

mlflow.dspy.autolog()
lm = dspy.LM(model="<PINNED_PROVIDER_MODEL>", max_tokens=250)
dspy.settings.configure(lm=lm)

class QA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.program = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.program(question=question)

candidate = QA()  # In production, replace with the optimizer-selected compiled program.
info = mlflow.dspy.log_model(
    candidate,
    name="dspy-qa",
    input_example="What is a model alias?",
)

pyfunc = mlflow.pyfunc.load_model(info.model_uri)
native = mlflow.dspy.load_model(info.model_uri)
```

DSPy streaming requires a compatible DSPy release (docs specify greater than 2.6.23), a logged
signature, and string outputs:

```python
for event in pyfunc.predict_stream("What is a model alias?"):
    handle(event)
```

Tokens/API keys are intentionally dropped from serialized DSPy settings. Inject them securely at
runtime. Treat optimizer dataset, metric, seed, budget, provider model, and resulting compiled
program as versioned evidence.

## LlamaIndex index and engine

`engine_type` fixes the PyFunc inference interface:

- `query`: one query → response;
- `chat`: conversational engine with history;
- `retriever`: query → relevant nodes/documents.

```python
import mlflow
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)

info = mlflow.llama_index.log_model(
    index,
    name="support-index",
    engine_type="query",
    input_example="What is the refund policy?",
)

pyfunc = mlflow.pyfunc.load_model(info.model_uri)
print(pyfunc.predict("What is the refund policy?"))

native_index = mlflow.llama_index.load_model(info.model_uri)
print(native_index.as_query_engine().query("What is the refund policy?"))
```

Direct object logging is suitable for the default in-memory `SimpleVectorStore`. Do not expect it
to embed a remote Qdrant or Databricks Vector Search collection.

## External vector store with Models from Code

`index.py` should reconnect to an existing immutable collection/index and avoid re-indexing on
every load:

```python
import os
import mlflow
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

client = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
store = QdrantVectorStore(client=client, collection_name="support-docs-v12")
index = VectorStoreIndex.from_vector_store(store)
mlflow.models.set_model(index)
```

```python
info = mlflow.llama_index.log_model(
    "index.py",
    name="support-index",
    engine_type="query",
)
```

Capture the external collection/index version and embedding model as version parameters. Remote
data lifecycle is separate from the MLflow artifact.

## LlamaIndex Workflow

Workflow packaging uses Models from Code and requires compatible releases (docs specify
LlamaIndex 0.11.0+ and MLflow 2.17.0+):

```python
info = mlflow.llama_index.log_model(
    "workflow.py",
    name="support-workflow",
    input_example={"input": "What is MLflow?"},
)
```

Native `workflow.run(...)` can be async. The PyFunc wrapper and deployed inference path are
synchronous and block until completion. Tracing supports async and streaming separately, but the
documented combination of async streaming is not supported.

## Settings guardrails

MLflow persists much of LlamaIndex global `Settings` for reproducibility but not API keys or
non-serializable objects. Because loading can update global settings, isolate tests and avoid
silently overriding model/embedding configuration after load unless that change is intentionally
versioned and reevaluated.
