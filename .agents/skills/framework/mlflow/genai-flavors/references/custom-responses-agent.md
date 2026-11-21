# Custom PythonModel and ResponsesAgent

## Choose ResponsesAgent for agents

Current MLflow 3 docs recommend `ResponsesAgent` over `ChatModel` and `ChatAgent`. It subclasses
`PythonModel`, uses an OpenAI Responses-compatible schema, supports multiple output items,
tool-call records, annotations, custom outputs, multi-agent scenarios, and streaming. It requires
Pydantic 2.

Use generic `PythonModel` for non-agent applications with a deliberately custom schema.

## Output helper catalog

Only construct `ResponsesAgentResponse` and `ResponsesAgentStreamEvent` directly.
Everything else in `mlflow.types.responses_helpers` is for validating dictionaries.
Use these instance helpers to build items:

| Helper | Purpose |
|---|---|
| `create_text_output_item` | Assistant text message |
| `create_reasoning_item` | Reasoning summary item |
| `create_function_call_item` | Tool call (`id`, `call_id`, `name`, `arguments`) |
| `create_function_call_output_item` | Tool result using the same `call_id` |
| `create_mcp_approval_request_item` / `create_mcp_approval_response_item` | MCP tool approval flow |
| `create_annotation_added` | Annotation item (streaming only) |
| `create_text_delta` | Text delta (streaming only) |

`request.custom_inputs` passes through to `custom_outputs` for arbitrary metadata.
Conversion helpers `to_chat_completions_input()` and
`output_to_responses_items_stream()` bridge Chat Completions providers and
Responses-format output without hand-writing item dictionaries.

## Complete tool-calling sequence

```python
import mlflow
from mlflow.entities import SpanType
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import ResponsesAgentRequest, ResponsesAgentResponse

class SimpleResponsesAgent(ResponsesAgent):
    @mlflow.trace(span_type=SpanType.AGENT)
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        return ResponsesAgentResponse(
            output=[
                self.create_function_call_item(
                    id="fc_1", call_id="call_1", name="python_exec",
                    arguments='{"code":"result = 4 * 3\\nprint(result)"}',
                ),
                self.create_function_call_output_item(call_id="call_1", output="12\n"),
                self.create_text_output_item(
                    text="The result of 4 * 3 in Python is 12.", id="msg_1"
                ),
            ],
            custom_outputs={"key1": "custom-value1"},
        )
```

For streaming tool calls, emit each call and its result as a separate
`response.output_item.done` event so MLflow tracing and clients can reconstruct
message history.

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

## Adapting a Chat Completions provider

Use the conversion helpers rather than manual item construction:

```python
import mlflow
from mlflow.models import set_model
from mlflow.pyfunc import ResponsesAgent
from mlflow.types.responses import (
    ResponsesAgentRequest, ResponsesAgentResponse,
    output_to_responses_items_stream, to_chat_completions_input,
)
from openai import OpenAI

client = OpenAI()

class SimpleResponsesAgent(ResponsesAgent):
    def call_llm(self, messages):
        for chunk in client.chat.completions.create(
            model="gpt-5", messages=messages, stream=True
        ):
            yield chunk.to_dict()

    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        outputs = [
            event.item
            for event in self.predict_stream(request)
            if event.type == "response.output_item.done"
        ]
        return ResponsesAgentResponse(output=outputs, custom_outputs=request.custom_inputs)

    def predict_stream(self, request: ResponsesAgentRequest):
        messages = to_chat_completions_input([i.model_dump() for i in request.input])
        yield from output_to_responses_items_stream(self.call_llm(messages))

mlflow.openai.autolog()
set_model(SimpleResponsesAgent())
```

## ChatAgent → ResponsesAgent message mapping

| Case | ChatAgent | ResponsesAgent |
|---|---|---|
| Text | `{"role": "assistant", "content": "..."}` | `{"type": "message", "id": "...", "role": "assistant", "content": [{"type": "output_text", "text": "...", "annotations": []}], "status": "completed"}` |
| Tool call | `tool_calls` on assistant message | `{"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": "...", "arguments": "..."}` |
| Tool result | `{"role": "tool", "tool_call_id": "call_1", "content": "..."}` | `{"type": "function_call_output", "call_id": "call_1", "output": "..."}` |
| Tool definition | `{"type": "function", "function": {...}}` | `{"type": "function", "name": "...", "parameters": {...}, "strict": true, "description": "..."}` |

Preserve `call_id` across call and output, replace the single assistant message with
a list of output items, and re-test clients, UI rendering, trace scorers, and
serving payloads.

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
