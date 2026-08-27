# Foundation Model APIs — Specifics

Source: [Databricks FM API limits](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/limits), [Pricing](https://www.databricks.com/product/pricing/foundation-model-serving)

---

## Endpoint Types

| Type | When to Use | Cost Model |
|------|-------------|------------|
| **Pay-per-token** | Dev/demo, low-volume, variable traffic | Per million input/output tokens |
| **Provisioned Throughput** | Production, guaranteed capacity | Per DBU/hour (entry or scaling capacity) |

---

## Supported Model Families

### Chat / LLM
- **OpenAI**: GPT-5.5 Pro, GPT-5.5, GPT-5.4, GPT-5.3 Codex, GPT-5.2, GPT-5.1, GPT-5
- **Anthropic**: Claude Sonnet 4/4.6/4.5, Opus 4.1/4.8/4.7/4.6/4.5, Fable 5, Haiku 4.5
- **Google**: Gemini 3.5 Flash, 3.1 Pro Preview, 2.5 Pro, 2.5 Flash
- **Meta**: Llama 4 Maverick, Llama 3.3 70B, Llama 3.1 405B/70B/8B
- **Other**: Qwen3.5 122B, Qwen3-Next 80B, GPT OSS 120B/20B, Gemma 3 12B

### Embedding
- Qwen3-Embedding-0.6B, GTE Large (En), BGE Large (En)

---

## Pay-Per-Token Pricing (DBU Rates)

| Model | DBU / M input tokens | DBU / M output tokens |
|-------|---------------------|----------------------|
| Llama 4 Maverick | 7.143 | 21.429 |
| Llama 3.3 70B | 7.143 | 21.429 |
| Qwen3-Next 80B | 2.143 | 17.143 |
| Qwen3.5 122B | 3.143 | 31.429 |
| GPT OSS 120B | 2.143 | 8.571 |
| Gemma 3 12B | 2.143 | 7.143 |
| Llama 3.1 8B | 2.143 | 6.429 |
| GPT OSS 20B | 1.000 | 4.286 |
| Qwen3-Embedding-0.6B | 0.286 | N/A |
| GTE Large | 1.857 | N/A |
| BGE Large | 1.429 | N/A |

### Provisioned Throughput Pricing (DBU/hour)

| Model | Entry Capacity (DBU/h) | Scaling Capacity (DBU/h) |
|-------|----------------------|------------------------|
| Llama 4 Maverick | 85.714 | 85.714 |
| Llama 3.3 70B | 85.714 | 342.857 |
| Qwen3.5 122B | 85.714 | 85.714 |
| GPT OSS 120B | 71.429 | 71.429 |
| Llama 3.1 8B | 53.571 | 106.000 |
| GPT OSS 20B | 53.571 | 53.571 |
| Llama 3.2 3B | 46.429 | 92.857 |

> Entry capacity = smaller, lower-cost unit (select clouds/regions only).
> Scaling capacity = standard increment. Minimum PT purchase = 1 scaling unit where entry is unavailable.

---

## Output Token Limits (Provisioned Throughput)

| Model | Max Output Tokens |
|-------|-----------------|
| GPT OSS 120B | 25,000 |
| GPT OSS 20B | 25,000 |
| Gemma 3 12B | 8,192 |
| Llama 4 Maverick | 8,192 |
| Llama 3.1 405B | 4,096 |
| Llama 3.1 70B | 8,192 |
| Llama 3.1 8B | 8,192 |

---

## Foundation Model & External Model Limits

| Feature | Limit |
|---------|-------|
| Payload size | 4 MB |
| Request/response logging | Over 1 MB = NOT logged |
| QPS per workspace | 200 |
| Model execution duration | 597 seconds |
| Overhead latency | < 50 ms |

---

## Best Practices

1. **Set `max_tokens` explicitly** — Claude Sonnet 4 defaults to 1,000 output tokens if not set.
2. **Monitor token usage** — Track both ITPM and OTPM separately in your app.
3. **Implement retry with exponential backoff** — 429 errors include `retry_after` field.
4. **Use smaller models for high volume** — Llama 3.1 8B for throughput; reserve 405B for complex tasks.
5. **Consider provisioned throughput** for sustained production usage — no TPM restrictions.
6. **Discover models at runtime** — use `serving-endpoints list` filtering on `system.ai.*` rather than hard-coding model names.
