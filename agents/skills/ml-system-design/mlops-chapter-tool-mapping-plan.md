# MLOps Tool ↔ Book-Chapter Mapping Plan

> A mapping plan that connects the MLOps tools referenced in Chip Huyen's *MLOps Tools* guide
> to 51 synthesized skill chapters across four source books (44 primary chapters plus 7
> available early-release Fregly sections), plus a repeatable discovery-and-validation workflow.

## Change log

- **2026-09-02** — Added an Exa-checked modern MLOps/LLMOps component map and prioritized pilot worklist in §6. The historical inventory and its caveats remain unchanged.

---

## 0. Scope, boundaries, and caveats (read first)

### 0.1 Source corpora and line boundaries
| Corpus | Source file | Line range | Contents |
|---|---|---|---|
| **Vol1** | `full_text.txt` | lines **2–64965** | *Introduction to Machine Learning Systems* (Vijay Janapa Reddi, MIT Press) — 16 chapters |
| **Vol2** | `full_text.txt` | lines **64966–135108** | companion volume — 17 chapters (Fleet, Distributed ML, Operations at Scale, Responsible AI) |
| **Chip Huyen** | `full_text.txt` | lines **135109–149731** | *Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications* — 11 chapters |
| **Chris Fregly** | `/tmp/book_skill_work-159406/full_text.txt` | lines **2–10085** | *AI Systems Performance Engineering* (O’Reilly, 2025 early release) — 7 available sections; TOC chapters 5–9 unavailable |
| **Tool guide** | `/tmp/mlops-tools.md` | — | Chip Huyen's *MLOps Tools* reference doc (the tool inventory source) |

### 0.2 Critical caveats
- **HISTORICAL / NON-COMPREHENSIVE.** The tool guide (`/tmp/mlops-tools.md`) is explicitly *not* a comprehensive or curated list. The author states tooling is ephemeral ("all software will eventually become legacy software"), that lists were often compiled by **vendor-sponsored communities**, and that he **stopped maintaining** his own 284-tool landscape. Every tool below inherits these limitations: it reflects a point-in-time snapshot (circa 2020–2021) and is **not** an endorsement or a complete market survey.
- **Tool drift is guaranteed.** Licenses change, projects are archived/abandoned, APIs break, and vendors pivot. Treat every "recommended tool" as a **hypothesis to re-validate**, never as a current fact. See §5 (Discovery & Validation Plan) for the refresh cadence.
- **Copyright / attribution.** Vol1 and Vol2 are © 2027 MIT — subject to a **Creative Commons CC-BY-NC-ND** license and explicitly licensed *against* AI training ("No part of this book may be used to train artificial intelligence systems without permission in writing from the MIT Press"). Chip Huyen's book is © O'Reilly Media. This mapping plan **quotes only short, necessary excerpts** (chapter titles, tool names, links) for reference/citation and does **not** reproduce book prose. Do **not** ingest, train on, or redistribute the corpus text. Verify your intended use against each license before any downstream use.
- **Historical link validity is unverified.** The historical inventory URLs were transcribed from the source docs offline and **must be re-verified** before reliance. The modern-refresh URLs in §6 were fetched from official documentation through Exa on **2026-09-02**, but they are still subject to release, ownership, and URL drift.
- **Conceptual ≠ tool.** Where a chapter's concern has no single mature tool, the mapping records **"conceptual / no direct tool"** — this is a deliberate, honest entry, not a gap.

---

## 1. Complete tool & category inventory (from `mlops-tools.md`)

Every category and tool mentioned in the tool guide, with its original link. Marked **historical / non-comprehensive** throughout.

### 1.1 Long lists of MLOps tools (meta-sources — treat as biased/evolving)
| Resource | Link | Note |
|---|---|---|
| MLOps Community's Learn | https://mlops.community/learn/ | Categories: Feature Store, Monitoring, Metadata/Model Store; Deploy in progress |
| TwiML Solutions Guide | https://twimlai.com/solutions/ | Categorized with features + deployment targets |
| StackShare | https://stackshare.io/ | General tech-stack adoption, not MLOps-specific |
| AI Infrastructure Landscape | https://ai-infrastructure.org/ai-infrastructure-landscape/ | Membership foundation; comprehensive MLOps research |
| Matt Turck's MAD Landscape | https://mattturck.com/data2021/ | Investor perspective, annual |
| Leigh Marie Braswell — Startup Opportunities in ML | https://leighmariebraswell.substack.com/p/startup-opportunities-in-machine | Investor-gap analysis |
| Chip Huyen's MLOps Landscape + 284-tool Google Sheet | https://huyenchip.com/2020/12/30/mlops-v2.html · https://docs.google.com/spreadsheets/d/1i8BzE4puGQ3dmQueu4LQCcwaqrulgK1Vb-xeFwhy6gY/edit#gid=0 | **Author stopped maintaining it** (last updated Dec 2020) |

### 1.2 Pandas alternatives
| Tool | Link | Category tag |
|---|---|---|
| modin | https://github.com/modin-project/modin | drop-in pandas replacement |
| dask | https://github.com/dask/dask | distributed; enterprise via Coiled |
| cuDF | https://github.com/rapidsai/cudf | GPU DataFrame (RAPIDS) |
| Polars | https://github.com/pola-rs/polars/ | Rust + Apache Arrow, fast |

### 1.3 Data and features
| Tool | Link | Sub-category |
|---|---|---|
| ClickHouse | https://github.com/ClickHouse/ClickHouse | OLAP DB |
| Druid | https://github.com/apache/druid | OLAP DB |
| ksql | https://github.com/confluentinc/ksql | stream processing |
| faust | https://github.com/robinhood/faust | stream processing |
| materialize | https://github.com/MaterializeInc/materialize | stream processing |
| Redpanda | https://github.com/redpanda-data/redpanda | stream processing (WASM) |
| D3 | https://github.com/d3/d3 | visualization |
| Superset | https://github.com/apache/superset | visualization |
| Facets | https://github.com/PAIR-code/facets | visualization |
| redash | https://github.com/getredash/redash | visualization |
| visdom | https://github.com/fossasia/visdom | visualization |
| plotly | https://github.com/plotly/plotly.py | visualization |
| Altair | https://github.com/altair-viz/altair | visualization |
| pandas-profiling | https://github.com/ydataai/pandas-profiling | visualization / profiling |
| lux | https://github.com/lux-org/lux | DataFrame visualization |
| bokeh | https://github.com/bokeh/bokeh | visualization |
| Great Expectations | https://github.com/great-expectations/great_expectations | data validation |
| deepchecks | https://github.com/deepchecks/deepchecks | data/model validation | |
| pandera | https://github.com/pandera-dev/pandera | data validation |
| Snorkel | https://github.com/snorkel-team/snorkel | labeling |
| Label Studio | https://github.com/heartexlabs/label-studio | labeling |
| doccano | https://github.com/doccano/doccano | labeling |
| DVC | https://github.com/iterative/dvc | data versioning |
| Dolt | https://github.com/dolthub/dolt | data versioning |
| pachyderm | https://github.com/pachyderm/pachyderm | data versioning / pipelines |
| Hub | https://github.com/activeloopai/Hub | unstructured data hosting |
| Amundsen | https://github.com/amundsen-io/amundsen | metadata store (Lyft) |
| DataHub | https://github.com/datahub-project/datahub | metadata store (LinkedIn) |
| FEAST | https://github.com/feast-dev/feast | feature store (OSS) |
| ploomber | https://github.com/ploomber/ploomber | data pipelines |
| hamilton | https://github.com/stitchfix/hamilton | data pipelines |
| NVTabular | https://github.com/NVIDIA-Merlin/NVTabular | data pipelines |
| arrow | https://github.com/apache/arrow | arrow ecosystem |
| flight | https://arrow.apache.org/blog/2019/10/13/introducing-arrow-flight/ | arrow flight |

### 1.4 Interpretability and fairness
| Tool | Link | Sub-category |
|---|---|---|
| SHAP | https://github.com/slundberg/shap | interpretability |
| Lime | https://github.com/marcotcr/lime | interpretability |
| Interpret | https://github.com/interpretml/interpret | interpretability |
| lit | https://github.com/PAIR-code/lit | interpretability (NLP) |
| captum | https://github.com/pytorch/captum | interpretability (PyTorch) |
| timeshap | https://github.com/feedzai/timeshap | interpretability (time-series) |
| AIX360 | https://github.com/Trusted-AI/AIX360 | interpretability |
| AIF360 | https://github.com/Trusted-AI/AIF360 | fairness |

### 1.5 Model development and evaluation
| Tool | Link | Sub-category |
|---|---|---|
| MLflow | https://github.com/mlflow/mlflow | experiment tracking |
| aim | https://github.com/aimhubio/aim | experiment tracking |
| TVM | https://github.com/apache/tvm | model optimization |
| TensorRT | https://developer.nvidia.com/tensorrt | model optimization |
| Triton | https://github.com/openai/triton | model optimization |
| hummingbird | https://github.com/microsoft/hummingbird | model optimization |
| composer | https://github.com/mosaicml/composer | model optimization / training |
| DeepSpeed | https://github.com/microsoft/DeepSpeed | distributed training |
| accelerate | https://github.com/huggingface/accelerate | distributed training |
| PySyft | https://github.com/OpenMined/PySyft | federated learning |
| FedML | https://github.com/FedML-AI/FedML | federated learning |
| FATE | https://github.com/FederatedAI/FATE | federated learning |
| TensorFlow Federated | https://www.tensorflow.org/federated | federated learning |
| checklist | https://github.com/marcotcr/checklist | evaluation (NLP) |
| reclist | https://github.com/jacopotagliabue/reclist | evaluation (recommenders) |
| growthbook | https://github.com/growthbook/growthbook | online experiments (A/B) |
| Ax | https://github.com/facebook/Ax | online experiments / optimization |

### 1.6 Use-case-specific frameworks
| Tool | Link | Use case |
|---|---|---|
| DLRM | https://github.com/facebookresearch/dlrm | recommender / CTR |
| DeepCTR | https://github.com/shenweichen/DeepCTR | recommender / CTR |
| tensorflow-DeepFM | https://github.com/ChenglongChen/tensorflow-DeepFM | recommender / CTR |
| Transformers4Rec | https://github.com/NVIDIA-Merlin/Transformers4Rec | recommender |
| rasa | https://github.com/RasaHQ/rasa | conversational AI |
| NeMo | https://github.com/NVIDIA/NeMo | conversational AI |
| annoy | https://github.com/spotify/annoy | similarity search |
| Faiss | https://github.com/facebookresearch/faiss | similarity search |
| Milvus | https://github.com/milvus-io/milvus | similarity search |
| faceswap | https://github.com/deepfakes/faceswap | deepfakes |
| deepface | https://github.com/serengil/deepface | deepfakes / face analysis |
| convoys | https://github.com/better/convoys | time-lagged conversion modeling |
| WTTE-RNN | (linked in source) | churn prediction |
| lifelines | https://github.com/CamDavidsonPilon/lifelines | survival analysis |

### 1.7 Dev environment
| Tool | Link | Sub-category |
|---|---|---|
| fzf | https://github.com/junegunn/fzf | CLI (fuzzy search) |
| lipgloss | https://github.com/charmbracelet/lipgloss | CLI |
| VSCode | (recommended) | IDE / notebooks |
| Poetry | https://github.com/python-poetry/poetry | dependency management |
| Hydra | https://github.com/facebookresearch/hydra | config management |
| gin-config | https://github.com/google/gin-config | config management |
| docusaurus | https://github.com/facebook/docusaurus | documentation |
| k9s | https://github.com/derailed/k9s | Kubernetes debugging |
| excalidraw | https://github.com/excalidraw/excalidraw | virtual whiteboard |

### 1.8 DevOps for MLOps
| Tool | Link | Sub-category |
|---|---|---|
| earthly | https://github.com/earthly/earthly | CI/CD |
| Sentry | https://github.com/getsentry/sentry | monitoring |
| Prometheus | https://github.com/prometheus/prometheus | monitoring |
| vector | https://github.com/vectordotdev/vector | monitoring / data pipeline |
| M3 | https://github.com/m3db/m3 | monitoring (time-series DB) |
| Grafana | https://github.com/grafana/grafana | dashboards |
| Metabase | https://github.com/metabase/metabase | dashboards |
| Chaos Monkey | https://github.com/Netflix/chaosmonkey | general DevOps (chaos) |
| k6 | https://github.com/grafana/k6 | general DevOps (load testing) |

---

## 2. The 51 skill chapters (the mapping target)

### 2.1 Vol1 — *Introduction to Machine Learning Systems* (16)
1. Introduction · 2. ML Systems · 3. ML Workflow · 4. Data Engineering · 5. Neural Computation · 6. Network Architectures · 7. ML Frameworks · 8. Model Training · 9. Data Selection · 10. Model Compression · 11. Hardware Acceleration · 12. Benchmarking · 13. Model Serving · 14. ML Operations · 15. Responsible Engineering · 16. Conclusion

### 2.2 Vol2 (17)
1. Introduction · 2. Compute Infrastructure · 3. Network Fabrics · 4. Data Storage · 5. Distributed Training · 6. Collective Communication · 7. Fault Tolerance · 8. Fleet Orchestration · 9. Performance Engineering · 10. Inference at Scale · 11. Edge Intelligence · 12. ML Operations at Scale · 13. Security & Privacy · 14. Robust AI · 15. Sustainable AI · 16. Responsible AI · 17. Conclusion

### 2.3 Chip Huyen — *Designing Machine Learning Systems* (11)
1. Overview of Machine Learning Systems · 2. Introduction to Machine Learning Systems Design · 3. Data Engineering Fundamentals · 4. Training Data · 5. Feature Engineering · 6. Model Development and Offline Evaluation · 7. Model Deployment and Prediction Service · 8. Data Distribution Shifts and Monitoring · 9. Continual Learning and Test in Production · 10. Infrastructure and Tooling for MLOps · 11. The Human Side of Machine Learning

---

### 2.4 Chris Fregly — *AI Systems Performance Engineering* (7 available sections)

The early-release TOC lists Chapters 1–12, but explicitly marks TOC Chapters 5–9 unavailable. The supplied body contains available material for TOC Chapters 1–4 and 10–12 only. The skill maps only those seven sections; it does not infer tools or content for the unavailable chapters.

| Skill chapter | Performance/MLOps connection | Tool or implementation examples | Selection and risk note |
|---|---|---|---|
| Fregly Ch1 — Introduction and AI System Overview | Establish full-stack performance baselines, goodput, utilization, cost, and bottleneck ownership before tuning. | `nvidia-smi`, profiler traces, Prometheus/Grafana where available | Tools observe the contract; validate metrics on representative workloads and do not equate GPU utilization with useful progress. |
| Fregly Ch2 — AI System Hardware Overview | Map memory hierarchy, accelerator capability, NVLink/NVSwitch topology, power, thermals, and ROI to training/inference requirements. | `nvidia-smi`, NVLink/NVSwitch telemetry, MIG/MPS, Prometheus/Grafana | Hardware and vendor tooling are environment-specific; measure effective bandwidth, power, and failure behavior rather than peak claims. |
| Fregly Ch3 — OS, Docker, and Kubernetes Tuning | Align NUMA/CPU affinity, pinned memory, driver state, container I/O, resource isolation, and topology-aware scheduling with the GPU data path. | `numactl`, Docker bind mounts, Kubernetes Topology Manager/GPU Operator, MPS/MIG | These are implementation controls, not substitutes for profiling; verify driver/runtime compatibility and isolation policy. |
| Fregly Ch4 — Distributed Communication and I/O Optimizations | Diagnose communication/computation overlap, RDMA, collectives, storage locality, and data-loader stalls. | NCCL, RDMA, SHARP, NIXL, Magnum IO, GPUDirect Storage | Treat each as a stack-dependent option; benchmark topology, message sizes, failure behavior, and I/O contention. |
| Fregly Ch10 — AI System Optimization Case Studies | Reproduce the book’s diagnosis-first case-study method and record before/after end-to-end evidence. | `nvidia-smi`, profiler traces, workload harnesses, MLflow for experiment evidence | Case-study results are not universal benchmarks; retain hardware, software, data, and configuration context. |
| Fregly Ch11 — Future Trends in Ultra-Scale AI Systems Performance Engineering | Use as scenario planning for emerging scale, memory, interconnect, and energy constraints. | Conceptual/no direct tool; connect to current fleet telemetry and benchmark suites | Do not turn projections into product recommendations; revalidate against current hardware and open-source support. |
| Fregly Ch12 — AI Systems Performance Checklist (175+ Items) | Convert checklist items into preflight, profiling, rollout, and regression gates for MLOps pipelines. | `nvidia-smi`, profiler tooling, Prometheus/Grafana, CI benchmark jobs | Keep checklist items evidence-backed and owner-assigned; automate only checks that are stable and reproducible. |

## 3. Tool ↔ Chapter mapping matrix

**Legend**
- **Lifecycle:** Data → Train → Tune/Eval → Deploy → Serve → Monitor → Govern/Maintain
- **Conceptual / no direct tool:** the chapter addresses the concern but no single mature tool from the (historical) inventory maps cleanly.
- Each cell: **Tool(s)** — *rationale* | Stage | Signal | Boundary | Selection | Risks | Alternatives.

Because a full 51-chapter × ~70-tool grid would be unreadable, the matrix is organized **by tool group → chapters it maps to**, with one structured block per (group, chapter) pair. Groups with **no strong chapter mapping** are listed at the end with the rationale for the null.

---

### Group A — Pandas alternatives (modin, dask, cuDF, Polars)

**Maps to:** Vol1 Ch4 Data Engineering · Vol1 Ch5 Neural Computation · Vol2 Ch4 Data Storage · Chip Ch3 Data Engineering Fundamentals · Chip Ch4 Training Data

- **Vol1 Ch4 Data Engineering**
  - *Rationale:* chapter covers collecting/processing data; tabular manipulation performance matters at scale.
  - *Stage:* Data. *Signal:* Pandas OOMs or is too slow on join-heavy ETL.
  - *Boundary:* notebook/ETL stage only, not serving.
  - *Selection:* drop-in need → modin; distributed CPU → dask; GPU → cuDF; single-fast-columnar → Polars.
  - *Risks:* API/behavior quirks (the guide itself cites "quirky" pandas semantics); cuDF requires NVIDIA/RAPIDS stack.
  - *Alternatives:* DuckDB, PyArrow tables, Spark.
- **Vol1 Ch5 Neural Computation**
  - *Rationale:* tensor/data movement under the hood; cuDF/Arrow relevance for preprocessing feeding models.
  - *Stage:* Data→Train. *Selection:* prefer native framework tensors over tabular frames for model input.
  - *Risks:* context-switch cost between tabular and tensor worlds.
  - *Alternatives:* NumPy, native torch/tf ops.
- **Vol2 Ch4 Data Storage**
  - *Rationale:* in-frame formats (Arrow-backed Polars/cuDF) align with columnar storage & zero-copy.
  - *Stage:* Data. *Selection:* match on-disk format (Arrow/Parquet) to in-memory frame.
  - *Risks:* memory-mapped vs copied semantics.
  - *Alternatives:* Parquet readers, pyarrow.
- **Chip Ch3 Data Engineering Fundamentals**
  - *Rationale:* batch vs stream, data formats, storage engines — tabular frames are the analysis layer.
  - *Stage:* Data. *Selection:* Polars/dask for batch analysis; keep streaming separate.
  - *Risks:* conflating batch frames with streaming semantics.
  - *Alternatives:* SQL engines, streaming libs.
- **Chip Ch4 Training Data**
  - *Rationale:* sampling/labeling/augmentation produce large intermediate tables.
  - *Stage:* Data→Train. *Selection:* dask/modin for out-of-core sampling pipelines.
  - *Risks:* data leakage from in-memory shuffling across folds.
  - *Alternatives:* streaming samplers, HF datasets.

---

### Group B — Data & features (OLAP, streaming, viz, validation, labeling, versioning, metadata, feature store, pipelines, Arrow)

**Maps to:** nearly the entire Data→Serve spine. Highest-density group in the guide.

#### B1. OLAP databases — ClickHouse, Druid
- **Vol2 Ch12 ML Operations at Scale** · **Chip Ch8 Data Distribution Shifts and Monitoring**
  - *Rationale:* join predictions with live feedback to monitor model performance in real time.
  - *Stage:* Monitor. *Signal:* need sub-second aggregation of prediction + outcome streams.
  - *Boundary:* monitoring warehouse, upstream of dashboards.
  - *Selection:* high-write analytical queries → ClickHouse; time-series/histogram → Druid.
  - *Risks:* operational burden of running a cluster; schema rigidity.
  - *Alternatives:* M3, Prometheus remote storage, DuckDB, ClickHouse Cloud.

#### B2. Stream processing — ksql, faust, materialize, Redpanda
- **Vol2 Ch2 Compute Infrastructure · Ch3 Network Fabrics · Ch10 Inference at Scale · Chip Ch3 · Ch7 Model Deployment and Prediction Service · Ch8 Monitoring**
  - *Rationale:* online prediction and streaming feature computation require low-latency streams.
  - *Stage:* Data→Serve→Monitor. *Signal:* batch latency too high for real-time features/predictions.
  - *Boundary:* the streaming layer between ingestion and feature store/serving.
  - *Selection:* Kafka-native SQL → ksql; Python → faust; managed streaming DB → materialize; Kafka-replacement → Redpanda.
  - *Risks:* complexity, exactly-once semantics, operational cluster management.
  - *Alternatives:* Kafka + Flink/Spark Streaming, keda.

#### B3. Visualization — D3, Superset, Facets, redash, visdom, plotly, Altair, pandas-profiling, lux, bokeh
- **Vol1 Ch2 ML Systems · Ch12 Benchmarking · Chip Ch2 Design · Ch8 Monitoring · Ch11 Human Side (UX)**
  - *Rationale:* EDA, experiment/feature visualization, and monitoring dashboards.
  - *Stage:* Data → Tune → Monitor. *Signal:* need to inspect data distributions or feature fairness (Facets, pandas-profiling).
  - *Boundary:* analysis/notebook (D3, plotly, Altair, bokeh, lux) vs org dashboards (Superset, redash).
  - *Selection:* embedded custom viz → D3/plotly; quick profiling → pandas-profiling/lux; training progress → visdom; shared BI → Superset/redash.
  - *Risks:* Facets/visdom are legacy/niche.
  - *Alternatives:* Streamlit, Gradio, Matplotlib/Seaborn, Metabase.

#### B4. Data validation — Great Expectations, deepchecks, pandera
- **Vol1 Ch4 Data Engineering · Ch15 Responsible Engineering · Chip Ch3 · Ch4 Training Data · Ch8 Monitoring**
  - *Rationale:* enforce data/feature quality and catch drift before it corrupts training/serving.
  - *Stage:* Data → Monitor. *Signal:* silent schema/quality regressions; data-shifting incidents.
  - *Boundary:* pipeline gates (fail-fast) and serving-time checks.
  - *Selection:* expressive dataset tests → Great Expectations; ML-specific (train/serving skew) → deepchecks; pandas/type-schema → pandera.
  - *Risks:* over-constraining pipelines; validation as ceremony.
  - *Alternatives:* Checkly, custom pytest data tests, TFX Transform.

#### B5. Labeling — Snorkel, Label Studio, doccano
- **Chip Ch4 Training Data · Vol1 Ch3 ML Workflow · Ch15 Responsible Engineering**
  - *Rationale:* training-data labeling and weak supervision.
  - *Stage:* Data. *Signal:* scarcity of hand labels; cost of annotation.
  - *Boundary:* dataset construction, upstream of training.
  - *Selection:* programmatic weak supervision → Snorkel; human-in-the-loop GUI → Label Studio; simple annotation → doccano.
  - *Risks:* label-quality and bias propagation (see Responsible chapters).
  - *Alternatives:* Label Box, Argilla, Prodigy (commercial).

#### B6. Data versioning — DVC, Dolt, pachyderm
- **Vol1 Ch4 Data Engineering · Ch3 ML Workflow · Chip Ch3 · Ch8 Monitoring (lineage)**
  - *Rationale:* reproducible data + model versions; the guide's flagship data tool is DVC.
  - *Stage:* Data → Train. *Signal:* "which dataset produced this model?" reproducibility failures.
  - *Boundary:* object-store-backed data versioning (not file-level git for big data).
  - *Selection:* git-integrated → DVC; SQL git → Dolt; pipeline+versioning → pachyderm.
  - *Risks:* large-binary handling, remote storage costs.
  - *Alternatives:* LakeFS, Databricks Delta, Pandas/Feather in object storage.

#### B7. Metadata stores — Amundsen, DataHub
- **Chip Ch1 Overview · Ch2 Design · Vol1 Ch2 ML Systems**
  - *Rationale:* feature/model discovery and lineage.
  - *Stage:* Govern/Maintain. *Signal:* can't discover what features/models exist or their provenance.
  - *Boundary:* data-discovery layer over existing warehouses/pipelines.
  - *Selection:* Lyft ecosystem → Amundsen; broad enterprise metadata → DataHub.
  - *Risks:* adoption requires data-discipline culture.
  - *Alternatives:* OpenMetadata, Data Catalog services.

#### B8. Feature store — FEAST
- **Chip Ch10 Infra/Tooling · Ch7 Model Deployment · Ch8 Monitoring · Vol1 Ch4**
  - *Rationale:* unify training and serving features to prevent train/serve skew (a Chip Huyen theme).
  - *Stage:* Data → Serve. *Signal:* inconsistent features between train and online inference.
  - *Boundary:* feature computation/storage shared by train and serve.
  - *Selection:* OSS self-host → FEAST; managed → cloud feature stores.
  - *Risks:* added latency hop; operational overhead.
  - *Alternatives:* Tectonic, Feast Cloud, Hologres, Redis-backed custom.

#### B9. Data pipelines — ploomber, hamilton, NVTabular, Arrow/flight
- **Vol1 Ch3 ML Workflow · Ch4 Data Engineering · Vol2 Ch4 · Ch5 Distributed Training · Chip Ch3**
  - *Rationale:* orchestrate reproducible data→feature→training DAGs.
  - *Stage:* Data→Train. *Signal:* fragile ad-hoc scripts; no DAG lineage.
  - *Boundary:* offline pipeline construction, not serving runtime.
  - *Selection:* DAG+dependency viz → hamilton; notebook/script pipelines → ploomber; GPU feature prep → NVTabular; interchange → Arrow/flight.
  - *Risks:* NVTabular deprecated-era; over-engineering small pipelines.
  - *Alternatives:* Airflow, Dagster, Prefect, Spark.

---

### Group C — Interpretability & fairness (SHAP, Lime, Interpret, lit, captum, timeshap, AIX360, AIF360)

**Maps to:** Vol1 Ch15 Responsible Engineering · Vol2 Ch14 Robust AI · Ch16 Responsible AI · Chip Ch11 Human Side · Ch8 Monitoring

- **Vol1 Ch15 Responsible Engineering**
  - *Rationale:* explainable predictions and bias detection are core to responsible design.
  - *Stage:* Govern/Monitor. *Signal:* need model explanations for stakeholders; fairness audits.
  - *Boundary:* post-hoc explanation; not part of the inference graph.
  - *Selection:* unified tabular/tabular+image → Interpret; per-feature attribution → SHAP; Lime for sampling-based; captum for PyTorch models.
  - *Risks:* explanations can be misleading/unstable.
  - *Alternatives:* ELI5, Captum, Alibi.
- **Vol2 Ch14 Robust AI · Ch16 Responsible AI**
  - *Rationale:* fairness tooling (AIF360, AIX360) audits for protected-class outcomes.
  - *Stage:* Govern. *Signal:* regulatory/ethical fairness requirements.
  - *Selection:* metric-based fairness audits → AIF360; modular explainability → AIX360.
  - *Risks:* fairness metrics conflict; measurement window matters.
  - *Alternatives:* Fairlearn, Microsoft InterpretML.
- **Chip Ch8 Monitoring · Ch11 Human Side**
  - *Rationale:* `lit` for NLP dataset/model inspection; SHAP/timeshap for production monitoring of NLP & time-series.
  - *Stage:* Monitor. *Signal:* NLP input drift; time-series concept drift.
  - *Selection:* NLP-focused → lit; time-series attribution → timeshap.
  - *Risks:* domain-specific; may not generalize across modalities.
  - *Alternatives:* What-If Tool, Alibi Detect.

---

### Group D — Model development & evaluation (MLflow, aim; TVM/TensorRT/Triton/hummingbird/composer; DeepSpeed/accelerate; PySyft/FedML/FATE/TF-Federated; checklist/reclist; growthbook/Ax)

**Maps to:** Vol1 Ch7 ML Frameworks · Ch8 Model Training · Ch10 Compression · Ch12 Benchmarking · Ch13 Serving · Chip Ch5·6·7·9

#### D1. Experiment tracking — MLflow, aim
- **Chip Ch5 Model Development and Offline Evaluation · Vol1 Ch8 Model Training · Ch3 ML Workflow**
  - *Rationale:* track runs, params, metrics, artifacts — the guide flags hosting artifacts as the hard part.
  - *Stage:* Train→Tune/Eval. *Signal:* untracked experiments; irreproducible runs.
  - *Boundary:* run logging + model registry; not training compute itself.
  - *Selection:* all-in-one OSS → MLflow; dev-friendly UI → aim.
  - *Risks:* server hosting burden; registry locking.
  - *Alternatives:* Weights & Biases, Neptune, ClearML, Kubeflow Experiments.

#### D2. Model optimization — TVM, TensorRT, Triton, hummingbird, composer
- **Vol1 Ch10 Model Compression · Ch11 Hardware Acceleration · Ch12 Benchmarking · Ch13 Serving · Vol2 Ch9 Performance Engineering · Ch10 Inference at Scale**
  - *Rationale:* compile/optimize graphs, quantize, and serve efficiently on target hardware.
  - *Stage:* Tune/Eval → Serve. *Signal:* latency/throughput/latency-budget failures on target hardware.
  - *Boundary:* compile-time optimization (TVM/TensorRT/hummingbird) + inference server (Triton).
  - *Selection:* vendor GPU → TensorRT; portable compiler → TVM; inference serving → Triton; sklearn→torch → hummingbird; training optimization → composer.
  - *Risks:* hardware/vendor lock-in; numerical precision surprises.
  - *Alternatives:* ONNX Runtime, OpenVINO, torch.compile, llama.cpp, vLLM.

#### D3. Distributed training — DeepSpeed, accelerate
- **Vol1 Ch8 Model Training · Vol2 Ch5 Distributed Training · Ch6 Collective Communication · Chip Ch5·6**
  - *Rationale:* scale training across devices/nodes; the guide's "super cool" tool is DeepSpeed.
  - *Stage:* Train. *Signal:* OOM on single GPU; long epoch times.
  - *Boundary:* training-time parallelism; separate from serving.
  - *Selection:* deep, flexible control → DeepSpeed; HF-ecosystem simplicity → accelerate.
  - *Risks:* correctness pitfalls (memory offload, gradient accumulation); steep learning curve.
  - *Alternatives:* FSDP, Megatron-LM, Deepspeed, PyTorch DDP/DeepSpeed ZeRO, Ray Train.

#### D4. Federated learning — PySyft, FedML, FATE, TensorFlow Federated
- **Vol2 Ch13 Security & Privacy · Ch14 Robust AI · Vol1 Ch15 Responsible**
  - *Rationale:* train across data silos without centralizing private data.
  - *Stage:* Train (privacy-preserving). *Signal:* data-sovereignty/privacy constraints prevent centralization.
  - *Boundary:* cross-institution training; not for single-org data.
  - *Selection:* Python framework → PySyft; production FL → FATE; HF-style → FedML; TF ecosystem → TF-Federated.
  - *Risks:* security/privacy guarantees are easy to misconfigure; slow adoption.
  - *Alternatives:* OpenFL, NVIDIA FLare, Syft's successors.

#### D5. Evaluation — checklist, reclist, deepchecks
- **Chip Ch6 Model Development and Offline Evaluation · Vol1 Ch12 Benchmarking · Ch15 Responsible**
  - *Rationale:* systematic, adversarial evaluation beyond aggregate metrics.
  - *Stage:* Tune/Eval. *Signal:* misleading aggregate scores; untested failure modes.
  - *Boundary:* offline evaluation; complement to production monitoring.
  - *Selection:* NLP checklists → checklist; recommender → reclist; general ML → deepchecks.
  - *Risks:* checklist coverage is effortful and author-dependent.
  - *Alternatives:* RATTLESNAKE, HF axolotl evals, Promptfoo.

#### D6. Online experiments — growthbook, Ax
- **Chip Ch9 Continual Learning and Test in Production · Ch10 Inference at Scale · Ch13 Serving**
  - *Rationale:* A/B, canary, and multi-armed bandit experimentation in production.
  - *Stage:* Serve→Monitor (Test in Production). *Signal:* need to validate model changes live before full rollout.
  - *Boundary:* experiment platform; separate from model serving.
  - *Selection* OSS A/B → growthbook; Bayesian optimization + experiments → Ax.
  - *Risks:* experiment contamination; statistical misuse.
  - *Alternatives:* Optimizely, Evidently, Meta Test-and-Learn.

---

### Group E — Use-case-specific frameworks

**Maps to:** Vol1 Ch6 Network Architectures · Ch13 Serving · Chip Ch5·6·7 (by use case)

- **Recommenders / CTR — DLRM, DeepCTR, tensorflow-DeepFM, Transformers4Rec**
  - *Chips Ch5·6 · Vol1 Ch6 · Ch13 Serving* — *Rationale:* CTR/embedding-heavy models; *Stage:* Train→Serve. *Selection:* match to framework familiarity. *Risks:* niche maintenance. *Alt:* LightFM, implicit, Vowpal Wabbit.
- **Conversational AI — rasa, NeMo**
  - *Chip Ch2 Design · Ch7 Deployment* — *Rationale:* dialogue systems. *Risks:* vendor vs OSS tradeoffs. *Alt:* LangChain/LlamaIndex, Microsoft Bot Framework.
- **Similarity search — annoy, Faiss, Milvus**
  - *Vol1 Ch13 Serving · Vol2 Ch4 Data Storage · Ch10 Inference at Scale* — *Rationale:* ANN serving for embeddings. *Stage:* Serve. *Selection:* in-memory → annoy; GPU-scale → Faiss; managed vector DB → Milvus. *Risks:* index rebuild cost. *Alt:* Qdrant, Weaviate, Pinecone, Milvus.
- **Deepfakes — faceswap, deepface** — *Conceptual/guardrail topic*; maps to **Vol2 Ch14 Robust AI · Ch13 Security** as misuse-risk discussion, not adoption.
- **Time-lagged conversion — convoys; Churn — WTTE-RNN; Survival — lifelines**
  - *Chip Ch4·6 · Vol1 Ch15 Responsible (model choice)* — *Rationale:* specialized statistical/ML models. *Stage:* Train/Eval. *Selection:* match to problem; *Risks:* narrow scope, maintenance. *Alt:* scikit-learn survival, PyTorch Survival.

---

### Group F — Dev environment (fzf, lipgloss, VSCode, Poetry, Hydra, gin-config, docusaurus, k9s, excalidraw)

**Maps to:** Chip Ch1 Overview · Ch2 Design · Ch10 Infra/Tooling · Vol1 Ch2 ML Systems · Ch3 ML Workflow · Vol2 Ch2 Compute Infrastructure

- *Rationale:* these are **productivity/dev-experience** tools, not MLOps lifecycle tools. They support the *whole* workflow rather than one stage.
- **Chip Ch10 Infrastructure and Tooling for MLOps** — strongest mapping: dev environment setup, standardizing environments, containers.
  - *Selection:* deps → Poetry; config/hyperparams → Hydra/gin-config; docs → docusaurus; k8s debugging → k9s; IDE → VSCode.
  - *Risks:* low stakes but easy to under-standardize across teams.
  - *Alternatives:* uv/poetry-core, Cookiecutter, Docker/Podman, Skaffold.
- **fzf/lipgloss/excalidraw** — **conceptual / no direct tool** in the lifecycle sense; dev-productivity only.

---

### Group G — DevOps for MLOps (earthly; Sentry, Prometheus, vector, M3; Grafana, Metabase; Chaos Monkey, k6)

**Maps to:** Vol1 Ch14 ML Operations · Vol2 Ch7 Fault Tolerance · Ch8 Fleet Orchestration · Ch9 Performance Engineering · Ch12 ML Operations at Scale · Chip Ch8 Monitoring · Ch9 Test in Production

- **CI/CD — earthly**
  - *Vol1 Ch14 · Vol2 Ch8 · Chip Ch10* — *Stage:* Deploy. *Signal:* non-reproducible builds. *Risks:* niche. *Alt:* GitHub Actions, Tekton, Argo CD, Buildkite.
- **Monitoring — Sentry, Prometheus, vector, M3**
  - *Chip Ch8 Monitoring · Vol1 Ch14 · Vol2 Ch12* — *Stage:* Monitor. *Signal:* need infra + ML metric collection; SLO alerting. *Selection:* app errors → Sentry; time-series → Prometheus/M3; log/shipping → vector. *Risks:* alert fatigue. *Alt:* Datadog, Elastic, Grafana Faro.
- **Dashboards — Grafana, Metabase**
  - *Stage:* Monitor. *Signal:* need shared observability UI. *Alt:* Superset, Kibana.
- **General DevOps — Chaos Monkey, k6**
  - *Vol2 Ch7 Fault Tolerance · Ch9 Performance Engineering* — *Rationale:* resilience (chaos) and load testing. *Stage:* Serve/Monitor. *Alt:* LitmusChaos, k6 (already listed), Locust.

---

### Group H — Conceptual / no direct tool (deliberate nulls)

The following chapter concerns are real but have **no clean single-tool mapping** in the historical inventory; record them as conceptual:

- **Vol1 Ch1 Introduction · Ch16 Conclusion** — synthesis/roadmap; no tool.
- **Vol1 Ch5 Neural Computation** (core math) — conceptual; tools only touch preprocessing.
- **Vol1 Ch6 Network Architectures** — design is research/choice; frameworks (Ch7) implement it, no dedicated "architecture" tool.
- **Vol1 Ch7 ML Frameworks** — the chapter *is* about frameworks (PyTorch/TF); it's meta, so map *to* frameworks rather than *from* a tool.
- **Vol1 Ch9 Data Selection** — conceptual (data-centric selection policy); partially served by HF datasets + Group B versioning, but no single named tool in the guide.
- **Vol1 Ch11 Hardware Acceleration** — hardware, not software tool; conceptual + benchmarking (Ch12).
- **Vol2 Ch3 Network Fabrics · Ch6 Collective Communication** — hardware/collective primitives; conceptual, surfaced via DeepSpeed/FSDP (D3) rather than a dedicated tool.
- **Vol2 Ch7 Fault Tolerance · Ch8 Fleet Orchestration** — operational practice; supported by Prometheus/Grafana/Chaos Monkey (Group G) but no single "FT tool."
- **Vol2 Ch11 Edge Intelligence** — deployment target; tools are compilers/quantizers (D2) + on-device runtimes (conceptual: TFLite, Core ML, ONNX Runtime Mobile — not in guide).
- **Vol2 Ch15 Sustainable AI · Ch16 Responsible AI** — measurement/governance concepts; partially SHAP/AIF360 (C) and benchmarking (Ch12), but no dedicated tool.
- **Chip Ch11 The Human Side** — UX/team-structure/responsible-AI process; **conceptual**, supported by dashboards + fairness tools, no single tool.
- **Chip Ch1 Overview · Ch2 Design** — framing/methodology; metadata stores (B7) and dashboards partially support, mostly conceptual.

---

## 4. Cross-cutting lifecycle coverage summary

| Lifecycle stage | Primary chapters | Representative mapped tools |
|---|---|---|
| Data | Vol1 Ch3·4 · Vol2 Ch4 · Chip Ch3·4 | DVC, Great Expectations, Label Studio, Polars/dask, FEAST, Amundsen/DataHub |
| Train | Vol1 Ch5·6·7·8 · Vol2 Ch5·6 · Chip Ch5·6 | MLflow, DeepSpeed, accelerate, Hydra, NVTabular |
| Tune / Eval | Vol1 Ch10·12 · Vol2 Ch9 · Chip Ch5·6 · Fregly Ch1·10·12 | TVM/TensorRT/Triton, checklist/reclist, hummingbird, Ax, profiler/CI benchmark jobs |
| Deploy | Vol1 Ch13 · Vol2 Ch2·8 · Chip Ch7 · Fregly Ch3 | earthly, Triton, FEAST, compilers (D2), Docker/Kubernetes topology controls |
| Serve | Vol1 Ch13 · Vol2 Ch9·10 · Chip Ch7·9 | Faiss/Milvus, Triton, growthbook, k6 |
| Monitor | Vol1 Ch14 · Vol2 Ch12 · Chip Ch8 · Fregly Ch1–4·10·12 | ClickHouse/Druid, Prometheus, Sentry, Grafana, deepchecks, nvidia-smi/profiler telemetry |
| Govern/Maintain | Vol1 Ch15 · Vol2 Ch13·14·15·16 · Chip Ch11 | AIF360, SHAP, DataHub, Metabase |

---

## 5. Discovery & validation plan (repeatable)

A living process to keep this mapping accurate. Owner rotates quarterly.

1. **Maintenance**
   - Re-run targeted reads of the three corpora (per line boundaries in §0.1) to confirm chapter titles/content are unchanged.
   - Re-read `/tmp/mlops-tools.md` and any PRs/issues to its source repo for new/retired tools.
   - Keep a changelog at the top of this file with date, editor, and what changed.
2. **License & security**
   - Before promoting any tool to "recommended," verify its license (Apache-2.0 / MIT / GPL implications) and scan for known CVEs (OSV/GHSA).
   - Re-confirm the corpus licenses (CC-BY-NC-ND for MIT Press; © O'Reilly for Chip Huyen) and the no-AI-training clause.
3. **Compatibility**
   - Check Python/version, framework (PyTorch vs TF vs JAX), hardware (NVIDIA/AMD/Apple Silicon), and cloud/air-gapped constraints.
   - Confirm inter-tool fit (e.g., FEAST + Prometheus + Grafana; MLflow registry + Triton server).
4. **Proof of concept**
   - Define a minimal but representative workload per tool; measure setup time, docs quality, and a core success metric before adoption.
5. **Representative benchmarks**
   - Use vendor-neutral, workload-matched benchmarks (e.g., H2O DB benchmark for tabular; MLPerf for training/inference; ANN benchmarks for Faiss/Milvus).
   - Record hardware + data-size context, since benchmarks are meaningless without it.
6. **Data & model lineage**
   - Ensure every mapped tool integrates with versioning/registry (DVC, MLflow registry, DataHub) so lineage from raw data → model → serving is auditable.
7. **Rollback**
   - For each deploy/serve/monitor tool, document the revert path: model registry rollback, feature-store versioning, CI/CD rollback, and data-rollback (DVC/LakeFS).
8. **Periodic re-evaluation**
   - **Quarterly:** license/CVE/compatibility sweep. **Semi-annually:** benchmark refresh + tool-drift review (archived/renamed/deprecated?). **Annually:** re-survey meta-lists (§1.1) for new tools; re-validate the "conceptual" nulls in case a category matured.

---

## 6. Modern MLOps / LLMOps refresh and actionable worklist

**Research method and status.** This section is a bounded refresh, not a replacement for the historical inventory above. On **2026-09-02**, Exa was used to fetch the official documentation pages linked in §6.5. The capabilities below are short, source-grounded descriptions of those pages; they are not adoption, quality, benchmark, or security claims. Verify release versions, licenses, CVEs, deployment requirements, and project health before committing to a production dependency.

### 6.1 Component model and selection rules

Use the component boundary—not the product name—as the design unit. Pick at most one primary tool per overlapping row for the first proof of concept, and keep the integration contract explicit.

1. **Data plane:** ingestion, transformation, storage, versioning, validation, labeling, features, retrieval.
2. **Training plane:** workflow execution, distributed compute, experiment/artifact/model registry, reproducibility.
3. **Serving plane:** model runtime, gateway/routing, rollout, autoscaling, latency/cost controls.
4. **Quality plane:** offline evaluation, regression tests, online feedback, drift, tracing, dashboards.
5. **Control plane:** metadata/lineage, identity, quotas, policy, auditability, rollback, and ownership.
6. **Selection gates:** workload fit (batch/online/agent), SLOs (quality, p95/p99 latency, TTFT/TPOT, throughput, availability), data residency, hardware, Kubernetes/cloud posture, operator burden, license, API/telemetry openness, and a measured rollback path.

Do not equate a broad feature checklist with a complete platform. A tool is a fit only when a representative workload demonstrates the required signal, failure behavior, and operating cost.

Exa also surfaced newer or less-established projects such as LLMTrace, PromptLedger, GuardLayer, Agnos Proxy, and SMG. They are **research candidates, not recommendations**: do not select one from a search snippet. First audit its repository history, release process, license, SBOM/CVEs, tests, documentation, governance, interoperability, and bus factor against the same gates.

### 6.2 MLOps shortlist

| Component | First candidate | Use it when / verified capability | Conditional alternatives | First proof-of-concept and exit signal |
|---|---|---|---|---|
| Workflow orchestration and data lineage | [Dagster](https://docs.dagster.io/) | Asset-oriented data orchestration with integrated lineage, observability, declarative definitions, and testability. | [Flyte](https://flyte.org/) for Kubernetes-native typed and immutable workflows; [Kestra](https://kestra.io/docs) for declarative, language-agnostic, event-driven data/AI/infrastructure workflows; [Metaflow](https://docs.metaflow.org/) for a Python-centric, scientist-friendly AI/ML lifecycle; [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/) for reusable Kubernetes pipeline components. | Run a data→feature→train DAG twice from a pinned input; require reproducible outputs, visible lineage, retry behavior, and an owner-readable failure. |
| Data-lake versioning and rollback | [lakeFS](https://docs.lakefs.io/project/) | Git-like branching/versioning over object-store data lakes/lakehouses; the project documentation states the open-source project is Apache-2.0. | DVC, Dolt, Pachyderm, or table-format/time-travel facilities when the storage and pipeline boundary already dictates one. | Branch a dataset, run validation/training, promote only the passing branch, and restore the prior version without copying the lake. |
| Data contracts and validation | [Great Expectations / GX Core](https://docs.greatexpectations.io/docs/) | Declarative expectations and dataset validation at pipeline boundaries. | Pandera for Python/schema-first checks; [Evidently](https://docs.evidentlyai.com/) for data/AI evaluation, drift, and monitoring. | Fail CI on schema, null-rate, range, and freshness violations; record the expectation version with the run and test a backward-compatible change. |
| Data/AI drift and production quality | [Evidently](https://docs.evidentlyai.com/) | OSS Python library with a broad metric catalogue, testing API, and a self-hostable platform for evaluations, traces, datasets, and dashboards. | Phoenix or Langfuse for LLM-centric traces/evals; Prometheus/Grafana for infrastructure signals. | Compare a known-good reference with shifted data and a degraded model; require an actionable alert with a link to the affected slice, not only a global score. |
| Offline/online feature management | [Feast](https://docs.feast.dev/) | Offline historical retrieval plus low-latency online serving, with feature definitions and a feature server; it manages features over existing stores rather than replacing the database. | A warehouse-native feature layer or a narrowly scoped service when online features are not required. | Prove point-in-time-correct training retrieval, online freshness, train/serve parity, and p99 lookup latency. Do not adopt Feast for a batch-only model without a demonstrated need. |
| Metadata, catalog, and lineage context | [OpenMetadata](https://open-metadata.org/) | Open metadata/context graph for data assets, pipelines, models, ownership, lineage, quality, and integrations; its site documents API/schema-driven extensibility and broad connectors. | DataHub or a cloud catalog when existing governance and connector coverage outweigh self-hosting. | Register one end-to-end asset graph (lakeFS→Dagster→MLflow→serving); require owners, lineage, classifications, and a deletion/access policy. |
| Experiment, artifact, and model registry | [MLflow](https://mlflow.org/docs/latest/) | Tracking/registry foundation; current MLflow GenAI docs also cover traces, evaluation, and an immutable, versioned prompt registry. | W&B, ClearML, Aim, or a cloud registry when collaboration, hosted scale, or existing platform integration is decisive. | Rebuild a model from a run’s code/config/data/model references; promote, canary, and roll back by immutable version with audit evidence. |
| Distributed training | [Ray Train](https://docs.ray.io/en/latest/train/train.html) | Scales training/fine-tuning from one machine to clusters and integrates with PyTorch, Transformers, Accelerate, DeepSpeed, and other frameworks. | DeepSpeed/FSDP/Megatron when low-level training control or a framework-specific optimizer is the actual bottleneck. | Scale the same job from one node to two; measure useful throughput, recovery after worker loss, checkpoint correctness, and communication overhead. |
| GPU quota, admission, and fleet scheduling | [Kueue](https://kueue.sigs.k8s.io/docs/overview/) | Kubernetes-native queueing, quotas, priority/preemption, fair sharing, resource flavors, topology-aware scheduling, and integrations for training/Ray workloads; it can coordinate training and serving workloads. | Volcano, Slurm, or managed schedulers if the platform already standardizes on them. | Submit competing training/inference jobs; verify fairness, preemption/recovery, GPU utilization, pending-work visibility, and no starvation of serving traffic. |
| Predictive-model serving | [KServe](https://kserve.github.io/website/) `InferenceService` | Kubernetes serving control plane for conventional predictive models, with a separate LLM-oriented API path in current docs. | BentoML, Triton, Seldon, or a simpler container service outside Kubernetes. | Deploy two model versions with readiness, autoscaling, traffic split, metrics, and rollback; measure p95/p99 latency under representative concurrency. |
| Telemetry and infrastructure observability | [OpenTelemetry](https://opentelemetry.io/docs/) + Prometheus/Grafana | OTel supplies vendor-neutral traces, metrics, logs, and a collector; Prometheus/Grafana supply familiar time-series collection and dashboards. | A managed observability suite where retention, support, or compliance is the primary constraint. | Correlate one request/run across pipeline, registry, serving, GPU, and user-feedback signals; exercise sampling, cardinality, retention, and alert routing. |
| Performance and load regression | [k6](https://grafana.com/docs/k6/latest/) plus profiler/GPU telemetry | Load and failure testing belongs beside Fregly’s diagnosis-first performance workflow; collect goodput, utilization, queueing, memory, power, and cost—not GPU utilization alone. | Locust, benchmark-specific harnesses, vendor profilers, or MLPerf where the workload is comparable. | Gate a release on workload-matched p95/p99, throughput/goodput, error rate, warm/cold behavior, and cost per useful prediction/token. |

### 6.3 LLMOps shortlist

| Component | First candidate | Use it when / verified capability | Conditional alternatives | First proof-of-concept and exit signal |
|---|---|---|---|---|
| Provider gateway, routing, budgets, and fallbacks | [LiteLLM](https://docs.litellm.ai/docs/) | Unified OpenAI-format access to many providers, retry/fallback routing, and a self-hostable proxy with virtual keys, spend tracking, guardrails, and caching. | Cloud-native API gateways, provider-native routers, or a small internal adapter when only one provider is allowed. | Route identical traffic through two providers; verify key/team budgets, rate limits, retries, fallback semantics, per-request cost, redaction, and audit logs. |
| LLM/agent tracing and iteration platform | [Langfuse](https://langfuse.com/docs) **or** [Phoenix](https://arize.com/docs/phoenix) | Langfuse is an open/self-hostable platform covering LLM and non-LLM traces, sessions, prompts, datasets, feedback, and evaluations. Phoenix is OTel/OpenInference-based and covers traces, evaluators, prompts, datasets, and experiments. Choose one primary UI/store initially. | MLflow GenAI for a unified ML+GenAI control plane; Traceloop/OpenLLMetry when instrumentation is the main gap. | Instrument a RAG/agent request end-to-end (retrieval, embeddings, tools, model calls); require trace completeness, token/cost/latency fields, dataset replay, and one reproducible regression comparison. |
| Vendor-neutral LLM instrumentation | [OpenLLMetry](https://www.traceloop.com/docs/openllmetry/getting-started) | Traceloop’s SDK uses OpenTelemetry to trace LLM applications and offers Python/TypeScript paths plus a proxy/platform option. | Native OpenInference integrations in Phoenix, Langfuse SDKs, or MLflow autologging. | Verify semantic-convention coverage for prompts, completions, tool calls, retrieval, errors, and sensitive-field redaction through the chosen collector/backend. |
| Prompt/model/RAG regression and red teaming | [promptfoo](https://www.promptfoo.dev/docs/intro/) | Open-source CLI/library for LLM evaluation and red teaming, declarative cases, metrics, caching/concurrency, multiple providers, and CI/CD use. | [DeepEval](https://deepeval.com/docs/getting-started) for Python/TypeScript test integration and agent trajectories; Ragas for RAG/agent metrics and experiment loops. | Store a small versioned failure set; run it in CI against prompt/model changes; block only on agreed thresholds and preserve inputs, outputs, rubric, judge model, and cost. |
| RAG and agent evaluation | [Ragas](https://docs.ragas.io/en/stable/) | Experiments-first evaluation with metrics, datasets, testset generation, RAG and agent-oriented use cases. | Phoenix evaluators, MLflow scorers, or DeepEval metrics when those already own the trace/eval store. | Evaluate retrieval recall/precision proxies, groundedness, answer quality, tool/task completion, and judge agreement on a labeled slice; do not use one LLM score as the sole release gate. |
| Safety, structured output, and I/O validation | [Guardrails AI](https://guardrailsai.com/docs/) | Python framework for input/output guards that detect/mitigate risks and for structured data generation, with reusable validators. | NeMo Guardrails, provider-native structured output, policy engines, or gateway-level filters. | Test malformed output, prompt injection, PII, unsafe content, refusal, retry, and fail-closed behavior; measure added latency and log every intervention. |
| Embedding/vector retrieval | [Qdrant](https://qdrant.tech/documentation/) | Vector search with payload filtering, hybrid/multimodal search, quantization, multitenancy, distributed deployment, snapshots, and Prometheus/Grafana telemetry documented in its current docs. | Milvus, Faiss, Weaviate, or a database-native vector index when query/operational constraints differ. | Build an index rebuild/rollback path; measure recall@k and answer quality by slice, write/read durability, filter correctness, p99 search latency, memory, and tenant isolation. |
| Local/high-throughput LLM inference | [vLLM](https://docs.vllm.ai/en/latest/) | High-throughput serving with PagedAttention, continuous batching, chunked prefill, prefix caching, quantization, distributed parallelism, and OpenAI-compatible APIs. | [SGLang](https://docs.sglang.ai/) for a different high-performance runtime and caching/scheduling trade-off; [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/) for NVIDIA-specific optimization and runtime control. | Benchmark the same model/request mix across engines; report TTFT, TPOT, p50/p95/p99 latency, throughput/goodput, KV-cache pressure, quality parity, startup/recovery time, and cost. |
| Kubernetes-scale LLM serving and routing | [KServe `LLMInferenceService`](https://kserve.github.io/website/docs/model-serving/generative-inference/llmisvc/llmisvc-overview) with [llm-d](https://llm-d.ai/docs/dev/architecture/core/model-servers) | Current docs describe an LLM-specific Kubernetes CRD and llm-d architecture for distributed inference, intelligent/KV-cache-aware routing, prefill/decode patterns, and vLLM/SGLang/TensorRT-LLM model servers. Treat the API/docs maturity and compatibility matrix as adoption gates. | Direct vLLM/SGLang deployment, Triton/TensorRT-LLM, managed inference, or a simpler KServe `InferenceService` for small single-node workloads. | Deploy one model with a real Gateway API route and one model-server pool; test queue/KV-cache-aware routing, scaling, multi-node failure, upgrade/rollback, and metrics before adding disaggregated serving. |

### 6.4 Recommended order of work

This is the project todo derived from the component map. It intentionally favors small, measurable integrations over installing a complete platform at once.

1. **Write the workload contract.** Document batch vs online vs RAG/agent traffic, data sensitivity, hardware/Kubernetes constraints, SLOs, quality slices, rollback owner, and success metrics (including TTFT/TPOT or goodput where applicable).
2. **Build the MLOps spine.** Choose one orchestrator (Dagster, Flyte, Kestra, Metaflow, or Kubeflow Pipelines) and prototype a representative pipeline with lakeFS, GX Core, MLflow, and OTel; add Evidently and OpenMetadata only after the lineage/quality signals have a consumer.
3. **Prove registry-to-serving rollback.** Register an immutable model, deploy it through KServe or a minimal service, run a canary/load test, link telemetry, and restore the prior model/data versions.
4. **Add GPU scheduling/training only when demanded.** Compare Ray Train plus Kueue against the existing DeepSpeed/FSDP path using a two-node workload, worker-loss recovery, checkpointing, fair sharing, and useful-throughput evidence.
5. **Build the LLM gateway boundary.** Use LiteLLM to exercise provider routing, budgets, fallback, rate limits, redaction, caching, and cost attribution; keep application code on an OpenAI-compatible contract.
6. **Instrument one RAG/agent application.** Compare Langfuse and Phoenix on trace completeness, self-hosting, OpenTelemetry interoperability, retention, and the ability to replay production failures without leaking sensitive data. Select one primary backend.
7. **Create an eval release gate.** Combine promptfoo CI with either DeepEval, Ragas, Phoenix, or MLflow scorers. Version datasets and prompts; include deterministic checks, LLM judges, human labels, and slice-level thresholds; test judge instability.
8. **Add safety controls before exposure.** Put Guardrails AI or an equivalent validator at explicit input/output boundaries; test injection, PII, structured-output failures, safe refusal, retry loops, fail-closed behavior, and latency.
9. **Benchmark inference engines.** Compare vLLM, SGLang, and—on NVIDIA hardware—TensorRT-LLM under identical model, quantization, context, concurrency, and streaming workloads. Record quality parity and full cost, not vendor peak numbers.
10. **Scale to Kubernetes only after the single-node path is understood.** Evaluate KServe `LLMInferenceService`/llm-d for routing, distributed/prefill-decode, and autoscaling; do not introduce it solely because the model is an LLM.
11. **Add Feast only for an online feature requirement.** Prove point-in-time retrieval and serving latency before accepting another operational store.
12. **Run a quarterly refresh.** Recheck official docs, release/maintenance activity, licenses, CVEs, API stability, and the benchmark matrix; archive rejected tools with the reason and date.

### 6.5 Evidence links

The official pages used for this refresh are:

- MLOps foundation: [Dagster](https://docs.dagster.io/), [Flyte](https://flyte.org/), [lakeFS](https://docs.lakefs.io/project/), [Feast](https://docs.feast.dev/), [Evidently](https://docs.evidentlyai.com/), [GX Core](https://docs.greatexpectations.io/docs/), [MLflow](https://mlflow.org/docs/latest/), [Ray Train](https://docs.ray.io/en/latest/train/train.html), [Kueue](https://kueue.sigs.k8s.io/docs/overview/), [OpenMetadata](https://open-metadata.org/), [OpenTelemetry](https://opentelemetry.io/docs/), [k6](https://grafana.com/docs/k6/latest/), [Kestra](https://kestra.io/docs), [Metaflow](https://docs.metaflow.org/), [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/).
- LLMOps foundation: [LiteLLM](https://docs.litellm.ai/docs/), [Langfuse](https://langfuse.com/docs), [Phoenix](https://arize.com/docs/phoenix), [OpenLLMetry](https://www.traceloop.com/docs/openllmetry/getting-started), [promptfoo](https://www.promptfoo.dev/docs/intro/), [DeepEval](https://deepeval.com/docs/getting-started), [Ragas](https://docs.ragas.io/en/stable/), [Guardrails AI](https://guardrailsai.com/docs/), [Qdrant](https://qdrant.tech/documentation/).
- Inference: [vLLM](https://docs.vllm.ai/en/latest/), [SGLang](https://docs.sglang.ai/), [TensorRT-LLM](https://nvidia.github.io/TensorRT-LLM/), [KServe LLMInferenceService](https://kserve.github.io/website/docs/model-serving/generative-inference/llmisvc/llmisvc-overview), [llm-d model servers](https://llm-d.ai/docs/dev/architecture/core/model-servers).

## 7. Caveats (reiteration)

- **Tool drift:** all entries are a snapshot; re-validate before use (§5 and §6.4).
- **Bias in sources:** meta-lists (§1.1) are vendor-sponsored; treat them as leads, not truth. Official project documentation is evidence of stated capability, not independent validation.
- **Copyright:** this plan quotes only titles/names/links; do not reproduce or train on corpus text. Verify license for any downstream use.
- **Historical links:** the historical inventory was produced offline; re-check every historical URL. Modern-refresh URLs were fetched through Exa on 2026-09-02 and must also be re-checked at adoption time.
- **"Conceptual" is intentional:** absence of a tool is a finding, not an omission.
