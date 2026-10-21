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
