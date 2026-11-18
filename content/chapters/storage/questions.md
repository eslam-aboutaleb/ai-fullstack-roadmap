<!-- chapter: storage -->

# What does a vector database store besides vectors?

<!-- meta
domain: ai-rag
subdomain: storage
concept: What does a vector database store besides vectors
difficulty: foundations
misconception_target: One storage backend handles all retrieval needs
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

A useful retrieval record contains identity, text or a text reference, a vector, and filterable metadata. Production systems also need revision and scope information, deletion semantics, and an explicit persistence model. A fast nearest-neighbor API alone does not provide those guarantees.

## Spoken Summary

A retrieval store may keep vectors, searchable text and metadata such as owner scope, document revision and source spans. Backend capabilities vary. Compare indexing, filtering, consistency, deletion and backup contracts rather than assuming every vector database provides equivalent authorization and durability.

## Why

The retrieval service's store contracts combine or separate writing, vector search, lexical search, fetch, and deletion. Backend capability declarations describe which operations and constraints the adapter actually supports.

## Production Case

A document is revoked but its vector and cached passage remain. Reconcile all derived stores and enforce current source access at retrieval and document-read boundaries.

## Risk

An index that returns similar vectors but cannot enforce a required tenant filter is unsuitable for that request. Capability validation rejects unsupported mandatory constraints instead of silently ignoring them.

## Trade-off

A general-purpose database can unify transactional metadata and vectors; a specialist engine can offer different scaling and operational features. Compare the adapter's concrete guarantees rather than category labels.

## Try This

Create a decision matrix for persistence, filters, lexical search, transactions, generation visibility, and deletion latency for two candidate backends.

## Execution Timeline

Ingest document -> Extract embeddings and keywords -> Store in appropriate backends -> Query routes to correct backend -> Merge and rank results

## Complexity

Exact vector comparison scales with corpus size and vector dimension. Approximate-search performance and recall depend on index/settings/data; inverted-index queries depend on posting lists and filtering, not merely term count.

## Definitions

- **Vector storage**: Stores embeddings and supports ANN similarity search
- **Keyword storage**: Indexes exact terms for lexical search
- **Document storage**: Keeps full documents with structured fields and filters

## Alternatives

- Single backend with hybrid support
- Separate specialized backends

## Pitfalls

- Vector-only misses exact SKUs
- Keyword-only misses synonyms
- Inconsistent metadata across backends

## Follow-ups

### Does a metadata filter automatically establish row-level security?

No. It must be derived from trusted scope and enforced for every path, with backend semantics and negative tests understood.

## Example

> Explanation: Store in both backends, query both, merge results.
> Output: Merged ranked results from both backends

```python
vector_store.add(embeddings, metadata)
keyword_index.add(texts, doc_ids)
results = hybrid_query(query, vector_store, keyword_index)
```

## Citations

- https://redis.io/docs/latest/develop/search/

# Why use PostgreSQL with pgvector and full-text search?

<!-- meta
domain: ai-rag
subdomain: storage
module: storage
concept: Why use PostgreSQL with pgvector and full-text search
difficulty: foundations
misconception_target: One storage backend handles all retrieval needs
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

PostgreSQL can combine relational filters, vector distance, lexical ranking, and host-managed transactions in one database. This is attractive when the application already depends on PostgreSQL and wants retrieval to participate in existing data governance.

## Spoken Summary

PostgreSQL can combine transactional source state with full-text search and vector capabilities through an extension such as pgvector. This can simplify operations and joins, but index/filter behavior, workload isolation and capacity need measurement. A dedicated search system may fit different scale or latency needs.

## Why

The PostgreSQL vector adapter builds table-agnostic SQL from validated identifiers and uses database-specific search operations. The host supplies schema and sessions; the adapter does not turn every database into PostgreSQL or own every application migration.

## Production Case

A team already operates PostgreSQL and wants one authoritative ownership model. Start with a measured search baseline, inspect query plans and test mixed transactional/search workloads before adding a second storage platform.

## Risk

Database extension setup, indexes, pool sizing, and query plans still need operational care. The presence of pgvector does not prove that an approximate index is configured or used for a particular query.

## Trade-off

One database reduces cross-system coordination but couples workloads and capacity. A separate vector service isolates scaling while introducing another consistency and authorization boundary.

## Try This

Explain what an EXPLAIN plan would need to show before you claim a vector query uses an ANN index. Keep that distinct from the Python adapter's API.

## Execution Timeline

Ingest document -> Extract embeddings and keywords -> Store in appropriate backends -> Query routes to correct backend -> Merge and rank results

## Complexity

Exact vector comparison scales with corpus size and vector dimension. Approximate-search performance and recall depend on index/settings/data; inverted-index queries depend on posting lists and filtering, not merely term count.

## Definitions

- **Vector storage**: Stores embeddings and supports ANN similarity search
- **Keyword storage**: Indexes exact terms for lexical search
- **Document storage**: Keeps full documents with structured fields and filters

## Alternatives

- Single backend with hybrid support
- Separate specialized backends

## Pitfalls

- Vector-only misses exact SKUs
- Keyword-only misses synonyms
- Inconsistent metadata across backends

## Follow-ups

### When would you add a dedicated vector service?

When measured requirements such as corpus scale, isolation, indexing throughput or query latency justify its additional operational and consistency boundaries.

## Example

> Explanation: Store in both backends, query both, merge results.
> Output: Merged ranked results from both backends

```python
vector_store.add(embeddings, metadata)
keyword_index.add(texts, doc_ids)
results = hybrid_query(query, vector_store, keyword_index)
```

## Citations

- https://redis.io/docs/latest/develop/search/

# What is ANN, and how is it different from exact nearest-neighbor search?

## Answer

Approximate Nearest Neighbor search trades guaranteed exact ranking for faster search over large vector collections. Exact search compares against all eligible vectors and provides a useful correctness baseline. Algorithms such as HNSW and IVF have different memory, tuning, and recall behavior.

## Why

The retrieval service delegates vector operations to backends. An in-memory scan is useful for small controlled examples; a production backend may use an approximate index depending on its configuration and query plan. ANN is not universally forced by this library.

## Risk

ANN can miss relevant candidates before reranking ever sees them. Metadata filters and small candidate pools can interact with index behavior, so recall must be measured under actual constraints.

## Trade-off

Higher search effort usually improves recall and costs latency or memory. Exact search may be sufficient for small corpora or useful as an offline oracle.

## Try This

Compare approximate results with exact results on the same authorized subset. Plot recall versus latency while varying backend search effort.

# Why are native lexical search and token-overlap fallback not equivalent?

## Answer

PostgreSQL full-text search provides language configuration, query parsing, and ranking facilities. The shared fallback tokenizes lowercase ASCII alphanumeric sequences and scores query-token overlap. It is a lightweight approximation, not BM25 and not equivalent multilingual search.

## Why

The scoring helper makes non-PostgreSQL backends usable in hybrid examples while capability declarations distinguish native and approximate lexical support. This preserves a common result shape without pretending the underlying ranking models are identical.

## Risk

Non-ASCII text and linguistic variation may behave poorly in the fallback. An evaluation that covers only English exact-word examples can miss this limitation.

## Trade-off

A portable fallback avoids another search service, while native full-text infrastructure generally offers richer lexical behavior. Choose according to corpus language and quality requirements.

## Try This

Tokenize an Arabic query and an English product code using the fallback. Inspect the actual tokens before interpreting any hybrid score.

# How does the reference design prevent SQL injection in dynamic queries?

## Answer

SQL values use bound parameters, while table and column names require separate identifier validation because SQL drivers cannot bind identifiers as ordinary values. the retrieval service validates dynamic names before interpolation into backend SQL.

## Why

The validation helper restricts identifiers to a simple allowlisted syntax. the PostgreSQL vector adapter applies validation when constructing operations and keeps values in parameter dictionaries. This is safer than escaping arbitrary user-provided SQL fragments.

## Risk

A valid identifier is not proof of authorization to access that table. Hosts must select trusted schema configuration and limit database permissions. Application transport validation also remains necessary.

## Trade-off

Strict names exclude qualified or unusual identifiers unless explicitly supported. That constraint simplifies safe SQL construction at the cost of some schema flexibility.

## Try This

Compare a malicious value, a malicious table name, and a syntactically valid but unauthorized table name. Explain which layer must stop each one.

# What does session injection buy, and when does atomicity fail?

## Answer

Session injection lets several operations join a transaction owned by the host or pipeline. When version mutations and vector writes truly use the same transactional database session, rollback can preserve the previous active state if a write fails.

## Why

The ingestion coordinator forwards the critical session into version storage and store upsert. Its guarantee depends on both adapters honoring that session. A remote vector service or in-memory store may not participate in the SQL transaction.

## Risk

Passing a session argument that an adapter ignores does not create cross-system atomicity. The sync path instead uses prepared generations and manifest visibility, with durable adapter obligations.

## Trade-off

Shared transactions simplify consistency within one database. Cross-service storage can scale independently but needs explicit visibility, retries, reconciliation, and failure recovery.

## Try This

Draw a rollback scenario for PostgreSQL-only storage and another for SQL versions plus a remote vector engine. Identify the write that cannot be rolled back in the second design.

# How do Qdrant, Chroma, FAISS, and in-memory adapters differ operationally?

## Answer

They expose a common retrieval surface but use different storage and execution models. In-memory state is process-local. FAISS is an indexing library whose surrounding metadata and persistence need attention. Service-backed engines introduce network and server configuration. Adapter support, not brand identity, determines available guarantees.

## Why

Each backend has its own implementation and optional dependency. The factory and capability layer let callers choose a backend while rejecting unsupported constraints instead of claiming complete interchangeability.

## Risk

Assuming identical durability, filter semantics, or transaction participation across these adapters can violate correctness. Inspect persistence and metadata behavior in the selected implementation and deployment.

## Trade-off

Lightweight local execution reduces setup; service-backed deployment supports different scale and operations needs. Portability often means accepting a common subset or explicitly branching on capabilities.

## Try This

Compare three public backend configurations. Record where vectors and metadata live, which constraints they enforce, and what survives a process restart.

# Why are strict error semantics important for storage operations?

## Answer

A failed query and a successful query with zero matches mean different things. Lenient APIs may log an error and return an empty list or zero count; that is convenient for some callers but dangerous when the host interprets emptiness as authoritative.

## Why

Retrieval supports strict mode and a typed retrieval error type. Mandatory capability and scope failures are designed to propagate rather than become silent fallbacks. Evidence assembly can represent backend failure distinctly when the host preserves that information.

## Risk

Forgetting strict mode can make an outage look like missing knowledge or an empty index. Health and deletion decisions should not infer success solely from an empty return value.

## Trade-off

Strict propagation requires explicit application error handling. Lenient fallback improves continuity only when the product can tolerate ambiguity and communicates it honestly.

## Try This

Make the backend raise on search and count. Compare strict and lenient behavior and design the corresponding UI states.

# How should deletion differ from physical garbage collection?

## Answer

Logical deletion removes permission or visibility immediately; physical cleanup later reservice requests index storage. Separating the two prevents asynchronous vector deletion from remaining an access-control dependency.

## Why

Sync manifests can tombstone documents, and a synchronous retrieval adapter validates status, generation, scope, and chunk membership before returning hits. Garbage collection removes retired or uncommitted vectors after visibility decisions.

## Risk

Calling the raw vector store bypasses manifest checks. A delayed physical deletion is safe only if every reader uses the required visibility boundary and source lookup also respects revocation.

## Trade-off

Manifest gating adds reads and coordination but permits conservative cleanup and safer recovery. Immediate physical deletion alone is simpler but can fail or lag.

## Try This

Leave a tombstoned document's vectors physically present. Verify that the supported sync retrieval path returns no evidence and explain why raw nearest-neighbor access must remain internal.

# What does a trustworthy backend capability contract look like?

## Answer

It states supported filter operators and features such as document fetch, deletion, scope enforcement, generation visibility, and transaction guarantees. Unsupported mandatory requirements produce an error before returning potentially unsafe results.

## Why

Store capability declarations validates both requested constraints and filter shapes. This makes backend selection a correctness decision rather than a best-effort call to methods that may silently ignore arguments.

## Risk

Declarations are assertions by adapter code. A falsely advertised capability is still a bug, and permissive host defaults can avoid requesting a guarantee that the product actually needs.

## Trade-off

Fail-closed behavior reduces surprising leakage but can reject configurations that previously appeared to work. That incompatibility is useful when the earlier behavior was unsafe or incomplete.

## Try This

Build an adapter that rejects range filters and transactions. Send requests requiring each feature and verify rejection occurs before any evidence is returned.

# How does an IVF index trade recall for speed, and how do lists and probes work in pgvector?

<!-- meta
domain: ai-rag
subdomain: vector-indexing
module: storage
concept: IVF recall and probes
difficulty: performance
misconception_target: An ANN index returns the same neighbours as exact search with only a small speed benefit
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Mechanism.** At build time the index runs clustering, typically k-means, to create `lists` partitions, each represented by a centroid. At query time it ranks centroids by distance to the query, selects the closest `probes` lists, and exhaustively searches vectors inside them. Cost drops from N distance computations to roughly `lists + N * probes / lists` under balanced lists.

**Recall loss at boundaries.** A query lying between clusters may have its true nearest neighbour in a neighbouring list. In the example, searching one list returns a point from cluster A, while the true nearest point belongs to cluster B. Probing two lists recovers it at the price of scanning 6 of 8 vectors rather than 3.

**pgvector specifics.** `CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);` builds the index; `SET ivfflat.probes = 10;` raises recall at query time. pgvector's guidance is to create the index after loading representative data, because centroids are computed from existing rows. A common starting heuristic is rows/1000 lists for up to a million rows and sqrt(rows) beyond, with probes around sqrt(lists), but these are starting points to tune with measured recall.

**IVF versus HNSW.** HNSW navigates a layered proximity graph and usually gives better speed-recall trade-offs at higher memory and build cost, and it does not need training data to build. IVF builds faster and uses less memory but depends on cluster quality, and cluster drift after many inserts can require a rebuild. Neither is universally better; benchmark on your vectors.

**Measure properly.** Compute exact top-K for a sample of queries (a sequential scan), then report ANN Recall@K against it together with p95 latency. Remember this recall measures agreement with exact nearest neighbours, not whether results answer the question, and re-measure with your real metadata filters, since filters can leave too few candidates in the probed lists.

## Spoken Summary

IVF, inverted file indexing, clusters vectors into lists around centroids. A query finds the nearest centroids and searches only those lists, controlled by the probes parameter. Fewer probes means fewer distance computations but a higher chance the true neighbour sits in an unsearched list near a boundary. Exact search is the ground truth for measuring recall. In pgvector I choose lists at build time, set ivfflat.probes at query time, build the index after loading data, and test filtered queries because filtering interacts badly with approximate indexes.

## Why

The example places points in three clusters, builds lists from fixed centroids, then compares exact search, one-probe search and two-probe search for a boundary query, also reporting how many vectors were scanned.

## Production Case

A catalog search with 5 million vectors builds IVF before data is fully loaded, so centroids reflect only early products. Recall falls after a seasonal import. Rebuilding after the import and raising probes restores recall at a measured latency increase.

## Risk

Undetected recall loss: results look plausible while the true best passage is never examined. Filtered queries and data drift make the problem worse.

## Trade-off

More probes raise recall and latency together. More lists speed up scanning per list but make boundary effects more frequent and require higher probes.

## Try This

Add a query near the A-B boundary and a query near a centroid, then compare recall for probes 1, 2 and 3 across many random queries.

## Execution Timeline

Load data -> cluster into lists -> build index -> query finds nearest centroids -> search probed lists -> return best -> measure recall against exact scan on sampled queries

## Complexity

Query cost about lists + N x probes / lists distance computations for balanced lists; build cost includes clustering over the dataset; memory is modest compared with graph indexes.

## Definitions

- **IVF**: Inverted File index: partition vectors into clusters and search only the closest clusters.
- **Probes**: Number of clusters examined per query.
- **ANN recall**: Fraction of the true exact nearest neighbours found by the approximate index.
- **Centroid**: Representative vector of a cluster, usually its mean.

## Alternatives

- HNSW for stronger speed-recall at higher memory
- Exact scan for small collections
- Quantization or partitioning combined with ANN for very large collections

## Pitfalls

- Building the index on a tiny or unrepresentative sample
- Never measuring recall against exact search
- Ignoring filtered-query behaviour
- Raising probes until latency fails without tracking recall

## Follow-ups

### Why keep an exact-search baseline at all?

It is the ground truth for ANN recall. Without it you cannot say whether a faster index silently dropped true neighbours, and you cannot tune probes or ef_search responsibly.

### What happens to IVF as data changes?

New vectors are assigned to existing centroids, which may no longer fit the distribution. Quality can degrade, so schedule rebuilds based on measured recall rather than elapsed time alone.

### How do filters affect IVF?

If a filter applies after probing, selective filters can leave few eligible rows in the searched lists. Raise probes, partition by the filter column, or choose an engine with filter-aware traversal, and benchmark with real tenant distributions.

## Example

> Explanation: IVF searches only the closest lists; probes trade recall for fewer distance computations.
> Output: verified

```python
"""IVF searches only the closest lists; probes trade recall for fewer distance computations."""
import math

POINTS = {
    "a1": (0.0, 0.0), "a2": (1.0, 1.0), "a3": (0.5, 2.0),
    "b1": (10.0, 0.0), "b2": (9.0, 1.0), "b3": (6.0, 0.4),
    "c1": (5.0, 10.0), "c2": (6.0, 9.0),
}
CENTROIDS = {"A": (0.5, 1.0), "B": (8.5, 0.5), "C": (5.5, 9.5)}


def assign():
    lists = {name: [] for name in CENTROIDS}
    for pid, p in POINTS.items():
        lists[min(CENTROIDS, key=lambda c: math.dist(p, CENTROIDS[c]))].append(pid)
    return lists


def search(query, lists, probes):
    chosen = sorted(CENTROIDS, key=lambda c: math.dist(query, CENTROIDS[c]))[:probes]
    candidates = [pid for c in chosen for pid in lists[c]]
    best = min(candidates, key=lambda pid: math.dist(query, POINTS[pid]))
    return best, len(candidates)


lists = assign()
query = (4.2, 0.3)
exact = min(POINTS, key=lambda pid: math.dist(query, POINTS[pid]))
one = search(query, lists, 1)
two = search(query, lists, 2)
assert exact == "b3" and one[0] != exact and two[0] == exact
print("exact", exact, "probes1", one, "probes2", two, "total", len(POINTS))
```

## Citations

- https://github.com/pgvector/pgvector
- https://arxiv.org/abs/1702.08734
- https://arxiv.org/abs/1603.09320

# What does an HNSW query’s speed depend on beyond the number of stored vectors?

<!-- meta
domain: ai-rag
subdomain: storage
module: storage
concept: What does an HNSW query’s speed depend on beyond the number of stored vectors?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A tenant filter leaves very few eligible records and the unfiltered ANN benchmark no longer predicts either recall or latency.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Graph construction parameters, search breadth, dimension, metric, memory layout, filter selectivity, updates and required recall all influence work. Approximate search is not a blanket worst-case logarithmic guarantee. Benchmark latency and recall together on realistic filtered queries and keep an exact or independently labeled baseline for diagnosis.

Concrete engineering case: A tenant filter leaves very few eligible records and the unfiltered ANN benchmark no longer predicts either recall or latency.

Boundary defense: No. It consumes work and can change tail latency and capacity. Evaluate the relevant trade-off under caller filters.

## Spoken Summary

Graph construction parameters, search breadth, dimension, metric, memory layout, filter selectivity, updates and required recall all influence work. Approximate search is not a blanket worst-case logarithmic guarantee. Benchmark latency and recall together on realistic filtered queries and keep an exact or independently labeled baseline for diagnosis.

## Why

Graph construction parameters, search breadth, dimension, metric, memory layout, filter selectivity, updates and required recall all influence work. Approximate search is not a blanket worst-case logarithmic guarantee. Benchmark latency and recall together on realistic filtered queries and keep an exact or independently labeled baseline for diagnosis.

## Production Case

A tenant filter leaves very few eligible records and the unfiltered ANN benchmark no longer predicts either recall or latency.

## Risk

A tenant filter leaves very few eligible records and the unfiltered ANN benchmark no longer predicts either recall or latency.

## Trade-off

No. It consumes work and can change tail latency and capacity. Evaluate the relevant trade-off under caller filters.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: storage**: Graph construction parameters, search breadth, dimension, metric, memory layout, filter selectivity, updates and required recall all influence work.

## Alternatives

- No. It consumes work and can change tail latency and capacity. Evaluate the relevant trade-off under caller filters.

## Pitfalls

- A tenant filter leaves very few eligible records and the unfiltered ANN benchmark no longer predicts either recall or latency.

## Follow-ups

### Can increasing search breadth be called a free accuracy improvement?

No. It consumes work and can change tail latency and capacity. Evaluate the relevant trade-off under caller filters.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A tenant filter leaves very few eligible records and the unfiltered ANN benchmark no longer predicts either recall or latency.",
  "required_decision": "Graph construction parameters, search breadth, dimension, metric, memory layout, filter selectivity, updates and required recall all influence work"
}
```

## Citations

- https://www.postgresql.org/docs/current/tutorial.html
- https://arxiv.org/abs/1603.09320

# How do you resume a huge upload safely after a disconnect or an expired upload URL?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: storage
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Persist an upload manifest.** Bind the upload identifier to the authenticated owner, intended object key, declared size, expiration policy and lifecycle state. Track acknowledged part numbers and integrity information. On resume, authenticate the user again and reconcile the server-side part listing with the client record. Refresh only the missing authorized operations; never accept an arbitrary bucket or key from the resume request.

**Separate transfer completion from ingestion completion.** Use states such as uploading, uploaded, validating, processing, ready, failed and canceled. A client claiming that all parts arrived is not enough to mark the document searchable. Complete the upload, inspect the resulting object and validate its size, checksum strategy and format. Multipart entity tags are not universally whole-file MD5 checksums; use the storage provider's documented integrity mechanism.

**Make completion and cancellation race-safe.** The application state transition must be conditional on the current upload version. Duplicate completion requests should return the same result. An object-finalization notification may be delivered more than once; deduplicate its ingestion job using object identity and version. A canceled upload must not become visible because a delayed worker finishes. Periodically reconcile abandoned sessions and incomplete multipart data.

**Design the learner-facing progress honestly.** Show bytes transferred separately from documents indexed. Offer resume for interrupted transfer, retry for failed processing and clear explanations for rejected formats. A progress bar at 100% uploaded should not imply that embeddings or search are ready.

## Why

A browser loses connectivity after part 800. Its old signed URLs expire overnight. The user resumes the same owned session, reconciles uploaded parts and requests new URLs for missing parts instead of starting an unrelated object.

## Worked Case

A browser loses connectivity after part 800. Its old signed URLs expire overnight. The user resumes the same owned session, reconciles uploaded parts and requests new URLs for missing parts instead of starting an unrelated object.

## Risk

A presigned URL is a bearer capability until it expires; avoid logging it or allowing it to select another tenant object.

## Trade-off

Fine-grained upload state improves recovery but needs reconciliation jobs and retention limits.

## Try This

Test duplicate completion, cancel-versus-complete races, expired URLs and a notification arriving after cancellation.

## Citations

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html

# Which metadata belongs on every retrieval chunk, and how do you evolve it without a full re-embedding?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: storage
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Design metadata around queries and lineage.** A useful contract can include tenant identifier, document identifier, immutable source version, chunk identifier, parent identifier, page or section coordinates, effective-time range, language, content type, ingestion time, extraction version and embedding model version. These fields answer different questions: ingestion time does not tell you when a policy applied.

**Separate trusted fields from inferred fields.** Tenant and access-control scope come from authenticated ownership and the permission service. An extracted product name or model-generated tag is uncertain content classification. Store its provenance and confidence if needed; do not grant access based on a tag predicted from document text. Use explicit types, timezone rules, null semantics and schema versions. An absent expiration date may mean open-ended validity only if the schema explicitly defines that meaning.

**Index the predicates you actually use.** Equality and range filters need appropriate scalar or payload indexes depending on the backend. Measure cardinality, selectivity, storage cost and update rate. Do not copy a huge access list into every chunk without considering membership churn and update amplification. An authorization service or scope indirection may be more maintainable, but its retrieval and recheck path must still be safe.

**Distinguish payload edits from representation changes.** Correcting a title or access scope may require a metadata update without recomputing the vector if that field was not embedded. If the title was prepended to embedding text, or the text/chunker/model changes, the vector is stale. During schema migration, dual-read compatible versions, backfill missing fields and deny records that cannot satisfy required authorization predicates.

## Why

A document has 20,000 chunks. Its department changes but its embedded body does not. Update the trusted scope metadata and invalidate authorization-sensitive caches; if department names were part of the embedding input, schedule a versioned re-embedding instead.

## Worked Case

A document has 20,000 chunks. Its department changes but its embedded body does not. Update the trusted scope metadata and invalidate authorization-sensitive caches; if department names were part of the embedding input, schedule a versioned re-embedding instead.

## Risk

Mixing created-at, ingested-at and effective-at produces confident answers based on the wrong historical policy.

## Trade-off

Denormalization speeds retrieval but amplifies metadata updates; indirection requires a dependable join or permission lookup.

## Try This

Design a schema for policies that change over time, then migrate a nullable field to a required field without exposing records with missing access scope.

## Citations

- https://qdrant.tech/documentation/search/filtering/
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html

# How do HNSW and inverted-file indexes trade build cost, search effort and recall?

<!-- meta
answer_format: conceptual
domain: ai-rag
subdomain: storage
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Hierarchical Navigable Small World indexes navigate a graph of vector neighborhoods; inverted-file indexes first select clusters and search their assigned vectors. Parameters trade memory, construction effort and query search breadth against approximate recall. Measure against exact search over the same eligible population and metric. Filtering and deletion can change the practical search behavior, so a benchmark without tenant constraints may not represent production. Track index generation and embedding compatibility rather than tuning parameters over a mixed representation space.

## Why

An approximate index can return ten candidates before a tenant filter removes nine. Increasing requested candidates may help, but the benchmark must measure the authorized result set and final recall, not raw global nearest neighbors.

## Worked Case

An approximate index can return ten candidates before a tenant filter removes nine. Increasing requested candidates may help, but the benchmark must measure the authorized result set and final recall, not raw global nearest neighbors.

## Risk

Low latency without a recall baseline can hide missing relevant results.

## Trade-off

Use exact search for small eligible sets when approximation adds little value.

## Try This

Benchmark recall and latency under the actual metadata filters at several search settings.

## Citations

- https://www.postgresql.org/docs/current/tutorial.html
- https://arxiv.org/abs/1603.09320
