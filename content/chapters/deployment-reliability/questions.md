<!-- chapter: deployment-reliability -->

# What must change when scaling from one process to multiple replicas?

<!-- meta
domain: operations
subdomain: reliability
concept: What must change when scaling from one process to multiple replicas
difficulty: foundations
misconception_target: A green deploy means the system is healthy
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Shared sessions, idempotency, rate limits, jobs, migrations, and telemetry need explicit cross-process semantics. Process-local dictionaries, locks, and counters remain local even when replicas run identical code.

## Spoken Summary

Multiple replicas need shared authoritative state, scoped identities, atomic/idempotent operation handling and coordinated schema changes. In-memory tasks and locks do not span processes. Also review connection pools, downstream quotas, health semantics, rollout compatibility and recovery behavior.

## Why

Move authoritative tasks, sessions, rate accounting, and operation identity into deliberately shared stores where required. Test concurrent replicas instead of extrapolating from one process.

## Production Case

A request is accepted by replica A and status polling reaches B. If state is process-local, B reports unknown despite a real accepted task; move authoritative task state to shared durable storage.

## Risk

Adding replicas can multiply quotas, repeat model calls, and split conversational state. A load balancer does not make local state shared.

## Trade-off

Shared services improve continuity and introduce network dependencies. One process with honest limitations can be a simpler initial deployment.

## Try This

Test retries routed to another replica, session continuation, worker claiming, and global quota behavior during Redis failure.

## Execution Timeline

Deploy new version -> Health checks pass -> Gradual traffic shift -> Monitor error rates -> Full rollout or rollback

## Complexity

Readiness probes should be bounded and inexpensive, but deployment cost includes startup, migration locks, mixed-version traffic and capacity headroom. Measure the actual rollout and recovery behavior.

## Definitions

- **Health check**: Endpoint that reports whether an instance can serve traffic
- **Rollout**: Gradual deployment to users with error-rate monitoring
- **Disaster recovery drill**: Practiced procedure for restoring service after failure

## Alternatives

- Big bang deployment
- Blue-green deployment

## Pitfalls

- Health checks pass but business logic broken
- Rollback too slow during incident
- No disaster recovery practice

## Follow-ups

### Will a load-balancer sticky session fix durability?

It may mask routing symptoms temporarily, but process loss, scaling and background workers still require shared recoverable state.

## Example

> Explanation: Unhealthy instances are removed from traffic and on-call is alerted.
> Output: Instance drained, alert sent

```python
if health_check() == unhealthy:
    remove_from_load_balancer(instance)
    alert_oncall()
```

## Citations

- https://sre.google/sre-book/

# Should migrations run on every application startup?

<!-- meta
domain: operations
subdomain: reliability
module: deployment-reliability
concept: Should migrations run on every application startup
difficulty: implementation
misconception_target: A successful deploy means the system is healthy
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

Startup migration is convenient for small deployments but couples readiness to schema changes and can make replicas compete to migrate. A controlled migration job followed by compatible application rollout is an alternative.

## Spoken Summary

Run migrations as an explicit, serialized release operation with reviewed locking and compatibility behavior. Avoid every replica racing to change schema at startup. Use expand/migrate/contract phases so old and new replicas can coexist, and rehearse rollback limits for destructive changes.

## Why

Give one deployment step ownership of reviewed migrations and deploy compatible application versions. Define upgrade failure and rollback behavior before enabling multiple startup processes.

## Production Case

Twenty replicas start after a rollout and all attempt one large schema rewrite. A migration job with a single ownership boundary, staged compatibility and measured lock behavior avoids the startup stampede.

## Risk

Concurrent DDL, long locks, and destructive changes can affect all replicas. A schema change can also prevent rollback to the prior image.

## Trade-off

Self-initializing services reduce manual steps; dedicated migration stages improve sequencing. Either requires tested failure behavior and appropriate database privileges.

## Try This

Design a rolling deployment with one migrator, compatible schema, application rollout, verification, and delayed cleanup.

## Execution Timeline

Review migration -> expand schema -> deploy compatible code -> backfill/verify -> retire old code -> contract schema

## Complexity

Runtime and locking depend on the specific DDL, engine version, table size and access pattern. Measure representative migrations and define failure/recovery behavior.

## Definitions

- **Migration owner**: The single coordinated release operation responsible for a schema change.
- **Expand/contract**: A staged transition that preserves compatibility before removing old fields or interfaces.
- **Rollback limit**: State or external changes that an application-image rollback cannot automatically undo.

## Alternatives

- Big bang deployment
- Blue-green deployment

## Pitfalls

- Health checks pass but business logic broken
- Rollback too slow during incident
- No disaster recovery practice

## Follow-ups

### Is application-image rollback enough after a destructive migration?

No. Old code may no longer understand the schema or lost data. Plan compatibility and restore/reconciliation before applying the migration.

## Example

> Explanation: This is an ordering fixture, not a database migration tool or proof that a real DDL operation has no locking cost.
> Output: contract only after verification

```python
release_steps = ['expand', 'compatible_code', 'backfill', 'verify', 'contract']
assert release_steps.index('verify') < release_steps.index('contract')
print('contract only after verification')
```

## Citations

- https://www.postgresql.org/docs/current/explicit-locking.html
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

# Why does startup ingestion need separate operational treatment?

## Answer

Ingestion performs provider calls and writes unrelated to accepting a web request. Running it during every replica startup can duplicate preparation, delay readiness, and couple scaling to source and model availability.

## Why

Run ingestion as a versioned background workflow with freshness state, deduplication, deadlines, and retry policy. Avoid repeating expensive source preparation on each replica startup.

## Risk

A service can start successfully with missing knowledge. Database connectivity does not prove usable policy evidence exists.

## Trade-off

Startup ingestion suits a sample corpus; a scheduled or operator-triggered worker gives clearer ownership, progress, and recovery.

## Try This

Start two replicas with an unchanged source, then with an unavailable provider. Report effective readiness, freshness, and duplicate preparation.

# What does the minimal health endpoint prove?

## Answer

A bounded database probe establishes only that a basic connection and query worked at that moment. It does not prove model availability, current evidence, healthy workers, correct permissions, or functioning event delivery.

## Why

Separate process liveness, dependency readiness, index freshness, and task-quality signals. Bound probes and avoid costly model calls on every health check.

## Risk

Calling this fully healthy can conceal an assistant unable to answer or index. Putting expensive evaluations in every probe can instead overload the service.

## Trade-off

Cheap probes suit frequent checks. Readiness and scheduled consistency checks should cover critical product dependencies separately.

## Try This

Define probe outcomes for database failure, provider failure, stale corpus, and a stopped embedding worker.

# How should connection pools and worker concurrency be sized together?

## Answer

Count API requests, background jobs, agent-session writes, migrations, and probes that need connections. Bound concurrency and pool waits so one workload cannot consume all capacity. Async I/O does not remove database connection limits.

## Why

Multiply pool limits by processes and replicas, then reserve database headroom for workers and operations. Bound simultaneous queries separately from model or HTTP concurrency.

## Risk

Increasing replicas can exceed the total connection budget. Provider waits inside open transactions amplify occupancy even when CPU usage is low.

## Trade-off

Larger pools reduce local waiting until database saturation; smaller pools protect the database and need admission control.

## Try This

Calculate connections across replicas and workers, reserve operational headroom, and measure pool checkout latency under load.

# How should container and dependency hardening be evaluated?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: deployment-reliability
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**A deployable artifact is more than source code that once ran locally.** Build a reproducible image from pinned dependencies, record its immutable digest and provenance, run with minimal privileges, and separate configuration/secrets from the image. A tag can move; a Git commit alone does not pin transitive packages, base images or build-time downloads. Scan the actual release artifact and retain enough metadata to reproduce or replace it.

Infrastructure as code (IaC) declares resources and change history, but applying it can still destroy data or expose a service. Review the plan, permissions, state storage, rollback/recovery and environment isolation. Map cloud concepts before naming products: compute runs code, object storage stores blobs, identity limits actions, network policy controls paths and managed databases own durable state. AWS-specific choices such as IAM roles, ECS/EKS, S3 or RDS change operational responsibility and cost; they do not remove authorization or backup duties.

Kubernetes schedules containers and reconciles desired state. A Deployment rolling update needs resource requests, readiness, availability/surge limits and a progress deadline. Readiness controls traffic eligibility; liveness can restart an unhealthy process. A remote provider outage should not cause every replica to restart through a badly designed liveness check. A stalled rollout reports failure; rollback is an explicit operational decision, not automatic evidence that the old version is healthy.

The workbench includes a non-root Dockerfile, a two-replica manifest and a disposable-kind failure/undo exercise. Those commands are optional learner activities until actual runtime output is recorded. This authoring environment has no working Docker daemon, so neither image execution nor cluster recovery is claimed. The local release gate checks digest shape, schema compatibility and recovery evidence, while real browser/API tests exercise the service outside a container. Keep those observations separate. Inject secrets only at runtime through a scoped mechanism, avoid logging them and test rotation/revocation without rebuilding the image.

## Why

An image tag points to new bytes although the application commit is unchanged. Recording the image digest and dependency locks makes the release identity inspectable; a manifest alone cannot prove the workload actually started.

## Worked Case

An image tag points to new bytes although the application commit is unchanged. Recording the image digest and dependency locks makes the release identity inspectable; a manifest alone cannot prove the workload actually started.

## Risk

A liveness probe tied to a provider outage can restart every replica and worsen the incident. Broad cloud credentials in a build image turn artifact access into infrastructure access.

## Trade-off

Managed services reduce some maintenance but add service constraints and cost. Kubernetes offers orchestration flexibility with significant operational overhead; a simpler container service may fit the workload better.

## Try This

Review the workbench Dockerfile and manifest, then follow the disposable-kind exercise only on an available local engine. Record rollout and undo output, or clearly mark execution unperformed rather than substituting YAML validation.

## Follow-ups

### Can rolling back the application safely reverse a destructive database migration?

No. Artifact rollback and data recovery are separate. Use compatible expand/contract migrations, verified backups and a rehearsed forward repair; restoring deleted or incompatible state can create new correctness and privacy failures.

## Citations

- https://docs.docker.com/build/building/best-practices/
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html

# How should worker shutdown and stale-job recovery be verified?

## Answer

Stop accepting new work, allow bounded completion, release resources, and use durable job state for later recovery. A finally block helps graceful shutdown but cannot be guaranteed after abrupt process death.

## Why

Stop accepting new work, allow or cancel active operations under a deadline, persist state, and recover stale leases safely. Verify shutdown through controlled worker interruption.

## Risk

Reclaiming too early overlaps workers; never reclaiming strands jobs. A crash after external delivery but before completion marking can repeat delivery.

## Trade-off

Graceful draining improves continuity and slows replacement. Abrupt replacement is faster and demands stronger recovery invariants.

## Try This

Terminate a worker after claim, after embedding, and after delivery. Verify the next worker converges without duplicate logical effects.

# How should an external provider outage affect the product?

## Answer

Distinguish unavailable generation, unavailable embeddings, failed retrieval, and degraded tracing. Preserve committed business state and expose retryable status. Do not fabricate policy answers or report unperformed actions as successful.

## Why

Classify affected capabilities and provide explicit degraded outcomes. Apply bounded retries and circuit or admission policies without generating unsupported answers when evidence or tools are unavailable.

## Risk

Nested retries can exhaust pools and budgets. Switching providers can change tool and privacy behavior and must be an explicit evaluated policy.

## Trade-off

Structured status lookup can preserve useful service while generation is unavailable. Full-availability service requests are inappropriate when essential evidence is missing.

## Try This

Define an outage matrix for PostgreSQL, Redis, embedding, generation, and tracing, with permitted operations and recovery behavior.

# What is a meaningful disaster-recovery drill?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: deployment-reliability
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**A recovery drill demonstrates restoration of a usable invariant, not merely the existence of a backup file.** Define recovery point objective (RPO), the acceptable data-loss interval, and recovery time objective (RTO), the acceptable restoration duration. State the reference event/time and workload. A green backup job says data was copied; it does not show decryption keys, schema compatibility, permissions, deletion intent or application behavior survived restoration.

Prepare a runbook with symptom, impact, owner, safe containment, diagnostic evidence and decision points. For an AI assistant, separate service errors, latency, unsupported answers, false refusals, source freshness, unauthorized access and cost amplification. Correlate safe request/attempt/operation IDs across UI, API, data and model calls. Keep secrets and raw private prompts out of default telemetry. A provider outage may require degraded read-only behavior or explicit refusal rather than a restart storm.

Restore into an isolated environment, verify integrity and business invariants, reapply deletion/revocation events newer than the snapshot, then test source eligibility and repeat-safe effects before allowing traffic. Measure elapsed recovery and actual recovered point; do not report planned RTO/RPO as achieved. A rollback may restore software while leaving incompatible data or stale model/index artifacts, so rehearse those coupled changes.

The workbench README provides optional container/cluster failure and explicit undo steps; local restore and rollout fixtures supply smaller reproducible exercises. A system-design defense should include a sequence diagram, capacity assumptions, failure timeline, proposed mitigation and observed validation. Keep the postmortem focused on the mechanism and prevention: for example, an owner-switch UI race, a stale policy cache or a changed-payload CDC replay. Cost and latency improvements cannot overrule critical disclosure or unsupported business decisions. Separate executed local evidence from infrastructure commands awaiting a suitable learner environment.

## Why

A backup restores an old document that was deleted after the snapshot. Integrity checks pass, but serving it violates current deletion intent; replaying tombstones before traffic is a required recovery step.

## Worked Case

A backup restores an old document that was deleted after the snapshot. Integrity checks pass, but serving it violates current deletion intent; replaying tombstones before traffic is a required recovery step.

## Risk

Restoration can resurrect private data or duplicate effects even when files are intact. A runbook that checks only HTTP 200 misses the important business invariants.

## Trade-off

Frequent backups improve possible RPO but add cost and retention obligations. Automated restoration reduces delay only when safety checks and access/deletion reconciliation are also automated and tested.

## Try This

Run restore_drill.py and write an incident timeline for a resurrected policy. State measured recovery versus target objectives and show the gate that prevents traffic before deletion reconciliation.

## Follow-ups

### What if telemetry itself contains the deleted document?

Treat telemetry as another retention/deletion surface. Minimize sensitive content, scope access and document purge/backup behavior separately; deleting the primary row does not erase logs or exported traces.

## Citations

- https://sre.google/sre-book/managing-incidents/
- https://opentelemetry.io/docs/security/handling-sensitive-data/

# What evidence supports a production-readiness claim?

<!-- meta
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Production readiness is a traceable claim about particular failure scenarios and observed environments.** Source code, a Helm manifest, Dockerfile or green unit-test badge is evidence of *intent* and some checked invariants, not proof that a service will survive a region outage, database restoration, model quality drift or a critical tenant isolation attack. Name the target operating envelope, customers, security boundary, model/data versions, expected throughput and recovery objectives before deciding what to test.

**Frontend boundary.** A React streaming chat interface must prevent stale network responses from an old request or authenticated user appearing in the new session. Use a request/epoch identity in UI state, cancellation on account switch/unmount, bounded render buffers, explicit stream completeness and accessible status. However, hiding a private citation in the browser does **not** authorize a server call; read permissions must be enforced at the authoritative API/database/retrieval layer. `labs/stream_session_reducer.cjs` tests the session/epoch reducer and deliberately drops late chunks after switching users.

**Data pipeline boundary.** ETL transforms source bytes; CDC (change data capture) replays versioned changes. To prevent double effects or stale-policy resurrection, atomically couple projected state with the consumed source event ID/checkpoint. Reject gaps, scope operations to the authenticated tenant, and propagate tombstones before reindexing old snapshots. Test restart, replay, changed-payload duplicate, schema incompatibility and deletion. `labs/data_rollout_contract.py` uses real SQLite transactions to verify source ordering, replay, tenant scope, tombstones and gap rejection. It is single-process evidence; an actual Kafka/Beam/database pipeline still requires distributed integration tests.

**Release and rollback.** A credible release manifest identifies the immutable container digest, compatible database/migration/schema revision, model/tokenizer/index and training-data lineage, deployment config and software-bill-of-materials/provenance as applicable. A readiness probe says the pod may serve work; liveness says whether it should be restarted. Neither proves answer correctness. A Kubernetes Deployment can roll back its pod template revision, but reverting container image alone does not reverse an incompatible database migration or stale downstream index. Use staged rollout, SLO/error budget gates, latency p95/p99, task-level evaluation slices, authorization negatives and an independently rehearsed restore.

**Worked failure.** A new retrieval index is deployed with fresh model weights but an older policy snapshot. The application returns HTTP 200 and passes liveness while giving unsupported outdated answers. A release gate should reject the index revision mismatch and missing deletion evidence, then rollback read alias while reconciling tombstones. The toy release-policy function in the local lab validates required digest/schema/recovery fields and compares a supplied rollout error fraction with a declared bound; it is **not** a Kubernetes deployment or live traffic measurement.

**Trade-offs and follow-up.** A static Pages learning site has no production backend or cloud credentials; complex services are downloadable labs. A single-machine test enables repeatability but cannot certify multi-zone durability. **If a successful rollback restores an old snapshot**, verify its deletion high-water mark and replay authorization/tombstones before serving; otherwise a 'successful' recovery can violate privacy.

## Why

Deployment readiness must be supported by exercised source-to-service evidence, not inferred from manifests, unit-test successes or green liveness probes.

## Risk

A polished architecture or passing unit suite can conceal untested runtime behavior. Secure, scalable, and exactly once are service requests requiring specific evidence.

## Trade-off

Readiness work is slower than a demo and establishes a defensible operational contract. A prototype may ship earlier with narrower commitments.

## Try This

Run the stream reducer and SQLite CDC/rollout exercises; intentionally replay a deleted record and explain the difference between mock rollout policy and real Kubernetes recovery.

## Follow-ups

### If a deployment rollback restores an older data snapshot, how can it remain unsafe despite healthy readiness probes?

An older snapshot may restore deleted policies or revoked owner permissions. Verify the data/ACL/tombstone high-water marks, replay authorized CDC events and ensure index/model/schema compatibility before serving; readiness/liveness only check process capability, not domain correctness.

## Citations

- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

# How does PagedAttention eliminate memory fragmentation in LLM serving engines, and how do virtual block tables coordinate parallel sampling and prefix sharing?

<!-- meta
answer_format: conceptual
domain: systems
subdomain: inference
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**PagedAttention applies the operating system concept of virtual memory with paging to LLM KV caches, eliminating internal and external memory fragmentation and increasing serving throughput by 2-4x.** In legacy LLM serving systems (e.g., vanilla Hugging Face Transformers or early FasterTransformer), KV caches were allocated as contiguous memory buffers sized for the maximum possible sequence length (e.g., 2,048 or 4,096 tokens). Because actual generation lengths vary unpredictably, 60-80% of allocated GPU VRAM sat completely unused as internal fragmentation (pre-allocated but never reached) or external fragmentation (differing request lifetimes preventing contiguous allocations), severely limiting batch sizes.\n\n**Logical blocks and physical memory pages.** PagedAttention divides the KV cache of each sequence into fixed-size logical blocks (e.g., 16 or 32 tokens). These logical blocks map to non-contiguous physical memory pages in GPU VRAM managed by a centralized page pool. As an autoregressive request generates tokens, the engine allocates new physical pages on demand, only when the current page fills up.\n\n**Virtual block tables and copy-on-write sharing.** Each active sequence maintains a block table mapping logical block indices to physical page numbers.

This abstraction enables zero-copy memory sharing across requests:\n1. *Parallel sampling / beam search:* When a prompt branches into multiple generation paths, all paths share the identical prompt physical pages in their block tables. Only when a child branch generates distinct tokens does the engine allocate a new page using copy-on-write (CoW) semantics.\n2. *System prompt prefix caching:* Identical system prompts across hundreds of concurrent users share the exact same physical KV cache pages, eliminating redundant compute and freeing gigabytes of VRAM.

## Why

An AI platform serving customer support receives 100 concurrent requests with a shared 1,500-token system prompt. Without PagedAttention, each request duplicates the 1,500-token KV cache, consuming 60GB VRAM and causing out-of-memory crashes. With PagedAttention prefix caching, the system prompt is stored once (600MB), allowing all 100 requests to run concurrently.

## Worked Case

An AI platform serving customer support receives 100 concurrent requests with a shared 1,500-token system prompt. Without PagedAttention, each request duplicates the 1,500-token KV cache, consuming 60GB VRAM and causing out-of-memory crashes. With PagedAttention prefix caching, the system prompt is stored once (600MB), allowing all 100 requests to run concurrently.

## Risk

Selecting a block size that is too small (e.g., 4 tokens) increases block table lookup overhead and GPU kernel launch latency, while a block size that is too large (e.g., 128 tokens) re-introduces internal fragmentation.

## Trade-off

PagedAttention introduces a layer of pointer indirection and custom non-contiguous CUDA attention kernels in exchange for recovering up to 96% of wasted VRAM and enabling radical throughput scaling.

## Try This

Run a vLLM server instance with `--block-size 16` and benchmark serving throughput with `--enable-prefix-caching` on multi-turn conversations versus a naive single-request Hugging Face baseline.

## Follow-ups

### How does PagedAttention handle sequence preemption when GPU memory is exhausted?

When physical pages run out, the engine preempts the lowest-priority request by either recomputing its tokens later or swapping its pages to CPU host RAM.

## Citations

- https://arxiv.org/abs/2309.06180
- https://vllm.ai/

# How does Continuous Batching (iteration-level scheduling) differ from static batching, and how does it prevent early-finishing requests from stalling GPU hardware?

<!-- meta
answer_format: conceptual
domain: systems
subdomain: inference
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Continuous batching (iteration-level scheduling) evicts completed sequences and injects new requests at every single autoregressive token generation step, eliminating the head-of-line blocking that cripples static batching.** In traditional static request-level batching, an inference engine groups $N$ requests together and runs them synchronously. Because generation lengths in generative AI are non-deterministic (one prompt may generate 10 tokens while another generates 1,000 tokens), static batching is forced to wait for the longest sequence in the batch to finish. The short requests finish in milliseconds but remain locked in GPU memory, padded with dummy tokens, while Tensor Cores run at fractional utilization.\n\n**Iteration-level scheduling loop.** Continuous batching (first introduced by Orca and standardized in vLLM and TensorRT-LLM) operates at the granularity of a single forward-pass iteration rather than a full request lifecycle:\n1. *Step start:* The scheduler checks available GPU memory pages and evaluates the current batch of active decoding sequences.\n2.

*New request admission:* If new prompts arrive in the queue and sufficient KV cache pages exist, the scheduler admits their prefill step into the execution schedule.\n3. *Single forward pass:* The model executes one transformer forward pass, generating exactly one token for all active decoding sequences.\n4. *Dynamic eviction & admission:* Any sequence that produces an End-Of-Sequence (`<eos>`) token or reaches max output tokens is immediately finalized and evicted from the batch, freeing its memory pages. Newly queued requests are slotted in without waiting for other requests to complete.\n\n**Throughput and latency gains.** By replacing coarse request boundaries with fine-grained iteration boundaries, continuous batching eliminates GPU idle time and achieves 10x to 20x higher token throughput compared to naive static batching under realistic multi-user workloads.

## Why

A customer API receives a mix of 50-token classifications and 1,000-token summaries. Under static batching of size 16, a single summary stalls 15 classification responses for 15 seconds. Continuous batching evicts the 15 classifications in 400ms and immediately admits new incoming queries.

## Worked Case

A customer API receives a mix of 50-token classifications and 1,000-token summaries. Under static batching of size 16, a single summary stalls 15 classification responses for 15 seconds. Continuous batching evicts the 15 classifications in 400ms and immediately admits new incoming queries.

## Risk

High prefill arrival rates can starve ongoing decoding requests (prefill starvation), causing Time-To-First-Token (TTFT) to degrade Time-Between-Tokens (TBT) if prefill and decode phases are not prioritized.

## Trade-off

Continuous batching introduces complex dynamic scheduling state machines and memory fragmentation challenges (solved by PagedAttention), but is mandatory for cost-effective multi-tenant LLM serving.

## Try This

Simulate a discrete event queue comparing static batching vs iteration-level batching with Poisson arrival times and Pareto-distributed response lengths. Measure average latency and GPU compute efficiency.

## Follow-ups

### What is the difference between compute-bound prefill and memory-bound decode?

Prefill processes all prompt tokens in parallel (compute-bound, high FLOP utilization); decode generates one token at a time per request (memory-bandwidth-bound, low FLOP utilization).

## Citations

- https://www.usenix.org/conference/osdi22/presentation/yu
- https://vllm.ai/

# How do Chunked Prefill and Preemptions balance prompt prefill latency (TTFT) against token generation smoothness (ITL/TBT) under heavy server load?

<!-- meta
answer_format: conceptual
domain: systems
subdomain: inference
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Chunked Prefill breaks large prompt prefill computations into smaller token chunks, co-scheduling prefill chunks alongside ongoing decode steps to prevent Time-Between-Token (TBT) latency spikes.** In standard LLM inference, the *prefill phase* (processing the input prompt) is compute-heavy and processes all prompt tokens in parallel via large matrix multiplications. The *decode phase* (generating subsequent tokens autoregressively) is memory-bandwidth-bound, processing only one token per stream per step.\n\n**The interference problem.** When a user submits an 8,000-token document, computing the full prefill occupies the GPU's Tensor Cores for several hundred milliseconds. If an engine prioritizes this prefill, all existing concurrent streams experience an abrupt pause in token streaming, causing noticeable stutter (inter-token latency / ITL spikes) for users reading generated output in real time.\n\n**Chunked Prefill mechanism.** Instead of processing an 8,000-token prompt in a single monolithic forward pass, the engine splits the prompt into fixed chunks (e.g., 512 tokens). In each iteration, the scheduler pairs a 512-token prefill chunk with the current batch of single-token decodes.

This achieves two major benefits:\n1. *Bound on iteration latency:* Every forward pass takes a predictable, bounded duration (e.g., 25ms), keeping user streaming smooth without perceptible stalls.\n2. *Compute saturation:* Adding a 512-token prefill to memory-bound decode steps raises overall compute utilization (FLOPs), converting wasted memory-bound clock cycles into productive prompt processing.\n\n**Preemption strategies.** When sudden bursts of concurrent traffic exceed the total physical KV cache page pool, the scheduler must gracefully resolve memory pressure. Rather than crashing with an OOM error, the engine triggers *preemption*: it selects a low-priority or newly started request, evicts its KV cache pages back to CPU system RAM (swapping) or completely discards its generated tokens (recomputation), preserving the execution integrity of requests nearing completion.

## Why

A medical chat service handles doctor queries. While Dr. A is reading an active streaming diagnosis, Dr. B uploads a 10-page medical record. Without chunked prefill, Dr. A's stream freezes for 800ms. With chunked prefill, Dr. A experiences continuous 30-token/sec streaming while Dr. B's document is prefilled in chunks.

## Worked Case

A medical chat service handles doctor queries. While Dr. A is reading an active streaming diagnosis, Dr. B uploads a 10-page medical record. Without chunked prefill, Dr. A's stream freezes for 800ms. With chunked prefill, Dr. A experiences continuous 30-token/sec streaming while Dr. B's document is prefilled in chunks.

## Risk

Recomputing preempted requests during prolonged overload cascades into throughput collapse, as the server repeatedly re-executes prefills without finishing decodes.

## Trade-off

Chunked prefill slightly increases total Time-To-First-Token (TTFT) for very large documents, in exchange for guaranteeing strict Service Level Objectives (SLOs) on Inter-Token Latency (ITL) across all concurrent users.

## Try This

Configure vLLM with `--enable-chunked-prefill --max-num-batched-tokens 512`. Send concurrent long-prompt and streaming-decode requests using a load testing tool, and measure p99 inter-token latency.

## Follow-ups

### What is Sarathi-Serve and how did it pioneer chunked prefill?

Sarathi-Serve demonstrated that piggybacking prefill chunks onto memory-bound decode batches 'piggybacks' compute onto unused memory bandwidth with almost zero latency penalty.

## Citations

- https://arxiv.org/abs/2308.16369
- https://arxiv.org/abs/2401.08671

# How does Speculative Decoding accelerate LLM inference, and how do speculative draft models and target model verification guarantee lossless mathematical equivalence?

<!-- meta
answer_format: conceptual
domain: systems
subdomain: inference
difficulty: advanced design scenario
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-24
-->

## Answer

**Speculative Decoding accelerates autoregressive inference by using an inexpensive draft model to propose candidate tokens speculatively, verifying them in parallel with the large target model in a single forward pass.** Autoregressive decoding is bottlenecked by GPU memory bandwidth: generating 1 token requires loading all weights of a massive model (e.g., 70 billion parameters) from HBM into SRAM, achieving only a tiny fraction of peak Tensor Core arithmetic throughput.\n\n**The Speculative workflow.** Speculative decoding decouples token generation into two cooperating components:\n1. *Draft phase:* A small, ultra-fast draft model (e.g., a 1B parameter model or an early-exit head) generates $K$ candidate tokens sequentially ($x_{t+1}, \dots, x_{t+K}$). Because the draft model is tiny, generating these $K$ tokens is 5-10x faster than the large model.\n2. *Verification phase:* The large target model (e.g., 70B parameters) evaluates all $K$ candidate tokens simultaneously in a single, parallel forward pass.

In matrix operations, computing logits for $K$ tokens in parallel takes virtually the same time as computing logits for 1 token because it shifts the execution from memory-bound to compute-bound.\n\n**Lossless modified rejection sampling.** To guarantee that the output distribution is mathematically identical to sampling directly from the target model without approximation, speculative decoding applies modified rejection sampling. For each candidate token $x$, if the target model probability $p(x) \ge q(x)$ (the draft probability), the token is accepted. If $p(x) < q(x)$, the token is accepted with probability $p(x)/q(x)$. If rejected, the token is discarded, a new token is sampled from the adjusted distribution $\max(0, p(x) - q(x))$, and subsequent speculative candidates are pruned.\n\n**Speedup factor.** If the acceptance rate is high (e.g., 75-85% on structured coding or reasoning tasks), each forward pass of the target model yields 2 to 4 validated tokens instead of 1, resulting in a 2x-3x end-to-end wall-clock latency speedup with zero quality degradation.

## Why

A code completion engine needs sub-50ms latency. Serving an unassisted 70B model yields 25 tokens/sec. Adding a 1B draft model with speculative decoding achieves an 80% acceptance rate on code syntax, boosting generation speed to 70 tokens/sec without changing any token probability distribution.

## Worked Case

A code completion engine needs sub-50ms latency. Serving an unassisted 70B model yields 25 tokens/sec. Adding a 1B draft model with speculative decoding achieves an 80% acceptance rate on code syntax, boosting generation speed to 70 tokens/sec without changing any token probability distribution.

## Risk

Serving a draft model whose vocabulary or tokenizer does not match the target model causes token mismatch errors and prevents validation.

## Trade-off

Speculative decoding achieves 2x-3x speedup on low-concurrency latency-sensitive streams, but consumes extra GPU memory to host both models and yields diminishing returns when the server is already compute-saturated under massive batch loads.

## Try This

Run speculative decoding in Hugging Face Transformers using `AutoModelForCausalLM` with `prompt_lookup_decoding` or an assistant model on a Python coding benchmark. Compare generation latency and token acceptance counts.

## Follow-ups

### What is Medusa and how does it perform speculative decoding without a separate draft model?

Medusa adds multiple lightweight feed-forward heads on top of the target model's final hidden state to predict multiple future tokens simultaneously, eliminating the need to load a second model.

## Citations

- https://arxiv.org/abs/2211.17192
- https://arxiv.org/abs/2302.01318

# How do you use circuit breakers and bulkheads in a RAG service without weakening security?

<!-- meta
domain: ai-rag
subdomain: reliability
module: deployment-reliability
concept: circuit breaker and fail-closed degradation
difficulty: security
misconception_target: Falling back to a simpler path is always safe when a dependency fails
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-29
-->

## Answer

**Circuit breaker.** It wraps calls to a dependency and tracks failures. Closed: calls pass through. Open: after a failure threshold, calls are rejected or redirected immediately, protecting the dependency and the caller's latency. Half-open: after a cooldown a limited number of trial calls test recovery; success closes the breaker, failure reopens it. Without it, a timing-out reranker adds its full timeout to every request and consumes worker capacity.

**What may degrade.** Optional quality stages can be bypassed: skip the reranker and return first-stage ordering, skip query expansion, or use a cached embedding. Document the degraded mode in the response metadata and metrics so quality monitors see it.

**What must never degrade.** Authorization, tenant filtering and data-governance checks. If the authorization service is unreachable, the safe behaviour is to fail closed with an error. In the example, the authorization step runs first and raises when unavailable, so no candidate is returned; the reranker breaker opens after two failures and later calls skip it.

**Bulkhead isolation.** Separate resource pools prevent one workload from exhausting shared capacity: independent queues and worker pools for interactive search and ingestion, per-tenant concurrency limits, separate database connection pools and provider quotas. A large batch import then cannot stall live questions.

**Operational details.** Use an injected clock for deterministic tests, emit metrics for state transitions, set the failure threshold and cooldown from observed dependency behaviour, and combine with timeouts, bounded retries with jitter and request-level deadlines. Retries without a breaker amplify load during outages.

## Spoken Summary

A circuit breaker stops calling a failing dependency after repeated errors, then probes for recovery after a cooldown. For optional stages like a reranker, I open the breaker and degrade to first-stage results. A bulkhead gives workloads separate pools so batch ingestion cannot starve interactive queries. The rule is that degradation must preserve correctness and security: if authorization is unavailable, the system fails closed instead of returning unfiltered results. I test open, half-open and closed states with an injected clock.

## Why

The example implements a small breaker with an injected clock, runs a pipeline with a failing reranker until the breaker opens, and then shows that an authorization outage raises instead of bypassing filtering.

## Production Case

A reranking service slows to 8 seconds under load. Without a breaker every query waits for the timeout and the API saturates. With a breaker, queries skip the reranker after two failures, p95 latency recovers, quality metrics show the degraded flag, and the reranker is re-enabled by a half-open probe.

## Risk

A permissive fallback during an authorization outage leaks data. A breaker with a cooldown that is too short flaps, and one too long delays recovery.

## Trade-off

Graceful degradation keeps the service responsive but returns lower-quality answers; a strict fail-closed policy preserves safety at the cost of availability for protected paths.

## Try This

Advance the injected clock beyond reset_after and verify the half-open probe closes the breaker when the reranker recovers, then add a bulkhead semaphore around the reranker call.

## Execution Timeline

Authorize first -> check breaker state -> call optional stage with timeout -> record success or failure -> on open state skip stage and mark degraded -> emit metrics -> half-open probe after cooldown

## Complexity

Breaker state checks are O(1) per call; the main cost is operational: tuning thresholds, monitoring and testing state transitions.

## Definitions

- **Circuit breaker**: A guard that stops calling a failing dependency and later probes for recovery.
- **Half-open state**: A trial state in which limited calls test whether the dependency recovered.
- **Bulkhead**: Resource isolation that prevents one workload from exhausting shared capacity.
- **Fail closed**: On failure of a protective check, deny access instead of allowing it.

## Alternatives

- Load shedding with HTTP 429 or 503
- Hedged requests to a second reranker replica
- Static timeouts only, accepting the saturation risk

## Pitfalls

- Permissive fallback on authorization failure
- Retries without breaker or jitter
- No metric for degraded mode
- Shared pools for ingestion and interactive traffic

## Follow-ups

### How do you test a circuit breaker deterministically?

Inject a clock and a controllable fake dependency. Assert transitions: failures below the threshold keep it closed, reaching the threshold opens it, before the cooldown calls are skipped, after the cooldown a probe is allowed, and a successful probe closes it.

### How is a bulkhead different from rate limiting?

Rate limiting caps request volume over time. A bulkhead caps concurrent resource use per workload so a flood in one class cannot starve another. They are complementary.

### Should the degraded response tell the user?

Expose it in metrics and, where relevant, in response metadata. For quality-sensitive domains consider a visible note, since lower-ranked evidence can change answer completeness.

## Example

> Explanation: Degrade optional stages with a circuit breaker; never degrade authorization into allow-all.
> Output: verified

```python
"""Degrade optional stages with a circuit breaker; never degrade authorization into allow-all."""


class Breaker:
    def __init__(self, threshold=2, reset_after=30.0, clock=lambda: 0.0):
        self.threshold, self.reset_after, self.clock = threshold, reset_after, clock
        self.failures, self.opened_at = 0, None

    def allow(self):
        if self.opened_at is None:
            return True
        if self.clock() - self.opened_at >= self.reset_after:
            return True            # half-open probe
        return False

    def record(self, ok):
        if ok:
            self.failures, self.opened_at = 0, None
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = self.clock()


class AuthorizationUnavailable(Exception):
    pass


def authorize(candidates, authz_up):
    if not authz_up:
        raise AuthorizationUnavailable("fail closed")
    return [c for c in candidates if c["tenant"] == "t1"]


def pipeline(candidates, breaker, reranker_up, authz_up=True):
    allowed = authorize(candidates, authz_up)          # always runs first
    if breaker.allow():
        try:
            if not reranker_up:
                raise TimeoutError
            breaker.record(True)
            return sorted(allowed, key=lambda c: -c["score"]), "reranked"
        except TimeoutError:
            breaker.record(False)
    return allowed, "first-stage"


now = [0.0]
breaker = Breaker(clock=lambda: now[0])
docs = [{"id": 1, "tenant": "t1", "score": 0.2}, {"id": 2, "tenant": "t2", "score": 0.9}, {"id": 3, "tenant": "t1", "score": 0.8}]
modes = [pipeline(docs, breaker, reranker_up=False)[1] for _ in range(3)]
try:
    pipeline(docs, breaker, reranker_up=True, authz_up=False)
    denied = False
except AuthorizationUnavailable:
    denied = True
assert breaker.opened_at is not None and denied
print(modes, "breaker_open", breaker.opened_at is not None, "authz_fail_closed", denied)
```

## Citations

- https://martinfowler.com/bliki/CircuitBreaker.html
- https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead

# Why can a healthy container be an unsafe candidate for production traffic?

<!-- meta
domain: operations
subdomain: deployment-reliability
module: deployment-reliability
concept: Why can a healthy container be an unsafe candidate for production traffic?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A new replica returns 200 on health while serving an index from the wrong data generation.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A process health check does not establish business correctness, data/schema compatibility, permission safety or acceptable quality. Promote an immutable artifact only after the relevant gates and recovery checks. Use readiness, liveness and rollout status for their distinct operational roles, and preserve a known compatible rollback path.

Concrete engineering case: A new replica returns 200 on health while serving an index from the wrong data generation.

Boundary defense: No. It reports stalled progress. An operator or higher-level controller must decide and execute recovery.

## Spoken Summary

A process health check does not establish business correctness, data/schema compatibility, permission safety or acceptable quality. Promote an immutable artifact only after the relevant gates and recovery checks. Use readiness, liveness and rollout status for their distinct operational roles, and preserve a known compatible rollback path.

## Why

A process health check does not establish business correctness, data/schema compatibility, permission safety or acceptable quality. Promote an immutable artifact only after the relevant gates and recovery checks. Use readiness, liveness and rollout status for their distinct operational roles, and preserve a known compatible rollback path.

## Production Case

A new replica returns 200 on health while serving an index from the wrong data generation.

## Risk

A new replica returns 200 on health while serving an index from the wrong data generation.

## Trade-off

No. It reports stalled progress. An operator or higher-level controller must decide and execute recovery.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: deployment reliability**: A process health check does not establish business correctness, data/schema compatibility, permission safety or acceptable quality.

## Alternatives

- No. It reports stalled progress. An operator or higher-level controller must decide and execute recovery.

## Pitfalls

- A new replica returns 200 on health while serving an index from the wrong data generation.

## Follow-ups

### Will a Kubernetes progress deadline automatically roll it back?

No. It reports stalled progress. An operator or higher-level controller must decide and execute recovery.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A new replica returns 200 on health while serving an index from the wrong data generation.",
  "required_decision": "A process health check does not establish business correctness, data/schema compatibility, permission safety or acceptable quality"
}
```

## Citations

- https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
- https://www.postgresql.org/docs/current/backup.html
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://developer.hashicorp.com/terraform/intro
- https://sre.google/sre-book/service-level-objectives/
- https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/

# How do you prevent duplicate notifications when delivery succeeds but acknowledgment is lost?

<!-- meta
answer_format: conceptual
domain: ai-systems
subdomain: deployment-reliability
difficulty: advanced design scenario
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

**Expect an ambiguous delivery window.** A worker can send successfully and crash before marking its outbox event delivered. Recovery then retries. The outbox guarantees recoverable intent, not exactly-once external delivery. Acknowledging before sending instead risks permanent loss, so merely swapping those two operations does not solve the problem.

**Deduplicate at the destination where possible.** An in-application feed can use a unique event identifier and insert the feed item transactionally. A duplicate delivery becomes a no-op and can still be acknowledged. For an external provider, send a stable provider-supported idempotency key and reconcile an unknown outcome using that key. Verify the provider's retention and conflict semantics; do not assume every channel supports deduplication.

**Separate unsupported channels from successful delivery.** A worker without an implemented delivery adapter should fail explicitly and preserve retry or dead-letter status. Silently returning success loses the event. Classify permanent validation errors separately from transient network failures, cap retries and retain enough safe diagnostic detail for repair.

**Design operations for uncertainty.** Track delivery attempts, provider references, next retry time and terminal disposition. Replaying a dead-letter event must retain the original logical event identity unless the operator intentionally creates a new event. Set expectations for channels that can still deliver duplicates, and ensure the message does not claim an effect that never committed. The local feed example uses a real unique constraint to make redelivery idempotent; it does not model email-provider guarantees.

## Why

A feed insertion commits, but the worker dies before acknowledging the outbox event. The next worker retries the same event ID. The feed retains one row and the worker can safely mark the intent delivered.

## Worked Case

A feed insertion commits, but the worker dies before acknowledging the outbox event. The next worker retries the same event ID. The feed retains one row and the worker can safely mark the intent delivered.

## Risk

Changing the event ID on every retry defeats destination deduplication. An unsupported channel reported as successful silently drops notifications.

## Trade-off

At-least-once delivery with destination deduplication is practical; channels without it require explicit duplicate tolerance or reconciliation.

## Try This

Inject a crash after destination commit and before acknowledgment. Retry the same event, then test a deliberately unsupported channel.

## Follow-ups

### What if a retry uses the same ID with different content?

Validate a payload fingerprint or store immutable event data before delivery. An idempotency key should not silently accept a different logical message.

### Is an operator replay always safe?

Only under the same delivery and authorization contract. Recheck recipient eligibility and preserve event identity when retrying the original notification.

## Citations

- https://www.sqlite.org/lang_transaction.html

# How do health checks, graceful shutdown and readiness affect safe releases?

<!-- meta
answer_format: conceptual
domain: operations
subdomain: deployment-reliability
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A process being alive does not mean it can serve correct traffic. Liveness detects a stuck process under a defined policy; readiness indicates whether it should receive traffic; startup checks allow initialization without premature restarts. Graceful shutdown stops admission, drains or transfers owned work and respects an overall termination deadline. Schema changes and background jobs need compatible rollout ordering. Test the deployed request path, not only a local process, and preserve operation status for work that outlives a client connection.

## Why

A worker receives termination after accepting a durable job. It should stop taking new jobs and leave an explicit completion or takeover boundary, rather than losing ownership silently when the process exits.

## Worked Case

A worker receives termination after accepting a durable job. It should stop taking new jobs and leave an explicit completion or takeover boundary, rather than losing ownership silently when the process exits.

## Risk

Aggressive health probes can repeatedly restart a slow but recovering dependency path.

## Trade-off

Fast detection must be balanced against startup, recovery and drain requirements.

## Try This

Terminate a replica during active work and verify client status, takeover and duplicate prevention.

## Citations

- https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
- https://www.postgresql.org/docs/current/backup.html
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://developer.hashicorp.com/terraform/intro
- https://sre.google/sre-book/service-level-objectives/
- https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/

# How do recovery objectives and restore drills differ from simply keeping backups?

<!-- meta
answer_format: conceptual
domain: operations
subdomain: deployment-reliability
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A backup is an artifact; recovery is a tested procedure that returns an acceptable service and data state. Define the recovery point objective as tolerated data loss and recovery time objective as tolerated restoration delay. Verify integrity, schema compatibility, credentials, deletion intents and dependent indexes after restore. Record what happened after the snapshot and how it is reconciled. A successful file copy does not establish that the restored application enforces current ownership or does not resurrect deleted data.

## Why

Restoring yesterday's database can recreate a document deleted this morning. Reapply authoritative deletion intent before exposing restored search results and report which newer accepted writes could not be recovered.

## Worked Case

Restoring yesterday's database can recreate a document deleted this morning. Reapply authoritative deletion intent before exposing restored search results and report which newer accepted writes could not be recovered.

## Risk

An untested backup can be unreadable, incomplete or semantically unsafe to publish.

## Trade-off

More frequent snapshots reduce some loss windows while increasing storage and operational cost.

## Try This

Perform a restore and record elapsed recovery, missing writes and deletion visibility.

## Citations

- https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
- https://www.postgresql.org/docs/current/backup.html
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://developer.hashicorp.com/terraform/intro
- https://sre.google/sre-book/service-level-objectives/
- https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/
