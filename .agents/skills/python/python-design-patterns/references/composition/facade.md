# Facade

## Intent

Expose one focused, stable API over a subsystem containing multiple clients, resources, or steps.

## Use when

Use a Facade when callers repeatedly coordinate the same provider setup, serialization, retries,
telemetry, and cleanup, or when the subsystem's internal modules should not become application API.

## Why

The Facade reduces coupling and gives one place to enforce policy. Unlike an Adapter, it may
combine several operations instead of translating one interface to another.

## Example

```python
class SearchFacade:
    def __init__(self, embed, vector_store, reranker) -> None:
        self.embed = embed
        self.vector_store = vector_store
        self.reranker = reranker

    def search(self, query: str, limit: int = 5) -> list[str]:
        candidates = self.vector_store.search(self.embed(query), limit=limit * 4)
        return self.reranker.rank(query, candidates)[:limit]
```

This solves repeated embedding, retrieval, and reranking orchestration at every call site.

## When not to use

Do not make a Facade a God object. Split it when it owns unrelated policies or exposes every
subsystem operation unchanged.

## Trade-offs and tests

The Facade can conceal expensive work and make advanced features harder to reach. Test the public
workflow, dependency failures, partial failure, timeouts, and the policy it owns.

## Framework evidence

The official OpenAI client, vLLM's high-level `LLM` interface, and MLflow PyFunc serving boundary
are candidate Facade examples. Verify current methods through the [framework matrix](../frameworks/index.md).

## Framework examples

### Hugging Face Hub — `HfApi` (adapted)

```python
from huggingface_hub import HfApi

class ModelHub:
    def __init__(self, token: str) -> None:
        self.api = HfApi(token=token)

    def publish(self, repo_id: str, folder: str) -> None:
        self.api.create_repo(repo_id, exist_ok=True)
        self.api.upload_folder(folder_path=folder, repo_id=repo_id)
```

This solves callers repeatedly coordinating authentication, repository creation, and uploads. It
fits Facade because `ModelHub.publish()` combines several Hub operations into one focused API
rather than merely renaming one method. See the official [Hugging Face Hub API
reference](https://huggingface.co/docs/huggingface_hub/package_reference/hf_api).

### OpenAI Python — `OpenAI` client (adapted)

```python
from openai import OpenAI

class AnswerService:
    def __init__(self) -> None:
        self.client = OpenAI()

    def answer(self, question: str) -> str:
        response = self.client.responses.create(
            model="model", input=question,
        )
        return response.output_text
```

This solves application code having to coordinate request construction, authentication, transport,
and response parsing for each call. The service fits Facade because it exposes one domain operation
over the SDK subsystem. See the official [OpenAI Python SDK repository](https://github.com/openai/openai-python).
