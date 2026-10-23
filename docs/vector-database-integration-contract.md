# Vector store integration learning module — issue #40

Introduction: vector databases make semantic similarity search practical, but
they do not automatically enforce authorization, version consistency or
deletion. Teach exact cosine first, then filtered approximate retrieval,
HNSW tuning, hybrid search and index migrations.

Run: python3 -B labs/vector_index_migration.py

This offline reference verifies dimension checking, owner eligibility before
ranking, revision filtering, tombstones and cutover completeness. It is not
a successful vendor connection.

Seven-engine practical adapter checklist:
- Qdrant: payload filters and named-vector collections (real server test pending).
- Chroma: persistent collection, metadata filters, deletion (pending).
- Pinecone: namespace, metadata filters and managed account (pending).
- Weaviate: collection predicate and client/server version (pending).
- FAISS: index/search plus external authoritative owner filtering (pending).
- pgvector: transactionally scoped SQL WHERE and index planner tests (pending).
- LanceDB: table snapshots, versioned embeddings and predicate (pending).

Each optional adapter needs pinned dependencies, actual server or cloud
access, negative owner/deletion tests, identical gold recall queries and
documented resources/cost/cleanup. Never label a mocked client as verified.

## Actual local SDK contract execution

Install `requirements-vector-engines.txt` in a fresh Python 3.12 environment:

```sh
python3.12 -m venv .venv-vector
.venv-vector/bin/python -m pip install -r requirements-vector-engines.txt
.venv-vector/bin/python labs/vector_engines.py --output vector-results.json
```

The same original five-record, two-dimensional vector corpus now runs through
actual Qdrant local, persistent Chroma, FAISS and LanceDB APIs. Positive checks
assert the independently specified eligible ID. Negative checks place a more
similar other-owner record, an obsolete embedding profile and a tombstoned
record ahead of the eligible result. Missing-owner reads return nothing; an
owner-A delete cannot remove owner B's record. Repeated upsert, profile change,
old-profile exclusion, repeated delete and post-delete query are executed.

FAISS is an index library: the wrapper selects the eligible owner/profile rows
before constructing its native exact index, rather than post-filtering a global
top-k. It does not claim native server ACLs. Qdrant's local SDK mode does not
exercise a distributed Qdrant server or HNSW graph. No adapter here provides an
HTTP authentication service or proves secure multi-tenant deployment by itself.
LanceDB and Chroma receive their actual prefilter predicates in their own APIs.

`docs/evidence/vector-engines.json` records observed SDK versions, raw build
and ten-query timings and the successful contract checks. Five vectors and ten
warm samples are not a representative p99, index-memory or ANN quality benchmark.
No embedding model is downloaded. Each profile uses a disposable local directory;
no existing database or production collection is touched.

Pinecone, Weaviate and PostgreSQL/pgvector service paths remain explicitly
unexecuted here. This increment replaces four fictional adapters with actual
SDK tests, while retaining the separate requirement for the remaining engines,
engine-specific HNSW/hybrid experiments and a complete migration assessment.

## Security correction — 23 October 2026

The published ChromaDB release is still 1.5.9. GitHub advisories
GHSA-f4j7-r4q5-qw2c and GHSA-36p7-vc44-83pf identify critical code injection;
GHSA-2wm9-hf6c-p5cr and GHSA-xph7-9rjv-w5fr identify tenant/RBAC flaws.
The advisory API reports no patched release. The optional requirements and runner
therefore remove Chroma entirely rather than waive dependency review. Explicit
programmatic requests for Chroma fail before any import; CLI choices omit it.

The earlier four-engine execution described above is historical evidence only.
The current runner and refreshed evidence execute **three** local SDKs: Qdrant,
FAISS and LanceDB. Chroma is blocked until an upstream fix can be verified and
retested. Pinecone, Weaviate and PostgreSQL/pgvector execution, representative
HNSW/hybrid measurements and a complete migration assessment also remain pending.
Issue #40 must stay open; removing an unsafe dependency does not waive its scope.

Advisories: https://github.com/advisories/GHSA-f4j7-r4q5-qw2c
https://github.com/advisories/GHSA-36p7-vc44-83pf
https://github.com/advisories/GHSA-2wm9-hf6c-p5cr
https://github.com/advisories/GHSA-xph7-9rjv-w5fr

## Actual isolated PostgreSQL/pgvector server path

`labs/vector_engines.py --engine pgvector --output pgvector-server.json` creates
its own temporary cluster using locally installed PostgreSQL binaries and the
matching vector extension. Set POSTGRES_BIN to the binary directory when needed.
On this run PostgreSQL 17 and pgvector 0.8.7 executed; exact versions, query samples
and scoped CRUD outcomes are in `docs/evidence/pgvector-server.json`. The runner
starts only its own loopback cluster on a temporary port, never accepts an existing
DSN, uses synthetic vectors, stops its server and removes the temporary directory.
It does not change any existing database. Local trust authentication is suitable
only for this disposable no-secret fixture, not a production authorization claim.

The native SQL query filters owner/profile/deletion before cosine ranking; a
parameterized owner predicate also protects deletion. Cases exercise repeated
upsert/delete, foreign-owner writes, profile migration and missing-owner reads.
This is exact search over five vectors, not an HNSW performance or production
RLS proof. PostgreSQL/pgvector is opt-in; the default three SDKs need no server.
Pinecone, Weaviate, the blocked Chroma path and broader assessed experiments
remain outstanding.
