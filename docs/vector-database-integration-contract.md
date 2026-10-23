# Vector store integration learning module — issue #40

Start with exact cosine, owner eligibility, source revision and deletion before
comparing approximate search. `python3 -B labs/vector_index_migration.py` is a
standard-library reference oracle for those rules and fail-closed index cutover.
Its assertions do not constitute vendor execution or ANN performance evidence.

## Actual SDK and SQL execution

Create a fresh Python 3.12 environment and install the pinned
`requirements-vector-engines.txt`. Run:

```sh
python3 -B labs/vector_engines.py --output vector-engines.json
python3 -B labs/vector_engines.py --engine pgvector --output pgvector-server.json
```

The default runs actual Qdrant local, FAISS and LanceDB APIs. The opt-in pgvector
path additionally needs installed PostgreSQL binaries and their matching vector
extension; set POSTGRES_BIN to the binary directory when necessary. Recorded
versions/hardware are authoritative for the executed run, rather than a claim
that any installed version has been tested.

Each adapter receives the same original five-record, two-dimensional corpus.
The expected eligible ID is fixed before execution. More-similar foreign-owner,
obsolete-profile and tombstoned vectors must not displace it. Tests cover a
missing owner, repeated upsert/delete, profile replacement, old-profile exclusion,
cross-owner deletion denial and preservation of the other owner's record.
`docs/evidence/vector-engines.json` and `docs/evidence/pgvector-server.json` record
actual SDK/server/extension versions, contract outcomes and raw query samples.
Five vectors and ten warm samples are not representative latency/recall results.

Qdrant uses local mode, not a distributed server or an HNSW graph benchmark.
FAISS builds its native exact index over eligible rows; it is not a native ACL
service. LanceDB receives a real prefilter predicate. PostgreSQL uses
parameterized owner/profile/deletion SQL predicates before cosine ranking and
an owner predicate on deletion. None proves remote authentication or production
row-level-security deployment.

## Isolated PostgreSQL lifecycle

The pgvector adapter creates its own temporary cluster, binds loopback on a
temporary port and accepts no existing DSN. It uses synthetic data only, stops
its owned server and deletes its temporary directory. It never changes an
existing database. Local trust authentication is only for this disposable,
no-secret fixture; it is not production identity isolation. The observed run
used PostgreSQL 17 with pgvector 0.8.7; the evidence gives the exact server build.

## Chroma security boundary — checked 23 October 2026

The current PyPI ChromaDB release is 1.5.9. GitHub advisories report unresolved
critical code injection and tenant/RBAC flaws; the advisory API lists no patched
release. Chroma is removed from the requirements and runner, CLI choices omit
it, and an explicit programmatic request fails before import. No dependency-risk
exception or vulnerable downgrade is used. A future fix needs advisory review,
a pinned release and fresh actual execution before enabling this path.

- https://github.com/advisories/GHSA-f4j7-r4q5-qw2c
- https://github.com/advisories/GHSA-36p7-vc44-83pf
- https://github.com/advisories/GHSA-2wm9-hf6c-p5cr
- https://github.com/advisories/GHSA-xph7-9rjv-w5fr

The earlier Chroma run is historical and is not counted as a supported current
adapter. `tests/check_vector_dependency_boundary.py` protects this exclusion.

## Remaining acceptance

Actual Pinecone and Weaviate paths, a safely patched Chroma path, engine-specific
filtered HNSW/hybrid comparisons and the complete reviewed syllabus/migration
assessment remain outstanding. Seven-engine acceptance is not waived by these
four working local paths. Keep issue #40 and this PR open until that evidence
and the final integrated checks pass. No model, existing collection, external
service credential or runtime course backend is needed for these local tests.

Primary mechanics: https://github.com/pgvector/pgvector
https://qdrant.tech/documentation/guides/optimize/
