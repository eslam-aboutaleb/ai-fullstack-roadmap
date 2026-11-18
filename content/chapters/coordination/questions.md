<!-- chapter: coordination -->

# Why does sync need more than the basic ingestion pipeline?

<!-- meta
domain: backend
subdomain: coordination
module: coordination
concept: Why does sync need more than the basic ingestion pipeline
difficulty: implementation
misconception_target: A database lock coordinates across all services
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Sync reconciles a changing collection over repeated scans and distributed workers. It must classify document changes, track active generations, prevent stale activation, manage removals, checkpoint progress, and clean abandoned writes. A one-shot replace operation does not cover all of those concerns.

## Spoken Summary

Multi-worker synchronization needs durable ownership, bounded admission, idempotent revision handling and crash recovery beyond a sequential ingestion loop. Leases can expire while work continues; fencing is useful only if the storage/effect receiver rejects stale tokens. An outbox and row claiming solve different boundaries.

## Why

A sync coordinator composes source scans, manifests, fencing state, embeddings, vector storage, optional reconciliation jobs, and garbage collection. It prepares generations before committing visibility through manifests.

## Production Case

Worker A pauses until its lease expires; B acquires the job and writes revision 8. A resumes with an older fencing token. The authoritative receiver must reject A rather than trusting its expired local lease.

## Risk

The coordinator's logic depends on durable adapters implementing atomic fencing and batch compare-and-swap. The provided in-memory implementations demonstrate semantics within a process, not a production multi-process coordination service.

## Trade-off

The richer protocol improves recoverability while adding state and adapter obligations. Small single-process applications may reasonably use the simpler pipeline.

## Try This

Compare the state required to replace one file with the state required to sync a million-object collection across two workers and intermittent source failures.

## Execution Timeline

Worker claims row with SKIP LOCKED → Acquires lease → Processes task → Writes outbox events → Commits → Releases lease

## Complexity

Claim latency depends on the eligible queue range, index plan, skipped locked rows and contention. Leases/fencing/outbox add durable reads and writes; none implies constant-time or exactly-once execution.

## Definitions

- **Lease**: Time-limited exclusive right to process a resource
- **Fencing token**: Monotonically increasing token that rejects stale writers
- **Outbox**: Table that stores events to publish after database commit
- **SKIP LOCKED**: SQL clause that skips rows locked by other transactions

## Alternatives

- Distributed lock service (Redis, etcd)
- Message queue with competing consumers

## Pitfalls

- Lease expiry during long tasks
- Fencing token not checked on write
- Outbox events not published atomically

## Follow-ups

### Does a lease by itself prevent stale writes?

No. A paused worker can continue after expiry. Enforce fencing or version predicates where the write actually commits.

## Example

> Explanation: Claim an available task row without waiting for locks held by other workers.
> Output: One task row claimed by this worker

```python
SELECT * FROM tasks WHERE status = 'pending' ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED;
```

## Citations

- https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html

# What are leases and fencing tokens, and why are both needed?

## Answer

A lease grants temporary ownership; a fencing token is a monotonically increasing epoch that lets authoritative storage reject obsolete owners. A worker can pause beyond its lease and later resume, so merely checking lease time before a write is insufficient.

## Why

A sync-state repository provides lease acquisition, renewal, token validation, and a fenced commit context. The coordinator validates tokens after preparation and performs activation inside the fenced context.

## Risk

A stale worker may already have written prepared vectors, but it must not activate them or overwrite checkpoints. Correctness depends on checking authority at the authoritative mutation boundary, not only in worker memory.

## Trade-off

Fencing requires shared durable state and atomic enforcement. A simple expiring lock is easier to implement but vulnerable to resumed zombie workers.

## Try This

Pause worker A, expire its lease, let B acquire a newer epoch, then resume A. Identify every operation A may still perform and every authoritative write that must reject it.

# Why does a separate token check followed by a write still race?

## Answer

Another worker can take ownership after the check and before the write. This is a time-of-check to time-of-use race. The authority check and authoritative mutation need one protected context or equivalent atomic database condition.

## Why

The a sync-state repository protocol explicitly requires fenced() to exclude takeover while committing. A production adapter can use transactional row locking, advisory locking, or equivalent compare-and-swap semantics; a no-op context is not sufficient.

## Risk

Implementing validate_token correctly but fenced incorrectly creates false confidence. Unit tests that never interleave takeover with commit will miss the race.

## Trade-off

Holding a guard during activation can increase contention. Keep expensive embedding outside it and protect only the necessary visibility and checkpoint operations.

## Try This

Write an interleaving with a successful token check, a takeover, and an obsolete write. Then show which atomic guard makes that history impossible.

# What does compare-and-swap do for manifest activation?

## Answer

Compare-and-swap updates state only if its current version matches the expected version. It detects that another operation changed the document while new content was being prepared. Batch compare-and-swap applies the intended set without a partially updated manifest snapshot.

## Why

The coordinator records expected fences, prepares vectors, and calls compare_and_swap_many during activation. Readers use a manifest snapshot to validate which generation and chunk IDs are visible.

## Risk

A loop of individually successful per-document swaps is not equivalent to an atomic batch when collection consistency is required. Adapter contracts must make the promised visibility semantics real.

## Trade-off

Batch atomicity simplifies reader consistency while placing stronger demands on durable storage. Per-document activation permits partial progress with weaker whole-collection simultaneity.

## Try This

Simulate two prepared updates where one expected fence is stale. Verify that a batch failure does not leave only the other document activated.

# How do document and collection activation modes differ?

## Answer

Document mode can activate successful document updates even when another document fails preparation. Collection mode aims to avoid publishing a partially prepared collection and advances collection-generation state after activation. They express different consistency and availability choices.

## Why

The coordinator's preparation loop records errors; collection mode raises on preparation failure, while document mode can continue. The activation path updates manifests and collection state under the supplied coordination contracts.

## Risk

Cross-store atomicity is not created automatically by selecting collection mode. Durable adapters must preserve the fenced and batch visibility obligations, including failure between manifest commit and generation advancement.

## Trade-off

Collection consistency can delay fresh data because one bad document blocks a run. Document mode improves partial availability while exposing mixed document update times.

## Try This

Make one of three documents fail embedding. Compare reports and visible generations in both modes and state which behavior your product requires.

# How do metadata-only changes avoid unnecessary re-embedding?

## Answer

If content and embedding-relevant processing remain unchanged, a metadata update can reuse stored vectors while writing records with new metadata. This saves provider work without pretending that all changes are harmless to vector identity.

## Why

Sync plans distinguish metadata_only updates. The coordinator fetches existing embeddings by active chunk IDs and passes them into preparation instead of calling the embedder again for that case.

## Risk

Misclassifying a semantic preprocessing change as metadata-only reuses invalid vectors. Missing stored vectors also need an explicit failure path rather than silently substituting arbitrary values.

## Trade-off

This optimization reduces cost but requires accurate fingerprints and a fetch-capable backend. Re-embedding everything is simpler and more expensive.

## Try This

Change a display title, then change chunker configuration, then change an access field. Explain which changes can reuse vectors and which still require immediate authorization updates.

# How does a synchronous retrieval adapter protect against stale and tombstoned vectors?

## Answer

It asks the backend for scoped active candidates, oversamples, reads a manifest snapshot, and rejects results whose document is absent or non-active, whose generation differs, or whose chunk ID is not in the active manifest. Physical presence is not sufficient for visibility.

## Why

This read-time gate decouples authorization and active-state checks from eventual vector cleanup. It also checks returned metadata rather than trusting that every backend filter was honored perfectly.

## Risk

Its finite oversampling can still return fewer than the requested number of valid hits. Also, callers using the raw store bypass this protection, so integration must preserve the intended reader path.

## Trade-off

Additional manifest reads and filtering improve consistency while adding latency and possible underfilling. A stronger backend-native visibility index could reduce that overhead but needs equivalent guarantees.

## Try This

Insert old-generation, tombstoned, wrong-scope, and valid records. Verify which survive and show a case where oversampling still cannot fill final_k.

# What is the transactional outbox pattern, and what must the host implement?

## Answer

The outbox writes a job in the same transaction as the application change it represents. A separate worker later processes that job. This prevents a committed business change from losing its intended background work because a process crashed before sending an external message.

## Why

A durable job repository and a job processor are host-implemented contracts. enqueue behavior with a supplied session must join the caller's transaction; protocol documentation describes safe claiming, including SKIP LOCKED semantics for a SQL implementation.

## Risk

A separate job insert after commit is not a transactional outbox. Likewise, the sync coordinator's optional reconciliation enqueue should not automatically be described as atomic with every remote vector write.

## Trade-off

An outbox adds polling, retries, and retention but avoids fragile dual writes. It still requires idempotent processing because a crash can cause a job to run again.

## Try This

Draw crashes before business commit, after commit, and after processing but before completion marking. Explain how an outbox avoids lost work while permitting duplicate processing.

# Does SKIP LOCKED provide exactly-once job execution?

## Answer

No. It helps concurrent SQL workers claim different available rows without waiting on already locked rows. A worker can still finish external work and crash before recording completion, causing a later retry to repeat that work.

## Why

The job system tracks status, attempts, lock ownership, and stale-job reclamation. These mechanisms support recovery, while the processor must ensure repeated execution has safe logical effects.

## Risk

Reclaiming too early can overlap a still-running worker; never reclaiming can strand jobs forever. Production adapters must enforce ownership on completion and failure transitions, not just during initial selection.

## Trade-off

At-least-once processing is practical with idempotent writes and fencing. Claiming exactly-once behavior across unrelated external services would require a much stronger design.

## Try This

Make the processor succeed, then simulate failure in completion marking. Run reclamation and show that the second execution does not duplicate the application's intended effect.

# How do shutdown, retries, checkpoints, and garbage collection work together?

## Answer

The drainer checks for stale jobs, processes pending work, survives failed passes, and uses a stop event for shutdown. Sync cancels heartbeats, releases leases, and cleans retired or uncommitted vectors in a finally path. Checkpoints record committed progress under the example token.

## Why

These are recovery mechanisms for different lifetimes: process shutdown, task execution, authority ownership, and storage cleanup. A completion report alone cannot replace all of them.

## Risk

Cleanup can itself fail, and process termination may prevent finally blocks from running. Durable reconciliation must discover leftovers on a later run; a successful logical activation should not be undone by deleting committed IDs as abandoned work.

## Trade-off

Conservative cleanup leaves temporary storage overhead while protecting visible data. Aggressive deletion reduces space and can make recovery unsafe.

## Try This

Build a crash matrix for preparation, vector write, manifest activation, checkpoint, and cleanup. For each point identify visible state and the next repair action.

# Why can a lock lease expire while its worker is still performing a write?

<!-- meta
domain: backend
subdomain: coordination
module: coordination
concept: Why can a lock lease expire while its worker is still performing a write?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: Worker A pauses, its lease expires, worker B writes the new state, then A resumes and overwrites it.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A lease bounds ownership in time; it cannot stop a paused or partitioned worker from resuming later. Use a receiver-enforced generation or fencing token when stale writers must be rejected. Keep operation identity and idempotency separate from lock ownership, and test pause, expiry and restart behavior.

Concrete engineering case: Worker A pauses, its lease expires, worker B writes the new state, then A resumes and overwrites it.

Boundary defense: It sacrifices recovery and still does not establish receiver authority under every failure. Choose bounded leases plus a stale-write rejection contract where needed.

## Spoken Summary

A lease bounds ownership in time; it cannot stop a paused or partitioned worker from resuming later. Use a receiver-enforced generation or fencing token when stale writers must be rejected. Keep operation identity and idempotency separate from lock ownership, and test pause, expiry and restart behavior.

## Why

A lease bounds ownership in time; it cannot stop a paused or partitioned worker from resuming later. Use a receiver-enforced generation or fencing token when stale writers must be rejected. Keep operation identity and idempotency separate from lock ownership, and test pause, expiry and restart behavior.

## Production Case

Worker A pauses, its lease expires, worker B writes the new state, then A resumes and overwrites it.

## Risk

Worker A pauses, its lease expires, worker B writes the new state, then A resumes and overwrites it.

## Trade-off

It sacrifices recovery and still does not establish receiver authority under every failure. Choose bounded leases plus a stale-write rejection contract where needed.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: coordination**: A lease bounds ownership in time; it cannot stop a paused or partitioned worker from resuming later.

## Alternatives

- It sacrifices recovery and still does not establish receiver authority under every failure. Choose bounded leases plus a stale-write rejection contract where needed.

## Pitfalls

- Worker A pauses, its lease expires, worker B writes the new state, then A resumes and overwrites it.

## Follow-ups

### Will extending every lease indefinitely solve the problem?

It sacrifices recovery and still does not establish receiver authority under every failure. Choose bounded leases plus a stale-write rejection contract where needed.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "Worker A pauses, its lease expires, worker B writes the new state, then A resumes and overwrites it.",
  "required_decision": "A lease bounds ownership in time; it cannot stop a paused or partitioned worker from resuming later"
}
```

## Citations

- https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/

# When does multi-agent research help, and how do you keep agents from duplicating or contradicting each other?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: coordination
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Decompose into genuinely separable work.** Parallel agents can help when each subtask has a distinct evidence set and can return a compact, verifiable artifact. If every agent needs the full shared history or edits the same transaction, coordination can dominate the work. First compare against ordinary parallel tool calls and a single agent with the same total budget.

**Define contracts before fan-out.** Assign a task identifier, scope, allowed sources, deadline, token budget and expected result schema. Each result should contain claims, citations, uncertainty and unresolved questions. The supervisor tracks ownership and rejects duplicate assignments or unsupported conclusions. Keep a shared artifact index rather than broadcasting every transcript to everyone.

**Treat synthesis as a real stage.** The supervisor checks source overlap, incompatible definitions, timestamps and conflicting claims. Majority vote does not establish truth when agents use the same incorrect source. Preserve disagreements and reopen decisive primary evidence. Limit the amount of returned text so synthesis itself fits the context budget.

**Account for end-to-end cost.** Parallel execution can shorten wall time but increases total tokens and tool calls. Reserve budget for synthesis and verification before spawning workers. Cancel outstanding work when the root task is canceled or its budget expires. A worker's late result should not revive a completed task. Measure success per dollar and tail latency, including failed and redundant branches.

## Why

Three agents research three countries using separate public sources. They return structured findings with dates. A supervisor discovers that two use different definitions of revenue and resolves that before comparing results; three fluent paragraphs alone would hide the mismatch.

## Worked Case

Three agents research three countries using separate public sources. They return structured findings with dates. A supervisor discovers that two use different definitions of revenue and resolves that before comparing results; three fluent paragraphs alone would hide the mismatch.

## Risk

Uncontrolled fan-out multiplies cost and propagates correlated errors while appearing more thorough.

## Trade-off

Parallelism helps independent breadth; tightly coupled sequential reasoning often favors one shared stateful workflow.

## Try This

Compare one agent, parallel tool calls and three agents under the same total budget. Include overlapping assignments and conflicting source dates.

## Citations

- https://www.anthropic.com/research/multi-agent-research-system

# Why must a background worker commit ownership before releasing its row-selection locks?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: coordination
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Selection and ownership are separate operations unless the transaction joins them.** A query using row locks can select available jobs without waiting on rows another transaction holds. Those row locks disappear when the transaction ends. Returning selected rows to application code does not extend their database lock lifetime.

**Choose a coherent claiming protocol.** One option selects eligible jobs and changes their state to processing in the same transaction, then commits before performing network work. Another uses conditional updates as the actual arbitration: multiple workers may discover the same candidate, but only an update whose eligibility predicate still matches acquires it. The worker must process only rows that its update actually returned. A local list of selected identifiers is not proof of ownership.

**Include all eligibility conditions in the arbitration boundary.** A retry job may not be due yet, may have exhausted attempts or may have been canceled after discovery. Check those conditions atomically when claiming rather than trusting an earlier snapshot. Stamp an owner and attempt generation, and return that generation to the worker. Keep the transaction short; the provider call should happen after commit rather than while a database row lock remains held for minutes.

**Account for fairness and recovery.** Skipping locked jobs improves competing-consumer throughput, but it is not a fairness or exactly-once guarantee. Track the oldest pending age, cap attempts and reclaim abandoned work through a defined lease protocol. The SQLite example demonstrates the compare-and-set predicate under a sequential competing-claim schedule; it does not implement PostgreSQL's skip-locked scheduling.

## Why

Workers A and B both discover job 7. A changes pending to processing and commits. B must observe zero rows affected and skip execution. If both process their original discovery lists, two provider calls occur.

## Worked Case

Workers A and B both discover job 7. A changes pending to processing and commits. B must observe zero rows affected and skip execution. If both process their original discovery lists, two provider calls occur.

## Risk

Treating a released selection lock as durable ownership permits duplicate execution. Reclaiming a job also requires stale-completion protection.

## Trade-off

Atomic batch claiming reduces contention; small claims limit the amount of work stranded when one worker crashes.

## Try This

Draw the select/commit/update interleaving for two workers, then identify exactly which statement decides ownership.

## Follow-ups

### Should a claim transaction include the embedding call?

Usually avoid that: network latency would extend lock duration and consume database connections. Commit a durable lease first and make the subsequent work replay-safe.

### What if claiming 100 jobs takes longer than one lease?

Size batches by realistic processing capacity, use renewal where appropriate and limit prefetch. A large claimed backlog can expire before a worker even starts its later jobs.

## Citations

- https://www.postgresql.org/docs/current/sql-select.html
- https://www.sqlite.org/lang_transaction.html

# How do you reject a stale worker result after its job has been reclaimed?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: coordination
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Lease expiration is permission to recover work, not evidence that the original process stopped.** A paused worker may wake after another worker has taken ownership. Both can still hold valid network connections. Checking the lease only before a slow operation leaves a time-of-check/time-of-use gap.

**Issue a new attempt generation on each claim.** Store a monotonically increasing generation or another unambiguous attempt identifier with the owner. Completion, failure and renewal transitions must match the job identifier, current owner, current generation and expected processing state. A stale worker gets zero affected rows and must discard its result rather than overwrite the current status.

**Fence every authoritative write.** Guarding the job table does not protect an external vector index if the stale worker has already overwritten a newer vector. Use generation-qualified vector identities and publish only the current generation, or enforce a conditional version rule at the destination. Where the destination cannot validate versions, isolate writes into immutable attempts and arbitrate visibility through an authoritative pointer.

**Handle late failure as carefully as late success.** A timed-out worker must not mark a newly completed job failed or reset its retry schedule. Keep attempt-specific diagnostic events separately from the current job state. Use clock assumptions for lease expiry explicitly; generation checks provide write ordering without depending on the old worker's local clock. The example executes a real SQL completion predicate and proves that a previous generation cannot commit job completion.

## Why

Attempt 4 pauses during embedding. Attempt 5 reclaims the job and finishes. Attempt 4 later returns a vector and must not replace attempt 5 data or mark its completed job failed.

## Worked Case

Attempt 4 pauses during embedding. Attempt 5 reclaims the job and finishes. Attempt 4 later returns a vector and must not replace attempt 5 data or mark its completed job failed.

## Risk

Owner names alone are insufficient when one process name can be reused across attempts. Unconditional completion updates undo recovery guarantees.

## Trade-off

Immutable attempt outputs simplify fencing across services but add cleanup work and transient storage.

## Try This

Inject a pause after the old worker starts its provider call, reclaim the job and resume the old worker after the new one completes. Check destination data as well as job status.

## Follow-ups

### Are heartbeat timestamps enough?

Heartbeats help detect likely abandonment, but a delayed writer can still return. Use timestamps for liveness decisions and a current attempt predicate for authoritative writes.

### Can the stale provider call be canceled reliably?

Cancellation is best effort across process and network boundaries. Correctness must survive a late response even when cancellation fails.

## Citations

- https://www.postgresql.org/docs/current/sql-select.html
- https://www.sqlite.org/lang_transaction.html

# How do you commit a business change and its notification intent atomically?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: coordination
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**The invariant is about intent, not immediate delivery.** If a business transaction commits, the durable notification intent should exist; if it rolls back, neither the state change nor its intent should remain. Insert the outbox row using the caller's transaction rather than opening a separate session that commits independently.

**Keep network delivery outside the business transaction.** Calling an email or push provider before commit can notify users about a change that later rolls back. Calling it after commit without a durable intent leaves a crash window where the change survives but no notification is ever sent. The outbox bridges that window by committing the change and intent together, then letting a worker deliver later.

**Record enough stable context.** Include event identity, business-object identity, event type, payload schema version, recipient scope and occurrence time. Decide whether rendering uses a snapshot of event facts or queries current state. Querying current state for a historical event can accidentally announce a later status instead of the transition that occurred. Minimize sensitive payloads and enforce retention.

**Define event identity at the transition.** Duplicate client requests or repeated state-machine execution should not create multiple logical notifications for one transition. Use an event identifier or a uniqueness constraint consistent with the business semantics; two different transitions on the same object may both need notifications. The SQLite example performs a real rollback and proves that the business update and outbox insertion disappear together.

## Why

A service changes a task from pending to approved and inserts its notification intent. A validation failure before commit must leave the task pending and the outbox empty, even though both SQL statements already ran.

## Worked Case

A service changes a task from pending to approved and inserts its notification intent. A validation failure before commit must leave the task pending and the outbox empty, even though both SQL statements already ran.

## Risk

An outbox helper that commits its own session breaks atomicity with the business change.

## Trade-off

The outbox adds delivery lag and worker operations while preserving a recoverable record of what must be sent.

## Try This

Crash before commit, after commit and during delivery. Identify the durable state and safe recovery action at each point.

## Follow-ups

### Should an outbox row say delivered when it is inserted?

No. It records pending intent. Delivery status changes only when the worker has sufficient evidence of the destination outcome.

### Can the outbox contain a pointer rather than the full payload?

Yes, if the referenced event data is durable, versioned and available throughout retries. A pointer to mutable current state may lose the historical event facts.

## Citations

- https://www.sqlite.org/lang_transaction.html
- https://www.postgresql.org/docs/current/transaction-iso.html

# How do leases, fencing and clock assumptions prevent a recovered worker from corrupting newer work?

<!-- meta
answer_format: conceptual
domain: backend
subdomain: coordination
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A lease limits how long a worker may claim ownership, but a paused worker may resume after its lease expires. Fencing uses a monotonically ordered ownership token checked atomically at the protected write boundary to reject the old worker. A separate pre-write check is not enough because ownership can change immediately after it. Define the clock authority, renewal rules and destination enforcement. If the destination cannot enforce fencing, the design needs another scoped exclusion or version policy.

## Why

Worker A pauses, B obtains a newer lease and writes current state, then A resumes. The destination must reject A's lower fence even if A still believes it owns the job.

## Worked Case

Worker A pauses, B obtains a newer lease and writes current state, then A resumes. The destination must reject A's lower fence even if A still believes it owns the job.

## Risk

Process-local locks cannot coordinate independent replicas or fence stale writers.

## Trade-off

Leases improve recovery only with enforcement where protected state changes.

## Try This

Pause an owner past expiry and demonstrate rejection of its delayed write.

## Citations

- https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/
