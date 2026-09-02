# ML System Design Cheatsheet

## Decision rules
- **If** outcome, owner, value, or harm metric is unclear, **stop**; define business metric, ML proxy, guardrails, and a rule/search baseline.
- Write hard limits first: slice quality, p95/p99, throughput, availability, cost, privacy, energy, update cadence, label delay, rollback time.
- Apply **D·A·M** (Data, Algorithm, Machine); estimate `T ≈ Dvol/BW + O/(Rpeak·ηhw) + Llat`; optimize the binding term.
- **If** result is needed before a request, use batch; otherwise online. **If** round trips violate limits, use edge; if one target cannot satisfy all limits, use hybrid.

| Smell/binding constraint | First move | Recheck |
|---|---|---|
| Memory | smaller model, quantize, locality, shard | accuracy; decode stalls |
| Compute | batch, fuse, compile | queue; power |
| Network | move closer, compress, overlap | codec; staleness |
| I/O | sequential reads, cache, prefetch | contention |
| Coordination | fewer/topology-aware workers, overlap | scaling efficiency |

**Fregly performance check:** if GPU utilization is low, trace storage → CPU/NUMA → pinned memory → GPU → communication before changing the model. Profile one bottleneck, then remeasure end to end.

## Data and release
- **If** an event follows prediction time, exclude it: point-in-time joins need event/availability time, window, key, version.
- **If** train/serve code, schema, or statistics differ, share definitions or replay-test parity.
- **If** labels lag, use proxies and model delay; retraining cannot outrun label computation.
- **If** classes are imbalanced, report precision/recall and slices; do not trust aggregate accuracy alone.
- **If** categories are open-ended, use unknown handling or hashing; test unseen/collision behavior.

```text
Offline fail? → inspect baseline, labels, leakage, slices; do not tune blindly.
Offline pass? → test hardware, peak memory, realistic load, calibration,
                 privacy/fairness, edge cases, and failure behavior.
System pass? → shadow → canary → A/B when causal evidence is needed.
Guardrail/safety slice regresses? → hold/abort despite primary gains.
```

| Stage | Evidence | Limitation |
|---|---|---|
| Held-out | sampled behavior | misses possible production shift |
| Shadow | integration, latency, comparison | no user outcome |
| Canary | live load, small blast radius | weak power at tiny traffic |
| A/B | causal outcome comparison | traffic, duration, interference, label delay |

## Serving and monitoring
- **If** p99 nears saturation, reserve headroom, scale or shed load; queueing rises near the knee.
- Budget latency across network, retrieval, parsing, preprocessing, inference, postprocessing, serialization. **If inference is under half, optimize elsewhere.**
- **If** batching improves throughput but violates p99, shrink the window or split pools.
- **If** timeout, missing feature, low confidence, overload, or unsafe output occurs, use tested cache/heuristic/smaller-model/human path; measure outcomes.
- Keep the prior artifact warm; version cache/session state when stateful. Version data, code, config, environment, dependencies, model, metrics, owner.

| Speed | Signals → response |
|---|---|
| Immediate | errors/readiness/queue/latency/resources → page, shed, fail over |
| Near-real-time | schema/missingness/confidence/rates/drift → inspect pipeline/cohort |
| Label-lagged | accuracy/PR/calibration/business outcome → validate cause |
| Strategic | cohort/intersection coverage, freshness, cost, fairness → review |

**If drift appears:** check bugs, schema/version mismatch, missingness, and parity; classify covariate `p(x)`, label `p(y)`, or concept `p(y|x)`. Retrain only when benefit exceeds compute/labor, rollout risk, and staleness cost.

## Safety and build/buy
- **If** high-impact or safety-critical, define human override and uncertain-case routing; test aggregate/intersection slices, calibration, perturbations, outliers, and worst failures after updates.
- Threat-model data, storage, training, supply chain, endpoint, hardware, feedback, and updates. Minimize retention; use least privilege, encryption, audit, signed artifacts, and rate limits. Local/federated is not automatically private.
- Ship a model card: intended/out-of-scope use, factors, data, metrics, thresholds, limitations, risks, owner, version, date.
- **If** commodity, buy; build for differentiation/control. Evaluate workload, hardware, failure drill, total cost, portability, and exit path; avoid platformizing a one-off.
