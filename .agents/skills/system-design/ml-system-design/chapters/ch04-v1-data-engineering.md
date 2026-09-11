# Chapter 4: Data Engineering

**Source**: Introduction to Machine Learning Systems — Vijay Janapa Reddi (Vol. 1), Chapter 4

## Core Idea
Data is the source code of an ML system and also a physical workload. Data engineering determines what the model can learn, how fast training can be fed, whether training and serving agree, and whether behavior remains traceable and governable.

## Frameworks Introduced
- **Four Pillars Framework**: Organize data systems around Quality, Reliability, Scalability, and Governance.
- **Data Cascades**: Upstream collection and labeling defects amplify through preparation, training, evaluation, and production.
- **Training-Serving Consistency**: Reuse equivalent feature semantics and learned state, such as normalization constants or vocabularies, across both paths.
- **Data-as-Code Principle**: Version, test, review, document, and debug datasets with software-like rigor.

## Key Concepts
- **Dataset compilation**: Turning raw sources into a curated, ML-ready corpus.
- **Data gravity**: Large or high-value data attracts computation and makes movement costly.
- **Feeding tax**: The time and resources required to retrieve, decode, transform, and deliver examples to accelerators.
- **Data pipeline**: Ingestion, validation, processing, labeling, storage, and lineage components.
- **Data drift**: Divergence between production and reference distributions; divergence alone does not prove outcome degradation.
- **Feature store**: A managed system for consistent feature computation and access.
- **Data debt**: Accumulated cost from missing documentation, schema, quality, or freshness practices.
- **Operational data health**: Ongoing checks for freshness, validity, coverage, and distribution changes.

## Mental Models
Treat a dataset like a program plus a supply chain. Use the Four Pillars as a review checklist: Is the signal correct, can the pipeline recover, can it grow, and are consent and accountability explicit? Choose batch or streaming based on the value of freshness, not the appeal of real time. Match storage to access pattern: databases serve operational reads, warehouses support curated analytics, and lakes retain heterogeneous raw data. Drift is an investigation trigger; pair it with labels or validated proxies before declaring model degradation.

## Anti-patterns
- **“Clean once” pipelines**: Data quality changes as sources, schemas, sensors, and populations change.
- **Training-only transformations**: Separate feature logic creates silent training-serving skew.
- **Real-time by default**: Streaming adds operational cost and complexity when batch freshness is sufficient.
- **Storage trend-following**: A fashionable lake or warehouse does not replace workload-based tier selection.
- **Ignoring labels and lineage**: Untraceable labels and examples block debugging, audit, and safe retraining.

## Worked Example
The keyword-spotting case combines curated, crowdsourced, and synthetic audio, then applies consistency validation and lineage. Its 23.4 million samples occupy about 748.8 GB of raw data. A tiered design retains inexpensive raw data in object storage while placing active training data on faster local NVMe. The example shows why storage throughput changes iteration speed and why source diversity, label quality, and traceability matter as much as model selection.

## Key Takeaways
1. Version and test data because changing a row can change learned behavior.
2. Prevent cascades at collection and labeling, where quality investment has high leverage.
3. Reuse transformation semantics and learned state across training and serving.
4. Select ingestion and storage from freshness, scale, access, and cost requirements.
5. Pair drift measurements with outcome evidence and an explicit response path.

## Connects To
- **Chapter 3**: Supplies the data stages and contracts of the lifecycle.
- **Chapter 5**: Provides the examples from which neural computation learns.
- **Chapter 8**: Determines whether training hardware is fed efficiently.
- **Chapter 14**: Extends data health into production monitoring and maintenance.
