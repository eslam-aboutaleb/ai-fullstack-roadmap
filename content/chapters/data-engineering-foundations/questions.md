<!-- chapter: data-engineering-foundations -->

# Why is schema compatibility a semantic contract rather than only a field-name check?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: data-engineering-foundations
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**A data pipeline turns source events into validated, queryable state.** Extract-transform-load (ETL) validates/transforms before loading the destination; extract-load-transform (ELT) first stores raw input and transforms inside the destination environment. Neither name guarantees quality or privacy. Decide which raw data may be retained, who can query it and how transformations are versioned and reproduced.

Define a data contract: identity, owner, schema version, event/source time, operation, revision and payload constraints. Validate at ingestion and at the authoritative write boundary. SQL types, NOT NULL, uniqueness, foreign keys and checks protect different invariants; an application validator alone can be bypassed by another producer. Parameterize values rather than constructing SQL from source text. Quarantine malformed items with bounded diagnostics and an explicit replay path.

Batch processes a bounded snapshot; streaming processes an ongoing sequence and needs checkpoint, ordering and late-data policy. Event time describes when the business event happened; processing time describes when the system handled it. A watermark is a progress estimate, not proof no older event can arrive. Backpressure bounds in-flight work when the sink cannot keep up; unlimited buffering only moves the failure into memory.

**Reason about compatibility.** Adding a nullable column can be compatible for named-column readers yet break positional SELECT-star consumers or an old writer with a fixed insert list. Use an expand/contract migration: introduce compatible fields, deploy readers/writers, backfill under versioned rules, verify then retire old fields. `data_contract_pipeline.py` exercises schema and transformation behavior; `data_rollout_contract.py` adds transactional CDC failure paths. A passing synthetic pipeline establishes its declared fixtures, not arbitrary production schemas. Save input/profile hashes, output rows, rejected records and reconstruction instructions so a learner can independently inspect lineage and quality.

## Why

An old consumer unpacks SELECT-star into three values after a fourth nullable column is added. The database change is legal but the consumer contract breaks; compatibility must be evaluated across actual readers and writers.

## Worked Case

An old consumer unpacks SELECT-star into three values after a fourth nullable column is added. The database change is legal but the consumer contract breaks; compatibility must be evaluated across actual readers and writers.

## Risk

Permissive parsing can silently coerce invalid timestamps or identifiers and corrupt downstream joins. Retaining raw data without purpose/retention controls can also violate privacy expectations.

## Trade-off

ELT preserves flexible raw evidence but expands access and storage obligations. ETL can minimize sensitive raw retention while making transformation recovery dependent on source availability.

## Try This

Run data_contract_pipeline.py and data_rollout_contract.py. Design an expand/contract change with an old reader and writer, then show a negative compatibility case and a replayable quarantine decision.

## Follow-ups

### Can a watermark justify deleting all older raw events?

Not by itself. It describes processing progress under assumptions, not a retention authorization or guarantee of no late corrections. Apply explicit correction, retention and deletion policies with reconstructable lineage.

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://www.postgresql.org/docs/current/ddl-constraints.html

# How do ETL, ELT and incremental updates change where failures are repaired?

<!-- meta
domain: data-engineering
subdomain: data-engineering-foundations
module: data-engineering-foundations
concept: How do ETL, ELT and incremental updates change where failures are repaired?
difficulty: interview
misconception_target: Missing the stated transformation placement boundary: A transformation bug has affected a month of projections. Retained versioned raw inputs allow a controlled rebuild, but deletion authority must still be applied.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

ETL transforms before loading the destination, while ELT loads a retained representation before downstream transformation. Incremental processing changes only new or modified source state under a cursor or change contract. Choose from data volume, governance, latency and rebuild requirements; the acronym does not supply deduplication or correctness guarantees.

Engineering case: A transformation bug has affected a month of projections. Retained versioned raw inputs allow a controlled rebuild, but deletion authority must still be applied.

Reasoning under a changed assumption: No. Apply access, retention and deletion policy. A convenient rebuild source can become an unauthorized long-term copy of sensitive data.

## Spoken Summary

ETL transforms before loading the destination, while ELT loads a retained representation before downstream transformation. Incremental processing changes only new or modified source state under a cursor or change contract. Choose from data volume, governance, latency and rebuild requirements; the acronym does not supply deduplication or correctness guarantees.

## Why

ETL transforms before loading the destination, while ELT loads a retained representation before downstream transformation. Incremental processing changes only new or modified source state under a cursor or change contract. Choose from data volume, governance, latency and rebuild requirements; the acronym does not supply deduplication or correctness guarantees.

## Production Case

A transformation bug has affected a month of projections. Retained versioned raw inputs allow a controlled rebuild, but deletion authority must still be applied.

## Risk

A transformation bug has affected a month of projections. Retained versioned raw inputs allow a controlled rebuild, but deletion authority must still be applied.

## Trade-off

No. Apply access, retention and deletion policy. A convenient rebuild source can become an unauthorized long-term copy of sensitive data.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Transformation placement**: ETL transforms before loading the destination, while ELT loads a retained representation before downstream transformation.

## Alternatives

- No. Apply access, retention and deletion policy. A convenient rebuild source can become an unauthorized long-term copy of sensitive data.

## Pitfalls

- A transformation bug has affected a month of projections. Retained versioned raw inputs allow a controlled rebuild, but deletion authority must still be applied.

## Follow-ups

### Is retaining every raw record always appropriate?

No. Apply access, retention and deletion policy. A convenient rebuild source can become an unauthorized long-term copy of sensitive data.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A transformation bug has affected a month of projections. Retained versioned raw inputs allow a controlled rebuild, but deletion authority must still be applied.",
  "decision": "ETL transforms before loading the destination, while ELT loads a retained representation before downstream transformation"
}
```

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# Why must a CDC checkpoint and destination state have a recovery contract?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: data-engineering-foundations
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Change data capture (CDC) carries source mutations to a derived view.** The source event identity, source position and business revision are different concepts. A retry repeats the same event; a correction is a new event that may update a prior business fact. Store enough lineage to distinguish them and preserve owner scope in both progress and document keys.

Apply destination mutation, deduplication record and checkpoint in one transaction when they share a database. If the process crashes after commit but before broker acknowledgment, replay should recognize the exact same event without applying it again. Compare a canonical digest of all material fields: accepting the same operation/offset with changed payload hides corruption. A broker's delivery guarantee cannot make an unrelated HTTP effect atomic with a database commit.

In `data_rollout_contract.py`, owner A and B can use the same document ID without sharing state. A gap or out-of-order sequence is rejected, not skipped. A tombstone excludes a deleted document and blocks an unapproved stale restoration. The checker deliberately aborts checkpoint insertion and verifies that neither the document nor consumed-event row remains. This tests transaction behavior rather than checking only a final checkpoint value.

Lineage connects source revision, transformation profile, derived rows/chunks and consumer output. During an index rebuild, snapshot the source, catch up changes, reconcile tombstones and validate quality before switching readers. A restored backup can contain records deleted after the backup; reapply authoritative deletion intent before serving traffic. Define freshness, null/duplicate rates, schema failures and owner leakage as separate quality signals. A count match alone can conceal swapped owners or incorrect values. Keep recovery evidence with exact input/output manifests and a rubric that requires both normal results and fault behavior.

## Why

A consumer commits a projection and crashes before acknowledgment. Exact replay must do no new work; a replay with the same offset but changed payload must fail rather than being silently treated as the original event.

## Worked Case

A consumer commits a projection and crashes before acknowledgment. Exact replay must do no new work; a replay with the same offset but changed payload must fail rather than being silently treated as the original event.

## Risk

Advancing the checkpoint before durable destination state loses data. Restoring an old snapshot without reapplying deletion intent can resurrect confidential records.

## Trade-off

Atomic local checkpoints simplify recovery but constrain storage design. Cross-system sinks require receiver idempotency or reconciliation, with the uncertainty explicitly documented.

## Try This

Run data_rollout_contract.py. Inspect the changed-payload replay and injected checkpoint failure, then explain why each catches a bug that an ordinary duplicate-event test misses.

## Follow-ups

### What if an old database has deduplication keys but no payload digests?

Do not infer equality from the key alone. Preserve history, reject unverifiable replay and reconcile against authoritative source evidence or rebuild under a controlled migration policy.

## Citations

- https://www.sqlite.org/lang_transaction.html
- https://kafka.apache.org/documentation/#semantics

# How do event time, watermarks and accumulating panes affect a dashboard total?

<!-- meta
domain: data-engineering
subdomain: data-engineering-foundations
module: data-engineering-foundations
concept: How do event time, watermarks and accumulating panes affect a dashboard total?
difficulty: interview
misconception_target: Missing the stated accumulating pane boundary: An on-time pane totals five and a late correction totals twelve. Adding them produces seventeen although twelve already includes the earlier five.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Event time describes when an event belongs logically, while watermarks and lateness policy govern when windows may be considered complete or corrected. An accumulating pane already contains earlier accepted values. A destination should upsert the authoritative window aggregate or use a deliberately different contribution contract, not blindly add cumulative results.

Engineering case: An on-time pane totals five and a late correction totals twelve. Adding them produces seventeen although twelve already includes the earlier five.

Reasoning under a changed assumption: No. It establishes the configured processing policy. Decide whether to discard, quarantine or backfill and how to communicate later corrections.

## Spoken Summary

Event time describes when an event belongs logically, while watermarks and lateness policy govern when windows may be considered complete or corrected. An accumulating pane already contains earlier accepted values. A destination should upsert the authoritative window aggregate or use a deliberately different contribution contract, not blindly add cumulative results.

## Why

Event time describes when an event belongs logically, while watermarks and lateness policy govern when windows may be considered complete or corrected. An accumulating pane already contains earlier accepted values. A destination should upsert the authoritative window aggregate or use a deliberately different contribution contract, not blindly add cumulative results.

## Production Case

An on-time pane totals five and a late correction totals twelve. Adding them produces seventeen although twelve already includes the earlier five.

## Risk

An on-time pane totals five and a late correction totals twelve. Adding them produces seventeen although twelve already includes the earlier five.

## Trade-off

No. It establishes the configured processing policy. Decide whether to discard, quarantine or backfill and how to communicate later corrections.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Accumulating pane**: Event time describes when an event belongs logically, while watermarks and lateness policy govern when windows may be considered complete or corrected.

## Alternatives

- No. It establishes the configured processing policy. Decide whether to discard, quarantine or backfill and how to communicate later corrections.

## Pitfalls

- An on-time pane totals five and a late correction totals twelve. Adding them produces seventeen although twelve already includes the earlier five.

## Follow-ups

### Does an expired lateness window prove an event never existed?

No. It establishes the configured processing policy. Decide whether to discard, quarantine or backfill and how to communicate later corrections.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "An on-time pane totals five and a late correction totals twelve. Adding them produces seventeen although twelve already includes the earlier five.",
  "decision": "Event time describes when an event belongs logically, while watermarks and lateness policy govern when windows may be considered complete or corrected"
}
```

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How do lineage and immutable manifests make a derived index rebuild auditable?

<!-- meta
domain: data-engineering
subdomain: data-engineering-foundations
module: data-engineering-foundations
concept: How do lineage and immutable manifests make a derived index rebuild auditable?
difficulty: interview
misconception_target: Missing the stated artifact lineage boundary: Two indexes built from different source revisions share the same label. A retrieval regression cannot be traced to either data or code.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Record source revisions, transformation and schema versions, embedding/model identity where applicable, and destination generation. A rebuild should identify exactly which source set it used and allow safe promotion or rollback. A mutable path called latest is insufficient evidence of input identity.

Engineering case: Two indexes built from different source revisions share the same label. A retrieval regression cannot be traced to either data or code.

Reasoning under a changed assumption: Only under a valid retention and access policy. Reproducibility requirements do not override deletion authority or justify an undeclared data store.

## Spoken Summary

Record source revisions, transformation and schema versions, embedding/model identity where applicable, and destination generation. A rebuild should identify exactly which source set it used and allow safe promotion or rollback. A mutable path called latest is insufficient evidence of input identity.

## Why

Record source revisions, transformation and schema versions, embedding/model identity where applicable, and destination generation. A rebuild should identify exactly which source set it used and allow safe promotion or rollback. A mutable path called latest is insufficient evidence of input identity.

## Production Case

Two indexes built from different source revisions share the same label. A retrieval regression cannot be traced to either data or code.

## Risk

Two indexes built from different source revisions share the same label. A retrieval regression cannot be traced to either data or code.

## Trade-off

Only under a valid retention and access policy. Reproducibility requirements do not override deletion authority or justify an undeclared data store.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Artifact lineage**: Record source revisions, transformation and schema versions, embedding/model identity where applicable, and destination generation.

## Alternatives

- Only under a valid retention and access policy. Reproducibility requirements do not override deletion authority or justify an undeclared data store.

## Pitfalls

- Two indexes built from different source revisions share the same label. A retrieval regression cannot be traced to either data or code.

## Follow-ups

### Can you reproduce a deleted source by keeping a private shadow copy?

Only under a valid retention and access policy. Reproducibility requirements do not override deletion authority or justify an undeclared data store.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "Two indexes built from different source revisions share the same label. A retrieval regression cannot be traced to either data or code.",
  "decision": "Record source revisions, transformation and schema versions, embedding/model identity where applicable, and destination generation"
}
```

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How should data-quality quarantine avoid silently losing or exposing records?

<!-- meta
domain: data-engineering
subdomain: data-engineering-foundations
module: data-engineering-foundations
concept: How should data-quality quarantine avoid silently losing or exposing records?
difficulty: interview
misconception_target: Missing the stated quarantine contract boundary: A new event schema is quarantined for every record while the pipeline continues advancing offsets. Throughput looks normal but the served projection becomes stale.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Declare which violations stop processing and which are quarantined while progress continues. Retain safe reason codes, source identity and repair provenance without copying sensitive bodies into unrestricted logs. Track quarantine counts and age so the system cannot appear healthy while excluding a growing slice of source data.

Engineering case: A new event schema is quarantined for every record while the pipeline continues advancing offsets. Throughput looks normal but the served projection becomes stale.

Reasoning under a changed assumption: No. Preserve immutable source identity or use an explicit repair/reprocessing contract. Changed content under a reused identity must be detected.

## Spoken Summary

Declare which violations stop processing and which are quarantined while progress continues. Retain safe reason codes, source identity and repair provenance without copying sensitive bodies into unrestricted logs. Track quarantine counts and age so the system cannot appear healthy while excluding a growing slice of source data.

## Why

Declare which violations stop processing and which are quarantined while progress continues. Retain safe reason codes, source identity and repair provenance without copying sensitive bodies into unrestricted logs. Track quarantine counts and age so the system cannot appear healthy while excluding a growing slice of source data.

## Production Case

A new event schema is quarantined for every record while the pipeline continues advancing offsets. Throughput looks normal but the served projection becomes stale.

## Risk

A new event schema is quarantined for every record while the pipeline continues advancing offsets. Throughput looks normal but the served projection becomes stale.

## Trade-off

No. Preserve immutable source identity or use an explicit repair/reprocessing contract. Changed content under a reused identity must be detected.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Quarantine contract**: Declare which violations stop processing and which are quarantined while progress continues.

## Alternatives

- No. Preserve immutable source identity or use an explicit repair/reprocessing contract. Changed content under a reused identity must be detected.

## Pitfalls

- A new event schema is quarantined for every record while the pipeline continues advancing offsets. Throughput looks normal but the served projection becomes stale.

## Follow-ups

### Should an operator simply overwrite the old event under the same identity?

No. Preserve immutable source identity or use an explicit repair/reprocessing contract. Changed content under a reused identity must be detected.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A new event schema is quarantined for every record while the pipeline continues advancing offsets. Throughput looks normal but the served projection becomes stale.",
  "decision": "Declare which violations stop processing and which are quarantined while progress continues"
}
```

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# Why can a restore or backfill resurrect data deleted after its snapshot?

<!-- meta
domain: data-engineering
subdomain: data-engineering-foundations
module: data-engineering-foundations
concept: Why can a restore or backfill resurrect data deleted after its snapshot?
difficulty: interview
misconception_target: Missing the stated deletion authority boundary: A restored database passes integrity checks but serves a customer document that was deleted after the backup.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A snapshot represents an older state and may contain a record whose newer deletion is authoritative. Preserve deletion intent independently and apply it before a restored or rebuilt projection becomes visible. Include caches, indexes, replicas and retained backups in the policy rather than checking only one table.

Engineering case: A restored database passes integrity checks but serves a customer document that was deleted after the backup.

Reasoning under a changed assumption: No. It proves the snapshot bytes match the recorded artifact. It does not establish current visibility authority or application-level recovery correctness.

## Spoken Summary

A snapshot represents an older state and may contain a record whose newer deletion is authoritative. Preserve deletion intent independently and apply it before a restored or rebuilt projection becomes visible. Include caches, indexes, replicas and retained backups in the policy rather than checking only one table.

## Why

A snapshot represents an older state and may contain a record whose newer deletion is authoritative. Preserve deletion intent independently and apply it before a restored or rebuilt projection becomes visible. Include caches, indexes, replicas and retained backups in the policy rather than checking only one table.

## Production Case

A restored database passes integrity checks but serves a customer document that was deleted after the backup.

## Risk

A restored database passes integrity checks but serves a customer document that was deleted after the backup.

## Trade-off

No. It proves the snapshot bytes match the recorded artifact. It does not establish current visibility authority or application-level recovery correctness.

## Try This

Construct the stated case, record the expected and actual outcome, then change one assumption and defend the result.

## Execution Timeline

State the input and invariant → trace the mechanism → reproduce the stated case → evaluate the changed assumption

## Complexity

Cost must be measured under the stated input size, representation and resource limits. The tiny reasoning fixture does not establish production capacity.

## Definitions

- **Deletion authority**: A snapshot represents an older state and may contain a record whose newer deletion is authoritative.

## Alternatives

- No. It proves the snapshot bytes match the recorded artifact. It does not establish current visibility authority or application-level recovery correctness.

## Pitfalls

- A restored database passes integrity checks but serves a customer document that was deleted after the backup.

## Follow-ups

### Does a valid backup digest prevent this?

No. It proves the snapshot bytes match the recorded artifact. It does not establish current visibility authority or application-level recovery correctness.

## Example

> Explanation: A reasoning fixture, not a simulated measurement or an implementation. Compare it with the chapter’s executable reference.
> Output: No runtime result claimed; inspect the linked executable example and reproduce the case.

```python
{
  "case": "A restored database passes integrity checks but serves a customer document that was deleted after the backup.",
  "decision": "A snapshot represents an older state and may contain a record whose newer deletion is authoritative"
}
```

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# What is the architectural difference between Row-Oriented and Column-Oriented database engines, and why are columnar formats like Parquet 100x faster for analytics?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Row-oriented and column-oriented database engines organize on-disk byte layouts to optimize opposing query workloads: single-record transactions versus aggregate analytics.** In traditional row-oriented OLTP databases (such as PostgreSQL or MySQL), all fields belonging to a single row are stored contiguously on fixed-size disk blocks (e.g., 8KB pages): `[Row1_colA, Row1_colB, Row1_colC], [Row2_colA, Row2_colB, Row2_colC]`. This layout is optimal for transactional workloads where queries read or mutate individual entities by primary key (`SELECT * FROM users WHERE id = 42`), because the entire row is retrieved in a single disk read.\n\n**The I/O bottleneck in analytical aggregations.** Consider an analytical query computing average transaction value across 100,000,000 records: `SELECT AVG(amount) FROM transactions`. In a row-oriented database, the storage engine must load every single 8KB disk page into RAM, reading billions of bytes of unneeded customer names, addresses, and timestamps simply to extract the 8-byte `amount` float from each row, saturating disk I/O and memory bandwidth.\n\n**Columnar storage, compression, and vectorized SIMD execution.** Column-oriented engines (ClickHouse, Snowflake, DuckDB) and storage formats (Apache Parquet) store all values for a given column contiguously: `[Row1_amount, Row2_amount, ...

RowN_amount]`. For analytical aggregates, the engine reads *only* the specific column queried, slashing disk I/O by over 90%. Furthermore, because contiguous data in a column shares the identical data type, columnar formats achieve extraordinary compression ratios (using run-length encoding, dictionary encoding, and delta encoding) and enable modern CPU vectorized execution (SIMD instructions evaluating millions of rows per CPU cycle).

## Why

A monthly revenue query takes 14 minutes in PostgreSQL because the database reads 45GB of row data from disk to access one column. The identical query in Parquet / ClickHouse reads only 180MB of compressed column data, completing in 220ms.

## Worked Case

A monthly revenue query takes 14 minutes in PostgreSQL because the database reads 45GB of row data from disk to access one column. The identical query in Parquet / ClickHouse reads only 180MB of compressed column data, completing in 220ms.

## Risk

Using columnar formats for high-velocity single-row transactional writes or updates causes massive write amplification and continuous file fragmentation.

## Trade-off

Columnar engines deliver 100x faster analytical aggregates and 5x better compression, but are inefficient for single-row point lookups and real-time updates.

## Try This

Save a 1,000,000-row DataFrame as both CSV/SQLite and Parquet. Compare file sizes and benchmark `SELECT AVG(col)` query runtimes on both formats.

## Follow-ups

### Why is Parquet an immutable file format?

Parquet files are written in immutable column chunks with embedded metadata footers; updating a single row requires rewriting the entire file, which is why updates are handled via append-and-merge compaction.

## Citations

- https://parquet.apache.org/docs/overview/
- https://clickhouse.com/docs/en/development/architecture

# How do Log-Structured Merge Trees in NoSQL engines compare with B-Trees in relational databases for write-heavy workloads?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Log-Structured Merge Trees (LSM-Trees) and B-Trees represent two distinct storage engine architectures optimized for opposing I/O profiles: append-only ingestion versus in-place point reads.** Traditional relational databases (PostgreSQL, MySQL InnoDB) rely on B-Tree variants. B-Trees perform in-place updates: when a record is modified, the engine navigates the tree and overwrites the exact disk page hosting that record.

Under high-concurrency write workloads, updating B-Tree pages scattered across gigabytes of storage causes massive random disk I/O, write amplification, and page lock contention, degrading write throughput.\n\n**The LSM-Tree sequential append architecture.** Engines like Apache Cassandra, RocksDB, and ScyllaDB replace in-place page mutation with append-only LSM-Trees: (1) Ingestion: incoming writes are sequentially appended to an on-disk Write-Ahead Log (WAL) for durability and simultaneously inserted into an in-memory sorted data structure called the Memtable (typically a SkipList); (2) Flushing: when the Memtable reaches capacity (e.g. 64MB), it is flushed to disk as an immutable Sorted String Table (SSTable) using pure sequential I/O, completely avoiding random disk writes; and (3) Compaction: background workers merge multiple SSTables, reconciling duplicate keys and purging deleted records (tombstones).\n\n**The read penalty and Bloom filters.** Because a key may reside in any of several SSTables on disk, reads in LSM-trees are more expensive than B-Trees. To prevent reading every SSTable from disk, LSM-trees maintain in-memory Bloom filters for each SSTable: a probabilistic data structure that can instantly determine with zero false negatives whether a key is definitely absent from an SSTable.

## Why

An IoT logging platform receives 100,000 sensor writes per second. A PostgreSQL B-Tree saturates disk IOPS due to random page updates. Cassandra with LSM-Trees handles the writes effortlessly via sequential WAL appends and Memtable flushes.

## Worked Case

An IoT logging platform receives 100,000 sensor writes per second. A PostgreSQL B-Tree saturates disk IOPS due to random page updates. Cassandra with LSM-Trees handles the writes effortlessly via sequential WAL appends and Memtable flushes.

## Risk

If write volume outpaces background compaction, SSTables accumulate on disk, causing catastrophic read latency degradation (read amplification) and space exhaustion.

## Trade-off

LSM-Trees provide unmatched sequential write throughput at the cost of higher read latency, periodic compaction I/O spikes, and complex tombstone management.

## Try This

Write a basic in-memory Memtable using a Python dictionary. Flush it to sorted text files once it reaches 100 items, and implement a merge-compaction function to combine two sorted files.

## Follow-ups

### What is a tombstone in an LSM-tree?

Because SSTables are immutable, deleting a key cannot erase on-disk bytes; instead, a special marker called a tombstone is written, which purges the key during subsequent compaction cycles.

## Citations

- https://github.com/facebook/rocksdb/wiki/RocksDB-Overview
- https://cassandra.apache.org/doc/latest/cassandra/architecture/storage_engine.html

# How does Query-Driven Data Modeling work in Wide-Column stores like Apache Cassandra, and why is relational normalization forbidden?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Wide-column distributed databases like Apache Cassandra mandate Query-Driven Data Modeling: designing database tables strictly around application read queries rather than entity relationships.** In relational database design, developers normalize data into logical entities (Users, Products, Orders) and rely on SQL JOINs at query time to satisfy arbitrary access patterns. In Cassandra, data is partitioned and distributed across hundreds of cluster nodes; distributed cross-node JOINs, subqueries, and table locks are physically impossible because they would require catastrophic network-wide synchronization.\n\n**Partition Keys, Clustering Columns, and Data Locality.** Every Cassandra table definition must be engineered around a specific query: `CREATE TABLE orders_by_user (user_id UUID, order_id UUID, order_date TIMESTAMP, total_amount DECIMAL, PRIMARY KEY (user_id, order_date)) WITH CLUSTERING ORDER BY (order_date DESC)`. The PRIMARY KEY consists of two distinct components: (1) The Partition Key (`user_id`): passed through a consistent hashing function (Murmur3Partitioner) to determine the exact cluster nodes that store the data; and (2) The Clustering Column (`order_date`): dictates the physical sorted order of rows stored on disk within that partition, allowing fast range queries for a given user.\n\n**Intentional data duplication by design.** If an application needs to query orders by `user_id` AND query orders by `order_id`, normalizing data into one table is fatal.

The application must create two separate tables (`orders_by_user` and `orders_by_id`) and write to both. Primary modeling anti-patterns include: creating hot partitions (e.g. using a low-cardinality status string as a partition key) and allowing partitions to exceed 100MB, which causes JVM garbage collection pauses and node instability.

## Why

A developer models Cassandra like PostgreSQL, putting all orders in one table with order_id as the primary key. When the UI asks for 'all orders for user X', the query executes a full-cluster scan across all 50 nodes, timing out and taking down cluster nodes.

## Worked Case

A developer models Cassandra like PostgreSQL, putting all orders in one table with order_id as the primary key. When the UI asks for 'all orders for user X', the query executes a full-cluster scan across all 50 nodes, timing out and taking down cluster nodes.

## Risk

Allowing a single partition to grow beyond 100MB or accumulating over 100,000 cells causes severe Cassandra read timeouts and node crashes.

## Trade-off

Query-driven modeling delivers predictable, sub-10ms reads at petabyte scale, at the cost of duplicate data storage and application-managed multi-table writes.

## Try This

Design a Cassandra schema for a messaging application supporting two queries: 'Get recent messages in a channel' and 'Get a message by its message_id'. Create two dedicated tables with distinct partition keys.

## Follow-ups

### Can Cassandra materialize views automatically?

Cassandra supports Materialized Views, but in production they are often avoided due to subtle replication lag and hidden cluster write overhead, favoring application-level dual writes.

## Citations

- https://cassandra.apache.org/doc/latest/cassandra/data_modeling/intro.html
- https://www.datastax.com/learn/data-modeling-by-example

# What is the CAP Theorem and PACELC Theorem, and how do distributed databases navigate the trade-off between Consistency, Latency, and Partition Tolerance?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**The CAP and PACELC theorems formalize the fundamental physical constraints governing distributed state across networked machines.** The CAP Theorem (Brewer) states that a distributed data store can guarantee at most two of three properties simultaneously: Consistency (C: every read receives the most recent write or an error), Availability (A: every non-failing node returns a non-error response, without guaranteeing it is the most recent write), and Partition Tolerance (P: the system continues to operate despite arbitrary network drops or communication delays between nodes).\n\n**Why network partitions make CP vs AP mandatory.** In real-world physical networks, network Partitions (P) are unavoidable due to fiber cuts, switch failures, and cloud routing glitches. Therefore, distributed architectures cannot choose 'CA'; they must choose how to behave when a partition occurs: (1) CP systems (e.g., Google Spanner, CockroachDB, etcd, MongoDB with majority write): prioritize strict Consistency. When a partition disconnects minority nodes, the minority refuses reads and writes, ensuring no client reads stale data or causes split-brain state; (2) AP systems (e.g., Apache Cassandra, DynamoDB, Couchbase): prioritize Availability.

Nodes on both sides of the network split continue accepting reads and writes, sacrificing immediate consistency in favor of eventual consistency and zero downtime.\n\n**The PACELC Theorem (Daniel Abadi).** The CAP theorem only describes behavior during rare partition events. The PACELC theorem expands this to normal operating conditions: **If there is a Partition (P)**, trade Availability (A) vs Consistency (C); **Else (E)**, trade Latency (L) vs Consistency (C). For example, DynamoDB and Cassandra are PA/EL (Availability during partitions; Low Latency normally via eventual consistency). Spanner and CockroachDB are PC/EC (Consistency during partitions; Consistency normally via Raft/Paxos consensus rounds, accepting higher network latency).

## Why

A cloud region experiences a network partition. An AP system (Cassandra) allows users in both regions to book hotel rooms, causing double-bookings that require manual reconciliation. A CP system (Spanner) locks the minority region until the partition heals, preventing double-bookings.

## Worked Case

A cloud region experiences a network partition. An AP system (Cassandra) allows users in both regions to book hotel rooms, causing double-bookings that require manual reconciliation. A CP system (Spanner) locks the minority region until the partition heals, preventing double-bookings.

## Risk

Assuming an AP database provides transactional read-your-writes guarantees leads to phantom reads, stale inventory displays, and state corruption.

## Trade-off

CP databases guarantee zero data divergence at the cost of higher latency and request rejections during network partitions; AP databases guarantee high availability at the cost of eventual consistency anomalies.

## Try This

Map four databases (PostgreSQL, Cassandra, CockroachDB, Redis) onto the PACELC taxonomy matrix and justify the placement of each based on their consensus protocols.

## Follow-ups

### What is the difference between linearizability and serializability in distributed systems?

Serializability is a multi-operation transactional property guaranteeing transactions appear to execute in some serial order; linearizability is a single-operation real-time property guaranteeing any read reflects the latest write in wall-clock time.

## Citations

- https://en.wikipedia.org/wiki/PACELC_theorem
- https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf

# How do Replication Lag and Read-Your-Writes consistency issues manifest in read-replica database architectures, and how do applications mitigate them?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Replication lag in distributed read-replica topologies breaks causal consistency, causing users to observe their own committed modifications vanish upon page refresh.** To scale read throughput, production relational architectures deploy a single primary database (accepting all INSERT, UPDATE, and DELETE mutations) paired with multiple asynchronous read replicas.

The primary streams its Write-Ahead Log (WAL) to replicas over the network, where background receiver processes replay WAL records to update local tables.\n\n**The Replication Lag illusion.** Because replication is asynchronous to prevent slowing down primary write commits, replicas lag behind the primary by milliseconds to seconds (or minutes during network congestion or heavy batch updates). A classic user experience failure occurs: (1) A user updates their profile address on the website; (2) The web application writes to the primary database, commits the transaction, and returns HTTP 200; (3) The browser immediately navigates or refreshes, issuing a GET request; (4) The load balancer routes the read request to a read replica that is 400ms behind; (5) The replica returns the user's old address; and (6) The user assumes their update failed, repeatedly re-submitting the form or contacting customer support.\n\n**Architectural mitigations for Read-Your-Writes consistency.** Production web applications eliminate replication lag anomalies through three engineering patterns: (1) Session Pinning with Cooldown Timers: after a user performs a write mutation, the application sets a short-lived cookie or Redis flag pinning all subsequent read requests from that specific user to the *primary database* for a 5-second cooldown window; (2) Monotonic Log Sequence Number (LSN) tracking: the primary returns its commit LSN to the client; the client passes this token on reads, and the proxy routes the read to a replica only if `replica_last_replay_lsn >= client_commit_lsn`; and (3) Explicit Primary routing for sensitive workflows (checkout, authentication).

## Why

A user resets their password. The write commits to the primary. The user immediately attempts to log in. The login authentication query hits a replica experiencing 800ms of lag. The replica compares against the old password hash, rejecting the valid login.

## Worked Case

A user resets their password. The write commits to the primary. The user immediately attempts to log in. The login authentication query hits a replica experiencing 800ms of lag. The replica compares against the old password hash, rejecting the valid login.

## Risk

Routing authentication or billing reads to asynchronous replicas without LSN validation allows stale credentials and duplicate payments.

## Trade-off

Pinning users to the primary database after writes guarantees immediate consistency, at the cost of sending extra read load to the primary instance during write-heavy bursts.

## Try This

Simulate replication lag in PostgreSQL by configuring `recovery_min_apply_delay = '2s'` on a replica. Write a row to the primary and immediately query the replica to observe the lag window.

## Follow-ups

### Can synchronous replication eliminate replication lag entirely?

Yes, but synchronous replication forces the primary to wait for network acknowledgment from replicas before committing, adding latency to every single write and blocking writes if replicas fail.

## Citations

- https://www.postgresql.org/docs/current/warm-standby.html
- https://martinfowler.com/articles/patterns-of-distributed-systems/read-your-writes.html

# How do Database Migrations execute zero-downtime schema changes on multi-million row tables using the Expand-and-Contract pattern?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Executing naive schema changes on large production tables causes table-level lock contention that crashes web applications; zero-downtime migrations require the Expand-and-Contract pattern.** In relational databases like PostgreSQL, running naive DDL commands—such as `ALTER TABLE orders ADD COLUMN status_code VARCHAR NOT NULL DEFAULT 'PENDING';` or renaming a column on a 50-million-row table—requests an AccessExclusiveLock. This lock blocks all concurrent SELECT, INSERT, UPDATE, and DELETE operations.

Incoming web worker requests queue up, exhausting database connection pools and precipitating a full application outage.\n\n**The four-phase Expand-and-Contract lifecycle.** Zero-downtime migrations (managed via tools like Alembic or Flyway) decouple schema changes across four discrete deployment phases: (1) Phase 1 (Expand): Deploy non-locking DDL to add the new column as nullable, or create non-blocking indexes concurrently (`CREATE INDEX CONCURRENTLY`). Deploy application code v1 that continues reading from the old column but dual-writes updates to both the old and new columns; (2) Phase 2 (Backfill): Run an idempotent, throttled background migration worker (e.g., processing 2,000 rows at a time: `UPDATE orders SET new_col = old_col WHERE id BETWEEN :start AND :end AND new_col IS NULL`). Throttling ensures the backfill does not saturate disk I/O or cause lock escalation; (3) Phase 3 (Switch): Once backfill reaches 100% parity, deploy application code v2 that reads exclusively from the new column while maintaining dual-writes; and (4) Phase 4 (Contract): Once code v2 is stable, deploy code v3 that ceases writing to the old column, followed by a final non-locking migration that drops the obsolete old column.

## Why

A team renames a column on a 30M-row table during a production deployment. The DDL locks the table for 4 minutes. All 200 web workers block waiting for the lock, maxing out database connections and throwing 504 Gateway Timeouts across the entire site.

## Worked Case

A team renames a column on a 30M-row table during a production deployment. The DDL locks the table for 4 minutes. All 200 web workers block waiting for the lock, maxing out database connections and throwing 504 Gateway Timeouts across the entire site.

## Risk

Running DDL that acquires an AccessExclusiveLock behind a long-running SELECT query blocks all subsequent read and write queries, starving the connection pool in seconds.

## Trade-off

Expand-and-contract requires multi-stage deployments, dual-writing application logic, and backfill scripts, trading deployment speed for zero user downtime and zero data loss.

## Try This

Write an Alembic migration using the expand-and-contract pattern to rename a column on an orders table. Verify that application v1 and v2 can run simultaneously against the intermediate database state.

## Follow-ups

### Why must CREATE INDEX CONCURRENTLY be used in production PostgreSQL?

Standard CREATE INDEX acquires a ShareLock that blocks all concurrent writes; CONCURRENTLY executes in multiple transactions without blocking writes, though it takes longer to complete.

## Citations

- https://martinfowler.com/bliki/ParallelRun.html
- https://alembic.sqlalchemy.org/en/latest/cookbook.html

# How do you distinguish duplicate records from different entities that happen to share the same name?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: data-engineering-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Separate source identity, entity identity and search normalization.** A source identifier names a record in one system. An entity identifier names the real-world object your application believes several records describe. A normalized name is merely a matching feature. Making the normalized name the primary key can permanently merge distinct entities before you have enough evidence.

**Define the unit being deduplicated.** Two advertisements may describe one opening, two openings with the same title, or successive versions of one opening. Similar questions arise for products, people and organizations. Include stable source references, location, dates and other domain-specific evidence when generating candidate matches. Preserve every original source record and its provenance so a merge can be reviewed or reversed.

**Use staged resolution.** Exact trusted identifiers can support deterministic links. Weaker signals generate candidates for a scored decision with an explicit match, nonmatch or review outcome. A useful system can abstain. Do not automatically merge an entire connected component simply because A resembles B and B resembles C; pairwise similarity is not necessarily transitive entity identity.

**Evaluate the mistakes that matter.** Measure false merges and false splits separately on labeled pairs and entity clusters. Stratify by language, source, missing fields and common names. A false merge can leak one person's information into another profile or contaminate evidence, while a false split can inflate counts. The local example keeps two identical names under different source identities and demonstrates why the display name alone cannot arbitrate a merge.

## Why

Two records share the display name North Star but have different verified registration identifiers. A name-based key collapses them; an identity model keeps both and can still index the shared name for search.

## Worked Case

Two records share the display name North Star but have different verified registration identifiers. A name-based key collapses them; an identity model keeps both and can still index the shared name for search.

## Risk

Overwriting source records during deduplication makes an incorrect merge hard to investigate or undo.

## Trade-off

Conservative matching creates more review work and some false splits, but preserves evidence needed to correct false merges.

## Try This

Build a fixture containing identical names, changed names and duplicated source records. Label which pairs should merge and explain which evidence authorizes that decision.

## Follow-ups

### Does a high embedding similarity prove two records are duplicates?

No. Embeddings capture aspects of semantic similarity, not authoritative identity. Use them to propose candidates and combine independent evidence under a reviewed decision policy.

### How do you undo a false merge?

Preserve immutable source records and versioned link decisions. Reverse the link, rebuild affected aggregates and invalidate derived search or answer artifacts using lineage.

## Citations

- https://docs.python.org/3/library/json.html

# How do you change canonicalization or alias rules without breaking existing record identities?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: data-engineering-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Version the rule set independently of the entity.** A new alias dictionary or suffix rule can change a computed key even when the source record did not change. Persist the normalization version and the features used for a decision. Keep the application's stable entity identifier independent of recomputed labels wherever possible.

**Treat aliases as scoped assertions.** An acquisition, a product brand and a legal subsidiary are different relationships. Collapsing all of them into one organization can be wrong for the task. Store the relationship type, scope and validity period where relevant. Reject cycles and ambiguous mappings instead of silently following an arbitrary chain. A malformed configuration should be visible to operators rather than quietly changing identity behavior.

**Migrate with a collision report.** Compute new keys alongside old ones on a representative snapshot. Identify many-old-to-one-new merges and one-old-to-many-new splits before writes. Retain an old-key lookup or explicit redirect for external references. Promote the mapping through a reviewed migration, and define rollback for links and derived artifacts. Avoid mass-renaming primary keys based only on a string transformation.

**Do not confuse determinism with uniqueness.** A short hash suffix reduces some accidental collisions but cannot make a finite key mathematically unique for unlimited inputs. Include the suffix in the total length budget, preserve the full identity basis for collision checks, and use a uniqueness constraint with explicit conflict handling. The example exposes a collision caused by a rule change without merging either stored entity.

## Why

Old rules keep North Star Labs and North Star separate. A new suffix-stripping rule maps both to north-star. The migration should report a collision for review rather than choosing whichever row is processed last.

## Worked Case

Old rules keep North Star Labs and North Star separate. A new suffix-stripping rule maps both to north-star. The migration should report a collision for review rather than choosing whichever row is processed last.

## Risk

A silent alias change can alter deduplication, foreign references, cached answers and historical counts in one deployment.

## Trade-off

Dual-key compatibility costs storage and transition logic but makes migration and rollback controlled.

## Try This

Create an alias cycle, a many-to-one rule change and two long labels sharing a truncated prefix. Define migration outcomes before updating any primary key.

## Follow-ups

### Should every subsidiary share its parent company identity?

Only when the task explicitly uses that grouping. Keep legal entity, parent relationship and brand as separate concepts so one alias rule does not erase distinctions needed elsewhere.

### Can a random identifier replace all normalization?

It solves stable storage identity but not cross-source matching. Keep normalization and evidence-based linking as separate operations.

## Citations

- https://docs.python.org/3/library/json.html

# How do you migrate legacy data when the new schema requires information the old schema never stored?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: data-engineering-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**A migration must not invent missing facts.** New required fields may have no truthful value in old records. Separate the structural conversion from the policy deciding which migrated records can be used. A fabricated default can make validation pass while corrupting later decisions or model training.

**Represent uncertainty explicitly.** Depending on the domain, use a supported unknown state, retain a legacy-only representation, quarantine the record for review, or request user clarification. Distinguish absent, explicitly declined, not applicable and invalid where those states have different meanings. A migration note should record the original value, conversion rule, rule version and any unresolved fields without copying unnecessary sensitive data.

**Validate at the new boundary.** A constructor accepting a dictionary does not prove every nested object satisfies the new contract. Validate nested records, required discriminators and cross-field invariants before marking the record migrated. Preserve rejected inputs for a controlled repair path rather than repeatedly crashing an entire batch.

**Make conversion restartable and observable.** Give each source record and migration version a durable identity, count successes and review-required outcomes, and define behavior on a second run. Do not overwrite a user correction that arrived after the migration read. The example marks a missing proficiency field as unknown instead of guessing a level from an unrelated fact; it separates the reportable issue from the converted record.

## Why

An old record stores a language name but no proficiency. The new model requires proficiency. Setting fluent would assert knowledge the system does not have; a reviewable unknown state preserves the original evidence.

## Worked Case

An old record stores a language name but no proficiency. The new model requires proficiency. Setting fluent would assert knowledge the system does not have; a reviewable unknown state preserves the original evidence.

## Risk

Validation-friendly fabricated values can silently become trusted features in downstream matching or generated claims.

## Trade-off

Allowing unknown states adds downstream handling, while quarantine reduces usable coverage until missing data is repaired.

## Try This

Migrate fixtures with missing, invalid, explicitly unknown and valid values. Show which records remain usable and which need review.

## Follow-ups

### What if the new schema forbids unknown?

Keep the record outside the active target dataset until it can be repaired, or approve a schema change that represents uncertainty. Do not silently forge a value just to satisfy a constructor.

### Should a migration infer missing data with an LLM?

Only under an explicit enrichment policy that preserves inferred status, evidence and review requirements. A generated guess must not be relabeled as an observed source fact.

## Citations

- https://docs.python.org/3/library/json.html
- https://docs.python.org/3/library/dataclasses.html

# How do you preserve extracted, inferred and user-confirmed facts without turning guesses into ground truth?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: data-engineering-foundations
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Store epistemic status as part of the data contract.** A directly observed field, a model inference and a user confirmation have different evidential weight. Keep the proposed value, source span or record, extraction/model version, timestamp and review status. Do not hide all of them behind one canonical value with no history.

**Define promotion and supersession rules.** An extracted candidate may become confirmed after user review. A later model run should not overwrite that confirmed value just because it produced a higher self-reported confidence. Conflicting observations need an explicit resolution path, and a user's correction should preserve the fact that an earlier derived value was superseded. Keep the current projection separate from immutable evidence where auditability matters.

**Use confidence carefully.** A score is meaningful only relative to a calibrated task and population. A model's verbal confidence or a heuristic label is not a measured probability. Preserve abstention and unknown states, and route consequential ambiguity to confirmation rather than converting it into a definitive feature.

**Control downstream propagation.** Generated answers, recommendations and analytics should know which facts are confirmed, inferred or stale. A human-readable completeness percentage measures filled fields, not truth or suitability. If an upstream source is corrected or deleted, use lineage to invalidate or rebuild affected outputs. The example prevents a new low-authority inference from replacing a confirmed value and preserves unknown information rather than filling it with a guess.

## Why

A model infers that a user is an expert from a title string, but the user has explicitly marked their proficiency as intermediate. The inferred update must not silently overwrite the confirmed field.

## Worked Case

A model infers that a user is an expert from a title string, but the user has explicitly marked their proficiency as intermediate. The inferred update must not silently overwrite the confirmed field.

## Risk

Canonicalizing inferred labels as source truth can amplify errors through retrieval, ranking and generated text.

## Trade-off

Keeping provenance and review state costs storage and UI complexity but makes corrections and explanation possible.

## Try This

Create observed, inferred, confirmed and corrected versions of one fact. Show which is displayed and which derived artifacts must be invalidated after correction.

## Follow-ups

### Can user-confirmed data ever be wrong?

Yes. Confirmation is provenance and workflow evidence, not an infallible truth guarantee. Support correction and distinguish user assertions from independently verified facts where the task requires it.

### Does a complete profile imply high-quality data?

No. Completeness measures presence under a chosen checklist. Correctness, freshness, provenance and task relevance need independent measures.

## Citations

- https://docs.python.org/3/library/json.html

# How do analytical data models differ from transactional models?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Transactional models support valid concurrent changes to operational entities. Analytical models organize historical facts and dimensions for repeated aggregation and interpretation. A fact table needs an explicit grain: what one row represents. Dimensions supply descriptive context, sometimes with historical versions. Denormalization can improve analytical access but must not silently duplicate measures across joins. Define the relationship between source truth, derived transformations and published metrics so operational corrections can be traced into reports.

## Why

Joining an order total to multiple order lines and then summing that total counts the same order repeatedly. The defect comes from mismatched grain, even though the join and SQL execute successfully.

## Worked Case

Joining an order total to multiple order lines and then summing that total counts the same order repeatedly. The defect comes from mismatched grain, even though the join and SQL execute successfully.

## Risk

A valid query can produce a semantically inflated metric.

## Trade-off

Model for the workload while preserving grain, keys and source lineage.

## Try This

State the grain of two tables and demonstrate a join that would double-count a measure.

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How do batch and streaming pipelines differ in latency and recovery?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Batch pipelines process bounded collections under a completion boundary. Streaming pipelines process an ongoing sequence and need explicit event-time, state and progress semantics. Lower latency does not remove data-quality checks, replay requirements or the need for idempotent effects. A batch can still run incrementally, and a streaming system may internally use microbatches. Choose based on freshness requirements, operational cost and recovery behavior rather than equating streaming with a universally more advanced design.

## Why

A nightly report may tolerate hours of delay and benefit from a reproducible bounded snapshot. A fraud alert may need seconds, while its final corrected aggregates still require a late-data policy.

## Worked Case

A nightly report may tolerate hours of delay and benefit from a reproducible bounded snapshot. A fraud alert may need seconds, while its final corrected aggregates still require a late-data policy.

## Risk

A continuously running process is not automatically a correct streaming computation.

## Trade-off

Batch simplifies bounded reconciliation; streaming reduces delay with more state and timing complexity.

## Try This

Define freshness and recovery targets for a report and an alerting pipeline.

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# What do at-most-once, at-least-once and exactly-once mean for pipeline effects?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Delivery guarantees describe a particular boundary, not every downstream consequence. At-most-once can lose work after failure, while at-least-once permits replay and needs duplicate-safe effects. Exactly-once claims require a precise state and progress transaction, or an equivalent destination contract. A broker's processing guarantee does not automatically cover an unrelated email service or database. Identify the source position, accepted event identity, durable destination state and acknowledgement order, then test crashes between them.

## Why

A worker commits a row and crashes before acknowledging its event. Restarting must either replay safely through a deduplication invariant or use a shared transaction that coordinates the relevant state and progress.

## Worked Case

A worker commits a row and crashes before acknowledging its event. Restarting must either replay safely through a deduplication invariant or use a shared transaction that coordinates the relevant state and progress.

## Risk

Advertising broker-level exactly-once as universal effect safety hides uncoordinated sinks.

## Trade-off

Idempotent destination writes often provide a practical scoped replay contract.

## Try This

Inject a crash after the destination commit and inspect the replayed result.

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How do data contracts handle nulls, units, time zones and schema changes?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A contract includes meanings, not only column names and primitive types. Null may mean unknown, inapplicable or deliberately removed; one ambiguous value cannot reliably encode all three. Numeric fields need units, timestamps need clock and zone semantics, and enums need a compatibility policy. A structurally backward-compatible field can still alter a business meaning. Version producer and consumer assumptions together, validate at boundaries and quarantine records that cannot be interpreted safely rather than inventing defaults silently.

## Why

Changing an amount from cents to currency units leaves its numeric type unchanged but multiplies the effective value by 100 if the consumer retains the earlier meaning. A type-only compatibility check misses it.

## Worked Case

Changing an amount from cents to currency units leaves its numeric type unchanged but multiplies the effective value by 100 if the consumer retains the earlier meaning. A type-only compatibility check misses it.

## Risk

Silent coercion can turn a breaking semantic change into plausible corrupt data.

## Trade-off

Flexible schemas aid evolution only when semantic ownership and validation remain explicit.

## Try This

Write compatible and incompatible changes for one event schema and explain each consumer outcome.

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How do lineage, quality checks and reconciliation support trustworthy derived data?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Lineage connects a published row or aggregate to source versions and transformation versions. Quality checks test declared properties such as uniqueness, allowed ranges, completeness and referential integrity. Reconciliation compares source and destination totals under matching scope and time boundaries. A passed row count alone does not prove correct values, ownership or deletion. Store enough versioned metadata to reproduce or explain a discrepancy, and distinguish quarantined records from a complete successful ingestion.

## Why

Two datasets can have the same row count while containing different customer identifiers or reversed amounts. Reconcile keys and relevant measures, and trace a sampled result back to its exact source revision.

## Worked Case

Two datasets can have the same row count while containing different customer identifiers or reversed amounts. Reconcile keys and relevant measures, and trace a sampled result back to its exact source revision.

## Risk

A green pipeline status can hide records silently dropped by a transformation.

## Trade-off

More checks cost work; select checks tied to downstream consequences.

## Try This

Design reconciliation for counts, keys, amounts and deletion visibility after a replay.

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# How should historical backfills coexist with live ingestion and deletion?

<!-- meta
answer_format: conceptual
domain: data-engineering
subdomain: data-engineering-foundations
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A backfill reprocesses older data under a defined source and transformation version. Live processing may continue while it runs, so updates need ordering or version guards to prevent older results overwriting newer state. Deletion intents and permissions must also survive replay. Build a separate generation when appropriate, validate it, then promote it with an explicit read boundary and rollback plan. A replay should not resurrect data removed after the historical snapshot was taken.

## Why

An old snapshot contains document D at revision 2, while live state has a revision-4 tombstone. Backfill must preserve that deletion instead of republishing revision 2 simply because it appears in the snapshot.

## Worked Case

An old snapshot contains document D at revision 2, while live state has a revision-4 tombstone. Backfill must preserve that deletion instead of republishing revision 2 simply because it appears in the snapshot.

## Risk

Unversioned upserts can make historical work overwrite current truth.

## Trade-off

Separate generations ease validation at the cost of temporary duplicate storage.

## Try This

Replay an old snapshot alongside a newer update and tombstone, then verify final visibility.

## Citations

- https://beam.apache.org/documentation/programming-guide/
- https://kafka.apache.org/quickstart/
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://opentelemetry.io/docs/security/handling-sensitive-data/
