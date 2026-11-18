<!-- chapter: fullstack -->

# What application components are still needed around the retrieval service?

<!-- meta
domain: system-design
subdomain: fullstack
module: fullstack
concept: What application components are still needed around the retrieval service
difficulty: implementation
misconception_target: Each layer can be developed independently without integration testing
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

A complete product needs identity, authorized API routes, a document-management workflow, durable adapters, background workers, generation policy, a user interface, monitoring, deployment, and evaluation. The reference design supplies important subsystem pieces and examples, not all of these production services.

## Spoken Summary

A full product adds authenticated API boundaries, owned durable tasks, provider adapters, scoped evidence, validation, approvals, effect recovery, frontend states, observability and deployment/recovery practices around retrieval. Trace one real user workflow through these boundaries and test partial failures.

## Why

Build around the evidence contract: the API obtains authorized evidence, then a host generator produces an answer, while the UI can open source spans and show status. This keeps source verification useful even without generation.

## Production Case

The model streams a plausible confirmation, but the write times out after committing. The UI must show an uncertain/processing state and reconcile the same operation key rather than prompting another uncontrolled write.

## Risk

Assuming the library owns users or migrations can leave critical responsibilities unimplemented. A polished chat screen does not compensate for missing tenant isolation or recovery behavior.

## Trade-off

Explicit host ownership requires more work but fits an existing backend. A monolithic demo can be quicker and should be labeled according to its actual guarantees.

## Try This

Draw your target application with browser, API, workers, identity provider, source system, vector store, snapshot store, and model provider. Mark every trust boundary.

## Execution Timeline

User submits -> Frontend sends request -> Backend orchestrates retrieval and agents -> Streams results -> Frontend renders with citations

## Complexity

End-to-end cost includes queueing and the critical path across services, plus parallel work, retries and model tokens. Summing nominal orchestration step counts does not explain tail latency or spend.

## Definitions

- **End-to-end test**: Test that verifies the complete user flow from frontend to backend
- **Independent error handling**: Each layer handles its own errors without cascading failures
- **Streaming integration**: Frontend displays results as backend produces them

## Alternatives

- Monolithic single-service
- Separate frontend/backend without streaming

## Pitfalls

- No end-to-end tests
- Error cascading between layers
- No streaming integration

## Follow-ups

### Which end-to-end failure should you test first?

A lost acknowledgment across a real effect boundary, combined with ownership checks, is more revealing than only a happy-path text-generation demo.

## Example

> Explanation: Backend orchestrates and streams results to frontend.
> Output: Streamed response with citations

```python
app.post("/ask", async (req, res) => {\n  const stream = await backend.orchestrate(req.question);\n  res.setHeader("Content-Type", "text/event-stream");\n  for await (const chunk of stream) res.write(`data: ${chunk}\\n\\n`);\n});
```

## Citations

- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

# How would you design the search and chat API contracts?

## Answer

Expose structured request and response objects with query, permitted collection choice, bounded retrieval options, operation identity, status, evidence, and citations. Resolve user identity and allowed scope on the server. Keep internal database names and arbitrary backend filters out of the public API unless deliberately supported.

## Why

RetrievalRequest and EvidenceBundle provide useful internal shapes, but the host should create a stable transport contract rather than expose all library internals. Errors should distinguish validation, denied access, backend outage, and successful empty search.

## Risk

Letting a browser select raw table names or trusted client IDs bypasses the composition boundary. Returning provider exceptions directly may leak secrets or infrastructure details.

## Trade-off

A narrow API is safer and easier to evolve; an expert administration API may expose more controls under stronger permissions.

## Try This

Write example request and response JSON for success, denied scope, and backend failure. Explain which fields the server derives instead of trusting the client.

# How should streaming work without misleading the user?

## Answer

Complete authorization and evidence selection before presenting factual generated service requests as supported. Stream generation events with an operation ID and explicit stages, then preserve a final status and citation mapping. The exact HTTP transport is a host design choice, not a provided chat server feature.

## Why

Evidence assembly produces a stable bundle before a generator consumes it. The UI can show searching, assembling, generating, complete, cancelled, or failed states without pretending that partial text is a verified final answer.

## Risk

A network disconnect can leave server work running, and partial output may contain incomplete citation syntax. Propagate cancellation where possible and never silently mark a truncated stream complete.

## Trade-off

Early streaming improves perceived responsiveness while complicating error recovery and state handling. A non-streaming first version is easier to validate.

## Try This

Design events for evidence_ready, answer_delta, complete, and failure. Simulate a disconnect after two deltas and specify what remains visible and retryable.

# What should a useful RAG interface show besides the answer text?

## Answer

Show source titles and bounded excerpts, revision or freshness when relevant, citation navigation, loading and failure states, and a clear way to refine an ambiguous question. Make evidence accessible by keyboard and avoid presenting similarity as factual confidence.

## Why

The bundle already contains attribution and status data that a frontend can render. revision-aware source lookup provides a verification path when the user opens a citation; that path must retain the same identity and scope policy.

## Risk

Rendering document text as raw HTML can create cross-site scripting. Use safe text rendering or a deliberately sanitized markup pipeline, and treat citation URLs as untrusted input.

## Trade-off

More evidence improves transparency but can overwhelm users. Start with concise source summaries and progressive disclosure of full spans.

## Try This

Build a search-only UI before chat. Include empty, stale, failed, and insufficient-budget examples, then test it entirely with keyboard navigation.

# How should frontend state be separated from backend truth?

## Answer

Keep local interaction state such as expanded sources or draft input separate from server state such as operation status, evidence, and active document versions. Key cached results by the relevant identity, scope, query, and configuration or revision where necessary.

## Why

The retrieval service returns structured results, leaving the browser framework and caching library to the host. A frontend must preserve status distinctions and invalidate data when permissions or active generations change.

## Risk

Reusing a browser cache across sign-out or tenant switching can expose another user's evidence. Optimistically marking ingestion complete before activation can also misrepresent searchability.

## Trade-off

Explicit invalidation and cache partitioning add complexity but preserve correct user expectations. A simple no-cache first implementation can be preferable to unsafe reuse.

## Try This

Switch tenants while a request is in flight. Ensure its late response cannot populate the new tenant's visible state or source drawer.

# How should document upload and indexing progress be designed?

## Answer

Treat upload acceptance, source storage, extraction, embedding, activation, and searchability as distinct states. Persist the accepted source and enqueue background work according to the host's transaction policy. Return an operation identifier rather than blocking the request until every provider call completes.

## Why

Outbox and drainer interfaces decouple request latency from processing. Sync reports and events provide lifecycle information that a host can translate into progress, while active visibility determines when content can actually be searched.

## Risk

A successful upload can later fail extraction or embedding. The UI must not claim indexed status solely because bytes were received, and retry actions must avoid duplicate logical documents.

## Trade-off

Background workflows need polling or event delivery and durable state. Synchronous ingestion is simpler for small local experiments but less resilient under provider latency.

## Try This

Define a document state machine from uploaded to searchable, with retry and failed states. Associate each transition with the component that can authoritatively report it.

# What does production deployment require beyond installing optional extras?

## Answer

Provision durable stores and schemas, configure credentials and network access, run workers, set identity and permissions, select compatible profiles, validate startup, and establish backups, monitoring, and rollback. An optional dependency installs client code; it does not provision or secure its service.

## Why

The dependency manifest separates backend extras from dependency-free core, while health checks and integration examples help validate wiring. Actual database indexes and extension configuration remain deployment responsibilities.

## Risk

Multiple replicas using in-memory manifests or rate limits do not share authoritative state. Secrets in configuration fingerprints or public diagnostics can also create exposure.

## Trade-off

Managed services reduce some operations work and add cost or provider dependence. Self-hosting gives control and requires deeper operational expertise.

## Try This

Produce a deployment inventory with ownership, persistence, backup, restart behavior, and secret source for every component. Include what happens when one replica restarts.

# How would you plan capacity and handle overload?

<!-- meta
answer_format: conceptual
domain: fullstack-engineering
subdomain: fullstack
difficulty: implementation
review.status: reviewed
review.reviewer: Technical curriculum review
review.reviewed_at: 2026-10-22
-->

## Answer

**Capacity planning connects arrival rate, service time and constrained resources.** With a stable mean arrival rate lambda and mean time W in the system, Little's law gives mean in-flight work L=lambda*W. If 20 requests/s each occupy a model slot for 2 seconds on average, about 40 are in flight. With eight effective concurrent slots per replica, five replicas is only the arithmetic minimum at full utilization, not a resilient tail-latency plan.

Reserve headroom for bursts, retries, slow dependencies and an unavailable replica. Queue wait grows sharply near saturation, and real service times vary with input/output tokens. Bound admitted work and return a clear overload response rather than accepting an unlimited queue. Rate limiting controls arrival policy; concurrency limits control simultaneous work; a token/cost budget controls resource exposure. A user retry can consume another provider attempt even if the UI still shows one logical question.

Partition only where invariants allow. Owner-sharded state can isolate workloads, while one hot tenant or shared model dependency remains a bottleneck. A cache reduces repeated work only when its key includes scope and relevant revisions; stale or cross-owner cache hits are correctness/security failures. Queue and cache layers need explicit deletion, cancellation and recovery rules, not just throughput graphs.

Build a system-design case with end-to-end request sequence, critical data/effect boundaries, storage consistency assumptions and capacity arithmetic. State what is measured versus assumed. Allocate a latency budget across queueing, retrieval, reranking, first token and completion, then measure whole-request percentiles; adding stage p95 values does not yield request p95. Compare simpler fixed workflows or smaller models against more autonomous designs under the same quality gate. The workbench and CDC fixtures expose several boundaries locally; they do not establish distributed production capacity.

## Why

Twenty requests per second times two seconds yields 40 mean in-flight requests. Five eight-slot replicas leaves no failure headroom, so a defensible design adds measured utilization/tail behavior, admission policy and an N-1 scenario.

## Worked Case

Twenty requests per second times two seconds yields 40 mean in-flight requests. Five eight-slot replicas leaves no failure headroom, so a defensible design adds measured utilization/tail behavior, admission policy and an N-1 scenario.

## Risk

An unbounded queue turns overload into timeouts, retries and higher cost. Caching an incorrect or unauthorized answer can multiply the impact of one bad result.

## Trade-off

More replicas can reduce compute contention while increasing connection pressure and cost. Larger candidate pools or models may improve quality but consume the same latency and budget headroom.

## Try This

Calculate the 40-slot example, design an N-1 headroom policy and trace an overload incident through UI, queue, retrieval and provider attempts. State which parameters need measurement before deployment.

## Follow-ups

### What if most requests finish quickly but a few generate very long answers?

Mean service time hides the tail and slot occupancy. Measure length-conditioned completion and queue latency, enforce output limits and consider separate admission classes without starving long legitimate requests.

## Citations

- https://sre.google/sre-book/handling-overload/
- https://sre.google/sre-book/monitoring-distributed-systems/

# What portfolio project would demonstrate AI full-stack competence?

## Answer

Build a multi-tenant knowledge assistant with a search-first interface, revision-aware citations, background ingestion, a grounded answer policy, and a reproducible evaluation report. Show a failure and its diagnosis, not only a polished happy-path recording.

## Why

This combines frontend state, API design, identity, async jobs, data modeling, retrieval, generation, evaluation, and operations. the retrieval service provides the subsystem foundation while your work proves the application integration.

## Risk

A public demo can accidentally expose private sample documents or provider credentials. Use a reviewed fixture corpus and document implemented guarantees rather than aspirational architecture.

## Trade-off

A narrow reliable project is more convincing than many unfinished advanced features. Add reranking or multi-query only when your benchmark shows why they help.

## Try This

Deliver a README with architecture, a threat-boundary map, benchmark results, three recovery demonstrations, and a five-minute walkthrough that opens a cited source revision.

# How should I answer a senior system-design interview using this reference design?

## Answer

Start with requirements and constraints, then describe the offline and online flows, data identities, permission boundary, consistency model, failure recovery, quality evaluation, and capacity plan. Defend choices with case-based mechanisms and acknowledge which guarantees depend on host adapters.

## Why

The reference design's strongest lessons are explicit boundaries: prepare versus commit, candidates versus final evidence, logical visibility versus physical cleanup, and retrieval quality versus answer faithfulness. These distinctions scale beyond one library.

## Risk

Memorized pattern names and invented timing claims collapse under follow-up questions. Be ready to explain a crash interleaving, an authorization failure, and a measured quality trade-off in concrete terms.

## Trade-off

A good design is conditional on requirements. State when a keyword-only system, one transactional database, or a simpler synchronous workflow would be the better choice.

## Try This

Give a 45-minute mock interview: five minutes requirements, ten architecture, ten consistency and security, ten evaluation and scale, and ten trade-offs and alternatives.

# How do you trace a duplicate action across a browser, task API, worker and provider?

<!-- meta
domain: system-design
subdomain: fullstack
module: fullstack
concept: How do you trace a duplicate action across a browser, task API, worker and provider?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: The browser retries after losing the acceptance response, the worker restarts after a checkpoint and the provider receives three calls for one intended operation.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

Follow one stable logical operation identity through caller scope, accepted payload, task state, worker attempt and receiver receipt. Separate presentation retries from effect retries and compare durable state at every commit boundary. A browser error or missing acknowledgment cannot alone establish whether the provider committed.

Concrete engineering case: The browser retries after losing the acceptance response, the worker restarts after a checkpoint and the provider receives three calls for one intended operation.

Boundary defense: Not by itself. Inspect the intended final durable effects and conflicts. Multiple deliveries may be acceptable when the receiver preserves one logical effect.

## Spoken Summary

Follow one stable logical operation identity through caller scope, accepted payload, task state, worker attempt and receiver receipt. Separate presentation retries from effect retries and compare durable state at every commit boundary. A browser error or missing acknowledgment cannot alone establish whether the provider committed.

## Why

Follow one stable logical operation identity through caller scope, accepted payload, task state, worker attempt and receiver receipt. Separate presentation retries from effect retries and compare durable state at every commit boundary. A browser error or missing acknowledgment cannot alone establish whether the provider committed.

## Production Case

The browser retries after losing the acceptance response, the worker restarts after a checkpoint and the provider receives three calls for one intended operation.

## Risk

The browser retries after losing the acceptance response, the worker restarts after a checkpoint and the provider receives three calls for one intended operation.

## Trade-off

Not by itself. Inspect the intended final durable effects and conflicts. Multiple deliveries may be acceptable when the receiver preserves one logical effect.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: fullstack**: Follow one stable logical operation identity through caller scope, accepted payload, task state, worker attempt and receiver receipt.

## Alternatives

- Not by itself. Inspect the intended final durable effects and conflicts. Multiple deliveries may be acceptable when the receiver preserves one logical effect.

## Pitfalls

- The browser retries after losing the acceptance response, the worker restarts after a checkpoint and the provider receives three calls for one intended operation.

## Follow-ups

### Is the number of calls the right correctness oracle?

Not by itself. Inspect the intended final durable effects and conflicts. Multiple deliveries may be acceptable when the receiver preserves one logical effect.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "The browser retries after losing the acceptance response, the worker restarts after a checkpoint and the provider receives three calls for one intended operation.",
  "required_decision": "Follow one stable logical operation identity through caller scope, accepted payload, task state, worker attempt and receiver receipt"
}
```

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
- https://ai.google.dev/gemini-api/docs/generate-content
- https://ai.google.dev/gemini-api/docs/rate-limits
- https://ai.google.dev/gemini-api/docs/structured-output
- https://developers.openai.com/api/docs/guides/rate-limits
- https://developers.openai.com/api/docs/guides/streaming-responses
- https://developers.openai.com/api/docs/guides/structured-outputs

# How do end-to-end contracts connect browser state, API state and background effects?

<!-- meta
answer_format: conceptual
domain: system-design
subdomain: fullstack
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

A full-stack workflow crosses independently failing components. Define a stable operation identity, authenticated scope, API representation, durable acceptance point and browser ownership rule. The browser can show a pending action while a worker completes it, but should recover status after refresh or disconnect. Keep generated explanation separate from authoritative business state. An end-to-end check should exercise the real boundary that could fail: stale responses, duplicate submission, denied ownership or an interrupted accepted operation.

## Why

A user refreshes immediately after submitting a request. The new page should recover the accepted operation by its stable identity instead of creating another request because the earlier in-memory loading state disappeared.

## Worked Case

A user refreshes immediately after submitting a request. The new page should recover the accepted operation by its stable identity instead of creating another request because the earlier in-memory loading state disappeared.

## Risk

A polished frontend can conceal missing durable acceptance and recovery behavior.

## Trade-off

Explicit cross-component identities simplify user recovery at additional state-modeling cost.

## Try This

Submit, disconnect, refresh and reconcile one operation without duplication.

## Citations

- https://developer.mozilla.org/en-US/curriculum/core/
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
- https://ai.google.dev/gemini-api/docs/generate-content
- https://ai.google.dev/gemini-api/docs/rate-limits
- https://ai.google.dev/gemini-api/docs/structured-output
- https://developers.openai.com/api/docs/guides/rate-limits
- https://developers.openai.com/api/docs/guides/streaming-responses
- https://developers.openai.com/api/docs/guides/structured-outputs
