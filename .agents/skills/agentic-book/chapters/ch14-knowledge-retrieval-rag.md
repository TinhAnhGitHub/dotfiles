# Chapter 14: Knowledge Retrieval (RAG)

## Core Idea
LLMs are "closed-book": their knowledge is frozen at training time, so they lack real-time facts, proprietary data, and niche expertise. Retrieval-Augmented Generation (RAG) makes them "open-book" by retrieving relevant evidence from an external knowledge base and appending it to the prompt before generation. The payoff is fresh, domain-specific, and verifiable answers with citations — and, when done well, fewer hallucinations. RAG is a pipeline whose reliability is bounded by retrieval quality, corpus freshness, and how carefully the model is constrained to the evidence.

## Frameworks Introduced
- **Standard RAG (ingest → index → retrieve → augment → generate)**: Documents are chunked, embedded, and stored in a vector store; at query time the most similar chunks are fetched, glued into the prompt, and fed to the LLM. Retrieval can be keyword (BM25), semantic (vector), or hybrid.
- **Agentic RAG**: A reasoning agent sits between query and answer as a gatekeeper. It validates sources, reconciles conflicts, decomposes multi-part questions into sub-queries, and can call external tools (e.g., live web search) to fill knowledge gaps — then synthesizes before generation.
- **GraphRAG**: Replaces (or augments) the vector store with a knowledge graph of entities (nodes) and relationships (edges). It answers complex, multi-hop questions by traversing connections and synthesizes across documents that no single chunk covers.
- **Managed RAG**: Platform services such as Google's `VertexAiRagMemoryService` that connect an agent to a hosted RAG corpus, parameterized by top-k results and a semantic-distance threshold.

## Key Concepts
1. **Embeddings**: Text encoded as high-dimensional vectors so that semantically similar items sit close together in vector space.
2. **Text / Semantic similarity and distance**: Meaning-based closeness (inverse of distance); the basis of "smart search" that matches intent even without shared keywords.
3. **Chunking**: Splitting documents into focused units (by section, paragraph, or sentence) with overlap, so retrieval returns tight, relevant context rather than whole manuals.
4. **Retrieval**: Candidate selection via vector search (e.g., HNSW indexing), keyword BM25, or hybrid fusion of both.
5. **Reranking / grounding**: Re-ordering or filtering candidates and constraining the LLM's answer strictly to the retrieved evidence.
6. **Vector databases**: Stores optimized for similarity search — Pinecone, Weaviate, Qdrant, Milvus, Chroma, plus pgvector/Redis/Elasticsearch — often backed by FAISS or ScaNN.
7. **Augmentation**: Appending retrieved chunks to the prompt to form a richer, grounded request.
8. **Attribution / citations**: Linking each claim to its source to build trust and verifiability.
9. **Corpus maintenance**: Periodic re-ingestion so the store tracks evolving sources like wikis.
10. **Latency / token cost**: Retrieval adds round-trips, model calls, and context tokens that must be budgeted.

## Mental Models
- **Open-book exam, not a magic eraser**: RAG improves recall of facts but does not by itself fix bad retrieval, stale data, or a model that ignores its evidence. Treat it as a measurable pipeline.
- **Two-stage quality gate**: Retrieval precision/recall and generation faithfulness are separate problems — evaluate each independently.
- **Evidence vs. inference vs. absence**: The model should distinguish what the sources say, what it reasons, and what nothing covers.
- **Meaning over keywords**: Vector search finds intent; BM25 finds literal matches; hybrid gets both.

## Anti-patterns / Failure Modes
- **Fragmented-answer failure**: The needed fact spans multiple chunks or documents; a single retrieval misses pieces and yields an incomplete answer (GraphRAG often helps here).
- **Noise and confusion**: Irrelevant chunks dilute the prompt and steer the LLM astray.
- **Conflict blindness**: Contradictory sources (e.g., a draft vs. a finalized report) are passed through unsynthesized.
- **Stale / unauthorized retrieval**: Trusting outdated blog posts over official policies, or documents the user lacks permission to see.
- **Corpus decay**: No re-ingestion schedule, so the store rots relative to live sources.
- **Cost / latency bloat**: Unbounded top-k, heavy reranking, and oversized chunks inflate tokens and response time.
- **Agentic pitfalls**: The reasoning agent can loop uselessly, mis-decompose the task, or discard good evidence — becoming a new error source.

## Implementation Sketch
Illustrative pseudocode (not copied source):

```
def rag(query):
    chunks = hybrid_retrieve(query, store, top_k=K)   # vector + BM25 fusion
    chunks = rerank(query, chunks)                    # keep only the strongest
    chunks = filter_freshness_and_authority(chunks)   # drop stale/unauthorized
    if not chunks:
        answer = call_external_tool(query) or "I don't know"   # gap handling
    else:
        context = join(chunks)
        answer = llm(prompt_with_evidence(query, context))
    return answer with_citations(chunks).stating_gaps_if_any()
```

LangGraph-style state carries `{question, documents, generation}` through a `retrieve` node and a `generate` node (retrieve → generate → end). Managed options like `VertexAiRagMemoryService` let an agent bind to a hosted corpus via `rag_corpus`, `similarity_top_k`, and `vector_distance_threshold`. Simplest entry point: attach a search tool (e.g., Google Search) to an agent so it grounds answers in live results.

## Worked Example
A customer asks, "What was Project Alpha's Q1 budget?" Standard RAG might return both a €50,000 proposal and a €65,000 finalized report. An **Agentic RAG** flags the conflict, prioritizes the authoritative financial report, answers €65,000, and cites it. For "How do our features and pricing compare to Competitor X?", the agent decomposes the question into four sub-queries (our features, our pricing, competitor features, competitor pricing), retrieves each, and synthesizes a comparison table. For a breaking question about yesterday's product launch, it detects the internal store is stale, calls a live web-search tool, and grounds its answer in fresh sources.

## Key Takeaways
1. RAG turns closed-book LLMs into open-book tools for fresh, proprietary, niche knowledge.
2. Retrieve first, then augment: retrieval quality is the ceiling on answer quality.
3. Prefer hybrid (vector + BM25) retrieval and add reranking to cut noise.
4. Ground answers strictly to evidence, cite sources, and state gaps rather than guessing.
5. Maintain the corpus on a schedule; freshness and permissions matter as much as recall.
6. Use GraphRAG for multi-hop, cross-document reasoning; Agentic RAG for validation, conflict resolution, and tool use — both at higher cost and latency.
7. Evaluate retrieval and generation separately, and budget latency, tokens, and cost.

## Connects To
- **ReAct / Agentic loops**: retrieval can be exposed as a tool and iterated from observations.
- **Memory (Ch 8)**: RAG and memory differ in retention and authority semantics — RAG is curated and citable, memory is conversational.
- **Prompt engineering**: augmentation and grounding are prompt-level constraints that shape faithfulness.
- **Evaluation chapters**: recall, precision, faithfulness, and citation accuracy are the metrics that make RAG trustworthy.
