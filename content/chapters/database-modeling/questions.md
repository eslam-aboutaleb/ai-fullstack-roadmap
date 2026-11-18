<!-- chapter: database-modeling -->

# Why store support service requests in relational tables instead of only vector documents?

<!-- meta
domain: backend
subdomain: database-modeling
module: database-modeling
concept: Why store support service requests in relational tables instead of only vector documents
difficulty: foundations
misconception_target: More tables always means better design
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Service requests have exact ownership, monetary amounts, lifecycle states, references, and transaction boundaries. A vector index optimizes similarity retrieval and does not replace those relational invariants. The same request can have an authoritative row and a derived search representation.

## Spoken Summary

Relational tables enforce structured identities, relationships, constraints and transactions for service requests. Vector documents support relevance lookup but do not replace the authoritative operation state. Model owned tasks, operation keys, revisions and effect intent explicitly, then derive searchable projections as needed.

## Why

Keep authoritative ownership, state transitions, and relationships in constrained transactional records. Use vector indexes as derived search projections that can be rebuilt, not as the only source of business truth.

## Production Case

A user retries the same request after a timeout. UNIQUE(owner, operation_key) resolves it to the existing task, whereas similarity search cannot reliably decide whether two messages are the same logical operation.

## Risk

Treating the vector record as the sole source of truth makes exact authorization, status transitions, and recovery dependent on a derived index. Search ranking cannot decide whether a service request exists or who owns it.

## Trade-off

Relational plus search modeling creates projection maintenance work but supports exact operations and flexible discovery. A text-only prototype is smaller and insufficient for authoritative workflows.

## Try This

Mark every Claim column as identity, business fact, authority constraint, lifecycle metadata, or derived search data. Explain which can be rebuilt.

## Execution Timeline

Identify entities → Define attributes → Choose primary keys → Map relationships → Add constraints → Review normal forms

## Complexity

Query cost depends on access path, selectivity, joins, indexes and concurrency. B-tree lookup is often logarithmic in tree height plus returned/filtered rows; an index does not make every query O(log n). Inspect real query plans.

## Definitions

- **Normalization**: Organizing tables to reduce redundancy and dependency
- **Foreign key**: Column that references a primary key in another table
- **Constraint**: Rule enforced by the database on column values

## Alternatives

- Denormalized design for read-heavy workloads
- Document store for unstructured content

## Pitfalls

- Missing foreign key constraints
- Storing derived data redundantly
- Over-normalizing for simple read patterns

## Follow-ups

### Can a vector index be your transaction ledger?

It is not a substitute for the uniqueness, ownership and atomic state-transition guarantees required by the operation contract.

## Example

> Explanation: Document ownership is separate from per-document revision identity. Different documents owned by the same user can each have revision one. PostgreSQL fragment requires an existing users table and a disposable schema.
> Output: Schema illustration; execute with its users dependency in a disposable PostgreSQL environment.

```python
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  owner_id UUID NOT NULL REFERENCES users(id)
);
CREATE TABLE document_revisions (
  document_id UUID NOT NULL REFERENCES documents(id),
  revision INT NOT NULL CHECK (revision > 0),
  content TEXT NOT NULL,
  PRIMARY KEY (document_id, revision)
);
```

## Citations

- https://www.postgresql.org/docs/current/ddl-constraints.html

# Why have both a UUID primary key and a human-readable request ID?

## Answer

A UUID provides an internal identifier suitable for references; a separate request ID provides a support-friendly external label. They have different display and collision properties. Neither identifier should be treated as an authorization secret.

## Why

Choose immutable internal identifiers and stable public references deliberately. Scope uniqueness to the right tenant or operation and reject collisions through database constraints.

## Risk

Shortened random identifiers can collide. A production collision-handling path should distinguish a retryable uniqueness conflict from unrelated database errors, and users must still be scoped even when an ID is known.

## Trade-off

Friendly IDs improve support and communication while adding an extra index and identity mapping. Full opaque IDs are simpler but awkward to read aloud.

## Try This

Explain how an identifier collision differs from an idempotent replay. Design a bounded generation retry that does not duplicate a pending submission.

# Why use Numeric and Decimal for request amounts?

## Answer

Decimal arithmetic and a fixed-scale Numeric column represent monetary values more predictably than binary floating point. Currency precision, rounding, allowed scale, and upper bounds are part of the domain contract rather than formatting details.

## Why

Use decimal representations and explicit currency rules. Validate scale and range before persistence, and preserve decimal strings across API serialization rather than round-tripping through binary floats.

## Risk

A Decimal column cannot retroactively undo precision lost earlier in JSON parsing, float conversion, or arithmetic. Validation and serialization must preserve the intended amount end to end.

## Trade-off

Decimal values need explicit JSON handling and careful provider-tool schemas. Float is convenient for generic numeric tools but weakens exact-money guarantees.

## Try This

Trace an amount with cents from browser JSON through Pydantic, pending JSONB, confirmation, and SQL storage. Propose a Decimal-preserving signature and matching tests.

# How do foreign keys, unique constraints, and check constraints complement application validation?

## Answer

Application validation gives useful error messages; database constraints protect against every writer sharing the database. Foreign keys preserve references, unique constraints enforce identity rules, and check constraints reject invalid row-level values even when a route is bypassed.

## Why

Specify foreign keys, nullability, uniqueness, and state checks in migrations. Application validation improves errors; database constraints protect against concurrent callers and alternative write paths.

## Risk

Assuming all invariants are enforced because ORM types exist leaves gaps for scripts, workers, and future routes. Constraints also need deliberate delete and migration behavior.

## Trade-off

Strong constraints simplify consistency reasoning but can complicate staged migrations and bulk imports. Relaxing them requires another proven enforcement mechanism.

## Try This

Compare the Claim, PendingRequest, an indexing job, and a request event models with their migrations. List invariants enforced only in Python and those enforced by PostgreSQL.

# What belongs in normalized columns versus JSONB?

## Answer

Put fields used for relationships, strict constraints, frequent filtering, and stable reporting in typed columns. JSONB is useful for variable event payloads or a prepared-form snapshot. Its flexibility does not remove the need for schema versions, validation, or selective indexing.

## Why

Normalize identity, ownership, status, amounts, timestamps, and relationships that need constraints. Reserve JSONB for evolving payloads whose validation and query needs are explicitly managed.

## Risk

Unversioned JSON can become unreadable after schema changes. Copying an entire stale state blob can also overwrite concurrent updates, while arbitrary JSON may retain more private data than needed.

## Trade-off

JSONB speeds evolving payloads and weakens some relational guarantees. Normalize stable, high-value fields instead of treating the database as a dictionary with no contracts.

## Try This

Design a version field and migration reader for a prepared submission whose incident_date field was added later. Explain the fallback for older records.

# Why does the owner-and-created-at composite index matter?

## Answer

A request list filters by owner and orders by creation time. An index beginning with owner_id and then created_at can support that access pattern more directly than two unrelated indexes. Index design should follow real predicates, ordering, and pagination.

## Why

Start index design from actual predicates and ordering. Inspect query plans and representative data distributions, then balance faster reads against write cost and maintenance.

## Risk

An index declaration does not prove an efficient plan at production data sizes. Additional sort keys, selective predicates, and row estimates can change the plan; unused indexes still cost writes and storage.

## Trade-off

More indexes accelerate selected reads while slowing mutation and increasing maintenance. Validate with representative EXPLAIN plans rather than indexing every column reflexively.

## Try This

Compare the owner-scoped listing plan with and without the composite index in a disposable database. Include a tie-breaking ID if you design keyset pagination.

# How do knowledge versions differ from active knowledge chunks?

## Answer

A knowledge version records the source and indexing configuration over time. Policy chunks are searchable material for a version. Keeping version records does not necessarily mean every historical chunk remains retained or that a query selects the contract applicable to an incident.

## Why

Track effective intervals separately from indexing time. Resolve the applicable source revision before searching its derived chunks, and retain the revision needed to verify an earlier answer.

## Risk

Current-source retrieval can answer the wrong historical question even when its text is accurately quoted. Historical evidence needs both retention and an explicit applicable-version filter.

## Trade-off

Retaining every version supports audits and costs storage and selection logic. Current-only indexing is simpler and must state its scope honestly.

## Try This

Create two rule revisions with different deductibles and one incident between their effective dates. Define the query and citation fields required to choose correctly.

# Why use Alembic migrations instead of create_all for production evolution?

## Answer

Create_all creates missing schema objects represented in current metadata; it is not a reviewed sequence for changing existing columns, backfilling data, or coordinating old and new application versions. Migrations record explicit upgrade steps and dependencies.

## Why

Make production schema changes explicit and reviewed. Assign migration ownership, verify upgrades against existing data, and coordinate application compatibility instead of relying on runtime table creation.

## Risk

Runtime-created tables can escape a migration policy, and concurrent DDL can disrupt startup. Inventory every schema owner and make a failed migration visibly block incompatible application use.

## Trade-off

Migrations add review and deployment sequencing but make history inspectable. Runtime creation is convenient for framework state and harder to govern consistently.

## Try This

Define which component owns each reference table and write a reviewed upgrade path for an existing populated database.

# What is an expand-and-contract migration?

## Answer

Add a compatible schema surface first, deploy code that can read old and new forms, backfill safely, switch writers, then remove the old form in a later release. The sequence allows rolling deployment and rollback without requiring every process to switch simultaneously.

## Why

Add a compatible new structure, backfill with bounded work, deploy readers and writers deliberately, and remove obsolete structure only after verifying all consumers have migrated.

## Risk

A backfill can hold locks or overload the database; a destructive cleanup can make application rollback impossible. Background jobs may also contain payloads written by an older schema version.

## Trade-off

Compatibility periods increase temporary complexity and reduce deployment coupling. A single destructive migration is shorter and can require a maintenance window.

## Try This

Design a migration from float-shaped tool input to explicit decimal-string amounts. Include old pending submissions and jobs, not just current Claim rows.

# How should you model authoritative events versus derived projections?

## Answer

A request event records lifecycle history; a request status is a current-state projection. Embedding records and notifications are downstream projections. Agent session events describe runtime execution, while audit events describe selected high-value actions. These logs are related but not interchangeable event-sourcing systems.

## Why

Separate authoritative lifecycle records from derived search and notification projections. Define replay and reconciliation for each projection rather than calling every append-only table an event-sourced system.

## Risk

Calling any append-only table event sourcing overstates replayability. A complete event-sourced design needs sufficient immutable events, deterministic projection rebuilding, versioning, and a declared source of truth.

## Trade-off

Current rows plus a transition trail provide useful history with lower complexity. Full event sourcing improves replay options and adds substantial schema and operational obligations.

## Try This

For each event table, state whether it can rebuild a Claim exactly. Identify missing facts before claiming replay-based recovery.

# How do Query Optimizers choose between Nested Loop, Hash Join, and Merge Join in SQL, and how do missing statistics cause catastrophic query plans?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Relational query optimizers select physical join operators by estimating the I/O and CPU cost of candidate execution trees based on catalog table statistics.** In engines like PostgreSQL, SQLite, and MySQL, the Cost-Based Optimizer (CBO) evaluates three fundamental join algorithms: (1) Nested Loop Join: For each row in the outer table, it scans the inner table. When the inner table possesses an efficient B-Tree index on the join key, cost is O(M * log N), making it exceptionally fast for small outer row sets; (2) Hash Join: The engine reads the entire build table into memory, constructs an in-memory hash table in work_mem, and sequentially probes it with rows from the outer table in O(M + N) time.

If the build table exceeds work_mem, it spills to disk as a multi-batch hash join, causing high disk I/O; and (3) Merge Join: Both inputs must be presorted by the join key (either via index scans or an explicit sort step) and are then joined in a single linear O(M + N) merge pass.\n\n**The catastrophe of stale catalog statistics.** The optimizer relies entirely on table statistics (stored in pg_statistic or collected via ANALYZE) to estimate row cardinalities and data distribution histograms. If a table experiences rapid bulk inserts or deletions without an updated ANALYZE, the optimizer may estimate that a filter matches 5 rows when it actually matches 5,000,000 rows. Relying on this erroneous estimate, the optimizer selects a Nested Loop Join instead of a Hash Join, forcing the database to execute 5,000,000 individual index lookups, turning a sub-second query into a 45-minute outage that exhausts database CPU and connection pools.

## Why

A database table grows from 1,000 to 10,000,000 rows after an ingestion run. Without running ANALYZE, the optimizer assumes the table is tiny and picks a Nested Loop join against a large transactions table, pegging database CPU at 100% and timing out all web requests.

## Worked Case

A database table grows from 1,000 to 10,000,000 rows after an ingestion run. Without running ANALYZE, the optimizer assumes the table is tiny and picks a Nested Loop join against a large transactions table, pegging database CPU at 100% and timing out all web requests.

## Risk

Stale statistics cause optimizers to choose pathological query plans; running unconstrained ANALYZE on multi-terabyte production tables during peak load can itself cause I/O lock contention.

## Trade-off

Automating aggressive autovacuum and autoanalyze maintains accurate statistics and optimal join selections, trading small continuous background I/O for query predictability.

## Try This

Run EXPLAIN (ANALYZE, BUFFERS) on a join query before and after running ANALYZE on a rapidly populated table. Observe how the estimated row count and chosen join algorithm change.

## Follow-ups

### Can query hints force a specific join algorithm in PostgreSQL?

PostgreSQL intentionally does not support query hints in core SQL; developers instead tune planner cost parameters (e.g. enable_nestloop=off for session diagnosis) or adjust work_mem and statistics targets.

## Citations

- https://www.postgresql.org/docs/current/using-explain.html
- https://www.postgresql.org/docs/current/planner-stats.html

# How do B-Trees and GIN indexes differ in PostgreSQL, and how must composite indexes be structured under the leftmost prefix rule?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**B-Trees and Generalized Inverted Indexes (GIN) organize on-disk data structures for fundamentally different query patterns and data types.** The B-Tree is a balanced multi-way search tree that maintains data in strict sorted lexicographical order. It excels at point equality lookups (=), range scans (<, <=, >, >=), prefix pattern matching (LIKE 'abc%' with text_pattern_ops), and satisfying ORDER BY clauses without requiring an in-memory sort pass. In contrast, a GIN index is an inverted index: instead of mapping one row to one index key, it maps individual elements (keys and values inside JSONB documents, elements of arrays, or lexemes in full-text tsvector columns) to a posting list of matching row pointers (TIDs).\n\n**The Leftmost Prefix Rule in composite B-Tree indexes.** When creating a composite index across multiple columns—such as `CREATE INDEX idx_tenant_status_date ON orders (tenant_id, status, created_at)`—the B-Tree sorts rows hierarchically: first by tenant_id, then by status within that tenant, and finally by created_at.

Under the leftmost prefix rule, this index accelerates queries filtering on: (1) `tenant_id`; (2) `tenant_id AND status`; or (3) `tenant_id AND status AND created_at`. However, a query filtering solely on `WHERE status = 'PENDING'` or `WHERE created_at > NOW()` cannot utilize the index directly because the leading column is missing.\n\n**Covering indexes with INCLUDE.** To optimize high-throughput queries, PostgreSQL supports covering indexes: `CREATE INDEX idx_orders_covering ON orders (tenant_id, status) INCLUDE (total_amount)`. The payload column `total_amount` is stored in the leaf pages without participating in B-Tree sorting, allowing Index-Only Scans that satisfy queries completely without reading primary table heap pages.

## Why

An API queries orders by `WHERE tenant_id = 5 AND created_at > :date`. An index on `(tenant_id, status, created_at)` cannot efficiently filter on created_at because the middle column `status` was skipped, forcing an index scan over all dates for that tenant.

## Worked Case

An API queries orders by WHERE tenant_id = 5 AND created_at > :date. An index on (tenant_id, status, created_at) cannot efficiently filter on created_at because the middle column status was skipped, forcing an index scan over all dates for that tenant.

## Risk

Creating separate GIN indexes on large, high-velocity JSONB columns drastically slows down INSERT and UPDATE throughput due to the overhead of updating inverted posting trees.

## Trade-off

Composite B-Trees require careful column ordering based on query filters; GIN indexes support arbitrary JSONB sub-key queries at the cost of higher storage and write overhead.

## Try This

Create a composite index on (a, b, c). Run EXPLAIN on queries filtering on (a), (a, b), and (b, c). Observe where Index Scans vs Seq Scans occur.

## Follow-ups

### What is an index skip scan in modern database engines?

An index skip scan allows the engine to jump across distinct values of a leading low-cardinality column to utilize subsequent indexed columns, emulating a series of equality queries.

## Citations

- https://www.postgresql.org/docs/current/indexes-types.html
- https://www.postgresql.org/docs/current/indexes-composite.html

# How do SQL Three-Valued Logic and NULL semantics create silent bugs in NOT IN subqueries and aggregation?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**SQL evaluates boolean logic under Three-Valued Logic (3VL), where conditions evaluate to TRUE, FALSE, or UNKNOWN.** In relational databases, NULL does not represent an empty string or zero; it represents the absence of a value or an unknown state. Consequently, any direct equality comparison involving NULL—such as `NULL = NULL` or `column = NULL`—does not evaluate to TRUE; it evaluates to UNKNOWN. To test for missing data, SQL mandates the explicit unary operators `IS NULL` or `IS NOT NULL`.\n\n**The catastrophic NOT IN subquery trap.** A notorious production defect occurs when using the `NOT IN` operator against a subquery that contains a single NULL value: `SELECT * FROM users WHERE id NOT IN (SELECT supervisor_id FROM employees)`.

Mathematically, `id NOT IN (1, 2, NULL)` expands to: `(id != 1) AND (id != 2) AND (id != NULL)`. Because `id != NULL` evaluates to UNKNOWN, and in boolean logic `TRUE AND UNKNOWN` equals UNKNOWN, the entire WHERE clause evaluates to UNKNOWN for every single row in the users table! As a result, the query returns zero rows silently, creating a catastrophic logic bug. The correct engineering solution is using `NOT EXISTS (SELECT 1 FROM employees WHERE supervisor_id = users.id)` or filtering `WHERE supervisor_id IS NOT NULL`.\n\n**Aggregation discrepancies with NULLs.** Aggregate functions handle NULLs non-uniformly: `COUNT(*)` counts all rows including those with NULLs; `COUNT(column)` counts only rows where column is NOT NULL; `SUM(column)` and `AVG(column)` completely ignore NULL values, which can distort financial averages if missing entries should have been treated as zero.

## Why

A billing audit query uses `WHERE customer_id NOT IN (SELECT customer_id FROM exempted_accounts)`. An unvalidated entry in exempted_accounts has a NULL customer_id. The audit query returns zero billable customers, causing missed billings.

## Worked Case

A billing audit query uses WHERE customer_id NOT IN (SELECT customer_id FROM exempted_accounts). An unvalidated entry in exempted_accounts has a NULL customer_id. The audit query returns zero billable customers, causing missed billings.

## Risk

Relying on NOT IN with nullable columns causes queries to fail silently by returning empty result sets without throwing database errors.

## Trade-off

Using NOT EXISTS or explicit NOT NULL predicates prevents silent empty results, while requiring developers to understand correlated subquery semantics.

## Try This

Insert three rows into a table where one row has a NULL column. Execute `SELECT * FROM test WHERE id NOT IN (SELECT col FROM test)` and observe that zero rows are returned.

## Follow-ups

### Why is NOT EXISTS immune to the NULL problem?

NOT EXISTS checks for the presence or absence of rows returned by the subquery (evaluating to TRUE or FALSE), completely bypassing three-valued logic on column values.

## Citations

- https://www.postgresql.org/docs/current/functions-comparisons.html
- https://en.wikipedia.org/wiki/Null_(SQL)

# How does Document Store data modeling in MongoDB differ from SQL Normalization, and when does embedding cause the 16MB document size limit breach?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Document database modeling optimizes for application access patterns through denormalization, contrasting sharply with third-normal-form (3NF) relational design.** In relational SQL databases, data normalization decomposes entities into independent tables linked by foreign keys, eliminating data redundancy and ensuring ACID consistency at the expense of multi-table JOINs at read time. In document stores like MongoDB, the fundamental design principle is: 'Data that is accessed together should be stored together', embedding child entities directly inside parent documents as nested sub-documents or arrays to eliminate query JOINs entirely.\n\n**The Unbounded Array anti-pattern and the 16MB limit.** A common and critical modeling anti-pattern is embedding 1-to-many or 1-to-squillions relationships inside a single document—such as embedding all historical user activity logs, product reviews, or sensor telemetry readings directly into an array in a parent User or Device document: `{ "device_id": 101, "readings": [ {...}, {...} ] }`.

BSON documents have a hard, unchangeable 16MB maximum document size limit in MongoDB. As the array grows, three critical failures occur: (1) The document eventually breaches 16MB, triggering fatal write exceptions (`Document exceeds maximum allowed BSON size`); (2) Continuous in-place array growth forces the WiredTiger storage engine to reallocate and move documents on disk, fragmenting storage and degrading I/O; and (3) Reading a device profile requires transferring megabytes of historical sensor arrays across the network even if the UI only needs the device name.\n\n**The Subset Pattern and Referencing.** The production architectural solution uses the Subset Pattern: embedding only the most recent N items (e.g., last 10 readings) in the primary document for fast UI rendering, while storing the complete historical log in a separate collection referenced by `device_id`.

## Why

An IoT application embeds temperature readings into a sensor document. After 18 months of continuous telemetry, the sensor document hits 16MB and rejects all incoming writes, shutting down the ingestion pipeline.

## Worked Case

An IoT application embeds temperature readings into a sensor document. After 18 months of continuous telemetry, the sensor document hits 16MB and rejects all incoming writes, shutting down the ingestion pipeline.

## Risk

Unbounded array growth in document stores guarantees catastrophic write rejection when the 16MB BSON ceiling is breached.

## Trade-off

Embedding data enables single-round-trip reads without JOINs; referencing requires secondary queries but completely avoids document size exhaustion and memory bloat.

## Try This

Model an e-commerce order system with customers, orders, and order items in MongoDB. Embed line items inside the order document, but reference the customer by customer_id.

## Follow-ups

### Can MongoDB perform joins across collections when referencing is used?

Yes. The `$lookup` aggregation pipeline stage performs left outer joins between collections, though it carries higher computational overhead than relational SQL joins.

## Citations

- https://www.mongodb.com/docs/manual/core/data-modeling-introduction/
- https://www.mongodb.com/docs/manual/reference/limits/

# How do Object-Document Mappers implement schema validation and atomic updates over schemaless databases?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Object-Document Mappers (ODMs like Beanie for Python or Mongoose for Node.js) enforce strict application-level schema governance over inherently schemaless database engines.** At the storage engine level, document databases like MongoDB are schemaless: collections allow inserting arbitrary JSON documents with differing fields, missing keys, or incompatible data types. An ODM acts as an application-side validation boundary, using typed schemas (such as Pydantic models in Python) to validate types, apply default values, and sanitize fields before payloads are converted into BSON and transmitted to the database.\n\n**The Schema Drift Trap in distributed microservices.** When multiple microservices or background workers interact with the same MongoDB database across different deployment versions, schema drift occurs: Service A (running v2) writes a document with a renamed field or new enum, while Service B (running v1) reads the document, fails schema validation, and crashes with a runtime DeserializationError.

Production ODM architectures mandate schema versioning flags (`_schema_version: 2`) and backwards-compatible field aliases (`Field(alias="legacy_name")`).\n\n**Atomic field-level mutations vs full-document overwrites.** A dangerous anti-pattern when using ODMs is the 'read-modify-write' trap: fetching an entire document into application memory, updating an in-memory attribute, and executing a full-document `save()`. Under concurrent traffic, two workers performing this flow simultaneously overwrite each other's changes, causing lost updates. Production ODMs avoid this by compiling mutations into atomic MongoDB operators: using `$set` for specific fields, `$inc` for counters, and `$addToSet` for unique array entries directly at the database engine level.

## Why

Two workers read a customer document with wallet balance $100. Worker A adds $50; Worker B adds $20. Both save the full document back; the last write wins, setting balance to $120 and losing $50. Using atomic `$inc: {balance: 50}` guarantees the correct final balance of $170.

## Worked Case

Two workers read a customer document with wallet balance $100. Worker A adds $50; Worker B adds $20. Both save the full document back; the last write wins, setting balance to $120 and losing $50. Using atomic $inc: {balance: 50} guarantees the correct final balance of $170.

## Risk

Using full-document save() methods in ODMs overwrites concurrent writes, causing silent financial and state loss in production.

## Trade-off

Atomic operator mutations require constructing explicit database update expressions rather than updating Python object attributes, trading syntactic simplicity for absolute concurrency safety.

## Try This

Write an ODM update using atomic `$inc` and `$set` operators in Python with Beanie or Motor. Verify that concurrent requests do not overwrite each other.

## Follow-ups

### Can MongoDB enforce schema validation at the database level?

Yes. MongoDB supports JSON Schema validation directly in collection rules, rejecting documents that violate specified types or required fields even if written via raw mongo drivers.

## Citations

- https://beanie-odm.dev/
- https://www.mongodb.com/docs/manual/reference/operator/update/

# What is Polyglot Persistence, and how do you design data synchronization between a transactional SQL database, Redis cache, and a Vector Database?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Polyglot Persistence is the architectural practice of utilizing multiple specialized database technologies within a single application, matching each storage technology to its optimal workload characteristics.** In a modern enterprise AI platform, no single database engine excels at all tasks: (1) PostgreSQL serves as the authoritative, ACID-compliant relational system of record for user accounts, billing ledgers, and permissions; (2) Redis operates as an in-memory cache and volatile session store for sub-millisecond key-value lookups, rate limiting, and pub/sub messaging; and (3) Qdrant or pgvector serves as a high-dimensional vector database for semantic similarity search.\n\n**The Dual-Write synchronization catastrophe.** A common and severe anti-pattern is executing dual-writes directly inside application web controllers: an API route updates the PostgreSQL database, then writes to Redis, and finally calls the vector database.

If the worker crashes, encounters a network timeout, or hits an unhandled exception after the PostgreSQL commit, the Redis cache and vector index become permanently out of sync with reality, serving stale or phantom records.\n\n**The Transactional Outbox and Change Data Capture (CDC) solution.** Resilient polyglot synchronization decouples transactional mutations from downstream projections using the Transactional Outbox pattern: (1) When business data is written to Postgres, an event record is inserted into an `outbox_events` table within the identical ACID transaction boundary; (2) A Change Data Capture (CDC) engine (such as Debezium monitoring PostgreSQL logical replication slots) tails the Write-Ahead Log (WAL); and (3) Events are published to a durable message broker (Kafka or RabbitMQ) where dedicated worker consumers update Redis caches and re-index vector embeddings idempotently with guaranteed at-least-once delivery.

## Why

A user deletes an account. The application deletes the Postgres row, but the network drops before deleting the Redis cache or vector embeddings. The user's private profile continues to be served from cache and returned in RAG semantic search results.

## Worked Case

A user deletes an account. The application deletes the Postgres row, but the network drops before deleting the Redis cache or vector embeddings. The user's private profile continues to be served from cache and returned in RAG semantic search results.

## Risk

Dual-writing to multiple data stores in application code guarantees eventual data inconsistency, phantom records, and cache corruption.

## Trade-off

Transactional Outbox and CDC require running message brokers and background consumers, trading operational infrastructure overhead for guaranteed eventual consistency across heterogeneous databases.

## Try This

Implement a transactional outbox table in PostgreSQL. Insert a record and an outbox event in a single atomic transaction. Build a consumer worker that polls the outbox and updates an external mock store.

## Follow-ups

### How do you handle out-of-order event consumption in downstream consumers?

Every outbox event carries a monotonic version sequence number or entity timestamp; consumers discard incoming events that have a sequence number lower than the currently recorded projection state.

## Citations

- https://microservices.io/patterns/data/transactional-outbox.html
- https://debezium.io/documentation/reference/stable/architecture.html

# How do you make a data migration resumable, idempotent and safe against concurrent user edits?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: database-modeling
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Define the logical migration operation.** Bind each attempt to a record identifier, source revision and migration version. A second run should recognize an already converted record rather than apply the same destructive transformation again. Idempotence concerns the target meaning, not just whether a script can run twice without throwing an exception.

**Use an explicit source and target contract.** Validate the incoming schema version, transform to a known target and reject unsupported future versions. Keep conversion functions narrow and deterministic where possible. External enrichment should be separately identified so retries do not silently call a changing provider and produce a different supposedly structural migration.

**Guard the write using the revision read.** Update the target only if the record still has the expected data revision and schema version. If a user edited it meanwhile, discard the stale conversion and reload. Do not write an old whole-record snapshot over newer fields. Commit migration status and converted data together when they share a database.

**Operate in bounded batches.** Record a durable cursor or per-record status, errors and migration version. Checkpoint after commit, expose review-required records and avoid logging entire private payloads. Test interruption, replay, invalid input and concurrent modification. The SQLite example executes a real conditional migration update, then verifies that both replay and a stale revision fail to overwrite the migrated record.

## Why

A migration reads a version-1 record at revision 4. Another operation updates it to revision 5. A write guarded only by record ID would lose that edit; the migration must compare its expected revision before committing.

## Worked Case

A migration reads a version-1 record at revision 4. Another operation updates it to revision 5. A write guarded only by record ID would lose that edit; the migration must compare its expected revision before committing.

## Risk

A restartable script can still corrupt data if its repeated operations or stale snapshots overwrite newer facts.

## Trade-off

Conditional writes create retry work under contention but preserve edits and make conflicts visible.

## Try This

Interrupt a migration after commit but before checkpoint, replay it, then inject a user edit between read and write. Verify target integrity in both cases.

## Follow-ups

### Is a batch checkpoint enough to prove every record migrated?

No. A cursor can skip failures unless their status is separately tracked. Reconcile expected source records with successful and review-required outcomes before declaring completion.

### Should rollback always restore the old schema?

Only if it preserves all information created since migration. A backward transformation may be lossy; use explicit compatibility or repair procedures instead of promising automatic reversal.

## Citations

- https://www.sqlite.org/lang_transaction.html

# Why should schema version, record revision and source version be separate fields?

<!-- meta
answer_format: conceptual
domain: data-integrity
subdomain: database-modeling
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Each version answers a different question.** Schema version identifies how to interpret structure. Record revision identifies a particular persisted edit of one logical record. Source version identifies the upstream evidence or content from which the record was derived. A single counter cannot reliably answer all three.

**Use record revision for lost-update protection.** A client reads revision 7, edits a field and submits a write conditional on revision 7. If another editor already committed revision 8, the write conflicts instead of overwriting it. Changing the record's ordinary content should not imply that its JSON schema changed. Likewise a schema conversion can preserve the source version while changing how its fields are represented.

**Connect versions to derived artifacts.** A vector, generated explanation or cache entry should record which source and representation it describes. A newer profile revision may only change a notification preference, while a changed extracted paragraph may require another embedding. Define dependencies rather than invalidating everything indiscriminately or retaining stale outputs by accident.

**Make the API contract explicit.** Return a revision token or an HTTP entity tag, define conflict handling and avoid treating a timestamp alone as a universal concurrency token. Explain which fields increment each version and whether revisions are monotonic within one record or across a stream. The SQLite example keeps the schema constant while a guarded edit increments the record revision and rejects a second stale edit.

## Why

Two editors both load a schema-2 record at revision 7. The first commits revision 8. The second must reload or merge its intent; changing schema_version to 3 would not resolve the lost-update conflict.

## Worked Case

Two editors both load a schema-2 record at revision 7. The first commits revision 8. The second must reload or merge its intent; changing schema_version to 3 would not resolve the lost-update conflict.

## Risk

Overloading one version field can trigger unnecessary migrations and still fail to prevent stale writes.

## Trade-off

Separate counters and identifiers add metadata but make interpretation, concurrency and lineage independent and testable.

## Try This

Trace an ordinary edit, a structural migration and an upstream document replacement. State exactly which versions change for each.

## Follow-ups

### Can updated_at replace a revision counter?

Only with a precise database and API contract that ensures sufficient uniqueness and atomic comparison. Timestamp precision, clock assumptions and multiple writes can make casual comparisons unreliable.

### Should a cache key include every version field?

Include the versions and scope that determine that cached value. Unrelated edits need not invalidate an artifact, while an authorization or source change may require immediate revalidation.

## Citations

- https://www.sqlite.org/lang_transaction.html
- https://docs.python.org/3/library/json.html

# How should document identity and revision identity be modeled without forbidding multiple documents per owner?

<!-- meta
domain: backend
subdomain: database-modeling
module: database-modeling
concept: How should document identity and revision identity be modeled without forbidding multiple documents per owner?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: An owner uploads a second document and its first revision fails a global owner/revision uniqueness rule.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Give the document a stable identity and model revisions under that document, with a key such as document_id plus revision. Scope ownership through the document relationship. A uniqueness rule on owner_id and revision alone can incorrectly prevent two unrelated documents from both having revision one. Use constraints that encode the actual entity invariant.

Concrete engineering case: An owner uploads a second document and its first revision fails a global owner/revision uniqueness rule.

Boundary defense: It may hold flexible metadata, but it does not automatically enforce the relationship or revision identity. Choose explicit constraints or a deliberately tested alternative.

## Spoken Summary

Give the document a stable identity and model revisions under that document, with a key such as document_id plus revision. Scope ownership through the document relationship. A uniqueness rule on owner_id and revision alone can incorrectly prevent two unrelated documents from both having revision one. Use constraints that encode the actual entity invariant.

## Why

Give the document a stable identity and model revisions under that document, with a key such as document_id plus revision. Scope ownership through the document relationship. A uniqueness rule on owner_id and revision alone can incorrectly prevent two unrelated documents from both having revision one. Use constraints that encode the actual entity invariant.

## Production Case

An owner uploads a second document and its first revision fails a global owner/revision uniqueness rule.

## Risk

An owner uploads a second document and its first revision fails a global owner/revision uniqueness rule.

## Trade-off

It may hold flexible metadata, but it does not automatically enforce the relationship or revision identity. Choose explicit constraints or a deliberately tested alternative.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: database modeling**: Give the document a stable identity and model revisions under that document, with a key such as document_id plus revision.

## Alternatives

- It may hold flexible metadata, but it does not automatically enforce the relationship or revision identity. Choose explicit constraints or a deliberately tested alternative.

## Pitfalls

- An owner uploads a second document and its first revision fails a global owner/revision uniqueness rule.

## Follow-ups

### Can a JSON field replace the relationship constraint?

It may hold flexible metadata, but it does not automatically enforce the relationship or revision identity. Choose explicit constraints or a deliberately tested alternative.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "An owner uploads a second document and its first revision fails a global owner/revision uniqueness rule.",
  "required_decision": "Give the document a stable identity and model revisions under that document, with a key such as document_id plus revision"
}
```

## Citations

- https://www.postgresql.org/docs/current/tutorial.html

# How do normalization, keys and constraints prevent update anomalies?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Normalization separates facts according to their dependencies so one fact is not inconsistently copied into many rows. A primary key identifies a row, a foreign key links valid references, and unique/check constraints enforce specific invariants. Application validation improves errors but cannot replace database enforcement under concurrent writers. Do not normalize by habit without considering the actual dependencies and workload. Denormalized projections can support reads when their source of truth, refresh policy and repair mechanism remain explicit.

## Why

Repeating a customer's address on every open request makes a change inconsistent unless all intended rows update. An immutable historical shipping address is a different fact and may deliberately remain with its order.

## Worked Case

Repeating a customer's address on every open request makes a change inconsistent unless all intended rows update. An immutable historical shipping address is a different fact and may deliberately remain with its order.

## Risk

Treating historical snapshots and current attributes as the same fact causes incorrect updates.

## Trade-off

Normalize authoritative facts and publish deliberate read projections when justified.

## Try This

Model current customer details and historical order addresses with distinct update rules.

## Citations

- https://www.postgresql.org/docs/current/tutorial.html

# How do joins, NULL and aggregate placement change query results?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-modeling
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

An inner join keeps matched rows; an outer join can retain unmatched rows with missing right-side values. SQL NULL is not an ordinary value: comparisons often produce unknown, which a WHERE filter does not treat as true. Filtering the right table in WHERE after a left join can remove the unmatched rows the outer join was intended to preserve. Aggregating after a one-to-many join can multiply measures. State desired row grain and missing-value meaning before choosing join and grouping structure.

## Why

A customer with no orders disappears if a left-joined order condition is placed in WHERE without accounting for NULL. Move the match restriction into the join when the requirement is to preserve all customers.

## Worked Case

A customer with no orders disappears if a left-joined order condition is placed in WHERE without accounting for NULL. Move the match restriction into the join when the requirement is to preserve all customers.

## Risk

Syntactically valid SQL can silently change business inclusion rules.

## Trade-off

Choose join semantics from the required retained population and measure grain.

## Try This

Write a report retaining customers with zero qualifying orders and test its total.

## Citations

- https://www.postgresql.org/docs/current/tutorial.html
