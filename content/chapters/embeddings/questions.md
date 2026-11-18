<!-- chapter: embeddings -->

# What is an embedding, and why is its dimension not enough to identify it?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: embeddings
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**An embedding maps an input into a numerical vector intended to preserve some learned notion of similarity.** A bi-encoder embeds queries and documents separately, enabling precomputed document vectors. A cross-encoder scores a query-document pair jointly and is usually more expensive per candidate. Neither similarity nor a model score proves a passage is true, current, authorized or sufficient to answer the question.

Use one compatible embedding profile: model/revision, query/document instructions, normalization, dimension and distance metric. Changing the model while keeping the same vector dimension does not preserve the geometry. Index and query vectors from incompatible spaces can produce plausible numbers with meaningless rankings. Reject a profile mismatch or build a new index and compare it before switching; do not silently coerce dimensions.

**Calculate a simple case.** For q=(1,1), a=(1,0), cosine is dot(q,a)/(norm(q)norm(a))=1/sqrt(2), about 0.7071. For b=(0,1) the score is identical. This tie says nothing about whether a is an applicable refund policy or b belongs to another tenant. Filter by trusted principal, active revision and deletion status before candidates leave the retrieval boundary. A high score from a foreign owner remains forbidden.

Learned dense retrieval can recover paraphrases with little lexical overlap, but can miss exact identifiers, negation and domain-specific distinctions. Lexical search can complement it. Compare against a fixed corpus and independently labeled queries; report per-slice recall rather than announcing that dense always wins. `grounded_policy_pipeline.py` uses hand-authored two-dimensional vectors to demonstrate cosine and fusion. `policy_assistant_project.py` uses lexical and coverage rankers and explicitly has no learned embeddings. To add a real model, pin its license/revision and normalization, regenerate both sides, save corpus/profile hashes and rerun owner, revision, paraphrase and refusal cases. A toy score is never evidence of real-model quality.

## Why

Two unit-axis document vectors tie at cosine 0.7071 for query (1,1). The eligibility filter and evidence meaning must decide what can be used; changing the owner must never be solved by similarity.

## Worked Case

Two unit-axis document vectors tie at cosine 0.7071 for query (1,1). The eligibility filter and evidence meaning must decide what can be used; changing the owner must never be solved by similarity.

## Risk

An embedding migration can silently mix coordinate systems. Similar dimensions and valid floating-point values do not make profiles interchangeable.

## Trade-off

Precomputed bi-encoder vectors make broad search efficient; cross-encoders can improve pairwise relevance but add inference latency and cannot recover candidates that were never retrieved.

## Try This

Run foundation_bridge.py and grounded_policy_pipeline.py. Recalculate the cosine tie by hand, then change a vector profile and demonstrate a fail-closed compatibility policy.

## Follow-ups

### Does normalization make dot product and cosine interchangeable?

For nonzero unit-normalized vectors their rankings coincide. Without that contract, dot product also reflects vector magnitude; zero vectors and implementation conventions need explicit handling and tests.

## Citations

- https://arxiv.org/abs/1908.10084
- https://faiss.ai/cpp_api/struct/structfaiss_1_1IndexFlatIP.html

# Why distinguish document and query embedding modes?

## Answer

Some embedding models are trained asymmetrically: a short question and a longer passage use different task instructions or modes but remain in a compatible retrieval space. Symmetric models use the same treatment for both. The correct mode is part of the model's intended retrieval contract.

## Why

A task mode represents DOCUMENT, QUERY, and SYMMETRIC. Query-vector helpers can call embed_query, while document processing can use document embedding methods. Profile compatibility deliberately allows different task modes for an otherwise matching pair.

## Risk

A generic callable may erase mode distinctions unless the adapter implements them correctly. Also, the compatibility helper does not compare preprocessing_config, so custom instruction compatibility needs additional validation.

## Trade-off

Task-aware interfaces improve provider fidelity but add API surface. A plain callable remains convenient for simple symmetric embedders and offline demonstrations.

## Try This

Inspect a custom adapter's query and document paths. Verify the instructions each sends and explain whether profile equality or query compatibility is the appropriate check.

# How do cosine, dot product, and L2 differ?

## Answer

Cosine compares direction, dot product combines alignment and magnitude, and L2 measures Euclidean separation. For unit-normalized vectors, squared L2 equals two minus twice the dot product, and dot product equals cosine similarity. Without normalization, those ranking relationships need not hold.

## Why

Profile enums describe metric and normalization. Stores translate the chosen metric into their backend semantics, while result scores distinguish lower-is-better distance from higher-is-better relevance.

## Risk

A threshold calibrated for one metric cannot safely be reused for another. Unknown dimensions and unnormalized vectors can also make low-level helpers behave unexpectedly if callers bypass validation.

## Trade-off

Cosine often fits directional semantic comparisons; dot product may intentionally use norm information. The right choice follows the embedding model and index configuration, then empirical evaluation.

## Try This

Compare vectors [1,0], [2,0], and [0,1] under all three measures. Predict which pairs tie and why normalization changes the answer.

# What validation should happen before storing embedding responses?

## Answer

Check one vector per input, the expected dimension, and finite numeric values. Preserve input-output order. A response with fewer vectors must fail rather than silently pair only a prefix of the chunks with embeddings.

## Why

A bounded embedding executor validates response count and geometry; the ingestion coordinator uses strict zip alignment and validates each chunk vector before mutation. Preparation failures therefore occur before the version-switching critical section.

## Risk

Valid shape does not prove semantic quality or correct provider task mode. A constant vector can pass shape validation and still destroy retrieval usefulness, so quality evaluation remains separate.

## Trade-off

Validation costs a pass over returned coordinates but prevents durable index corruption that is expensive to diagnose later. Skipping it is only a superficial throughput optimization.

## Try This

Use fake providers returning too few vectors, wrong dimensions, NaN, and identical finite vectors. Identify which failures validation catches and which require a retrieval test.

# How do retries and exponential backoff help without fixing every outage?

## Answer

Retries can recover transient network, rate-limit, and service failures. Exponential backoff delays repeated attempts; jitter reduces synchronized retry bursts. Permanent authentication, configuration, and dimension errors should fail promptly because identical retries are unlikely to help.

## Why

A bounded embedding executor classifies exceptions, honors exposed Retry-After hints, applies a retry ceiling, and validates responses. Cancellation is propagated rather than treated as another retryable failure.

## Risk

Classification includes message-pattern heuristics and treats unknown errors as transient. Misclassification can waste calls, and Retry-After can extend operation duration. The host still needs an overall deadline and provider-specific error handling where necessary.

## Trade-off

More retries improve recovery probability while increasing tail latency, cost, and load during an outage. Bound them against the request's purpose and budget.

## Try This

Simulate two transient failures followed by success, then a permanent failure. Record attempts and delays using injected clock and sleep functions.

# What do concurrency limits, queue bounds, and backpressure actually mean here?

## Answer

A semaphore limits simultaneous work inside one execution scope. A bounded queue limits waiting items. Backpressure controls how producers react when capacity is exhausted. None alone establishes a fleet-wide capacity limit.

## Why

Combine a bounded producer queue, explicit worker concurrency, request deadlines, and shared provider quotas where needed. Instrument queue time separately from provider latency; an async batch is not a durable job.

## Risk

Many waiting tasks or many process-local executors can still overwhelm memory or a shared provider quota. The host needs admission control and, when appropriate, a bounded job queue and shared quota policy.

## Trade-off

Small concurrency limits protect providers and increase waiting latency. Larger values improve throughput until the actual service or connection pool saturates.

## Try This

Launch many calls through one executor and then through several instances. Measure in-flight operations and explain why a process-local semaphore is not a global rate limiter.

# How does embedding caching preserve isolation and compatibility?

## Answer

Cache identity combines isolation scope, content hash, embedding profile hash, and task mode. Reusing a vector is safe only when these semantic inputs match the deployment's policy. A content hash alone is insufficient for model changes or tenant isolation.

## Why

A scoped embedding cache uses scoped keys by default, copies vectors on storage and retrieval, supports LRU capacity and optional TTL, and requires explicit opt-in for cross-tenant sharing. It is an in-process component, not a distributed cache.

## Risk

Cross-tenant reuse can leak equality signals or complicate retention obligations. The class is not thread-safe, and TTL expiry alone is not immediate revocation. The host must align cache scope and purge behavior with its privacy policy.

## Trade-off

More isolation reduces hit rate while keeping independent data lifecycles manageable. Shared caching saves calls but needs a justified policy.

## Try This

Cache identical content in two scopes with different profiles and task modes. Verify the allowed hits and test scope invalidation.

# How should an embedding model migration be rolled out?

## Answer

Treat a vector-space change as a new index generation. Build and validate new vectors without mixing them into the old query space, evaluate quality, activate the new generation, and retain a rollback plan. Query embeddings must switch compatibly with the active documents.

## Why

Profiles_require_reindex compares canonical hashes, while ingestion snapshots and sync generation mechanisms support detecting configuration changes and controlling visibility. They provide building blocks, not a complete deployment orchestrator for every backend.

## Risk

Switching only the query model can silently degrade retrieval. Reusing caches or thresholds calibrated for the old profile can also invalidate conclusions even if dimensions remain equal.

## Trade-off

Parallel generations need extra storage and embedding cost but permit verification before cutover. In-place replacement is cheaper and harder to roll back safely.

## Try This

Write a migration checklist with a shadow evaluation, profile hash check, activation condition, and rollback trigger. State how queries choose the active profile.

# Why can a hashing embedder demonstrate plumbing but not semantic intelligence?

## Answer

The quickstart hashes tokens into a small vector and normalizes it. Shared words produce shared coordinates, making an offline demonstration deterministic and cheap. It has no learned semantic representation and cannot reliably associate paraphrases that share little vocabulary.

## Why

A retrieval-service builder.local requires an injected embedder; core does not ship pretrained neural weights. The example deliberately supplies a fake so build, ingest, and search can run without API keys or external services.

## Risk

Treating success on that example as proof of production retrieval quality confuses system integration with representation learning. Hash collisions can also make unrelated text appear close in a tiny space.

## Trade-off

A fake is excellent for controlled tests and onboarding, while a learned provider is needed to evaluate realistic semantic behavior. Keep those purposes distinct.

## Try This

Search with a synonym-only paraphrase and compare it to an exact-word query. Explain the difference using the hashing algorithm rather than attributing it to an LLM.

# How should I measure embedding throughput and cost responsibly?

## Answer

Track documents and tokens processed, batches, retries, cache hits, provider latency, and validation failures. Estimate total spend using actual provider usage where available; heuristic token estimates are useful for scheduling but are not billing records.

## Why

Embedding metrics and telemetry support operational accounting, while the executor splits batches and can enforce a soft estimated-input cap. Separating preparation from transactions prevents slow provider calls from unnecessarily occupying ingestion locks.

## Risk

Average latency hides retries and tail behavior. A low per-batch cost can become expensive when overlap, query expansion, and repeated full indexing multiply input volume.

## Trade-off

Detailed metrics improve tuning while high-cardinality labels and raw text logging create overhead and privacy risks. Prefer aggregated, sanitized dimensions.

## Try This

Compare a cold ingestion with an unchanged-source rerun and a model-change rerun. Attribute work saved by snapshot skipping separately from cache hits.

# When do cosine similarity, dot product, and Euclidean distance produce the same ranking?

<!-- meta
domain: ai-rag
subdomain: embeddings
module: embeddings
concept: metric equivalence under normalization
difficulty: mechanism
misconception_target: Cosine is always the best metric and is unrelated to dot product or Euclidean distance
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**The three measures.** Cosine similarity is `A.B / (|A||B|)` and measures direction only. The dot product `sum(A_i B_i)` grows with both direction alignment and vector magnitude. Euclidean (L2) distance `sqrt(sum((A_i - B_i)^2))` measures straight-line separation.

**Why normalization unifies them.** If `|A| = |B| = 1`, then `A.B` is exactly the cosine. Expanding squared distance gives `|A-B|^2 = |A|^2 + |B|^2 - 2 A.B = 2 - 2 A.B`. Distance decreases exactly when the dot product increases, so ranking by smallest L2 is the same as ranking by largest cosine. In the example, the normalized cosine and normalized L2 orders match, while raw dot product on unnormalized vectors places a large-magnitude, poorly aligned vector first.

**Practical consequences.** (1) Check what the model card recommends, since some models are trained with a specific metric and some expose meaningful magnitude. (2) If vectors are normalized at write time, dot-product indexes are cosine-equivalent and often cheaper. (3) Keep query and document normalization identical, and record it in the embedding configuration alongside model name, version and dimension. (4) Make sure the vector database operator matches: in pgvector, `<=>` is cosine distance, `<#>` is negative inner product, `<->` is L2 distance, and an index must be built with the matching operator class.

**Do not over-read the number.** A high similarity indicates closeness in the model's space, not that the passage contains enough evidence to answer. Thresholds are model-specific and uncalibrated.

## Spoken Summary

They agree when vectors are L2-normalized to unit length. For unit vectors cosine equals the dot product, and squared Euclidean distance equals two minus two times the dot product, so sorting by any of them gives the same order. Without normalization, a dot product also rewards magnitude, so a long vector can outrank a better-aligned one. The right metric is the one the embedding model was trained for, and the index distance operator must match how vectors were normalized.

## Why

The example normalizes a query and three vectors, ranks with cosine and with L2, asserts they are equal, and shows that the raw dot product ranking differs because vector b has a large magnitude.

## Production Case

A team stores normalized embeddings but builds an HNSW index with the L2 operator class and queries with cosine distance. The planner ignores the index for those queries and latency spikes. Aligning operator class, normalization and query operator fixes it without changing results.

## Risk

Mixing a normalized index with a raw-dot-product query path, or using the wrong pgvector operator class, silently degrades ranking while queries still return results.

## Trade-off

Normalizing costs a division per vector and discards magnitude information. It simplifies metrics and makes dot-product indexes cosine-equivalent.

## Try This

Multiply vector a by 100 and re-run. Confirm normalized rankings do not change but the raw dot ranking does.

## Execution Timeline

Choose metric from model guidance -> normalize at write and query time if required -> store embedding configuration -> build index with matching operator -> verify ranking on a labelled sample

## Complexity

Normalization is O(d) per vector; all three measures are O(d) per comparison. Index search cost is governed by the ANN index, not the metric choice.

## Definitions

- **L2 normalization**: Scaling a vector so its Euclidean length is one.
- **Cosine similarity**: Dot product divided by the product of vector lengths; compares direction.
- **Inner product**: Sum of element-wise products; depends on magnitude and direction.
- **Operator class**: pgvector setting that tells an index which distance function it accelerates.

## Alternatives

- Keep raw vectors and use the model's trained metric
- Normalize at ingest and use inner product for speed
- Use cosine operators directly and let the database normalize

## Pitfalls

- Normalizing documents but not queries
- Wrong index operator class
- Assuming a universal similarity threshold
- Changing normalization without rebuilding the index

## Follow-ups

### Can magnitude carry useful information?

In some architectures, yes, for example popularity-like or confidence-like signals encoded in length. Normalizing would erase it, which is why you follow the model's documented usage and validate on labelled queries.

### Why do rankings match but scores differ?

L2 distance and cosine are monotonic transforms of one another for unit vectors, so order is preserved while the numerical values and any thresholds are different.

### How do you set a similarity cutoff?

Do not borrow a number. Collect labelled relevant and irrelevant pairs for your model and data, inspect the score distributions, and choose a cutoff for a target precision or recall; re-check after any model or index change.

## Example

> Explanation: For unit vectors, cosine, dot product and Euclidean distance rank documents identically.
> Output: verified

```python
"""For unit vectors, cosine, dot product and Euclidean distance rank documents identically."""
import math

DOCS = {"a": (3.0, 4.0), "b": (30.0, 10.0), "c": (1.0, 5.0)}
QUERY = (2.0, 3.0)


def unit(v):
    n = math.hypot(*v)
    return tuple(x / n for x in v)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def l2(a, b):
    return math.dist(a, b)


def rank(key, reverse):
    return [n for n, _ in sorted(DOCS.items(), key=lambda kv: key(kv[1]), reverse=reverse)]


raw_dot = rank(lambda d: dot(QUERY, d), True)
nq = unit(QUERY)
norm = {n: unit(v) for n, v in DOCS.items()}
cos_rank = [n for n, _ in sorted(norm.items(), key=lambda kv: dot(nq, kv[1]), reverse=True)]
l2_rank = [n for n, _ in sorted(norm.items(), key=lambda kv: l2(nq, kv[1]))]
assert cos_rank == l2_rank
assert raw_dot != cos_rank
print("raw_dot", raw_dot, "normalized_cosine", cos_rank, "normalized_l2", l2_rank)
```

## Citations

- https://github.com/pgvector/pgvector
- https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html

# Why can embeddings confuse $50,000 with $500,000, and how do you retrieve exact values reliably?

<!-- meta
domain: ai-rag
subdomain: embeddings
module: embeddings
concept: exact values and structured constraints
difficulty: debugging
misconception_target: A strong embedding model will distinguish exact numbers and identifiers
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**The failure.** Consider 'Maximum coverage is $50,000 for hospitalization' and 'Maximum coverage is $500,000 for hospitalization'. The surrounding language is identical, and embedding models often assign digits little weight relative to words. A dense retriever can rank both nearly equally, and the generator may then quote the wrong one. The same happens with product codes, regulation numbers, error codes and timestamps.

**Design principles.** (1) Treat exact requirements as constraints, not preferences. If the user gives a policy number, look it up by an indexed column; do not hope similarity finds it. (2) Extract structured attributes at ingestion, such as amount, currency, effective date and identifier, into typed fields. (3) For identifier-like tokens use lexical retrieval (BM25 or full-text search) with analyzers that preserve underscores, case and punctuation. (4) For mixed questions, run hybrid retrieval and fuse rankings, but keep hard constraints as filters. (5) Validate after retrieval: confirm the requested value appears in the evidence and that its scope (policy, version, date) matches.

**Reading the example.** A toy semantic vector built only from words gives both passages the same score, so similarity cannot pick the right one, whereas an exact numeric filter returns only the matching record. The toy exaggerates by ignoring digits entirely; real embeddings may weight them slightly, but not reliably enough to enforce equality.

**Interview framing.** Semantic search finds relevant neighbourhoods; structured access guarantees exact facts. Mature systems combine both and make the exact path deterministic.

## Spoken Summary

Embeddings are trained for semantic similarity, so two passages that differ only in a number, date or identifier can score almost identically. Dense retrieval therefore cannot be trusted to enforce exact values. For constraints like a policy number, an amount or a date range, I use structured fields and exact-match or numeric filters, lexical retrieval for identifiers, hybrid search for mixed queries, and a final validation that the retrieved evidence actually contains the requested value.

## Why

The example makes the limitation visible by construction: identical semantic scores, then an exact filter on a typed field. It models the principle, not a specific embedding model's numeric behaviour.

## Production Case

A claims assistant is asked about 'policy P-1027 hospitalization limit'. Dense search surfaces similar policies. Moving policy ID to an exact filter and amount extraction to a typed column returns the single correct record, and a validator checks the cited text contains the number before the answer is shown.

## Risk

A confident answer quoting the wrong amount or the wrong policy version. In regulated domains this is a high-severity defect that raw similarity scores will not reveal.

## Trade-off

Structured extraction and typed schemas add ingestion work and require maintenance when document formats change, but they make exact lookups deterministic and fast.

## Try This

Add a date field to each passage and filter on 'effective during 2025'. Then write a validator that rejects a final answer whose quoted amount does not appear in the cited evidence.

## Execution Timeline

Parse query for identifiers, amounts and dates -> apply typed filters and authorization -> lexical and dense retrieval within the filtered set -> fuse -> validate requested value in evidence -> answer or abstain

## Complexity

Indexed exact lookups are O(log n) or better in a relational database; hybrid retrieval costs the sum of its retrievers plus fusion.

## Definitions

- **Hard constraint**: A requirement that must be enforced exactly, such as an identifier, date range or tenant.
- **Typed field**: A structured attribute with a defined data type, such as integer amount or date.
- **Lexical retrieval**: Search based on matching terms, for example BM25 or full-text search.
- **Evidence validation**: Checking that the claimed fact appears in the retrieved passage.

## Alternatives

- Pure SQL for fully structured questions
- Hybrid retrieval with identifier-aware analyzers
- Key-value lookup service for IDs resolved before retrieval

## Pitfalls

- Relying on cosine similarity to enforce equality
- Analyzers that strip underscores or case from identifiers
- Skipping post-retrieval validation
- Putting hard constraints into the embedding text only

## Follow-ups

### What about numeric comparisons such as 'limit above $20,000'?

Use a typed numeric column and a range predicate. Semantic search selects the topic (dental surgery), while the predicate enforces the number. Never encode inequality in an embedding query.

### How do you handle a user typing the identifier with different formatting?

Normalize identifiers deterministically (case, separators) for both stored values and queries, keep the original for display, and test those variants explicitly.

### Does a reranker fix this?

Not reliably. A cross-encoder may weigh the number more, but equality is a deterministic requirement and should be enforced by a filter or validator.

## Example

> Explanation: Semantic similarity can tie on near-identical passages; exact values need structured constraints.
> Output: verified

```python
"""Semantic similarity can tie on near-identical passages; exact values need structured constraints."""
import math
import re
from collections import Counter

PASSAGES = [
    {"id": "p1", "limit": 50000, "text": "Maximum coverage is $50,000 for hospitalization"},
    {"id": "p2", "limit": 500000, "text": "Maximum coverage is $500,000 for hospitalization"},
]


def semantic_vector(text):
    # Toy stand-in: words carry meaning, digits barely register, as in many embedding models.
    return Counter(re.findall(r"[a-z]+", text.lower()))


def cosine(a, b):
    dot = sum(a[t] * b[t] for t in a)
    return dot / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())))


query = "hospitalization maximum coverage 50000"
scores = {p["id"]: round(cosine(semantic_vector(query), semantic_vector(p["text"])), 3) for p in PASSAGES}
exact_amount = int(re.search(r"\d+", query).group())
exact = [p["id"] for p in PASSAGES if p["limit"] == exact_amount]
assert len(set(scores.values())) == 1 and exact == ["p1"]
print("semantic_scores", scores, "exact_filter", exact)
```

## Citations

- https://www.postgresql.org/docs/current/textsearch.html
- https://arxiv.org/abs/2005.11401

# Why must embedding model identity and preprocessing be part of an index migration?

<!-- meta
domain: mathematics
subdomain: embeddings
module: embeddings
concept: Why must embedding model identity and preprocessing be part of an index migration?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: An index accepts the same vector dimension from another model, but semantic ranking collapses despite no type error.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Vectors are meaningful under their producing model, dimensions, normalization and input preparation. Do not mix incompatible generations or query a new model against old vectors without a verified compatibility claim. Build a new projection, evaluate representative and permission slices, then promote with a rollback plan and explicit generation identity.

Concrete engineering case: An index accepts the same vector dimension from another model, but semantic ranking collapses despite no type error.

Boundary defense: No. They establish only a shape. The learned representation and metric contract can still differ.

## Spoken Summary

Vectors are meaningful under their producing model, dimensions, normalization and input preparation. Do not mix incompatible generations or query a new model against old vectors without a verified compatibility claim. Build a new projection, evaluate representative and permission slices, then promote with a rollback plan and explicit generation identity.

## Why

Vectors are meaningful under their producing model, dimensions, normalization and input preparation. Do not mix incompatible generations or query a new model against old vectors without a verified compatibility claim. Build a new projection, evaluate representative and permission slices, then promote with a rollback plan and explicit generation identity.

## Production Case

An index accepts the same vector dimension from another model, but semantic ranking collapses despite no type error.

## Risk

An index accepts the same vector dimension from another model, but semantic ranking collapses despite no type error.

## Trade-off

No. They establish only a shape. The learned representation and metric contract can still differ.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: embeddings**: Vectors are meaningful under their producing model, dimensions, normalization and input preparation.

## Alternatives

- No. They establish only a shape. The learned representation and metric contract can still differ.

## Pitfalls

- An index accepts the same vector dimension from another model, but semantic ranking collapses despite no type error.

## Follow-ups

### Do matching dimensions prove compatibility?

No. They establish only a shape. The learned representation and metric contract can still differ.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "An index accepts the same vector dimension from another model, but semantic ranking collapses despite no type error.",
  "required_decision": "Vectors are meaningful under their producing model, dimensions, normalization and input preparation"
}
```

## Citations

- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1603.09320

# How do you embed millions of chunks when the provider is slower than ingestion?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: embeddings
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Treat embedding as a rate-limited, restartable stage.** Count tokens before enqueueing a request and enforce per-input limits plus batch token and item limits. Schedule against both requests per minute and tokens per minute; a batch that fits one quota may exceed the other. Avoid launching an unbounded task for every chunk.

**Apply backpressure upstream.** A bounded queue makes a producer wait when the consumer falls behind. For multi-process or restartable work, use a durable queue and object references; an in-memory queue alone does not survive a crash. Enforce queued-byte and oldest-job-age limits. Stop admitting new work or spill to durable storage before RAM grows without bound. Use a shared quota coordinator when many workers share one provider account.

**Retry the logical chunk, not the entire upload.** Give each work item a deterministic identity derived from tenant, source version, chunk position/content policy, embedding model and preprocessing version. Handle partial batch failures separately. Retry transient failures with bounded exponential backoff and jitter, honor server retry guidance, and put persistent failures in a reviewable dead-letter state. A timeout may mean the provider processed the request; application deduplication prevents duplicate index records but may not prevent duplicate billing.

**Publish a coherent version.** Store vector dimension, model identifier, normalization policy and source lineage. Do not mix incompatible embeddings in the same similarity space. Verify expected chunk counts and failure policy before activating the new index version. Report throughput, token cost, backlog age and failed chunks so operators can distinguish slow progress from a stalled job.

## Why

A parser emits 1,000 chunks per second while embedding capacity is 100. A 10,000-chunk queue fills in roughly 11.1 seconds at a net 900 per second. Enlarging RAM delays the failure; throttling and durable backlog management address it.

## Worked Case

A parser emits 1,000 chunks per second while embedding capacity is 100. A 10,000-chunk queue fills in roughly 11.1 seconds at a net 900 per second. Enlarging RAM delays the failure; throttling and durable backlog management address it.

## Risk

Naive retries can create a thundering herd, duplicate charges and an index containing mixed model versions.

## Trade-off

Larger batches reduce request overhead but increase failure blast radius and wait time for small jobs.

## Try This

Simulate a quota reduction and partial batch failure. Show bounded memory, fair scheduling across tenants and exactly one active vector record per logical chunk.

## Citations

- https://docs.python.org/3/library/asyncio-queue.html

# How do contrastive objectives and hard negatives shape embedding behavior?

<!-- meta
answer_format: conceptual
domain: mathematics
subdomain: embeddings
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An embedding model learns a representation under its training objective; closeness is not an inherent property of language. Contrastive training pulls selected positive pairs together and separates negatives under a specified loss and sampling policy. Hard negatives can teach subtle distinctions but mislabeled negatives can repel genuinely relevant evidence. Match the training pair construction to query and document roles and keep held-out evaluation separate. Evaluate important slices after adaptation because improvement on average can erase a domain-specific distinction.

## Why

'Refund allowed' and 'refund not allowed' share many words but have opposite applicability. Reviewed hard negatives can expose that error, while treating a valid exception as an irrelevant negative would damage the desired ranking.

## Worked Case

'Refund allowed' and 'refund not allowed' share many words but have opposite applicability. Reviewed hard negatives can expose that error, while treating a valid exception as an irrelevant negative would damage the desired ranking.

## Risk

A high similarity score is not a calibrated probability of answer support.

## Trade-off

Domain adaptation helps when errors justify it and labels are reliable.

## Try This

Review positive and hard-negative pairs for a negation-sensitive retrieval task.

## Citations

- https://arxiv.org/abs/1706.03762
- https://arxiv.org/abs/1603.09320
