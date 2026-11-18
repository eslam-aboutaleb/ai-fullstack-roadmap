<!-- chapter: retrieval -->

# What happens inside a typed retrieval request?

<!-- meta
domain: ai-rag
subdomain: retrieval
concept: What happens inside a typed retrieval request
difficulty: foundations
misconception_target: Dense retrieval always beats keyword search
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

RetrievalRequest carries the query, candidate and final counts, threshold, filters, isolation scope, expected generation, metadata projection, session, and mandatory capabilities. It makes execution constraints explicit instead of hiding them in loosely interpreted keyword arguments.

## Spoken Summary

Validate the typed request, trusted caller scope, query and ranking limits, then fetch/rank candidates with source/version metadata. Apply authorization before exposing candidates, optionally fuse and rerank, and return a bounded, diagnosable result contract rather than unrestricted documents.

## Why

A hybrid retriever coerces legacy calls into this form and validates supported constraints before delegating to a store or strategy. Effective filters and required metadata help preserve scope checks across the execution path.

## Production Case

An approximate search returns mostly other-tenant neighbors. The system must not expose them or assume that post-filtering automatically yields enough permitted candidates; evaluate filtered retrieval recall.

## Risk

A well-typed request can still contain an unauthorized scope if the host trusts the user's input. Authentication must establish which scope the caller is allowed to request.

## Trade-off

A richer request object improves composability and inspection but requires a stable public contract and deliberate defaults. A small positional API is easier for toy usage.

## Try This

Construct one request for tenant A with a larger candidate pool and a smaller final result set. Explain every field that affects authorization, ranking, or visibility.

## Execution Timeline

Query -> Dense embedder creates vector -> ANN index searches -> BM25 ranks keywords -> RRF fuses results -> Ranked passages returned

## Complexity

Exact scoring, inverted-index postings, ANN candidates, fusion and model reranking have different costs. Describe corpus size, token lengths, filters and candidate/final limits before making a runtime claim.

## Definitions

- **Dense retrieval**: Vector similarity search over embedded text passages
- **BM25**: Keyword ranking based on term frequency and inverse document frequency
- **Hybrid retrieval**: Combining dense and lexical search results

## Alternatives

- Dense-only retrieval
- Lexical-only retrieval

## Pitfalls

- Dense misses exact terms
- Keyword misses semantic matches
- RRF parameter tuning

## Follow-ups

### What belongs in the response besides scores?

Stable permitted source/revision identifiers, relevant spans and enough ranking metadata to explain behavior without disclosing unauthorized candidates.

## Example

> Explanation: Run both retrievers, then fuse results using Reciprocal Rank Fusion.
> Output: Combined ranked list of 10 passages

```python
dense_results = vector_index.search(query_vector, k=10)
keyword_results = bm25.search(query, k=10)
fused = reciprocal_rank_fusion([dense_results, keyword_results])
```

## Citations

- https://www.pinecone.io/learn/series/rag/

# Why separate candidate_k from final_k?

<!-- meta
domain: ai-rag
subdomain: retrieval
module: retrieval
concept: Why separate candidate_k from final_k
difficulty: implementation
misconception_target: RRF requires normalizing scores from different retrievers
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Candidate_k determines how many initial hits later stages can inspect; final_k determines how many results the caller receives. A reranker cannot promote a relevant passage that the candidate stage never retrieved. Fetching only five candidates and returning five wastes much of the value of reranking.

## Spoken Summary

candidate_k controls the pool considered before expensive reranking or evidence selection; final_k controls the returned results. A larger candidate pool can recover relevant items but increases latency, compute and memory. Tune both under the same quality and scope constraints.

## Why

The strategy API carries both counts through retrieval and applies final slicing after optional reranking and scope validation. Evidence budgeting is yet another limit and should not be confused with either count.

## Production Case

A reranker can choose five results from fifty candidates instead of five initial neighbors. Evaluate whether the extra pool recovers difficult queries and whether the latency budget still holds.

## Risk

Very large candidate pools increase backend work, reranker cost, and exposure of material to external services. Candidates sent to a reranker must already respect applicable permissions.

## Trade-off

More candidates can improve recall with diminishing returns. Tune using recall, final ranking quality, and latency rather than assuming larger is always better.

## Try This

Compare candidate pools of 10, 30, and 100 while holding final_k at five. Track whether missing answers were absent from the pool or simply ranked too low.

## Execution Timeline

Authorize scope -> retrieve candidate_k -> rerank permitted candidates -> select final_k -> validate evidence

## Complexity

Reranking cost generally grows with candidate count and pair lengths. A comparison sort may be O(n log n); model inference and retrieval can dominate the actual service cost.

## Definitions

- **Candidate pool**: The retrieved objects considered before reranking or final evidence selection.
- **final_k**: The number of selected results exposed by the final retrieval stage.
- **Candidate recall**: Whether relevant evidence entered the pool that downstream selection can inspect.

## Alternatives

- Weighted score combination
- Learned ranking models

## Pitfalls

- Choosing k too small (over-weights top ranks)
- Ignoring retriever quality differences

## Follow-ups

### Can reranking recover a document absent from its candidate set?

No. It can reorder what it receives; improve candidate recall upstream if the relevant evidence never enters the pool.

## Example

> Explanation: The scores are fixed synthetic reranker outputs; the example illustrates pool selection rather than a real ranking benchmark.
> Output: ['doc-B', 'doc-C']

```python
candidates = [('doc-A', 0.2), ('doc-B', 0.9), ('doc-C', 0.5)]
final_k = 2
selected = sorted(candidates, key=lambda item: (-item[1], item[0]))[:final_k]
print([identity for identity, score in selected])
```

## Citations

- https://arxiv.org/abs/2005.11401
- https://arxiv.org/abs/1603.09320

# How does Reciprocal Rank Fusion work here?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: retrieval
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Reciprocal Rank Fusion (RRF) combines ranks, not raw relevance scores.** For document d, sum 1/(c+r) across result lists containing d, where r starts at 1 and c is a declared positive rank constant. BM25 uses term frequency, inverse document frequency and document-length normalization; a dense ranker uses vector similarity. Their raw scores generally have different meanings and scales. Rank fusion avoids pretending that a cosine value of 0.8 equals a BM25 score of 0.8.

With c=60, a document ranked 1st and 3rd scores 1/61+1/63, about 0.032266. A document ranked 2nd in both scores 2/62, about 0.032258. A document appearing in only one list at rank 1 scores 1/61, about 0.016393. The first two are very close, so deterministic tie-breaking and recorded original ranks matter for debugging. A missing hit contributes zero; never assign a fictitious vector distance to a keyword-only hit.

Before fusion, establish trusted scope, active revision, deletion status and compatible profiles in every candidate path. Then deduplicate by the declared document/span identity, fuse a bounded candidate pool, optionally rerank, and select final context under a separate token budget. Candidate_k controls opportunity for later ranking; final_k controls exposure and generation cost. Post-filtering only the final fused top-k can leave no permitted evidence even when useful permitted candidates existed deeper in each list.

**Diagnose by stage.** Save eligible source IDs and lexical/dense ranks, fused scores, reranker decisions and final context membership with privacy-aware trace metadata. If a relevant exception is absent from both candidate lists, changing the RRF constant cannot recover it. If it is present but omitted from context, inspect reranking and packing. Compare lexical, dense and fused variants on identical fixed gold cases, including exact IDs, paraphrases, negation and unanswerable queries. A tiny fixture demonstrates the calculation and authorization invariant; it cannot establish the best constant or a universal hybrid quality improvement.

## Why

With c=60, ranks (1,3) barely outrank (2,2). A keyword-only result still has a valid rank contribution even though it has no vector distance; preserving that distinction prevents misleading diagnostics.

## Worked Case

With c=60, ranks (1,3) barely outrank (2,2). A keyword-only result still has a valid rank contribution even though it has no vector distance; preserving that distinction prevents misleading diagnostics.

## Risk

Duplicated chunks or unfiltered branches can distort fusion and leak source identities. RRF does not normalize authorization or repair missing evidence.

## Trade-off

Rank fusion tolerates incompatible score scales but discards score magnitude. Weighted or learned fusion can help with enough representative labels, at the cost of calibration and drift monitoring.

## Try This

Run retrieval_ranking.js and grounded_policy_pipeline.py. Calculate all three worked RRF values independently, remove the exception from both lists and explain why no rank constant can restore it.

## Follow-ups

### What if the lexical branch is unavailable?

Expose degraded single-branch retrieval explicitly and evaluate its refusal/quality behavior. Do not fabricate lexical ranks or call the result full hybrid search; decide whether the task can tolerate the reduced evidence path.

## Citations

- https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion
- https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity

# Are dense and lexical stages executed concurrently?

## Answer

Dense and lexical search can run concurrently when they are independent and the backend supports the combined load. They can also run sequentially or inside one SQL statement. Choose deliberately and measure the actual execution path.

## Why

Parallelize independent I/O with a bounded task group and preserve separate failure outcomes. A combined database query has its own query plan; Python-level concurrency cannot be inferred from its SQL shape.

## Risk

Assuming stage concurrency understates latency. Conversely, parallelizing blindly can violate a shared database session's rules or increase load beyond intended limits.

## Trade-off

Sequential execution is easier to reason about with one session. Parallel execution may reduce latency for independent backends but requires separate safe resources, cancellation, and error policy.

## Try This

Instrument start and finish events for both stages. Propose a parallel variant only after specifying which sessions and connections may be used concurrently.

# When does a reranker help, and what can it not fix?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: retrieval
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Reranking reorders an existing candidate pool; it does not search the missing corpus.** A cross-encoder reads a query and candidate jointly to estimate relevance, unlike a bi-encoder whose document vectors can be precomputed. An approximate nearest-neighbor (ANN) index trades some exact-search recall for reduced search work. HNSW is a graph-based ANN method: construction and search breadth influence memory, build cost and recall. Its parameters are engine-specific; they are not interchangeable with final answer count.

Separate corpus eligibility, ANN candidate retrieval, fusion, reranking and context selection. If candidate_k=40 and final_k=5, the reranker can inspect 40 permitted candidates before selecting five. If only five are fetched, it cannot promote the relevant exception at rank 12. Increasing candidate_k may improve recall but also increases reranker token work, remote data exposure and tail latency. A score threshold must be calibrated for the particular model/task rather than copied from a cosine example.

**Use an exact oracle.** For a fixed query set and embedding snapshot, compare ANN candidates to exact nearest neighbors under the same owner/revision filters, then separately compare both to human/task relevance labels. ANN recall measures approximation fidelity; relevance recall measures usefulness. Exact nearest neighbors can all be irrelevant. Filtering after a small ANN top-k may badly reduce eligible recall; test actual engine prefilter behavior and authorization at source resolution.

A credible experiment varies search breadth and candidate pool while holding corpus/model/profile/gold labels fixed. Record recall, MRR/nDCG, reranking latency and context cost, including selective filters and rare exceptions. Keep a safe lexical-only baseline and a fallback/refusal policy when reranking times out. The repository's local SDK contracts prove selected filtering/deletion invariants, not a production HNSW benchmark. The policy capstone deliberately removes the exception to show a reranker's hard boundary: a plausible general rule is still unsupported for a final-sale question.

## Why

The decisive exception is corpus rank 12 but only five candidates are fetched. Reranking those five cannot recover it; a larger candidate pool and an independent relevance oracle distinguish retrieval failure from ranking failure.

## Worked Case

The decisive exception is corpus rank 12 but only five candidates are fetched. Reranking those five cannot recover it; a larger candidate pool and an independent relevance oracle distinguish retrieval failure from ranking failure.

## Risk

A slow remote reranker can exceed the deadline after retrieval already succeeded. Sending unfiltered candidates to it creates a disclosure even if the final UI hides them.

## Trade-off

A larger pool improves opportunity with diminishing returns. Exact search is a useful small-data oracle; an ANN graph can scale retrieval but needs measured recall under real filter selectivity.

## Try This

Remove the final-sale candidate in policy_assistant_project.py and inspect the failed release result. Design an exact-vs-ANN comparison that reports approximation recall separately from task relevance.

## Follow-ups

### Can a perfect reranker guarantee a correct generated answer?

No. It only ranks the candidates it receives. The context packer can drop evidence and the generator can misinterpret it; assess final claim support, revision validity and correct abstention separately.

## Citations

- https://arxiv.org/abs/1603.09320
- https://arxiv.org/abs/1901.04085

# How should query rewriting and multi-query retrieval be bounded?

## Answer

Query rewriting can make a conversational or ambiguous question more searchable; multi-query retrieval explores alternative phrasings. Both add work and can drift away from the original intent. Bounds should cover variant count, text length, time, and downstream calls.

## Why

A bounded query transformer wraps a host-provided transformer with limits and a timeout. Query generation should be an explicit optional dependency with measured cost and failure behavior.

## Risk

Generated variants may invent identifiers or broaden the scope of meaning. Scope filters must remain fixed across variants, and deduplication does not by itself calibrate rankings across all variants.

## Trade-off

Expansion can improve recall for difficult language while multiplying embedding and search cost. Start with a baseline and add it only for demonstrated failures.

## Try This

Supply a transformer returning duplicates, blank strings, too many variants, and a slow response. Explain which limits protect cost and which protect meaning.

# How does multi-query merging differ from a fully calibrated global ranker?

## Answer

The generic hybrid strategy fuses each query variant's dense and lexical results, extends a candidate list, and deduplicates by ID in first-seen order before optional reranking. That is not a learned global calibration of all variant scores.

## Why

The implementation is a bounded composition mechanism. Its optional reranker is the natural place to compare the combined candidates against the original question, but absent that stage the ordering reflects implementation choices.

## Risk

The first query variant can dominate which duplicate representation and ordering survive. More variants therefore need not improve final ranking and can increase noise.

## Trade-off

First-seen deduplication is simple and deterministic. A second fusion across variants or a global reranker adds complexity and should be justified by evaluation.

## Try This

Reverse the order of two transformer variants and compare final results without a reranker. Explain any changed ordering using the execution policy.

# Why must filters be applied during each retrieval stage?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Authorization is an eligibility predicate, not a post-processing feature.** Each tenant, source revision, deletion tombstone, confidentiality policy and document scope must be enforced before ranking (and again when resolving citations). If an ANN query retrieves the global top five and then filters other tenants, five forbidden near neighbors can displace the only eligible records. This both hides relevant evidence and can expose identifiers through debug output. Filter by trusted owner inside the search engine or isolate indexes when the engine cannot enforce it.

**Vector math and correctness.** Cosine similarity equals dot(a,b) divided by the product of both norms; a zero vector has undefined cosine. A query vector must use the same embedding model/version and dimensions as indexed records. HNSW approximates nearest neighbors, trading search time, memory and recall according to index/query parameters. A benchmark must hold gold queries, eligible corpus, metric and hardware constant rather than comparing vendor score fields directly.

**Versioned migration case.** When replacing model v1 with v2, construct a separate versioned index, dual-write immutable record IDs and revisions, backfill, propagate deletions and verify the full expected ID set. Gate a read cutover on completeness and gold Recall@k plus tenant-denial tests; retain rollback with deletion reconciliation. Swapping an alias after only 90% of documents were indexed creates a silent relevance regression.

**Exercise.** The dependency-free `labs/vector_index_migration.py` demonstrates exact cosine search scoped before ranking, revision eligibility, tombstones and a fail-closed migration. It is an executable **reference oracle**, not a live integration with Qdrant, Chroma, Pinecone, Weaviate, FAISS, pgvector or LanceDB. Provider adapters must be checked against this behavior with official SDKs, pinned server versions and genuine negative integration tests.

**Follow-up.** If an ACL is revoked while a query is running, agree on an authorization-epoch snapshot policy and check source retrieval again; a cached result from an earlier ACL revision must not be used without revalidation. Exact search may be slower than filtered ANN, but correctness is the gate for tuning the latter.

## Why

Global top-k then authorization filtering can silently drop eligible evidence and leak unauthorized IDs.

## Risk

A backend that ignores a filter can still leak data. Defense in depth detects some invalid results, but tests must also ensure a reranker or external processor does not receive unauthorized candidates before that final check.

## Trade-off

Filter-aware search can affect query plans and approximate recall. Security requirements take precedence; tune backend indexes rather than dropping constraints for speed.

## Try This

Run the exact reference fixture with different owners, an unindexed revision and a deletion; specify the real provider integration test needed next.

## Follow-ups

### Why can top-k post-filtering harm recall even if it removes every unauthorized result?

Unscoped candidates can fill all top-k slots with forbidden neighbors and displace lower-ranked eligible evidence. Apply the trusted ACL in the engine's candidate selection or separate index namespaces, then verify an owner-scoped Recall@k oracle and a revoked-document negative case.

## Citations

- https://qdrant.tech/documentation/guides/optimize/

# How should I interpret distance thresholds and relevance scores?

## Answer

Distance is a geometric measurement, not a truth probability. RRF is a rank-fusion score, not a calibrated confidence. Reranker scores have provider-specific meaning. A distance threshold must match the selected metric and embedding profile.

## Why

Result types preserve distance, keyword score, and fusion or reranker scores separately rather than pretending they share a universal numerical scale. The retriever can apply a configured threshold and explicit final result limit.

## Risk

Displaying 0.92 as 92 percent correct misleads users. A low distance can retrieve an obsolete, unauthorized, or merely related passage; those require separate checks.

## Trade-off

Thresholding removes weak candidates but can reduce coverage and varies across corpus changes. Product confidence should be evaluated empirically using multiple signals and abstention policy.

## Try This

Collect score distributions for answerable and unanswerable questions. Evaluate a threshold's false acceptance and false rejection rates before choosing a UI label.

# How would you debug a relevant document missing from the final answer?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Debug the pipeline in the direction the information travels, not by rewriting the final prompt first.** Ingestion must read the intended source, preserve page/revision and access metadata, normalize text/OCR accurately and emit stable chunk IDs. Retrieval then enforces the trusted principal and current revision, retrieves a broad enough lexical/dense candidate set, fuses/reranks it, selects a bounded evidence packet, and only then can generation cite or abstain. A missing relevant document at any earlier stage cannot be recovered by a cleverer answer prompt.

**Concrete failure trace.** A customer asks whether an item can be returned within 30 days. The final answer incorrectly refuses, even though a policy PDF contains the rule. Inspect: (1) was the PDF present and indexed; (2) did OCR and chunk boundaries preserve the conditional language; (3) was tenant/page/revision authorization too restrictive or too broad; (4) did BM25 find exact "returns" and dense search find paraphrases; (5) did fusion/RRF retain the actual rule among candidate_k; (6) did reranking move a general rule ahead of the relevant exception; (7) did context compaction remove negation; (8) did the model refuse despite adequate evidence? Attribute the error to its stage before changing anything.

**Mechanics and metrics.** For a gold source set G, Recall@k is the fraction of G included among the first k retrieved eligible IDs. MRR uses 1/rank of the first relevant result, averaged over queries; nDCG weights graded relevance by rank. Compute retrieval metrics before involving a stochastic generator. Then separately evaluate claim-to-citation support, appropriate abstention and false refusal. A high Recall@k can coexist with an unsupported answer, and a perfectly grounded refusal can be wrong for an answerable case.

**Runnable local capstone.** `labs/grounded_policy_pipeline.py` uses synthetic documents to perform owner-scoped BM25 lexical ranking, toy cosine dense ranking, reciprocal rank fusion and a deliberately **extractive**, citation-grounded answer/refusal. It tests a 30-day rule, a cross-tenant 90-day rule, deleted/stale data and malicious retrieved text. This exercises architecture decisions without requiring a hosted LLM; it does not prove a production embedding model, ANN engine or generative answer reliability. Tests assert supported claim text and exact authorized source IDs.

**Trade-offs and next checks.** Increase candidate_k to improve recall but account for reranking cost and token budgets. Do not weaken ACLs to fix an empty result. Repair index path and quality fixtures, then rerun a held-out evaluation rather than modifying gold expectations or lowering targets. More retrieval variants mean more failure modes and potentially worse evidence selection if score semantics are not calibrated.

**Changed assumption.** If the relevant policy was deleted yesterday and a legacy cache still returns it, treat freshness and authorization as invariants: invalidate the cache, honor tombstone revision and abstain when no valid current source remains. A correct but stale citation is not current policy evidence.

## Why

The retrieval service exposes distinct modules and result shapes for these stages. That separation supports inspection of intermediate artifacts rather than guessing that every wrong answer is an embedding problem.

## Risk

Debug logging can expose queries or private passages. Prefer controlled fixtures and sanitized IDs, and do not bypass scope checks simply to make a document appear during investigation.

## Trade-off

Stage-by-stage diagnosis takes longer than tweaking a single constant but targets the actual cause and prevents compensating errors.

## Try This

Run the grounded policy pipeline, delete the primary rule or swap tenant scope, and observe which stage makes the answer abstain.

## Follow-ups

### If a RAG answer cites an obsolete but lexically perfect policy, what should the retrieval stage do?

Check validity/revision and deletion before candidate ranking and revalidate at source resolution. Refuse when no current authorized evidence remains; improving BM25 or reranker score cannot make an invalid source valid, and the stale cache must be invalidated.

## Citations

- https://aclanthology.org/2020.emnlp-main.550/

# Why can a citation to a real policy document still be wrong after a source revision or deletion?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: retrieval
difficulty: design
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-23
-->

## Answer

**Citations establish provenance, not timeless correctness.** A retrieved passage can accurately quote a real document yet be obsolete for the user's requested time, superseded by a later policy revision or no longer authorized for this principal. Grounding therefore needs *which* source, *which* revision, a relevant effective/validity interval, trusted owner eligibility and evidence that the answer's claim actually follows from the cited span. A URL or a high semantic score alone proves none of these.

**A reproducible retrieval path.** Index each passage with a stable document ID, content digest, version/revision, source span, validity/effective time and trusted access labels. At question time, resolve the requested temporal context, filter eligible owner/document revisions *before* dense/BM25 ranking and select evidence. Before rendering a citation, recheck its access policy and active revision, especially when search and document reads cross different stores or caches. Treat tombstones and revocations as independent authoritative events and propagate them through vector indexes and output caches; don't allow a background backfill to resurrect deleted records.

**Worked version conflict.** A policy v1, effective until September 30, permits refunds for 60 days; v2, effective October 1, permits 30 days. A question about October 15 should cite v2, while a legitimate historical question about August might need v1 under a documented archive policy. If v1 and v2 share near-identical text embeddings, naive top-k can prefer v1 even though its relevance score is high. Use an effective-date predicate and version-aware citation resolution; if the valid policy cannot be verified, abstain rather than assert the wrong rule.

**Failure and trade-offs.** Over-aggressive recency filters can incorrectly hide historical data, and unscoped approximate search can leak foreign tenant candidates. State snapshot/version semantics, keep immutable source evidence for audits where legally permitted, and benchmark true relevance and citation support separately. A synthetic exact-cosine fixture can verify the filtering invariant but cannot certify ANN filtering semantics, real policy ingestion or a production service's cache invalidation.

## Why

Correct wording from an outdated or unauthorized source is still not correct evidence for the question's principal and requested time.

## Worked Case

Refund policy v1 allows 60 days through September 30, but v2 changes the limit to 30 days from October 1. A current October request must cite v2; an archive query may reference v1 only with valid time and access evidence. A v1 vector hit must not overrule the effective revision.

## Risk

Stale cached passages, deleted records and backfilled older embeddings can reintroduce invalid citations despite a high retrieval score.

## Trade-off

Revision and validity filters complicate indexing and historical queries, but make answers auditable and prevent policy-version errors.

## Try This

Index two revisions with different effective dates, add a tombstone and ask current and historical questions; verify citation revision and owner eligibility.

## Follow-ups

### Does a high Recall@5 certify that the generated answer uses the correct policy revision?

No. Recall@5 may count an outdated source as relevant if the gold set ignores validity. Evaluate eligible revision-specific evidence, citation-to-claim support, freshness and false refusal separately; high retrieval recall does not guarantee that the generator cited or interpreted the right passage.

## Citations

- https://www.postgresql.org/docs/current/mvcc-intro.html
- https://www.postgresql.org/docs/18/ddl-rowsecurity.html
- https://www.sqlite.org/lang_expr.html#the_between_operator

# How does Late Chunking resolve the context-loss problem of traditional sentence-level chunking in dense vector retrieval?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Late Chunking eliminates the semantic fragmentation inherent in traditional pre-embedding chunking strategies.** In standard RAG pipelines, long documents are cut into 200–500 token segments *before* being passed to an embedding model. Consequently, pronouns, conditional clauses, and contextual references (e.g., 'it', 'this exception applies', 'as mentioned above') lose their semantic antecedents from earlier paragraphs. The resulting chunk embedding represents a fragmented snippet stripped of its global document context.\n\n**Full-document attention with span-specific pooling.** Late Chunking inverts this order using long-context transformer embedding models (such as jina-embeddings-v3 or modern 8k/32k token embedding backends).

The entire document (or large multi-thousand-token section) is passed through the transformer encoder as a single continuous sequence. Every token generates a contextualized representation that attends across all other tokens in the entire document. After the full-document forward pass is complete, mean-pooling is applied over the exact token offset spans corresponding to each chunk boundary.\n\n**Retaining granular retrieval with global context.** The resulting chunk embeddings have the identical vector dimensions and granular granularity as standard chunk embeddings, allowing exact chunk-level citation and efficient vector database indexing. However, because each token's embedding was computed under full-document self-attention, the chunk vector inherently encodes global document semantics, dramatically improving retrieval recall on queries requiring antecedent context.

## Why

A contract states: 'Section 5 applies only to European subsidiaries'. Three paragraphs later, Chunk 4 says: 'Under this section, liability is capped at $1M'. Traditional chunking embeds Chunk 4 without knowing it applies only to Europe. Late Chunking embeds Chunk 4 with full awareness of the European restriction.

## Worked Case

A contract states: 'Section 5 applies only to European subsidiaries'. Three paragraphs later, Chunk 4 says: 'Under this section, liability is capped at $1M'. Traditional chunking embeds Chunk 4 without knowing it applies only to Europe. Late Chunking embeds Chunk 4 with full awareness of the European restriction.

## Risk

Late Chunking requires the embedding model to support long context windows (e.g., 8k+ tokens) and increases GPU VRAM consumption during the document ingestion forward pass.

## Trade-off

Late Chunking requires slightly more ingestion compute and memory per document, but produces vastly superior retrieval vectors without needing multi-vector parent-child index complexity.

## Try This

Embed a multi-paragraph text with a coreferent pronoun using early chunking vs Late Chunking. Measure the cosine similarity between the chunk vector and the global antecedent entity.

## Follow-ups

### Can Late Chunking be used with dense bi-encoders that have a 512-token limit?

No. Late Chunking requires long-context transformer architectures capable of attending across multiple chunk boundaries in a single forward pass.

## Citations

- https://arxiv.org/abs/2409.04701
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How does ColBERT late interaction bridge the trade-off between bi-encoder latency and cross-encoder accuracy?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**ColBERT resolves the core dilemma of Information Retrieval: the speed of bi-encoders versus the precision of cross-encoders.** Dense bi-encoders compress an entire passage into a single pooled vector (e.g., 768 or 1,536 floats). This single-vector bottleneck inevitably blurs fine-grained token-level details, rare entities, and exact numbers. Conversely, cross-encoders concatenate query and passage into a single transformer, evaluating full token-to-token attention; while highly accurate, cross-encoders require running full neural inference on every candidate passage at query time, creating unacceptable multi-second latency at scale.\n\n**Contextualized Late Interaction over BERT (ColBERT).** ColBERT eliminates the single-vector bottleneck by encoding both query and document into matrices of token-level embeddings (e.g., 128-dimensional vectors per token).

Instead of computing a single dot product, ColBERT computes the MaxSim operator: for every token vector in the query, it finds the maximum cosine similarity among all token vectors in the document, and then sums these maximum scores: S(Q, D) = sum_{q in Q} max_{d in D} (q . d).\n\n**Offline indexing with sub-50ms query latency.** Document token embeddings are precomputed offline and indexed using vector quantization (Residual Compression) in vector search engines like Vespa or PLAID. At query time, finding the MaxSim score across millions of passages requires only fast vector lookups and additions, achieving cross-encoder ranking accuracy with sub-50ms retrieval latency.

## Why

A search query asks: 'What is the maximum torque of the 2024 turbo hybrid model?'. A dense bi-encoder conflates this with the standard non-hybrid model due to semantic overlap. ColBERT's MaxSim aligns the exact query tokens 'torque' and 'hybrid' with matching document tokens, correctly retrieving the specific specification.

## Worked Case

A search query asks: 'What is the maximum torque of the 2024 turbo hybrid model?'. A dense bi-encoder conflates this with the standard non-hybrid model due to semantic overlap. ColBERT's MaxSim aligns the exact query tokens 'torque' and 'hybrid' with matching document tokens, correctly retrieving the specific specification.

## Risk

ColBERT stores multiple vectors per document chunk rather than a single vector, increasing index disk and RAM storage requirements by 3x–6x compared to standard dense vector databases.

## Trade-off

ColBERT requires specialized index infrastructure (such as PLAID or Vespa) and higher storage capacity, but delivers cross-encoder retrieval quality at sub-50ms query speeds.

## Try This

Implement a Python prototype of the MaxSim operator using NumPy matrices representing query tokens and document tokens. Observe how exact token alignment drives the final score.

## Follow-ups

### How does PLAID accelerate ColBERT search?

PLAID prunes candidate documents using centroid clustering and residual quantization, avoiding computing MaxSim across documents that lack high centroid overlap.

## Citations

- https://arxiv.org/abs/2004.12832
- https://arxiv.org/abs/2112.01488

# How does Corrective RAG dynamically evaluate retrieval confidence and trigger web-search fallback?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Corrective RAG (CRAG) prevents generative hallucination by introducing an autonomous self-correction loop around retrieved evidence.** In naive RAG pipelines, top-K retrieved document chunks are unconditionally injected into the LLM prompt regardless of whether they actually contain the answer. When retrieval fails or returns irrelevant distractors, the generator either hallucinates speculative answers or fails silently.\n\n**The three-tier retrieval confidence gate.** Corrective RAG inserts a lightweight retrieval evaluator (a fine-tuned classifier or fast SLM) between retrieval and generation. The evaluator scores the confidence of retrieved documents into three operational bands: (1) Correct (Confidence > 0.8): The retrieved passages contain authoritative evidence.

The pipeline invokes a knowledge refinement algorithm that decomposes chunks into individual sentences, filters out irrelevant noise, and sends only verified sentences to the generator; (2) Ambiguous (0.4 <= Confidence <= 0.8): The local retrieval is partially relevant but incomplete. The pipeline combines the refined local passages with an external web search query (Google/Bing API) or secondary enterprise database lookup to patch missing details; and (3) Incorrect (Confidence < 0.4): The retrieved passages are irrelevant or misleading. The pipeline completely discards the local chunks, reformulates the user query, and executes an external web search or returns a safe, honest abstention.\n\n**Production impact.** By refusing to feed low-confidence chunks to the generator, CRAG dramatically reduces hallucination rates while ensuring high answer coverage across novel or out-of-domain queries.

## Why

A user asks about a breaking product announcement released today. Internal vector search returns old documentation from last year. CRAG scores the retrieval confidence as Incorrect (<0.4), discards the stale internal chunks, and falls back to a live web search to answer accurately.

## Worked Case

A user asks about a breaking product announcement released today. Internal vector search returns old documentation from last year. CRAG scores the retrieval confidence as Incorrect (<0.4), discards the stale internal chunks, and falls back to a live web search to answer accurately.

## Risk

An overly strict retrieval evaluator can misclassify nuanced but correct local evidence as ambiguous, triggering unnecessary external web searches that add latency and cost.

## Trade-off

CRAG introduces an extra evaluation classification step (10–30ms) and dynamic branching logic, trading pipeline simplicity for vastly improved answer faithfulness and resilience.

## Try This

Build a CRAG confidence routing function. Pass a query with irrelevant chunks and verify that the router routes to the web search fallback branch instead of passing bad chunks to the LLM.

## Follow-ups

### How does knowledge refinement differ from text summarization in CRAG?

Knowledge refinement strips irrelevant sentences and retains only verbatim factual clauses, whereas summarization rewrites text and risks introducing new inaccuracies.

## Citations

- https://arxiv.org/abs/2401.15884
- https://scikit-learn.org/stable/modules/model_evaluation.html

# What is Graph RAG, and when does community-detected hierarchical summarization outperform vector similarity search?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Graph RAG bridges the architectural divide between local entity queries and global dataset-wide summarization.** Dense vector search operates on local semantic proximity: it excels at answering focused questions that map to specific document passages (e.g., 'What is the return policy for footwear?'). However, vector search fundamentally fails on holistic, corpus-wide synthesis queries (e.g., 'What are the top three strategic risks mentioned across all 500 company earnings transcripts?').

Because vector embeddings cannot aggregate across hundreds of dispersed chunks, top-K search merely retrieves a few arbitrary examples.\n\n**Knowledge graph extraction and hierarchical community detection.** Graph RAG solves global sensemaking through a multi-stage graph pipeline: (1) Entity and relationship extraction: an LLM extracts entities (nodes), relationships (edges), and narrative claims from all text chunks across the corpus; (2) Community detection: graph clustering algorithms (specifically the Leiden algorithm) partition the knowledge graph into hierarchical communities of closely interconnected entities at multiple granularities; and (3) Precomputed community summaries: an LLM generates structured summaries of every community at each hierarchical tier, synthesizing themes, key actors, and overarching narratives.\n\n**Global query routing.** When a global query arrives, Graph RAG maps the query across the precomputed community summaries at the appropriate hierarchy level, combining partial summaries into a comprehensive final synthesis. For global analytical queries, Graph RAG provides significantly higher comprehensiveness and factual coverage than standard vector retrieval.

## Why

An analyst asks: 'Summarize the common cyber vulnerabilities reported across 2,000 incident reports'. Vector search retrieves 5 specific incidents. Graph RAG traverses community summaries of vulnerability clusters, producing a comprehensive taxonomy across all 2,000 reports.

## Worked Case

An analyst asks: 'Summarize the common cyber vulnerabilities reported across 2,000 incident reports'. Vector search retrieves 5 specific incidents. Graph RAG traverses community summaries of vulnerability clusters, producing a comprehensive taxonomy across all 2,000 reports.

## Risk

Extracting entities, relationships, and community summaries across an entire enterprise corpus consumes large LLM token budgets and substantial indexing compute time.

## Trade-off

Graph RAG indexing is computationally expensive and slow compared to simple vector embedding, but unlocks corpus-wide analytical queries that vector databases cannot answer.

## Try This

Extract an entity-relationship graph from three short articles. Cluster the entities into two communities and generate a community summary for each.

## Follow-ups

### Can Graph RAG and Vector RAG be combined in a single hybrid pipeline?

Yes. Production systems use an intent router: point queries are routed to fast vector search, while thematic aggregation queries are routed to Graph RAG community summaries.

## Citations

- https://arxiv.org/abs/2404.16130
- https://scikit-learn.org/stable/modules/model_evaluation.html

# How does Matryoshka Representation Learning enable multi-stage vector search with 80% RAM savings?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Matryoshka Representation Learning (MRL) enables nested vector representations that can be truncated to smaller dimensions with minimal loss in retrieval accuracy.** High-dimensional embeddings (e.g., 1,536 dimensions for OpenAI text-embedding-3-large, or 3,072 dimensions) provide exceptional semantic representation but impose massive RAM and latency costs when indexing millions of vectors in graph-based vector indexes (such as HNSW in pgvector or Qdrant).\n\n**Nested dimensionality loss optimization.** Traditional embedding models distribute information uniformly across all vector dimensions; slicing a 1,536-dimensional vector to 256 dimensions degrades performance catastrophically. In contrast, MRL (named after Russian nesting dolls) is trained with a composite loss function that simultaneously optimizes retrieval loss across multiple explicit prefix sub-dimensions: Loss = sum_{d in {64, 128, 256, 512, 1536}} w_d * Loss(v_{1:d}).

This forces the neural network to compress the most critical semantic variance into the earliest dimensions.\n\n**Two-stage search architecture with 80% RAM reduction.** Production architectures exploit MRL through a hierarchical two-stage search strategy: (1) Stage 1 (Fast candidate retrieval in RAM): only the initial 256 dimensions of each vector are held in high-speed RAM within an HNSW index, slashing memory footprint by over 80%. When a query arrives, it queries the 256-dimensional index to retrieve the top 100 candidates in milliseconds; (2) Stage 2 (Exact full-dimension reranking): the full 1,536-dimensional vectors for only those 100 candidates are fetched from disk or SSD to compute exact cosine similarities, reranking down to the final top 10. The system achieves 98%+ of full-dimensional retrieval recall while reducing memory infrastructure costs by 80%.

## Why

A vector database indexes 10 million documents. Storing 1,536-dim float32 vectors in RAM requires over 60GB of memory. Truncating to 256 dimensions using MRL reduces the in-memory index footprint to under 12GB while retaining 98% of original search recall.

## Worked Case

A vector database indexes 10 million documents. Storing 1,536-dim float32 vectors in RAM requires over 60GB of memory. Truncating to 256 dimensions using MRL reduces the in-memory index footprint to under 12GB while retaining 98% of original search recall.

## Risk

Truncating an embedding model that was NOT trained with Matryoshka loss destroys representation geometry and ruins retrieval performance.

## Trade-off

Two-stage MRL retrieval requires managing a secondary disk fetch for full-dimensional reranking, trading a tiny I/O latency increment for massive RAM cost savings.

## Try This

Take an MRL-enabled embedding vector. Truncate it to the first 256 dimensions, normalize to unit length, and compare its cosine similarity ranking against the full 1,536-dimensional baseline.

## Follow-ups

### Does Matryoshka truncation require re-normalizing the vector?

Yes. After slicing a vector to its prefix sub-dimension, it must be L2-normalized so that cosine similarity can be calculated via fast dot products.

## Citations

- https://arxiv.org/abs/2205.13147
- https://scikit-learn.org/stable/modules/model_evaluation.html

# What is HyDE, and why must its hypothetical document never be treated as evidence?

<!-- meta
domain: ai-rag
subdomain: query-transformation
module: retrieval
concept: HyDE retrieval
difficulty: mechanism
misconception_target: The generated hypothetical document can be shown to the answer model as supporting context
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**HyDE changes the retrieval representation, not the evidence.** A user query such as 'why does boot stop' is short and uses everyday words, while the relevant documentation is long, formal and full of domain terms. A single-vector bi-encoder (an embedding model that encodes query and passage separately) often places the short question far from the matching passage. HyDE asks an LLM to write a hypothetical passage that would answer the question, embeds that passage, and runs nearest-neighbour search against the real document vectors. The hypothetical text carries vocabulary such as 'ECC', 'uncorrectable error' and 'startup sequence' that the query lacked.

**Pipeline.** (1) Receive the question. (2) Generate a short hypothetical passage under a token limit. (3) Embed it with the document-side embedding mode. (4) Retrieve real chunks, ideally merging with the result list from the original query so a bad hypothesis cannot erase a good direct match. (5) Rerank, authorize and assemble context from retrieved chunks only. (6) Generate the final answer with citations to those chunks.

**The trust boundary.** The hypothetical document may be fluent and wrong. If it were passed to the answer generator as context, the system would effectively let the model cite its own guess. Keep it out of the evidence set, out of citations, and out of caches keyed as source text. Log it for debugging, but treat it as an untrusted intermediate artifact.

**When it helps and when it hurts.** HyDE tends to help short, conceptual or vocabulary-mismatched queries over explanatory corpora. It tends to hurt exact-identifier lookups, queries where the model has no domain knowledge and invents terminology, and latency-sensitive paths, because it adds a full LLM call before retrieval. Measure it per query class with Recall@K rather than enabling it globally.

## Spoken Summary

HyDE, Hypothetical Document Embeddings, asks a language model to write a plausible answer passage, embeds that passage instead of the short question, and searches the real corpus with it. The idea is that an answer-shaped text lies closer to real answer passages than a terse question does. The generated text is only a search probe. It can contain wrong claims, so the final answer must cite retrieved real documents. I would run it as an optional strategy, merge it with ordinary query retrieval, and fall back to plain retrieval if generation fails or times out.

## Why

The example scores a vague question directly and through a hypothetical passage against three toy documents. The probe raises the top-1 score and widens the margin over distractors, while the fallback path proves the pipeline still works if generation fails. The toy bag-of-words cosine stands in for a real embedding model, so the numbers illustrate the mechanism, not a benchmark.

## Production Case

A support assistant over hardware manuals receives short symptom queries such as 'boot stops'. Direct dense retrieval ranks generic overviews first. HyDE plus direct-query merge recovers the startup-error chapter for this class, while exact error-code queries are routed to lexical search and skip HyDE because the extra call only adds latency.

## Risk

A wrong hypothesis can pull retrieval toward the wrong topic, and a prompt-injected question can steer the generated probe. Because the probe is sent to a model, it also becomes an additional place where sensitive question text can leak.

## Trade-off

Extra LLM latency and cost per query in exchange for better recall on a subset of queries. Merging with the direct query keeps a safety net at the cost of a second search.

## Try This

Replace fake_hypothesis with a deliberately wrong passage about the CAN driver. Observe whether merging with the direct query still returns the right document, then add a query-class rule that skips HyDE when the query contains an identifier.

## Execution Timeline

Question -> generate hypothetical passage (bounded) -> embed passage -> search real chunks -> merge with direct-query results -> rerank and authorize -> answer from real chunks only

## Complexity

One extra LLM generation (time roughly linear in generated tokens) plus one extra embedding call and, when merging, a second nearest-neighbour search. Index size is unchanged.

## Definitions

- **HyDE**: Hypothetical Document Embeddings: embed an LLM-written answer-shaped passage and use it as the retrieval query.
- **Bi-encoder**: A model that embeds query and document separately so document vectors can be precomputed.
- **Retrieval probe**: Text used only to locate evidence; it is never quoted or cited as evidence.
- **Recall@K**: The fraction of relevant items that appear in the top K retrieved results.

## Alternatives

- Query expansion with domain synonyms when vocabulary mismatch is narrow and known
- Multi-query retrieval when the question has several plausible interpretations
- Fine-tuning the embedding model on query-passage pairs when labelled data exists

## Pitfalls

- Citing or caching the hypothetical text as if it were a source
- Applying HyDE to identifier lookups where exact tokens matter
- No timeout or fallback when the generator is slow
- Judging it on a handful of anecdotes instead of Recall@K per query class

## Follow-ups

### How would you decide objectively whether HyDE is worth enabling?

Build a labelled query set split by class (short conceptual, identifier, multi-aspect, conversational). Compare direct retrieval, HyDE-only and HyDE-plus-direct on Recall@K and nDCG@K (normalized discounted cumulative gain), then add p95 latency and cost per query. Enable it only for classes where the quality gain justifies the added latency, and keep an offline regression test so a model upgrade cannot silently invert the result.

### Is merging the HyDE results with the original-query results always better than HyDE alone?

Not always, but it is the safer default. HyDE alone fails badly when the hypothesis drifts. Merging, for example with Reciprocal Rank Fusion (RRF), preserves candidates the direct query found. The cost is a second search and a larger candidate pool for the reranker, so measure it instead of assuming.

### How does HyDE differ from query expansion and multi-query retrieval?

Expansion adds terms to one query, multi-query issues several rewritten questions, and HyDE replaces the query representation with a generated answer-shaped document. HyDE exploits the question-to-answer asymmetry, whereas the other two mainly increase lexical or interpretive coverage.

## Example

> Explanation: HyDE: embed a hypothetical answer, search real documents, keep the original query as a fallback.
> Output: verified

```python
"""HyDE: embed a hypothetical answer, search real documents, keep the original query as a fallback."""
import math
import re
from collections import Counter

DOCS = {
    "ecc-startup": "startup sequence initializes ecc memory before caches are enabled and an uncorrectable ecc error during memory initialization halts boot",
    "can-driver": "the can driver transmits frames through mailbox hardware using the bit timing register",
    "wdg-timeout": "watchdog timeout is configured in startup code before the application main function runs",
}


def vector(text):
    return Counter(re.findall(r"[a-z]+", text.lower()))


def cosine(a, b):
    dot = sum(a[t] * b[t] for t in a)
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def search(text):
    scored = [(round(cosine(vector(text), vector(body)), 3), name) for name, body in DOCS.items()]
    return sorted(scored, reverse=True)


def fake_hypothesis(question):
    # Stand-in for an LLM call. Its text is a retrieval probe, never evidence.
    return "ecc memory initialization can fail in the startup sequence when an uncorrectable error is found before caches are enabled"


def hyde_search(question, generate=fake_hypothesis):
    try:
        probe = generate(question)
    except Exception:
        return search(question), "fallback-query"
    merged = {}
    for rank_list in (search(question), search(probe)):
        for score, name in rank_list:
            merged[name] = max(score, merged.get(name, 0.0))
    return sorted(((s, n) for n, s in merged.items()), reverse=True), "hyde+query"


question = "why does boot stop"
direct = search(question)
hyde, mode = hyde_search(question)
assert hyde[0][1] == "ecc-startup"
assert hyde_search(question, generate=lambda q: 1 / 0)[1] == "fallback-query"
print("direct_top", direct[0], "hyde_top", hyde[0], mode)
```

## Citations

- https://arxiv.org/abs/2212.10496

# How do you decompose a complex question into subqueries, and when must they run sequentially instead of in parallel?

<!-- meta
domain: ai-rag
subdomain: query-transformation
module: retrieval
concept: query decomposition and dependency planning
difficulty: design
misconception_target: Every subquery from a decomposed question can run in parallel
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Decomposition solves the one-vector problem.** A single embedding of 'How did the 2026 update change eligibility, reimbursement limits and cancellation rules?' blends three needs, so top results may cover only the dominant one. Splitting it into three focused subqueries retrieves focused evidence for each.

**Parallel versus sequential.** Independent subqueries share no data, so they can run concurrently, which reduces critical-path latency to roughly the slowest branch. Dependent subqueries need a prior result: 'Which regulations apply to the company Organization A acquired in 2025?' requires identifying the company before its industry and jurisdiction can be searched. Running those in parallel would search with a guess.

**Model it as a directed acyclic graph (DAG).** Each node is a retrieval step; edges are data dependencies. A scheduler computes dependency levels: nodes in the same level run with `asyncio.gather`, and later levels receive earlier results as typed state. This captures hybrid shapes, such as industry and jurisdiction running in parallel after the company is known, then a final rules lookup joining both.

**Failure handling is the senior part.** (1) Validate coverage: the union of subqueries must still answer every clause of the original question. (2) Verify intermediate facts, because an error in hop one propagates to every later hop. (3) If a dependency cannot be resolved with confidence, stop and return a defined 'insufficient' outcome instead of continuing with a guessed entity. (4) Enforce max depth, max fan-out, a shared deadline and authorization on every step. (5) Keep the original question available for the final answer so the generator does not answer only the fragments.

## Spoken Summary

Decomposition splits a multi-part question into smaller retrievable information needs. If the subqueries are independent, such as eligibility, exclusions and limits, run them concurrently and merge the evidence. If one answer is needed to form the next query, such as first identifying an acquired company and then its regulations, they are dependent and must run in order. I represent the plan as a dependency graph, execute it level by level, bound the number of steps, and stop with an explicit failure if an intermediate entity cannot be resolved with confidence.

## Why

The example builds a four-node plan, derives dependency levels, runs each level concurrently with asyncio, and passes accumulated state to later steps. The printed levels show which steps can overlap and which cannot.

## Production Case

A compliance assistant gets 'Which standard applies to the payment provider Company A acquired?'. Hop one resolves the provider from acquisition filings, then industry and jurisdiction are retrieved in parallel, then the standard. When hop one returns two candidate providers, the plan stops and asks a clarifying question instead of guessing.

## Risk

Decomposition can omit a requirement, invent an assumption inside a subquery, or produce redundant subqueries that waste budget. Errors in early hops silently corrupt later hops.

## Trade-off

Parallel plans reduce latency but raise concurrent load on the retriever and provider quotas. Sequential plans support dependent reasoning but add latency and error propagation. Over-decomposing a simple question costs more than it gains.

## Try This

Add a cycle to PLAN and confirm levels raises. Then make the first retrieval return None and add a rule that halts the plan with an 'insufficient' result rather than querying with None.

## Execution Timeline

Plan subqueries with dependencies -> validate coverage of original clauses -> compute dependency levels -> run each level concurrently -> verify intermediate facts -> merge evidence -> answer from original question plus evidence

## Complexity

Critical-path latency equals the sum of the slowest node per dependency level; total work equals the sum of all nodes. Concurrency is bounded by a semaphore, so wall time is at least total work divided by the concurrency limit.

## Definitions

- **Query decomposition**: Splitting one complex question into smaller independently retrievable subquestions.
- **DAG**: Directed acyclic graph: nodes with one-way dependencies and no cycles, used here to order retrieval steps.
- **Multi-hop**: A question whose answer requires chaining facts where later searches depend on earlier results.
- **Fan-out**: The number of subqueries launched from one request.

## Alternatives

- Multi-query retrieval when sub-aspects are interchangeable phrasings rather than distinct needs
- Iterative retrieval with a planner that chooses each next query from accumulated evidence
- Knowledge-graph traversal when the dependencies are explicit entity relations

## Pitfalls

- Treating dependent steps as independent and searching with guessed entities
- No cycle, depth or fan-out limits
- Dropping the original question so the answer covers only fragments
- Skipping per-step authorization

## Follow-ups

### How would you verify that a decomposition covers the whole question?

Extract the information requirements from the original question (for example eligibility, exclusions, limits), then check that every requirement maps to at least one subquery. A cheap deterministic check compares extracted entities, dates and constraints; a model-based check can judge coverage, but it should be evaluated against labelled examples because the judge can also be wrong.

### What changes if the subqueries target different knowledge bases?

Add routing per node and enforce the caller's permissions at each source. A node for HR policies and a node for a finance database have different retrievers and different access rules. Routing never replaces authorization.

### Why not let the LLM decide everything in an agent loop?

An open loop is flexible but harder to bound, test and audit. A declared plan with limits gives predictable cost and traces. Many systems use a hybrid: a planner proposes a graph, deterministic code validates and executes it.

## Example

> Explanation: Run independent subqueries concurrently and dependent subqueries by dependency level.
> Output: verified

```python
"""Run independent subqueries concurrently and dependent subqueries by dependency level."""
import asyncio

CALLS = []


async def retrieve(name, **context):
    CALLS.append(name)
    await asyncio.sleep(0.05)
    facts = {
        "acquired_company": "PayCo",
        "industry": "payments",
        "jurisdiction": "EU",
        "rules": f"rules for {context.get('industry')} in {context.get('jurisdiction')}",
    }
    return facts[name]


PLAN = {
    "acquired_company": [],
    "industry": ["acquired_company"],
    "jurisdiction": ["acquired_company"],
    "rules": ["industry", "jurisdiction"],
}


def levels(plan):
    done, result = set(), []
    while len(done) < len(plan):
        ready = sorted(n for n, deps in plan.items() if n not in done and set(deps) <= done)
        if not ready:
            raise ValueError("cycle or missing dependency")
        result.append(ready)
        done.update(ready)
    return result


async def run(plan):
    state = {}
    for level in levels(plan):
        values = await asyncio.gather(*(retrieve(name, **state) for name in level))
        state.update(dict(zip(level, values)))
    return state


state = asyncio.run(run(PLAN))
assert state["rules"] == "rules for payments in EU"
print(levels(PLAN), state["rules"])
```

## Citations

- https://arxiv.org/abs/2205.10625
- https://arxiv.org/abs/2210.03350

# How do you turn a follow-up chat message into a standalone search query without semantic drift?

<!-- meta
domain: ai-rag
subdomain: query-transformation
module: retrieval
concept: conversational query condensation
difficulty: debugging
misconception_target: A rewritten query is safe as long as it reads fluently
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Why condensation exists.** In a chat, the last message often depends on earlier turns: 'What about its exclusions?' is meaningless to a retriever that sees only that sentence. Embedding the whole transcript is also poor, because irrelevant earlier turns dilute the vector. Condensation produces a short standalone query such as 'What are the exclusions in Policy P-102?'.

**Three sub-problems.** Reference resolution (what do 'it' or 'those' refer to), context selection (which earlier turns matter), and intent preservation (do not add requirements the user never stated).

**Drift is a correctness bug.** Rewriting with an LLM is a fallible transformation. Typical failures are replacing P-102 with a similar identifier, removing 'not' so the query asks the opposite question, broadening a date range, or adding a product assumption. Each failure silently retrieves plausible but wrong evidence.

**Guard design.** Keep the original user message immutable for audit, fallback and evaluation. Extract protected features from the original message plus the resolved referent: exact identifiers, dates, numbers and negation words. After rewriting, validate that every required protected feature is present and no unexpected identifier was introduced. On failure, retry once, fall back to the original query plus the last explicit entity, or ask a clarifying question.

**Separate semantics from constraints.** Put tenant, permission and hard filters in a structured request built from trusted server-side state, never inside the rewritten text. Then even a bad rewrite cannot widen access, and exact constraints are enforced by filters rather than hoped for through embeddings.

## Spoken Summary

Conversational condensation rewrites a follow-up like 'which items are not covered?' into a standalone query that names the policy it refers to. The retriever needs a precise information request, not the whole transcript. The risk is drift: a rewrite can change an identifier, drop a negation or shift a date. So I keep the original as immutable input, extract protected tokens such as identifiers, dates and negations, and reject any rewrite that adds, removes or changes them. Authorization scope never comes from the rewrite.

## Why

The example validates three rewrites for the same follow-up: a faithful one passes, one with a changed identifier is flagged as both missing and invented, and one that removes 'not' is flagged as a dropped negation. It is deliberately rule-based so the guard is deterministic and testable.

## Production Case

A policy chatbot sees 'Which items are not covered?' after a discussion of Policy P-102. A rewrite that reads 'Which items are covered by Policy P-102?' retrieves a coverage list and the assistant answers with the opposite meaning. The negation guard rejects it and the system falls back to the original query plus the last explicit policy identifier.

## Risk

Regex guards miss semantic drift that preserves tokens, such as swapping the topic while keeping the identifier. Treat the guard as one layer and still evaluate end-to-end retrieval on conversational test sets.

## Trade-off

Rewriting adds an LLM call and latency but makes follow-ups retrievable. Stricter validation rejects more rewrites and triggers more fallbacks or clarifying questions.

## Try This

Add date protection (for example 2025 versus 2026) to the guard, then write a rewrite that passes the guard but changes the topic to see what rule-based checks cannot catch.

## Execution Timeline

Receive follow-up -> select relevant turns -> LLM rewrite -> extract protected tokens -> validate rewrite -> accept, retry once, or fall back/clarify -> build retrieval request with trusted filters

## Complexity

One short LLM call per turn plus constant-time regular-expression validation. Cost grows with the number of history turns included, so cap them.

## Definitions

- **Query condensation**: Rewriting a context-dependent follow-up into a standalone retrieval query.
- **Semantic drift**: A transformation that changes the meaning or constraints of the original request.
- **Protected token**: An identifier, date, number or negation that a rewrite must preserve exactly.
- **Immutable input**: The original user message, retained unchanged for audit and fallback.

## Alternatives

- Maintain explicit conversation state (current entity, filters) updated by deterministic code
- Rolling conversation summaries used as additional retrieval context
- Ask a clarifying question when references are ambiguous

## Pitfalls

- Embedding the full transcript
- Letting the rewrite carry tenant or permission constraints
- Overwriting the original query
- Validating fluency instead of constraint preservation

## Follow-ups

### Where should the tenant filter live when you rewrite queries?

In a structured retrieval request built from the authenticated principal. The rewrite output is untrusted text. If the tenant constraint were embedded in the string, a model error or injection could change it.

### How do you evaluate a condensation component?

Create conversations with gold standalone queries and gold relevant documents. Measure exact preservation of protected tokens, retrieval Recall@K with condensed versus original queries, and the fallback rate. Track negation and identifier errors as separate counters because they are high-severity.

### What if the rewrite is ambiguous even to a human?

Ask the user. A clarifying question costs a turn, while a confident wrong rewrite can produce an authoritative wrong answer.

## Example

> Explanation: Accept a standalone rewrite only when protected identifiers and negations survive.
> Output: verified

```python
"""Accept a standalone rewrite only when protected identifiers and negations survive."""
import re

IDENTIFIER = re.compile(r"\b[A-Z]{1,5}-\d+\b")
NEGATIONS = {"not", "no", "never", "without", "except"}


def protected(text):
    words = set(re.findall(r"[a-z]+", text.lower()))
    return set(IDENTIFIER.findall(text)), words & NEGATIONS


def validate_rewrite(history_text, original, rewrite):
    ids_needed = protected(history_text + " " + original)[0]
    negations_needed = protected(original)[1]
    ids_seen, negations_seen = protected(rewrite)
    problems = []
    if ids_needed - ids_seen:
        problems.append("missing " + ",".join(sorted(ids_needed - ids_seen)))
    if ids_seen - ids_needed:
        problems.append("invented " + ",".join(sorted(ids_seen - ids_needed)))
    if negations_needed - negations_seen:
        problems.append("dropped negation")
    return problems


history = "Explain the coverage limits of Policy P-102."
follow_up = "Which items are not covered?"
good = "Which items are not covered by Policy P-102?"
bad_id = "Which items are not covered by Policy P-120?"
bad_negation = "Which items are covered by Policy P-102?"

assert validate_rewrite(history, follow_up, good) == []
assert validate_rewrite(history, follow_up, bad_id) == ["missing P-102", "invented P-120"]
assert validate_rewrite(history, follow_up, bad_negation) == ["dropped negation"]
print(validate_rewrite(history, follow_up, good), validate_rewrite(history, follow_up, bad_id), validate_rewrite(history, follow_up, bad_negation))
```

## Citations

- https://python.langchain.com/docs/how_to/qa_chat_history_how_to/
- https://arxiv.org/abs/2005.11401

# What is Maximal Marginal Relevance (MMR), and how does lambda control redundancy?

<!-- meta
domain: ai-rag
subdomain: ranking
module: retrieval
concept: Maximal Marginal Relevance
difficulty: implementation
misconception_target: Diversity-aware selection always improves answer quality
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**The problem.** Top-K by similarity often returns five passages that all state the same 30-day notice rule. Evidence budget is wasted and other required aspects are missing.

**The rule.** MMR selects iteratively:

`MMR(d) = lambda * sim(q, d) - (1 - lambda) * max over s in S of sim(d, s)`

where q is the query, d a candidate, S the already selected set, and lambda in [0, 1]. At lambda = 1 it reduces to ordinary relevance ranking. As lambda decreases, similarity to already selected passages is penalized more heavily. The first pick is always the most relevant because S is empty.

**Reading the example.** Two near-identical notice-period passages are the most relevant. With lambda 1.0 both are selected. With lambda 0.3 the second slot goes to a less similar passage about exceptions, giving a more complete evidence set.

**Choosing lambda.** It depends on how the similarity scale is distributed, so there is no universal value. Evaluate candidate values on a labelled set of multi-aspect questions using aspect coverage, faithfulness and completeness, not only similarity. Because MMR scores mix a query similarity with a pairwise similarity, make sure both use the same metric and normalization.

**Where it sits in the pipeline.** Run MMR after authorization and candidate retrieval, usually over the reranked pool. Deduplicating exact or near-exact copies first is cheaper than relying on MMR for it. MMR is greedy, so it is not guaranteed to find the best possible set, and it has no notion of a token budget; for a hard budget combine it with a coverage or knapsack-style selector.

## Spoken Summary

MMR is a greedy selection rule. At each step it picks the candidate with the highest value of lambda times similarity to the query minus one minus lambda times the largest similarity to anything already selected. Lambda of one is pure relevance; lower values penalize passages that repeat what is already chosen. It is useful when the top results are near-duplicates and the question needs several aspects covered, like notice period, exceptions and refunds. It only helps if the added passages stay relevant, so tune lambda against answer completeness, not intuition.

## Why

The example uses 2-D vectors so the effect is visible without a model. Selection with lambda 1.0 is identical to ranking by relevance, while lambda 0.3 swaps the duplicate for a distinct aspect.

## Production Case

Asked for all reasons a claim can be rejected, a retriever returns five 'missing documents' passages. MMR over the reranked pool selects missing documents, expired coverage, fraud review and filing deadline instead, and the answer lists all four with citations.

## Risk

Too much diversity brings in irrelevant passages and hurts precision. Diversity measured by embeddings can also treat a genuinely conflicting passage as 'different' and select it without handling the conflict.

## Trade-off

Better coverage versus lower individual relevance, plus O(K x N) pairwise similarity work. For small reranked pools the cost is negligible.

## Try This

Add a fifth candidate that is irrelevant but far from everything and find the lambda at which MMR starts selecting it. That value shows where diversity turns into noise.

## Execution Timeline

Authorized candidate pool -> pick top by relevance -> for each next pick compute relevance minus redundancy -> select best -> repeat until K -> pass set to context builder

## Complexity

O(K x N) pairwise similarity evaluations for selecting K of N candidates, each costing the embedding dimension. Negligible for reranked pools of tens, noticeable for thousands.

## Definitions

- **MMR**: Maximal Marginal Relevance: greedy selection balancing query relevance and novelty against already selected items.
- **Lambda**: The weight on relevance; one minus lambda weights redundancy avoidance.
- **Redundancy**: Similarity of a candidate to passages already selected.
- **Greedy algorithm**: Chooses the locally best item at each step and does not revisit earlier choices.

## Alternatives

- Near-duplicate removal with MinHash or embedding thresholds as a cheap first pass
- Coverage-aware selection when requirements are explicit
- Cluster the pool and take the best passage per cluster

## Pitfalls

- Choosing lambda without a labelled multi-aspect test set
- Applying MMR before filtering unauthorized documents
- Using different similarity functions for the two terms
- Expecting MMR to enforce a token budget

## Follow-ups

### How is MMR different from a reranker?

A reranker scores each candidate's relevance to the query, usually independently. MMR is set-aware: a candidate's score depends on what has already been chosen. They are complementary; rerank first, then select a diverse subset.

### What do you do when diverse passages conflict?

Diversity is not conflict resolution. Apply applicability metadata (version, jurisdiction, effective date) first, then detect remaining contradictions and surface them or abstain rather than letting similarity-based diversity pick a side.

### Can you give MMR a token budget?

Not directly. Use it to rank by marginal value, then stop when the token budget is exhausted, or switch to a utility-per-token greedy selector that also accounts for required aspects.

## Example

> Explanation: Maximal Marginal Relevance: trade relevance against redundancy with the already selected set.
> Output: verified

```python
"""Maximal Marginal Relevance: trade relevance against redundancy with the already selected set."""
import math

QUERY = (1.0, 0.0)
CANDIDATES = {
    "notice-a": (0.99, 0.10),
    "notice-b": (0.98, 0.12),
    "refund": (0.80, 0.60),
    "exceptions": (0.75, 0.66),
}


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))


def mmr(candidates, query, k, lam):
    selected = []
    pool = dict(candidates)
    while pool and len(selected) < k:
        def score(name):
            redundancy = max((cosine(pool[name], candidates[s]) for s in selected), default=0.0)
            return lam * cosine(pool[name], query) - (1 - lam) * redundancy
        best = max(sorted(pool), key=score)
        selected.append(best)
        pool.pop(best)
    return selected


relevance_only = mmr(CANDIDATES, QUERY, 2, lam=1.0)
diverse = mmr(CANDIDATES, QUERY, 2, lam=0.3)
assert relevance_only == ["notice-a", "notice-b"]
assert diverse == ["notice-a", "exceptions"]
print("lambda=1.0", relevance_only, "lambda=0.3", diverse)
```

## Citations

- https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf

# How do Self-RAG, Corrective RAG, and an LLM retrieval router differ, and how do you bound a correction loop?

<!-- meta
domain: ai-rag
subdomain: adaptive-retrieval
module: retrieval
concept: corrective retrieval
difficulty: tradeoffs
misconception_target: Any LLM that decides whether to retrieve is implementing Self-RAG
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Three different things.** Self-RAG (Asai et al.) trains a language model to produce special reflection tokens that decide when retrieval is needed and to critique retrieved passages and its own output. It is a training and decoding method, so wrapping a prompt around a base model does not make it Self-RAG. Corrective RAG (CRAG) adds a lightweight retrieval evaluator that classifies retrieved evidence and triggers corrective actions, for example refining the knowledge, or searching another source, when confidence is low. An LLM retrieval router just chooses a strategy per query; it is useful, but it is a different pattern.

**What 'corrective' must mean.** Running a second search whenever the first returns something is not correction. Correction must be driven by an assessment of evidence quality against what the question requires. In the example, the required fact is a specific diagnostic identifier. The dense-style first pass returns a generic overview, the assessor sees the identifier is not covered, and one lexical correction finds the definition.

**Bounding the loop.** Define: (1) max corrections, so there is a hard stop; (2) a latency and cost deadline shared across attempts; (3) a diversity rule so the correction uses a different strategy or source and does not repeat the same query; (4) a terminal outcome: answer, ask for clarification, or abstain. Setting max_corrections to zero in the example makes the same question abstain, which shows the stop condition is part of correctness.

**Pitfalls.** An evaluator that is too lenient hides retrieval failures; one that is too strict triggers expensive loops. Calibrate it on labelled query-evidence pairs and watch the correction rate and the abstention rate as operational metrics. Every correction path must keep authorization identical to the first path, because a fallback source is a common place to leak.

## Spoken Summary

Self-RAG is a specific research method where a model is trained to emit reflection tokens that decide whether to retrieve and critique relevance and support. Corrective RAG adds an evaluator over retrieved results and triggers a correction, such as a different search or query rewrite, when evidence looks weak. An application that simply asks an LLM whether to retrieve is a router, not Self-RAG. In production I implement a bounded corrective loop: assess evidence against required facts, apply at most a fixed number of corrections, and abstain if still insufficient.

## Why

The example models assessment as coverage of required terms, applies one lexical correction when dense-like retrieval is insufficient, and shows that a zero-correction budget turns the same query into an abstention.

## Production Case

A diagnostics assistant gets a question containing an AUTOSAR-style error identifier. Dense retrieval returns bus overviews. The assessor notices the identifier is absent from evidence, one exact lexical search finds the definition, and the trace records both stages. When the identifier does not exist anywhere, the loop stops after its single correction and the user gets a no-evidence response instead of an invented explanation.

## Risk

Unbounded correction loops waste money and can chase irrelevant evidence. A fallback to the open web or another collection can bypass tenant or data-governance rules if not authorized identically.

## Trade-off

Higher answer reliability and better handling of weak retrieval versus added latency, more failure paths and an evaluator that needs its own quality measurement.

## Try This

Add a third strategy, such as a query rewrite, and cap the combined latency budget. Verify the loop still terminates and records which strategy produced the final evidence.

## Execution Timeline

Initial retrieval -> assess coverage of required facts -> if insufficient and budget remains, apply a different strategy -> reassess -> answer when sufficient, otherwise abstain or clarify -> log strategy path

## Complexity

Latency grows linearly with the number of correction rounds, bounded by max_corrections times the per-round cost. Evaluator cost adds one pass per round.

## Definitions

- **Self-RAG**: A trained approach where a model emits reflection tokens to control retrieval and critique evidence and output.
- **CRAG**: Corrective Retrieval-Augmented Generation: evaluate retrieval quality and trigger corrective actions.
- **Evidence assessment**: A check of whether retrieved content covers what the question requires.
- **Abstention**: A defined outcome in which the system declines to answer or asks for more information.

## Alternatives

- Hybrid retrieval by default so correction is rarely needed
- Static routing by query type without a feedback loop
- A trained reflection model such as Self-RAG when you control model training

## Pitfalls

- Calling any retry a correction
- No maximum number of correction attempts
- Letting the fallback source skip authorization
- Not measuring the evaluator itself

## Follow-ups

### How would you test a corrective loop?

Use cases with known outcomes: evidence sufficient on first pass, sufficient after correction, and never sufficient. Assert the strategy path, the number of rounds, that authorization filters are identical across rounds, and that the never-sufficient case abstains within the budget.

### What metrics tell you the loop is healthy?

Correction rate by query class, success rate after correction, abstention rate, added p95 latency, and cost per answered question. A rising correction rate often points to index staleness or an embedding regression.

### Can the evidence evaluator be an LLM?

Yes, but treat it as a model with error rates. Combine it with deterministic checks for structured requirements such as identifiers, policy numbers and dates, and calibrate against labels.

## Example

> Explanation: Corrective retrieval: assess evidence, apply one bounded correction, then answer or abstain.
> Output: verified

```python
"""Corrective retrieval: assess evidence, apply one bounded correction, then answer or abstain."""
CORPUS = {
    "d1": "general canbus overview of frames and arbitration",
    "d2": "diagnostic error wdgif_e_param_device is raised when the device id is invalid",
}
REQUIRED = {"wdgif_e_param_device"}


def dense_like(query):
    words = set(query.lower().split())
    return [d for d, text in CORPUS.items() if words & set(text.split()) and "overview" in text]


def lexical(query):
    return [d for d, text in CORPUS.items() if REQUIRED & set(text.split())]


def assess(hits):
    covered = {term for d in hits for term in REQUIRED if term in CORPUS[d]}
    return "sufficient" if covered == REQUIRED else "insufficient"


def answer_path(query, max_corrections=1):
    trace = []
    hits = dense_like(query)
    trace.append(("dense", hits, assess(hits)))
    corrections = 0
    while assess(hits) != "sufficient" and corrections < max_corrections:
        hits = lexical(query)
        corrections += 1
        trace.append(("lexical", hits, assess(hits)))
    return ("answer" if assess(hits) == "sufficient" else "abstain"), trace


decision, trace = answer_path("explain can frames error code")
assert decision == "answer" and [step[0] for step in trace] == ["dense", "lexical"]
assert answer_path("explain can frames error code", max_corrections=0)[0] == "abstain"
print(decision, trace)
```

## Citations

- https://arxiv.org/abs/2310.11511
- https://arxiv.org/abs/2401.15884

# How does ColBERT-style late interaction (MaxSim) differ from single-vector dense retrieval and cross-encoders?

<!-- meta
domain: ai-rag
subdomain: ranking
module: retrieval
concept: late interaction and MaxSim
difficulty: mechanism
misconception_target: Late interaction is just another name for cross-encoder reranking
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Three scoring architectures.** A bi-encoder produces one vector per query and per passage and scores with a dot product or cosine. It is fast and indexable but squeezes all content of a passage into one point. A cross-encoder feeds query and passage jointly through a Transformer, so every query token can attend to every passage token. That gives strong relevance judgments but requires a forward pass per query-document pair, so it is used on small candidate sets. Late interaction encodes query and document separately, keeps all contextual token vectors, and applies a light interaction after encoding.

**MaxSim.** `S(q, d) = sum over query tokens i of max over document tokens j of (q_i . d_j)`. Each query token finds its best-matching document token, and those best matches are summed. A passage that covers both of two query requirements scores high even if its overall mean vector is unremarkable.

**Reading the example.** The two toy query tokens represent two requirements. After mean pooling, a passage that covers both and a passage whose tokens sit between them look identical (both about 1.0). MaxSim separates them: about 2.0 versus about 1.41. The numbers are a constructed illustration of the mechanism, not a benchmark.

**Engineering implications.** Because document token vectors are stored, index size grows roughly with the number of tokens rather than the number of passages, so storage and memory are much larger than for single vectors. ColBERT systems use compression and candidate generation tricks to keep search practical. Late interaction can serve as a first-stage retriever or as a reranker, and it complements, rather than replaces, a cross-encoder for the final small set.

**Decision rule.** Start with a good dense plus lexical hybrid and a cross-encoder reranker. Consider late interaction when error analysis shows fine-grained, multi-aspect matching failures that single vectors cannot resolve and you can afford the index and serving complexity.

## Spoken Summary

A bi-encoder compresses a passage into one vector. A cross-encoder reads query and passage together, which is accurate but cannot be precomputed. Late interaction, as in ColBERT, keeps one vector per token for both sides and scores with MaxSim: for each query token take its best match among document tokens, then sum. Document token vectors are precomputed and indexable, so it sits between the two. The cost is a much larger index and more complex serving, so I would compare it on the whole quality, latency and storage frontier.

## Why

The example constructs two query requirements and two documents so that mean-pooled single-vector scores tie while MaxSim differentiates them. That isolates the property under discussion: token-level matching survives where pooling blurs it.

## Production Case

A legal search team sees queries with two distinct clauses where single-vector search returns passages matching only one clause. A late-interaction first stage improves coverage on that slice, but the multi-vector index is several times larger, so they restrict it to the highest-value collection and keep hybrid search elsewhere.

## Risk

Index size and memory can be many times larger than single-vector retrieval. Mixing late-interaction scores with other score scales without calibration or rank-based fusion produces unstable rankings.

## Trade-off

Finer-grained matching and precomputed document representations versus larger indexes and more complicated infrastructure. Cross-encoders are simpler to deploy as rerankers but cost compute per pair at query time.

## Try This

Change the BLURRY tokens to (1, 0.2) and (0.2, 1) and observe how the MaxSim and pooled scores converge, which shows when late interaction stops adding value.

## Execution Timeline

Offline: encode document tokens and store them -> Online: encode query tokens -> for each query token find max similarity over candidate document tokens -> sum -> rank or pass to reranker

## Complexity

Scoring one document costs about |q| x |d| dot products of the embedding dimension; storage scales with total document tokens times dimension rather than with passage count.

## Definitions

- **Late interaction**: Encode query and document separately into token vectors and combine them with a light operation afterward.
- **MaxSim**: Sum over query tokens of each token's maximum similarity to any document token.
- **Cross-encoder**: A model that scores a query-document pair jointly with full attention across both texts.
- **Mean pooling**: Averaging token vectors into one vector.

## Alternatives

- Hybrid dense plus lexical retrieval with a cross-encoder reranker
- Larger or domain-fine-tuned single-vector embedding model
- Multiple vectors per passage at chunk level instead of token level

## Pitfalls

- Ignoring storage and memory growth
- Adding raw MaxSim scores to BM25 scores
- Benchmarking quality without latency and indexing cost
- Assuming it removes the need for any reranker

## Follow-ups

### Why can a cross-encoder not be precomputed like late interaction?

A cross-encoder's representation of a passage depends on the query because the two are attended together. There is nothing reusable per document, so each pair needs a forward pass. Late interaction keeps document encodings independent of the query.

### How do you compare the three on a real workload?

Hold the candidate pool and labels fixed and measure Recall@K and nDCG@K, then p95 latency, index size, ingestion time and serving cost. Report the quality-latency frontier, not an isolated relevance number.

### When is late interaction a bad fit?

Small teams without serving capacity for large indexes, exact-identifier workloads better served by lexical search, and corpora where single-vector hybrid already meets quality targets.

## Example

> Explanation: MaxSim keeps token-level matches that one mean-pooled vector blurs together.
> Output: verified

```python
"""MaxSim keeps token-level matches that one mean-pooled vector blurs together."""
import math


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def unit(v):
    n = math.hypot(*v)
    return tuple(x / n for x in v)


def maxsim(query_tokens, doc_tokens):
    return sum(max(dot(q, d) for d in doc_tokens) for q in query_tokens)


def pooled(tokens):
    return unit(tuple(sum(t[i] for t in tokens) for i in range(2)))


QUERY = [unit((1, 0)), unit((0, 1))]            # two distinct requirements
BOTH = [unit((1, 0.05)), unit((0.05, 1))]        # one document covers both
BLURRY = [unit((1, 1)), unit((1, 1))]            # tokens sit between them

single = {"both": dot(pooled(QUERY), pooled(BOTH)), "blurry": dot(pooled(QUERY), pooled(BLURRY))}
late = {"both": maxsim(QUERY, BOTH), "blurry": maxsim(QUERY, BLURRY)}
assert late["both"] > late["blurry"]
print({k: round(v, 3) for k, v in single.items()}, {k: round(v, 3) for k, v in late.items()})
```

## Citations

- https://arxiv.org/abs/2004.12832

# What is contextual retrieval, and why index enriched chunk text but generate from the original passage?

<!-- meta
domain: ai-rag
subdomain: indexing
module: retrieval
concept: contextual chunk enrichment
difficulty: design
misconception_target: Context added for indexing can safely be shown to the model as source text
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**The ambiguity problem.** After chunking, pronouns, section references and local terms lose their surroundings. 'The threshold is reduced to 10 seconds in fast mode' does not say which module, product or timeout is meant, so a query about the watchdog fast-mode timeout may not match it well in either dense or lexical search.

**The technique.** Before indexing, construct an enriched retrieval text: document title, section path, and optionally a one- or two-sentence description of how the chunk fits into the document. Embed and lexically index that enriched text. In the example, lexical overlap with the query rises from 3 to 5 tokens after enrichment.

**Two representations, two roles.** (1) `index_text` is optimized for finding the chunk. (2) `original` is the exact source passage used for generation, quoting and citation. Keeping them separate prevents generated descriptions from being cited as if the source said them. Store a provenance flag such as `heading-derived` versus `llm-generated` so reviews and evaluations can compare both.

**Sources of context.** Deterministic context from headings and metadata is cheap, reproducible and auditable. LLM-generated chunk descriptions can capture implicit context but cost one model call per chunk, can hallucinate, and must be regenerated when the chunker, document or prompt changes. Include the context-generation prompt and model in the ingestion fingerprint.

**Related approaches.** Parent-child retrieval returns larger parents at answer time. Late chunking embeds with full-document attention before pooling. Contextual retrieval modifies the indexed text instead. They can be combined, but each should be justified by measured gains in Recall@K and answer faithfulness.

## Spoken Summary

A chunk like 'The threshold is reduced to 10 seconds in fast mode' is ambiguous alone. Contextual retrieval prepends source and section context, such as document title and heading or a short generated description, to the text used for embedding and lexical indexing so the chunk can be found. I store the original passage separately and give only that to the generator and citations, because generated context can be wrong and must not become authoritative evidence. The trade-off is higher ingestion cost and a larger index.

## Why

The example computes query-token overlap against the bare chunk and against the enriched index text, and asserts that the original passage remains unchanged for generation. It illustrates the lexical side; embedding retrieval benefits from the same added context.

## Production Case

A specification repository has hundreds of chunks that say 'in fast mode' or 'this register'. After prefixing document, chapter and section, queries naming the module find the right chunk in the first page of results, and answers cite the unchanged original text with its section path.

## Risk

A wrong generated description biases retrieval toward the wrong queries and can leak into citations if the two representations are mixed. Enrichment increases token counts for embedding and storage.

## Trade-off

Better recall for context-dependent chunks versus extra ingestion compute, larger indexes and re-enrichment when inputs change. Heading-derived context is cheaper but less expressive than generated context.

## Try This

Compare heading-only enrichment with a generated one-sentence description on ten ambiguous chunks, and record which queries each fixes or breaks.

## Execution Timeline

Chunk document -> derive heading and metadata context (optionally generate description) -> build index_text -> embed and lexical-index it -> store original passage separately -> retrieve by index_text -> generate from original

## Complexity

Ingestion adds either negligible deterministic work or one LLM call per chunk; index size grows by the added context tokens per chunk. Query-time cost is unchanged.

## Definitions

- **Contextual retrieval**: Adding document and section context to chunk text before building retrieval indexes.
- **Index text**: The enriched text embedded or lexically indexed for finding a chunk.
- **Original passage**: The unmodified source text used for generation and citation.
- **Provenance flag**: Metadata recording how a piece of context was produced.

## Alternatives

- Parent-child retrieval returning larger sections
- Late chunking with a long-context embedding model
- Structure-aware chunking that keeps headings inside chunks

## Pitfalls

- Citing the enriched text
- Forgetting to include context-generation settings in the ingestion fingerprint
- Generating context for every chunk without measuring benefit
- Letting enrichment inflate chunks past the embedding input limit

## Follow-ups

### How is this different from parent-child chunking?

Parent-child changes what is returned at answer time (a larger parent). Contextual retrieval changes what is indexed so the chunk is easier to find. One affects context assembly; the other affects candidate retrieval.

### What belongs in the ingestion fingerprint?

Parser version, chunker configuration, context-generation prompt and model, embedding model and version, and normalization settings. A change in any of them can invalidate cached or stored representations.

### How do you check that enrichment helped?

Evaluate on labelled queries before and after, measuring Recall@K and answer faithfulness, then look at per-query wins and losses. Enrichment can hurt exact-phrase queries by diluting the chunk.

## Example

> Explanation: Index enriched text for retrieval, but keep the original passage as generation evidence.
> Output: verified

```python
"""Index enriched text for retrieval, but keep the original passage as generation evidence."""
import re

CHUNK = "The threshold is reduced to 10 seconds in fast mode."
CONTEXT = "AUTOSAR Watchdog Driver Specification, section Watchdog Modes: describes watchdog timeout behavior."


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def overlap(query, text):
    return len(tokens(query) & tokens(text))


QUERY = "watchdog fast mode timeout threshold"
record = {
    "original": CHUNK,                      # shown to the generator and cited
    "index_text": CONTEXT + " " + CHUNK,    # embedded or lexically indexed
    "context_origin": "heading-derived",    # generated context is never source evidence
}
before = overlap(QUERY, record["original"])
after = overlap(QUERY, record["index_text"])
assert after > before and record["original"] == CHUNK
print("overlap_before", before, "overlap_after", after, record["context_origin"])
```

## Citations

- https://www.anthropic.com/news/contextual-retrieval
- https://arxiv.org/abs/2409.04701

# Why can't you add cosine, BM25, and reranker scores directly, and when is learned fusion justified?

<!-- meta
domain: ai-rag
subdomain: ranking
module: retrieval
concept: score fusion and learning to rank
difficulty: tradeoffs
misconception_target: Normalizing scores makes different retrievers directly comparable
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Scores are not comparable.** A cosine of 0.8, a BM25 score of 12 and a cross-encoder score of 3.2 measure different things on different scales. Adding them gives the feature with the largest numeric range an accidental veto. In the example the raw sum ranks candidates in exactly BM25 order because BM25 values (up to 60) swamp cosine values (below 1).

**Option 1: score normalization.** Min-max or z-score each list before a weighted sum. This is sensitive to the candidate set: a single outlier BM25 score of 60 compresses all other normalized values toward zero, changing the order versus a list without the outlier. Normalization does not calibrate scores to probabilities either.

**Option 2: rank-based fusion.** Reciprocal Rank Fusion scores `sum over lists of 1 / (k + rank)`, with k often 60. It needs no score alignment, is robust to scale and outliers, and is a strong baseline. It discards how large the gap between ranks was and cannot express that one retriever is more trustworthy for a query type unless you weight lists.

**Option 3: learning to rank (LTR).** Train a model over a feature vector such as dense similarity, BM25, exact-entity match, freshness, authority and category. Pointwise methods predict a relevance label per document, pairwise methods learn which of two documents should rank higher, and listwise methods optimize the order of a list. This can capture interactions among features, but needs labelled judgments or reliable feedback, careful train-test splits and ongoing maintenance.

**How to choose.** Start with RRF. Evaluate alternatives per query with Recall@K, MRR (mean reciprocal rank) and nDCG@K on held-out labelled queries. Move to LTR only if the lift justifies the data and operations burden. Calibrate or re-fit after any change to the embedding model, index or query distribution.

## Spoken Summary

Those scores live on different scales and distributions. Cosine might range zero to one, BM25 can reach tens, and a cross-encoder logit is unbounded, so a raw sum is dominated by whichever has the largest scale. Min-max normalization depends on the candidate set and one outlier compresses everyone else. Rank-based fusion such as Reciprocal Rank Fusion avoids scale but ignores score gaps. If I have enough labelled data and several meaningful signals, a learning-to-rank model can learn the weights. I choose among them by query-level ranking metrics.

## Why

The example holds four candidates and compares raw addition, min-max normalized addition and RRF. The assertion proves the raw sum equals BM25 order; the printed orders show that the three methods can disagree.

## Production Case

A search team adds BM25 to dense retrieval and sums raw scores. Error-code queries improve, but conceptual queries degrade because BM25 magnitudes dominate. Switching to RRF restores conceptual quality with most of the lexical gain, and a later LTR experiment adds only a small lift, so they keep RRF.

## Risk

Choosing a fusion method because its formula looks reasonable, without labelled evaluation, can lock in a worse ranker. Features computed from the candidate set (min-max) can change when the candidate set changes.

## Trade-off

RRF is simple and robust but coarse. Weighted normalized fusion is tunable but fragile. LTR is expressive but needs data and maintenance.

## Try This

Remove candidate D from both score maps and compare min-max results. Then change the RRF constant k from 60 to 5 and observe how rank gaps matter more.

## Execution Timeline

Collect per-retriever candidates and scores -> choose fusion (rank-based, normalized, or learned) -> compute combined order -> evaluate on held-out labelled queries -> deploy and monitor

## Complexity

Fusion itself is O(N log N) for sorting N candidates; the dominant costs are the retrievers. LTR adds feature computation and model inference per candidate.

## Definitions

- **RRF**: Reciprocal Rank Fusion: combine ranked lists by summing 1/(k + rank) per document.
- **Min-max normalization**: Rescaling scores to the range zero to one using the list's minimum and maximum.
- **Learning to rank**: Training a model to order documents using features and relevance labels.
- **nDCG**: Normalized discounted cumulative gain, a ranking metric that rewards placing relevant items higher.

## Alternatives

- Weighted RRF with per-retriever weights
- Cross-encoder reranking over a fused pool
- Query-class routing so each class uses one retriever

## Pitfalls

- Summing raw scores
- Treating min-max output as probability
- Tuning weights on a handful of queries
- Not re-evaluating after embedding or index changes

## Follow-ups

### Why is RRF robust to outliers?

It uses only rank positions, so a score of 60 versus 12 changes nothing beyond the ordering. The trade-off is that information in score gaps is lost.

### What data do you need for learning to rank?

Query-document relevance judgments, from human labels or carefully validated feedback, with enough queries per class and a held-out set. Click data is biased by position and must be handled with care.

### How do you detect that a fusion change hurt?

Run offline per-query comparisons first, then a shadow or canary rollout with online metrics. Examine losses by query class, since an average can hide a class that regressed badly.

## Example

> Explanation: Raw score addition, min-max outliers and RRF can rank the same candidates differently.
> Output: verified

```python
"""Raw score addition, min-max outliers and RRF can rank the same candidates differently."""
DENSE = {"A": 0.90, "B": 0.80, "C": 0.70, "D": 0.20}
BM25 = {"A": 3.0, "B": 12.0, "C": 11.0, "D": 60.0}


def order(scores):
    return [k for k, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]


def minmax(scores):
    lo, hi = min(scores.values()), max(scores.values())
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def rrf(*rankings, k=60):
    out = {}
    for ranking in rankings:
        for rank, key in enumerate(ranking, 1):
            out[key] = out.get(key, 0.0) + 1 / (k + rank)
    return out


raw = {k: DENSE[k] + BM25[k] for k in DENSE}
normalized = {k: minmax(DENSE)[k] + minmax(BM25)[k] for k in DENSE}
fused = rrf(order(DENSE), order(BM25))
assert order(raw) == order(BM25)            # BM25 scale swamps cosine
print("raw", order(raw), "minmax", order(normalized), "rrf", order(fused))
```

## Citations

- https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
- https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/

# How do you combine vector retrieval with a knowledge graph while keeping edge provenance and trust?

<!-- meta
domain: ai-rag
subdomain: graph-retrieval
module: retrieval
concept: graph plus vector retrieval
difficulty: design
misconception_target: Edges extracted by an LLM are verified facts that need no provenance
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Why add a graph.** Passage similarity is weak at relationship questions such as 'Which suppliers are affected by the acquisition of Company B?'. The answer lives in relations across documents, not in a single passage. A graph stores entities and typed relationships and supports multi-hop traversal.

**Hybrid workflow.** (1) Vector or hybrid retrieval finds passages related to the question. (2) Entity linking maps mentions ('OpenAI', 'Open AI', 'the organization') to canonical identifiers, preferably from an authoritative source system. (3) Graph traversal expands from those entities along allowed relationship types and hop limits. (4) For every traversed edge, fetch the supporting source passage. (5) Assemble evidence containing both relationship paths and the underlying text with citations.

**Provenance and trust.** Edges extracted by an LLM can be wrong. Store for each edge the source document and chunk, extraction method, confidence, timestamp and verification status. The example shows that requiring verified edges removes an unverified supplier from the result, and that every returned path includes source IDs so the answer can be audited.

**Failure modes.** Entity extraction errors, wrong entity linking (two companies with similar names), stale relationships, missing temporal validity, and unbounded traversal that explodes in dense graphs. Mitigate with canonical IDs, relationship-type allowlists, hop limits, temporal fields, and tests with ambiguous entities.

**Variants.** GraphRAG is a family of approaches. Some build entity graphs for traversal; others build graph communities with generated summaries to answer corpus-level questions. Choose by the question type, not by trend: if relationships are first-class information needs, a graph helps; if questions are about single-document facts, hybrid text retrieval is simpler.

**Security.** Apply the caller's authorization to nodes, edges and the passages that justify them. An edge can reveal the existence of a restricted relationship even if the document text is hidden.

## Spoken Summary

Vector search finds relevant passages and the entities they mention. I resolve those mentions to canonical entities, traverse the graph for relationships such as acquired or supplied_by, then retrieve the source passages that support each edge. Graph edges produced by an LLM are extractions, not verified facts, so each edge carries source, confidence and a verified flag, and queries can require verified edges. Authorization applies to graph traversal as well as to text search.

## Why

The example starts from seed entities, traverses acquired and supplied_by edges, and returns suppliers with the paths and source IDs. A strict mode drops the unverified edge; a loose mode includes it.

## Production Case

A procurement assistant is asked which suppliers are affected by an acquisition. Vector search finds the announcement, the graph returns suppliers two hops away, and unverified extracted edges are held back for human review while verified ones are answered with contract citations.

## Risk

Unverified LLM-extracted edges presented as facts, mislinked entities, and graph traversal that bypasses document-level authorization.

## Trade-off

Explicit multi-hop reasoning and auditable paths versus extraction, maintenance and consistency costs. A graph is a second system to keep synchronized with the documents.

## Try This

Add a temporal valid_to field to the edges and filter traversal by an as-of date, then add a second company with a similar name to test your entity-linking guard.

## Execution Timeline

Vector retrieval -> extract and link entities -> bounded graph traversal with allowed relations -> fetch supporting passages for each edge -> authorize -> assemble paths plus text evidence

## Complexity

Traversal cost grows with branching factor to the power of hop count, so hop limits and relation allowlists are essential. Vector search remains approximate nearest-neighbour cost; graph storage adds nodes and edges maintenance.

## Definitions

- **GraphRAG**: A family of retrieval-augmented approaches that use graph structure for retrieval or summarization.
- **Entity linking**: Mapping a text mention to a canonical entity identifier.
- **Provenance**: Recorded origin of a fact, including document, extraction method and time.
- **Hop limit**: Maximum number of edges a traversal may follow.

## Alternatives

- Hybrid text retrieval with multi-query when relationships are shallow
- SQL joins when relationships are already in relational tables
- Community-summary GraphRAG for corpus-wide thematic questions

## Pitfalls

- Unbounded traversal
- No edge provenance or confidence
- Skipping authorization on edges
- Linking entities by name string alone

## Follow-ups

### How do you evaluate a graph retriever?

Create questions with gold entity paths and gold supporting passages. Measure path recall and precision, supporting-passage recall, entity-linking accuracy and the verified-edge rate, and compare answers against a text-only baseline.

### How should entity linking be done in an enterprise?

Prefer canonical identifiers from source systems, such as customer or supplier IDs, over names inferred by an LLM. Keep an alias table and review ambiguous matches.

### When is a graph overkill?

When questions are answered by a single passage or a structured table. A graph adds extraction and synchronization costs that only pay off for relationship-centric or multi-hop questions.

## Example

> Explanation: Combine vector-found entities with graph traversal while keeping edge provenance.
> Output: verified

```python
"""Combine vector-found entities with graph traversal while keeping edge provenance."""
EDGES = [
    ("CompanyA", "acquired", "CompanyB", {"source": "press-12", "verified": True}),
    ("CompanyB", "supplied_by", "SupplierX", {"source": "contract-7", "verified": True}),
    ("CompanyB", "supplied_by", "SupplierY", {"source": "llm-extraction-3", "verified": False}),
]


def neighbors(entity):
    return [(rel, dst, meta) for src, rel, dst, meta in EDGES if src == entity]


def affected_suppliers(seed_entities, allow_unverified=False):
    result = []
    for entity in seed_entities:
        for rel, company, meta in neighbors(entity):
            if rel != "acquired":
                continue
            for rel2, supplier, meta2 in neighbors(company):
                if rel2 == "supplied_by" and (meta2["verified"] or allow_unverified):
                    result.append({"supplier": supplier, "path": [entity, company],
                                   "sources": [meta["source"], meta2["source"]]})
    return result


seeds = ["CompanyA"]   # entities linked from vector-retrieved passages
strict = affected_suppliers(seeds)
loose = affected_suppliers(seeds, allow_unverified=True)
assert [r["supplier"] for r in strict] == ["SupplierX"]
assert len(loose) == 2
print(strict)
```

## Citations

- https://arxiv.org/abs/2404.16130
- https://arxiv.org/abs/2005.11401

# How do candidate-pool size and final answer-context size affect different failure modes?

<!-- meta
domain: ai-rag
subdomain: retrieval
module: retrieval
concept: How do candidate-pool size and final answer-context size affect different failure modes?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: The final context has room for five items, but the correct exception never enters a very small candidate pool.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

The candidate pool controls which possibly relevant items are available to later ranking. Final context selection controls what the model actually receives under a token and relevance budget. A reranker cannot recover a needed item excluded upstream. Measure candidate recall, final support coverage, diversity and latency separately.

Concrete engineering case: The final context has room for five items, but the correct exception never enters a very small candidate pool.

Boundary defense: No. The missing item is absent upstream. Diagnose candidate generation and filtering before increasing final-context size.

## Spoken Summary

The candidate pool controls which possibly relevant items are available to later ranking. Final context selection controls what the model actually receives under a token and relevance budget. A reranker cannot recover a needed item excluded upstream. Measure candidate recall, final support coverage, diversity and latency separately.

## Why

The candidate pool controls which possibly relevant items are available to later ranking. Final context selection controls what the model actually receives under a token and relevance budget. A reranker cannot recover a needed item excluded upstream. Measure candidate recall, final support coverage, diversity and latency separately.

## Production Case

The final context has room for five items, but the correct exception never enters a very small candidate pool.

## Risk

The final context has room for five items, but the correct exception never enters a very small candidate pool.

## Trade-off

No. The missing item is absent upstream. Diagnose candidate generation and filtering before increasing final-context size.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: retrieval**: The candidate pool controls which possibly relevant items are available to later ranking.

## Alternatives

- No. The missing item is absent upstream. Diagnose candidate generation and filtering before increasing final-context size.

## Pitfalls

- The final context has room for five items, but the correct exception never enters a very small candidate pool.

## Follow-ups

### Would raising only the final top-k fix this?

No. The missing item is absent upstream. Diagnose candidate generation and filtering before increasing final-context size.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "The final context has room for five items, but the correct exception never enters a very small candidate pool.",
  "required_decision": "The candidate pool controls which possibly relevant items are available to later ranking"
}
```

## Citations

- https://arxiv.org/abs/2005.11401
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
- https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity

# When should metadata filtering happen before vector search, and when is post-filtering acceptable?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Separate eligibility from relevance.** Tenant, access scope, effective date, source version and required product are eligibility constraints. Semantic similarity cannot decide whether a user may see a document. Build mandatory predicates from authenticated application state. Optional preferences, such as favored document type, can instead influence ranking when the user has not required them.

**Understand the candidate set.** Filtering before or during nearest-neighbor search lets ranking operate on eligible records. Filtering only a global top-k list can discard most results without searching for the next eligible neighbors. Provider implementations differ; test actual engine semantics and shard behavior rather than assuming a mode name is portable. Approximate search may still miss eligible neighbors.

**Illustrative counterexample.** Suppose the ten most similar global documents belong to another tenant, while the best authorized document ranks eleventh. Retrieving ten and then filtering gives zero results. Searching within the authorized tenant can find that document. Increasing k can mitigate this example, but it is not a general completeness guarantee and can increase cost.

**Keep security enforcement independent of ranking optimization.** No unauthorized content should reach a reranker, model, client or unprotected log. Recheck permissions before evidence leaves the trusted retrieval boundary, especially when index permissions lag. Treat missing required metadata as ineligible. For a legitimate optional filter with zero hits, explain the restriction and let the user broaden it; never silently relax tenant or access rules.

## Why

A user searches for a policy in a small tenant containing 0.1% of the global corpus. A global top-20 query followed by tenant filtering returns nothing although the relevant document exists. Measure recall against an exact eligible-set baseline.

## Worked Case

A user searches for a policy in a small tenant containing 0.1% of the global corpus. A global top-20 query followed by tenant filtering returns nothing although the relevant document exists. Measure recall against an exact eligible-set baseline.

## Risk

A relevance optimization can become a data leak if authorization is applied only after the model has seen candidates.

## Trade-off

Highly selective eligible sets can make exact filtered search competitive; benchmark latency and recall before choosing an approximate index strategy.

## Try This

Build a corpus with unauthorized nearest neighbors and an authorized lower-ranked match. Compare pre-filter, post-filter and exact eligible-set results.

## Citations

- https://learn.microsoft.com/en-us/azure/search/vector-search-filters

# How do you represent hybrid-search results when a keyword-only hit has no vector distance?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Missing evidence is not a numeric score.** A keyword-only candidate has no observed vector distance for that retrieval path. Represent it as absent, such as a null field, while recording that the keyword channel retrieved it. A real distance of zero can mean an exact vector match and must not be converted to missing data through truthiness checks.

**Keep channel semantics explicit.** Vector distance, cosine similarity, lexical scores and fused ranks have different directions and scales. Record the metric and channel where useful. Do not compare a raw lexical score directly with an arbitrary vector distance or insert zero for a missing distance merely to satisfy a sorting function. Use a fusion method with a documented interpretation, or calibrate scores on the actual task.

**Maintain provenance through fusion.** A candidate can appear in both lists. Deduplicate by a stable document/chunk identity, retain each channel's rank and score, and compute a separate fused value. Reciprocal rank fusion, for example, combines ranks rather than pretending every score has one physical meaning. A missing channel contributes nothing under that formula; it is not treated as a perfect match.

**Test the serialization boundary.** Check keyword-only hits, exact zero distances, negative similarities where valid, equal ranks and empty channels. APIs and UI badges should not label every result as a semantic match just because one query used embeddings. The example demonstrates explicit None checks and a tiny rank-fusion calculation using synthetic ranks.

## Why

A serializing expression 'distance or None' changes an exact distance of 0.0 into null. Replacing null with zero then makes a keyword-only hit look like an exact semantic match. Both errors destroy the meaning of the field.

## Worked Case

A serializing expression 'distance or None' changes an exact distance of 0.0 into null. Replacing null with zero then makes a keyword-only hit look like an exact semantic match. Both errors destroy the meaning of the field.

## Risk

Invented default distances can corrupt ranking, quality diagnostics and user explanations.

## Trade-off

Rank fusion avoids cross-scale score assumptions but discards some score magnitude information; evaluate it against calibrated alternatives.

## Try This

Serialize a zero-distance vector hit and a keyword-only hit, then verify both retain their distinct meaning after a round trip.

## Follow-ups

### Should missing distance sort last?

Only within a UI or diagnostic view that explicitly sorts by observed distance. Production fusion should use its own declared missing-channel policy rather than accidentally inheriting null ordering.

### Can two zero-distance results still be different documents?

Yes. Identical text or embeddings can belong to distinct sources or versions. Preserve provenance and choose deduplication semantics explicitly.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do you build hybrid-search regression tests that survive legitimate ranking changes?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: retrieval
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Test invariants separately from exact rankings.** Stable invariants include eligibility, preserved identifiers, finite vector values, missing-versus-zero semantics and the presence of answer-critical evidence within a measured retrieval budget. The exact order of two equally useful passages may legitimately change after an index or model upgrade.

**Build a query matrix from failure classes.** Include exact identifiers, paraphrases, typos, rare terms, numerical constraints, empty metadata, cross-tenant nearest neighbors, no-hit queries and keyword-only evidence. Specify acceptable source sets and required exclusions. For a question requiring two supporting clauses, define evidence-set coverage rather than counting either clause as a complete success.

**Compare against an appropriate oracle.** For small filtered fixtures, use exact eligible-set search or explicit labels to isolate approximate-retrieval losses. Report recall at k and mean reciprocal rank (MRR), including the chosen relevance rule and denominator. Aggregate scores need per-category slices so a rare-identifier regression cannot hide behind many easy paraphrases. Treat ties and nondeterministic index behavior explicitly.

**Use release thresholds rather than one fragile golden list.** Pin model, corpus, tokenizer and filter configuration for a regression run. Permit reviewed ranking changes when evidence and operational constraints still pass, and keep the old baseline for comparison. The local example checks required evidence and forbidden candidates while allowing two valid orderings; it intentionally does not emulate a search engine.

## Why

An upgraded retriever swaps two equally relevant passages, so an exact-list test fails despite unchanged answer support. Meanwhile a tenant filter regression passes because the golden test never asserted forbidden identifiers.

## Worked Case

An upgraded retriever swaps two equally relevant passages, so an exact-list test fails despite unchanged answer support. Meanwhile a tenant filter regression passes because the golden test never asserted forbidden identifiers.

## Risk

Overly exact rankings create noisy tests; only aggregate metrics can hide serious category failures.

## Trade-off

Invariant and category checks are more durable, while a few carefully chosen exact fixtures still help isolate deterministic serialization defects.

## Try This

Build ten queries across five failure classes. Include one query requiring two sources and one with an unauthorized nearest neighbor.

## Follow-ups

### Can recall at k establish final answer correctness?

No. It measures retrieval under a relevance definition. The generator may ignore, distort or incorrectly combine the retrieved evidence, requiring separate answer checks.

### Should a no-hit query automatically fail?

Not if no eligible evidence exists. Label expected empty outcomes and distinguish them from retrieval misses on answerable questions.

## Citations

- https://scikit-learn.org/stable/modules/model_evaluation.html

# How do lexical retrieval, dense retrieval and cross-encoder reranking complement one another?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: retrieval
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Lexical retrieval rewards token matches under a scoring model, dense retrieval compares learned representations, and a cross-encoder jointly scores a query/candidate pair. They fail differently: identifiers can favor exact matching, paraphrases can favor dense representations, and joint scoring can improve ordering of a bounded candidate set. A reranker cannot recover a relevant item absent from that set. Fuse or combine ranks under an evaluated policy rather than directly averaging incompatible raw score scales. Apply authorization consistently before evidence is exposed.

## Why

A product code can be missed by a dense encoder while a paraphrased question misses lexical terms. Taking authorized candidates from both can improve coverage before a more expensive reranker selects a small final set.

## Worked Case

A product code can be missed by a dense encoder while a paraphrased question misses lexical terms. Taking authorized candidates from both can improve coverage before a more expensive reranker selects a small final set.

## Risk

A better reranker may leave candidate-recall failures unchanged.

## Trade-off

Spend expensive scoring on candidates with demonstrated coverage value.

## Try This

Separate candidate recall from final ranking quality for exact-code and paraphrase queries.

## Citations

- https://arxiv.org/abs/2005.11401
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html
- https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity
