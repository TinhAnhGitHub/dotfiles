# Model Serving Limits, Quotas, and Regions

Source: [Databricks docs](https://docs.databricks.com/aws/en/machine-learning/model-serving/model-serving-limits)

## Resource and Payload Limits (Custom Models & AI Agents)

| Feature | Granularity | Limit |
|---------|-------------|-------|
| Endpoints | Per workspace | 1,000 |
| Queries per second (QPS) | **Per endpoint** (route-optimized) | 300,000 |
| Queries per second (QPS) | **Per workspace** (route-optimized) | 300,000 |
| Queries per second (QPS) | **Per workspace** (non-route-optimized) | 200 (dev only) |
| Provisioned concurrency | Per model | 1,024 |
| Provisioned concurrency | Per workspace | 4,096 |
| Create/update operations | Per workspace | 50 in 5 minutes |
| Payload size | Per request | **16 MB** (custom model); **4 MB** (AI agent) |
| Request/response logging | Per request | Over 1 MB → NOT logged |
| Model execution duration | Per request | **597 seconds** (~10 min) |
| CPU model memory | Per model instance | `CPU`: 4 GB, `CPU_MEDIUM`: 8 GB, `CPU_LARGE`: 16 GB |
| GPU model memory | Per endpoint | Depends on GPU type (see GPU table) |
| Environment variables | Per served model | 50 |
| Overhead latency (route-optimized) | Per request | < 20 ms |
| Overhead latency (standard) | Per request | < 50 ms |

> **To increase limits**: Reach out to your Databricks account team. Most hard limits can be raised on request.

---

## Foundation Model API Limits (Pay-per-Token)

### Rate Limits by Model

All limits are **per workspace**. Tokens-per-minute (TPM) limits use a sliding window with burst buffer and token bucket smoothing.

**Large Language Models** (Enterprise tier):

| Model | ITPM | OTPM | QPH |
|-------|------|------|-----|
| GPT-5.5 Pro / GPT-5.5 / GPT-5.4 / GPT-5.4 mini / GPT-5.4 nano | 200K | 20K | 360K |
| GPT-5.3 Codex / GPT-5.2 Codex / GPT-5.2 / GPT-5.1 | 200K | 20K | 360K |
| GPT-5.1 Codex Max / GPT-5.1 Codex Mini | 200K | 20K | 360K |
| GPT-5 / GPT-5 mini / GPT-5 nano | 200K | 20K | 360K |
| Gemini 3.5 Flash / 3.1 Pro Preview / 3.1 Flash Lite | 200K | 20K | 360K |
| Gemini 2.5 Pro / 2.5 Flash | 200K | 20K | 360K |
| Qwen3.5 122B / Qwen3-Next 80B (Beta) | 200K | 10K | — |
| Llama 4 Maverick | 200K | 10K | 2,400 |
| Llama 3.3 70B | 200K | 10K | 2,400 |
| Llama 3.1 8B | 200K | 10K | 7,200 |
| Llama 3.1 405B | 5K | 500 | 1,200 |
| Gemma 3 12B | 200K | 10K | 7,200 |

**Anthropic Claude models** (all 200K ITPM / 20K OTPM / 360K QPH):
Claude Sonnet 4, Opus 4.1, Fable 5, Opus 4.8/4.7/4.6/4.5, Sonnet 4.6/4.5, Haiku 4.5

**Embedding models** (QPH only):
- Qwen3-Embedding-0.6B: 2,160,000 QPH
- GTE Large (En): 540,000 QPH
- BGE Large (En): 2,160,000 QPH

### How Rate Limits Are Enforced

1. **Pre-admission check**: Input tokens counted from actual prompt; output tokens estimated from `max_tokens` (or default reservation).
2. **Credit-back**: If actual output < reserved `max_tokens`, the difference is credited back immediately.
3. **Burst buffer**: Small buffer allows short bursts above nominal rate.
4. **Sliding window**: Token consumption tracked with sliding window + token bucket algorithm.
5. **Claude Sonnet 4 default**: If `max_tokens` not set, defaults to **1,000** output tokens (finish reason "length").

### 429 Error Response Format

```json
{
  "error": {
    "message": "Rate limit exceeded: ITPM limit of 200,000 tokens reached",
    "type": "rate_limit_exceeded",
    "code": 429,
    "limit_type": "input_tokens_per_minute",
    "limit": 200000,
    "current": 200150,
    "retry_after": 15
  }
}
```

### Retry Logic Pattern

```python
import time, random

def retry_with_backoff(func, max_retries=10, initial_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" not in str(e) and "rate_limit" not in str(e).lower():
                raise
            delay = initial_delay * (2 ** attempt) * (1 + random.random())
            time.sleep(delay)
    raise Exception(f"Max retries {max_retries} exceeded")
```

### Provisioned Throughput Limits

| Feature | Limit |
|---------|-------|
| TPM restrictions | None (capacity-based) |
| Queries per second | Up to 200 per workspace |
| Output token limits | Varies by model (e.g., GPT OSS 120B: 25K; Llama 4 Maverick: 8,192) |
| Llama 4 Maverick PT limitations | No autoscaling, no metrics panels, no traffic splitting |

---

## Resource & Payload Limits (Foundation & External Models)

| Feature | Limit |
|---------|-------|
| Payload size | 4 MB per request |
| Request/response logging | Over 1 MB → NOT logged |
| QPS per workspace | 200 |
| Model execution duration | 597 seconds |
| Overhead latency | < 50 ms |

---

## Networking & Security Limitations

- Endpoints respect IP allowlists and PrivateLink ingress rules.
- Model Serving does **NOT** support PrivateLink to external endpoints by default (per-region evaluation).
- No security patches to existing model images (risk of destabilization). New model version = new image with latest patches.
- Outbound network access can be restricted via [network policies](https://docs.databricks.com/aws/en/security/network/serverless-network-security/manage-network-policies).

---

## Region Availability & Compliance

Model Serving is available in all major AWS regions (us-east-1/2, us-west-2, eu-west-1/2/3, eu-central-1, ap-northeast-1/2, ap-southeast-1/2, ap-south-1, ca-central-1, sa-east-1).

Compliance standards (varies by region): HIPAA, PCI-DSS, FedRAMP Moderate, IRAP, CCCS Medium (Protected B), UK Cyber Essentials Plus.

> Containers must be rebuilt within the last 30 days for compliance. Databricks auto-rebuilds; if the job fails, re-log the model.
