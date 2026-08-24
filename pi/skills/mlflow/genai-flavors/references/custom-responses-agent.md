# Custom PythonModel and ResponsesAgent

## Choose ResponsesAgent for agents

Current MLflow 3 docs recommend `ResponsesAgent` over `ChatModel` and `ChatAgent`. It subclasses
`PythonModel`, uses an OpenAI Responses-compatible schema, supports multiple output items,
tool-call records, annotations, custom outputs, multi-agent scenarios, and streaming. It requires
Pydantic 2.

Use generic `PythonModel` for non-agent applications with a deliberately custom schema.

## Minimal ResponsesAgent with streaming

`agent.py`:

```python
from typing import Generator

import mlflow
from mlflow.entities.span import SpanType
from mlflow.models import set_model
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest,
    ResponsesAgentResponse,
    ResponsesAgentStreamEvent,
)
from openai import OpenAI


class SupportAgent(ResponsesAgent):
    def __init__(self, model: str):
        self.client = OpenAI()
        self.model = model

    @mlflow.trace(span_type=SpanType.AGENT)
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        response = self.client.responses.create(
            model=self.model,
            input=request.input,
        )
        return ResponsesAgentResponse(**response.to_dict())

    @mlflow.trace(span_type=SpanType.AGENT)
    def predict_stream(
        self, request: ResponsesAgentRequest
    ) -> Generator[ResponsesAgentStreamEvent, None, None]:
        for event in self.client.responses.create(
            model=self.model,
            input=request.input,
            stream=True,
        ):
            yield ResponsesAgentStreamEvent(**event.to_dict())


mlflow.openai.autolog()
set_model(SupportAgent(model="<PINNED_PROVIDER_MODEL>"))
```

Log and contract-test:

```python
import mlflow

info = mlflow.pyfunc.log_model(
    python_model="agent.py",
    name="support-agent",
    pip_requirements=[
        "mlflow==<TARGET_VERSION>",
        "openai==<TESTED_VERSION>",
        "pydantic>=2,<3",
    ],
)

request = {
    "input": [{"role": "user", "content": "How do refunds work?"}],
    "context": {"conversation_id": "test-123", "user_id": "anonymous-test"},
}
loaded = mlflow.pyfunc.load_model(info.model_uri)
response = loaded.predict(request)
events = list(loaded.predict_stream(request))
```

ResponsesAgent supplies a default input example and schema metadata, but a domain-realistic
example is still valuable for integration testing. Do not put sensitive identifiers in examples.

## Manual streaming contract

When adapting a non-Responses provider, text streaming must use a stable `item_id`, emit
`response.output_text.delta` events, then emit a `response.output_item.done` event containing the
aggregated item:

```python
yield ResponsesAgentStreamEvent(
    **self.create_text_delta(delta="Hello", item_id="msg_1")
)
yield ResponsesAgentStreamEvent(
    type="response.output_item.done",
    item=self.create_text_output_item(text="Hello", id="msg_1"),
)
```

Test that concatenated deltas equal the final text and that errors/cancellation do not produce a
false completed item.

## Tool-call contract

A complete recorded sequence is:

1. `function_call` item with `id`, `call_id`, name, and JSON arguments;
2. traced, allow-listed tool execution with validated arguments and time/resource limits;
3. `function_call_output` item using the same `call_id`;
4. assistant message item explaining the result.

Never expose arbitrary `eval`, shell execution, unrestricted file/network access, or unvalidated
tool names. Prefer a fixed dispatch table and Pydantic/JSON Schema validation. For side effects,
use idempotency keys, authorization, audit logging, and approval steps.

## Generic PythonModel

For a non-agent contract:

```python
import mlflow
from mlflow.models import set_model
from mlflow.pyfunc import PythonModel

class Normalizer(PythonModel):
    def predict(self, context, model_input, params=None):
        return [text.strip() for text in model_input]

set_model(Normalizer())
```

Define explicit batch behavior and a signature. `predict_stream` handles one logical request and
must return/yield an iterator in compatible releases; it is not an automatic batch-streaming API.

## Migration from ChatAgent/ChatModel

- convert Chat Completions messages/tool calls to Responses items;
- preserve `call_id` across function call and output;
- replace a single assistant message with a list of output items;
- adapt streaming to Responses event types and final item semantics;
- reevaluate clients, UI rendering, trace scorers, and serving payloads;
- log as Models from Code and validate before moving registry/endpoint traffic.
