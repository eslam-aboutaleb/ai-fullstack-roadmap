<!-- chapter: architecture -->

# Why separate a reusable retrieval subsystem from a complete application?

<!-- meta
domain: system-design
subdomain: architecture
module: architecture
concept: Why separate a reusable retrieval subsystem from a complete application
difficulty: design
misconception_target: More abstractions always mean better design
added: true
review.status: draft
review.reviewer: independent technical review pending
review.reviewed_at: 2026-10-20
-->

## Answer

The package supplies composable RAG infrastructure while the host owns application models, authentication, routing, deployment, and generation. That boundary allows an existing backend to adopt retrieval without letting a library control its domain schema or request lifecycle.

## Spoken Summary

A reusable retrieval subsystem returns scoped, versioned evidence under a clear interface. The full application adds identity, task state, model generation, approvals, effects, presentation and recovery. Separating these responsibilities improves replacement and testing when the interface preserves the required invariants.

## Why

Expose retrieval, ingestion, and evidence contracts independently from web routes and business models. The host binds authentication, persistence, and generation policy. This makes components testable without implying that every backend is interchangeable.

## Production Case

A second product reuses retrieval but has a different approval flow. It should not inherit hidden write privileges from a retrieval adapter that was designed only to return evidence.

## Risk

Integration errors move to the seams: missing scope policy, incorrect transaction ownership, or a fake embedder accidentally used for real search. Examples and contract tests help, but the host must review its wiring.

## Trade-off

You gain control and portability while doing more assembly. A packaged application would offer faster initial setup with more predetermined choices.

## Try This

Draw a ports-and-adapters diagram showing which side owns users, SQL tables, provider credentials, evidence, and chat responses.

## Execution Timeline

Identify boundaries -> Define interfaces -> Choose abstractions -> Document ADRs -> Review and refine

## Complexity

Interface choices are evaluated through change isolation, correctness and operational cost. O(components) is not a useful substitute for analyzing the actual request/data path.

## Definitions

- **Interface boundary**: Explicit contract between system components
- **Abstraction**: Hiding complexity behind a simpler interface
- **ADR**: Architecture Decision Record documenting context, options, and rationale

## Alternatives

- Tightly coupled components
- No interface documentation

## Pitfalls

- Over-abstraction with no benefit
- Undocumented decisions
- Interfaces that leak implementation details

## Follow-ups

### When is another abstraction unnecessary?

When it adds indirection without isolating a real responsibility, independent change or test boundary. Compare concrete maintenance and failure costs.

## Example

> Explanation: Interface allows swapping retrieval implementations.
> Output: Interface definition for swappable components

```python
class RetrievalInterface:
    def search(self, query): pass
    def rerank(self, results): pass

# Swappable implementations behind the same interface
```

## Citations

- https://martinfowler.com/bliki/InterfaceSegregationPrinciple.html

# How does dependency inversion appear in the reference design?

## Answer

A fluent builder assembles collaborators through readable configuration methods and a final construction step. It can provide safe local defaults while requiring explicit production dependencies. The builder is a convenience facade; the lower-level contracts remain useful independently.

## Why

The ingestion coordinator accepts its collaborators in the constructor. the version repository receives the active session for mutations, and a SQL adapter interface abstracts database operations. You can replace a collaborator with a controlled test implementation without rewriting orchestration.

## Risk

An adapter can satisfy a Python method signature while violating atomicity or isolation semantics. Structural compatibility is weaker than behavioral compatibility, so tests need to exercise the promised guarantees.

## Trade-off

Interfaces add indirection and documentation work. They pay off when deployment stacks differ or when failure paths need deterministic testing.

## Try This

Replace version storage with a tiny recording fake. Verify the order of find, close, create, delete, and upsert calls without assuming that call order alone proves rollback safety.

# Why use Protocol instead of requiring every adapter to inherit a base class?

## Answer

Python Protocol supports structural typing: an object can satisfy a contract by providing the required members. This is useful when a host already has settings or session providers and should not need to inherit library-specific classes.

## Why

Retrieval settings and several storage seams express the attributes or methods consumers need. Some interfaces also use runtime_checkable, but runtime checks do not fully validate annotations, returned values, or transactional behavior.

## Risk

Duck typing can postpone integration errors until execution. Validate configuration at startup and run adapter contract tests; do not interpret isinstance against a protocol as a complete certification.

## Trade-off

Protocols reduce inheritance coupling while offering less shared implementation. Abstract base classes remain useful when construction rules or common behavior must be enforced.

## Try This

Supply a dataclass as settings, then remove a required attribute. Compare static type feedback with the eventual runtime failure.

# What does the Fluent Builder pattern contribute here?

## Answer

A retrieval-service builder assembles collaborators through readable configuration methods and an asynchronous build step. The local constructor chooses in-memory defaults while still requiring an embedding function. The result is a convenient facade over the lower-level components.

## Why

This keeps a small experiment short while allowing chunkers, stores, version stores, and settings to be replaced. The builder is composition convenience; it does not make an in-memory setup durable or create a learned local embedding model.

## Risk

Hidden defaults can be carried into production. Review the resolved store, embedding dimension, scope policy, and state retention before deploying an instance built for local use.

## Trade-off

A builder is easier to discover than a large constructor but adds another assembly surface to maintain. Direct constructors are clearer for unusual production wiring.

## Try This

Run the offline quickstart, then rewrite its setup with explicit collaborators. Describe which defaults you would replace for a multi-worker service.

# How are Factory, Registry, Strategy, and Adapter different patterns?

## Answer

A factory constructs a collaborator. A registry maps names to implementations. A strategy selects interchangeable behavior such as dense, lexical, or hybrid retrieval. An adapter translates an external API into the reference design's contract. The patterns solve different problems and often appear together.

## Why

Store factories and registries choose backend implementations; retrieval strategies compose search capabilities; backend classes translate vendor operations. This allows configuration-driven construction without forcing every search behavior into a storage class.

## Risk

A name-based registry can defer typos or missing optional dependency failures until runtime. Validate names and dependencies during startup, and avoid loading plugins based on arbitrary untrusted input.

## Trade-off

Configurable assembly improves extension but increases possible combinations. Support a documented matrix rather than assuming every registered backend supports every strategy and filter.

## Try This

Explain how adding a new vector backend differs from adding a query reranker. Identify the construction, contract, and behavior changes separately.

# Why split the vector-store interface into smaller capability protocols?

## Answer

A broad store interface is convenient when one backend supports every operation. Separate vector search, lexical search, fetch, and write capabilities let callers depend only on the operations they need. A keyword-only route should not require an embedding provider.

## Why

The retrieval service's retrieval strategies compose vector and lexical capabilities, permitting different backends for different signals. Capability declarations describe supported filters and guarantees before the strategy executes.

## Risk

A backend may advertise a capability it implements incompletely. Mandatory constraints should fail closed, and contract tests should verify semantics rather than only checking that methods exist.

## Trade-off

More interfaces create more concepts, but avoid fake implementations of unsupported methods. A single-store facade remains helpful for simple applications.

## Try This

Design a lexical-only adapter. List the interfaces it needs and the vector-specific methods it should never have to emulate.

# What does a SQL adapter interface abstract, and what remains PostgreSQL-specific?

## Answer

A SQL adapter interface abstracts session construction, execution, fetching, and advisory locking. It lets orchestration avoid direct dependence on one SQL library. It does not make PostgreSQL full-text functions or pgvector operators portable to an arbitrary database engine.

## Why

The PostgreSQL vector adapter still owns database-specific SQL. An alternative driver can implement the factory contract while preserving PostgreSQL semantics; a different database usually needs a different storage adapter and capability declaration.

## Risk

Replacing the driver without matching transaction and lock behavior can invalidate ingestion guarantees. A no-op advisory-lock implementation is not an equivalent production replacement.

## Trade-off

The extra seam improves driver flexibility and testability but carries semantic obligations. Direct driver calls would be simpler and more tightly coupled.

## Try This

Write down the minimum behavior an async database driver adapter must preserve for a locked ingestion transaction. Include failure and rollback cases.

# Why use dataclasses and explicit converters at API boundaries?

## Answer

Dataclasses make fields, defaults, and meanings discoverable without requiring a validation framework. Explicit converters keep dictionary-based adapters compatible while typed consumers work with Document, SearchResult, RetrievalRequest, and RetrievalResponse.

## Why

As_dicts and typed retrieval bridges separate legacy shapes from newer APIs. This supports gradual adoption without forcing every host and backend to migrate simultaneously.

## Risk

Type annotations alone do not validate hostile input, and conversions can lose fields such as reranker scores if an older result type does not represent them. Validate transport input and choose the typed response when you need its richer score information.

## Trade-off

Compatibility layers cost code and can preserve ambiguity. Removing them simplifies internals but may break downstream callers; a migration policy must be explicit.

## Try This

Convert one typed hit to a dictionary and back. Check identity, metadata, distance, RRF score, and reranker score separately.

# How does the Null Object pattern appear in telemetry?

## Answer

A a null event sink implements the event-sink contract while doing nothing. Consumers can emit an event without checking whether telemetry is configured at every call site. This keeps optional observability out of the main control flow.

## Why

Constructors select a null sink when no sink is supplied. A real sink can later export sanitized events, and the business path can retain the same call structure.

## Risk

A null sink can make missing production instrumentation invisible. Also inspect whether a supplied sink can raise or block; optional observability should not accidentally become an uncontrolled availability dependency.

## Trade-off

Fewer branches improve readability, while silent default behavior requires explicit operational verification. An application may choose mandatory instrumentation at its composition root.

## Try This

Run the same retrieval with a recording sink and a null sink. Verify equal results and inspect which dimensions the recording sink receives.

# How should I defend the architecture in an interview without inventing author intent?

## Answer

Describe observed boundaries, explain the problems they address, and distinguish inference from documented intent. For example, injected sessions support host transaction ownership; you can infer a portability benefit without claiming the author measured it against every ORM or framework.

## Why

Tie architectural explanations to an invariant and a failure scenario. For example, caller-owned transactions allow a business update and an outbox record to commit together. Explain the consequences without inventing historical author intent.

## Risk

Repeating comments as guarantees can mislead. Some comments simplify current behavior: the generic hybrid strategy awaits stages sequentially, and sliding-window chunks use UUIDs rather than universally deterministic IDs.

## Trade-off

Qualified service requests sound less absolute but survive technical scrutiny. A good design defense acknowledges obligations pushed to host adapters and conditions under which another design would win.

## Try This

Prepare a five-minute defense with three source references, two explicit limitations, and one alternative architecture you would choose under different requirements.

# How can a cached RAG response become a permission leak even when retrieval is scoped correctly?

<!-- meta
domain: system-design
subdomain: architecture
module: architecture
concept: How can a cached RAG response become a permission leak even when retrieval is scoped correctly?
difficulty: scenario
misconception_target: Assuming this concrete failure is excluded by a happy-path success: A response generated for an administrator is cached by query text and served to a regular user.
review.status: draft
review.reviewer: Independent review pending
review.reviewed_at: 2026-10-21
-->

## Answer

A cache can bypass the otherwise-correct retrieval path. Its identity and invalidation policy must include the relevant caller scope, permission generation, source/model/prompt versions and task semantics. Do not assume that two users asking identical text are allowed to share evidence. Evaluate cache hits and misses under the same security contract.

Concrete engineering case: A response generated for an administrator is cached by query text and served to a regular user.

Boundary defense: That is too late if the response or claims already disclose restricted information. Enforce scope before returning cached bytes.

## Spoken Summary

A cache can bypass the otherwise-correct retrieval path. Its identity and invalidation policy must include the relevant caller scope, permission generation, source/model/prompt versions and task semantics. Do not assume that two users asking identical text are allowed to share evidence. Evaluate cache hits and misses under the same security contract.

## Why

A cache can bypass the otherwise-correct retrieval path. Its identity and invalidation policy must include the relevant caller scope, permission generation, source/model/prompt versions and task semantics. Do not assume that two users asking identical text are allowed to share evidence. Evaluate cache hits and misses under the same security contract.

## Production Case

A response generated for an administrator is cached by query text and served to a regular user.

## Risk

A response generated for an administrator is cached by query text and served to a regular user.

## Trade-off

That is too late if the response or claims already disclose restricted information. Enforce scope before returning cached bytes.

## Try This

Reproduce this case with synthetic data, state the authoritative result and show a regression that rejects the broken behavior.

## Execution Timeline

Identify the authoritative state → trace the failure boundary → inspect durable or visible evidence → test the proposed recovery

## Complexity

Include workload size, retained state, latency, concurrency and recovery work under the declared assumptions; the reasoning fixture is not a capacity benchmark.

## Definitions

- **Boundary: architecture**: A cache can bypass the otherwise-correct retrieval path.

## Alternatives

- That is too late if the response or claims already disclose restricted information. Enforce scope before returning cached bytes.

## Pitfalls

- A response generated for an administrator is cached by query text and served to a regular user.

## Follow-ups

### Can the UI remove private citations after a cache hit?

That is too late if the response or claims already disclose restricted information. Enforce scope before returning cached bytes.

## Example

> Explanation: A source-linked reasoning fixture. JSON parsing checks representation only; reproduce the actual mechanism with the chapter reference.
> Output: No runtime or production measurement is inferred from this reasoning fixture.

```python
{
  "scenario": "A response generated for an administrator is cached by query text and served to a regular user.",
  "required_decision": "A cache can bypass the otherwise-correct retrieval path"
}
```

## Citations

- https://opentelemetry.io/docs/concepts/signals/

# How do dependency inversion and anti-corruption adapters prevent provider details from spreading?

<!-- meta
answer_format: conceptual
domain: system-design
subdomain: architecture
difficulty: mechanism
review.status: draft
review.reviewer: Independent technical review pending
-->

## Answer

Domain code should depend on the behavior it needs, while an adapter translates a provider's transport and data model into that contract. An anti-corruption boundary prevents provider-specific statuses, identifiers and exceptions from silently becoming domain policy. Match semantic guarantees, not just method signatures. Unsupported behavior must remain visible; a wrapper should not claim durable cancellation or tenant isolation that the provider does not supply. Keep the adapter small enough to test against real boundary cases.

## Why

A provider's 'accepted' response may mean queued rather than completed. Translating it directly into the domain state 'succeeded' corrupts every caller even though the adapter's return type looks convenient.

## Worked Case

A provider's 'accepted' response may mean queued rather than completed. Translating it directly into the domain state 'succeeded' corrupts every caller even though the adapter's return type looks convenient.

## Risk

An overgeneric interface can erase distinctions needed for safe recovery.

## Trade-off

Normalize compatible behavior and expose material capability differences explicitly.

## Try This

Write a contract test distinguishing accepted, completed, denied and unknown outcomes.

## Citations

- https://opentelemetry.io/docs/concepts/signals/
