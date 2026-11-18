<!-- chapter: database-concurrency -->

# How does SELECT FOR UPDATE prevent duplicate confirmation?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: database-concurrency
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**In PostgreSQL, SELECT FOR UPDATE locks selected rows until transaction end.** A confirmation transaction selects the owner-scoped request row, checks pending status while holding its lock, writes confirmation/outbox state and commits. A second concurrent caller waits for the lock, then must inspect the current row and return the existing confirmation rather than repeat the effect. Under other isolation levels it may instead need a serialization retry. Locking an absent row does not lock a future matching insert; use a unique owner/idempotency constraint for creation. A conditional UPDATE with RETURNING can be a simpler alternative when its predicate captures the whole invariant.

**A transaction protects a declared invariant over authoritative state.** Begin by naming the business rule: one confirmation per request, one effect per owner/operation or one projection update with its checkpoint. A read-then-write sequence is not automatically safe when two clients can read the same old state. Use uniqueness, conditional updates, locks or an appropriate isolation level and handle their actual conflict behavior.

A typed HTTP request improves representation, but runtime validation and object-level authorization still belong at the service boundary. Derive owner from trusted identity, scope reads/writes by that owner and reject changed material payload under a reused idempotency key. A successful network response is not the only possible committed outcome: the database can commit before the acknowledgment is lost. Reconciliation must use stable business identity rather than creating a new operation on every retry.

The CDC contract commits document mutation, consumed-event digest and checkpoint together. The support project commits ticket, run state and audit event together. Their fault tests abort the final write and verify the earlier writes roll back. These are local atomicity examples because all state shares one SQLite database. They do not imply atomicity across PostgreSQL, a message broker and an external tool provider; that boundary needs outbox/inbox patterns, receiver deduplication or explicit reconciliation.

Consistency is a product decision, not simply choosing a database label. An eventually updated search index may lag source truth, so source eligibility must still be checked when resolving sensitive citations. An owner-sharded key avoids collisions but cannot enforce a cross-owner global invariant without coordination. Test concurrent confirmation, duplicate/changed replay, rollback, stale reads and access revocation. Explain which invariant the transaction protects and which remaining side effects lie outside it before claiming the workflow is safe.

## Why

An injected failure occurs while saving the checkpoint after a document update. The transaction rolls back both, so replay sees neither a falsely advanced cursor nor an untracked mutation.

## Worked Case

An injected failure occurs while saving the checkpoint after a document update. The transaction rolls back both, so replay sees neither a falsely advanced cursor nor an untracked mutation.

## Risk

Two individually correct services can disagree after partial failure. Calling each operation idempotent does not prove their combined business workflow is atomic.

## Trade-off

Stronger coordination simplifies some invariants but increases contention and availability costs. Eventual projections can scale reads when stale-data and source-validation policies are explicit.

## Try This

Run the CDC and support fault suites. Draw every transaction boundary and identify the first external effect that could not participate in that same commit.

## Follow-ups

### Can a client timeout be interpreted as a failed transaction?

No. The commit may have succeeded before the reply was lost. Look up the original owner/operation identity and reconcile authoritative state; a fresh write with a new identity can duplicate the business action.

## Citations

- https://www.sqlite.org/lang_transaction.html
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://www.postgresql.org/docs/current/explicit-locking.html

# What is the difference between flush, commit, and rollback?

## Answer

Flush sends pending ORM changes to the transaction, allowing generated identities and database constraints to be observed. Commit makes the transaction's successful changes durable. Rollback discards its transactional changes. Flushed data is not therefore committed, and another session's visibility depends on isolation.

## Why

Flush exposes transactional changes and constraint errors without committing. Keep one owner for commit and rollback so nested services cannot partially finalize a larger business operation.

## Risk

Catching a database exception and continuing with the same failed transaction can produce further errors. A swallowed exception is not a successful recovery; rollback or a correctly scoped savepoint is needed.

## Trade-off

Caller-owned transactions permit atomic composition but require explicit ownership. Helpers that commit themselves are easier in isolation and unsafe inside larger workflows.

## Try This

Inject failure after the service request flush but before the final commit. Inspect all related tables from another session after rollback.

# What does PostgreSQL Read Committed mean for an application workflow?

<!-- meta
reference: https://www.postgresql.org/docs/current/transaction-iso.html
-->

## Answer

Ordinary statements see committed state as of each statement's snapshot, so two reads in one transaction can observe intervening commits. A transaction boundary alone does not make a sequence of business decisions appear serial. Locking or conditional updates must protect the relevant invariant.

## Why

Under Read Committed, separate statements may observe different committed snapshots. Protect a multi-statement invariant with appropriate constraints, locks, or guarded updates instead of assuming one stable view.

## Risk

A pattern that reads pending, calls external work, then updates completed can race under ordinary concurrency. Shared data snapshots and write authority are different properties.

## Trade-off

Stronger isolation can reduce anomalies while increasing retries and contention. It does not eliminate the need for idempotent external effects.

## Try This

Reproduce a changing read in two sessions, then compare a locked confirmation and a conditional UPDATE. Record actual transaction settings.

# When would optimistic concurrency control be useful?

## Answer

Optimistic control updates a row only when its version or prior state matches what the caller observed. A zero-row update signals a conflict. It suits edits where collisions are uncommon and a caller can reload rather than hold a lock during long user interaction.

## Why

Include the expected version in the update predicate and require exactly one affected row. On conflict, reload state and revalidate intent before deciding whether retry is safe.

## Risk

Checking a version in Python and then issuing an unconditional update is not optimistic concurrency control. The comparison and mutation must be one database operation.

## Trade-off

Short conditional writes reduce waiting but require conflict handling. Row locks can be simpler for a small critical transition with many related writes.

## Try This

Write a versioned update for a hypothetical claim note. Make two editors submit the same expected version and verify only one succeeds.

# How does job selection differ from durable job ownership?

## Answer

A selection transaction can return candidate IDs and then release its locks. If acquisition happens later, a guarded update and its returned rows establish which worker owns each job. Alternatively, select and claim atomically in one transaction. Inspect the full lifecycle before asserting exclusive ownership.

## Why

If candidate selection ends its transaction before acquisition, a later conditional update establishes ownership. Alternatively, claim atomically in one transaction; inspect the whole lifecycle before asserting exclusivity.

## Risk

Describing selection alone as exclusive ownership hides a race and encourages unsafe future changes. Completion and reclamation also need ownership-aware conditions to prevent obsolete workers from overwriting newer outcomes.

## Trade-off

Split selection and guarded claiming compose with the generic protocol but require more careful reasoning. One atomic claim statement can simplify the implementation at the cost of adapter-specific SQL.

## Try This

Interleave two workers between selection and marking. Verify the loser receives no processing payload for the contested job.

# Why is one AsyncSession per concurrent task important?

<!-- meta
reference: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
-->

## Answer

AsyncSession represents mutable transactional and ORM state. Independent concurrent operations should use independent sessions rather than sharing one session inside asyncio.gather. An async driver does not make one transaction object safe for arbitrary concurrent use.

## Why

Create an independent AsyncSession per independently concurrent transaction. Bound database concurrency separately from provider calls and avoid sharing mutable ORM state across unrelated async tasks.

## Risk

Sharing can cause state errors, unintended transaction coupling, or unpredictable query sequencing. Creating too many sessions instead can exhaust the pool, so concurrency also needs a bound.

## Trade-off

Separate sessions allow independent I/O while consuming additional connections and potentially observing different snapshots. Sequential queries on one session are easier when one consistent transaction is required.

## Try This

Compare concurrent reads with separate sessions and sequential reads with one session. Measure pool checkout waits and document the required consistency model.

# Can persistent ADK session state still suffer lost updates?

## Answer

Yes. Persistence retains state but does not automatically merge concurrent updates. If two workers read one version, modify different fields, and overwrite the whole JSON object, the later write can discard the earlier change.

## Why

Choose session serialization, optimistic versions, or explicit field-level merge semantics. Test two stale readers changing different fields; durable storage alone does not protect against a lost update.

## Risk

An append-only event record can survive while the latest state loses another turn's field. Sequence numbers also do not prove the model saw a serial conversational history.

## Trade-off

Per-session turn serialization improves consistency and reduces same-conversation throughput. Delta updates or optimistic versions offer alternatives with their own conflict policy.

## Try This

Load the same session twice, apply different state keys concurrently, and inspect both the event log and final state.

# Why is the Redis idempotency claim a best-effort mechanism rather than exactly-once execution?

## Answer

The claim has a finite TTL, waiters stop waiting after a bounded time, and Redis outages permit local execution. A slow winner can still run while another replica gives up and recomputes. The claim value is not a durable operation result or a fencing token for a business write.

## Why

A short-lived Redis lease can reduce duplicate model work while expiring during a slow call. Use an owner token with checked release, and enforce business idempotency through a durable operation key in the authoritative database.

## Risk

An obsolete worker can delete or overwrite a newer lease if ownership is not checked. Duplicate model calls may add cost; repeated business writes require a separate durable protection.

## Trade-off

Best-effort deduplication improves responsiveness. Stronger operation state requires ownership tokens, durable result identity, and explicit timeout/retry semantics.

## Try This

Make a model turn outlast the service request TTL and waiter deadline. Count model executions separately from durable business effects.

# How should deadlocks, lock timeouts, and serialization failures be handled?

<!-- meta
reference: https://www.postgresql.org/docs/current/explicit-locking.html
-->

## Answer

Acquire shared resources in a consistent order, keep transactions short, bound waiting, and retry only the whole appropriate transactional unit when the database reports a retryable conflict. Reusing a partially failed session or blindly retrying external effects is unsafe.

## Why

Classify database errors and retry only an entire safely repeatable transaction under a bounded deadline. Preserve the business operation key and avoid retrying partial side effects blindly.

## Risk

Retrying a transaction can repeat already-sent emails or model calls if they occur inside the unit. Outbox writes let the database retry without repeating external delivery synchronously.

## Trade-off

Retries improve recovery while increasing tail latency. An overloaded system needs admission control, not only more retry attempts.

## Try This

Create a two-row opposite-order locking exercise in a disposable database. Record the failure class and retry the complete unit with a bounded policy.

# How do you test concurrency without relying on random sleeps?

## Answer

Use controlled barriers or events to pause workers at known boundaries, then force a specific interleaving. Assert durable state and ownership outcomes, not only response codes. Use a real PostgreSQL instance for lock and isolation service requests.

## Why

Use barriers or explicit synchronization to control the interleaving. Assert final rows and operation outcomes after takeover, duplicate confirmation, deadlock recovery, and stale-worker completion attempts.

## Risk

A test that runs two coroutines on one session may test an invalid integration rather than a real race. An in-memory SQLite database cannot establish PostgreSQL row-lock semantics.

## Trade-off

Deterministic integration tests take setup but produce stronger evidence and fewer flaky timing assumptions. Broad stress tests complement them and do not replace them.

## Try This

Specify barriers for two confirmations, two job service requests, and two session-state updates. State the invariant each test could falsify.

# How do ORMs implement the Unit of Work and Identity Map patterns, and how do they detect and flush changes to the database?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Modern Object-Relational Mappers (ORMs like SQLAlchemy and Hibernate) coordinate database interactions through two fundamental architectural patterns: the Identity Map and the Unit of Work.** Without these patterns, interacting with relational tables via object-oriented code results in duplicated in-memory entity representations, out-of-order SQL emissions, and fragmented transaction management.\n\n**The Identity Map pattern.** The Identity Map maintains an in-memory dictionary mapping primary keys to loaded object instances within the lifecycle of a single session: `session.identity_map[(User, 42)] = user_instance`. If a query requests user ID 42 multiple times during a transaction (e.g., across distinct functions or service layers), the ORM intercepts the call and returns the exact same in-memory object reference.

This prevents entity duplication, eliminates redundant database SELECT queries for already-loaded rows, and guarantees that in-memory mutations remain consistent across the application.\n\n**The Unit of Work pattern and dirty checking.** The Unit of Work acts as a transaction-scoped buffer that tracks all newly created (`new`), modified (`dirty`), and marked-for-deletion (`deleted`) objects. When an application modifies attributes on a model, the ORM intercepts the change via descriptor instrumentation. When `session.flush()` or `session.commit()` is invoked, the Unit of Work: (1) Examines snapshots to compute exact column-level diffs; (2) Performs a topological sort of all pending INSERT, UPDATE, and DELETE operations based on foreign key dependency graphs; and (3) Emits minimal, batched SQL statements to the database, ensuring foreign key constraints are never violated during execution.

## Why

A service updates a user's email in function A and adds an order in function B. Without the Unit of Work, function A would immediately issue an un-batched SQL UPDATE. With Unit of Work, both operations are batched and flushed together in a single atomic transaction.

## Worked Case

A service updates a user's email in function A and adds an order in function B. Without the Unit of Work, function A would immediately issue an un-batched SQL UPDATE. With Unit of Work, both operations are batched and flushed together in a single atomic transaction.

## Risk

Keeping long-lived ORM sessions open across multiple HTTP requests bloats the Identity Map, consuming excessive RAM and causing stale in-memory reads.

## Trade-off

Unit of Work defers SQL execution until flush, improving network batching and foreign key ordering while requiring developers to remember that Python attribute changes are not instantly persisted.

## Try This

Inspect `session.dirty` and `session.new` in SQLAlchemy after modifying model attributes. Call `session.flush()` and verify with SQL logging when the UPDATE statement is emitted.

## Follow-ups

### What is the difference between flush() and commit() in an ORM session?

flush() emits SQL queries to the database transaction buffer without committing; commit() emits flush() and then issues the final COMMIT instruction to finalize the transaction.

## Citations

- https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- https://martinfowler.com/eaaCatalog/unitOfWork.html

# What is the N+1 Query Problem in ORMs, how does it manifest in production, and how do joinedload, selectinload, and subqueryload solve it?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**The N+1 Query Problem is the most pervasive performance defect in ORM-driven applications, turning a single logical data fetch into dozens or hundreds of sequential database queries.** It occurs when an application queries a list of N parent entities and subsequently accesses a related child collection configured with default lazy loading. The ORM executes 1 initial query to retrieve the N parent rows, followed by N separate, sequential queries to fetch the children for each individual parent (1 + N total network round-trips), causing massive database connection pool saturation, latency spikes, and severe CPU contention.\n\n**Three distinct Eager Loading strategies in SQLAlchemy 2.0.** To eliminate lazy-loading waterfalls, modern ORMs provide three explicit eager-loading strategies, each engineered for specific relational topologies: (1) `joinedload()`: Executes an SQL `LEFT OUTER JOIN` in a single combined query.

It is optimal for 1-to-1 relationships and many-to-one foreign key lookups. However, applying joinedload to one-to-many or many-to-many collections creates Cartesian product row duplication, transferring massive redundant data over the network; (2) `selectinload()`: Executes exactly two queries: `SELECT * FROM parents` followed immediately by `SELECT * FROM children WHERE parent_id IN (1, 2, ..., N)`. It completely avoids Cartesian product row duplication, making it the premier strategy for 1-to-many collections in PostgreSQL; and (3) `subqueryload()`: Executes two queries using an SQL subquery (`WHERE parent_id IN (SELECT id FROM parents ...)`), useful when parent IDs cannot be listed in an IN clause.

## Why

An API endpoint lists 50 customer accounts with their recent orders. Under lazy loading, loading the page executes 51 SQL queries, taking 1,800ms. Applying `selectinload(Account.orders)` reduces the execution to exactly 2 queries, dropping latency to 28ms.

## Worked Case

An API endpoint lists 50 customer accounts with their recent orders. Under lazy loading, loading the page executes 51 SQL queries, taking 1,800ms. Applying selectinload(Account.orders) reduces the execution to exactly 2 queries, dropping latency to 28ms.

## Risk

Applying joinedload across multiple nested one-to-many collections causes a Cartesian explosion of rows returned, exhausting web worker memory.

## Trade-off

Eager loading eliminates round-trip query waterfalls at the cost of fetching related collections upfront even if some code paths do not read them.

## Try This

Enable SQLAlchemy SQL echo logging (`echo=True`). Query 10 parent records with lazy loading vs `selectinload`. Count the exact number of SQL statements emitted to the console.

## Follow-ups

### Can linters or tests automatically detect N+1 queries in CI pipelines?

Yes. Libraries like nplusone or custom query-counter fixtures in pytest track database statement counts per API endpoint, asserting that query counts remain constant regardless of dataset size.

## Citations

- https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html
- https://docs.sqlalchemy.org/en/20/orm/loading_relationships.html

# How should SQLAlchemy AsyncSession and connection pools be managed in FastAPI to prevent cross-request session leakage and pool starvation?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Managing asynchronous database sessions in high-concurrency Python web frameworks requires strict session lifecycle scoping and carefully calibrated connection pools.** In asynchronous frameworks like FastAPI running on Uvicorn, multiple concurrent HTTP requests execute cooperatively on a single-threaded asyncio event loop. If database sessions or connections are mismanaged, applications suffer from cross-request data leaks, concurrency race conditions, and connection pool starvation.\n\n**The Session-Per-Request pattern via Dependency Injection.** An AsyncSession must never be instantiated as a global or module-level variable. Global sessions cause concurrent coroutines to interleave operations on the same session instance, corrupting transaction state and throwing `InvalidRequestError: Object is already attached to session`.

The production standard is the session-per-request pattern implemented via FastAPI dependencies with async context managers: `async def get_db(): async with async_session_maker() as session: try: yield session; await session.commit() except Exception: await session.rollback(); raise`. This guarantees that every request receives its own isolated session and transaction boundary that closes deterministically even on unhandled exceptions.\n\n**Connection pool sizing and anti-starvation rules.** The underlying engine connection pool (e.g., using asyncpg) must be sized according to: `Total Connections = (Uvicorn Workers * (pool_size + max_overflow)) < PostgreSQL max_connections`. A frequent cause of connection pool starvation is holding a database transaction open while awaiting a slow external HTTP API call or long LLM completion. Production systems mandate that external network I/O must never occur inside an active database transaction; commit or close the database session before invoking third-party APIs.

## Why

A developer places an OpenAI API call inside an open database transaction. When the LLM takes 12 seconds to stream a response, all 20 connection pool slots are held open waiting on the LLM, starving all incoming user login requests and crashing the API.

## Worked Case

A developer places an OpenAI API call inside an open database transaction. When the LLM takes 12 seconds to stream a response, all 20 connection pool slots are held open waiting on the LLM, starving all incoming user login requests and crashing the API.

## Risk

Holding database connections while awaiting slow external network calls rapidly exhausts database connection pools, taking down the entire application.

## Trade-off

Strict session-per-request scoping requires dependency injection boilerplate on every route, but completely eliminates concurrency race conditions and connection leaks.

## Try This

Simulate 50 concurrent requests hitting a FastAPI route that forgets to close its session in an error branch. Observe the pool exhaustion error `TimeoutError: QueuePool limit of size 5 overflow 10 reached`.

## Follow-ups

### What is the greenlet requirement in SQLAlchemy asyncio?

SQLAlchemy uses greenlet under the hood to bridge its synchronous core execution engine with the asyncio event loop, requiring greenlet binary wheels to be installed.

## Citations

- https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- https://fastapi.tiangolo.com/tutorial/sql-databases/

# How does Optimistic Concurrency Control work in ORMs using version columns, and when is it preferred over Pessimistic Locking?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Optimistic Concurrency Control (OCC) and Pessimistic Locking represent two opposing concurrency control strategies with contrasting scalability, throughput, and contention characteristics.** When multiple users or processes concurrently attempt to modify the same database entity (e.g., updating inventory stock or booking an appointment slot), the system must prevent lost updates and race conditions.\n\n**Pessimistic Locking (SELECT ... FOR UPDATE).** Pessimistic locking assumes conflicts are frequent. It instructs the database engine to acquire an exclusive row-level lock immediately upon reading the row: `SELECT * FROM inventory WHERE id = 1 FOR UPDATE`. Any other concurrent transaction attempting to read or update that row is blocked and queued until the holding transaction commits. While safe, pessimistic locking has major drawbacks: it degrades throughput under high concurrency, creates high lock contention, and risks database deadlocks if multiple rows are locked in inconsistent orders across transactions.\n\n**Optimistic Concurrency Control via version columns.** OCC assumes conflicts are rare.

It avoids taking database locks during read time, instead adding an integer version counter to the table: `version_id = Column(Integer, default=1)`. When updating, the ORM generates conditional SQL: `UPDATE inventory SET stock = :new_stock, version_id = version_id + 1 WHERE id = :id AND version_id = :original_version`. If a concurrent transaction updated the row in the interim, the version number has incremented; the WHERE clause matches zero rows, and the ORM immediately raises `StaleDataError`. The application catches the exception and cleanly retries or informs the user. OCC is vastly superior for read-heavy workloads, stateless REST APIs, and workflows involving user think-time.

## Why

In an e-commerce checkout, 50 users view the last concert ticket. Pessimistic locking locks the row for 10 minutes while User 1 fills out payment details, blocking all other users. OCC allows all users to browse; only the final submit checks the version column, rejecting concurrent checkouts safely.

## Worked Case

In an e-commerce checkout, 50 users view the last concert ticket. Pessimistic locking locks the row for 10 minutes while User 1 fills out payment details, blocking all other users. OCC allows all users to browse; only the final submit checks the version column, rejecting concurrent checkouts safely.

## Risk

In extremely high-contention write workloads (e.g. flash sales with 10,000 writes/sec to a single row), OCC causes massive retry loops and high abort rates.

## Trade-off

OCC eliminates database lock queuing and deadlocks at the cost of requiring application-level retry logic when `StaleDataError` is raised.

## Try This

Add a `version_id` column to a SQLAlchemy model with `__mapper_args__ = {version_id_col: version_id}`. Open two sessions, modify the same record in both, and commit the second to observe `StaleDataError`.

## Follow-ups

### Can timestamps be used as version columns instead of integers?

Yes, but integer version counters are preferred because system clocks can experience drift, NTP adjustments, or identical timestamp collisions during sub-millisecond concurrent writes.

## Citations

- https://docs.sqlalchemy.org/en/20/orm/versioning.html
- https://en.wikipedia.org/wiki/Optimistic_concurrency_control

# How do SQL Transaction Isolation Levels differ in PostgreSQL MVCC, and what anomalies occur in each?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Transaction isolation levels define the mathematical guarantees that prevent concurrent transactions from observing or interfering with each other's uncommitted or intermediate states.** In PostgreSQL, isolation is implemented via Multi-Version Concurrency Control (MVCC): rows are never overwritten in place; instead, row updates create new tuple versions stamped with `xmin` (creating transaction ID) and `xmax` (deleting transaction ID). Readers never block writers, and writers never block readers.\n\n**The three operational isolation levels and their anomalies.** The ANSI SQL standard defines four isolation levels, which PostgreSQL implements across three concrete tiers: (1) Read Committed (default): Every individual query within the transaction takes a fresh snapshot of committed data. It prevents Dirty Reads (reading uncommitted changes), but permits Non-Repeatable Reads (executing the same SELECT query twice yields different values if another transaction commits an update in between) and Phantom Reads (new rows inserted by another committed transaction appear in a second query); (2) Repeatable Read: The entire transaction takes a single immutable snapshot at the start of its first query.

It prevents Dirty Reads, Non-Repeatable Reads, and Phantom Reads. However, it permits Write Skew: two concurrent transactions check an overlapping constraint (e.g. ensuring at least one doctor remains on call), each modifying a different row; both commit successfully, leaving zero doctors on call; and (3) Serializable: The strictest level, implemented via Serializable Snapshot Isolation (SSI). It tracks read-write antidependencies (SIREAD locks) in memory; if a cycle is detected, the database aborts the transaction with `ERROR: 40001 could not serialize access`, requiring an application retry.

## Why

Two hospital dispatchers concurrently take Doctor A and Doctor B off call. Under Repeatable Read, both check `SELECT count(*) WHERE on_call=true` (returns 2). Both transactions update one doctor to false and commit, leaving zero doctors on call. Under Serializable, the second commit fails with a serialization error.

## Worked Case

Two hospital dispatchers concurrently take Doctor A and Doctor B off call. Under Repeatable Read, both check SELECT count(*) WHERE on_call=true (returns 2). Both transactions update one doctor to false and commit, leaving zero doctors on call. Under Serializable, the second commit fails with a serialization error.

## Risk

Running all application transactions under Serializable without automated retry middleware causes frequent 40001 database aborts to bubble up as 500 errors to end users.

## Trade-off

Serializable guarantees absolute mathematical correctness and eliminates all concurrency anomalies, but introduces transaction aborts and memory tracking overhead.

## Try This

Open two psql shells. Begin transactions in both with `SET TRANSACTION ISOLATION LEVEL REPEATABLE READ`. Update opposite rows based on an intersecting premise and observe Write Skew.

## Follow-ups

### Why doesn't PostgreSQL support Read Uncommitted?

PostgreSQL's MVCC architecture naturally isolates uncommitted tuples via xmin/xmax transaction visibility checks; supporting dirty reads would require deliberately bypassing core MVCC guarantees.

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html
- https://wiki.postgresql.org/wiki/SSI

# How do Distributed Locks with Redis work, and why can GC pauses or network partitions break lock exclusivity?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Distributed locks coordinate mutual exclusion across independent processes that share no physical memory, but are susceptible to timing assumptions in asynchronous networks.** In a single Redis instance, a safe distributed lock is acquired using the atomic command: `SET resource_name client_uuid NX PX 30000`, which sets the key only if it does not exist (`NX`), bound to an automatic 30-second expiry (`PX`). Releasing the lock requires a Lua script that verifies the `client_uuid` matches before deleting the key, preventing a process from inadvertently deleting a lock held by another worker.\n\n**The Redlock algorithm across multi-node clusters.** To survive single-node Redis failures, the Redlock algorithm acquires the lock across N independent Redis masters (typically N = 5). The client attempts to acquire the lock on all nodes sequentially with a small timeout. If the client acquires the lock on a majority (at least 3 nodes) within a total time less than the validity duration, the lock is granted.\n\n**The fatal GC pause vulnerability (Martin Kleppmann's critique).** Distributed locks that rely on wall-clock lease expiry fail in asynchronous distributed systems due to Stop-The-World (STW) pauses. Consider: Worker 1 acquires a lock with a 10-second TTL.

Immediately after acquisition, Worker 1 experiences a 15-second GC pause, OS swapping delay, or network stall. While Worker 1 is paused, its 10-second lease expires in Redis. Worker 2 requests and acquires the lock. Worker 1 wakes up from its GC pause, assumes it still owns the lock, and issues its write to shared storage. Both workers write concurrently, completely violating mutual exclusion and corrupting data. The only provable defense is Fencing Tokens: monotonically increasing numbers validated by the underlying storage engine.

## Why

Worker 1 acquires a lock to process a payment batch. A 20-second JVM garbage collection pause stalls Worker 1. Redis expires the lock. Worker 2 acquires the lock and begins charging customers. Worker 1 resumes and also charges customers, double-billing thousands of users.

## Worked Case

Worker 1 acquires a lock to process a payment batch. A 20-second JVM garbage collection pause stalls Worker 1. Redis expires the lock. Worker 2 acquires the lock and begins charging customers. Worker 1 resumes and also charges customers, double-billing thousands of users.

## Risk

Assuming a distributed lock guarantees absolute exclusivity without storage-level fencing tokens allows delayed processes to corrupt production databases.

## Trade-off

Redis distributed locks provide fast, best-effort coordination for non-critical tasks; mission-critical mutations require consensus-backed stores (etcd, Zookeeper) paired with monotonic fencing tokens.

## Try This

Implement a Redis lock in Python with a 2-second TTL. Acquire the lock, call `time.sleep(3)` to simulate a pause, and attempt to write. Confirm that the lock was lost during sleep.

## Follow-ups

### How does a fencing token protect storage from delayed workers?

The storage engine tracks the highest fencing token observed; any write request presenting a token lower than the highest recorded token is rejected as stale.

## Citations

- https://redis.io/docs/latest/develop/use/distlock/
- https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html

# Why can checking an operation key before inserting still create duplicate tasks?

<!-- meta
domain: backend
subdomain: database-concurrency
module: database-concurrency
concept: Why can checking an operation key before inserting still create duplicate tasks?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A read-then-insert race admits two matching requests from concurrent browser retries.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Two transactions can both observe absence before either commits. Enforce identity with a database uniqueness rule and resolve the conflict against stored payload and ownership. Keep state changes and outbox intent in the required transaction. Retrying after a serialization or uniqueness conflict must preserve the logical operation identity.

Concrete engineering case: A read-then-insert race admits two matching requests from concurrent browser retries.

Boundary defense: Reject the conflict or use an explicit new operation contract. Do not silently return an unrelated task as if the payload matched.

## Spoken Summary

Two transactions can both observe absence before either commits. Enforce identity with a database uniqueness rule and resolve the conflict against stored payload and ownership. Keep state changes and outbox intent in the required transaction. Retrying after a serialization or uniqueness conflict must preserve the logical operation identity.

## Why

Two transactions can both observe absence before either commits. Enforce identity with a database uniqueness rule and resolve the conflict against stored payload and ownership. Keep state changes and outbox intent in the required transaction. Retrying after a serialization or uniqueness conflict must preserve the logical operation identity.

## Production Case

A read-then-insert race admits two matching requests from concurrent browser retries.

## Risk

A read-then-insert race admits two matching requests from concurrent browser retries.

## Trade-off

Reject the conflict or use an explicit new operation contract. Do not silently return an unrelated task as if the payload matched.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: database concurrency**: Two transactions can both observe absence before either commits.

## Alternatives

- Reject the conflict or use an explicit new operation contract. Do not silently return an unrelated task as if the payload matched.

## Pitfalls

- A read-then-insert race admits two matching requests from concurrent browser retries.

## Follow-ups

### What if the same key arrives with changed content?

Reject the conflict or use an explicit new operation contract. Do not silently return an unrelated task as if the payload matched.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A read-then-insert race admits two matching requests from concurrent browser retries.",
  "required_decision": "Two transactions can both observe absence before either commits"
}
```

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html
- https://www.postgresql.org/docs/current/explicit-locking.html

# How should an idempotency service order result publication, claim release and conflicting request detection?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Idempotency identifies a logical operation, not merely identical text.** Scope the key to the authenticated principal and operation type, and bind it to a canonical request fingerprint. Reusing one key with changed parameters must produce a conflict instead of replaying an unrelated result. Two intentional identical messages may be different operations, so content hashing alone is not always the correct identity policy.

**Publish the durable result before relinquishing ownership.** A successful worker records its completed result under the operation identity, then releases its coordination claim. Releasing first creates a window in which another replica sees neither a result nor an owner and executes again. Publishing first lets a retry replay the result even if the original process crashes before release.

**Do not overstate what that ordering solves.** A crash after a remote effect but before durable result publication still leaves an unknown outcome. Reconcile with the effect service using the same logical operation identity. A cache lock cannot make a payment, model provider or external write participate in the result-store transaction. For durable effects, the authoritative service needs its own idempotency or reconciliation contract.

**Design expiration and ownership safely.** A time-to-live (TTL) bounds how long a claim remains, but it does not stop its owner from running. Use owner tokens for conditional release and an attempt rule for stale publication. If the result retention expires, document whether the same key is rejected, reconciled or treated as new. The in-memory trace below isolates the release-before-publication race; it is not a distributed-lock implementation.

## Why

A completes work and releases its claim. Before A stores the result, B sees a miss and starts the same operation. Reversing those two steps closes this particular window, but not the earlier remote-effect-versus-result-store crash window.

## Worked Case

A completes work and releases its claim. Before A stores the result, B sees a miss and starts the same operation. Reversing those two steps closes this particular window, but not the earlier remote-effect-versus-result-store crash window.

## Risk

A successful lock acquisition is not an exactly-once effect guarantee. Ignoring body fingerprints can replay a result for changed arguments.

## Trade-off

Longer result retention improves replay safety but increases storage and privacy obligations.

## Try This

Trace crashes before effect, after effect, after result publication and after claim release. State how every retry learns the authoritative outcome.

## Follow-ups

### What if publication succeeds but the response is lost?

A retry with the same operation identity reads the durable result. Return the original outcome rather than invoke the operation again.

### Can an old owner delete a replacement claim?

Only if release is unsafe. Compare the stored ownership token with the releasing token in one atomic backend operation; a plain unconditional delete can remove another worker's lease.

## Citations

- https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/

# What should happen to write requests when distributed idempotency coordination is unavailable?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: database-concurrency
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Classify the operation before choosing a fallback.** A duplicate read or repeated model generation may waste money but leave business state intact. A duplicate settlement, account change or external notification can have a different impact. One generic fail-open rule cannot represent all these outcomes.

**Separate coordination availability from effect safety.** If the authoritative effect service enforces a durable idempotency key, a request may proceed using that contract even while an optional response cache is down. If shared coordination is the only mechanism suppressing duplicate effects, falling back to an in-process dictionary loses cross-replica protection. A local mutex covers one process, not the deployment.

**Use explicit degraded modes.** Permit safe reads with reduced deduplication where acceptable. For writes, either obtain durable protection from the destination, queue an operation intent in a durable transactional store, or reject temporarily with a documented retry policy. Do not acknowledge queued work until its intent is committed. Requests whose previous outcome is unknown should reconcile before starting another effect.

**Expose the loss of guarantees.** Record coordination outages, degraded-mode admission counts and unknown operations using bounded telemetry labels. Communicate pending or unavailable status to the client rather than inventing success. Recovery should reconcile queued intents and completed effects before ordinary traffic assumes the cache is authoritative again. The example is an admission decision table; it validates policy choices rather than simulating an outage or network partition.

## Why

Two replicas receive the same write during a coordination outage. With destination-side durable deduplication both can safely reference the same operation. Without it, local caches cannot prevent duplicate effects, so the application must defer or reject.

## Worked Case

Two replicas receive the same write during a coordination outage. With destination-side durable deduplication both can safely reference the same operation. Without it, local caches cannot prevent duplicate effects, so the application must defer or reject.

## Risk

Silent fallback can preserve HTTP availability while removing the business invariant users rely on.

## Trade-off

Conservative admission lowers availability; destination-enforced operation identities can preserve more availability without trusting a cache.

## Try This

Build a failure matrix for cache outage, destination timeout, result-store outage and network partition. Assign proceed, queue, reconcile or reject to each operation class.

## Follow-ups

### Should a timeout release an operation for immediate retry?

Not if the effect may have happened. Transition to an unknown or reconciling state and ask the destination about the operation identity before deciding whether it is safe to execute.

### Does a longer cache TTL fix the outage?

It changes retention and contention, but does not restore connectivity or provide durable ownership across unavailable replicas.

## Citations

- https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/

# When should a workflow use optimistic version checks instead of a row lock?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: database-concurrency
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Optimistic concurrency includes the version observed by a reader in the update condition and detects a conflicting change through the affected-row result. A row lock serializes access to selected rows while held, but can increase waiting and deadlock risk. Both require an explicit transaction boundary and do not automatically protect a multi-row invariant. Choose based on contention, interaction duration and retry cost. Never hold a database lock while a person reviews a form or a slow external provider responds.

## Why

Two editors read version 5. The first updates it to 6; the second update conditioned on version 5 affects zero rows and should surface a conflict rather than overwrite the accepted change.

## Worked Case

Two editors read version 5. The first updates it to 6; the second update conditioned on version 5 affects zero rows and should surface a conflict rather than overwrite the accepted change.

## Risk

Blind retries can discard user intent or repeat external effects.

## Trade-off

Optimistic checks fit low contention; locks can simplify short contested transitions.

## Try This

Demonstrate a two-editor conflict and a policy for reconciling it.

## Citations

- https://www.postgresql.org/docs/current/transaction-iso.html
- https://www.postgresql.org/docs/current/explicit-locking.html
